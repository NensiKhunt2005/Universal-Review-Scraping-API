import logging
import sys

from src.core.config import settings


def setup_logging():
    level_str = settings.logging.level if settings else "INFO"
    level = getattr(logging, level_str.upper(), logging.INFO)

    logger = logging.getLogger("scraper_api")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logging()
