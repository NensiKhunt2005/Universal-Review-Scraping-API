import time
from typing import List
from bs4 import BeautifulSoup

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.core.logging import logger
from src.scrapers.base import BaseScraper


class FlipkartScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__(url)

    def navigate_to_reviews(self):
        try:
            # Flipkart "All reviews" link is usually a div with 'All' and 'reviews' text or a specific class
            elements = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'All') and contains(text(), 'reviews')]")
            if elements:
                # Click the closest clickable parent
                self.driver.execute_script("arguments[0].click();", elements[-1])
                logger.info("Navigated to main reviews page.")
                time.sleep(2)
        except Exception as e:
            logger.warning(f"Could not find 'See all reviews' link. Assuming already on the reviews page. {e}")

    def extract_reviews_from_page(self) -> List[str]:
        reviews = []
        try:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Flipkart unique DOM structure identifiers 
            # Review blocks almost always contain a 'Verified Purchase' or 'Certified Buyer' tag somewhere
            verified_tags = soup.find_all(lambda tag: tag.name == "span" and ("Verified Purchase" in tag.text or "Certified Buyer" in tag.text))
            
            for tag in verified_tags:
                # Traverse up to the main review wrapper
                wrapper = tag.parent.parent.parent
                if not wrapper or wrapper.name != 'div':
                    wrapper = tag.parent.parent
                
                # The review text body is typically the largest block of text inside this wrapper
                # that isn't the title or metadata. Let's extract all div texts.
                candidate_texts = []
                for div in wrapper.find_all('div', recursive=True):
                    # Direct text of the div without children text
                    direct_texts = [text for text in div.stripped_strings if text]
                    if direct_texts:
                        # Join them just in case
                        full_text = " ".join(direct_texts)
                        candidate_texts.append(full_text)
                
                # Filter out known metadata substrings
                cleaned_candidates = [
                    t for t in candidate_texts 
                    if len(t) > 15 
                    and "Verified Purchase" not in t 
                    and "Certified Buyer" not in t 
                    and "Review for:" not in t
                    and "days ago" not in t
                    and "months ago" not in t
                    and "Helpful for" not in t
                    and "READ MORE" not in t
                    and not t.startswith("5.0 ")
                    and not t.startswith("4.0 ")
                    and not t.startswith("3.0 ")
                    and not t.startswith("2.0 ")
                    and not t.startswith("1.0 ")
                ]
                
                if cleaned_candidates:
                    # Usually the review body is the longest surviving candidate
                    longest_text = max(cleaned_candidates, key=len)
                    
                    # Clean the read more artifact if it sneaked in
                    if longest_text.endswith("READ MORE"):
                        longest_text = longest_text[:-9].strip()
                        
                    if longest_text and longest_text not in reviews:
                        reviews.append(longest_text)
                        
            logger.info(f"Extracted {len(reviews)} reviews from page.")
        except Exception as e:
            logger.error(f"Failed to extract review texts: {e}")
            
        return reviews

    def go_to_next_page(self) -> bool:
        try:
            # Flipkart next button usually has span 'Next'
            next_button = self.driver.find_element(By.XPATH, "//span[text()='Next']/parent::a")
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)  # Wait for staleness
            return True
        except NoSuchElementException:
            return False
