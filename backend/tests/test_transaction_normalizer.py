"""
test_transaction_normalizer.py — Unit tests for transaction type normalisation.

Covers: all spec-defined variants, case-insensitivity, whitespace tolerance,
and rejection of unknown types.
"""

import pytest

from app.utils.constants import TransactionCategory
from app.utils.transaction_normalizer import get_category, is_known_type


# ---------------------------------------------------------------------------
# PURCHASE variants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Purchase", "purchase", "PURCHASE",
    "Buy", "buy", "BUY",
    "SIP", "sip", "Sip",
    "SIP Purchase", "sip purchase", "SIP PURCHASE",
    "Systematic Investment", "systematic investment", "SYSTEMATIC INVESTMENT",
    "Systematic Investment Plan", "systematic investment plan",
])
def test_purchase_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.PURCHASE


# ---------------------------------------------------------------------------
# SELL variants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["SELL", "sell", "Sell"])
def test_sell_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.SELL


# ---------------------------------------------------------------------------
# REDEMPTION variants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["REDEMPTION", "redemption", "Redemption"])
def test_redemption_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.REDEMPTION


# ---------------------------------------------------------------------------
# DIVIDEND_REINVEST variants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Dividend Reinvest", "dividend reinvest",
    "DIVIDEND REINVEST", "Dividend Reinvestment",
])
def test_dividend_reinvest_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.DIVIDEND_REINVEST


# ---------------------------------------------------------------------------
# STAMP_DUTY variants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Stamp Duty", "stamp duty", "STAMP DUTY",
    "STT Paid", "stt paid", "STT PAID",
])
def test_stamp_duty_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.STAMP_DUTY


# ---------------------------------------------------------------------------
# Whitespace tolerance
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "  Purchase  ", "\tSELL\t", " SIP ", "  Stamp Duty  ",
])
def test_whitespace_stripped(raw):
    result = get_category(raw, 1)
    assert result in TransactionCategory.__members__.values()


# ---------------------------------------------------------------------------
# Unknown type → ValueError with row number
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Unknown", "TRANSFER", "BONUS", "Dividend", "Growth",
    "", "123",
])
def test_unknown_type_raises(raw):
    with pytest.raises(ValueError, match=r"Row 5"):
        get_category(raw, 5)


# ---------------------------------------------------------------------------
# is_known_type helper
# ---------------------------------------------------------------------------

def test_is_known_type_true():
    assert is_known_type("Purchase") is True
    assert is_known_type("SELL") is True
    assert is_known_type("stamp duty") is True


def test_is_known_type_false():
    assert is_known_type("Unknown") is False
    assert is_known_type("") is False
    assert is_known_type("Transfer") is False
