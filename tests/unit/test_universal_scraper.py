import os
from unittest.mock import MagicMock
from bs4 import BeautifulSoup

from src.scrapers.universal.candidate_detector import ReviewCandidateDetector
from src.scrapers.universal.confidence_scorer import ConfidenceScorer
from src.scrapers.universal.dom_analyzer import DOMAnalyzer
from src.scrapers.universal.metadata_classifier import MetadataClassifier
from src.scrapers.universal.structured_data import StructuredDataExtractor
from src.scrapers.universal.universal_scraper import UniversalScraper

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "html")


def load_fixture(filename: str) -> str:
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_structured_data_extractor():
    html = """
    <html>
    <script type="application/ld+json">
    {
      "@type": "Product",
      "name": "Headphones",
      "review": {
        "@type": "Review",
        "reviewBody": "JSON-LD review text is working great!"
      }
    }
    </script>
    <body><div itemprop="reviewBody">Microdata review text is also working!</div></body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    reviews = StructuredDataExtractor.extract_reviews(soup)
    assert len(reviews) == 2
    assert "JSON-LD review text is working great!" in reviews
    assert "Microdata review text is also working!" in reviews


def test_metadata_classifier():
    assert MetadataClassifier.classify("5.0") == "RATING"
    assert MetadataClassifier.classify("Verified Purchase") == "VERIFIED"
    assert MetadataClassifier.classify("August 15, 2026") == "DATE"
    assert MetadataClassifier.classify("Q: Is this compatible with Mac?") == "QUESTION"
    assert MetadataClassifier.classify("A: Yes it is compatible.") == "ANSWER"
    assert MetadataClassifier.classify("These headphones are amazing!") == "REVIEW"


def test_confidence_scorer_qna_rejection():
    review_score = ConfidenceScorer.calculate_score("Great battery life and sound.", evidence_score=0.8)
    qna_score = ConfidenceScorer.calculate_score("Q: Is this waterproof?", evidence_score=0.8)

    assert ConfidenceScorer.is_acceptable(review_score) is True
    assert ConfidenceScorer.is_acceptable(qna_score) is False


def test_universal_scraper_layout_a_semantic():
    html = load_fixture("layout_a_semantic.html")
    scraper = UniversalScraper("https://example-shop.com/item")
    scraper.driver = MagicMock()
    scraper.driver.page_source = html

    reviews = scraper.extract_reviews_from_page()
    assert len(reviews) == 2
    assert "These headphones are amazing! The sound quality is top-notch and battery lasts all day." in reviews
    assert "Good value for money. Comfortable fit for long listening sessions." in reviews


def test_universal_scraper_layout_b_nested():
    html = load_fixture("layout_b_nested.html")
    scraper = UniversalScraper("https://example-shop.com/item")
    scraper.driver = MagicMock()
    scraper.driver.page_source = html

    reviews = scraper.extract_reviews_from_page()
    assert len(reviews) >= 1
    assert any("build quality is impressive" in r for r in reviews)


def test_universal_scraper_layout_c_random_css():
    html = load_fixture("layout_c_random_css.html")
    scraper = UniversalScraper("https://example-shop.com/item")
    scraper.driver = MagicMock()
    scraper.driver.page_source = html

    reviews = scraper.extract_reviews_from_page()
    assert len(reviews) == 2
    assert any("Super fast shipping" in r for r in reviews)
    assert any("Color did not match" in r for r in reviews)


def test_universal_scraper_layout_d_no_rating():
    html = load_fixture("layout_d_no_rating.html")
    scraper = UniversalScraper("https://example-shop.com/item")
    scraper.driver = MagicMock()
    scraper.driver.page_source = html

    reviews = scraper.extract_reviews_from_page()
    assert len(reviews) == 2
    assert any("soft padding makes this product so comfortable" in r for r in reviews)


def test_universal_scraper_layout_e_qna_rejection():
    html = load_fixture("layout_e_qna_section.html")
    scraper = UniversalScraper("https://example-shop.com/item")
    scraper.driver = MagicMock()
    scraper.driver.page_source = html

    reviews = scraper.extract_reviews_from_page()
    # Q&A section should produce 0 review texts (false positive protection)
    assert len(reviews) == 0
