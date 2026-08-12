"""
src/api/routers/screener.py

Sprint 6 - Day 40: Financial Screener API Router
"""

from __future__ import annotations

import sqlite3
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
SECTORS_EXCEL = PROJECT_ROOT / "supporting_datasets" / "sectors.xlsx"

router = APIRouter(tags=["Screener"])


def get_db():
    return sqlite3.connect(DB_PATH)


@router.get("/screener")
def screen_companies(
    min_roe: Optional[float] = Query(None, description="Minimum Return on Equity (%)"),
    max_de: Optional[float] = Query(None, description="Maximum Debt to Equity ratio"),
    min_fcf: Optional[float] = Query(None, description="Minimum Free Cash Flow (Cr)"),
    sector: Optional[str] = Query(None, description="Broad Sector filter"),
    min_rev_cagr_5yr: Optional[float] = Query(None, description="Minimum 5-year Revenue CAGR (%)"),
    min_pat_cagr_5yr: Optional[float] = Query(None, description="Minimum 5-year PAT CAGR (%)"),
    max_pe: Optional[float] = Query(None, description="Maximum P/E ratio")
):
    """
    Financial Stock Screener Endpoint.
    Filters Nifty 100 companies based on fundamental financial parameters and ranks them.
    Returns HTTP 400 if invalid parameter values are provided.
    """
    # Parameter sanity checks for HTTP 400
    if min_roe is not None and min_roe < -1000:
        raise HTTPException(status_code=400, detail="Invalid min_roe parameter value.")
    if max_de is not None and max_de < 0:
        raise HTTPException(status_code=400, detail="max_de cannot be negative.")
    if max_pe is not None and max_pe < 0:
        raise HTTPException(status_code=400, detail="max_pe cannot be negative.")

    conn = get_db()

    query = """
        SELECT c.id AS company_id, c.company_name, c.roe_percentage, c.roce_percentage,
               r.return_on_equity_pct, r.debt_to_equity, r.free_cash_flow,
               r.revenue_cagr_5yr, r.pat_cagr_5yr, r.operating_profit_margin_pct,
               r.composite_quality_score
        FROM companies c
        LEFT JOIN (
            SELECT * FROM financial_ratios
            WHERE (company_id, year) IN (
                SELECT company_id, MAX(year) FROM financial_ratios GROUP BY company_id
            )
        ) r ON c.id = r.company_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Merge broad sector
    if SECTORS_EXCEL.exists():
        sec_df = pd.read_excel(SECTORS_EXCEL)
        df = df.merge(sec_df[["company_id", "broad_sector"]], on="company_id", how="left")
    else:
        df["broad_sector"] = "N/A"

    df["broad_sector"] = df["broad_sector"].fillna("N/A")

    # Apply filters
    if min_roe is not None:
        df = df[df["return_on_equity_pct"].fillna(df["roe_percentage"]) >= min_roe]

    if max_de is not None:
        df = df[df["debt_to_equity"].fillna(0) <= max_de]

    if min_fcf is not None:
        df = df[df["free_cash_flow"].fillna(0) >= min_fcf]

    if sector:
        df = df[df["broad_sector"].str.lower() == sector.lower()]

    if min_rev_cagr_5yr is not None:
        df = df[df["revenue_cagr_5yr"].fillna(-999) >= min_rev_cagr_5yr]

    if min_pat_cagr_5yr is not None:
        df = df[df["pat_cagr_5yr"].fillna(-999) >= min_pat_cagr_5yr]

    # Rank filtered companies by ROE / Composite Quality Score
    df["rank"] = df["composite_quality_score"].fillna(0).rank(ascending=False, method="dense").astype(int)
    df = df.sort_values("rank")

    return {
        "count": len(df),
        "results": df.fillna("").to_dict(orient="records")
    }
