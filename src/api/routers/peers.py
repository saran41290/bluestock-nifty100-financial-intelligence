"""
src/api/routers/peers.py

Sprint 6 - Day 40: Peer Analysis & Radar Comparison API Router
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from fastapi import APIRouter, HTTPException
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

router = APIRouter(tags=["Peers"])


def get_db():
    return sqlite3.connect(DB_PATH)


@router.get("/peers/{group_name}")
def get_peer_group_percentiles(group_name: str):
    """Returns all companies in a peer group with percentile ranks for 10 core financial metrics."""
    conn = get_db()
    query = "SELECT * FROM peer_percentiles"
    df_all = pd.read_sql_query(query, conn)
    conn.close()

    if df_all.empty:
        raise HTTPException(status_code=404, detail="No peer percentiles found.")

    target = group_name.lower().strip()
    df_matched = df_all[df_all["peer_group_name"].fillna("").str.lower().str.strip() == target]

    if df_matched.empty:
        # Flexible partial / plural matching (e.g. Automobile -> Automobiles)
        df_matched = df_all[
            df_all["peer_group_name"].fillna("").str.lower().str.contains(target) |
            df_all["peer_group_name"].fillna("").str.lower().str.startswith(target)
        ]

    if df_matched.empty:
        raise HTTPException(status_code=404, detail=f"Peer group '{group_name}' not found.")

    return {
        "peer_group_name": group_name,
        "company_count": len(df_matched),
        "companies": df_matched.fillna("").to_dict(orient="records")
    }


@router.get("/companies/{ticker}/peers/compare")
def compare_company_radar(ticker: str):
    """Returns 8-axis radar comparison data for target company, peer average, and benchmark company."""
    ticker_upper = ticker.upper()
    conn = get_db()

    peer_entry = pd.read_sql_query(
        "SELECT peer_group_name FROM peer_percentiles WHERE UPPER(company_id) = ? LIMIT 1",
        conn, params=(ticker_upper,)
    )

    if peer_entry.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Peer data for company '{ticker}' not found.")

    group_name = peer_entry.iloc[0]["peer_group_name"]
    group_df = pd.read_sql_query("SELECT * FROM peer_percentiles WHERE peer_group_name = ?", conn, params=(group_name,))
    conn.close()

    target_df = group_df[group_df["company_id"].str.upper() == ticker_upper]
    benchmark_df = group_df[group_df["is_benchmark"] == 1]
    if benchmark_df.empty:
        benchmark_df = group_df.head(1)

    radar_axes = [
        "return_on_equity_pct_percentile",
        "return_on_capital_employed_pct_percentile",
        "net_profit_margin_pct_percentile",
        "debt_to_equity_percentile",
        "interest_coverage_percentile",
        "asset_turnover_percentile",
        "free_cash_flow_percentile",
        "revenue_cagr_5yr_percentile"
    ]

    target_scores = target_df.iloc[0][radar_axes].to_dict() if not target_df.empty else {}
    peer_avg_scores = group_df[radar_axes].mean().round(2).to_dict()
    benchmark_scores = benchmark_df.iloc[0][radar_axes].to_dict() if not benchmark_df.empty else {}

    return {
        "ticker": ticker_upper,
        "peer_group_name": group_name,
        "target_company": target_scores,
        "peer_group_average": peer_avg_scores,
        "benchmark_company": {
            "company_id": benchmark_df.iloc[0]["company_id"] if not benchmark_df.empty else "",
            "scores": benchmark_scores
        }
    }
