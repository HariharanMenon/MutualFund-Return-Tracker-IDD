"""
validator.py — Full data validation engine.

Validates raw parsed Excel data against all spec rules (§3 Step 4, §6):

  Column-level:
    1.  Required headers present: Date, Transaction Type, Amount
    2.  Row count >= 2 and <= 10,000

  Per-row (in file order, stops on first error):
    3.  Transaction type is recognised (case-insensitive)
    4.  Date is DD-MMM-YYYY format, in range [1960-01-01, today]
    5.  Amount is numeric and positive
    6.  PURCHASE / DIVIDEND_REINVEST: Units, Price, Unit Balance required and positive
    7.  SELL / REDEMPTION: Units required and positive; Price and Unit Balance MUST be empty
    8.  STAMP_DUTY: Units optional; Price and Unit Balance MUST be empty
    9.  Unit balance consistency: cumulative units must match Unit Balance column (within tolerance)

  File-level:
    10. Last transaction must be SELL or REDEMPTION
    11. Cumulative unit balance must be ~0 after all transactions (full exit)

Returns a list of typed validated row dicts on success.
Raises FileValidationError on the first detected violation.
"""

import datetime
from typing import Any, Optional

from app.exceptions.validation_error import FileValidationError
from app.utils.constants import (
    COL_DATE,
    COL_TRANSACTION_TYPE,
    COL_AMOUNT,
    COL_UNITS,
    COL_PRICE,
    COL_UNIT_BALANCE,
    MANDATORY_HEADER_COLUMNS,
    MAX_TRANSACTIONS,
    MIN_TRANSACTIONS,
    PRICE_UNIT_BALANCE_EMPTY_CATEGORIES,
    PRICE_UNIT_BALANCE_REQUIRED_CATEGORIES,
    TERMINAL_CATEGORIES,
    UNITS_OPTIONAL_CATEGORIES,
    UNITS_REQUIRED_CATEGORIES,
    UNIT_BALANCE_TOLERANCE,
    TransactionCategory,
    ErrorMessages,
)
from app.utils.date_parser import format_date, parse_date
from app.utils.logger import get_logger
from app.utils.transaction_normalizer import get_category

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_empty(value: Any) -> bool:
    """Return True when a cell value should be treated as absent/empty."""
    return value is None or (isinstance(value, str) and value.strip() == "")


def _cell_to_date_string(raw: Any) -> str:
    """Convert a raw openpyxl cell value to a stripped string for parse_date().

    openpyxl may return ``datetime.datetime`` objects for date-formatted cells
    (when data_only=True).  This function normalises those back to a
    DD-MMM-YYYY string so parse_date() can apply its format + range checks.
    """
    if isinstance(raw, datetime.datetime):
        return format_date(raw.date())
    if isinstance(raw, datetime.date):
        return format_date(raw)
    if raw is None:
        return ""
    return str(raw).strip()


def _parse_positive_numeric(
    value: Any,
    row: int,
    non_numeric_msg_tpl: str,
    negative_msg_tpl: str,
) -> float:
    """Parse *value* to a positive float.

    Parameters
    ----------
    value:
        Raw cell value (already confirmed non-empty by caller).
    row:
        1-based data row number for error messages.
    non_numeric_msg_tpl:
        ``ErrorMessages`` template with ``{row}`` and ``{value}`` placeholders.
    negative_msg_tpl:
        ``ErrorMessages`` template with ``{row}`` and ``{value}`` placeholders.

    Raises
    ------
    ValueError
        With a spec-formatted message when the value is non-numeric or negative.
    """
    try:
        result = float(value)
    except (ValueError, TypeError):
        raise ValueError(non_numeric_msg_tpl.format(row=row, value=value))

    if result < 0:
        raise ValueError(negative_msg_tpl.format(row=row, value=value))

    return result


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def validate(raw_rows: list[dict[str, Any]]) -> list[dict]:
    """Validate raw parsed rows and return typed validated data.

    Parameters
    ----------
    raw_rows:
        Output of ``file_parser.parse_excel()`` — list of dicts with
        normalised (lowercase, stripped) keys and raw cell values.

    Returns
    -------
    list[dict]
        Validated rows in original file order.  Each dict contains:

        - ``date_str``     — DD-MMM-YYYY string (for ``Transaction`` model)
        - ``date``         — :class:`datetime.date` object (for XIRR)
        - ``raw_type``     — original transaction type string (display)
        - ``category``     — :class:`TransactionCategory`
        - ``amount``       — ``float`` (positive)
        - ``units``        — ``float`` or ``None``
        - ``price``        — ``float`` or ``None`` (preserved as entered)
        - ``unit_balance`` — ``float`` or ``None``

    Raises
    ------
    FileValidationError
        On the first validation failure, with a spec-formatted error
        message and details including the row number when applicable.
    """

    # ------------------------------------------------------------------ #
    # Rule 1 — Required column headers                                     #
    # ------------------------------------------------------------------ #
    present_headers: set[str] = set(raw_rows[0].keys()) if raw_rows else set()
    for col in MANDATORY_HEADER_COLUMNS:
        if col not in present_headers:
            raise FileValidationError(
                message="File validation failed",
                details=ErrorMessages.MISSING_COLUMN.format(column=col.title()),
            )

    # ------------------------------------------------------------------ #
    # Rule 2 — Row count bounds                                            #
    # ------------------------------------------------------------------ #
    if len(raw_rows) < MIN_TRANSACTIONS:
        raise FileValidationError(
            message="File validation failed",
            details=ErrorMessages.INSUFFICIENT_TRANSACTIONS,
        )
    if len(raw_rows) > MAX_TRANSACTIONS:
        raise FileValidationError(
            message="File validation failed",
            details=ErrorMessages.TOO_MANY_TRANSACTIONS.format(
                max_rows=MAX_TRANSACTIONS,
                actual_rows=len(raw_rows),
            ),
        )

    # ------------------------------------------------------------------ #
    # Rules 3–9 — Per-row validation                                       #
    # ------------------------------------------------------------------ #
    validated: list[dict] = []
    cumulative_units: float = 0.0

    for data_idx, raw in enumerate(raw_rows):
        row_num = data_idx + 1  # 1-based for user-facing messages

        # ---- Transaction Type (Rule 3) ----
        raw_type_val = raw.get(COL_TRANSACTION_TYPE)
        if _is_empty(raw_type_val):
            raise FileValidationError(
                message="File validation failed",
                details=ErrorMessages.UNKNOWN_TRANSACTION_TYPE.format(
                    row=row_num, value="(empty)"
                ),
            )
        raw_type = str(raw_type_val).strip()
        try:
            category = get_category(raw_type, row_num)
        except ValueError as exc:
            raise FileValidationError(message="File validation failed", details=str(exc))

        # ---- Date (Rule 4) ----
        raw_date_val = raw.get(COL_DATE)
        if _is_empty(raw_date_val):
            raise FileValidationError(
                message="File validation failed",
                details=ErrorMessages.INVALID_DATE_FORMAT.format(
                    row=row_num, value="(empty)"
                ),
            )
        date_str_for_parse = _cell_to_date_string(raw_date_val)
        try:
            parsed_date = parse_date(date_str_for_parse, row_num)
        except ValueError as exc:
            raise FileValidationError(message="File validation failed", details=str(exc))
        date_str = format_date(parsed_date)

        # ---- Amount (Rule 5) ----
        raw_amount = raw.get(COL_AMOUNT)
        if _is_empty(raw_amount):
            raise FileValidationError(
                message="File validation failed",
                details=ErrorMessages.NON_NUMERIC_AMOUNT.format(row=row_num, value="(empty)"),
            )
        try:
            amount = _parse_positive_numeric(
                raw_amount, row_num,
                ErrorMessages.NON_NUMERIC_AMOUNT,
                ErrorMessages.NEGATIVE_AMOUNT,
            )
        except ValueError as exc:
            raise FileValidationError(message="File validation failed", details=str(exc))

        # ---- Units (Rules 6, 7, 8) ----
        raw_units = raw.get(COL_UNITS)
        units_empty = _is_empty(raw_units)

        if category in UNITS_REQUIRED_CATEGORIES and units_empty:
            if category in (TransactionCategory.SELL, TransactionCategory.REDEMPTION):
                msg = ErrorMessages.SELL_MISSING_UNITS.format(row=row_num)
            else:
                msg = ErrorMessages.PURCHASE_MISSING_UNITS.format(
                    row=row_num, tx_type=raw_type
                )
            raise FileValidationError(message="File validation failed", details=msg)

        units: Optional[float] = None
        if not units_empty:
            try:
                units = _parse_positive_numeric(
                    raw_units, row_num,
                    ErrorMessages.NON_NUMERIC_UNITS,
                    ErrorMessages.NEGATIVE_UNITS,
                )
            except ValueError as exc:
                raise FileValidationError(message="File validation failed", details=str(exc))

        # ---- Price (Rules 6, 7, 8) ----
        raw_price = raw.get(COL_PRICE)
        price_empty = _is_empty(raw_price)

        if category in PRICE_UNIT_BALANCE_EMPTY_CATEGORIES and not price_empty:
            if category == TransactionCategory.STAMP_DUTY:
                detail = ErrorMessages.STAMP_DUTY_NON_EMPTY_PRICE_UNIT_BALANCE.format(
                    row=row_num
                )
            else:
                detail = ErrorMessages.SELL_NON_EMPTY_PRICE_UNIT_BALANCE.format(row=row_num)
            raise FileValidationError(message="File validation failed", details=detail)

        if category in PRICE_UNIT_BALANCE_REQUIRED_CATEGORIES and price_empty:
            raise FileValidationError(
                message="File validation failed",
                details=ErrorMessages.PURCHASE_MISSING_PRICE.format(
                    row=row_num, tx_type=raw_type
                ),
            )

        price: Optional[float] = None
        if not price_empty:
            try:
                price = _parse_positive_numeric(
                    raw_price, row_num,
                    ErrorMessages.NON_NUMERIC_PRICE,
                    ErrorMessages.NEGATIVE_PRICE,
                )
            except ValueError as exc:
                raise FileValidationError(message="File validation failed", details=str(exc))

        # ---- Unit Balance (Rules 6, 7, 8) ----
        raw_ub = raw.get(COL_UNIT_BALANCE)
        ub_empty = _is_empty(raw_ub)

        if category in PRICE_UNIT_BALANCE_EMPTY_CATEGORIES and not ub_empty:
            if category == TransactionCategory.STAMP_DUTY:
                detail = ErrorMessages.STAMP_DUTY_NON_EMPTY_PRICE_UNIT_BALANCE.format(
                    row=row_num
                )
            else:
                detail = ErrorMessages.SELL_NON_EMPTY_PRICE_UNIT_BALANCE.format(row=row_num)
            raise FileValidationError(message="File validation failed", details=detail)

        if category in PRICE_UNIT_BALANCE_REQUIRED_CATEGORIES and ub_empty:
            raise FileValidationError(
                message="File validation failed",
                details=ErrorMessages.PURCHASE_MISSING_UNIT_BALANCE.format(
                    row=row_num, tx_type=raw_type
                ),
            )

        unit_balance: Optional[float] = None
        if not ub_empty:
            try:
                unit_balance = _parse_positive_numeric(
                    raw_ub, row_num,
                    ErrorMessages.NON_NUMERIC_UNIT_BALANCE,
                    ErrorMessages.NEGATIVE_UNIT_BALANCE,
                )
            except ValueError as exc:
                raise FileValidationError(message="File validation failed", details=str(exc))

        # ---- Cumulative unit tracking + consistency check (Rule 9) ----
        if category in (TransactionCategory.PURCHASE, TransactionCategory.DIVIDEND_REINVEST):
            cumulative_units += units or 0.0
        elif category in (TransactionCategory.SELL, TransactionCategory.REDEMPTION):
            cumulative_units -= units or 0.0
        # STAMP_DUTY: no unit change

        if unit_balance is not None:
            diff = abs(cumulative_units - unit_balance)
            if diff > UNIT_BALANCE_TOLERANCE:
                raise FileValidationError(
                    message="File validation failed",
                    details=ErrorMessages.UNIT_BALANCE_MISMATCH.format(
                        row=row_num,
                        balance=unit_balance,
                        cumulative=round(cumulative_units, 3),
                    ),
                )

        validated.append(
            {
                "date_str": date_str,
                "date": parsed_date,
                "raw_type": raw_type,
                "category": category,
                "amount": float(amount),
                "units": float(units) if units is not None else None,
                "price": float(price) if price is not None else None,
                "unit_balance": float(unit_balance) if unit_balance is not None else None,
            }
        )

    # ------------------------------------------------------------------ #
    # Rule 10 — Last transaction must be SELL or REDEMPTION               #
    # ------------------------------------------------------------------ #
    last = validated[-1]
    if last["category"] not in TERMINAL_CATEGORIES:
        raise FileValidationError(
            message="File validation failed",
            details=ErrorMessages.LAST_NOT_SELL_OR_REDEMPTION.format(
                tx_type=last["raw_type"]
            ),
        )

    # ------------------------------------------------------------------ #
    # Rule 11 — Full exit: cumulative units must be ~0                    #
    # ------------------------------------------------------------------ #
    if abs(cumulative_units) > UNIT_BALANCE_TOLERANCE:
        raise FileValidationError(
            message="File validation failed",
            details=ErrorMessages.MISSING_FINAL_REDEMPTION,
        )

    logger.info("Validation passed: %d rows validated", len(validated))
    return validated
