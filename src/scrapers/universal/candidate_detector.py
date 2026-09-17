import re
from typing import List, Tuple
from bs4 import BeautifulSoup, Tag

VERIFICATION_KEYWORDS = [
    "verified purchase", "certified buyer", "verified review",
    "compra verificada", "achat vérifié", "verifizierter kauf", "vásárlás"
]

HELPFUL_KEYWORDS = [
    "helpful", "helpful for", "was this helpful", "útil", "nützlich"
]

RATING_PATTERNS = [
    r'\b[1-5]\.0\b',
    r'\b[1-5]\s*★',
    r'\b[1-5]\s*out of\s*5\b',
    r'★'
]


class ReviewCandidateDetector:
    """Detects review evidence markers and candidate DOM elements."""

    @staticmethod
    def find_evidence_tags(soup: BeautifulSoup) -> List[Tuple[Tag, float]]:
        """
        Scans soup for elements matching verification, rating, or helpfulness markers.
        Returns list of (Tag, evidence_score).
        """
        candidates: List[Tuple[Tag, float]] = []

        # 1. Semantic containers
        for tag in soup.find_all(["article", "li"], recursive=True):
            if tag.get("role") == "article" or "review" in tag.get("class", []) or tag.name == "article":
                candidates.append((tag, 0.8))

        # 2. Text evidence anchors
        all_tags = soup.find_all(["span", "div", "p", "a"], recursive=True)
        for tag in all_tags:
            text = tag.get_text(strip=True).lower()
            if not text:
                continue

            score = 0.0
            if any(vk in text for vk in VERIFICATION_KEYWORDS):
                score += 0.9
            if any(hk in text for hk in HELPFUL_KEYWORDS):
                score += 0.5
            if any(re.search(pat, text, re.IGNORECASE) for pat in RATING_PATTERNS):
                score += 0.7

            if score > 0:
                # Keep only leaf-most tag for evidence anchor
                has_matching_child = any(
                    child.name in ["span", "div", "p", "a"] and
                    any(vk in child.get_text(strip=True).lower() for vk in VERIFICATION_KEYWORDS)
                    for child in tag.find_all()
                )
                if not has_matching_child:
                    candidates.append((tag, score))

        return candidates
