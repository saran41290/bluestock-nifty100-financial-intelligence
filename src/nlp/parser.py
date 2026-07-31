"""
src/nlp/parser.py

Sprint 5 - Day 29: Analysis Text Parser

Parses textual CAGR and ROE fields from analysis data (Excel/DB) using regex,
exports structured parsed output to CSV, logs parse failures, and cross-validates
parsed CAGR metrics against computed values in financial_ratios.
"""

from __future__ import annotations

import os
import re
import sqlite3
import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = PROJECT_ROOT / "output"
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


class AnalysisParser:
    """
    Parses textual analysis fields into structured numeric data.
    """

    TARGET_FIELDS = [
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe",
    ]

    REGEX_PATTERNS = [
        # Standard: 10 Years: 21% or 5 Years 14% or 3 Years: -2.5%
        re.compile(r"(\d+)\s*Years?:?\s*([-\d.]+)%?", re.IGNORECASE),
        # Special case: Last Year: 12% or 1 Year: 12%
        re.compile(r"(?:Last|1)\s*Years?:?\s*([-\d.]+)%?", re.IGNORECASE),
    ]

    def __init__(self, db_path: Path = DB_PATH, datasets_dir: Path = DATASETS_DIR, output_dir: Path = OUTPUT_DIR):
        self.db_path = db_path
        self.datasets_dir = datasets_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_analysis_data(self) -> pd.DataFrame:
        """
        Loads analysis records from datasets/analysis.xlsx if available,
        otherwise falls back to db/nifty100.db analysis table.
        """
        excel_path = self.datasets_dir / "analysis.xlsx"
        if excel_path.exists():
            logger.info(f"Loading analysis data from Excel: {excel_path}")
            # Try reading with header=1 first (often raw exports have subtitle on line 0)
            df = pd.read_excel(excel_path, header=1)
            if "company_id" not in df.columns:
                df = pd.read_excel(excel_path, header=0)
            return df
        elif self.db_path.exists():
            logger.info(f"Loading analysis data from SQLite DB: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM analysis", conn)
            conn.close()
            return df
        else:
            raise FileNotFoundError("Neither analysis.xlsx nor nifty100.db analysis table found.")

    def parse_field_value(self, raw_val) -> tuple[int | None, float | None, str | None]:
        """
        Parses a single text cell value (e.g. '10 Years: 21%' or 'Last Year: 12%').
        Returns (period_years, value_pct, error_reason).
        """
        if pd.isna(raw_val) or raw_val is None:
            return None, None, "EMPTY_VALUE"

        val_str = str(raw_val).strip()
        if not val_str:
            return None, None, "EMPTY_STRING"

        # Check pattern 1: (\d+)\s*Years?:?\s*([-\d.]+)%
        m1 = self.REGEX_PATTERNS[0].search(val_str)
        if m1:
            period = int(m1.group(1))
            val_pct = float(m1.group(2))
            return period, val_pct, None

        # Check pattern 2: Last Year: 12%
        m2 = self.REGEX_PATTERNS[1].search(val_str)
        if m2:
            period = 1
            val_pct = float(m2.group(1))
            return period, val_pct, None

        return None, None, f"UNMATCHED_PATTERN: '{val_str}'"

    def run_parser(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Parses all analysis records across target fields.
        Returns (df_parsed, df_failures).
        """
        df_raw = self.load_analysis_data()

        parsed_records = []
        failure_records = []

        for idx, row in df_raw.iterrows():
            company_id = row.get("company_id")
            if pd.isna(company_id) or not company_id:
                continue

            company_id = str(company_id).strip()

            for field in self.TARGET_FIELDS:
                if field not in df_raw.columns:
                    continue

                raw_cell = row[field]
                period, value_pct, error = self.parse_field_value(raw_cell)

                if error is None:
                    parsed_records.append({
                        "company_id": company_id,
                        "metric_type": field,
                        "period_years": period,
                        "value_pct": value_pct,
                    })
                else:
                    failure_records.append({
                        "company_id": company_id,
                        "metric_type": field,
                        "raw_text": str(raw_cell),
                        "reason": error,
                    })

        df_parsed = pd.DataFrame(parsed_records)
        df_failures = pd.DataFrame(failure_records)

        # Remove duplicate parsed records if any
        if not df_parsed.empty:
            df_parsed = df_parsed.drop_duplicates(subset=["company_id", "metric_type", "period_years"])

        # Save to CSV
        parsed_path = self.output_dir / "analysis_parsed.csv"
        failures_path = self.output_dir / "parse_failures.csv"

        df_parsed.to_csv(parsed_path, index=False)
        df_failures.to_csv(failures_path, index=False)

        logger.info(f"Saved {len(df_parsed)} parsed records to {parsed_path}")
        logger.info(f"Saved {len(df_failures)} failure records to {failures_path}")

        return df_parsed, df_failures

    def cross_validate_cagr(self, df_parsed: pd.DataFrame) -> pd.DataFrame:
        """
        Cross-validates parsed CAGR values against computed CAGR values in financial_ratios table.
        Flags divergence > 5%.
        """
        if not self.db_path.exists():
            logger.warning("Database path not found for cross-validation.")
            return pd.DataFrame()

        conn = sqlite3.connect(self.db_path)
        try:
            df_ratios = pd.read_sql_query(
                "SELECT company_id, revenue_cagr_3yr, revenue_cagr_5yr, pat_cagr_3yr, pat_cagr_5yr FROM financial_ratios",
                conn
            )
        except Exception as e:
            logger.warning(f"Could not read financial_ratios table: {e}")
            conn.close()
            return pd.DataFrame()
        conn.close()

        if df_ratios.empty:
            return pd.DataFrame()

        # Group by company_id, get latest available ratio record
        df_ratios_latest = df_ratios.groupby("company_id").first().reset_index()

        divergence_records = []

        # Mapping between metric_type & period_years -> DB ratio column
        mapping = {
            ("compounded_sales_growth", 3): "revenue_cagr_3yr",
            ("compounded_sales_growth", 5): "revenue_cagr_5yr",
            ("compounded_profit_growth", 3): "pat_cagr_3yr",
            ("compounded_profit_growth", 5): "pat_cagr_5yr",
        }

        for (metric, period), col_name in mapping.items():
            sub = df_parsed[(df_parsed["metric_type"] == metric) & (df_parsed["period_years"] == period)]
            merged = pd.merge(sub, df_ratios_latest[["company_id", col_name]], on="company_id", how="inner")

            for _, row in merged.iterrows():
                parsed_val = row["value_pct"]
                calc_val = row[col_name]

                if pd.notna(parsed_val) and pd.notna(calc_val):
                    diff = abs(parsed_val - calc_val)
                    if diff > 5.0:
                        divergence_records.append({
                            "company_id": row["company_id"],
                            "metric_type": metric,
                            "period_years": period,
                            "parsed_cagr_pct": parsed_val,
                            "computed_cagr_pct": calc_val,
                            "divergence_pct": round(diff, 2),
                            "flagged_for_review": True
                        })

        df_div = pd.DataFrame(divergence_records)
        if not df_div.empty:
            div_path = self.output_dir / "cagr_divergence_flagged.csv"
            df_div.to_csv(div_path, index=False)
            logger.info(f"Flagged {len(df_div)} CAGR records with divergence > 5% in {div_path}")
        else:
            logger.info("No CAGR divergence > 5% detected during cross-validation.")

        return df_div


if __name__ == "__main__":
    parser = AnalysisParser()
    df_parsed, df_failures = parser.run_parser()
    df_div = parser.cross_validate_cagr(df_parsed)
    print("Parsed count:", len(df_parsed))
    print("Failures count:", len(df_failures))
    print("Divergence count:", len(df_div))
