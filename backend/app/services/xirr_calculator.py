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
  PURCHASE / DIVIDEND_REINVEST / STAMP_DUTY  →  negative  (money leaves investor)
  SELL / REDEMPTION                          →  positive  (money enters investor),
                                                netted against same-date STT_PAID
  STT_PAID                                   →  netted against the SELL/REDEMPTION
                                                inflow on the same date (Option B);
                                                no separate cash flow entry.
                                                Fallback: standalone negative outflow
                                                if no matching inflow exists on date.
  GROSS_PURCHASE                             →  excluded  (summary row — actual
                                                cash flows captured by Net Purchase
                                                + Stamp Duty rows)

Summary Metrics (spec §7):
  Total Invested  = Σ amount  for  PURCHASE + STAMP_DUTY rows
                    (STT_PAID excluded — it is a redemption-side tax, not a cost)
  Final Proceeds  = Σ amount  for  ALL SELL / REDEMPTION rows (absolute values)
                    minus total STT_PAID across all rows
  Profit / Loss   = Final Proceeds − Total Invested
"""

from datetime import date
from typing import Optional
import math

from app.exceptions.calculation_error import XirrCalculationError
from app.models.response import SummaryMetrics
from app.utils.constants import (
    DECIMAL_PLACES_AMOUNT,
    DECIMAL_PLACES_XIRR,
    ErrorMessages,
    STT_PAID_CATEGORIES,
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
        try:
            f = _npv(rate, cash_flows, day_fractions)
            df = _npv_deriv(rate, cash_flows, day_fractions)
        except OverflowError:
            return None

        # If values are not finite (inf/nan) treat as non-convergent
        if not (math.isfinite(f) and math.isfinite(df)):
            return None
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

    Notes
    -----
    Two-pass strategy is used to handle STT_PAID netting correctly:

    Pass 1 — Aggregate by date:
        Accumulate gross SELL/REDEMPTION inflows and STT_PAID amounts
        keyed by date, so netting can be applied per date in Pass 2.
        Also accumulate Total Invested and gross Final Proceeds.

    Pass 2 — Build XIRR cash flow array:
        For each SELL/REDEMPTION date, subtract same-date STT_PAID from
        the inflow before appending to the cash flow array.
        STT_PAID rows are skipped — they are consumed by netting.
        Fallback: any STT_PAID with no matching SELL/REDEMPTION on its
        date is appended as a standalone negative outflow.
    """
    # ------------------------------------------------------------------
    # Pass 1 — Collect per-date aggregates and summary metric accumulators
    # ------------------------------------------------------------------
    total_invested: float = 0.0
    gross_final_proceeds: float = 0.0   # sum of all SELL/REDEMPTION amounts
    total_stt_paid: float = 0.0         # sum of all STT_PAID amounts

    # Keyed by date — gross redemption inflows and STT_PAID totals per date.
    # Used in Pass 2 to build the netted XIRR cash flow array.
    inflow_by_date: dict[date, float] = {}
    stt_by_date: dict[date, float] = {}

    for row in validated_rows:
        category: TransactionCategory = row["category"]
        amount: float = row["amount"]
        d: date = row["date"]

        # Total Invested: PURCHASE + STAMP_DUTY only.
        # STT_PAID is intentionally excluded (redemption-side tax, not a cost).
        if category in TOTAL_INVESTED_CATEGORIES:
            total_invested += amount

        # Final Proceeds: accumulate ALL SELL/REDEMPTION rows (not just last).
        # Amounts are already positive floats (sign stripped in validator).
        if category in XIRR_INFLOW_CATEGORIES:
            gross_final_proceeds += amount
            inflow_by_date[d] = inflow_by_date.get(d, 0.0) + amount

        # STT_PAID: track total and per-date for netting against redemptions.
        if category in STT_PAID_CATEGORIES:
            total_stt_paid += amount
            stt_by_date[d] = stt_by_date.get(d, 0.0) + amount

    # Final Proceeds = gross redemption proceeds minus all STT_PAID deductions.
    # This reflects the net amount that actually arrives in the investor's bank.
    final_proceeds: float = gross_final_proceeds - total_stt_paid

    # ------------------------------------------------------------------
    # Pass 2 — Build XIRR cash flow array
    # ------------------------------------------------------------------
    # Track which STT_PAID dates have been consumed by netting so the
    # fallback path (standalone outflow) only fires for unmatched ones.
    stt_dates_netted: set[date] = set()

    cash_flows: list[float] = []
    cf_dates: list[date] = []

    for row in validated_rows:
        category = row["category"]
        amount = row["amount"]
        d = row["date"]

        # Skip summary rows — never enter the XIRR array.
        if category in XIRR_EXCLUDED_CATEGORIES:
            continue

        # STT_PAID is handled by netting; skip as a standalone entry here.
        # The fallback loop below catches any unmatched STT_PAID dates.
        if category in STT_PAID_CATEGORIES:
            continue

        if category in XIRR_OUTFLOW_CATEGORIES:
            # PURCHASE / DIVIDEND_REINVEST / STAMP_DUTY — negative cash flow.
            cash_flows.append(-amount)
            cf_dates.append(d)

        elif category in XIRR_INFLOW_CATEGORIES:
            # SELL / REDEMPTION — net against same-date STT_PAID if present.
            # Each date's inflow is only appended once (aggregated in Pass 1),
            # so we emit the full date aggregate, not each individual row.
            # We process each row individually but subtract the full date-level
            # STT once when we encounter the first inflow row for that date.
            if d not in stt_dates_netted and d in stt_by_date:
                # First SELL/REDEMPTION row on this date — absorb the full
                # date-level STT_PAID deduction into this single cash flow entry
                # so only one netted inflow per date appears in the array.
                net_inflow = inflow_by_date[d] - stt_by_date[d]
                cash_flows.append(net_inflow)
                cf_dates.append(d)
                stt_dates_netted.add(d)
            elif d not in stt_dates_netted:
                # No STT on this date — use the full date aggregate as-is.
                # Mark as processed so subsequent rows on the same date are skipped.
                cash_flows.append(inflow_by_date[d])
                cf_dates.append(d)
                stt_dates_netted.add(d)
            # else: already emitted a single aggregated entry for this date — skip.

    # Fallback: STT_PAID rows with no matching SELL/REDEMPTION on the same date.
    # Rare in practice (STT is always tied to a redemption) but handled for safety.
    for stt_date, stt_amount in stt_by_date.items():
        if stt_date not in stt_dates_netted:
            cash_flows.append(-stt_amount)
            cf_dates.append(stt_date)

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