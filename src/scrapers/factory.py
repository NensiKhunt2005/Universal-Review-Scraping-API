import urllib.parse

from src.core.exceptions import WebsiteNotSupportedException
from src.scrapers.base import BaseScraper
from src.scrapers.websites.amazon import AmazonScraper
from src.scrapers.websites.flipkart import FlipkartScraper
from src.scrapers.websites.generic import GenericScraper


def get_scraper_for_url(url: str) -> BaseScraper:
    domain = urllib.parse.urlparse(url).netloc.lower()

    if "amazon" in domain:
        return AmazonScraper(url)
    if "flipkart" in domain:
        return FlipkartScraper(url)

    # Use Universal Config-Driven Scraper for anything else
    return GenericScraper(url)
