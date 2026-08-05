import re
import unicodedata

from bs4 import BeautifulSoup


class TextCleaner:
    @staticmethod
    def remove_html(text: str) -> str:
        """Removes all HTML tags from the given text."""
        return BeautifulSoup(text, "html.parser").get_text(separator=" ")

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Normalizes unicode characters."""
        return unicodedata.normalize("NFKD", text)

    @staticmethod
    def clean_whitespace(text: str) -> str:
        """Removes tabs, newlines, and duplicate spaces, then trims."""
        text = re.sub(r"[\n\t\r]+", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def remove_emojis(text: str) -> str:
        """Optionally remove emojis / non-ascii."""
        return text.encode("ascii", "ignore").decode("ascii")

    @classmethod
    def process(cls, text: str, drop_emojis: bool = False) -> str:
        """Full pipeline to safely clean raw review text."""
        if not text:
            return ""
        text = cls.remove_html(text)
        text = cls.normalize_unicode(text)
        text = cls.clean_whitespace(text)
        if drop_emojis:
            text = cls.remove_emojis(text)
        return text
