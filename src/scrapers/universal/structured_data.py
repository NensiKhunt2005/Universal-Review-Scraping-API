import json
from typing import List
from bs4 import BeautifulSoup
from src.core.logging import logger


class StructuredDataExtractor:
    """Extracts review texts from JSON-LD and Schema.org microdata."""

    @staticmethod
    def extract_reviews(soup: BeautifulSoup) -> List[str]:
        reviews = []
        
        # 1. JSON-LD Extraction
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                reviews.extend(StructuredDataExtractor._find_reviews_in_json(data))
            except Exception as e:
                logger.debug(f"JSON-LD parsing skipped: {e}")

        # 2. Schema.org Microdata Extraction (itemprop="reviewBody")
        microdata_elements = soup.find_all(attrs={"itemprop": "reviewBody"})
        for el in microdata_elements:
            text = el.get_text(strip=True)
            if text and text not in reviews:
                reviews.append(text)

        return reviews

    @staticmethod
    def _find_reviews_in_json(data) -> List[str]:
        found = []
        if isinstance(data, dict):
            # Direct Review object
            if data.get("@type") == "Review" and "reviewBody" in data:
                body = data["reviewBody"]
                if isinstance(body, str) and body.strip():
                    found.append(body.strip())
            
            # Recurse through dictionary values (e.g. Product -> review)
            for value in data.values():
                found.extend(StructuredDataExtractor._find_reviews_in_json(value))

        elif isinstance(data, list):
            for item in data:
                found.extend(StructuredDataExtractor._find_reviews_in_json(item))

        return found
