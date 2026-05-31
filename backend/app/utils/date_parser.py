"""
date_parser.py — DD-MMM-YYYY date parsing and range validation.

Spec requirements:
- Accepted format: DD-MMM-YYYY  (e.g., 15-Jan-2020)
- Any other format → validation error with row number
- Valid date range: 1960-01-01 to today (inclusive)
- Future dates → validation error
- Dates before 1960 → validation error
"""

from datetime import date, datetime

from app.utils.constants import ErrorMessages

# strptime format code for DD-MMM-YYYY
_DATE_FMT: str = "%d-%b-%Y"

# Inclusive lower bound
_MIN_DATE: date = date(1960, 1, 1)


def parse_date(raw: str, row: int) -> date:
    """Parse a raw cell value to a :class:`datetime.date`.

    Parameters
    ----------
    raw:
        The raw string value from the Excel cell (already stripped).
    row:
        1-based data row index used in error messages.

    Returns
    -------
    date
        A valid :class:`datetime.date` within [1960-01-01, today].

    Raises
    ------
    ValueError
        With an error message matching the spec format when the value
        cannot be parsed or falls outside the acceptable range.
    """
    # --- Format validation ---
    try:
        parsed: date = datetime.strptime(raw, _DATE_FMT).date()
    except (ValueError, TypeError):
        raise ValueError(
            ErrorMessages.INVALID_DATE_FORMAT.format(row=row, value=raw)
        )

    # --- Range validation: before 1960 ---
    if parsed < _MIN_DATE:
        raise ValueError(
            ErrorMessages.DATE_BEFORE_MIN.format(row=row, value=raw)
        )

    # --- Range validation: future date ---
    if parsed > date.today():
        raise ValueError(
            ErrorMessages.DATE_IN_FUTURE.format(row=row, value=raw)
        )

    return parsed


def format_date(d: date) -> str:
    """Format a :class:`datetime.date` to DD-MMM-YYYY string.

    Example::

        format_date(date(2020, 1, 15))  # "15-Jan-2020"
    """
    return d.strftime(_DATE_FMT)
