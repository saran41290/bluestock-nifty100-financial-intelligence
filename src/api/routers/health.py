"""
src/api/routers/health.py

Sprint 6 - Day 38: API Health & System Diagnostics Router
"""

from __future__ import annotations

import time
import sqlite3
from pathlib import Path
from fastapi import APIRouter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
START_TIME = time.time()

router = APIRouter(tags=["Health"])

ALL_TABLES = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "financial_ratios",
    "peer_percentiles",
    "cluster_labels"
]


@router.get("/health")
def get_health():
    """Returns API health status, database table row counts, uptime, and version."""
    uptime = round(time.time() - START_TIME, 2)
    db_row_counts = {}

    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for tbl in ALL_TABLES:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
                db_row_counts[tbl] = cursor.fetchone()[0]
            except Exception:
                db_row_counts[tbl] = 0
        conn.close()
    else:
        for tbl in ALL_TABLES:
            db_row_counts[tbl] = 0

    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime_seconds": uptime,
        "db_row_counts": db_row_counts
    }
