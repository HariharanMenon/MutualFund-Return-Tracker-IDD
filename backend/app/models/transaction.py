"""
transaction.py — Pydantic model for a single mutual fund transaction row.

Field nullability follows the spec exactly (§5 Data Model, §6 Validation Rules):

  Field           | Required for                           | Nullable for
  --------------- | -------------------------------------- | ----------------------------------
  date            | All                                    | Never
  transactionType | All                                    | Never
  amount          | All                                    | Never
  units           | PURCHASE, SELL, REDEMPTION, DIV_REINV  | STAMP_DUTY (optional)
  price           | PURCHASE, DIVIDEND_REINVEST            | SELL, REDEMPTION, STAMP_DUTY
  unitBalance     | PURCHASE, DIVIDEND_REINVEST            | SELL, REDEMPTION, STAMP_DUTY

The model stores display-ready values (date as DD-MMM-YYYY string; amounts
already rounded by transaction_processor.py before construction).
"""

from typing import Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """A single processed mutual fund transaction row."""

    date: str = Field(
        ...,
        description="Transaction date in DD-MMM-YYYY format (e.g., 15-Jan-2020)",
        examples=["15-Jan-2020"],
    )
    transactionType: str = Field(
        ...,
        description="Original transaction type string as it appeared in the file",
        examples=["Purchase", "SIP", "SELL"],
    )
    amount: float = Field(
        ...,
        description="Transaction amount (positive for all types; 2 decimal places)",
        examples=[10000.00],
    )
    units: Optional[float] = Field(
        default=None,
        description=(
            "Number of units transacted (3 decimal places). "
            "Null for Stamp Duty / STT Paid transactions."
        ),
        examples=[100.123],
    )
    price: Optional[float] = Field(
        default=None,
        description=(
            "NAV / unit price at time of transaction (2–4 decimal places as entered). "
            "Null for SELL, REDEMPTION, Stamp Duty, and STT Paid transactions."
        ),
        examples=[99.85],
    )
    unitBalance: Optional[float] = Field(
        default=None,
        description=(
            "Cumulative units held after this transaction (3 decimal places). "
            "Null for SELL, REDEMPTION, Stamp Duty, and STT Paid transactions."
        ),
        examples=[200.246],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "15-Jan-2020",
                "transactionType": "Purchase",
                "amount": 10000.00,
                "units": 100.123,
                "price": 99.85,
                "unitBalance": 100.123,
            }
        }
    }
