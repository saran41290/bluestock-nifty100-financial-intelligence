"""
src/api/routers/companies.py

Sprint 6 - Day 39: Company Data & Financial Statements Router
"""

from __future__ import annotations

import sqlite3
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
REPORTS_DIR = PROJECT_ROOT / "reports" / "tearsheets"
SECTORS_EXCEL = PROJECT_ROOT / "supporting_datasets" / "sectors.xlsx"

router = APIRouter(tags=["Companies"])


def get_db():
    return sqlite3.connect(DB_PATH)


@router.get("/companies")
def get_companies(
    sector: Optional[str] = Query(None, description="Filter by broad sector"),
    market_cap_category: Optional[str] = Query(None, description="Filter by market cap category"),
    search: Optional[str] = Query(None, description="Search by partial name or ticker symbol")
):
    """Returns list of companies with roe_pct, roce_pct, and sector metadata."""
    conn = get_db()
    query = """
        SELECT c.id, c.company_name, c.roe_percentage AS roe_pct, c.roce_percentage AS roce_pct
        FROM companies c
    """
    df_comp = pd.read_sql_query(query, conn)
    conn.close()

    # Sector mapping
    sectors_df = pd.DataFrame()
    if SECTORS_EXCEL.exists():
        sectors_df = pd.read_excel(SECTORS_EXCEL)

    if not sectors_df.empty:
        df_comp = df_comp.merge(
            sectors_df[["company_id", "broad_sector", "sub_sector", "market_cap_category"]],
            left_on="id", right_on="company_id", how="left"
        ).drop(columns=["company_id"], errors="ignore")
    else:
        df_comp["broad_sector"] = "N/A"
        df_comp["sub_sector"] = "N/A"
        df_comp["market_cap_category"] = "Large Cap"

    # Filters
    if sector:
        df_comp = df_comp[df_comp["broad_sector"].str.lower() == sector.lower()]

    if market_cap_category:
        df_comp = df_comp[df_comp["market_cap_category"].str.lower() == market_cap_category.lower()]

    if search:
        s = search.lower()
        df_comp = df_comp[
            df_comp["id"].str.lower().str.contains(s) |
            df_comp["company_name"].str.lower().str.contains(s)
        ]

    df_comp = df_comp.fillna("")
    return df_comp.to_dict(orient="records")


@router.get("/companies/{ticker}")
def get_company_profile(ticker: str):
    """Returns full company profile including company details, sector data, and latest year KPIs."""
    ticker_upper = ticker.upper()
    conn = get_db()

    comp = pd.read_sql_query("SELECT * FROM companies WHERE UPPER(id) = ?", conn, params=(ticker_upper,))
    if comp.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company with ticker '{ticker}' not found.")

    comp_dict = comp.iloc[0].to_dict()

    # Latest ratios
    latest_ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios WHERE UPPER(company_id) = ? ORDER BY year DESC LIMIT 1",
        conn, params=(ticker_upper,)
    )

    conn.close()

    # Sector data
    sector_info = {"broad_sector": "N/A", "sub_sector": "N/A", "market_cap_category": "Large Cap"}
    if SECTORS_EXCEL.exists():
        sec_df = pd.read_excel(SECTORS_EXCEL)
        matched = sec_df[sec_df["company_id"].str.upper() == ticker_upper]
        if not matched.empty:
            sector_info = {
                "broad_sector": matched.iloc[0].get("broad_sector", "N/A"),
                "sub_sector": matched.iloc[0].get("sub_sector", "N/A"),
                "market_cap_category": matched.iloc[0].get("market_cap_category", "Large Cap"),
            }

    kpis = latest_ratios.iloc[0].to_dict() if not latest_ratios.empty else {}

    return {
        "company": comp_dict,
        "sector": sector_info,
        "latest_kpis": kpis
    }


@router.get("/companies/{ticker}/pl")
def get_profit_and_loss(
    ticker: str,
    from_year: Optional[str] = Query(None, description="Start year filter"),
    to_year: Optional[str] = Query(None, description="End year filter")
):
    """Returns Profit & Loss statement history array for the given company."""
    ticker_upper = ticker.upper()
    conn = get_db()

    check = pd.read_sql_query("SELECT id FROM companies WHERE UPPER(id) = ?", conn, params=(ticker_upper,))
    if check.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found.")

    query = "SELECT * FROM profitandloss WHERE UPPER(company_id) = ?"
    params = [ticker_upper]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year[:4])
    if to_year:
        query += " AND year <= ?"
        params.append(to_year[:4])

    query += " ORDER BY year"
    pnl_df = pd.read_sql_query(query, conn, params=tuple(params))
    conn.close()

    return pnl_df.fillna("").to_dict(orient="records")


@router.get("/companies/{ticker}/bs")
def get_balance_sheet(
    ticker: str,
    from_year: Optional[str] = Query(None, description="Start year filter"),
    to_year: Optional[str] = Query(None, description="End year filter")
):
    """Returns Balance Sheet statement history array for the given company."""
    ticker_upper = ticker.upper()
    conn = get_db()

    check = pd.read_sql_query("SELECT id FROM companies WHERE UPPER(id) = ?", conn, params=(ticker_upper,))
    if check.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found.")

    query = "SELECT * FROM balancesheet WHERE UPPER(company_id) = ?"
    params = [ticker_upper]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year[:4])
    if to_year:
        query += " AND year <= ?"
        params.append(to_year[:4])

    query += " ORDER BY year"
    bs_df = pd.read_sql_query(query, conn, params=tuple(params))
    conn.close()

    return bs_df.fillna("").to_dict(orient="records")


@router.get("/companies/{ticker}/cashflow")
def get_cashflow(
    ticker: str,
    from_year: Optional[str] = Query(None, description="Start year filter"),
    to_year: Optional[str] = Query(None, description="End year filter")
):
    """Returns Cash Flow statement history array for the given company."""
    ticker_upper = ticker.upper()
    conn = get_db()

    check = pd.read_sql_query("SELECT id FROM companies WHERE UPPER(id) = ?", conn, params=(ticker_upper,))
    if check.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found.")

    query = "SELECT * FROM cashflow WHERE UPPER(company_id) = ?"
    params = [ticker_upper]

    if from_year:
        query += " AND year >= ?"
        params.append(from_year[:4])
    if to_year:
        query += " AND year <= ?"
        params.append(to_year[:4])

    query += " ORDER BY year"
    cf_df = pd.read_sql_query(query, conn, params=tuple(params))
    conn.close()

    return cf_df.fillna("").to_dict(orient="records")


@router.get("/companies/{ticker}/ratios")
def get_financial_ratios(
    ticker: str,
    year: Optional[str] = Query(None, description="Single year filter")
):
    """Returns all computed financial KPIs per year for the target company."""
    ticker_upper = ticker.upper()
    conn = get_db()

    check = pd.read_sql_query("SELECT id FROM companies WHERE UPPER(id) = ?", conn, params=(ticker_upper,))
    if check.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found.")

    query = "SELECT * FROM financial_ratios WHERE UPPER(company_id) = ?"
    params = [ticker_upper]

    if year:
        query += " AND year = ?"
        params.append(year[:4])

    query += " ORDER BY year"
    ratios_df = pd.read_sql_query(query, conn, params=tuple(params))
    conn.close()

    return ratios_df.fillna("").to_dict(orient="records")


@router.get("/companies/{ticker}/tearsheet")
def get_tearsheet_pdf(ticker: str):
    """Downloads the pre-generated executive 2-page PDF tearsheet for the target company."""
    ticker_upper = ticker.upper()
    pdf_path = REPORTS_DIR / f"{ticker_upper}_tearsheet.pdf"

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Tearsheet PDF for company '{ticker}' not found.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"{ticker_upper}_tearsheet.pdf"
    )
