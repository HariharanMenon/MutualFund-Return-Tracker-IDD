"""
constants.py — All domain constants: transaction type sets, categories,
XIRR/summary groupings, error message templates, column metadata.

This is the single source of truth for string literals used across
file_parser, validator, transaction_processor, and xirr_calculator.
"""

from enum import Enum


# ============================================================
# Transaction categories (canonical values used internally)
# ============================================================

class TransactionCategory(str, Enum):
    """Canonical transaction categories after normalisation."""
    PURCHASE = "PURCHASE"
    SELL = "SELL"
    REDEMPTION = "REDEMPTION"
    DIVIDEND_REINVEST = "DIVIDEND_REINVEST"
    STAMP_DUTY = "STAMP_DUTY"


# ============================================================
# Recognised variant strings per category  (all lower-cased)
# Matching is done after lower() + strip() on the input value.
# ============================================================

PURCHASE_VARIANTS: frozenset[str] = frozenset({
    "purchase",
    "buy",
    "sip",
    "sip purchase",
    "systematic investment",
    "systematic investment plan",
})

SELL_VARIANTS: frozenset[str] = frozenset({
    "sell",
})

REDEMPTION_VARIANTS: frozenset[str] = frozenset({
    "redemption",
})

DIVIDEND_REINVEST_VARIANTS: frozenset[str] = frozenset({
    "dividend reinvest",
    "dividend reinvestment",
})

STAMP_DUTY_VARIANTS: frozenset[str] = frozenset({
    "stamp duty",
    "stt paid",
})

# Union of every known variant — used to reject unrecognised types
ALL_KNOWN_VARIANTS: frozenset[str] = (
    PURCHASE_VARIANTS
    | SELL_VARIANTS
    | REDEMPTION_VARIANTS
    | DIVIDEND_REINVEST_VARIANTS
    | STAMP_DUTY_VARIANTS
)


# ============================================================
# Functional groupings used by services
# ============================================================

# Categories that produce a NEGATIVE cash flow for XIRR (money out)
XIRR_OUTFLOW_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.PURCHASE,
    TransactionCategory.DIVIDEND_REINVEST,
})

# Categories that produce a POSITIVE cash flow for XIRR (money in)
XIRR_INFLOW_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.SELL,
    TransactionCategory.REDEMPTION,
})

# Categories excluded from XIRR cash-flow arrays entirely
XIRR_EXCLUDED_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.STAMP_DUTY,
})

# Categories whose amounts sum to Total Invested (summary metric)
# Spec §7: "Sum of all PURCHASE/Buy/SIP/Systematic Investment/Stamp Duty/STT Paid"
TOTAL_INVESTED_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.PURCHASE,
    TransactionCategory.STAMP_DUTY,
})

# Valid categories for the terminal (last) transaction
TERMINAL_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.SELL,
    TransactionCategory.REDEMPTION,
})

# Categories that MUST have empty Price and Unit Balance columns
PRICE_UNIT_BALANCE_EMPTY_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.SELL,
    TransactionCategory.REDEMPTION,
    TransactionCategory.STAMP_DUTY,
})

# Categories where Units is OPTIONAL (can be empty, not a validation error)
UNITS_OPTIONAL_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.STAMP_DUTY,
})

# Categories that REQUIRE Units to be populated
UNITS_REQUIRED_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.PURCHASE,
    TransactionCategory.SELL,
    TransactionCategory.REDEMPTION,
    TransactionCategory.DIVIDEND_REINVEST,
})

# Categories that REQUIRE Price and Unit Balance to be populated
PRICE_UNIT_BALANCE_REQUIRED_CATEGORIES: frozenset[TransactionCategory] = frozenset({
    TransactionCategory.PURCHASE,
    TransactionCategory.DIVIDEND_REINVEST,
})


# ============================================================
# Excel column names (normalised: lowercase + stripped)
# ============================================================

COL_DATE: str = "date"
COL_TRANSACTION_TYPE: str = "transaction type"
COL_AMOUNT: str = "amount"
COL_UNITS: str = "units"
COL_PRICE: str = "price"
COL_UNIT_BALANCE: str = "unit balance"

REQUIRED_COLUMNS: list[str] = [
    COL_DATE,
    COL_TRANSACTION_TYPE,
    COL_AMOUNT,
    COL_UNITS,
    COL_PRICE,
    COL_UNIT_BALANCE,
]

# Columns that are strictly required at the file level (must be present as headers)
MANDATORY_HEADER_COLUMNS: list[str] = [
    COL_DATE,
    COL_TRANSACTION_TYPE,
    COL_AMOUNT,
]


# ============================================================
# Error message templates
# All row-level errors use 1-based row numbers (header = row 0).
# ============================================================

class ErrorMessages:
    """Static error message templates matching the spec exactly."""

    # --- Column / header errors ---
    MISSING_COLUMN = "Missing required column: {column}"

    # --- Date errors ---
    INVALID_DATE_FORMAT = (
        "Row {row}: Invalid date format '{value}' "
        "(expected DD-MMM-YYYY, e.g., 15-Jan-2020)"
    )
    DATE_BEFORE_MIN = (
        "Row {row}: Transaction date '{value}' is before 1960; cannot process"
    )
    DATE_IN_FUTURE = (
        "Row {row}: Transaction date '{value}' is in the future; cannot process"
    )

    # --- Transaction type errors ---
    UNKNOWN_TRANSACTION_TYPE = (
        "Row {row}: Unrecognised transaction type '{value}'"
    )

    # --- Numeric / amount errors ---
    NON_NUMERIC_AMOUNT = "Row {row}: Amount must be numeric; got '{value}'"
    NEGATIVE_AMOUNT = "Row {row}: Amount must be positive; got '{value}'"
    NON_NUMERIC_UNITS = "Row {row}: Units must be numeric; got '{value}'"
    NEGATIVE_UNITS = "Row {row}: Units must be positive; got '{value}'"
    NON_NUMERIC_PRICE = "Row {row}: Price must be numeric; got '{value}'"
    NEGATIVE_PRICE = "Row {row}: Price must be positive; got '{value}'"
    NON_NUMERIC_UNIT_BALANCE = "Row {row}: Unit Balance must be numeric; got '{value}'"
    NEGATIVE_UNIT_BALANCE = "Row {row}: Unit Balance must be positive; got '{value}'"

    # --- Conditional field errors ---
    SELL_MISSING_UNITS = (
        "Row {row}: SELL/REDEMPTION transaction must have Units field populated"
    )
    STAMP_DUTY_NON_EMPTY_PRICE_UNIT_BALANCE = (
        "Row {row}: Stamp Duty transaction must have empty Price and Unit Balance columns"
    )
    SELL_NON_EMPTY_PRICE_UNIT_BALANCE = (
        "Row {row}: SELL/REDEMPTION transaction must have empty Price and Unit Balance columns"
    )
    PURCHASE_MISSING_PRICE = (
        "Row {row}: {tx_type} transaction must have Price populated"
    )
    PURCHASE_MISSING_UNIT_BALANCE = (
        "Row {row}: {tx_type} transaction must have Unit Balance populated"
    )
    PURCHASE_MISSING_UNITS = (
        "Row {row}: {tx_type} transaction must have Units populated"
    )

    # --- File-level errors ---
    INSUFFICIENT_TRANSACTIONS = (
        "Insufficient data: At least 2 transactions required (1 investment + 1 redemption)"
    )
    TOO_MANY_TRANSACTIONS = (
        "File too large: Maximum {max_rows:,} transactions allowed "
        "(your file has {actual_rows:,})"
    )
    MISSING_FINAL_REDEMPTION = (
        "Final redemption missing: Last transaction must be SELL/REDEMPTION with Unit Balance = 0"
    )
    LAST_NOT_SELL_OR_REDEMPTION = (
        "Last transaction must be SELL or REDEMPTION; found: {tx_type}"
    )
    UNIT_BALANCE_MISMATCH = (
        "Row {row}: Unit Balance '{balance}' doesn't match cumulative units '{cumulative}'"
    )

    # --- File parsing errors ---
    FILE_CANNOT_BE_READ = "File could not be read. Please upload a valid .xlsx file."
    FILE_TOO_LARGE = "File size exceeds 10 MB limit"
    EMPTY_FILE = "The uploaded file contains no data rows."

    # --- XIRR errors ---
    XIRR_CONVERGENCE_FAILURE = (
        "Cannot calculate XIRR for this data. Please verify all transactions."
    )


# ============================================================
# Decimal precision rules (for rounding in output)
# ============================================================

DECIMAL_PLACES_AMOUNT: int = 2
DECIMAL_PLACES_UNITS: int = 3
DECIMAL_PLACES_XIRR: int = 2
# Price: preserved as-is (2–4 decimals per user entry, not modified)

# Tolerance for unit balance consistency check (floating-point rounding)
UNIT_BALANCE_TOLERANCE: float = 0.005

# ============================================================
# File-level limits (mirrors config.py — single source for services)
# ============================================================
MAX_TRANSACTIONS: int = 10_000
MIN_TRANSACTIONS: int = 2
