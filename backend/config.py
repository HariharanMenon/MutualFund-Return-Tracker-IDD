"""
config.py — Application-wide configuration and constants.
All tunable limits and environment-driven settings live here.
"""

from datetime import date


# ============================================================
# File constraints
# ============================================================
MAX_FILE_SIZE: int = 10 * 1024 * 1024   # 10 MB in bytes
MAX_TRANSACTIONS: int = 10_000           # maximum rows allowed
ALLOWED_EXTENSIONS: tuple[str, ...] = (".xlsx",)

# ============================================================
# Date constraints
# ============================================================
MIN_DATE: date = date(1960, 1, 1)
MAX_DATE: date = date.today          # evaluated at runtime via property

DATE_FORMAT: str = "DD-MMM-YYYY"     # display label for error messages
# strptime conversion code used internally
_DATE_STRPTIME: str = "%d-%b-%Y"    # e.g.  15-Jan-2020

# ============================================================
# Required Excel column names (normalised: lowercase + stripped)
# ============================================================
REQUIRED_COLUMNS: list[str] = [
    "date",
    "transaction type",
    "amount",
    "units",
    "price",
    "unit balance",
]

# ============================================================
# CORS
# ============================================================
CORS_ALLOW_ORIGINS: list[str] = ["*"]
CORS_ALLOW_METHODS: list[str] = ["*"]
CORS_ALLOW_HEADERS: list[str] = ["*"]

# ============================================================
# API
# ============================================================
API_PREFIX: str = "/api"
