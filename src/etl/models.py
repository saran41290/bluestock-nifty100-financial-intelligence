"""
models.py

Common data models used by the ETL validation framework.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(slots=True)
class ValidationFailure:
    """
    Represents one Data Quality validation failure.
    """

    rule_id: str
    severity: str
    dataset: str
    row_number: Optional[int]

    company_id: Optional[str] = None
    year: Optional[str] = None

    column_name: Optional[str] = None

    message: str = ""

    value: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Convert object into dictionary.
        """

        return asdict(self)