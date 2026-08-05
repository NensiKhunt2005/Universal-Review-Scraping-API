from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class ScrapeRequest(BaseModel):
    url: HttpUrl
    max_pages: Optional[int] = None
    drop_emojis: Optional[bool] = False
    remove_duplicates: Optional[bool] = True


class ScrapeResponse(BaseModel):
    website: str
    total_reviews: int
    reviews: List[str]


class ErrorResponse(BaseModel):
    detail: str
