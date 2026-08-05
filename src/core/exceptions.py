class ScraperBaseException(Exception):
    """Base exception for scraper operations."""

    pass


class WebsiteNotSupportedException(ScraperBaseException):
    """Raised when the requested website is not supported."""

    pass


class SelectorsNotFoundException(ScraperBaseException):
    """Raised when selectors are missing for a website."""

    pass


class ElementNotFoundException(ScraperBaseException):
    """Raised when a crucial element (like pagination) is not found."""

    pass
