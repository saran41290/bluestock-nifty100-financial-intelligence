"""
Utility helpers for ratio calculations.
"""

from typing import Optional


def safe_divide(
    numerator: float,
    denominator: float
) -> Optional[float]:

    if denominator is None:
        return None

    if denominator == 0:
        return None

    return numerator / denominator


def percentage(
    numerator: float,
    denominator: float
):

    value = safe_divide(
        numerator,
        denominator
    )

    if value is None:
        return None

    return value * 100


def round2(value):

    if value is None:
        return None

    return round(value, 2)