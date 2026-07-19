"""
cashflow_kpis.py

Financial Ratio Engine

Sprint 2

Implements

• Free Cash Flow
• CFO Quality Score
• CapEx Intensity
• FCF Conversion
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from .helpers import percentage, round2


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

    # ------------------------------------------------------

    @staticmethod
    def _round(value):

        if value is None:
            return None

        return round2(value)

    # ------------------------------------------------------

    @staticmethod
    def safe_float(value):

        try:

            if value is None:
                return 0.0

            return float(value)

        except Exception:

            return 0.0

    # ======================================================
    # FREE CASH FLOW
    # ======================================================

    @staticmethod
    def free_cash_flow(
        operating_activity,
        investing_activity,
    ) -> CashflowResult:
        """
        Free Cash Flow

        CFO + CFI

        Investing activity is usually negative,
        therefore addition is correct.
        """

        cfo = CashflowKPICalculator.safe_float(
            operating_activity
        )

        cfi = CashflowKPICalculator.safe_float(
            investing_activity
        )

        fcf = cfo + cfi

        label = None

        if fcf > 0:
            label = "POSITIVE_FCF"
        elif fcf < 0:
            label = "NEGATIVE_FCF"

        return CashflowResult(
            value=CashflowKPICalculator._round(fcf),
            label=label,
        )

    # ======================================================
    # CFO QUALITY SCORE
    # ======================================================

    @staticmethod
    def cfo_quality_score(
        cfo_history: List[float],
        pat_history: List[float],
    ) -> CashflowResult:
        """
        CFO / PAT averaged across history.

        >1.0  -> High Quality
        0.5-1 -> Moderate
        <0.5  -> Accrual Risk
        """

        if (
            len(cfo_history) == 0
            or len(pat_history) == 0
        ):

            return CashflowResult(
                value=None,
                flag="INSUFFICIENT_HISTORY",
            )

        ratios = []

        for cfo, pat in zip(
            cfo_history,
            pat_history,
        ):

            cfo = CashflowKPICalculator.safe_float(cfo)
            pat = CashflowKPICalculator.safe_float(pat)

            if pat == 0:
                continue

            ratios.append(cfo / pat)

        if len(ratios) == 0:

            return CashflowResult(
                value=None,
                flag="PAT_ZERO",
            )

        average = sum(ratios) / len(ratios)

        label = "Accrual Risk"

        if average > 1:
            label = "High Quality"

        elif average >= 0.5:
            label = "Moderate"

        return CashflowResult(
            value=CashflowKPICalculator._round(average),
            label=label,
        )

    # ======================================================
    # CAPEX INTENSITY
    # ======================================================

    @staticmethod
    def capex_intensity(
        investing_activity,
        sales,
    ) -> CashflowResult:
        """
        CapEx Intensity

        abs(CFI) / Sales ×100
        """

        cfi = abs(
            CashflowKPICalculator.safe_float(
                investing_activity
            )
        )

        sales = CashflowKPICalculator.safe_float(
            sales
        )

        value = percentage(
            cfi,
            sales,
        )

        value = CashflowKPICalculator._round(value)

        if value is None:

            return CashflowResult(
                value=None,
                flag="ZERO_SALES",
            )

        label = "Capital Intensive"

        if value < 3:
            label = "Asset Light"

        elif value <= 8:
            label = "Moderate"

        return CashflowResult(
            value=value,
            label=label,
        )

    # ======================================================
    # FCF CONVERSION
    # ======================================================

    @staticmethod
    def fcf_conversion(
        free_cash_flow,
        operating_profit,
    ) -> CashflowResult:
        """
        FCF Conversion

        FCF / Operating Profit ×100
        """

        value = percentage(
            free_cash_flow,
            operating_profit,
        )

        value = CashflowKPICalculator._round(value)

        if value is None:

            return CashflowResult(
                value=None,
                flag="ZERO_OPERATING_PROFIT",
            )

        label = "Weak"

        if value >= 100:
            label = "Excellent"

        elif value >= 75:
            label = "Good"

        elif value >= 50:
            label = "Average"

        return CashflowResult(
            value=value,
            label=label,
        )
        # ======================================================
    # CAPITAL ALLOCATION PATTERN
    # ======================================================

    @staticmethod
    def _cashflow_sign(value):
        """
        Returns
        -------
        '+'
        '-'
        '0'
        """

        value = CashflowKPICalculator.safe_float(value)

        if value > 0:
            return "+"

        if value < 0:
            return "-"

        return "0"

    # ------------------------------------------------------

    @staticmethod
    def capital_allocation_pattern(
        operating_activity,
        investing_activity,
        financing_activity,
        cfo_pat_ratio=None,
    ) -> CashflowResult:
        """
        Capital Allocation Classification

        Pattern Matrix

        (+,-,-) = Reinvestor

        (+,-,-) + CFO/PAT>1
                = Shareholder Returns

        (+,+,-) = Liquidating Assets

        (-,+,+) = Distress Signal

        (-,-,+) = Growth Funded by Debt

        (+,+,+) = Cash Accumulator

        (-,-,-) = Pre-Revenue

        (+,-,+) = Mixed
        """

        cfo = CashflowKPICalculator._cashflow_sign(
            operating_activity
        )

        cfi = CashflowKPICalculator._cashflow_sign(
            investing_activity
        )

        cff = CashflowKPICalculator._cashflow_sign(
            financing_activity
        )

        pattern = (
            cfo,
            cfi,
            cff
        )

        label = "Unknown"

        if pattern == ("+", "-", "-"):

            label = "Reinvestor"

            if (
                cfo_pat_ratio is not None
                and cfo_pat_ratio > 1
            ):

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

        return CashflowResult(

            value=None,

            label=label

        )

    # ======================================================
    # COMPLETE CASHFLOW SUMMARY
    # ======================================================

    @staticmethod
    def calculate_all(
        *,
        operating_activity,
        investing_activity,
        financing_activity,
        operating_profit,
        sales,
        cfo_history,
        pat_history,
    ):
        """
        Main public API

        Returns dictionary.
        """

        result = {}

        # ----------------------------------------------

        fcf = (
            CashflowKPICalculator.free_cash_flow(
                operating_activity,
                investing_activity,
            )
        )

        # ----------------------------------------------

        quality = (
            CashflowKPICalculator.cfo_quality_score(
                cfo_history,
                pat_history,
            )
        )

        # ----------------------------------------------

        capex = (
            CashflowKPICalculator.capex_intensity(
                investing_activity,
                sales,
            )
        )

        # ----------------------------------------------

        conversion = (
            CashflowKPICalculator.fcf_conversion(
                fcf.value,
                operating_profit,
            )
        )

        # ----------------------------------------------

        allocation = (
            CashflowKPICalculator.capital_allocation_pattern(
                operating_activity,
                investing_activity,
                financing_activity,
                quality.value,
            )
        )

        # ----------------------------------------------

        result["free_cash_flow"] = fcf.value

        result["free_cash_flow_label"] = fcf.label

        # ----------------------------------------------

        result["cfo_quality_score"] = quality.value

        result["cfo_quality_label"] = quality.label

        # ----------------------------------------------

        result["capex_intensity"] = capex.value

        result["capex_label"] = capex.label

        # ----------------------------------------------

        result["fcf_conversion"] = conversion.value

        result["fcf_conversion_label"] = conversion.label

        # ----------------------------------------------

        result["capital_allocation"] = allocation.label

        return result

    # ======================================================
    # CSV HELPER
    # ======================================================

    @staticmethod
    def capital_allocation_record(
        company_id,
        year,
        operating_activity,
        investing_activity,
        financing_activity,
        pattern_label,
    ):
        """
        One CSV row
        """

        return {

            "company_id": company_id,

            "year": year,

            "cfo_sign":
                CashflowKPICalculator._cashflow_sign(
                    operating_activity
                ),

            "cfi_sign":
                CashflowKPICalculator._cashflow_sign(
                    investing_activity
                ),

            "cff_sign":
                CashflowKPICalculator._cashflow_sign(
                    financing_activity
                ),

            "pattern_label":
                pattern_label,

        }