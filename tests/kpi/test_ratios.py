"""
Unit tests for Financial Ratio Engine and KPI calculations (Sprint 6 Day 41).
"""
import pytest
from src.analytics.ratios import FinancialRatioCalculator, RatioResult
from src.analytics.cagr import CAGREngine, CAGRResult
from src.analytics.cashflow_kpis import CashFlowKPIEngine


def test_roe_with_positive_equity():
    calc = FinancialRatioCalculator()
    res = calc.return_on_equity(net_profit=100.0, equity_capital=400.0, reserves=100.0)
    assert res.value == 20.0
    assert res.flag is None


def test_roe_with_negative_equity():
    calc = FinancialRatioCalculator()
    res = calc.return_on_equity(net_profit=100.0, equity_capital=-100.0, reserves=50.0)
    assert res.value is None
    assert res.flag == "NEGATIVE_EQUITY"


def test_de_for_debt_free_company():
    calc = FinancialRatioCalculator()
    res = calc.debt_to_equity(borrowings=0.0, equity_capital=500.0, reserves=500.0)
    assert res.value == 0.0
    assert res.label == "Debt Free"


def test_icr_when_interest_zero():
    calc = FinancialRatioCalculator()
    res = calc.interest_coverage(operating_profit=200.0, other_income=10.0, interest=0.0)
    assert res.value is None
    assert res.label == "Debt Free"


def test_de_high_leverage_flag_non_financial():
    calc = FinancialRatioCalculator()
    res = calc.debt_to_equity(borrowings=6000.0, equity_capital=500.0, reserves=500.0)
    assert res.value == 6.0
    assert res.flag == "HIGH_LEVERAGE"


def test_cagr_turnaround_flag():
    engine = CAGREngine()
    res = engine.calculate_cagr(start_val=-100.0, end_val=200.0, periods=5)
    assert res.value is None
    assert res.flag == "TURNAROUND"


def test_cagr_decline_to_loss_flag():
    engine = CAGREngine()
    res = engine.calculate_cagr(start_val=100.0, end_val=-50.0, periods=5)
    assert res.value is None
    assert res.flag == "DECLINE_TO_LOSS"


def test_normal_cagr_calculation():
    engine = CAGREngine()
    res = engine.calculate_cagr(start_val=100.0, end_val=161.051, periods=5)
    assert res.value is not None
    assert abs(res.value - 10.0) < 0.2


def test_opm_cross_check_divergence_flag():
    calc = FinancialRatioCalculator()
    res = calc.operating_profit_margin(sales=1000.0, operating_profit=200.0, source_opm=25.0)
    assert res.value == 20.0
    assert res.flag == "OPM_MISMATCH"


def test_cfo_quality_score_calculation():
    engine = CashFlowKPIEngine()
    res = engine.cfo_quality_score(cfo_history=[120, 130, 140, 150, 160], pat_history=[100, 110, 120, 130, 140])
    assert res.value is not None and res.value > 1.0


def test_net_profit_margin_normal():
    calc = FinancialRatioCalculator()
    res = calc.net_profit_margin(sales=1000.0, net_profit=150.0)
    assert res.value == 15.0


def test_net_profit_margin_zero_sales():
    calc = FinancialRatioCalculator()
    res = calc.net_profit_margin(sales=0.0, net_profit=100.0)
    assert res.value is None


def test_roce_normal():
    calc = FinancialRatioCalculator()
    res = calc.return_on_capital_employed(operating_profit=190.0, interest=10.0, equity_capital=500.0, reserves=300.0, borrowings=200.0)
    assert res.value == 20.0


def test_roa_normal():
    calc = FinancialRatioCalculator()
    res = calc.return_on_assets(net_profit=100.0, total_assets=1000.0)
    assert res.value == 10.0


def test_asset_turnover_normal():
    calc = FinancialRatioCalculator()
    res = calc.asset_turnover(sales=2000.0, total_assets=1000.0)
    assert res.value == 2.0


def test_free_cash_flow_normal():
    engine = CashFlowKPIEngine()
    res = engine.free_cash_flow(operating_activity=500.0, investing_activity=-200.0)
    assert res.value == 300.0


def test_capex_intensity():
    engine = CashFlowKPIEngine()
    res = engine.capex_intensity(investing_activity=-200.0, sales=2000.0)
    assert res.value == 10.0


def test_fcf_conversion_rate():
    engine = CashFlowKPIEngine()
    res = engine.fcf_conversion(free_cash_flow=300.0, operating_profit=500.0)
    assert res.value == 60.0


def test_capital_allocation_pattern():
    engine = CashFlowKPIEngine()
    res = engine.capital_allocation_pattern(operating_activity=500, investing_activity=-200, financing_activity=-100)
    assert res.label is not None
