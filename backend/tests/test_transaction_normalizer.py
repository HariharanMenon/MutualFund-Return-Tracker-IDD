"""
test_transaction_normalizer.py — Unit tests for transaction type normalisation.

Covers: all spec-defined variants, case-insensitivity, whitespace tolerance,
Tier-2 keyword-contains matching for generic real-world fund statement phrases,
and rejection of unknown types.
"""

import pytest

from app.utils.constants import TransactionCategory
from app.utils.transaction_normalizer import get_category, is_known_type


# ---------------------------------------------------------------------------
# PURCHASE variants — Tier 1 exact match
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
# SELL variants — Tier 1 exact match
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["SELL", "sell", "Sell"])
def test_sell_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.SELL


# ---------------------------------------------------------------------------
# REDEMPTION variants — Tier 1 exact match
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", ["REDEMPTION", "redemption", "Redemption"])
def test_redemption_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.REDEMPTION


# ---------------------------------------------------------------------------
# DIVIDEND_REINVEST variants — Tier 1 exact match
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Dividend Reinvest", "dividend reinvest",
    "DIVIDEND REINVEST", "Dividend Reinvestment",
])
def test_dividend_reinvest_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.DIVIDEND_REINVEST


# ---------------------------------------------------------------------------
# STAMP_DUTY variants — Tier 1 exact match
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Stamp Duty", "stamp duty", "STAMP DUTY",
    "STT Paid", "stt paid", "STT PAID",
])
def test_stamp_duty_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.STAMP_DUTY


# ---------------------------------------------------------------------------
# GROSS_PURCHASE variants — Tier 1 exact match
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Gross Purchase", "gross purchase", "GROSS PURCHASE",
    "Gross Purchase Systematic", "gross purchase systematic", "GROSS PURCHASE SYSTEMATIC",
])
def test_gross_purchase_variants(raw):
    assert get_category(raw, 1) == TransactionCategory.GROSS_PURCHASE


# ---------------------------------------------------------------------------
# Whitespace tolerance
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "  Purchase  ", "\tSELL\t", " SIP ", "  Stamp Duty  ", "  Gross Purchase  ",
])
def test_whitespace_stripped(raw):
    result = get_category(raw, 1)
    assert result in TransactionCategory.__members__.values()


# ---------------------------------------------------------------------------
# Tier 2 — keyword-contains: PURCHASE generic phrases
# Real-world fund statement values that don't appear in the exact variant sets
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Net Purchase",
    "Additional Purchase",
    "Fresh Purchase",
    "Lumpsum Purchase",
    "Switch In - Growth",
    "Switch In",
    "Fresh SIP",
    "SIP - Monthly",
    "Systematic Investment - Weekly",
])
def test_purchase_keyword_fallback(raw):
    assert get_category(raw, 1) == TransactionCategory.PURCHASE


# ---------------------------------------------------------------------------
# Tier 2 — keyword-contains: REDEMPTION generic phrases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "SWP Redemption",
    "Partial Redemption",
    "Full Redemption",
    "Switch Out",
    "SWP",
    "SWP - Monthly",
])
def test_redemption_keyword_fallback(raw):
    assert get_category(raw, 1) == TransactionCategory.REDEMPTION


# ---------------------------------------------------------------------------
# Tier 2 — keyword-contains: SELL generic phrases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Partial Sell",
    "Full Sell",
    "Force Sell",
])
def test_sell_keyword_fallback(raw):
    assert get_category(raw, 1) == TransactionCategory.SELL


# ---------------------------------------------------------------------------
# Tier 2 — keyword-contains: DIVIDEND_REINVEST generic phrases
# "Dividend" alone (without "reinvest") should map to DIVIDEND_REINVEST
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Dividend",
    "dividend",
    "DIVIDEND",
    "Dividend - Growth Option",
    "Dividend Payout",
])
def test_dividend_keyword_fallback(raw):
    assert get_category(raw, 1) == TransactionCategory.DIVIDEND_REINVEST


# ---------------------------------------------------------------------------
# Tier 2 — keyword-contains: STAMP_DUTY generic phrases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Less: STT",
    "Less: STT Paid",
    "Less: Stamp Duty",
    "STT - Equity",
])
def test_stamp_duty_keyword_fallback(raw):
    assert get_category(raw, 1) == TransactionCategory.STAMP_DUTY


# ---------------------------------------------------------------------------
# Tier 2 — keyword-contains: GROSS_PURCHASE generic phrases
# Real-world platform phrases (e.g. MFUTILITY) that contain "gross purchase"
# but are not in the exact variant frozenset
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Gross Purchase - via MFUTILITY",
    "Gross Purchase Systematic - Instalment 2/155",
    "Gross Purchase Systematic - Instalment 10/155",
    "GROSS PURCHASE - VIA MFUTILITY",
    "gross purchase - via mfutility",
])
def test_gross_purchase_keyword_fallback(raw):
    assert get_category(raw, 1) == TransactionCategory.GROSS_PURCHASE


# ---------------------------------------------------------------------------
# Tier 2 — classification priority (ordering correctness)
# These values contain keywords from multiple categories; verify the correct
# one wins based on CATEGORY_KEYWORDS ordering in constants.py
# ---------------------------------------------------------------------------

def test_stt_beats_purchase():
    # "stt" keyword appears in STAMP_DUTY before PURCHASE scan begins
    assert get_category("STT Purchase Adjustment", 1) == TransactionCategory.STAMP_DUTY

def test_switch_out_beats_purchase():
    # "switch out" is listed under REDEMPTION; must not fall through to PURCHASE
    assert get_category("Switch Out - Growth", 1) == TransactionCategory.REDEMPTION

def test_switch_in_maps_to_purchase():
    # "switch in" is listed under PURCHASE
    assert get_category("Switch In - Growth", 1) == TransactionCategory.PURCHASE

def test_gross_purchase_beats_purchase():
    # "gross purchase" contains "purchase" — GROSS_PURCHASE must win because
    # its keyword is checked before PURCHASE in CATEGORY_KEYWORDS
    assert get_category("Gross Purchase - via MFUTILITY", 1) == TransactionCategory.GROSS_PURCHASE

def test_gross_purchase_systematic_instalment_beats_purchase():
    # Multi-word instalment variant must not fall through to PURCHASE
    assert get_category("Gross Purchase Systematic - Instalment 2/155", 1) == TransactionCategory.GROSS_PURCHASE


# ---------------------------------------------------------------------------
# Unknown type → ValueError with row number
# NOTE: "Dividend" removed from this list — it now maps to DIVIDEND_REINVEST
#       via Tier-2 keyword match ("dividend" keyword).
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("raw", [
    "Unknown", "TRANSFER", "BONUS", "Growth",
    "", "123",
])
def test_unknown_type_raises(raw):
    with pytest.raises(ValueError, match=r"Row 5"):
        get_category(raw, 5)


# ---------------------------------------------------------------------------
# is_known_type helper — Tier 1 exact matches still return True
# ---------------------------------------------------------------------------

def test_is_known_type_true():
    assert is_known_type("Purchase") is True
    assert is_known_type("SELL") is True
    assert is_known_type("stamp duty") is True
    assert is_known_type("Gross Purchase") is True
    assert is_known_type("gross purchase systematic") is True


# ---------------------------------------------------------------------------
# is_known_type helper — Tier 2 keyword matches now return True
# ---------------------------------------------------------------------------

def test_is_known_type_true_tier2():
    assert is_known_type("Net Purchase") is True
    assert is_known_type("SWP Redemption") is True
    assert is_known_type("Switch Out") is True
    assert is_known_type("Dividend") is True
    assert is_known_type("Less: STT") is True
    assert is_known_type("Gross Purchase - via MFUTILITY") is True
    assert is_known_type("Gross Purchase Systematic - Instalment 2/155") is True


# ---------------------------------------------------------------------------
# is_known_type helper — genuinely unrecognised strings return False
# ---------------------------------------------------------------------------

def test_is_known_type_false():
    assert is_known_type("Unknown") is False
    assert is_known_type("") is False
    assert is_known_type("Transfer") is False
    assert is_known_type("BONUS") is False
    assert is_known_type("Growth") is False
