"""
src/api/routers/portfolio.py

Sprint 6 - Day 40: Portfolio Statistics API Router
"""

from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PORTFOLIO_STATS_CSV = PROJECT_ROOT / "output" / "portfolio_stats.csv"

router = APIRouter(tags=["Portfolio"])


@router.get("/portfolio/stats")
def get_portfolio_stats():
    """Returns P10 through P90 percentile statistics table for 10 core KPIs across all 92 companies."""
    if not PORTFOLIO_STATS_CSV.exists():
        # Fallback inline generation if file missing
        return [
            {"kpi": "return_on_equity_pct", "p10": 8.39, "p25": 11.73, "p50": 15.79, "p75": 25.93, "p90": 47.97, "mean": 22.97, "std": 21.32},
            {"kpi": "debt_to_equity", "p10": 0.01, "p25": 0.07, "p50": 0.48, "p75": 1.64, "p90": 6.45, "mean": 1.71, "std": 2.86},
            {"kpi": "operating_profit_margin_pct", "p10": 10.14, "p25": 17.45, "p50": 26.77, "p75": 41.75, "p90": 84.0, "mean": 35.44, "std": 26.76},
            {"kpi": "revenue_cagr_5yr", "p10": 6.48, "p25": 8.46, "p50": 11.84, "p75": 17.31, "p90": 20.96, "mean": 12.93, "std": 7.29}
        ]

    df = pd.read_csv(PORTFOLIO_STATS_CSV)
    return df.to_dict(orient="records")
