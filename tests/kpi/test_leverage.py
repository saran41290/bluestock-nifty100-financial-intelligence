"""
Sprint 2
Financial Ratio Engine

Leverage & Efficiency KPI Unit Tests

Covers

1. Debt To Equity
2. Interest Coverage Ratio
3. Net Debt
4. Asset Turnover
5. Leverage Summary
"""

from src.analytics.ratios import FinancialRatioCalculator


# ==========================================================
# Debt To Equity
# ==========================================================

def test_debt_to_equity_normal():
    result = FinancialRatioCalculator.debt_to_equity(
        borrowings=500,
        equity_capital=500,
        reserves=500,
    )

    assert result.value == 0.5
    assert result.flag is None
    assert result.label is None


def test_debt_to_equity_debt_free():
    result = FinancialRatioCalculator.debt_to_equity(
        borrowings=0,
        equity_capital=500,
        reserves=500,
    )

    assert result.value == 0.0
    assert result.label == "Debt Free"


def test_debt_to_equity_high_leverage():
    result = FinancialRatioCalculator.debt_to_equity(
        borrowings=7000,
        equity_capital=500,
        reserves=500,
    )

    assert result.value == 7.0
    assert result.flag == "HIGH_LEVERAGE"


def test_debt_to_equity_negative_equity():
    result = FinancialRatioCalculator.debt_to_equity(
        borrowings=1000,
        equity_capital=-500,
        reserves=200,
    )

    assert result.value is None
    assert result.flag == "NEGATIVE_EQUITY"


# ==========================================================
# Interest Coverage Ratio
# ==========================================================

def test_interest_coverage_normal():
    result = FinancialRatioCalculator.interest_coverage_ratio(
        operating_profit=200,
        other_income=50,
        interest=50,
    )

    assert result.value == 5.0
    assert result.flag is None


def test_interest_coverage_debt_free():
    result = FinancialRatioCalculator.interest_coverage_ratio(
        operating_profit=200,
        other_income=50,
        interest=0,
    )

    assert result.value is None
    assert result.label == "Debt Free"


def test_interest_coverage_low_cover():
    result = FinancialRatioCalculator.interest_coverage_ratio(
        operating_profit=40,
        other_income=20,
        interest=50,
    )

    assert result.value == 1.2
    assert result.flag == "LOW_INTEREST_COVER"


# ==========================================================
# Net Debt
# ==========================================================

def test_net_debt_normal():
    result = FinancialRatioCalculator.net_debt(
        borrowings=1000,
        investments=400,
    )

    assert result.value == 600
    assert result.label is None


def test_net_debt_net_cash_company():
    result = FinancialRatioCalculator.net_debt(
        borrowings=500,
        investments=1000,
    )

    assert result.value == -500
    assert result.label == "NET_CASH"


# ==========================================================
# Asset Turnover
# ==========================================================

def test_asset_turnover_normal():
    result = FinancialRatioCalculator.asset_turnover(
        sales=1000,
        total_assets=500,
    )

    assert result.value == 2.0


def test_asset_turnover_zero_assets():
    result = FinancialRatioCalculator.asset_turnover(
        sales=1000,
        total_assets=0,
    )

    assert result.value is None
    assert result.flag == "ZERO_ASSETS"


# ==========================================================
# Complete Leverage Summary
# ==========================================================

def test_leverage_summary_contains_all_fields():

    result = FinancialRatioCalculator.leverage_summary(
        borrowings=500,
        equity_capital=500,
        reserves=500,
        operating_profit=300,
        other_income=50,
        interest=50,
        investments=100,
        sales=1000,
        total_assets=2000,
    )

    expected = {
        "debt_to_equity",
        "high_leverage_flag",
        "debt_label",
        "interest_coverage",
        "interest_flag",
        "icr_label",
        "net_debt",
        "net_debt_label",
        "asset_turnover",
        "asset_turnover_flag",
    }

    assert expected.issubset(result.keys())