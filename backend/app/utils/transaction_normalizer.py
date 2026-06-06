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
    GROSS_PURCHASE_VARIANTS,
    ALL_KNOWN_VARIANTS,
    CATEGORY_KEYWORDS,
    ErrorMessages,
)


def get_category(raw: str, row: int) -> TransactionCategory:
    """Return the canonical :class:`TransactionCategory` for a raw type string.

    Matching uses a two-tier strategy:

    **Tier 1 — Exact match** (fast path):
        Lower-cased, stripped input is checked against each known variant
        frozenset. Handles all values explicitly listed in ``constants.py``.

    **Tier 2 — Keyword-contains fallback**:
        If Tier 1 finds no match, the input is tested for substring
        containment against ``CATEGORY_KEYWORDS`` (in declared order).
        This handles real-world fund statement phrases such as:
        "Net Purchase", "Additional Purchase", "SWP Redemption",
        "Switch In – Growth", "Fresh SIP",
        "Gross Purchase - via MFUTILITY", "Gross Purchase Systematic - Instalment 2/155",
        etc.

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
        When neither tier matches the raw value.
    """
    key = raw.strip().lower()

    # --- Tier 1: exact match against known variant sets ---
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
    if key in GROSS_PURCHASE_VARIANTS:
        return TransactionCategory.GROSS_PURCHASE

    # --- Tier 2: keyword-contains fallback ---
    for category_name, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in key:
                return TransactionCategory[category_name]

    raise ValueError(
        ErrorMessages.UNKNOWN_TRANSACTION_TYPE.format(row=row, value=raw)
    )


def is_known_type(raw: str) -> bool:
    """Return ``True`` if *raw* matches any known transaction type variant.

    Checks both Tier-1 exact variants and Tier-2 keyword-contains rules,
    mirroring the full logic of :func:`get_category`.

    Useful for quick membership checks without needing a row number.
    """
    key = raw.strip().lower()

    # Tier 1: exact match
    if key in ALL_KNOWN_VARIANTS:
        return True

    # Tier 2: keyword-contains
    for keywords in CATEGORY_KEYWORDS.values():
        for keyword in keywords:
            if keyword in key:
                return True

    return False
