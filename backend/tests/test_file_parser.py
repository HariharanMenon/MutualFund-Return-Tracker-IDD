"""
test_file_parser.py — Unit tests for Excel file parsing service.

Tests: valid xlsx loading, first-sheet-only rule, header normalisation,
empty row skipping, corrupt input handling.
"""

import io

import openpyxl
import pytest

from app.exceptions.file_error import FileProcessingError
from app.services.file_parser import parse_excel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_xlsx(headers: list, rows: list) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_parse_returns_correct_row_count(valid_xlsx):
    rows = parse_excel(valid_xlsx)
    assert len(rows) == 2


def test_parse_headers_normalised(valid_xlsx):
    rows = parse_excel(valid_xlsx)
    expected_keys = {"date", "transaction type", "amount", "units", "price", "unit balance"}
    assert set(rows[0].keys()) == expected_keys


def test_parse_row_values(valid_xlsx):
    rows = parse_excel(valid_xlsx)
    first = rows[0]
    assert first["transaction type"] == "Purchase"
    assert first["amount"] == 10000


def test_parse_uppercase_headers(uppercase_headers_xlsx):
    """Case-insensitive header normalisation — spec §3."""
    rows = parse_excel(uppercase_headers_xlsx)
    assert "date" in rows[0]
    assert "transaction type" in rows[0]


# ---------------------------------------------------------------------------
# First-sheet-only rule (spec §3)
# ---------------------------------------------------------------------------

def test_first_sheet_only(multi_sheet_xlsx):
    """Only the first worksheet is parsed; second sheet data is ignored."""
    rows = parse_excel(multi_sheet_xlsx)
    # First sheet has 2 data rows
    assert len(rows) == 2
    # No 'garbage' value from the second sheet
    all_values = [str(v) for row in rows for v in row.values() if v is not None]
    assert "garbage" not in all_values


# ---------------------------------------------------------------------------
# Empty row skipping
# ---------------------------------------------------------------------------

def test_empty_rows_skipped():
    xlsx = _make_xlsx(
        ["Date", "Transaction Type", "Amount", "Units", "Price", "Unit Balance"],
        [
            ["01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0],
            [None, None, None, None, None, None],   # fully empty → should be skipped
            ["01-Jan-2021", "SELL", 11500, 100.0, None, None],
        ],
    )
    rows = parse_excel(xlsx)
    assert len(rows) == 2


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_corrupt_bytes_raises():
    with pytest.raises(FileProcessingError, match="could not be read"):
        parse_excel(b"this is not an xlsx file")


def test_empty_bytes_raises():
    with pytest.raises(FileProcessingError):
        parse_excel(b"")


def test_empty_worksheet_raises():
    """Workbook with a completely empty first worksheet."""
    wb = openpyxl.Workbook()
    wb.active  # empty sheet, no rows
    buf = io.BytesIO()
    wb.save(buf)
    xlsx_bytes = buf.getvalue()
    with pytest.raises(FileProcessingError):
        parse_excel(xlsx_bytes)


# ---------------------------------------------------------------------------
# None cells preserved as None
# ---------------------------------------------------------------------------

def test_none_cells_preserved():
    """Cells left blank are returned as None (not empty string)."""
    xlsx = _make_xlsx(
        ["Date", "Transaction Type", "Amount", "Units", "Price", "Unit Balance"],
        [
            ["01-Jan-2020", "Purchase", 10000, 100.0, 100.0, 100.0],
            ["01-Jan-2021", "SELL", 11500, 100.0, None, None],
        ],
    )
    rows = parse_excel(xlsx)
    sell_row = rows[1]
    assert sell_row["price"] is None
    assert sell_row["unit balance"] is None
