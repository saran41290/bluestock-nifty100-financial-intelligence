"""
Sprint 2

Cashflow KPI Unit Tests

Tests:

1. Free Cash Flow
2. CFO Quality Score
3. CapEx Intensity
4. FCF Conversion
5. Capital Allocation Pattern
6. Summary API
7. CSV Helper
"""

from src.analytics.cashflow_kpis import CashflowKPICalculator


# ==========================================================
# FREE CASH FLOW
# ==========================================================

def test_free_cash_flow_positive():

    result = CashflowKPICalculator.free_cash_flow(
        operating_activity=500,
        investing_activity=-200,
    )

    assert result.value == 300
    assert result.label == "POSITIVE_FCF"
    assert result.flag is None


def test_free_cash_flow_negative():

    result = CashflowKPICalculator.free_cash_flow(
        operating_activity=100,
        investing_activity=-300,
    )

    assert result.value == -200
    assert result.label == "NEGATIVE_FCF"


# ==========================================================
# CFO QUALITY SCORE
# ==========================================================

def test_cfo_quality_high():

    result = CashflowKPICalculator.cfo_quality_score(
        cfo_history=[120, 130, 140],
        pat_history=[100, 100, 100],
    )

    assert result.value == 1.3
    assert result.label == "High Quality"


def test_cfo_quality_moderate():

    result = CashflowKPICalculator.cfo_quality_score(
        cfo_history=[60, 70, 80],
        pat_history=[100, 100, 100],
    )

    assert result.value == 0.7
    assert result.label == "Moderate"


def test_cfo_quality_accrual_risk():

    result = CashflowKPICalculator.cfo_quality_score(
        cfo_history=[20, 30, 40],
        pat_history=[100, 100, 100],
    )

    assert result.value == 0.3
    assert result.label == "Accrual Risk"


def test_cfo_quality_pat_zero():

    result = CashflowKPICalculator.cfo_quality_score(
        cfo_history=[100, 120],
        pat_history=[0, 0],
    )

    assert result.value is None
    assert result.flag == "PAT_ZERO"


def test_cfo_quality_insufficient():

    result = CashflowKPICalculator.cfo_quality_score(
        cfo_history=[],
        pat_history=[],
    )

    assert result.value is None
    assert result.flag == "INSUFFICIENT_HISTORY"


# ==========================================================
# CAPEX INTENSITY
# ==========================================================

def test_capex_asset_light():

    result = CashflowKPICalculator.capex_intensity(
        investing_activity=-20,
        sales=1000,
    )

    assert result.value == 2.0
    assert result.label == "Asset Light"


def test_capex_moderate():

    result = CashflowKPICalculator.capex_intensity(
        investing_activity=-50,
        sales=1000,
    )

    assert result.value == 5.0
    assert result.label == "Moderate"


def test_capex_capital_intensive():

    result = CashflowKPICalculator.capex_intensity(
        investing_activity=-120,
        sales=1000,
    )

    assert result.value == 12.0
    assert result.label == "Capital Intensive"


def test_capex_zero_sales():

    result = CashflowKPICalculator.capex_intensity(
        investing_activity=-120,
        sales=0,
    )

    assert result.value is None
    assert result.flag == "ZERO_SALES"


# ==========================================================
# FCF CONVERSION
# ==========================================================

def test_fcf_conversion_good():

    result = CashflowKPICalculator.fcf_conversion(
        free_cash_flow=300,
        operating_profit=400,
    )

    assert result.value == 75.0
    assert result.label == "Good"


def test_fcf_conversion_zero_profit():

    result = CashflowKPICalculator.fcf_conversion(
        free_cash_flow=100,
        operating_profit=0,
    )

    assert result.value is None
    assert result.flag == "ZERO_OPERATING_PROFIT"


# ==========================================================
# CAPITAL ALLOCATION
# ==========================================================

def test_capital_allocation_reinvestor():

    result = CashflowKPICalculator.capital_allocation_pattern(
        operating_activity=500,
        investing_activity=-300,
        financing_activity=-100,
    )

    assert result.label == "Reinvestor"


def test_capital_allocation_shareholder_returns():

    result = CashflowKPICalculator.capital_allocation_pattern(
        operating_activity=500,
        investing_activity=-300,
        financing_activity=-100,
        cfo_pat_ratio=1.2,
    )

    assert result.label == "Shareholder Returns"


def test_capital_allocation_growth_debt():

    result = CashflowKPICalculator.capital_allocation_pattern(
        operating_activity=-100,
        investing_activity=-300,
        financing_activity=400,
    )

    assert result.label == "Growth Funded by Debt"


def test_capital_allocation_cash_accumulator():

    result = CashflowKPICalculator.capital_allocation_pattern(
        operating_activity=100,
        investing_activity=50,
        financing_activity=20,
    )

    assert result.label == "Cash Accumulator"


# ==========================================================
# SUMMARY API
# ==========================================================

def test_calculate_all():

    result = CashflowKPICalculator.calculate_all(
        operating_activity=500,
        investing_activity=-200,
        financing_activity=-100,
        operating_profit=400,
        sales=1000,
        cfo_history=[500, 520, 540],
        pat_history=[400, 420, 440],
    )

    expected = {
        "free_cash_flow",
        "free_cash_flow_label",
        "cfo_quality_score",
        "cfo_quality_label",
        "capex_intensity",
        "capex_label",
        "fcf_conversion",
        "fcf_conversion_label",
        "capital_allocation",
    }

    assert expected.issubset(result.keys())


# ==========================================================
# CSV HELPER
# ==========================================================

def test_capital_allocation_record():

    row = CashflowKPICalculator.capital_allocation_record(
        company_id=101,
        year="2024",
        operating_activity=500,
        investing_activity=-200,
        financing_activity=-100,
        pattern_label="Reinvestor",
    )

    assert row["company_id"] == 101
    assert row["year"] == "2024"
    assert row["cfo_sign"] == "+"
    assert row["cfi_sign"] == "-"
    assert row["cff_sign"] == "-"
    assert row["pattern_label"] == "Reinvestor"