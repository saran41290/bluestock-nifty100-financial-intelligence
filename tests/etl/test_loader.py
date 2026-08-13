"""
Unit tests for ETL raw dataset loader.
"""
import os
import pandas as pd
import pytest
from src.etl.loader import (
    load_companies,
    load_profit_and_loss,
    load_balance_sheet,
    load_cash_flow,
    load_analysis,
    load_documents,
    load_pros_and_cons,
)


def test_load_companies_returns_dataframe():
    df = load_companies()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 90
    assert "id" in df.columns


def test_load_companies_columns():
    df = load_companies()
    assert "company_name" in df.columns
    assert "book_value" in df.columns


def test_load_pnl_returns_dataframe():
    df = load_profit_and_loss()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 1000
    assert "company_id" in df.columns
    assert "sales" in df.columns


def test_load_pnl_year_normalized():
    df = load_profit_and_loss()
    assert "year" in df.columns
    sample_year = str(df["year"].iloc[0])
    assert len(sample_year) > 0



def test_load_balance_sheet_returns_dataframe():
    df = load_balance_sheet()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 1000
    assert "equity_capital" in df.columns
    assert "total_assets" in df.columns


def test_load_cash_flow_returns_dataframe():
    df = load_cash_flow()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 1000
    assert "operating_activity" in df.columns


def test_load_analysis_returns_dataframe():
    df = load_analysis()
    assert isinstance(df, pd.DataFrame)
    assert "company_id" in df.columns


def test_load_documents_returns_dataframe():
    df = load_documents()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 500
    assert "Annual_Report" in df.columns or "annual_report" in df.columns.str.lower()


def test_load_prosandcons_returns_dataframe():
    df = load_pros_and_cons()
    assert isinstance(df, pd.DataFrame)
    assert "company_id" in df.columns


def test_load_all_datasets_row_count_positive():
    cos = load_companies()
    pnl = load_profit_and_loss()
    bs = load_balance_sheet()
    assert len(cos) > 0 and len(pnl) > 0 and len(bs) > 0
