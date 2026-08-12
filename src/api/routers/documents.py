"""
src/api/routers/documents.py

Sprint 6 - Day 40: Annual Report Documents & Link Validation API Router
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

router = APIRouter(tags=["Documents"])


def get_db():
    return sqlite3.connect(DB_PATH)


@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):
    """Returns annual report links with is_url_valid boolean flag for the given company."""
    ticker_upper = ticker.upper()
    conn = get_db()

    check = pd.read_sql_query("SELECT id FROM companies WHERE UPPER(id) = ?", conn, params=(ticker_upper,))
    if check.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found.")

    docs_df = pd.read_sql_query(
        "SELECT company_id, Year AS year, Annual_Report AS annual_report_url FROM documents WHERE UPPER(company_id) = ? ORDER BY year DESC",
        conn, params=(ticker_upper,)
    )
    conn.close()

    results = []
    for idx, row in docs_df.iterrows():
        url = str(row["annual_report_url"]).strip() if pd.notna(row["annual_report_url"]) else ""
        is_valid = bool(url and (url.startswith("http://") or url.startswith("https://") or "bseindia" in url or "nseindia" in url))
        results.append({
            "company_id": row["company_id"],
            "year": row["year"],
            "annual_report_url": url,
            "is_url_valid": is_valid
        })

    return {
        "company_id": ticker_upper,
        "document_count": len(results),
        "documents": results
    }
