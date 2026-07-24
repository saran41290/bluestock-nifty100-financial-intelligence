"""
==========================================================
test_peer_integration.py

Integration Tests for PeerAnalyticsEngine

Sprint 3
==========================================================
"""

from pathlib import Path

import pandas as pd
import pytest

from src.analytics.peer import PeerAnalyticsEngine


# ==========================================================
# FIXTURE
# ==========================================================

@pytest.fixture
def integration_engine():

    return PeerAnalyticsEngine(
        peer_group_path="supporting_datasets/peer_groups.xlsx",
    )


# ==========================================================
# DATABASE
# ==========================================================

def test_database_connection(
    integration_engine,
):

    integration_engine.connect()

    assert integration_engine.db.connection is not None

    integration_engine.close()


def test_load_financial_ratios(
    integration_engine,
):

    integration_engine.connect()

    integration_engine.load_financial_ratios()

    assert len(
        integration_engine.financial_df
    ) > 0

    integration_engine.close()


def test_load_companies(
    integration_engine,
):

    integration_engine.connect()

    integration_engine.load_companies()

    assert len(
        integration_engine.company_df
    ) > 0

    integration_engine.close()


def test_load_peer_groups(
    integration_engine,
):

    integration_engine.load_peer_groups()

    assert len(
        integration_engine.peer_df
    ) > 0


# ==========================================================
# PIPELINE
# ==========================================================

def test_prepare_pipeline(
    integration_engine,
):

    integration_engine.prepare()

    assert integration_engine.master_df is not None

    integration_engine.close()


def test_keep_latest_year(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    years = integration_engine.master_df.groupby(
        "company_id"
    )["year"].nunique()

    assert years.max() == 1

    integration_engine.close()


def test_remove_duplicates(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.remove_duplicates()

    duplicates = integration_engine.master_df.duplicated(
        subset="company_id"
    ).sum()

    assert duplicates == 0

    integration_engine.close()


# ==========================================================
# ANALYTICS
# ==========================================================

def test_compute_peer_percentiles(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.compute_peer_percentiles()

    assert (
        "return_on_equity_pct_percentile"
        in integration_engine.master_df.columns
    )

    integration_engine.close()


def test_compute_peer_scores(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.compute_peer_percentiles()

    integration_engine.compute_peer_scores()

    assert "peer_score" in integration_engine.master_df.columns

    integration_engine.close()


def test_peer_rank_exists(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.compute_peer_percentiles()

    integration_engine.compute_peer_scores()

    assert "peer_rank" in integration_engine.master_df.columns

    integration_engine.close()


# ==========================================================
# EXPORTS
# ==========================================================

def test_excel_export(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.compute_peer_percentiles()

    integration_engine.compute_peer_scores()

    integration_engine.export_excel()

    assert (
        integration_engine.output_dir /
        "peer_comparison.xlsx"
    ).exists()

    integration_engine.close()


def test_sqlite_export(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.compute_peer_percentiles()

    integration_engine.compute_peer_scores()

    integration_engine.execute_transaction()

    integration_engine.close()


# ==========================================================
# REPORTS
# ==========================================================

def test_generate_reports(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.compute_peer_percentiles()

    integration_engine.compute_peer_scores()

    integration_engine.generate_reports()

    assert integration_engine.chart_dir.exists()

    integration_engine.close()


def test_generate_all_radar_charts(
    integration_engine,
):

    integration_engine.prepare()

    integration_engine.keep_latest_year()

    integration_engine.compute_peer_percentiles()

    integration_engine.compute_peer_scores()

    integration_engine.generate_all_radar_charts()

    pngs = list(
        integration_engine.chart_dir.glob("*.png")
    )

    assert len(pngs) > 0

    integration_engine.close()


# ==========================================================
# FULL RUN
# ==========================================================

def test_full_run(
    integration_engine,
):

    df = integration_engine.run()

    assert isinstance(
        df,
        pd.DataFrame,
    )


def test_full_run_contains_scores(
    integration_engine,
):

    df = integration_engine.run()

    assert "peer_score" in df.columns


def test_full_run_contains_rank(
    integration_engine,
):

    df = integration_engine.run()

    assert "peer_rank" in df.columns


def test_full_run_not_empty(
    integration_engine,
):

    df = integration_engine.run()

    assert len(df) > 0


# ==========================================================
# SUMMARY
# ==========================================================

def test_summary_after_run(
    integration_engine,
):

    integration_engine.run()

    summary = integration_engine.summary()

    assert summary["companies"] > 0


def test_dataset_summary_after_run(
    integration_engine,
):

    integration_engine.run()

    summary = integration_engine.dataset_summary()

    assert summary["rows"] > 0


def test_top_companies(
    integration_engine,
):

    integration_engine.run()

    df = integration_engine.top_companies(10)

    assert len(df) == 10


# ==========================================================
# CLEANUP
# ==========================================================

def test_close_database(
    integration_engine,
):

    integration_engine.connect()

    integration_engine.close()

    assert integration_engine.db.connection is None