import os
import sqlite3
import csv
import json
import pytest
from src.storage.exporters import StorageExporter


@pytest.fixture
def mock_data():
    return {
        "website": "AmazonScraper",
        "total_reviews": 2,
        "reviews": ["Great product", "Not so great"]
    }


@pytest.fixture
def temp_export_dir(tmp_path):
    # tmp_path is a built-in pytest fixture for temporary directories
    d = tmp_path / "exports"
    d.mkdir()
    return str(d)


def test_to_json(mock_data, temp_export_dir):
    exporter = StorageExporter(export_dir=temp_export_dir)
    filepath = exporter.to_json(mock_data, "test_reviews.json")
    
    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["website"] == "AmazonScraper"
    assert len(data["reviews"]) == 2
    assert data["reviews"][0] == "Great product"


def test_to_csv(mock_data, temp_export_dir):
    exporter = StorageExporter(export_dir=temp_export_dir)
    filepath = exporter.to_csv(mock_data, "test_reviews.csv")
    
    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    assert len(rows) == 3 # Header + 2 reviews
    assert rows[0] == ["Website", "Review"]
    assert rows[1] == ["AmazonScraper", "Great product"]
    assert rows[2] == ["AmazonScraper", "Not so great"]


def test_to_sqlite(mock_data, temp_export_dir):
    exporter = StorageExporter(export_dir=temp_export_dir)
    # mock settings for db path or let it use default if we can't easily mock settings
    # Storage exporter uses settings.storage.sqlite_db_path. If settings is None it defaults to scraper.db
    # To isolate, we just use the default fallback or rely on the directory change
    filepath = exporter.to_sqlite(mock_data)
    
    assert os.path.exists(filepath)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT website, review_text FROM reviews")
    rows = cursor.fetchall()
    conn.close()
    
    assert len(rows) == 2
    assert rows[0] == ("AmazonScraper", "Great product")
    assert rows[1] == ("AmazonScraper", "Not so great")
