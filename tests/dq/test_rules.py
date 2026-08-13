"""
Unit tests for Data Quality (DQ) validation rules (Sprint 6 Day 41).
"""
import pandas as pd
import pytest
from src.etl.rules.company_rules import dq01_company_pk, dq08_company_id, dq13_company_urls
from src.etl.rules.pnl_rules import (
    dq02_company_year,
    dq05_opm,
    dq06_sales,
    dq11_tax,
    dq12_dividend,
    dq14_eps,
)
from src.etl.rules.balance_rules import dq04_balance_sheet, dq10_fixed_assets
from src.etl.rules.cashflow_rules import dq09_net_cash
from src.etl.rules.common_rules import dq03_foreign_key, dq07_year, dq16_minimum_years


def test_dq01_company_pk_duplicate():
    df = pd.DataFrame({"id": ["TCS", "TCS", "INFY"]})
    failures = dq01_company_pk(df, "companies")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-01"
    assert failures[0].severity == "CRITICAL"


def test_dq02_company_year_duplicate():
    df = pd.DataFrame({"company_id": ["TCS", "TCS"], "year": ["2023-03", "2023-03"]})
    failures = dq02_company_year(df, "profitandloss")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-02"


def test_dq04_balance_sheet_mismatch():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "total_assets": [1000.0],
        "total_liabilities": [1200.0]
    })
    failures = dq04_balance_sheet(df, "balancesheet")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-04"
    assert failures[0].severity == "WARNING"


def test_dq05_opm_divergence():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "sales": [1000.0],
        "operating_profit": [200.0],
        "opm_percentage": [35.0]
    })
    failures = dq05_opm(df, "profitandloss")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-05"


def test_dq06_zero_sales():
    df = pd.DataFrame({
        "company_id": ["TESTCO"],
        "year": ["2023-03"],
        "sales": [0.0]
    })
    failures = dq06_sales(df, "profitandloss")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-06"


def test_dq07_unparseable_year():
    df = pd.DataFrame({"company_id": ["TCS"], "Year": [None]})
    failures = dq07_year(df, "pnl")
    assert len(failures) > 0


def test_dq08_ticker_lowercase():
    df = pd.DataFrame({"id": ["tcs"]})
    failures = dq08_company_id(df, "companies")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-08"


def test_dq09_net_cash_mismatch():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "cash_from_operating_activity": [500.0],
        "cash_from_investing_activity": [-200.0],
        "cash_from_financing_activity": [-100.0],
        "net_cash_flow": [999.0]
    })
    failures = dq09_net_cash(df, "cashflow")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-09"


def test_dq10_negative_fixed_assets():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "fixed_assets": [-50.0]
    })
    failures = dq10_fixed_assets(df, "balancesheet")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-10"


def test_dq11_tax_out_of_range():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "tax_percentage": [150.0]
    })
    failures = dq11_tax(df, "profitandloss")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-11"


def test_dq12_dividend_payout_exceeded():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "dividend_payout": [150.0]
    })
    failures = dq12_dividend(df, "profitandloss")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-12"


def test_dq14_eps_sign_mismatch():
    df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "net_profit": [100.0],
        "eps": [-10.0]
    })
    failures = dq14_eps(df, "profitandloss")
    assert len(failures) > 0
    assert failures[0].rule_id == "DQ-14"


def test_dq16_insufficient_history():
    df = pd.DataFrame({
        "company_id": ["TCS", "TCS"],
        "Year": ["2023-03", "2024-03"]
    })
    failures = dq16_minimum_years(df, "pnl")
    assert len(failures) > 0
