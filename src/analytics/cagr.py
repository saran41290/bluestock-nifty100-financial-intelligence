"""
cagr.py

Financial CAGR Engine

Implements

• Revenue CAGR
• PAT CAGR
• EPS CAGR

Supports

✓ 3 Years
✓ 5 Years
✓ 10 Years

Handles

✓ Positive → Positive
✓ Positive → Negative
✓ Negative → Positive
✓ Negative → Negative
✓ Zero Base
✓ Insufficient Data
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List
import math


# ==========================================================
# Result Object
# ==========================================================

@dataclass(slots=True)
class CAGRResult:

    value: Optional[float]

    flag: Optional[str] = None


# ==========================================================
# CAGR Calculator
# ==========================================================

class CAGRCalculator:

    @staticmethod
    def calculate_cagr(start_val: float, end_val: float, periods: int) -> CAGRResult:
        return CAGRCalculator.calculate(start_val, end_val, periods)

    # ------------------------------------------------------

    @staticmethod
    def round2(value):


        if value is None:

            return None

        return round(value, 2)

    # ------------------------------------------------------

    @staticmethod
    def calculate(
        start_value: float,
        end_value: float,
        years: int,
    ) -> CAGRResult:
        """
        CAGR Formula

        ((End/Start)^(1/n)-1)*100
        """

        if years <= 0:

            return CAGRResult(
                value=None,
                flag="INVALID_PERIOD"
            )

        if start_value == 0:

            return CAGRResult(
                value=None,
                flag="ZERO_BASE"
            )

        # Positive -> Positive

        if start_value > 0 and end_value > 0:

            value = (
                math.pow(
                    end_value / start_value,
                    1 / years
                ) - 1
            ) * 100

            return CAGRResult(
                value=CAGRCalculator.round2(value)
            )

        # Positive -> Loss

        if start_value > 0 and end_value < 0:

            return CAGRResult(
                value=None,
                flag="DECLINE_TO_LOSS"
            )

        # Loss -> Profit

        if start_value < 0 and end_value > 0:

            return CAGRResult(
                value=None,
                flag="TURNAROUND"
            )

        # Loss -> Loss

        if start_value < 0 and end_value < 0:

            return CAGRResult(
                value=None,
                flag="BOTH_NEGATIVE"
            )

        return CAGRResult(
            value=None,
            flag="UNKNOWN"
        )

    # ======================================================

    @staticmethod
    def get_window(
        values: List[float],
        years: int,
    ):
        """
        Returns

        start,end
        """

        if len(values) < years + 1:

            return None

        return (

            values[-(years + 1)],

            values[-1]

        )

    # ======================================================

    @staticmethod
    def calculate_window(
        values: List[float],
        years: int,
    ) -> CAGRResult:

        window = CAGRCalculator.get_window(
            values,
            years,
        )

        if window is None:

            return CAGRResult(
                value=None,
                flag="INSUFFICIENT"
            )

        start_value, end_value = window

        return CAGRCalculator.calculate(
            start_value,
            end_value,
            years,
        )

    # ======================================================

    @staticmethod
    def revenue_cagr(
        sales: List[float],
    ):

        return {

            "revenue_cagr_3yr":
                CAGRCalculator.calculate_window(
                    sales,
                    3,
                ),

            "revenue_cagr_5yr":
                CAGRCalculator.calculate_window(
                    sales,
                    5,
                ),

            "revenue_cagr_10yr":
                CAGRCalculator.calculate_window(
                    sales,
                    10,
                ),
        }

    # ======================================================

    @staticmethod
    def pat_cagr(
        profits: List[float],
    ):

        return {

            "pat_cagr_3yr":
                CAGRCalculator.calculate_window(
                    profits,
                    3,
                ),

            "pat_cagr_5yr":
                CAGRCalculator.calculate_window(
                    profits,
                    5,
                ),

            "pat_cagr_10yr":
                CAGRCalculator.calculate_window(
                    profits,
                    10,
                ),
        }

    # ======================================================

    @staticmethod
    def eps_cagr(
        eps_values: List[float],
    ):

        return {

            "eps_cagr_3yr":
                CAGRCalculator.calculate_window(
                    eps_values,
                    3,
                ),

            "eps_cagr_5yr":
                CAGRCalculator.calculate_window(
                    eps_values,
                    5,
                ),

            "eps_cagr_10yr":
                CAGRCalculator.calculate_window(
                    eps_values,
                    10,
                ),
        }

    # ======================================================

    @staticmethod
    def calculate_all(
        sales: List[float],
        profits: List[float],
        eps: List[float],
    ):
        """
        Returns one merged dictionary
        """

        result = {}

        revenue = CAGRCalculator.revenue_cagr(
            sales
        )

        pat = CAGRCalculator.pat_cagr(
            profits
        )

        eps_result = CAGRCalculator.eps_cagr(
            eps
        )

        for item in revenue.items():

            result[item[0]] = item[1].value

            result[item[0] + "_flag"] = item[1].flag

        for item in pat.items():

            result[item[0]] = item[1].value

            result[item[0] + "_flag"] = item[1].flag

        for item in eps_result.items():

            result[item[0]] = item[1].value

            result[item[0] + "_flag"] = item[1].flag

        return result


CAGREngine = CAGRCalculator