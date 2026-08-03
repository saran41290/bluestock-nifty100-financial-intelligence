"""
src/analytics/cashflow_kpis.py

Financial Ratio Engine - Cash Flow Intelligence & Capital Allocation Module

Sprint 2 & Sprint 5 (Day 31 & Day 32)

Implements:
• Free Cash Flow (FCF)
• CFO Quality Score
• CapEx Intensity
• FCF Conversion
• Capital Allocation Classification (8 patterns)
• Distress Signal Detection (CFO < 0 AND CFF > 0 in latest year)
• Deleveraging Flag (CFF < 0 AND borrowings declining YoY)
• Export of output/cashflow_intelligence.xlsx, output/distress_alerts.csv, output/pattern_changes.csv
"""

from __future__ import annotations

import os
import sqlite3
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
import pandas as pd
import numpy as np

try:
    from .helpers import percentage, round2
except ImportError:
    from src.analytics.helpers import percentage, round2

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"


# ==========================================================
# Result Object
# ==========================================================

@dataclass(slots=True)
class CashflowResult:
    """
    Generic result returned by every KPI.
    """
    value: Optional[float]
    flag: Optional[str] = None
    label: Optional[str] = None


# ==========================================================
# Cashflow KPI Calculator
# ==========================================================

class CashflowKPICalculator:

    @staticmethod
    def _round(value):
        if value is None:
            return None
        return round2(value)

    @staticmethod
    def safe_float(value):
        try:
            if value is None or pd.isna(value):
                return 0.0
            return float(value)
        except Exception:
            return 0.0

    # ======================================================
    # FREE CASH FLOW
    # ======================================================

    @staticmethod
    def free_cash_flow(operating_activity, investing_activity) -> CashflowResult:
        """
        Free Cash Flow = CFO + CFI (CFI is usually negative).
        """
        cfo = CashflowKPICalculator.safe_float(operating_activity)
        cfi = CashflowKPICalculator.safe_float(investing_activity)
        fcf = cfo + cfi
        label = "POSITIVE_FCF" if fcf > 0 else ("NEGATIVE_FCF" if fcf < 0 else "ZERO_FCF")
        return CashflowResult(value=CashflowKPICalculator._round(fcf), label=label)

    # ======================================================
    # CFO QUALITY SCORE
    # ======================================================

    @staticmethod
    def cfo_quality_score(cfo_history: List[float], pat_history: List[float]) -> CashflowResult:
        """
        CFO / PAT averaged across 5-year history.
        >1.0  -> High Quality
        0.5-1.0 -> Moderate
        <0.5  -> Accrual Risk
        """
        if not cfo_history or not pat_history:
            return CashflowResult(value=None, flag="INSUFFICIENT_HISTORY", label="Accrual Risk")

        ratios = []
        for cfo, pat in zip(cfo_history, pat_history):
            cfo_val = CashflowKPICalculator.safe_float(cfo)
            pat_val = CashflowKPICalculator.safe_float(pat)
            if pat_val > 0:
                ratios.append(cfo_val / pat_val)

        if not ratios:
            return CashflowResult(value=0.0, flag="NO_POSITIVE_PAT", label="Accrual Risk")

        average = sum(ratios) / len(ratios)

        label = "Accrual Risk"
        if average > 1.0:
            label = "High Quality"
        elif average >= 0.5:
            label = "Moderate"

        return CashflowResult(value=CashflowKPICalculator._round(average), label=label)

    # ======================================================
    # CAPEX INTENSITY
    # ======================================================

    @staticmethod
    def capex_intensity(investing_activity, sales) -> CashflowResult:
        """
        CapEx Intensity = abs(CFI) / Sales × 100
        <3%   -> Asset Light
        3-8%  -> Moderate
        >8%   -> Capital Intensive
        """
        cfi = abs(CashflowKPICalculator.safe_float(investing_activity))
        sales_val = CashflowKPICalculator.safe_float(sales)

        if sales_val <= 0:
            return CashflowResult(value=None, flag="ZERO_SALES", label="Moderate")

        val = (cfi / sales_val) * 100.0
        val = CashflowKPICalculator._round(val)

        label = "Capital Intensive"
        if val < 3.0:
            label = "Asset Light"
        elif val <= 8.0:
            label = "Moderate"

        return CashflowResult(value=val, label=label)

    # ======================================================
    # FCF CONVERSION
    # ======================================================

    @staticmethod
    def fcf_conversion(free_cash_flow, operating_profit) -> CashflowResult:
        """
        FCF Conversion = FCF / Operating Profit × 100
        """
        fcf_val = CashflowKPICalculator.safe_float(free_cash_flow)
        op_val = CashflowKPICalculator.safe_float(operating_profit)

        if op_val == 0:
            return CashflowResult(value=None, flag="ZERO_OPERATING_PROFIT", label="Weak")

        val = percentage(fcf_val, op_val)
        val = CashflowKPICalculator._round(val)

        if val is None:
            return CashflowResult(value=None, flag="ZERO_OPERATING_PROFIT", label="Weak")

        label = "Weak"
        if val >= 100:
            label = "Excellent"
        elif val >= 75:
            label = "Good"
        elif val >= 50:
            label = "Average"

        return CashflowResult(value=val, label=label)

    # ======================================================
    # CAPITAL ALLOCATION PATTERN
    # ======================================================

    @staticmethod
    def _cashflow_sign(value):
        val = CashflowKPICalculator.safe_float(value)
        if val > 0:
            return "+"
        if val < 0:
            return "-"
        return "0"

    @staticmethod
    def capital_allocation_pattern(
        operating_activity, investing_activity, financing_activity, cfo_pat_ratio=None
    ) -> CashflowResult:
        """
        Capital Allocation Classification
        (+,-,-) = Reinvestor (or Shareholder Returns if CFO/PAT > 1)
        (+,+,-) = Liquidating Assets
        (-,+,+) = Distress Signal
        (-,-,+) = Growth Funded by Debt
        (+,+,+) = Cash Accumulator
        (-,-,-) = Pre-Revenue
        (+,-,+) = Mixed
        """
        cfo = CashflowKPICalculator._cashflow_sign(operating_activity)
        cfi = CashflowKPICalculator._cashflow_sign(investing_activity)
        cff = CashflowKPICalculator._cashflow_sign(financing_activity)

        pattern = (cfo, cfi, cff)
        label = "Mixed"

        if pattern == ("+", "-", "-"):
            label = "Reinvestor"
            if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
                label = "Shareholder Returns"
        elif pattern == ("+", "+", "-"):
            label = "Liquidating Assets"
        elif pattern == ("-", "+", "+"):
            label = "Distress Signal"
        elif pattern == ("-", "-", "+"):
            label = "Growth Funded by Debt"
        elif pattern == ("+", "+", "+"):
            label = "Cash Accumulator"
        elif pattern == ("-", "-", "-"):
            label = "Pre-Revenue"
        elif pattern == ("+", "-", "+"):
            label = "Mixed"

        return CashflowResult(value=None, label=label)


# ==========================================================
# BATCH GENERATOR FOR SPRINT 5
# ==========================================================

class CashFlowIntelligenceManager:
    """
    Manages generation of output/cashflow_intelligence.xlsx, distress_alerts.csv,
    and pattern_changes.csv.
    """

    def __init__(self, db_path: Path = DB_PATH, output_dir: Path = OUTPUT_DIR):
        self.db_path = db_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self):
        conn = sqlite3.connect(self.db_path)
        companies = pd.read_sql_query("SELECT id FROM companies", conn)
        cf = pd.read_sql_query("SELECT * FROM cashflow ORDER BY company_id, year", conn)
        pnl = pd.read_sql_query("SELECT * FROM profitandloss ORDER BY company_id, year", conn)
        bs = pd.read_sql_query("SELECT * FROM balancesheet ORDER BY company_id, year", conn)

        try:
            peer = pd.read_sql_query("SELECT DISTINCT company_id, peer_group_name FROM peer_percentiles", conn)
            sector_map = dict(zip(peer["company_id"], peer["peer_group_name"]))
        except Exception:
            sector_map = {}

        # Fallback to sectors.xlsx if needed
        sec_excel = PROJECT_ROOT / "supporting_datasets" / "sectors.xlsx"
        if sec_excel.exists():
            df_sec = pd.read_excel(sec_excel)
            for _, row in df_sec.iterrows():
                cid = row["company_id"]
                if cid not in sector_map:
                    sector_map[cid] = row.get("broad_sector", "Other")

        conn.close()
        return companies, cf, pnl, bs, sector_map

    def generate(self):
        companies, cf, pnl, bs, sector_map = self.load_data()

        intel_records = []
        distress_alerts = []
        pattern_history = []

        for cid in companies["id"].unique():
            c_cf = cf[cf["company_id"] == cid].sort_values("year")
            c_pnl = pnl[pnl["company_id"] == cid].sort_values("year")
            c_bs = bs[bs["company_id"] == cid].sort_values("year")

            sector = sector_map.get(cid, "Other")

            if c_cf.empty or c_pnl.empty:
                intel_records.append({
                    "company_id": cid,
                    "sector": sector,
                    "cfo_quality_score": None,
                    "cfo_quality_label": "Accrual Risk",
                    "capex_intensity_pct": None,
                    "capex_label": "Moderate",
                    "fcf_cagr_5yr": None,
                    "fcf_conversion_pct": None,
                    "distress_flag": False,
                    "deleveraging_flag": False,
                    "capital_allocation_label": "Mixed",
                })
                continue

            # Historical vectors for 5-year CFO quality
            cfo_list = c_cf["operating_activity"].tolist()
            pat_list = c_pnl["net_profit"].tolist()

            # Latest values
            latest_cf = c_cf.iloc[-1]
            latest_pnl = c_pnl.iloc[-1]
            latest_bs = c_bs.iloc[-1] if not c_bs.empty else None

            cfo_lat = CashflowKPICalculator.safe_float(latest_cf["operating_activity"])
            cfi_lat = CashflowKPICalculator.safe_float(latest_cf["investing_activity"])
            cff_lat = CashflowKPICalculator.safe_float(latest_cf["financing_activity"])
            sales_lat = CashflowKPICalculator.safe_float(latest_pnl["sales"])
            op_lat = CashflowKPICalculator.safe_float(latest_pnl["operating_profit"])
            net_profit_lat = CashflowKPICalculator.safe_float(latest_pnl["net_profit"])

            # 1. CFO Quality
            cfo_qual_res = CashflowKPICalculator.cfo_quality_score(cfo_list[-5:], pat_list[-5:])

            # 2. CapEx Intensity
            capex_res = CashflowKPICalculator.capex_intensity(cfi_lat, sales_lat)

            # 3. FCF Conversion & 5yr FCF CAGR
            fcf_lat = cfo_lat + cfi_lat
            fcf_conv_res = CashflowKPICalculator.fcf_conversion(fcf_lat, op_lat)

            # Compute 5yr FCF CAGR
            fcfs = [CashflowKPICalculator.safe_float(c) + CashflowKPICalculator.safe_float(i)
                    for c, i in zip(c_cf["operating_activity"], c_cf["investing_activity"])]
            fcf_cagr_5yr = None
            if len(fcfs) >= 5 and fcfs[-5] > 0 and fcfs[-1] > 0:
                fcf_cagr_5yr = round2(((fcfs[-1] / fcfs[-5]) ** (1 / 5.0) - 1) * 100.0)

            # 4. Distress Signal: CFO < 0 AND CFF > 0 in latest year
            distress_flag = (cfo_lat < 0) and (cff_lat > 0)
            if distress_flag:
                distress_alerts.append({
                    "company_id": cid,
                    "latest_year": latest_cf["year"],
                    "cfo_value": cfo_lat,
                    "cff_value": cff_lat,
                    "latest_net_profit": net_profit_lat,
                })

            # 5. Deleveraging flag: CFF < 0 AND borrowings declining YoY
            deleveraging_flag = False
            if c_bs is not None and len(c_bs) >= 2:
                borr_curr = CashflowKPICalculator.safe_float(c_bs.iloc[-1].get("borrowings", 0))
                borr_prev = CashflowKPICalculator.safe_float(c_bs.iloc[-2].get("borrowings", 0))
                if cff_lat < 0 and borr_curr < borr_prev:
                    deleveraging_flag = True

            # 6. Capital Allocation Label
            cap_alloc_res = CashflowKPICalculator.capital_allocation_pattern(
                cfo_lat, cfi_lat, cff_lat, cfo_qual_res.value
            )

            # Record historical patterns for pattern change tracking
            for i, cf_row in c_cf.iterrows():
                yr = cf_row["year"]
                cfo_i = CashflowKPICalculator.safe_float(cf_row["operating_activity"])
                cfi_i = CashflowKPICalculator.safe_float(cf_row["investing_activity"])
                cff_i = CashflowKPICalculator.safe_float(cf_row["financing_activity"])
                pat_i = CashflowKPICalculator.safe_float(c_pnl[c_pnl["year"] == yr]["net_profit"].values[0]) if yr in c_pnl["year"].values else 0
                ratio_i = (cfo_i / pat_i) if pat_i > 0 else 0
                pat_label = CashflowKPICalculator.capital_allocation_pattern(cfo_i, cfi_i, cff_i, ratio_i).label
                pattern_history.append({
                    "company_id": cid,
                    "year": yr,
                    "pattern": pat_label,
                })

            intel_records.append({
                "company_id": cid,
                "sector": sector,
                "cfo_quality_score": cfo_qual_res.value,
                "cfo_quality_label": cfo_qual_res.label,
                "capex_intensity_pct": capex_res.value,
                "capex_label": capex_res.label,
                "fcf_cagr_5yr": fcf_cagr_5yr,
                "fcf_conversion_pct": fcf_conv_res.value,
                "distress_flag": distress_flag,
                "deleveraging_flag": deleveraging_flag,
                "capital_allocation_label": cap_alloc_res.label,
            })

        df_intel = pd.DataFrame(intel_records)
        df_distress = pd.DataFrame(distress_alerts)
        df_pat_hist = pd.DataFrame(pattern_history)

        # Track Year-over-Year Pattern Changes
        pattern_changes = []
        if not df_pat_hist.empty:
            for cid, group in df_pat_hist.groupby("company_id"):
                group = group.sort_values("year")
                if len(group) >= 2:
                    prev_yr = group.iloc[-2]["year"]
                    prev_pat = group.iloc[-2]["pattern"]
                    curr_yr = group.iloc[-1]["year"]
                    curr_pat = group.iloc[-1]["pattern"]

                    if prev_pat != curr_pat:
                        pattern_changes.append({
                            "company_id": cid,
                            "previous_year": prev_yr,
                            "previous_pattern": prev_pat,
                            "latest_year": curr_yr,
                            "latest_pattern": curr_pat,
                            "change_summary": f"Moved from {prev_pat} to {curr_pat}"
                        })

        df_changes = pd.DataFrame(pattern_changes)

        # Save deliverables
        excel_path = self.output_dir / "cashflow_intelligence.xlsx"
        alerts_path = self.output_dir / "distress_alerts.csv"
        changes_path = self.output_dir / "pattern_changes.csv"

        df_intel.to_excel(excel_path, index=False)
        df_distress.to_csv(alerts_path, index=False)
        df_changes.to_csv(changes_path, index=False)

        logger.info(f"Saved cashflow_intelligence.xlsx ({len(df_intel)} rows) to {excel_path}")
        logger.info(f"Saved distress_alerts.csv ({len(df_distress)} rows) to {alerts_path}")
        logger.info(f"Saved pattern_changes.csv ({len(df_changes)} rows) to {changes_path}")

        return df_intel, df_distress, df_changes


if __name__ == "__main__":
    manager = CashFlowIntelligenceManager()
    df_intel, df_distress, df_changes = manager.generate()
    print("Cashflow Intelligence rows:", len(df_intel))
    print("Distress alerts count:", len(df_distress))
    print("Pattern changes count:", len(df_changes))