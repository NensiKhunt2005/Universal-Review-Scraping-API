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
        if not self.driver:
            logger.warning("WebDriver is not initialized. Cannot navigate to reviews.")
            return
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
        if not self.driver:
            logger.warning("WebDriver is not initialized. Cannot extract reviews.")
            return []
        reviews = []
        try:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Flipkart unique DOM structure identifiers 
            # Review blocks almost always contain a 'Verified Purchase' or 'Certified Buyer' tag somewhere
            # Find all matching tags (span, div, p) containing these keywords
            all_matches = soup.find_all(lambda tag: tag.name in ["span", "div", "p"] and ("Verified Purchase" in tag.text or "Certified Buyer" in tag.text))
            
            # Filter to get the leaf-most (deepest) elements to avoid outer container divs
            verified_tags = []
            for tag in all_matches:
                has_child_match = any(
                    child.name in ["span", "div", "p"] and ("Verified Purchase" in child.text or "Certified Buyer" in child.text)
                    for child in tag.find_all()
                )
                if not has_child_match:
                    verified_tags.append(tag)
            
            for tag in verified_tags:
                # Traverse up to the main review wrapper
                # On responsive/mobile layout, the tag is a 'div' and the card is 5 levels up.
                # On older/desktop layout, the tag is usually a 'span' or 'p' and the card is 2-3 levels up.
                if tag.name == "div":
                    wrapper = tag
                    for _ in range(5):
                        if wrapper.parent:
                            wrapper = wrapper.parent
                else:
                    wrapper = tag.parent.parent.parent
                    if not wrapper or wrapper.name != 'div':
                        wrapper = tag.parent.parent
                
                if not wrapper:
                    continue
                
                # Extract review body
                review_text = None
                
                # 1. Try to find the review body span (specific to the responsive layout where only 1 span is used for review body)
                spans = wrapper.find_all("span")
                valid_spans = []
                for s in spans:
                    text = s.text.strip()
                    if (
                        text
                        and "Verified Purchase" not in text
                        and "Certified Buyer" not in text
                        and "Helpful" not in text
                        and "Review for:" not in text
                        and "days ago" not in text
                        and "months ago" not in text
                        and not text.endswith("ago")
                    ):
                        valid_spans.append(text)
                        
                if valid_spans:
                    review_text = max(valid_spans, key=len)
                
                # 2. Fallback to candidate text extraction (older layout compatibility)
                if not review_text:
                    candidate_texts = []
                    for div in wrapper.find_all(['div', 'span'], recursive=True):
                        # Direct text of the div without children text
                        direct_texts = [text for text in div.stripped_strings if text]
                        if direct_texts:
                            # Join them just in case
                            full_text = " ".join(direct_texts)
                            candidate_texts.append(full_text)
                    
                    # Filter out known metadata substrings
                    cleaned_candidates = [
                        t for t in candidate_texts 
                        if len(t) > 5 
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
                        and not t.endswith("ago")
                    ]
                    
                    if cleaned_candidates:
                        # Usually the review body is the longest surviving candidate
                        review_text = max(cleaned_candidates, key=len)
                        
                if isinstance(review_text, str):
                    # Clean the read more artifact if it sneaked in
                    if review_text.endswith("READ MORE"):
                        review_text = review_text[:-9].strip()
                        
                    if review_text and review_text not in reviews:
                        reviews.append(review_text)
                        
            logger.info(f"Extracted {len(reviews)} reviews from page.")
        except Exception as e:
            logger.error(f"Failed to extract review texts: {e}")
            
        return reviews

    def go_to_next_page(self) -> bool:
        if not self.driver:
            logger.warning("WebDriver is not initialized. Cannot navigate to next page.")
            return False
        try:
            # Flipkart next button usually has span 'Next'
            next_button = self.driver.find_element(By.XPATH, "//span[text()='Next']/parent::a")
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)  # Wait for staleness
            return True
        except NoSuchElementException:
            return False
