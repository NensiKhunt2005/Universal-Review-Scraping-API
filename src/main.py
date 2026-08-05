from fastapi import FastAPI

from src.api.routes import router
from src.core.config import settings

app = FastAPI(
    title=settings.app.name if settings else "Review Scraping API",
    version=settings.app.version if settings else "1.0.0",
    description="Universal API for structured e-commerce product reviews.",
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
