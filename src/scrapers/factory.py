import urllib.parse

from src.core.exceptions import WebsiteNotSupportedException
from src.scrapers.base import BaseScraper
from src.scrapers.websites.amazon import AmazonScraper


def get_scraper_for_url(url: str) -> BaseScraper:
    domain = urllib.parse.urlparse(url).netloc.lower()

    if "amazon" in domain:
        return AmazonScraper(url)

    raise WebsiteNotSupportedException(f"No scraper implemented for domain: {domain}")
