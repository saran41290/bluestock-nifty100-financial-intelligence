"""
=========================================================
NIFTY100 Platform
Sprint 3

Unit Tests
tests/test_presets.py

Author : Saranya
=========================================================
"""

from pathlib import Path

import pytest

from src.screener.engine import FilterRule

from src.screener.presets import (
    DEFAULT_REGISTRY,
    PresetBuilder,
    PresetRegistry,
    PresetValidationError,
    ScreeningPreset,
    available_tags,
    buffett_preset,
    clone_preset,
    create_registry,
    delete_preset,
    dividend_growth_preset,
    get_preset,
    graham_preset,
    high_roe_preset,
    list_presets,
    load_preset_yaml,
    low_debt_preset,
    peter_lynch_preset,
    presets_by_tag,
    quality_compounder_preset,
    register_builtin_presets,
    register_preset,
    rule,
    save_preset_yaml,
    validate_filter,
    validate_preset,
)


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------


@pytest.fixture
def registry():

    return create_registry()


@pytest.fixture
def sample_preset():

    return ScreeningPreset(

        name="Sample",

        description="Sample preset",

        filters=[

            FilterRule(

                metric="return_on_equity_pct",

                operator=">=",

                value=15,

            )

        ],

    )


# ---------------------------------------------------------
# Registry
# ---------------------------------------------------------


def test_create_registry(registry):

    assert isinstance(
        registry,
        PresetRegistry,
    )


def test_builtin_presets(registry):

    presets = registry.list()

    assert "Buffett" in presets

    assert "Benjamin Graham" in presets

    assert "Peter Lynch" in presets


def test_registry_length(registry):

    assert len(registry) >= 7


def test_registry_exists(registry):

    assert registry.exists("Buffett")

    assert registry.exists("buffett")

    assert not registry.exists("xyz")


def test_registry_get(registry):

    preset = registry.get("Buffett")

    assert preset.name == "Buffett"

    assert len(preset.filters) > 0


def test_registry_unknown(registry):

    with pytest.raises(KeyError):

        registry.get("Unknown")


def test_register(sample_preset):

    registry = PresetRegistry()

    registry.register(sample_preset)

    assert registry.exists("Sample")


def test_duplicate_register(sample_preset):

    registry = PresetRegistry()

    registry.register(sample_preset)

    with pytest.raises(PresetValidationError):

        registry.register(sample_preset)


def test_unregister(sample_preset):

    registry = PresetRegistry()

    registry.register(sample_preset)

    registry.unregister("Sample")

    assert not registry.exists("Sample")


def test_registry_iteration(registry):

    count = 0

    for preset in registry:

        assert isinstance(

            preset,

            ScreeningPreset,

        )

        count += 1

    assert count == len(registry)


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------


def test_validate_filter():

    validate_filter(

        FilterRule(

            metric="return_on_equity_pct",

            operator=">=",

            value=20,

        )

    )


def test_invalid_metric():

    with pytest.raises(

        PresetValidationError

    ):

        validate_filter(

            FilterRule(

                metric="dummy",

                operator=">=",

                value=10,

            )

        )


def test_invalid_operator():

    with pytest.raises(

        PresetValidationError

    ):

        validate_filter(

            FilterRule(

                metric="return_on_equity_pct",

                operator="LIKE",

                value=10,

            )

        )


def test_validate_preset(sample_preset):

    validate_preset(sample_preset)


def test_empty_name():

    preset = ScreeningPreset(

        name="",

        description="",

    )

    with pytest.raises(

        PresetValidationError

    ):

        validate_preset(preset)


# ---------------------------------------------------------
# Builder
# ---------------------------------------------------------


def test_builder():

    preset = (

        PresetBuilder(

            "Builder"

        )

        .description(

            "Builder preset"

        )

        .tag(

            "quality"

        )

        .add(

            metric="return_on_equity_pct",

            operator=">=",

            value=18,

        )

        .add(

            metric="debt_to_equity",

            operator="<=",

            value=0.5,

        )

        .build()

    )

    assert preset.name == "Builder"

    assert len(preset.filters) == 2

    assert preset.tags == [

        "quality"

    ]


def test_builder_sort():

    preset = (

        PresetBuilder(

            "Sort"

        )

        .sort_by(

            "return_on_equity_pct",

            ascending=True,

        )

        .add(

            metric="return_on_equity_pct",

            operator=">=",

            value=15,

        )

        .build()

    )

    assert preset.sort_by == "return_on_equity_pct"

    assert preset.ascending is True


# ---------------------------------------------------------
# Rule Factory
# ---------------------------------------------------------


def test_rule():

    r = rule(

        "pe_ratio",

        "<=",

        20,

    )

    assert isinstance(

        r,

        FilterRule,

    )

    assert r.metric == "pe_ratio"

    assert r.operator == "<="


# ---------------------------------------------------------
# Built-in Presets
# ---------------------------------------------------------


@pytest.mark.parametrize(

    "factory",

    [

        buffett_preset,

        graham_preset,

        peter_lynch_preset,

        high_roe_preset,

        low_debt_preset,

        quality_compounder_preset,

        dividend_growth_preset,

    ],

)

def test_builtin_factories(factory):

    preset = factory()

    assert isinstance(

        preset,

        ScreeningPreset,

    )

    assert len(

        preset.filters

    ) > 0


def test_filter_count():

    preset = buffett_preset()

    assert preset.filter_count == 5


def test_copy():

    preset = buffett_preset()

    cloned = preset.copy()

    assert cloned is not preset

    assert cloned.filters is not preset.filters

    assert cloned.name == preset.name


def test_as_dict():

    data = buffett_preset().as_dict()

    assert data["name"] == "Buffett"

    assert "filters" in data

    assert len(data["filters"]) > 0

# ---------------------------------------------------------
# YAML Import / Export
# ---------------------------------------------------------


def test_yaml_export_import(tmp_path):

    preset = buffett_preset()

    output = tmp_path / "buffett.yaml"

    save_preset_yaml(
        preset,
        output,
    )

    assert output.exists()

    loaded = load_preset_yaml(
        output,
    )

    assert loaded.name == preset.name

    assert loaded.description == preset.description

    assert len(loaded.filters) == len(
        preset.filters
    )


def test_yaml_file_not_found():

    with pytest.raises(FileNotFoundError):

        load_preset_yaml(
            "dummy.yaml"
        )


# ---------------------------------------------------------
# Clone / Delete
# ---------------------------------------------------------


def test_clone_preset(registry):

    clone = clone_preset(

        registry,

        "Buffett",

        "Buffett Clone",

    )

    assert registry.exists(
        "Buffett Clone"
    )

    assert clone.name == "Buffett Clone"

    assert len(clone.filters) > 0


def test_delete_preset(registry):

    clone_preset(

        registry,

        "Buffett",

        "Delete Me",

    )

    assert registry.exists(
        "Delete Me"
    )

    delete_preset(

        registry,

        "Delete Me",

    )

    assert not registry.exists(
        "Delete Me"
    )


# ---------------------------------------------------------
# Tags
# ---------------------------------------------------------


def test_presets_by_tag_quality(registry):

    presets = presets_by_tag(

        registry,

        "quality",

    )

    assert len(presets) > 0

    for preset in presets:

        assert "quality" in [

            tag.lower()

            for tag in preset.tags

        ]


def test_available_tags():

    tags = available_tags()

    assert isinstance(tags, list)

    assert "quality" in [

        tag.lower()

        for tag in tags

    ]


# ---------------------------------------------------------
# Global Registry
# ---------------------------------------------------------


def test_default_registry():

    assert isinstance(

        DEFAULT_REGISTRY,

        PresetRegistry,

    )

    assert len(DEFAULT_REGISTRY) >= 7


def test_list_presets():

    names = list_presets()

    assert isinstance(

        names,

        list,

    )

    assert "Buffett" in names


def test_get_preset():

    preset = get_preset(

        "Buffett"

    )

    assert preset.name == "Buffett"


def test_register_global():

    preset = ScreeningPreset(

        name="Global",

        description="",

        filters=[

            FilterRule(

                metric="return_on_equity_pct",

                operator=">=",

                value=18,

            )

        ],

    )

    register_preset(

        preset

    )

    assert "Global" in list_presets()


# ---------------------------------------------------------
# Registry Factory
# ---------------------------------------------------------


def test_register_builtin_presets():

    registry = PresetRegistry()

    register_builtin_presets(
        registry
    )

    assert len(registry) >= 7


# ---------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------


def test_copy_independent():

    preset = buffett_preset()

    clone = preset.copy()

    clone.filters.append(

        FilterRule(

            metric="pe_ratio",

            operator="<=",

            value=20,

        )

    )

    assert len(clone.filters) == (

        len(preset.filters) + 1

    )

    assert len(clone.filters) != len(

        preset.filters

    )


def test_registry_clear():

    registry = create_registry()

    assert len(registry) > 0

    registry.clear()

    assert len(registry) == 0


def test_contains_operator():

    registry = create_registry()

    assert "Buffett" in registry

    assert "XYZ" not in registry


def test_all_returns_copy(registry):

    presets = registry.all()

    presets.pop()

    assert len(registry) > len(presets)


def test_filter_rule_values():

    preset = buffett_preset()

    for rule in preset.filters:

        assert rule.metric

        assert rule.operator

        assert rule.value is not None


def test_registry_list_sorted(registry):

    names = registry.list()

    assert names == sorted(names)


def test_enabled_flag():

    preset = buffett_preset()

    assert preset.enabled is True


def test_version():

    preset = buffett_preset()

    assert preset.version == "1.0"


def test_author():

    preset = buffett_preset()

    assert preset.author == "Saranya"


def test_description():

    preset = buffett_preset()

    assert len(preset.description) > 0


# ---------------------------------------------------------
# Smoke Test
# ---------------------------------------------------------


def test_every_builtin_valid():

    registry = create_registry()

    for preset in registry:

        validate_preset(preset)


# ---------------------------------------------------------
# End
# ---------------------------------------------------------