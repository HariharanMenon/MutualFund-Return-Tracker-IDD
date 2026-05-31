"""
test_data.py — Raw row dict generators for validator and xirr_calculator unit tests.

These functions return data in the format that file_parser.parse_excel() produces:
  list of dicts with normalised (lowercase, stripped) header keys and raw cell values.

They are plain functions (not pytest fixtures) so they can be called directly
from any test module.
"""

from datetime import date as _date
from typing import Any


def _row(
    date_val: Any,
    tx_type: str,
    amount: Any,
    units: Any = None,
    price: Any = None,
    unit_balance: Any = None,
) -> dict[str, Any]:
    return {
        "date": date_val,
        "transaction type": tx_type,
        "amount": amount,
        "units": units,
        "price": price,
        "unit balance": unit_balance,
    }


# ---------------------------------------------------------------------------
# Valid datasets (pass validation)
# ---------------------------------------------------------------------------

def valid_two_row() -> list[dict[str, Any]]:
    """Minimal valid dataset: one Purchase + one SELL.
    XIRR ≈ 14.96% (verified manually for 2020-01-01 → 2021-01-01).
    """
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def valid_with_stamp_duty() -> list[dict[str, Any]]:
    """Valid dataset with a Stamp Duty row (Units optional, Price/UB empty)."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2020", "Stamp Duty", 50),           # units/price/ub all None
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def valid_with_dividend_reinvest() -> list[dict[str, Any]]:
    """Valid dataset with Dividend Reinvest (treated as investment in XIRR)."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jul-2020", "Dividend Reinvest", 500, 5.0, 100.0, 105.0),
        _row("01-Jan-2021", "SELL", 12000, 105.0),
    ]


def valid_sip() -> list[dict[str, Any]]:
    """Valid SIP fund (multiple purchases + final redemption)."""
    return [
        _row("01-Jan-2020", "SIP", 5000, 50.0, 100.0, 50.0),
        _row("01-Feb-2020", "SIP", 5000, 49.5, 101.01, 99.5),
        _row("01-Jan-2021", "REDEMPTION", 11500, 99.5),
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — column/header errors
# ---------------------------------------------------------------------------

def missing_date_column() -> list[dict[str, Any]]:
    """Rows with 'date' key absent — simulates missing Date column in xlsx."""
    return [
        {"transaction type": "Purchase", "amount": 10000, "units": 100.0,
         "price": 100.0, "unit balance": 100.0},
        {"transaction type": "SELL", "amount": 11500, "units": 100.0,
         "price": None, "unit balance": None},
    ]


def missing_transaction_type_column() -> list[dict[str, Any]]:
    return [
        {"date": "01-Jan-2020", "amount": 10000, "units": 100.0,
         "price": 100.0, "unit balance": 100.0},
        {"date": "01-Jan-2021", "amount": 11500, "units": 100.0,
         "price": None, "unit balance": None},
    ]


def missing_amount_column() -> list[dict[str, Any]]:
    return [
        {"date": "01-Jan-2020", "transaction type": "Purchase", "units": 100.0,
         "price": 100.0, "unit balance": 100.0},
        {"date": "01-Jan-2021", "transaction type": "SELL", "units": 100.0,
         "price": None, "unit balance": None},
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — row count errors
# ---------------------------------------------------------------------------

def single_row() -> list[dict[str, Any]]:
    """Only one row — fails MIN_TRANSACTIONS check."""
    return [_row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0)]


def over_limit_rows(n: int = 10_001) -> list[dict[str, Any]]:
    """n rows — fails MAX_TRANSACTIONS check when n > 10,000."""
    return [
        _row("01-Jan-2020", "Purchase", 1000, 10.0, 100.0, float((i + 1) * 10))
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — date errors
# ---------------------------------------------------------------------------

def invalid_date_format() -> list[dict[str, Any]]:
    """Row with date in DD/MM/YYYY format instead of DD-MMM-YYYY."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def date_before_1960() -> list[dict[str, Any]]:
    """Row with a date before the 1960 floor."""
    return [
        _row("01-Jan-1959", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def future_date() -> list[dict[str, Any]]:
    """Row with a date in the future."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2099", "SELL", 11500, 100.0),
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — amount errors
# ---------------------------------------------------------------------------

def non_numeric_amount() -> list[dict[str, Any]]:
    return [
        _row("01-Jan-2020", "Purchase", "not_a_number", 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def negative_amount() -> list[dict[str, Any]]:
    return [
        _row("01-Jan-2020", "Purchase", -10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — conditional field errors
# ---------------------------------------------------------------------------

def purchase_missing_units() -> list[dict[str, Any]]:
    """Purchase row without Units."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, None, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def purchase_missing_price() -> list[dict[str, Any]]:
    """Purchase row without Price."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, None, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def purchase_missing_unit_balance() -> list[dict[str, Any]]:
    """Purchase row without Unit Balance."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, None),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def sell_missing_units() -> list[dict[str, Any]]:
    """SELL row without Units."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, None),
    ]


def sell_with_price() -> list[dict[str, Any]]:
    """SELL row where Price is populated (must be empty)."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0, 115.0, None),
    ]


def sell_with_unit_balance() -> list[dict[str, Any]]:
    """SELL row where Unit Balance is populated (must be empty)."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0, None, 0.0),
    ]


def stamp_duty_with_price() -> list[dict[str, Any]]:
    """Stamp Duty row where Price is populated (must be empty)."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2020", "Stamp Duty", 50, None, 1.0, None),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def stamp_duty_with_unit_balance() -> list[dict[str, Any]]:
    """Stamp Duty row where Unit Balance is populated (must be empty)."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2020", "Stamp Duty", 50, None, None, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — file-level errors
# ---------------------------------------------------------------------------

def last_not_sell() -> list[dict[str, Any]]:
    """Last transaction is a Purchase — not SELL/REDEMPTION."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jun-2020", "Purchase", 5000, 45.0, 111.11, 145.0),
    ]


def unit_balance_mismatch() -> list[dict[str, Any]]:
    """Row where Unit Balance doesn't match cumulative units."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 200.0),  # ub=200 but cumulative=100
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]


def partial_sell() -> list[dict[str, Any]]:
    """SELL covers only 50% of units → cumulative ≠ 0 at end."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 5750, 50.0),   # 50 units left → cumulative = 50 ≠ 0
    ]


def unknown_transaction_type() -> list[dict[str, Any]]:
    return [
        _row("01-Jan-2020", "Whatever", 10000, 100.0, 100.0, 100.0),
        _row("01-Jan-2021", "SELL", 11500, 100.0),
    ]
