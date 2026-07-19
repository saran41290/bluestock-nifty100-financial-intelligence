"""
Sprint 2
Financial Ratio Engine

CAGR Engine Unit Tests

Covers

1. Revenue CAGR
2. PAT CAGR
3. EPS CAGR
4. All CAGR Edge Cases
5. CAGR Summary
"""

from src.analytics.cagr import CAGRCalculator


# ==========================================================
# Normal CAGR
# ==========================================================

def test_cagr_normal():

    result = CAGRCalculator.calculate(
        start_value=100,
        end_value=200,
        years=5,
    )

    assert round(result.value, 2) == 14.87
    assert result.flag is None


# ==========================================================
# Positive -> Negative
# ==========================================================

def test_cagr_decline_to_loss():

    result = CAGRCalculator.calculate(
        start_value=100,
        end_value=-50,
        years=5,
    )

    assert result.value is None
    assert result.flag == "DECLINE_TO_LOSS"


# ==========================================================
# Negative -> Positive
# ==========================================================

def test_cagr_turnaround():

    result = CAGRCalculator.calculate(
        start_value=-20,
        end_value=50,
        years=5,
    )

    assert result.value is None
    assert result.flag == "TURNAROUND"


# ==========================================================
# Negative -> Negative
# ==========================================================

def test_cagr_both_negative():

    result = CAGRCalculator.calculate(
        start_value=-20,
        end_value=-50,
        years=5,
    )

    assert result.value is None
    assert result.flag == "BOTH_NEGATIVE"


# ==========================================================
# Zero Base
# ==========================================================

def test_cagr_zero_base():

    result = CAGRCalculator.calculate(
        start_value=0,
        end_value=200,
        years=5,
    )

    assert result.value is None
    assert result.flag == "ZERO_BASE"


# ==========================================================
# Insufficient History
# ==========================================================

def test_cagr_insufficient_history():

    values = [
        100,
        120,
        140,
    ]

    result = CAGRCalculator.calculate_window(
        values,
        years=5,
    )

    assert result.value is None
    assert result.flag == "INSUFFICIENT"


# ==========================================================
# Revenue CAGR
# ==========================================================

def test_revenue_cagr():

    sales = [
        100,
        120,
        140,
        170,
        190,
        200,
    ]

    result = CAGRCalculator.revenue_cagr(sales)

    assert result["revenue_cagr_5yr"].value == 14.87
    assert result["revenue_cagr_5yr"].flag is None

# ==========================================================
# PAT CAGR
# ==========================================================

def test_pat_cagr():

    profits = [
        20,
        24,
        28,
        32,
        36,
        40,
    ]

    result = CAGRCalculator.pat_cagr(profits)

    assert result["pat_cagr_5yr"].value == 14.87
    assert result["pat_cagr_5yr"].flag is None


# ==========================================================
# EPS CAGR
# ==========================================================

def test_eps_cagr():

    eps = [
        10,
        12,
        14,
        17,
        18,
        20,
    ]

    result = CAGRCalculator.eps_cagr(eps)

    assert result["eps_cagr_5yr"].value == 14.87
    assert result["eps_cagr_5yr"].flag is None

# ==========================================================
# Summary API
# ==========================================================

def test_cagr_summary_contains_all_fields():

    sales = [
        100,
        120,
        140,
        170,
        190,
        200,
    ]

    profits = [
        20,
        24,
        28,
        32,
        36,
        40,
    ]

    eps = [
        10,
        12,
        14,
        17,
        18,
        20,
    ]

    result = CAGRCalculator.calculate_all(
        sales=sales,
        profits=profits,
        eps=eps,
    )

    expected = {
        "revenue_cagr_5yr",
        "revenue_cagr_5yr_flag",
        "pat_cagr_5yr",
        "pat_cagr_5yr_flag",
        "eps_cagr_5yr",
        "eps_cagr_5yr_flag",
    }

    assert expected.issubset(result.keys())