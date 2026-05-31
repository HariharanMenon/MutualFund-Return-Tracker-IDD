"""
logger.py — Lightweight structured logging utility.

Uses Python's stdlib `logging` module. A single application logger
is configured here; all modules import `get_logger()` to obtain a
named child logger.

Render free tier note: logs are ephemeral (per spec §15). No file
handlers are configured — stdout only.
"""

import logging
import sys


def _configure_root() -> None:
    """Configure the root logger once at import time."""
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g., during tests) — leave as-is.
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(logging.INFO)


_configure_root()


def get_logger(name: str) -> logging.Logger:
    """Return a named child logger.

    Usage::

        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Processing file: %s", filename)
    """
    return logging.getLogger(name)
