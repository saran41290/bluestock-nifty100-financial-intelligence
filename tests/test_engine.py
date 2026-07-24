from pathlib import Path

import pandas as pd
import pytest

from src.screener.engine import (
    ScreenerEngine,
    ValidationError,
)


# ----------------------------------------------------------
# Test Paths
# ----------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RATIOS = ROOT / "supporting_datasets" / "financial_ratios.xlsx"

MARKET = ROOT / "supporting_datasets" / "market_cap.xlsx"

SECTORS = ROOT / "supporting_datasets" / "sectors.xlsx"

PEERS = ROOT / "supporting_datasets" / "peer_groups.xlsx"

CONFIG = ROOT / "config" / "screener_config.yaml"

OUTPUT = ROOT / "output" / "test_output.xlsx"


# ----------------------------------------------------------
# Fixture
# ----------------------------------------------------------

@pytest.fixture
def engine():

    return ScreenerEngine(

        ratios_path=RATIOS,

        market_cap_path=MARKET,

        sectors_path=SECTORS,

        peer_groups_path=PEERS,

        config_path=CONFIG,

    )


# ----------------------------------------------------------
# Configuration
# ----------------------------------------------------------

def test_load_config(engine):

    engine.load_config()

    assert engine.config is not None

    assert len(engine.config.filters) > 0


# ----------------------------------------------------------
# Dataset Loading
# ----------------------------------------------------------

def test_load_data(engine):

    engine.load_data()

    assert isinstance(engine.ratios_df, pd.DataFrame)

    assert isinstance(engine.market_df, pd.DataFrame)

    assert isinstance(engine.sector_df, pd.DataFrame)

    assert isinstance(engine.peer_df, pd.DataFrame)


# ----------------------------------------------------------
# Validation
# ----------------------------------------------------------

def test_validation(engine):

    engine.load_data()

    engine.validate()


# ----------------------------------------------------------
# Build Master
# ----------------------------------------------------------

def test_master_dataframe(engine):

    engine.prepare()

    assert engine.master_df is not None

    assert len(engine.master_df) > 0

    assert "company_id" in engine.master_df.columns

    assert "pe_ratio" in engine.master_df.columns

    assert "return_on_equity_pct" in engine.master_df.columns


# ----------------------------------------------------------
# Latest Year
# ----------------------------------------------------------

def test_keep_latest_year(engine):

    engine.prepare()

    engine.keep_latest_year()

    grouped = (

        engine.master_df

        .groupby("company_id")

        .size()

    )

    assert grouped.max() == 1


# ----------------------------------------------------------
# Duplicate Removal
# ----------------------------------------------------------

def test_remove_duplicates(engine):

    engine.prepare()

    engine.remove_duplicates()

    assert (

        engine.master_df["company_id"]

        .duplicated()

        .sum()

        == 0

    )


# ----------------------------------------------------------
# Apply Filters
# ----------------------------------------------------------

def test_apply_filters(engine):

    engine.prepare()

    engine.keep_latest_year()

    engine.remove_duplicates()

    result = engine.apply_filters()

    assert isinstance(result, pd.DataFrame)

    assert len(result) > 0


# ----------------------------------------------------------
# Composite Score
# ----------------------------------------------------------

def test_composite_score(engine):

    engine.prepare()

    engine.keep_latest_year()

    engine.remove_duplicates()

    result = engine.apply_filters()

    result = engine.calculate_composite_score(result)

    assert "composite_score" in result.columns

    assert result["composite_score"].between(

        0,

        100

    ).all()


# ----------------------------------------------------------
# Sorting
# ----------------------------------------------------------

def test_sorting(engine):

    engine.prepare()

    engine.keep_latest_year()

    engine.remove_duplicates()

    result = engine.apply_filters()

    result = engine.calculate_composite_score(result)

    result = engine.sort_results(result)

    assert len(result) > 0


# ----------------------------------------------------------
# Summary
# ----------------------------------------------------------

def test_summary(engine):

    engine.prepare()

    engine.keep_latest_year()

    engine.remove_duplicates()

    result = engine.apply_filters()

    result = engine.calculate_composite_score(result)

    summary = engine.screening_summary(result)

    assert isinstance(summary, dict)

    assert "total_companies" in summary

    assert "selected_companies" in summary


# ----------------------------------------------------------
# Export
# ----------------------------------------------------------

def test_export(engine):

    engine.prepare()

    engine.keep_latest_year()

    engine.remove_duplicates()

    result = engine.apply_filters()

    result = engine.calculate_composite_score(result)

    engine.export_excel(

        result,

        OUTPUT,

    )

    assert OUTPUT.exists()


# ----------------------------------------------------------
# Run Pipeline
# ----------------------------------------------------------

def test_run(engine):

    result = engine.run(

        output_file=OUTPUT,

    )

    assert isinstance(result, pd.DataFrame)

    assert len(result) > 0

    assert OUTPUT.exists()


# ----------------------------------------------------------
# Missing Report
# ----------------------------------------------------------

def test_missing_report(engine):

    engine.prepare()

    report = engine.missing_value_report()

    assert isinstance(report, pd.DataFrame)

    assert "column" in report.columns

    assert "missing" in report.columns


# ----------------------------------------------------------
# Dataset Summary
# ----------------------------------------------------------

def test_dataset_summary(engine):

    engine.prepare()

    summary = engine.dataset_summary()

    assert summary["rows"] > 0

    assert summary["columns"] > 0


# ----------------------------------------------------------
# Available Filters
# ----------------------------------------------------------

def test_available_filters(engine):

    filters = engine.available_filters()

    assert isinstance(filters, dict)

    assert "Financial Ratios" in filters


# ----------------------------------------------------------
# Invalid Dataset
# ----------------------------------------------------------

def test_invalid_dataset():

    with pytest.raises(Exception):

        bad = ScreenerEngine(

            ratios_path="abc.xlsx",

            market_cap_path="xyz.xlsx",

            sectors_path="1.xlsx",

            peer_groups_path="2.xlsx",

            config_path="bad.yaml",

        )

        bad.prepare()