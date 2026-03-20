"""
response.py — Pydantic models for the POST /api/upload response envelope.

Spec API contract (§4 API Endpoint + §5 Data Model):

  Success (200):
    { "success": true,
      "xirr": 12.54,
      "summaryMetrics": { "totalInvested": 1250000, "finalProceeds": 1475500, "profitLoss": 225500 },
      "transactions": [ ... ] }

  Failure (400 / 413 / 500):
    { "success": false,
      "error": { "message": "...", "details": "..." } }

All monetary values are raw floats (2 decimal places after rounding in
xirr_calculator.py). Formatting to ₹ with thousands separator is the
frontend's responsibility.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.transaction import Transaction
from app.models.error import ErrorDetail


class SummaryMetrics(BaseModel):
    """Calculated financial summary metrics for the uploaded fund statement."""

    totalInvested: float = Field(
        ...,
        description=(
            "Sum of all PURCHASE / SIP / Systematic Investment / "
            "Stamp Duty / STT Paid transaction amounts (2 decimal places)"
        ),
        examples=[1250000.00],
    )
    finalProceeds: float = Field(
        ...,
        description="Amount received from the final SELL / REDEMPTION transaction (2 decimal places)",
        examples=[1475500.00],
    )
    profitLoss: float = Field(
        ...,
        description="finalProceeds – totalInvested (2 decimal places; negative = loss)",
        examples=[225500.00],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "totalInvested": 1250000.00,
                "finalProceeds": 1475500.00,
                "profitLoss": 225500.00,
            }
        }
    }


class UploadResponse(BaseModel):
    """Top-level response envelope for POST /api/upload.

    On success: ``success=True``, ``xirr``, ``summaryMetrics``, and
    ``transactions`` are populated; ``error`` is None.

    On failure: ``success=False``, ``error`` is populated; all other
    optional fields are None.
    """

    success: bool = Field(
        ...,
        description="True if the file was processed successfully; False otherwise",
    )
    xirr: Optional[float] = Field(
        default=None,
        description="XIRR as an annualised percentage (2 decimal places, e.g., 12.54 means 12.54%)",
        examples=[12.54],
    )
    summaryMetrics: Optional[SummaryMetrics] = Field(
        default=None,
        description="Calculated summary financial metrics",
    )
    transactions: Optional[List[Transaction]] = Field(
        default=None,
        description="All parsed transactions in original file order",
    )
    error: Optional[ErrorDetail] = Field(
        default=None,
        description="Error details when success is False",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Success response",
                    "value": {
                        "success": True,
                        "xirr": 12.54,
                        "summaryMetrics": {
                            "totalInvested": 1250000.00,
                            "finalProceeds": 1475500.00,
                            "profitLoss": 225500.00,
                        },
                        "transactions": [
                            {
                                "date": "15-Jan-2020",
                                "transactionType": "Purchase",
                                "amount": 10000.00,
                                "units": 100.123,
                                "price": 99.85,
                                "unitBalance": 100.123,
                            }
                        ],
                        "error": None,
                    },
                },
                {
                    "summary": "Validation failure response",
                    "value": {
                        "success": False,
                        "xirr": None,
                        "summaryMetrics": None,
                        "transactions": None,
                        "error": {
                            "message": "File validation failed",
                            "details": "Row 5: Invalid date format 'xyz' (expected DD-MMM-YYYY, e.g., 15-Jan-2020)",
                        },
                    },
                },
            ]
        }
    }
