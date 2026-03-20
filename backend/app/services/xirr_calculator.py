"""
xirr_calculator.py — XIRR calculation and summary metrics (spec §7).

XIRR Formula
------------
Solves for ``r`` in:

    NPV(r) = Σ  C_i / (1 + r)^((d_i − d_0) / 365)  =  0

where:
  C_i = signed cash flow (negative = outflow, positive = inflow)
  d_i = date of cash flow i
  d_0 = date of first cash flow
  r   = XIRR (annualised rate)

Algorithm: Newton-Raphson with multiple starting guesses — matches
Excel's XIRR behaviour.  No external dependency required.

Cash-flow sign convention (spec §7):
  PURCHASE / DIVIDEND_REINVEST  →  negative  (money leaves investor)
  SELL / REDEMPTION             →  positive  (money enters investor)
  STAMP_DUTY                    →  excluded  (not a cash-flow for returns)

Summary Metrics (spec §7):
  Total Invested  = Σ amount  for  PURCHASE + STAMP_DUTY rows
  Final Proceeds  = amount of the last SELL / REDEMPTION row
  Profit / Loss   = Final Proceeds − Total Invested
"""

from datetime import date
from typing import Optional

from app.exceptions.calculation_error import XirrCalculationError
from app.models.response import SummaryMetrics
from app.utils.constants import (
    DECIMAL_PLACES_AMOUNT,
    DECIMAL_PLACES_XIRR,
    ErrorMessages,
    TERMINAL_CATEGORIES,
    TOTAL_INVESTED_CATEGORIES,
    XIRR_EXCLUDED_CATEGORIES,
    XIRR_INFLOW_CATEGORIES,
    XIRR_OUTFLOW_CATEGORIES,
    TransactionCategory,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Newton-Raphson XIRR solver
# ---------------------------------------------------------------------------

_MAX_ITER: int = 1_000
_CONVERGENCE_TOL: float = 1e-7
_STARTING_GUESSES: tuple[float, ...] = (0.1, 0.0, -0.05, 0.5, -0.3, 1.0)


def _npv(rate: float, cash_flows: list[float], day_fractions: list[float]) -> float:
    """Net present value for given rate and irregular cash flows."""
    return sum(c / (1.0 + rate) ** t for c, t in zip(cash_flows, day_fractions))


def _npv_deriv(rate: float, cash_flows: list[float], day_fractions: list[float]) -> float:
    """Analytical first derivative of NPV with respect to rate."""
    return sum(
        -c * t / (1.0 + rate) ** (t + 1.0)
        for c, t in zip(cash_flows, day_fractions)
    )


def _newton_raphson(
    cash_flows: list[float],
    day_fractions: list[float],
    guess: float,
) -> Optional[float]:
    """Run Newton-Raphson from a single starting guess.

    Returns the converged rate or ``None`` if it fails to converge or
    produces an economically invalid result (rate ≤ −1).
    """
    rate = guess
    for _ in range(_MAX_ITER):
        # Guard against (1+rate) <= 0 which produces complex/undefined values
        if rate <= -1.0:
            return None
        f = _npv(rate, cash_flows, day_fractions)
        df = _npv_deriv(rate, cash_flows, day_fractions)
        if df == 0.0:
            return None
        new_rate = rate - f / df
        if abs(new_rate - rate) < _CONVERGENCE_TOL:
            if new_rate > -1.0:
                return new_rate
            return None
        rate = new_rate
    return None


def _compute_xirr(cash_flows: list[float], dates: list[date]) -> float:
    """Compute XIRR and return it as a percentage value.

    Example: returns ``12.54`` to mean ``12.54 %``.

    Raises
    ------
    XirrCalculationError
        When no starting guess converges within ``_MAX_ITER`` iterations.
    """
    if len(cash_flows) < 2:
        raise XirrCalculationError(
            message="Cannot calculate XIRR",
            details=ErrorMessages.XIRR_CONVERGENCE_FAILURE,
        )

    d0 = dates[0]
    day_fractions = [(d - d0).days / 365.0 for d in dates]

    for guess in _STARTING_GUESSES:
        rate = _newton_raphson(cash_flows, day_fractions, guess)
        if rate is not None:
            xirr_pct = round(rate * 100.0, DECIMAL_PLACES_XIRR)
            logger.info("XIRR converged: %.4f%% (guess=%.2f)", xirr_pct, guess)
            return xirr_pct

    raise XirrCalculationError(
        message="Cannot calculate XIRR",
        details=ErrorMessages.XIRR_CONVERGENCE_FAILURE,
    )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def calculate(validated_rows: list[dict]) -> tuple[float, SummaryMetrics]:
    """Calculate XIRR and summary metrics from validated transaction data.

    Parameters
    ----------
    validated_rows:
        Output of ``validator.validate()`` — list of typed, validated row
        dicts containing ``date`` (:class:`datetime.date`),
        ``category`` (:class:`TransactionCategory`), and ``amount`` (float).

    Returns
    -------
    tuple[float, SummaryMetrics]
        - XIRR as a percentage value (e.g., ``12.54`` means 12.54 %)
        - Populated :class:`SummaryMetrics` instance

    Raises
    ------
    XirrCalculationError
        When XIRR calculation fails to converge.
    """
    cash_flows: list[float] = []
    cf_dates: list[date] = []
    total_invested: float = 0.0
    final_proceeds: float = 0.0

    for row in validated_rows:
        category: TransactionCategory = row["category"]
        amount: float = row["amount"]
        d: date = row["date"]

        # --- Summary metrics ---
        if category in TOTAL_INVESTED_CATEGORIES:
            total_invested += amount

        if category in TERMINAL_CATEGORIES:
            # Track last SELL/REDEMPTION; spec requires the file ends with one
            final_proceeds = amount

        # --- XIRR cash flows (STAMP_DUTY excluded entirely) ---
        if category in XIRR_EXCLUDED_CATEGORIES:
            continue
        if category in XIRR_OUTFLOW_CATEGORIES:
            cash_flows.append(-amount)
            cf_dates.append(d)
        elif category in XIRR_INFLOW_CATEGORIES:
            cash_flows.append(amount)
            cf_dates.append(d)

    xirr_pct = _compute_xirr(cash_flows, cf_dates)

    metrics = SummaryMetrics(
        totalInvested=round(total_invested, DECIMAL_PLACES_AMOUNT),
        finalProceeds=round(final_proceeds, DECIMAL_PLACES_AMOUNT),
        profitLoss=round(final_proceeds - total_invested, DECIMAL_PLACES_AMOUNT),
    )

    logger.info(
        "Summary — XIRR: %.2f%% | Invested: %.2f | Proceeds: %.2f | P/L: %.2f",
        xirr_pct,
        metrics.totalInvested,
        metrics.finalProceeds,
        metrics.profitLoss,
    )

    return xirr_pct, metrics
