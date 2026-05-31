"""
transaction_processor.py — Convert validated row dicts into Transaction objects.

Responsibilities:
- Round numeric fields to spec-mandated precision:
    Amount       → 2 decimal places
    Units        → 3 decimal places
    Unit Balance → 3 decimal places
    Price        → preserved as entered (2–4 decimals, not modified)
- Preserve the original transaction type string (not the canonical category)
- Return list[Transaction] in original file order (no sorting — spec §4.4)
"""

from app.models.transaction import Transaction
from app.utils.constants import DECIMAL_PLACES_AMOUNT, DECIMAL_PLACES_UNITS
from app.utils.logger import get_logger

logger = get_logger(__name__)


def process(validated_rows: list[dict]) -> list[Transaction]:
    """Convert validated row dicts to :class:`Transaction` Pydantic objects.

    Parameters
    ----------
    validated_rows:
        Output of ``validator.validate()`` — list of typed, validated row
        dicts (see validator docstring for dict schema).

    Returns
    -------
    list[Transaction]
        Pydantic ``Transaction`` objects in original file order, ready for
        inclusion in the API response.
    """
    transactions: list[Transaction] = []

    for row in validated_rows:
        tx = Transaction(
            date=row["date_str"],
            transactionType=row["raw_type"],
            amount=round(row["amount"], DECIMAL_PLACES_AMOUNT),
            units=(
                round(row["units"], DECIMAL_PLACES_UNITS)
                if row["units"] is not None
                else None
            ),
            price=row["price"],  # preserved as-is — spec §9 & §4.4
            unitBalance=(
                round(row["unit_balance"], DECIMAL_PLACES_UNITS)
                if row["unit_balance"] is not None
                else None
            ),
        )
        transactions.append(tx)

    logger.info("Built %d Transaction objects", len(transactions))
    return transactions
