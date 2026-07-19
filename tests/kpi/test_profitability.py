"""
Sprint 2
Financial Ratio Engine

Profitability KPI Unit Tests

Covers

1. Net Profit Margin
2. Operating Profit Margin
3. ROE
4. ROCE
5. ROA
"""

import pytest

from src.analytics.ratios import FinancialRatioCalculator


# ==========================================================
# Net Profit Margin
# ==========================================================

def test_net_profit_margin_normal():
    result = FinancialRatioCalculator.net_profit_margin(
        sales=1000,
        net_profit=200,
    )

    assert result.value == 20.0
    assert result.flag is None


def test_net_profit_margin_zero_sales():
    result = FinancialRatioCalculator.net_profit_margin(
        sales=0,
        net_profit=200,
    )

    assert result.value is None


# ==========================================================
# Operating Profit Margin
# ==========================================================

def test_operating_profit_margin_normal():
    result = FinancialRatioCalculator.operating_profit_margin(
        sales=1000,
        operating_profit=250,
        source_opm=25,
    )

    assert result.value == 25.0
    assert result.flag is None


def test_operating_profit_margin_mismatch():
    result = FinancialRatioCalculator.operating_profit_margin(
        sales=1000,
        operating_profit=250,
        source_opm=30,
    )

    assert result.value == 25.0
    assert result.flag == "OPM_MISMATCH"


# ==========================================================
# Return On Equity
# ==========================================================

def test_return_on_equity_normal():
    result = FinancialRatioCalculator.return_on_equity(
        net_profit=200,
        equity_capital=100,
        reserves=900,
    )

    assert result.value == 20.0
    assert result.flag is None


def test_return_on_equity_negative_equity():
    result = FinancialRatioCalculator.return_on_equity(
        net_profit=200,
        equity_capital=-100,
        reserves=50,
    )

    assert result.value is None
    assert result.flag == "NEGATIVE_EQUITY"


# ==========================================================
# ROCE
# ==========================================================

def test_return_on_capital_employed_normal():
    result = FinancialRatioCalculator.return_on_capital_employed(
        operating_profit=180,
        interest=20,
        equity_capital=500,
        reserves=500,
        borrowings=500,
    )

    # EBIT = 180 + 20 = 200
    # Capital = 1500
    # ROCE = 13.33%

    assert result.value == 13.33
    assert result.flag is None


# ==========================================================
# ROA
# ==========================================================

def test_return_on_assets_normal():
    result = FinancialRatioCalculator.return_on_assets(
        net_profit=150,
        total_assets=1000,
    )

    assert result.value == 15.0
    assert result.flag is None


def test_return_on_assets_zero_assets():
    result = FinancialRatioCalculator.return_on_assets(
        net_profit=150,
        total_assets=0,
    )

    assert result.value is None


# ==========================================================
# Complete Profitability Summary
# ==========================================================

def test_profitability_summary_contains_all_fields():

    result = FinancialRatioCalculator.profitability_summary(
        sales=1000,
        net_profit=150,
        operating_profit=200,
        source_opm=20,
        equity_capital=200,
        reserves=800,
        borrowings=500,
        interest=20,
        total_assets=2000,
    )

    expected_keys = {
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "return_on_capital_employed_pct",
        "return_on_assets_pct",
        "opm_flag",
        "roe_flag",
        "roce_flag",
        "roa_flag",
    }

    assert expected_keys.issubset(result.keys())