"""
test_validator.py — Unit tests for the full data validation engine.

Each test exercises one validation rule and asserts:
  1. A FileValidationError is raised.
  2. The error details contain the expected substring (row number or field name).

Valid path test confirms that clean data passes without exception.
"""

import pytest

from app.exceptions.validation_error import FileValidationError
from app.services.validator import validate
from tests.fixtures import test_data as td


def _raises(raw_rows, match: str = ""):
    """Assert that validate() raises FileValidationError with details matching `match`."""
    with pytest.raises(FileValidationError) as exc_info:
        validate(raw_rows)
    if match:
        assert match.lower() in exc_info.value.details.lower(), (
            f"Expected '{match}' in details: '{exc_info.value.details}'"
        )


# ---------------------------------------------------------------------------
# Valid path — must pass entirely
# ---------------------------------------------------------------------------

def test_valid_two_row_passes():
    result = validate(td.valid_two_row())
    assert len(result) == 2
    assert result[0]["category"].value == "PURCHASE"
    assert result[1]["category"].value == "SELL"


def test_valid_with_stamp_duty_passes():
    result = validate(td.valid_with_stamp_duty())
    assert len(result) == 3


def test_valid_with_dividend_reinvest_passes():
    result = validate(td.valid_with_dividend_reinvest())
    assert len(result) == 3


def test_valid_sip_passes():
    result = validate(td.valid_sip())
    assert len(result) == 3


def test_valid_with_gross_purchase_passes():
    """Gross Purchase rows (summary rows) validate successfully without error.
    They have empty Units, Price, and Unit Balance as required."""
    result = validate(td.valid_with_gross_purchase())
    assert len(result) == 4
    # Verify the Gross Purchase row is parsed correctly
    gross_row = result[0]
    assert gross_row["category"].value == "GROSS_PURCHASE"
    assert gross_row["raw_type"] == "Gross Purchase - via MFUTILITY"
    assert gross_row["units"] is None
    assert gross_row["price"] is None
    assert gross_row["unit_balance"] is None
    # Verify the Net Purchase row follows as expected
    net_row = result[1]
    assert net_row["category"].value == "PURCHASE"
    assert net_row["raw_type"] == "Net Purchase"


def test_valid_with_gross_purchase_systematic_passes():
    """Gross Purchase Systematic (multi-instalment) variant validates successfully.
    Each instalment has Gross Purchase → Net Purchase → Stamp Duty pattern."""
    result = validate(td.valid_with_gross_purchase_systematic())
    assert len(result) == 7
    # First instalment Gross Purchase
    gross_row_1 = result[0]
    assert gross_row_1["category"].value == "GROSS_PURCHASE"
    assert "Instalment 1/12" in gross_row_1["raw_type"]
    # Second instalment Gross Purchase
    gross_row_2 = result[3]
    assert gross_row_2["category"].value == "GROSS_PURCHASE"
    assert "Instalment 2/12" in gross_row_2["raw_type"]


# ---------------------------------------------------------------------------
# Rule 1 — Required column headers
# ---------------------------------------------------------------------------

def test_missing_date_column():
    _raises(td.missing_date_column(), match="date")


def test_missing_transaction_type_column():
    _raises(td.missing_transaction_type_column(), match="transaction type")


def test_missing_amount_column():
    _raises(td.missing_amount_column(), match="amount")


# ---------------------------------------------------------------------------
# Rule 2 — Row count
# ---------------------------------------------------------------------------

def test_insufficient_rows():
    _raises(td.single_row(), match="insufficient")


def test_too_many_rows():
    _raises(td.over_limit_rows(10_001), match="10,000")


# ---------------------------------------------------------------------------
# Rule 3 — Unknown transaction type
# ---------------------------------------------------------------------------

def test_unknown_transaction_type():
    _raises(td.unknown_transaction_type(), match="unrecognised")


# ---------------------------------------------------------------------------
# Rule 4 — Date format and range
# ---------------------------------------------------------------------------

def test_invalid_date_format():
    _raises(td.invalid_date_format(), match="dd/mm/yyyy")


def test_date_before_1960():
    _raises(td.date_before_1960(), match="before 1960")


def test_future_date():
    _raises(td.future_date(), match="future")


# ---------------------------------------------------------------------------
# Rule 5 — Amount validation
# ---------------------------------------------------------------------------

def test_non_numeric_amount():
    _raises(td.non_numeric_amount(), match="amount must be numeric")


def test_negative_amount():
    _raises(td.negative_amount(), match="amount must be positive")


# ---------------------------------------------------------------------------
# Rules 6–9 — Conditional field requirements per transaction type
# ---------------------------------------------------------------------------

def test_purchase_missing_units():
    _raises(td.purchase_missing_units(), match="units")


def test_purchase_missing_price():
    _raises(td.purchase_missing_price(), match="price")


def test_purchase_missing_unit_balance():
    _raises(td.purchase_missing_unit_balance(), match="unit balance")


def test_sell_missing_units():
    _raises(td.sell_missing_units(), match="units")


def test_sell_with_price_must_be_empty():
    _raises(td.sell_with_price(), match="empty")


def test_sell_with_unit_balance_must_be_empty():
    _raises(td.sell_with_unit_balance(), match="empty")


def test_stamp_duty_with_price_must_be_empty():
    _raises(td.stamp_duty_with_price(), match="empty")


def test_stamp_duty_with_unit_balance_must_be_empty():
    _raises(td.stamp_duty_with_unit_balance(), match="empty")


def test_gross_purchase_with_price_must_be_empty():
    """Gross Purchase row with Price populated (must be empty) raises error."""
    _raises(td.gross_purchase_with_price(), match="gross purchase")


def test_gross_purchase_with_unit_balance_must_be_empty():
    """Gross Purchase row with Unit Balance populated (must be empty) raises error."""
    _raises(td.gross_purchase_with_unit_balance(), match="gross purchase")


# ---------------------------------------------------------------------------
# Rule 10 — Unit balance consistency
# ---------------------------------------------------------------------------

def test_unit_balance_mismatch():
    _raises(td.unit_balance_mismatch(), match="unit balance")


# ---------------------------------------------------------------------------
# Rule 11 — Last transaction must be SELL or REDEMPTION
# ---------------------------------------------------------------------------

def test_last_transaction_not_sell_or_redemption():
    _raises(td.last_not_sell(), match="sell or redemption")


# ---------------------------------------------------------------------------
# Rule 12 — Full exit: cumulative units ≈ 0
# ---------------------------------------------------------------------------

def test_partial_sell_cumulative_not_zero():
    _raises(td.partial_sell(), match="final redemption")


# ---------------------------------------------------------------------------
# Validated row dict structure
# ---------------------------------------------------------------------------

def test_validated_row_has_correct_keys():
    result = validate(td.valid_two_row())
    expected_keys = {"date_str", "date", "raw_type", "category", "amount",
                     "units", "price", "unit_balance"}
    assert set(result[0].keys()) == expected_keys


def test_validated_row_date_string_format():
    result = validate(td.valid_two_row())
    assert result[0]["date_str"] == "01/01/2020"


def test_stamp_duty_units_optional():
    """Stamp Duty with None units must pass (units are optional for stamp duty)."""
    rows = [
        {"date": "01/01/2020", "transaction type": "Purchase",
         "amount": 10000, "units": 100.0, "price": 100.0, "unit balance": 100.0},
        {"date": "01/01/2020", "transaction type": "Stamp Duty",
         "amount": 50, "units": None, "price": None, "unit balance": None},
        {"date": "01/01/2021", "transaction type": "SELL",
         "amount": 11500, "units": 100.0, "price": None, "unit balance": None},
    ]
    result = validate(rows)
    assert result[1]["units"] is None  # stamp duty units remain None


def test_stamp_duty_units_with_value_accepted():
    """Stamp Duty with a units value must also pass (units are optional, not forbidden)."""
    rows = [
        {"date": "01/01/2020", "transaction type": "Purchase",
         "amount": 10000, "units": 100.0, "price": 100.0, "unit balance": 100.0},
        {"date": "01/01/2020", "transaction type": "Stamp Duty",
         "amount": 50, "units": 0.5, "price": None, "unit balance": None},
        {"date": "01/01/2021", "transaction type": "SELL",
         "amount": 11500, "units": 100.0, "price": None, "unit balance": None},
    ]
    result = validate(rows)
    assert result[1]["units"] == 0.5


def test_gross_purchase_units_optional():
    """Gross Purchase with None units must pass (units are optional)."""
    rows = [
        {"date": "21/01/2026", "transaction type": "Gross Purchase - via MFUTILITY",
         "amount": 10000, "units": None, "price": None, "unit balance": None},
        {"date": "21/01/2026", "transaction type": "Net Purchase",
         "amount": 9999.50, "units": 293.439, "price": 34.08, "unit balance": 293.439},
        {"date": "21/01/2026", "transaction type": "Less: Stamp Duty",
         "amount": 0.50, "units": None, "price": None, "unit balance": None},
        {"date": "01/05/2026", "transaction type": "SELL",
         "amount": 11500, "units": 293.439, "price": None, "unit_balance": None},
    ]
    result = validate(rows)
    assert result[0]["units"] is None  # gross purchase units remain None


def test_gross_purchase_units_with_value_accepted():
    """Gross Purchase with a units value must also pass (units are optional, not forbidden)."""
    rows = [
        {"date": "21/01/2026", "transaction type": "Gross Purchase - via MFUTILITY",
         "amount": 10000, "units": 100.0, "price": None, "unit balance": None},
        {"date": "21/01/2026", "transaction type": "Net Purchase",
         "amount": 9999.50, "units": 293.439, "price": 34.08, "unit balance": 293.439},
        {"date": "21/01/2026", "transaction type": "Less: Stamp Duty",
         "amount": 0.50, "units": None, "price": None, "unit balance": None},
        {"date": "01/05/2026", "transaction type": "SELL",
         "amount": 11500, "units": 293.439, "price": None, "unit_balance": None},
    ]
    result = validate(rows)
    assert result[0]["units"] == 100.0