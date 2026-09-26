import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app.core.settings import settings


def setup_logging():
    log_dir = settings.logging.log_dir
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = str(settings.logging.log_file_path)

    rotating_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
        utc=True,
    )
    rotating_handler.suffix = "%Y-%m-%d"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    rotating_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=settings.logging.log_level,
        handlers=[rotating_handler, console_handler],
    )
