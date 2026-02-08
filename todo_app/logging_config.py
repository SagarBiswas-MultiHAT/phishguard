"""Logging configuration for the application."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .paths import get_user_config_dir

LOG_FILE_NAME = "todo-app.log"


def setup_logging(log_level: int = logging.INFO) -> None:
    """Configure rotating file logging for the app."""
    config_dir = get_user_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    log_path = Path(config_dir) / LOG_FILE_NAME

    handler = RotatingFileHandler(
        log_path,
        maxBytes=512 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(log_level)
    for existing in root.handlers:
        if isinstance(existing, RotatingFileHandler):
            return
    root.addHandler(handler)
