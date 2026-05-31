"""
transaction_normalizer.py — Map raw transaction type strings to canonical categories.

Normalisation is case-insensitive and whitespace-tolerant, matching the spec:
  "Column headers are case-insensitive with leading/trailing spaces trimmed"

Canonical :class:`TransactionCategory` values are used throughout the
validator, transaction_processor, and xirr_calculator services.
The original (display) string is preserved in ``Transaction.transactionType``.
"""

from app.utils.constants import (
    TransactionCategory,
    PURCHASE_VARIANTS,
    SELL_VARIANTS,
    REDEMPTION_VARIANTS,
    DIVIDEND_REINVEST_VARIANTS,
    STAMP_DUTY_VARIANTS,
    ALL_KNOWN_VARIANTS,
    ErrorMessages,
)


def get_category(raw: str, row: int) -> TransactionCategory:
    """Return the canonical :class:`TransactionCategory` for a raw type string.

    Matching is performed after lower-casing and stripping the input.

    Parameters
    ----------
    raw:
        The raw transaction type value from the Excel cell (already stripped).
    row:
        1-based data row index used in error messages.

    Returns
    -------
    TransactionCategory

    Raises
    ------
    ValueError
        When the raw value does not match any known transaction type variant.
    """
    key = raw.strip().lower()

    if key in PURCHASE_VARIANTS:
        return TransactionCategory.PURCHASE
    if key in SELL_VARIANTS:
        return TransactionCategory.SELL
    if key in REDEMPTION_VARIANTS:
        return TransactionCategory.REDEMPTION
    if key in DIVIDEND_REINVEST_VARIANTS:
        return TransactionCategory.DIVIDEND_REINVEST
    if key in STAMP_DUTY_VARIANTS:
        return TransactionCategory.STAMP_DUTY

    raise ValueError(
        ErrorMessages.UNKNOWN_TRANSACTION_TYPE.format(row=row, value=raw)
    )


def is_known_type(raw: str) -> bool:
    """Return ``True`` if *raw* matches any known transaction type variant.

    Useful for quick membership checks without needing a row number.
    """
    return raw.strip().lower() in ALL_KNOWN_VARIANTS
