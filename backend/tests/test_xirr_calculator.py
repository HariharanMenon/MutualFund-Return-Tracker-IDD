"""
test_xirr_calculator.py — Unit tests for XIRR calculation and summary metrics.

Tests: XIRR accuracy for a known dataset, Stamp Duty inclusion as outflow,
DIVIDEND_REINVEST treatment, summary metric values, convergence failure handling,
XIRR_OUTFLOW_CATEGORIES / TOTAL_INVESTED_CATEGORIES membership assertions,
multi-redemption Final Proceeds accumulation, negative SELL amount sign stripping,
and STT Paid netting against same-date SELL inflow in XIRR cash flows.
"""

from datetime import date

import pytest

from app.exceptions.calculation_error import XirrCalculationError
from app.services.validator import validate
from app.services.xirr_calculator import _compute_xirr, calculate
from app.utils.constants import (
    TransactionCategory,
    TOTAL_INVESTED_CATEGORIES,
    XIRR_OUTFLOW_CATEGORIES,
)
from tests.fixtures import test_data as td


# ---------------------------------------------------------------------------
# XIRR accuracy
# ---------------------------------------------------------------------------

def test_xirr_basic_accuracy():
    """Known two-transaction case: Purchase 10000 → SELL 11500 over one year.

    Manual computation:
      day_fraction = 366 / 365 = 1.00274  (2020 is a leap year)
      (1 + r)^1.00274 = 11500 / 10000 = 1.15
      r = 1.15^(1/1.00274) − 1 ≈ 0.14958 → XIRR ≈ 14.96%
    """
    validated = validate(td.valid_two_row())
    xirr, _ = calculate(validated)
    assert xirr == pytest.approx(14.96, abs=0.2)


def test_xirr_stamp_duty_included_as_outflow():
    """Stamp Duty is a negative cash outflow in XIRR — lowers return vs no-stamp-duty case.

    Fixture: Purchase 10000 + Stamp Duty 50 on 01/01/2020, SELL 11500 on 01/01/2021.
    Cash flows: [-10000, -50, 11500]
    Expected XIRR ≈ 14.39% (lower than 14.96% without stamp duty — more cash out,
    same proceeds, confirming stamp duty is counted as a real cost outflow).
    """
    xirr_with_sd, _ = calculate(validate(td.valid_with_stamp_duty()))
    xirr_without_sd, _ = calculate(validate(td.valid_two_row()))
    # Stamp duty included as outflow means XIRR is lower than the no-stamp-duty case
    assert xirr_with_sd < xirr_without_sd
    assert xirr_with_sd == pytest.approx(14.39, abs=0.05)


def test_stamp_duty_is_member_of_xirr_outflow_categories():
    """STAMP_DUTY must be in XIRR_OUTFLOW_CATEGORIES (constants.py spec)."""
    assert TransactionCategory.STAMP_DUTY in XIRR_OUTFLOW_CATEGORIES


def test_xirr_dividend_reinvest_treated_as_outflow():
    """DIVIDEND_REINVEST adds a negative cash flow (additional investment)."""
    validated = validate(td.valid_with_dividend_reinvest())
    xirr, _ = calculate(validated)
    # Just verify it converges and is a reasonable number
    assert isinstance(xirr, float)
    assert -100.0 < xirr < 1000.0


# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------

def test_total_invested_basic():
    validated = validate(td.valid_two_row())
    _, metrics = calculate(validated)
    assert metrics.totalInvested == pytest.approx(10000.00, abs=0.01)


def test_final_proceeds_basic():
    validated = validate(td.valid_two_row())
    _, metrics = calculate(validated)
    assert metrics.finalProceeds == pytest.approx(11500.00, abs=0.01)


def test_profit_loss_basic():
    validated = validate(td.valid_two_row())
    _, metrics = calculate(validated)
    assert metrics.profitLoss == pytest.approx(1500.00, abs=0.01)


def test_total_invested_includes_stamp_duty():
    """Total Invested = sum of all PURCHASE + STAMP_DUTY amounts (spec §7)."""
    validated = validate(td.valid_with_stamp_duty())
    _, metrics = calculate(validated)
    # Purchase 10000 + Stamp Duty 50 = 10050
    assert metrics.totalInvested == pytest.approx(10050.00, abs=0.01)


def test_profit_loss_sign_positive():
    validated = validate(td.valid_two_row())
    _, metrics = calculate(validated)
    assert metrics.profitLoss > 0


def test_summary_metrics_two_decimal_precision():
    validated = validate(td.valid_two_row())
    _, metrics = calculate(validated)
    # Values are already rounded to 2 dp by xirr_calculator
    assert round(metrics.totalInvested, 2) == metrics.totalInvested
    assert round(metrics.finalProceeds, 2) == metrics.finalProceeds
    assert round(metrics.profitLoss, 2) == metrics.profitLoss


# ---------------------------------------------------------------------------
# Convergence failure
# ---------------------------------------------------------------------------

def test_xirr_convergence_failure_all_positive_flows():
    """All-positive cash flows have no root — must raise XirrCalculationError."""
    with pytest.raises(XirrCalculationError, match="Cannot calculate XIRR"):
        _compute_xirr(
            cash_flows=[1000.0, 2000.0],
            dates=[date(2020, 1, 1), date(2021, 1, 1)],
        )


def test_xirr_convergence_failure_single_flow():
    """Only one cash flow — below minimum of 2 required."""
    with pytest.raises(XirrCalculationError):
        _compute_xirr(
            cash_flows=[-5000.0],
            dates=[date(2020, 1, 1)],
        )


# ---------------------------------------------------------------------------
# Return type and rounding
# ---------------------------------------------------------------------------

def test_xirr_is_float():
    validated = validate(td.valid_two_row())
    xirr, _ = calculate(validated)
    assert isinstance(xirr, float)


def test_xirr_rounded_to_two_decimal_places():
    validated = validate(td.valid_two_row())
    xirr, _ = calculate(validated)
    assert round(xirr, 2) == xirr


# ---------------------------------------------------------------------------
# Multi-redemption Final Proceeds (Req 1 & 2)
# ---------------------------------------------------------------------------

def test_final_proceeds_accumulates_all_sell_rows():
    """Final Proceeds = sum of ALL SELL/REDEMPTION amounts, not just the last one.

    Fixture: Purchase 10000 → partial SELL 6000 → final SELL 4900.
    Final Proceeds must be 6000 + 4900 = 10900, not 4900 (last row only).
    """
    validated = validate(td.valid_with_partial_redemptions())
    _, metrics = calculate(validated)
    assert metrics.finalProceeds == pytest.approx(10900.00, abs=0.01)


def test_total_invested_unchanged_with_multiple_sells():
    """Total Invested is unaffected by multiple SELL rows — still purchase sum only."""
    validated = validate(td.valid_with_partial_redemptions())
    _, metrics = calculate(validated)
    assert metrics.totalInvested == pytest.approx(10000.00, abs=0.01)


def test_profit_loss_with_multiple_sells():
    """Profit/Loss = Final Proceeds (sum of all SELLs) minus Total Invested."""
    validated = validate(td.valid_with_partial_redemptions())
    _, metrics = calculate(validated)
    # Final Proceeds 10900 − Total Invested 10000 = 900
    assert metrics.profitLoss == pytest.approx(900.00, abs=0.01)


def test_xirr_converges_with_multiple_sells():
    """XIRR must converge when there are multiple partial SELL rows."""
    validated = validate(td.valid_with_partial_redemptions())
    xirr, _ = calculate(validated)
    assert isinstance(xirr, float)
    assert -100.0 < xirr < 1000.0


# ---------------------------------------------------------------------------
# Negative SELL/REDEMPTION amount sign stripping (Req 1 & 2)
# ---------------------------------------------------------------------------

def test_negative_sell_amount_treated_as_positive():
    """SELL amount of -11500 must produce identical results to +11500.

    The validator strips the sign; xirr_calculator sees the same positive
    amount regardless of how the fund statement presented it.
    """
    validated_negative = validate(td.valid_with_negative_sell_amount())
    validated_positive = validate(td.valid_two_row())
    xirr_neg, metrics_neg = calculate(validated_negative)
    xirr_pos, metrics_pos = calculate(validated_positive)
    assert xirr_neg == pytest.approx(xirr_pos, abs=0.01)
    assert metrics_neg.finalProceeds == pytest.approx(metrics_pos.finalProceeds, abs=0.01)
    assert metrics_neg.totalInvested == pytest.approx(metrics_pos.totalInvested, abs=0.01)


# ---------------------------------------------------------------------------
# STT Paid netting against same-date redemption (Req 5)
# ---------------------------------------------------------------------------

def test_stt_paid_netted_against_sell_in_xirr():
    """XIRR reflects net inflow (SELL minus STT Paid) — not two separate entries.

    Fixture: Purchase 10000 → STT Paid 10 + SELL 11500 on same date.
    Net inflow = 11490. Cash flows for XIRR: [-10000, +11490].
    XIRR ≈ 14.86% — lower than 14.96% (no STT) confirming netting reduces return.
    """
    xirr_with_stt, _ = calculate(validate(td.valid_with_stt_paid()))
    xirr_without_stt, _ = calculate(validate(td.valid_two_row()))
    # STT reduces the net inflow → lowers XIRR vs no-STT case
    assert xirr_with_stt < xirr_without_stt
    assert xirr_with_stt == pytest.approx(14.86, abs=0.05)


def test_stt_paid_reduces_final_proceeds():
    """Final Proceeds = gross SELL amount minus total STT Paid.

    Fixture: SELL 11500, STT Paid 10 → Final Proceeds = 11490.
    """
    validated = validate(td.valid_with_stt_paid())
    _, metrics = calculate(validated)
    assert metrics.finalProceeds == pytest.approx(11490.00, abs=0.01)


def test_stt_paid_excluded_from_total_invested():
    """STT Paid must NOT appear in Total Invested — it is a redemption-side tax."""
    validated = validate(td.valid_with_stt_paid())
    _, metrics = calculate(validated)
    # Total Invested = Purchase 10000 only; STT Paid 10 must not be added
    assert metrics.totalInvested == pytest.approx(10000.00, abs=0.01)


def test_profit_loss_with_stt_paid():
    """Profit/Loss = Final Proceeds (net of STT) minus Total Invested."""
    validated = validate(td.valid_with_stt_paid())
    _, metrics = calculate(validated)
    # Final Proceeds 11490 − Total Invested 10000 = 1490
    assert metrics.profitLoss == pytest.approx(1490.00, abs=0.01)


# ---------------------------------------------------------------------------
# Constants membership assertions (Req 5)
# ---------------------------------------------------------------------------

def test_stt_paid_not_in_total_invested_categories():
    """STT_PAID must NOT be in TOTAL_INVESTED_CATEGORIES (constants.py spec)."""
    assert TransactionCategory.STT_PAID not in TOTAL_INVESTED_CATEGORIES


def test_stt_paid_not_in_xirr_outflow_categories():
    """STT_PAID must NOT be in XIRR_OUTFLOW_CATEGORIES — it is netted, not a standalone outflow."""
    assert TransactionCategory.STT_PAID not in XIRR_OUTFLOW_CATEGORIES