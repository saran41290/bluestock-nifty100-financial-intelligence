"""
test_sprint4.py

Integration QA & Verification Test Suite for Sprint 4 (Day 27)
"""

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_sectors,
    get_peers,
    get_valuation,
    get_documents,
    get_prosandcons
)
from src.analytics.valuation import ValuationEngine


def test_valuation_outputs():
    summary_path = PROJECT_ROOT / "output" / "valuation_summary.xlsx"
    flags_path = PROJECT_ROOT / "output" / "valuation_flags.csv"

    # Run valuation engine
    engine = ValuationEngine(PROJECT_ROOT)
    summary_df, flags_df = engine.run()

    assert summary_path.exists(), "valuation_summary.xlsx does not exist"
    assert flags_path.exists(), "valuation_flags.csv does not exist"

    # Check 92 companies row count
    df_summary = pd.read_excel(summary_path)
    assert len(df_summary) == 92, f"Expected 92 rows in valuation_summary.xlsx, got {len(df_summary)}"

    required_cols = [
        'company_id', 'company_name', 'sector', 'P/E', 'P/B',
        'EV/EBITDA', 'FCF_yield_pct', '5yr_median_PE',
        'PE_vs_sector_median_pct', 'flag'
    ]
    for col in required_cols:
        assert col in df_summary.columns, f"Missing column {col} in valuation_summary.xlsx"

    df_flags = pd.read_csv(flags_path)
    assert not df_flags.empty, "valuation_flags.csv is empty"
    assert set(df_flags['flag'].unique()).issubset({'Caution', 'Discount'}), "Invalid flag values in flags CSV"


def test_db_utilities_for_10_tickers():
    test_tickers = [
        'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'ITC',
        'RELIANCE', 'NTPC', 'SUNPHARMA', 'CIPLA', 'TITAN'
    ]
    
    companies = get_companies()
    assert len(companies) == 92, "get_companies() should return 92 rows"

    for ticker in test_tickers:
        ratios = get_ratios(ticker)
        pl = get_pl(ticker)
        bs = get_bs(ticker)
        cf = get_cf(ticker)
        val = get_valuation(ticker)
        docs = get_documents(ticker)
        pros = get_prosandcons(ticker)

        assert isinstance(ratios, pd.DataFrame), f"Failed get_ratios for {ticker}"
        assert isinstance(pl, pd.DataFrame), f"Failed get_pl for {ticker}"
        assert isinstance(bs, pd.DataFrame), f"Failed get_bs for {ticker}"
        assert isinstance(cf, pd.DataFrame), f"Failed get_cf for {ticker}"
        assert isinstance(val, pd.DataFrame), f"Failed get_valuation for {ticker}"


def test_page_files_syntax():
    pages_dir = PROJECT_ROOT / "pages"
    page_files = sorted(list(pages_dir.glob("*.py")))
    assert len(page_files) == 8, f"Expected 8 page files in pages/, found {len(page_files)}"

    for pf in page_files:
        with open(pf, "r", encoding="utf-8") as f:
            code = f.read()
            compile(code, pf.name, "exec")


if __name__ == "__main__":
    test_valuation_outputs()
    test_db_utilities_for_10_tickers()
    test_page_files_syntax()
    print("ALL SPRINT 4 INTEGRATION TESTS PASSED SUCCESSFULLY!")
