"""
=========================================================
NIFTY100 Platform
Sprint 3 - Screening Presets

Provides reusable investment screening strategies.

Author : Saranya
=========================================================
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

import yaml

from .engine import FilterRule
from .engine import ScreenerEngine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Exceptions
# ---------------------------------------------------------


class PresetValidationError(Exception):
    """Raised when an invalid preset is created."""


# ---------------------------------------------------------
# Dataclass
# ---------------------------------------------------------


@dataclass(slots=True)
class ScreeningPreset:
    """
    Represents one reusable screening strategy.
    """

    name: str

    description: str

    filters: List[FilterRule] = field(default_factory=list)

    sort_by: str = "composite_score"

    ascending: bool = False

    tags: List[str] = field(default_factory=list)

    version: str = "1.0"

    author: str = "Saranya"

    enabled: bool = True

    def copy(self) -> "ScreeningPreset":
        """
        Return a deep copy.
        """

        return copy.deepcopy(self)

    @property
    def filter_count(self) -> int:
        return len(self.filters)

    def as_dict(self) -> Dict:

        return {

            "name": self.name,

            "description": self.description,

            "sort_by": self.sort_by,

            "ascending": self.ascending,

            "tags": self.tags,

            "version": self.version,

            "author": self.author,

            "enabled": self.enabled,

            "filters": [

                {

                    "metric": f.metric,

                    "operator": f.operator,

                    "value": f.value,

                }

                for f in self.filters

            ],

        }


# ---------------------------------------------------------
# Registry
# ---------------------------------------------------------


class PresetRegistry:
    """
    Stores all available presets.
    """

    def __init__(self):

        self._presets: Dict[str, ScreeningPreset] = {}

    # -----------------------------------------------------

    @staticmethod
    def _normalize(name: str) -> str:

        return name.strip().lower()

    # -----------------------------------------------------

    def exists(self, name: str) -> bool:

        return self._normalize(name) in self._presets

    # -----------------------------------------------------

    def register(
        self,
        preset: ScreeningPreset,
        overwrite: bool = False,
    ):

        key = self._normalize(
            preset.name
        )

        if key in self._presets and not overwrite:

            raise PresetValidationError(

                f"Preset '{preset.name}' already exists."

            )

        self._presets[key] = preset

        logger.info(

            "Registered preset : %s",

            preset.name,

        )

    # -----------------------------------------------------

    def unregister(
        self,
        name: str,
    ):

        key = self._normalize(name)

        if key not in self._presets:

            raise KeyError(name)

        del self._presets[key]

    # -----------------------------------------------------

    def get(
        self,
        name: str,
    ) -> ScreeningPreset:

        key = self._normalize(name)

        if key not in self._presets:

            raise KeyError(

                f"Unknown preset '{name}'."

            )

        return self._presets[key].copy()

    # -----------------------------------------------------

    def list(self) -> List[str]:

        return sorted(

            p.name

            for p in self._presets.values()

        )

    # -----------------------------------------------------

    def all(self) -> List[ScreeningPreset]:

        return [

            p.copy()

            for p in self._presets.values()

        ]

    # -----------------------------------------------------

    def clear(self):

        self._presets.clear()

    # -----------------------------------------------------

    def __len__(self):

        return len(self._presets)

    def __contains__(self, item):

        return self.exists(item)

    def __iter__(self):

        return iter(

            self.all()

        )


# ---------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------


VALID_OPERATORS = {

    ">",

    ">=",

    "<",

    "<=",

    "==",

    "!=",

    "contains",

}


def validate_filter(
    rule: FilterRule,
):

    """
    Validate one filter rule.
    """

    supported = set(

        ScreenerEngine.supported_metrics()

    )

    if rule.metric not in supported:

        raise PresetValidationError(

            f"Unsupported metric : {rule.metric}"

        )

    if rule.operator not in VALID_OPERATORS:

        raise PresetValidationError(

            f"Unsupported operator : {rule.operator}"

        )


def validate_preset(
    preset: ScreeningPreset,
):

    """
    Validate preset.
    """

    if not preset.name.strip():

        raise PresetValidationError(

            "Preset name cannot be empty."

        )

    for rule in preset.filters:

        validate_filter(rule)

    if preset.sort_by != "composite_score":

        supported = set(

            ScreenerEngine.supported_metrics()

        )

        supported.add(

            "composite_score"

        )

        if preset.sort_by not in supported:

            raise PresetValidationError(

                f"Invalid sort column : "

                f"{preset.sort_by}"

            )


# ---------------------------------------------------------
# Registry Factory
# ---------------------------------------------------------


def create_registry() -> PresetRegistry:
    """
    Returns a registry populated with all built-in presets.

    Actual registrations are performed
    in Part 2.
    """

    registry = PresetRegistry()

    return registry

# ---------------------------------------------------------
# Filter Factory
# ---------------------------------------------------------


def rule(
    metric: str,
    operator: str,
    value,
) -> FilterRule:
    """
    Convenience factory for FilterRule.
    """

    return FilterRule(
        metric=metric,
        operator=operator,
        value=value,
    )


# ---------------------------------------------------------
# Buffett Style
# ---------------------------------------------------------


def buffett_preset() -> ScreeningPreset:

    preset = ScreeningPreset(

        name="Buffett",

        description=(
            "High quality companies with "
            "strong profitability and low debt."
        ),

        tags=[
            "value",
            "quality",
            "long_term",
        ],

        filters=[

            rule(
                "return_on_equity_pct",
                ">=",
                20,
            ),

            rule(
                "debt_to_equity",
                "<=",
                0.50,
            ),

            rule(
                "interest_coverage",
                ">=",
                5,
            ),

            rule(
                "net_profit_margin_pct",
                ">=",
                15,
            ),

            rule(
                "operating_profit_margin_pct",
                ">=",
                18,
            ),

        ],

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# Benjamin Graham
# ---------------------------------------------------------


def graham_preset() -> ScreeningPreset:

    preset = ScreeningPreset(

        name="Benjamin Graham",

        description=(
            "Conservative value investing."
        ),

        tags=[
            "value",
            "defensive",
        ],

        filters=[

            rule(
                "pe_ratio",
                "<=",
                20,
            ),

            rule(
                "pb_ratio",
                "<=",
                2,
            ),

            rule(
                "debt_to_equity",
                "<=",
                1,
            ),

            rule(
                "return_on_equity_pct",
                ">=",
                12,
            ),

        ],

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# Peter Lynch
# ---------------------------------------------------------


def peter_lynch_preset() -> ScreeningPreset:

    preset = ScreeningPreset(

        name="Peter Lynch",

        description=(
            "Fast-growing profitable companies."
        ),

        tags=[
            "growth",
            "quality",
        ],

        filters=[

            rule(
                "return_on_equity_pct",
                ">=",
                18,
            ),

            rule(
                "operating_profit_margin_pct",
                ">=",
                15,
            ),

            rule(
                "asset_turnover",
                ">=",
                1,
            ),

            rule(
                "interest_coverage",
                ">=",
                4,
            ),

        ],

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# High ROE
# ---------------------------------------------------------


def high_roe_preset() -> ScreeningPreset:

    preset = ScreeningPreset(

        name="High ROE",

        description=(
            "Companies with exceptional ROE."
        ),

        tags=[
            "quality",
        ],

        filters=[

            rule(
                "return_on_equity_pct",
                ">=",
                25,
            ),

        ],

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# Low Debt
# ---------------------------------------------------------


def low_debt_preset() -> ScreeningPreset:

    preset = ScreeningPreset(

        name="Low Debt",

        description=(
            "Financially strong balance sheets."
        ),

        tags=[
            "quality",
            "safe",
        ],

        filters=[

            rule(
                "debt_to_equity",
                "<=",
                0.30,
            ),

            rule(
                "interest_coverage",
                ">=",
                8,
            ),

        ],

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# Quality Compounders
# ---------------------------------------------------------


def quality_compounder_preset() -> ScreeningPreset:

    preset = ScreeningPreset(

        name="Quality Compounders",

        description=(
            "Businesses with consistently "
            "high profitability."
        ),

        tags=[
            "compounder",
            "quality",
        ],

        filters=[

            rule(
                "return_on_equity_pct",
                ">=",
                18,
            ),

            rule(
                "net_profit_margin_pct",
                ">=",
                15,
            ),

            rule(
                "operating_profit_margin_pct",
                ">=",
                15,
            ),

            rule(
                "free_cash_flow_cr",
                ">",
                0,
            ),

            rule(
                "cash_from_operations_cr",
                ">",
                0,
            ),

        ],

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# Dividend Growth
# ---------------------------------------------------------


def dividend_growth_preset() -> ScreeningPreset:

    preset = ScreeningPreset(

        name="Dividend Growth",

        description=(
            "Dividend-paying companies "
            "with sustainable profits."
        ),

        tags=[
            "income",
            "dividend",
        ],

        filters=[

            rule(
                "dividend_yield_pct",
                ">=",
                1.0,
            ),

            rule(
                "dividend_payout_ratio_pct",
                "<=",
                70,
            ),

            rule(
                "return_on_equity_pct",
                ">=",
                15,
            ),

        ],

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# Register Built-in Presets
# ---------------------------------------------------------


def register_builtin_presets(
    registry: PresetRegistry,
):
    """
    Register all built-in presets.
    """

    presets = [

        buffett_preset(),

        graham_preset(),

        peter_lynch_preset(),

        high_roe_preset(),

        low_debt_preset(),

        quality_compounder_preset(),

        dividend_growth_preset(),

    ]

    for preset in presets:

        registry.register(
            preset,
            overwrite=True,
        )

    logger.info(

        "%d built-in presets registered.",

        len(presets),

    )

    return registry


# ---------------------------------------------------------
# Update Registry Factory
# ---------------------------------------------------------


def create_registry() -> PresetRegistry:

    registry = PresetRegistry()

    register_builtin_presets(
        registry
    )

    return registry

# ---------------------------------------------------------
# Preset Builder
# ---------------------------------------------------------


class PresetBuilder:
    """
    Fluent builder for custom presets.

    Example
    -------
    preset = (
        PresetBuilder("My Preset")
        .description("Custom screening")
        .tag("custom")
        .add(
            metric="return_on_equity_pct",
            operator=">=",
            value=20,
        )
        .add(
            metric="debt_to_equity",
            operator="<=",
            value=0.5,
        )
        .build()
    )
    """

    def __init__(self, name: str):

        self._preset = ScreeningPreset(
            name=name,
            description="",
        )

    def description(self, text: str):

        self._preset.description = text

        return self

    def tag(self, tag: str):

        if tag not in self._preset.tags:

            self._preset.tags.append(tag)

        return self

    def sort_by(
        self,
        column: str,
        ascending: bool = False,
    ):

        self._preset.sort_by = column

        self._preset.ascending = ascending

        return self

    def add(
        self,
        metric: str,
        operator: str,
        value,
    ):

        self._preset.filters.append(

            rule(
                metric,
                operator,
                value,
            )

        )

        return self

    def build(self) -> ScreeningPreset:

        validate_preset(
            self._preset
        )

        return self._preset.copy()


# ---------------------------------------------------------
# YAML Export
# ---------------------------------------------------------


def save_preset_yaml(
    preset: ScreeningPreset,
    filename,
):
    """
    Save preset as YAML.
    """

    validate_preset(
        preset
    )

    output = Path(filename)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output,
        "w",
        encoding="utf8",
    ) as file:

        yaml.safe_dump(

            preset.as_dict(),

            file,

            sort_keys=False,

            allow_unicode=True,

        )

    logger.info(
        "Preset exported : %s",
        output,
    )


# ---------------------------------------------------------
# YAML Import
# ---------------------------------------------------------


def load_preset_yaml(
    filename,
) -> ScreeningPreset:
    """
    Load preset from YAML.
    """

    path = Path(filename)

    if not path.exists():

        raise FileNotFoundError(path)

    with open(
        path,
        "r",
        encoding="utf8",
    ) as file:

        data = yaml.safe_load(file)

    filters = []

    for item in data.get(
        "filters",
        [],
    ):

        filters.append(

            FilterRule(

                metric=item["metric"],

                operator=item["operator"],

                value=item["value"],

            )

        )

    preset = ScreeningPreset(

        name=data["name"],

        description=data.get(
            "description",
            "",
        ),

        filters=filters,

        sort_by=data.get(
            "sort_by",
            "composite_score",
        ),

        ascending=data.get(
            "ascending",
            False,
        ),

        tags=data.get(
            "tags",
            [],
        ),

        version=data.get(
            "version",
            "1.0",
        ),

        author=data.get(
            "author",
            "Saranya",
        ),

        enabled=data.get(
            "enabled",
            True,
        ),

    )

    validate_preset(
        preset
    )

    return preset


# ---------------------------------------------------------
# Registry Utilities
# ---------------------------------------------------------


def presets_by_tag(
    registry: PresetRegistry,
    tag: str,
):
    """
    Return presets having the given tag.
    """

    tag = tag.lower()

    return [

        preset.copy()

        for preset in registry.all()

        if tag in [

            t.lower()

            for t in preset.tags

        ]

    ]


def clone_preset(
    registry: PresetRegistry,
    source: str,
    new_name: str,
):

    preset = registry.get(
        source
    )

    preset.name = new_name

    registry.register(
        preset
    )

    return preset


def delete_preset(
    registry: PresetRegistry,
    name: str,
):

    registry.unregister(
        name
    )


# ---------------------------------------------------------
# Singleton Registry
# ---------------------------------------------------------


DEFAULT_REGISTRY = create_registry()


# ---------------------------------------------------------
# Public Helper API
# ---------------------------------------------------------


def list_presets():

    return DEFAULT_REGISTRY.list()


def get_preset(
    name: str,
):

    return DEFAULT_REGISTRY.get(
        name
    )


def register_preset(
    preset: ScreeningPreset,
):

    validate_preset(
        preset
    )

    DEFAULT_REGISTRY.register(
        preset,
        overwrite=True,
    )


def available_tags():

    tags = set()

    for preset in DEFAULT_REGISTRY.all():

        tags.update(
            preset.tags
        )

    return sorted(tags)


# ---------------------------------------------------------
# Module Exports
# ---------------------------------------------------------


__all__ = [

    "ScreeningPreset",

    "PresetRegistry",

    "PresetBuilder",

    "PresetValidationError",

    "create_registry",

    "register_builtin_presets",

    "list_presets",

    "get_preset",

    "register_preset",

    "available_tags",

    "clone_preset",

    "delete_preset",

    "presets_by_tag",

    "save_preset_yaml",

    "load_preset_yaml",

    "DEFAULT_REGISTRY",

]