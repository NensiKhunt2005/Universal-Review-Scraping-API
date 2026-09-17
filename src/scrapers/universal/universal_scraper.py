import time
from typing import List
from bs4 import BeautifulSoup

from src.core.logging import logger
from src.scrapers.base import BaseScraper
from src.scrapers.universal.candidate_detector import ReviewCandidateDetector
from src.scrapers.universal.confidence_scorer import ConfidenceScorer
from src.scrapers.universal.dom_analyzer import DOMAnalyzer
from src.scrapers.universal.navigation import NavigationDetector
from src.scrapers.universal.structured_data import StructuredDataExtractor
from src.scrapers.universal.text_extractor import ReviewTextExtractor


class UniversalScraper(BaseScraper):
    """Site-independent Universal Review Scraper."""

    def __init__(self, url: str):
        super().__init__(url)

    def navigate_to_reviews(self):
        if not self.driver:
            return
        try:
            # Universal attempt to find and click links containing "all reviews" or "customer reviews"
            buttons = self.driver.find_elements(
                "xpath",
                "//a[contains(translate(text(), 'REVIEWS', 'reviews'), 'review')] | "
                "//button[contains(translate(text(), 'REVIEWS', 'reviews'), 'review')]"
            )
            if buttons:
                for btn in buttons[:3]:
                    if btn.is_displayed() and btn.is_enabled():
                        self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(2)
                        break
        except Exception as e:
            logger.debug(f"Universal navigate_to_reviews notice: {e}")

    def extract_reviews_from_page(self) -> List[str]:
        if not self.driver:
            return []

        reviews: List[str] = []
        try:
            # Expand truncated "Read More" controls
            ReviewTextExtractor.expand_read_more_controls(self.driver)

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Level 1: Structured Data (JSON-LD & Schema.org)
            structured_reviews = StructuredDataExtractor.extract_reviews(soup)
            for r in structured_reviews:
                score = ConfidenceScorer.calculate_score(r, is_structured=True)
                if ConfidenceScorer.is_acceptable(score) and r not in reviews:
                    reviews.append(r)

            # Level 2-6: Heuristic DOM Evidence Anchors & Containers
            evidence_anchors = ReviewCandidateDetector.find_evidence_tags(soup)
            for anchor_tag, evidence_score in evidence_anchors:
                container = DOMAnalyzer.find_card_boundary(anchor_tag)
                if not container:
                    continue

                review_text = ReviewTextExtractor.extract_from_container(container)
                if review_text:
                    score = ConfidenceScorer.calculate_score(review_text, evidence_score=evidence_score)
                    if ConfidenceScorer.is_acceptable(score) and review_text not in reviews:
                        reviews.append(review_text)

            # Fallback: Find direct <p> tags with natural language text if no evidence anchors matched
            if not reviews:
                for p in soup.find_all("p"):
                    text = p.get_text(strip=True)
                    score = ConfidenceScorer.calculate_score(text, evidence_score=0.4)
                    if ConfidenceScorer.is_acceptable(score) and text not in reviews:
                        reviews.append(text)

            logger.info(f"UniversalScraper extracted {len(reviews)} reviews.")
        except Exception as e:
            logger.error(f"Error in UniversalScraper extraction: {e}")

        return reviews

    def go_to_next_page(self) -> bool:
        if not self.driver:
            return False
        return NavigationDetector.click_next_page(self.driver)
