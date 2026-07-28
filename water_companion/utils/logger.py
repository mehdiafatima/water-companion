"""
logger.py
=========
Centralised logging configuration for Water Companion.

Usage:
    from water_companion.utils.logger import get_logger
    log = get_logger(__name__)
    log.info("Hello")
"""

import logging
import logging.handlers
from pathlib import Path

from water_companion.utils.constants import APP_NAME, LOG_FILE


def _ensure_log_dir() -> None:
    """Create the log file's parent directory if it does not exist."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure root logger with:
    - A rotating file handler  (max 2 MB × 3 backups)
    - A console handler        (for CLI feedback)

    Call once at app startup.
    """
    _ensure_log_dir()

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(level)

    # ── File handler (rotating) ──────────────────────────────────────────
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=2 * 1024 * 1024,   # 2 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    # ── Console handler ──────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    root.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.  Always call this instead of logging.getLogger()
    directly so that future centralised changes are painless.
    """
    return logging.getLogger(name)
