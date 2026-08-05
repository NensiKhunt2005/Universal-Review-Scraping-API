import time
from typing import List

import yaml
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.core.exceptions import SelectorsNotFoundException
from src.core.logging import logger
from src.scrapers.base import BaseScraper


class AmazonScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__(url)
        self._load_selectors()

    def _load_selectors(self):
        try:
            with open("config/selectors.yaml", "r") as f:
                data = yaml.safe_load(f)
                self.selectors = data.get("amazon", {})
                if not self.selectors:
                    raise SelectorsNotFoundException("Amazon selectors not found.")
        except Exception as e:
            raise SelectorsNotFoundException(f"Error loading selectors: {e}")

    def navigate_to_reviews(self):
        try:
            sel = self.selectors.get("see_all_reviews")
            see_all_reviews = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            self.driver.execute_script("arguments[0].click();", see_all_reviews)
            logger.info("Navigated to main reviews page.")
        except TimeoutException:
            logger.warning(
                "Could not find 'See all reviews' link. "
                "Assuming already on the reviews page."
            )

    def extract_reviews_from_page(self) -> List[str]:
        reviews = []
        try:
            elements = self.driver.find_elements(
                By.CSS_SELECTOR, self.selectors.get("review_text")
            )
            for el in elements:
                text = el.text.strip()
                if text:
                    reviews.append(text)
            logger.info(f"Extracted {len(reviews)} reviews from page.")
        except Exception as e:
            logger.error(f"Failed to extract review texts: {e}")
        return reviews

    def go_to_next_page(self) -> bool:
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR, self.selectors.get("next_page")
            )
            if "a-disabled" in next_button.get_attribute("class"):
                return False
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)  # Wait for staleness
            return True
        except NoSuchElementException:
            return False
