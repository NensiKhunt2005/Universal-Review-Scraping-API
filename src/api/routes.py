from fastapi import APIRouter, HTTPException

from src.core.exceptions import ScraperBaseException
from src.models.schemas import ScrapeRequest, ScrapeResponse
from src.scrapers.factory import get_scraper_for_url
from src.services.cleaner import TextCleaner
from src.services.deduplicator import Deduplicator
from src.storage.exporters import StorageExporter

router = APIRouter()
exporter = StorageExporter()


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_reviews(request: ScrapeRequest):
    url_str = str(request.url)
    try:
        scraper = get_scraper_for_url(url_str)
        raw_reviews = scraper.scrape(max_pages=request.max_pages)

        # Clean reviews
        cleaned_reviews = [
            TextCleaner.process(r, drop_emojis=request.drop_emojis) for r in raw_reviews
        ]

        # Deduplicate
        if request.remove_duplicates:
            cleaned_reviews = Deduplicator.remove_normalized_duplicates(cleaned_reviews)

        # Final output
        response_data = {
            "website": scraper.__class__.__name__,
            "total_reviews": len(cleaned_reviews),
            "reviews": cleaned_reviews,
        }

        # Optional: Save locally
        exporter.to_json(response_data, filename="latest_scrape.json")
        exporter.to_sqlite(response_data)

        return response_data

    except ScraperBaseException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
