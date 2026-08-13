"""
ratios.py

Financial Ratio Engine

Sprint 2

Implements:

• Net Profit Margin
• Operating Profit Margin
• ROE
• ROCE
• ROA

Author:
Bluestock Internship
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .helpers import percentage, round2
from .constants import (
    HIGH_LEVERAGE_THRESHOLD,
    LOW_ICR_THRESHOLD,
    OPM_TOLERANCE,
)


# ==========================================================
# Result Object
# ==========================================================

@dataclass(slots=True)
class RatioResult:
    """
    Generic result returned by every ratio calculation.
    """

    value: Optional[float]

    flag: Optional[str] = None

    label: Optional[str] = None


# ==========================================================
# Ratio Calculator
# ==========================================================

class FinancialRatioCalculator:
    """
    Computes all financial ratios.

    Each function is independent so that it can be
    unit tested easily.
    """

    # ------------------------------------------------------
    # Internal Helper
    # ------------------------------------------------------

    @staticmethod
    def _round(value):

        if value is None:
            return None

        return round2(value)

    # ======================================================
    # PROFITABILITY RATIOS
    # ======================================================

    @staticmethod
    def net_profit_margin(
        sales,
        net_profit,
    ) -> RatioResult:
        """
        Net Profit Margin

        Net Profit / Sales ×100

        Return None if sales == 0
        """

        value = percentage(
            net_profit,
            sales,
        )

        return RatioResult(
            value=FinancialRatioCalculator._round(value)
        )

    # ------------------------------------------------------

    @staticmethod
    def operating_profit_margin(
        sales,
        operating_profit,
        source_opm=None,
    ) -> RatioResult:
        """
        Operating Profit Margin

        Operating Profit / Sales ×100

        Cross-check against source OPM.
        """

        value = percentage(
            operating_profit,
            sales,
        )

        value = FinancialRatioCalculator._round(value)

        flag = None

        if (
            source_opm is not None
            and value is not None
        ):

            if abs(value - source_opm) > OPM_TOLERANCE:

                flag = "OPM_MISMATCH"

        return RatioResult(
            value=value,
            flag=flag,
        )

    # ------------------------------------------------------

    @staticmethod
    def return_on_equity(
        net_profit,
        equity_capital,
        reserves,
    ) -> RatioResult:
        """
        ROE

        Net Profit /
        (Equity + Reserves)

        Return None if denominator <=0
        """

        denominator = (
            equity_capital +
            reserves
        )

        if denominator <= 0:

            return RatioResult(
                value=None,
                flag="NEGATIVE_EQUITY",
            )

        value = percentage(
            net_profit,
            denominator,
        )

        return RatioResult(
            value=FinancialRatioCalculator._round(value)
        )

    # ------------------------------------------------------

    @staticmethod
    def return_on_capital_employed(
        operating_profit,
        interest,
        equity_capital,
        reserves,
        borrowings,
    ) -> RatioResult:
        """
        ROCE

        EBIT /
        (Equity + Reserves + Borrowings)

        EBIT =
        Operating Profit + Interest
        """

        denominator = (
            equity_capital +
            reserves +
            borrowings
        )

        if denominator <= 0:

            return RatioResult(
                value=None,
                flag="INVALID_CAPITAL",
            )

        ebit = (
            operating_profit +
            interest
        )

        value = percentage(
            ebit,
            denominator,
        )

        return RatioResult(
            value=FinancialRatioCalculator._round(value)
        )

    # ------------------------------------------------------

    @staticmethod
    def return_on_assets(
        net_profit,
        total_assets,
    ) -> RatioResult:
        """
        ROA

        Net Profit /
        Total Assets
        """

        value = percentage(
            net_profit,
            total_assets,
        )

        return RatioResult(
            value=FinancialRatioCalculator._round(value)
        )

    # ======================================================
    # Generic Validation Helpers
    # ======================================================

    @staticmethod
    def is_positive(value):

        return (
            value is not None
            and value > 0
        )

    @staticmethod
    def is_zero(value):

        return (
            value is not None
            and value == 0
        )

    @staticmethod
    def is_negative(value):

        return (
            value is not None
            and value < 0
        )

    @staticmethod
    def safe_float(value):

        try:

            if value is None:
                return 0.0

            return float(value)

        except Exception:

            return 0.0
        
        # ======================================================
    # LEVERAGE RATIOS
    # ======================================================

    @staticmethod
    def debt_to_equity(
        borrowings,
        equity_capital,
        reserves,
    ) -> RatioResult:
        """
        Debt to Equity

        Borrowings /
        (Equity + Reserves)

        Rules
        -----
        • Debt free company -> 0
        • Negative equity -> None
        • D/E > 5 -> HIGH_LEVERAGE
        """

        borrowings = FinancialRatioCalculator.safe_float(
            borrowings
        )

        equity_capital = FinancialRatioCalculator.safe_float(
            equity_capital
        )

        reserves = FinancialRatioCalculator.safe_float(
            reserves
        )

        if borrowings == 0:

            return RatioResult(
                value=0.0,
                label="Debt Free"
            )

        denominator = (
            equity_capital +
            reserves
        )

        if denominator <= 0:

            return RatioResult(
                value=None,
                flag="NEGATIVE_EQUITY"
            )

        ratio = borrowings / denominator

        flag = None

        if ratio > HIGH_LEVERAGE_THRESHOLD:

            flag = "HIGH_LEVERAGE"

        return RatioResult(
            value=FinancialRatioCalculator._round(ratio),
            flag=flag
        )

    @staticmethod
    def interest_coverage(operating_profit, other_income, interest) -> RatioResult:
        return FinancialRatioCalculator.interest_coverage_ratio(operating_profit, other_income, interest)

    # ------------------------------------------------------

    @staticmethod
    def interest_coverage_ratio(

        operating_profit,
        other_income,
        interest,
    ) -> RatioResult:
        """
        Interest Coverage Ratio

        (Operating Profit + Other Income)
/ Interest

        Rules
        -----

        Interest == 0

        -> Debt Free

        ICR <1.5

        -> LOW_INTEREST_COVER
        """

        operating_profit = (
            FinancialRatioCalculator.safe_float(
                operating_profit
            )
        )

        other_income = (
            FinancialRatioCalculator.safe_float(
                other_income
            )
        )

        interest = (
            FinancialRatioCalculator.safe_float(
                interest
            )
        )

        if interest == 0:

            return RatioResult(
                value=None,
                label="Debt Free"
            )

        icr = (
            operating_profit +
            other_income
        ) / interest

        flag = None

        if icr < LOW_ICR_THRESHOLD:

            flag = "LOW_INTEREST_COVER"

        return RatioResult(
            value=FinancialRatioCalculator._round(
                icr
            ),
            flag=flag
        )

    # ------------------------------------------------------

    @staticmethod
    def net_debt(
        borrowings,
        investments,
    ) -> RatioResult:
        """
        Net Debt

        Borrowings -
        Investments

        Negative value

        = Net Cash Company
        """

        borrowings = (
            FinancialRatioCalculator.safe_float(
                borrowings
            )
        )

        investments = (
            FinancialRatioCalculator.safe_float(
                investments
            )
        )

        value = (
            borrowings -
            investments
        )

        label = None

        if value < 0:

            label = "NET_CASH"

        return RatioResult(
            value=FinancialRatioCalculator._round(
                value
            ),
            label=label
        )

    # ------------------------------------------------------

    @staticmethod
    def asset_turnover(
        sales,
        total_assets,
    ) -> RatioResult:
        """
        Asset Turnover

        Sales /
        Total Assets
        """

        sales = (
            FinancialRatioCalculator.safe_float(
                sales
            )
        )

        total_assets = (
            FinancialRatioCalculator.safe_float(
                total_assets
            )
        )

        if total_assets == 0:

            return RatioResult(
                value=None,
                flag="ZERO_ASSETS"
            )

        ratio = (
            sales /
            total_assets
        )

        return RatioResult(
            value=FinancialRatioCalculator._round(
                ratio
            )
        )

    # ------------------------------------------------------

    @staticmethod
    def leverage_summary(
        borrowings,
        equity_capital,
        reserves,
        operating_profit,
        other_income,
        interest,
        investments,
        sales,
        total_assets,
    ):
        """
        Computes all leverage &
        efficiency KPIs together.

        Returns
        -------
        dict
        """

        debt = (
            FinancialRatioCalculator.debt_to_equity(
                borrowings,
                equity_capital,
                reserves,
            )
        )

        icr = (
            FinancialRatioCalculator.interest_coverage_ratio(
                operating_profit,
                other_income,
                interest,
            )
        )

        net_debt = (
            FinancialRatioCalculator.net_debt(
                borrowings,
                investments,
            )
        )

        turnover = (
            FinancialRatioCalculator.asset_turnover(
                sales,
                total_assets,
            )
        )

        return {

            "debt_to_equity":
                debt.value,

            "high_leverage_flag":
                debt.flag,

            "debt_label":
                debt.label,

            "interest_coverage":
                icr.value,

            "interest_flag":
                icr.flag,

            "icr_label":
                icr.label,

            "net_debt":
                net_debt.value,

            "net_debt_label":
                net_debt.label,

            "asset_turnover":
                turnover.value,

            "asset_turnover_flag":
                turnover.flag,
        }
        # ======================================================
    # COMPOSITE QUALITY SCORE
    # ======================================================

    @staticmethod
    def composite_quality_score(
        roe,
        roce,
        net_profit_margin,
        debt_to_equity,
        interest_coverage,
        asset_turnover,
    ) -> RatioResult:
        """
        Composite Quality Score (0-100)

        Scoring Model
        -------------
        ROE                 : 25
        ROCE                : 25
        Net Profit Margin   : 15
        Debt To Equity      : 15
        Interest Coverage   : 10
        Asset Turnover      : 10
        """

        score = 0.0

        # ROE
        if roe is not None:
            if roe >= 20:
                score += 25
            elif roe >= 15:
                score += 20
            elif roe >= 10:
                score += 15
            elif roe >= 5:
                score += 10

        # ROCE
        if roce is not None:
            if roce >= 20:
                score += 25
            elif roce >= 15:
                score += 20
            elif roce >= 10:
                score += 15
            elif roce >= 5:
                score += 10

        # Net Profit Margin
        if net_profit_margin is not None:
            if net_profit_margin >= 20:
                score += 15
            elif net_profit_margin >= 10:
                score += 10
            elif net_profit_margin >= 5:
                score += 5

        # Debt To Equity
        if debt_to_equity is not None:
            if debt_to_equity <= 0.5:
                score += 15
            elif debt_to_equity <= 1:
                score += 12
            elif debt_to_equity <= 2:
                score += 8
            elif debt_to_equity <= 3:
                score += 5

        # Interest Coverage
        if interest_coverage is not None:
            if interest_coverage >= 5:
                score += 10
            elif interest_coverage >= 3:
                score += 8
            elif interest_coverage >= 2:
                score += 5

        # Asset Turnover
        if asset_turnover is not None:
            if asset_turnover >= 2:
                score += 10
            elif asset_turnover >= 1:
                score += 7
            elif asset_turnover >= 0.5:
                score += 4

        return RatioResult(
            value=FinancialRatioCalculator._round(score)
        )

    # ======================================================
    # COMPLETE PROFITABILITY SUMMARY
    # ======================================================

    @staticmethod
    def profitability_summary(
        sales,
        net_profit,
        operating_profit,
        source_opm,
        equity_capital,
        reserves,
        borrowings,
        interest,
        total_assets,
    ):
        """
        Compute all profitability KPIs.
        """

        npm = FinancialRatioCalculator.net_profit_margin(
            sales,
            net_profit,
        )

        opm = FinancialRatioCalculator.operating_profit_margin(
            sales,
            operating_profit,
            source_opm,
        )

        roe = FinancialRatioCalculator.return_on_equity(
            net_profit,
            equity_capital,
            reserves,
        )

        roce = FinancialRatioCalculator.return_on_capital_employed(
            operating_profit,
            interest,
            equity_capital,
            reserves,
            borrowings,
        )

        roa = FinancialRatioCalculator.return_on_assets(
            net_profit,
            total_assets,
        )

        return {

            "net_profit_margin_pct": npm.value,

            "operating_profit_margin_pct": opm.value,

            "return_on_equity_pct": roe.value,

            "return_on_capital_employed_pct": roce.value,

            "return_on_assets_pct": roa.value,

            "opm_flag": opm.flag,

            "roe_flag": roe.flag,

            "roce_flag": roce.flag,

            "roa_flag": roa.flag,
        }

    # ======================================================
    # COMPLETE RATIO SUMMARY
    # ======================================================

    @staticmethod
    def calculate_all(
        *,
        sales,
        net_profit,
        operating_profit,
        source_opm,
        equity_capital,
        reserves,
        borrowings,
        interest,
        other_income,
        investments,
        total_assets,
    ):
        """
        Main public API.

        Ratio Engine calls ONLY this method.
        """

        profitability = (
            FinancialRatioCalculator.profitability_summary(
                sales=sales,
                net_profit=net_profit,
                operating_profit=operating_profit,
                source_opm=source_opm,
                equity_capital=equity_capital,
                reserves=reserves,
                borrowings=borrowings,
                interest=interest,
                total_assets=total_assets,
            )
        )

        leverage = (
            FinancialRatioCalculator.leverage_summary(
                borrowings=borrowings,
                equity_capital=equity_capital,
                reserves=reserves,
                operating_profit=operating_profit,
                other_income=other_income,
                interest=interest,
                investments=investments,
                sales=sales,
                total_assets=total_assets,
            )
        )

        quality = (
            FinancialRatioCalculator.composite_quality_score(
                roe=profitability["return_on_equity_pct"],
                roce=profitability["return_on_capital_employed_pct"],
                net_profit_margin=profitability["net_profit_margin_pct"],
                debt_to_equity=leverage["debt_to_equity"],
                interest_coverage=leverage["interest_coverage"],
                asset_turnover=leverage["asset_turnover"],
            )
        )

        result = {}

        result.update(profitability)

        result.update(leverage)

        result["composite_quality_score"] = quality.value

        return result