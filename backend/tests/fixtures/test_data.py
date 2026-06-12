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
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def valid_with_stamp_duty() -> list[dict[str, Any]]:
    """Valid dataset with a Stamp Duty row (Units optional, Price/UB empty)."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2020", "Stamp Duty", 50),           # units/price/ub all None
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def valid_with_dividend_reinvest() -> list[dict[str, Any]]:
    """Valid dataset with Dividend Reinvest (treated as investment in XIRR)."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/07/2020", "Dividend Reinvest", 500, 5.0, 100.0, 105.0),
        _row("01/01/2021", "SELL", 12000, 105.0),
    ]


def valid_sip() -> list[dict[str, Any]]:
    """Valid SIP fund (multiple purchases + final redemption)."""
    return [
        _row("01/01/2020", "SIP", 5000, 50.0, 100.0, 50.0),
        _row("01/02/2020", "SIP", 5000, 49.5, 101.01, 99.5),
        _row("01/01/2021", "REDEMPTION", 11500, 99.5),
    ]


def valid_with_gross_purchase() -> list[dict[str, Any]]:
    """Valid dataset modelling real MFUTILITY platform pattern.

    Row breakdown (mirrors the real-world example):
      1. Gross Purchase - via MFUTILITY  — gross summary row; Units/Price/UB empty.
                                           Excluded from XIRR and Total Invested.
      2. Net Purchase                    — actual investment row; Units/Price/UB populated.
                                           Included in XIRR (outflow) and Total Invested.
      3. Less: Stamp Duty                — cost row; Units/Price/UB empty.
                                           Included in Total Invested, excluded from XIRR.
      4. SELL                            — terminal row; Units populated, Price/UB empty.

    The gross amount (10000) = net purchase (9999.50) + stamp duty (0.50).
    Only the Net Purchase and Stamp Duty rows count toward Total Invested.
    """
    return [
        _row("21/01/2026", "Gross Purchase - via MFUTILITY", 10000.00),
        _row("21/01/2026", "Net Purchase", 9999.50, 293.439, 34.08, 293.439),
        _row("21/01/2026", "Less: Stamp Duty", 0.50),
        _row("01/05/2026", "SELL", 11500.00, 293.439),
    ]


def valid_with_gross_purchase_systematic() -> list[dict[str, Any]]:
    """Valid dataset with Gross Purchase Systematic instalment variant.

    Models a multi-instalment SIP where each instalment produces:
      - a Gross Purchase Systematic row (summary, excluded from XIRR/Total Invested)
      - a Net Purchase row (actual investment, included in XIRR/Total Invested)
      - a Less: Stamp Duty row (cost, included in Total Invested only)
    """
    return [
        _row("01/01/2026", "Gross Purchase Systematic - Instalment 1/12", 5000.00),
        _row("01/01/2026", "Net Purchase", 4999.50, 100.0, 50.0, 100.0),
        _row("01/01/2026", "Less: Stamp Duty", 0.50),
        _row("01/02/2026", "Gross Purchase Systematic - Instalment 2/12", 5000.00),
        _row("01/02/2026", "Net Purchase", 4999.50, 98.0, 51.02, 198.0),
        _row("01/02/2026", "Less: Stamp Duty", 0.50),
        _row("01/05/2026", "SELL", 11500.00, 198.0),
    ]


def valid_sell_with_price_and_unit_balance() -> list[dict[str, Any]]:
    """SELL row with Price and Unit Balance populated — now valid (optional fields).

    Previously rejected; Price and Unit Balance on SELL/REDEMPTION rows are now
    optional. When present in the fund statement they are accepted and displayed.
    Final UB = 0.0 satisfies the 'all units redeemed' terminal check.
    """
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0, 115.0, 0.0),
    ]


def valid_with_partial_redemptions() -> list[dict[str, Any]]:
    """Two partial SELL rows — Final Proceeds must sum both amounts.

    Row breakdown:
      1. Purchase 10000 (100 units @ 100.00, UB 100.0)
      2. SELL 6000 on 01/07/2020 — partial exit (60 units, UB 40.0)
      3. SELL 4900 on 01/01/2021 — final exit (40 units, UB 0.0)

    Final Proceeds = 6000 + 4900 = 10900
    Total Invested = 10000
    Profit/Loss    = 900
    """
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/07/2020", "SELL", 6000, 60.0, 100.0, 40.0),
        _row("01/01/2021", "SELL", 4900, 40.0),
    ]


def valid_with_negative_sell_amount() -> list[dict[str, Any]]:
    """SELL row with a negative amount — sign must be stripped to positive.

    Functionally identical to valid_two_row() (Purchase 10000 → SELL 11500).
    The only difference is the SELL amount is supplied as -11500 to simulate
    fund statements that show redemption amounts as negative numbers.
    XIRR and all summary metrics must be identical to valid_two_row().
    """
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", -11500, 100.0),
    ]


def valid_with_stt_paid() -> list[dict[str, Any]]:
    """SELL row with an STT Paid row on the same date — netted in XIRR.

    Row breakdown:
      1. Purchase 10000 on 01/01/2020 (100 units @ 100.00, UB 100.0)
      2. STT Paid 10 on 01/01/2021    — redemption-side tax; no Price/UB
      3. SELL 11500 on 01/01/2021     — gross redemption amount

    XIRR cash flows (netted):
      01/01/2020: -10000  (purchase outflow)
      01/01/2021: +11490  (11500 gross - 10 STT = net inflow to bank)

    Manual computation:
      day_fraction = 366 / 365 = 1.00274  (2020 is a leap year)
      r = (11490/10000)^(1/1.00274) − 1 ≈ 0.14865 → XIRR ≈ 14.86%

    Summary metrics:
      Total Invested  = 10000 (STT Paid excluded — not a purchase cost)
      Final Proceeds  = 11500 − 10 = 11490 (gross proceeds minus STT)
      Profit/Loss     = 11490 − 10000 = 1490
    """
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "STT Paid", 10),
        _row("01/01/2021", "SELL", 11500, 100.0),
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
        {"date": "01/01/2020", "amount": 10000, "units": 100.0,
         "price": 100.0, "unit balance": 100.0},
        {"date": "01/01/2021", "amount": 11500, "units": 100.0,
         "price": None, "unit balance": None},
    ]


def missing_amount_column() -> list[dict[str, Any]]:
    return [
        {"date": "01/01/2020", "transaction type": "Purchase", "units": 100.0,
         "price": 100.0, "unit balance": 100.0},
        {"date": "01/01/2021", "transaction type": "SELL", "units": 100.0,
         "price": None, "unit balance": None},
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — row count errors
# ---------------------------------------------------------------------------

def single_row() -> list[dict[str, Any]]:
    """Only one row — fails MIN_TRANSACTIONS check."""
    return [_row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0)]


def over_limit_rows(n: int = 10_001) -> list[dict[str, Any]]:
    """n rows — fails MAX_TRANSACTIONS check when n > 10,000."""
    return [
        _row("01/01/2020", "Purchase", 1000, 10.0, 100.0, float((i + 1) * 10))
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — date errors
# ---------------------------------------------------------------------------

def invalid_date_format() -> list[dict[str, Any]]:
    """Row with date in DD-MMM-YYYY format instead of DD/MM/YYYY."""
    return [
        _row("01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def date_before_1960() -> list[dict[str, Any]]:
    """Row with a date before the 1960 floor."""
    return [
        _row("01/01/1959", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def future_date() -> list[dict[str, Any]]:
    """Row with a date in the future."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2099", "SELL", 11500, 100.0),
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — amount errors
# ---------------------------------------------------------------------------

def non_numeric_amount() -> list[dict[str, Any]]:
    return [
        _row("01/01/2020", "Purchase", "not_a_number", 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def negative_amount() -> list[dict[str, Any]]:
    return [
        _row("01/01/2020", "Purchase", -10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — conditional field errors
# ---------------------------------------------------------------------------

def purchase_missing_units() -> list[dict[str, Any]]:
    """Purchase row without Units."""
    return [
        _row("01/01/2020", "Purchase", 10000, None, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def purchase_missing_price() -> list[dict[str, Any]]:
    """Purchase row without Price."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, None, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def purchase_missing_unit_balance() -> list[dict[str, Any]]:
    """Purchase row without Unit Balance."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, None),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def sell_missing_units() -> list[dict[str, Any]]:
    """SELL row without Units."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, None),
    ]


def stamp_duty_with_price() -> list[dict[str, Any]]:
    """Stamp Duty row where Price is populated (must be empty)."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2020", "Stamp Duty", 50, None, 1.0, None),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def stamp_duty_with_unit_balance() -> list[dict[str, Any]]:
    """Stamp Duty row where Unit Balance is populated (must be empty)."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2020", "Stamp Duty", 50, None, None, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def stt_paid_with_price() -> list[dict[str, Any]]:
    """STT Paid row where Price is populated (must be empty)."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "STT Paid", 10, None, 1.0, None),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def stt_paid_with_unit_balance() -> list[dict[str, Any]]:
    """STT Paid row where Unit Balance is populated (must be empty)."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "STT Paid", 10, None, None, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def gross_purchase_with_price() -> list[dict[str, Any]]:
    """Gross Purchase row where Price is populated (must be empty)."""
    return [
        _row("21/01/2026", "Gross Purchase - via MFUTILITY", 10000.00, None, 34.08, None),
        _row("21/01/2026", "Net Purchase", 9999.50, 293.439, 34.08, 293.439),
        _row("21/01/2026", "Less: Stamp Duty", 0.50),
        _row("01/05/2026", "SELL", 11500.00, 293.439),
    ]


def gross_purchase_with_unit_balance() -> list[dict[str, Any]]:
    """Gross Purchase row where Unit Balance is populated (must be empty)."""
    return [
        _row("21/01/2026", "Gross Purchase - via MFUTILITY", 10000.00, None, None, 293.439),
        _row("21/01/2026", "Net Purchase", 9999.50, 293.439, 34.08, 293.439),
        _row("21/01/2026", "Less: Stamp Duty", 0.50),
        _row("01/05/2026", "SELL", 11500.00, 293.439),
    ]


# ---------------------------------------------------------------------------
# Invalid datasets — file-level errors
# ---------------------------------------------------------------------------

def last_not_sell() -> list[dict[str, Any]]:
    """Last transaction is a Purchase — not SELL/REDEMPTION."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/06/2020", "Purchase", 5000, 45.0, 111.11, 145.0),
    ]


def unit_balance_mismatch() -> list[dict[str, Any]]:
    """Row where Unit Balance doesn't match cumulative units."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 200.0),  # ub=200 but cumulative=100
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]


def partial_sell() -> list[dict[str, Any]]:
    """SELL covers only 50% of units → cumulative ≠ 0 at end."""
    return [
        _row("01/01/2020", "Purchase", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 5750, 50.0),   # 50 units left → cumulative = 50 ≠ 0
    ]


def unknown_transaction_type() -> list[dict[str, Any]]:
    return [
        _row("01/01/2020", "Whatever", 10000, 100.0, 100.0, 100.0),
        _row("01/01/2021", "SELL", 11500, 100.0),
    ]