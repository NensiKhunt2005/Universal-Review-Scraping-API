from src.services.cleaner import TextCleaner
from src.services.deduplicator import Deduplicator


def test_remove_html():
    cleaned = TextCleaner.process("<p>Test <b>HTML</b></p>")
    assert cleaned == "Test HTML"


def test_clean_whitespace():
    cleaned = TextCleaner.process("Lots \n\t of   space.   ")
    assert cleaned == "Lots of space."


def test_remove_emojis():
    cleaned = TextCleaner.process("Hello 😀 World 😊", drop_emojis=True)
    assert cleaned.strip() == "Hello  World"


def test_deduplicator():
    reviews = ["Great product", "great product", "Bad product"]
    dedup = Deduplicator.remove_normalized_duplicates(reviews)
    assert len(dedup) == 2
    assert "Great product" in dedup
    assert "Bad product" in dedup
