import csv
import json
import os
import sqlite3
from typing import Dict

from src.core.config import settings
from src.core.logging import logger


class StorageExporter:
    def __init__(self, export_dir: str = None):
        self.export_dir = export_dir or (
            settings.storage.export_dir if settings else "exports"
        )
        os.makedirs(self.export_dir, exist_ok=True)

    def to_json(self, data: Dict, filename: str = "reviews.json") -> str:
        filepath = os.path.join(self.export_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Exported data to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
            raise

    def to_csv(self, data: Dict, filename: str = "reviews.csv") -> str:
        filepath = os.path.join(self.export_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Website", "Review"])
                website = data.get("website", "unknown")
                for review in data.get("reviews", []):
                    writer.writerow([website, review])
            logger.info(f"Exported data to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            raise

    def to_sqlite(self, data: Dict) -> str:
        db_path = os.path.join(
            self.export_dir,
            settings.storage.sqlite_db_path if settings else "scraper.db",
        )
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    website TEXT,
                    review_text TEXT
                )
            """)
            website = data.get("website", "unknown")
            records = [(website, r) for r in data.get("reviews", [])]
            cursor.executemany(
                "INSERT INTO reviews (website, review_text) VALUES (?, ?)", records
            )
            conn.commit()
            conn.close()
            logger.info(f"Exported data to SQLite database at {db_path}")
            return db_path
        except Exception as e:
            logger.error(f"Failed to export SQLite: {e}")
            raise
