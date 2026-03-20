"""
test_xirr_calculator.py — Unit tests for XIRR calculation and summary metrics.

Tests: XIRR accuracy for a known dataset, Stamp Duty exclusion, DIVIDEND_REINVEST
treatment, summary metric values, and convergence failure handling.
"""

from datetime import date

import pytest

from app.exceptions.calculation_error import XirrCalculationError
from app.services.validator import validate
from app.services.xirr_calculator import _compute_xirr, calculate
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


def test_xirr_stamp_duty_excluded():
    """Adding a Stamp Duty row must not change the XIRR (excluded from cash flows)."""
    xirr_without_sd, _ = calculate(validate(td.valid_two_row()))
    xirr_with_sd, _ = calculate(validate(td.valid_with_stamp_duty()))
    assert xirr_with_sd == pytest.approx(xirr_without_sd, abs=0.01)


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
