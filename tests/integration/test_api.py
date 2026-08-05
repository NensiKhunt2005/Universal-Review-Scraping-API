import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.scrapers.base import BaseScraper

client = TestClient(app)


class MockAmazonScraper(BaseScraper):
    def __init__(self, url):
        self.url = url

    def navigate_to_reviews(self):
        pass

    def extract_reviews_from_page(self):
        return ["Mock Amazon Review 1", "Mock Amazon Review 2", "mock amazon review 1"]

    def go_to_next_page(self):
        return False

    def scrape(self, max_pages=1):
        # Override scrape to bypass the real browser entirely for CI environments
        return self.extract_reviews_from_page()


@pytest.fixture
def override_scraper(monkeypatch):
    def mock_get_scraper(url: str):
        if "amazon" in url:
            return MockAmazonScraper(url)
        raise Exception("Unsupported")

    monkeypatch.setattr("src.api.routes.get_scraper_for_url", mock_get_scraper)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_scrape_amazon(override_scraper):
    payload = {"url": "https://www.amazon.com/dp/123", "remove_duplicates": True}
    response = client.post("/api/v1/scrape", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_reviews"] == 2  # 3 raw -> 2 after deduplication
    assert len(data["reviews"]) == 2
