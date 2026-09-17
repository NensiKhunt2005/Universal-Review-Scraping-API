from typing import List, Optional
from bs4 import BeautifulSoup, Tag
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from src.core.logging import logger
from src.scrapers.universal.metadata_classifier import MetadataClassifier


class ReviewTextExtractor:
    """Extracts, cleans, and merges review text from card containers."""

    @staticmethod
    def extract_from_container(container: Tag) -> Optional[str]:
        """Extracts and merges review text from a card container."""
        review_parts = []

        # Find paragraph elements first (semantic review bodies)
        p_tags = container.find_all("p", recursive=True)
        if p_tags:
            for p in p_tags:
                text = p.get_text(strip=True)
                category = MetadataClassifier.classify(text)
                if category == "REVIEW":
                    review_parts.append(text)

        # Fallback to direct text nodes if no <p> tags matched
        if not review_parts:
            for el in container.find_all(["div", "span"], recursive=True):
                # Avoid elements with matching children to prevent duplicating child text
                if any(child.name in ["div", "span", "p"] for child in el.find_all()):
                    continue

                text = el.get_text(strip=True)
                category = MetadataClassifier.classify(text)
                if category == "REVIEW" and text not in review_parts:
                    review_parts.append(text)

        if not review_parts:
            return None

        # Clean trailing "READ MORE" artifacts
        full_text = "\n".join(review_parts)
        if full_text.endswith("READ MORE"):
            full_text = full_text[:-9].strip()
        elif full_text.endswith("Read More"):
            full_text = full_text[:-9].strip()

        return full_text if len(full_text) >= 10 else None

    @staticmethod
    def expand_read_more_controls(driver: WebDriver):
        """Finds and clicks generic Read More / Show More buttons on the page."""
        if not driver:
            return

        try:
            buttons = driver.find_elements(
                By.XPATH,
                "//button[contains(translate(text(), 'READ MORE', 'read more'), 'read more') or contains(text(), 'Show more') or contains(text(), 'See more')] | "
                "//a[contains(translate(text(), 'READ MORE', 'read more'), 'read more') or contains(text(), 'Show more')]"
            )
            for btn in buttons[:10]:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].click();", btn)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Read More expansion skipped: {e}")
