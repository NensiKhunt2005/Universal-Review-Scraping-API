import re
from typing import Tuple

# Regex patterns for classification
DATE_PATTERN = re.compile(
    r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b|'
    r'\b(ago|days|months|years|yesterday|today)\b|'
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    re.IGNORECASE
)

RATING_PATTERN = re.compile(
    r'^\s*([1-5]\.0|[1-5]\s*★|[1-5]\s*out of\s*5|star rating|★+)\s*$',
    re.IGNORECASE
)

HELPFUL_PATTERN = re.compile(
    r'\b(helpful|was this helpful|found this helpful|people found|útil|nützlich)\b',
    re.IGNORECASE
)

VERIFIED_PATTERN = re.compile(
    r'\b(verified purchase|certified buyer|verified review|compra verificada|achat vérifié)\b',
    re.IGNORECASE
)

QNA_PATTERN = re.compile(
    r'^\s*(q:|a:|question:|answer:|asked by|answered by|\?)\s*|^\s*is this\b|\bdoes it work with\b',
    re.IGNORECASE
)

VARIANT_PATTERN = re.compile(
    r'\b(color:|size:|style:|quantity:|pattern:)\b',
    re.IGNORECASE
)


class MetadataClassifier:
    """Classifies text elements into metadata vs review content categories."""

    @staticmethod
    def classify(text: str) -> str:
        t = text.strip()
        if not t:
            return "OTHER"

        # Q&A Protection
        if QNA_PATTERN.search(t) or t.endswith("?"):
            return "QUESTION" if "?" in t else "ANSWER"

        # Rating
        if RATING_PATTERN.match(t):
            return "RATING"

        # Verified
        if VERIFIED_PATTERN.search(t):
            return "VERIFIED"

        # Helpful
        if HELPFUL_PATTERN.search(t):
            return "HELPFUL"

        # Date
        if DATE_PATTERN.search(t) and len(t) < 40:
            return "DATE"

        # Variant
        if VARIANT_PATTERN.search(t) and len(t) < 60:
            return "VARIANT"

        # Short author/location/read-more strings
        if t.endswith("READ MORE") or t.endswith("Read More"):
            return "NAVIGATION"

        if len(t) < 6 and not any(c in t for c in ['.', '!', '?']):
            return "OTHER"

        # Review content criteria: Minimum length & natural language
        if len(t) >= 12 or any(punct in t for punct in ['.', '!', '?', ',']):
            return "REVIEW"

        return "OTHER"
