"""
test_file_parser.py is at test_file_parser.py (already created).
This file is test_routes_upload.py — integration tests for POST /api/upload.

All tests use the shared TestClient fixture from conftest.py and send real
xlsx bytes as multipart/form-data uploads. This exercises the full stack:
  file_parser → validator → transaction_processor → xirr_calculator → response
"""

import pytest

from config import MAX_FILE_SIZE
from tests.conftest import make_xlsx_bytes

_HEADERS = ["Date", "Transaction Type", "Amount", "Units", "Price", "Unit Balance"]
_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _post(client, xlsx_bytes: bytes, filename: str = "fund.xlsx"):
    return client.post(
        "/api/upload",
        files={"file": (filename, xlsx_bytes, _MIME)},
    )


# ---------------------------------------------------------------------------
# Happy path (200 OK)
# ---------------------------------------------------------------------------

def test_upload_happy_path_status(client, valid_xlsx):
    resp = _post(client, valid_xlsx)
    assert resp.status_code == 200


def test_upload_happy_path_success_true(client, valid_xlsx):
    data = _post(client, valid_xlsx).json()
    assert data["success"] is True


def test_upload_happy_path_xirr_present(client, valid_xlsx):
    data = _post(client, valid_xlsx).json()
    assert data["xirr"] is not None
    assert isinstance(data["xirr"], float)


def test_upload_happy_path_xirr_value(client, valid_xlsx):
    data = _post(client, valid_xlsx).json()
    # XIRR for Purchase 10000 → SELL 11500 over ~1 year ≈ 14.96%
    assert abs(data["xirr"] - 14.96) < 0.5


def test_upload_happy_path_summary_metrics(client, valid_xlsx):
    data = _post(client, valid_xlsx).json()
    metrics = data["summaryMetrics"]
    assert metrics is not None
    assert metrics["totalInvested"] == pytest.approx(10000.0, abs=0.01)
    assert metrics["finalProceeds"] == pytest.approx(11500.0, abs=0.01)
    assert metrics["profitLoss"] == pytest.approx(1500.0, abs=0.01)


def test_upload_happy_path_transactions_list(client, valid_xlsx):
    data = _post(client, valid_xlsx).json()
    txs = data["transactions"]
    assert isinstance(txs, list)
    assert len(txs) == 2


def test_upload_happy_path_transaction_fields(client, valid_xlsx):
    data = _post(client, valid_xlsx).json()
    tx = data["transactions"][0]
    assert "date" in tx
    assert "transactionType" in tx
    assert "amount" in tx


def test_upload_happy_path_no_error_field(client, valid_xlsx):
    data = _post(client, valid_xlsx).json()
    assert data["error"] is None


def test_upload_stamp_duty_happy_path(client, stamp_duty_xlsx):
    data = _post(client, stamp_duty_xlsx).json()
    assert data["success"] is True
    # Total Invested includes Stamp Duty (10000 + 50 = 10050)
    assert data["summaryMetrics"]["totalInvested"] == pytest.approx(10050.0, abs=0.01)


def test_upload_transaction_date_format(client, valid_xlsx):
    """Transaction dates returned in DD-MMM-YYYY format."""
    data = _post(client, valid_xlsx).json()
    assert data["transactions"][0]["date"] == "01-Jan-2020"


def test_upload_transactions_in_file_order(client, valid_xlsx):
    """Transactions must be returned in original file order (no sorting)."""
    data = _post(client, valid_xlsx).json()
    assert data["transactions"][0]["transactionType"] == "Purchase"
    assert data["transactions"][1]["transactionType"] == "SELL"


# ---------------------------------------------------------------------------
# File too large (413)
# ---------------------------------------------------------------------------

def test_upload_file_too_large(client, monkeypatch):
    import app.api.routes.upload as upload_mod
    monkeypatch.setattr(upload_mod, "MAX_FILE_SIZE", 10)
    resp = _post(client, b"a" * 100)
    assert resp.status_code == 413


def test_upload_file_too_large_error_message(client, monkeypatch):
    import app.api.routes.upload as upload_mod
    monkeypatch.setattr(upload_mod, "MAX_FILE_SIZE", 10)
    data = _post(client, b"a" * 100).json()
    assert data["success"] is False
    assert "10 mb" in data["error"]["details"].lower()


# ---------------------------------------------------------------------------
# Validation errors (400)
# ---------------------------------------------------------------------------

def test_upload_corrupt_file_400(client):
    resp = _post(client, b"this is not a valid xlsx file")
    assert resp.status_code == 400


def test_upload_corrupt_file_success_false(client):
    data = _post(client, b"not xlsx").json()
    assert data["success"] is False
    assert data["error"] is not None


def test_upload_missing_date_column_400(client, missing_date_col_xlsx):
    resp = _post(client, missing_date_col_xlsx)
    assert resp.status_code == 400


def test_upload_missing_date_column_message(client, missing_date_col_xlsx):
    data = _post(client, missing_date_col_xlsx).json()
    assert data["success"] is False
    assert "date" in data["error"]["details"].lower()


def test_upload_invalid_date_format_400(client, invalid_dates_xlsx):
    resp = _post(client, invalid_dates_xlsx)
    assert resp.status_code == 400


def test_upload_invalid_date_format_message(client, invalid_dates_xlsx):
    data = _post(client, invalid_dates_xlsx).json()
    assert "dd-mmm-yyyy" in data["error"]["details"].lower()


def test_upload_no_redemption_400(client, no_redemption_xlsx):
    resp = _post(client, no_redemption_xlsx)
    assert resp.status_code == 400


def test_upload_no_redemption_message(client, no_redemption_xlsx):
    data = _post(client, no_redemption_xlsx).json()
    # Last transaction is Purchase, so expect "sell or redemption" in message
    assert "sell" in data["error"]["details"].lower() or \
           "redemption" in data["error"]["details"].lower()


# ---------------------------------------------------------------------------
# Health check endpoint
# ---------------------------------------------------------------------------

def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Response envelope structure
# ---------------------------------------------------------------------------

def test_error_response_has_no_xirr(client, missing_date_col_xlsx):
    data = _post(client, missing_date_col_xlsx).json()
    assert data["xirr"] is None


def test_error_response_has_no_transactions(client, missing_date_col_xlsx):
    data = _post(client, missing_date_col_xlsx).json()
    assert data["transactions"] is None


def test_error_response_has_no_summary_metrics(client, missing_date_col_xlsx):
    data = _post(client, missing_date_col_xlsx).json()
    assert data["summaryMetrics"] is None
