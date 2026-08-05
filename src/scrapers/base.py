import time
from abc import ABC, abstractmethod
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.core.config import settings
from src.core.exceptions import ScraperBaseException
from src.core.logging import logger


class BaseScraper(ABC):
    def __init__(self, url: str):
        self.url = url
        self.driver = None
        self.selectors = {}

    def start_browser(self):
        logger.info("Initializing Selenium WebDriver...")
        options = Options()
        if settings and settings.scraper.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        timeout = settings.scraper.page_load_timeout if settings else 30
        self.driver.set_page_load_timeout(timeout)
        wait_time = settings.scraper.implicitly_wait if settings else 10
        self.driver.implicitly_wait(wait_time)

    def close_browser(self):
        if self.driver:
            logger.info("Closing browser session.")
            self.driver.quit()

    def scroll_page(self):
        logger.info("Scrolling page to load dynamic content.")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    @abstractmethod
    def navigate_to_reviews(self):
        """Navigate specifically to the all reviews section."""
        pass

    @abstractmethod
    def extract_reviews_from_page(self) -> List[str]:
        """Extract reviews text from the current page."""
        pass

    @abstractmethod
    def go_to_next_page(self) -> bool:
        """Navigate to the next page. Returns True if successful, False otherwise."""
        pass

    def scrape(self, max_pages: int = None) -> List[str]:
        """Core template method for scraping."""
        max_p = max_pages or (settings.scraper.max_pages_default if settings else 5)
        self.start_browser()
        all_reviews = []
        try:
            logger.info(f"Navigating to URL: {self.url}")
            self.driver.get(self.url)
            self.navigate_to_reviews()

            for page in range(max_p):
                logger.info(f"Scraping page {page + 1}...")
                self.scroll_page()
                reviews = self.extract_reviews_from_page()
                all_reviews.extend(reviews)

                if not self.go_to_next_page():
                    logger.info("No more pages found or next page inactive.")
                    break

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise ScraperBaseException(f"Scraping failed: {str(e)}")
        finally:
            self.close_browser()

        return all_reviews
