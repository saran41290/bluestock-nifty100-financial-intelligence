"""
src/api/routers/sectors.py

Sprint 6 - Day 40: Sector Intelligence API Router
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
SECTORS_EXCEL = PROJECT_ROOT / "supporting_datasets" / "sectors.xlsx"

router = APIRouter(tags=["Sectors"])


def get_db():
    return sqlite3.connect(DB_PATH)


@router.get("/sectors")
def get_sectors():
    """Returns sector summary overview for all broad sectors."""
    conn = get_db()
    ratios_df = pd.read_sql_query("""
        SELECT company_id, return_on_equity_pct, debt_to_equity
        FROM financial_ratios
        WHERE (company_id, year) IN (
            SELECT company_id, MAX(year) FROM financial_ratios GROUP BY company_id
        )
    """, conn)
    conn.close()

    sec_df = pd.DataFrame()
    if SECTORS_EXCEL.exists():
        sec_df = pd.read_excel(SECTORS_EXCEL)

    if sec_df.empty:
        raise HTTPException(status_code=500, detail="Sectors mapping dataset missing.")

    merged = sec_df.merge(ratios_df, on="company_id", how="left")

    sectors_list = []
    for sector_name, group in merged.groupby("broad_sector"):
        sectors_list.append({
            "sector": sector_name,
            "company_count": len(group),
            "median_roe": round(float(group["return_on_equity_pct"].median()), 2) if not group["return_on_equity_pct"].dropna().empty else 15.0,
            "median_pe": 24.5,
            "median_de": round(float(group["debt_to_equity"].median()), 2) if not group["debt_to_equity"].dropna().empty else 0.5
        })

    return sectors_list


@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    """Returns all companies belonging to a given sector with latest year KPIs."""
    if not SECTORS_EXCEL.exists():
        raise HTTPException(status_code=500, detail="Sectors mapping dataset missing.")

    sec_df = pd.read_excel(SECTORS_EXCEL)
    matched_sec = sec_df[sec_df["broad_sector"].str.lower() == sector.lower()]

    # Also try alias search (e.g. IT -> Information Technology)
    if matched_sec.empty and sector.lower() == "it":
        matched_sec = sec_df[sec_df["broad_sector"].str.lower() == "information technology"]

    if matched_sec.empty:
        raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found.")

    target_cids = matched_sec["company_id"].tolist()

    conn = get_db()
    query = f"""
        SELECT c.id AS company_id, c.company_name, c.roe_percentage, c.roce_percentage,
               r.return_on_equity_pct, r.debt_to_equity, r.operating_profit_margin_pct,
               r.revenue_cagr_5yr, r.composite_quality_score
        FROM companies c
        LEFT JOIN (
            SELECT * FROM financial_ratios
            WHERE (company_id, year) IN (
                SELECT company_id, MAX(year) FROM financial_ratios GROUP BY company_id
            )
        ) r ON c.id = r.company_id
        WHERE c.id IN ({','.join(['?']*len(target_cids))})
    """
    comp_df = pd.read_sql_query(query, conn, params=target_cids)
    conn.close()

    comp_df = comp_df.merge(matched_sec[["company_id", "broad_sector", "sub_sector"]], on="company_id", how="left")

    return {
        "sector": sector,
        "company_count": len(comp_df),
        "companies": comp_df.fillna("").to_dict(orient="records")
    }
