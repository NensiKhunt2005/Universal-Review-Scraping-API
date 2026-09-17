import hashlib
import time
from typing import List, Set
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.core.logging import logger


class NavigationDetector:
    """Universal navigation and pagination detector."""

    @staticmethod
    def click_next_page(driver: WebDriver) -> bool:
        if not driver:
            return False

        xpath_query = (
            "//a[contains(translate(text(), 'NEXT', 'next'), 'next')] | "
            "//button[contains(translate(text(), 'NEXT', 'next'), 'next')] | "
            "//a[@rel='next'] | //a[contains(text(), '›')] | //a[contains(text(), '>')]"
        )

        try:
            buttons = driver.find_elements(By.XPATH, xpath_query)
            for btn in buttons:
                if btn.is_displayed() and btn.is_enabled():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(2.5)
                    return True
        except Exception as e:
            logger.debug(f"Next page navigation skipped: {e}")

        return False


class InfiniteScrollHandler:
    """Handles dynamic infinite scroll with DOM hash tracking."""

    def __init__(self):
        self.seen_hashes: Set[str] = set()

    def has_new_content(self, current_reviews: List[str]) -> bool:
        new_count = 0
        for r in current_reviews:
            r_hash = hashlib.md5(r.encode('utf-8')).hexdigest()
            if r_hash not in self.seen_hashes:
                self.seen_hashes.add(r_hash)
                new_count += 1
        return new_count > 0
