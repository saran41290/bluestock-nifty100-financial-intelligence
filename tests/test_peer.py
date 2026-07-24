"""
==========================================================
test_peer.py

Unit tests for PeerAnalyticsEngine

Sprint 3
==========================================================
"""

from pathlib import Path

import pandas as pd
import pytest
from src.analytics.peer import PEER_METRICS
from src.analytics.peer import (
    PeerAnalyticsEngine,
    PeerAnalyticsException,
    PeerValidationError,
)
# ==========================================================
# FIXTURES
# ==========================================================

@pytest.fixture
def engine(tmp_path):

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    charts = output_dir / "charts"
    charts.mkdir()

    reports = output_dir / "reports"
    reports.mkdir()

    engine = PeerAnalyticsEngine(

        peer_group_path=tmp_path / "peer_groups.xlsx",

        output_dir=output_dir,

    )

    return engine
@pytest.fixture
def sample_financial_df():

    return pd.DataFrame(

        {

            "company_id": [1, 2, 3],

            "year": [2024, 2024, 2024],

            "return_on_equity_pct": [18, 25, 30],

            "return_on_capital_employed_pct": [

                22,

                27,

                33,

            ],

            "net_profit_margin_pct": [

                15,

                18,

                22,

            ],

            "debt_to_equity": [

                0.80,

                0.30,

                0.50,

            ],

            "interest_coverage": [

                7,

                10,

                14,

            ],

            "asset_turnover": [

                1.2,

                1.4,

                1.7,

            ],

            "free_cash_flow": [

                110,

                250,

                300,

            ],

            "revenue_cagr_5yr": [

                9,

                12,

                18,

            ],

            "pat_cagr_5yr": [

                8,

                14,

                20,

            ],

            "eps_cagr_5yr": [

                10,

                16,

                22,

            ],

        }

    )
@pytest.fixture
def sample_company_df():

    return pd.DataFrame(

        {

            "company_id": [1, 2, 3],

            "company_name": [

                "TCS",

                "Infosys",

                "Wipro",

            ],

        }

    )
@pytest.fixture
def sample_peer_df():

    return pd.DataFrame(

        {

            "company_id": [

                1,

                2,

                3,

            ],

            "peer_group_name": [

                "IT",

                "IT",

                "IT",

            ],

            "is_benchmark": [

                False,

                True,

                False,

            ],

        }

    )
@pytest.fixture
def prepared_engine(
    engine,
    sample_financial_df,
    sample_company_df,
    sample_peer_df,
):

    engine.financial_df = sample_financial_df
    engine.company_df = sample_company_df
    engine.peer_df = sample_peer_df

    return engine
# ==========================================================
# INITIALIZATION
# ==========================================================

def test_engine_created(engine):

    assert engine is not None
def test_output_directory_exists(engine):

    assert engine.output_dir.exists()

def test_chart_directory_exists(engine):

    assert engine.chart_dir.exists()
def test_reports_directory_exists(engine):

    assert engine.report_dir.exists()
def test_master_dataframe_initially_none(engine):

    assert engine.master_df is None
def test_financial_dataframe_initially_none(engine):

    assert engine.financial_df is None
def test_company_dataframe_initially_none(engine):

    assert engine.company_df is None
def test_peer_dataframe_initially_none(engine):

    assert engine.peer_df is None
# ==========================================================
# VALIDATION
# ==========================================================

def test_validate_success(

    engine,

    sample_financial_df,

    sample_company_df,

    sample_peer_df,

):

    engine.financial_df = sample_financial_df

    engine.company_df = sample_company_df

    engine.peer_df = sample_peer_df

    engine.validate()
def test_validate_without_financial_df(engine):

    with pytest.raises(

        PeerValidationError

    ):

        engine.validate()
def test_validate_missing_company_column(

    engine,

    sample_financial_df,

    sample_company_df,

    sample_peer_df,

):

    sample_company_df = sample_company_df.drop(

        columns=["company_name"]

    )

    engine.financial_df = sample_financial_df

    engine.company_df = sample_company_df

    engine.peer_df = sample_peer_df

    with pytest.raises(

        PeerValidationError

    ):

        engine.validate()
def test_validate_missing_peer_group(

    engine,

    sample_financial_df,

    sample_company_df,

    sample_peer_df,

):

    sample_peer_df = sample_peer_df.drop(

        columns=["peer_group_name"]

    )

    engine.financial_df = sample_financial_df

    engine.company_df = sample_company_df

    engine.peer_df = sample_peer_df

    with pytest.raises(

        PeerValidationError

    ):

        engine.validate()
# ==========================================================
# MASTER DATAFRAME
# ==========================================================

def test_build_master_dataframe(

    engine,

    sample_financial_df,

    sample_company_df,

    sample_peer_df,

):

    engine.financial_df = sample_financial_df

    engine.company_df = sample_company_df

    engine.peer_df = sample_peer_df

    engine.build_master_dataframe()

    assert engine.master_df is not None
def test_master_dataframe_row_count(

    engine,

    sample_financial_df,

    sample_company_df,

    sample_peer_df,

):

    engine.financial_df = sample_financial_df

    engine.company_df = sample_company_df

    engine.peer_df = sample_peer_df

    df = engine.build_master_dataframe()

    assert len(df) == 3
def test_master_dataframe_contains_company_name(

    engine,

    sample_financial_df,

    sample_company_df,

    sample_peer_df,

):

    engine.financial_df = sample_financial_df

    engine.company_df = sample_company_df

    engine.peer_df = sample_peer_df

    df = engine.build_master_dataframe()

    assert "company_name" in df.columns
def test_master_dataframe_contains_peer_group(

    engine,

    sample_financial_df,

    sample_company_df,

    sample_peer_df,

):

    engine.financial_df = sample_financial_df

    engine.company_df = sample_company_df

    engine.peer_df = sample_peer_df

    df = engine.build_master_dataframe()

    assert "peer_group_name" in df.columns
def test_build_master_dataframe_without_inputs(

    engine,

):

    with pytest.raises(

        PeerAnalyticsException

    ):

        engine.build_master_dataframe()
# ==========================================================
# DATA PREPARATION
# ==========================================================

def test_keep_latest_year_single_year(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    df = prepared_engine.keep_latest_year()

    assert len(df) == 3
def test_keep_latest_year_multiple_years(
    prepared_engine,
):

    extra = prepared_engine.financial_df.copy()

    extra["year"] = 2023

    prepared_engine.financial_df = pd.concat(

        [

            prepared_engine.financial_df,

            extra,

        ],

        ignore_index=True,

    )

    prepared_engine.build_master_dataframe()

    df = prepared_engine.keep_latest_year()

    assert len(df) == 3

    assert df["year"].eq(2024).all()
def test_keep_latest_year_returns_dataframe(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    df = prepared_engine.keep_latest_year()

    assert isinstance(df, pd.DataFrame)
def test_keep_latest_year_without_master_dataframe(
    engine,
):

    with pytest.raises(
        PeerAnalyticsException
    ):

        engine.keep_latest_year()
# ==========================================================
# DUPLICATE REMOVAL
# ==========================================================

def test_remove_duplicates(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    duplicate = prepared_engine.master_df.iloc[[0]]

    prepared_engine.master_df = pd.concat(

        [

            prepared_engine.master_df,

            duplicate,

        ],

        ignore_index=True,

    )

    assert len(prepared_engine.master_df) == 4

    prepared_engine.remove_duplicates()

    assert len(prepared_engine.master_df) == 3
def test_remove_duplicates_no_duplicates(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    before = len(prepared_engine.master_df)

    prepared_engine.remove_duplicates()

    after = len(prepared_engine.master_df)

    assert before == after
def test_remove_duplicates_without_master_dataframe(
    engine,
):

    with pytest.raises(
        PeerAnalyticsException
    ):

        engine.remove_duplicates()
# ==========================================================
# PREPARE
# ==========================================================

def test_prepare_calls_validation(
    monkeypatch,
    engine,
):

    called = False

    def fake_validate():

        nonlocal called

        called = True

    monkeypatch.setattr(
        engine,
        "connect",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_financial_ratios",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_companies",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_peer_groups",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "validate",
        fake_validate,
    )

    monkeypatch.setattr(
        engine,
        "build_master_dataframe",
        lambda: None,
    )

    engine.prepare()

    assert called
def test_prepare_calls_build_master_dataframe(
    monkeypatch,
    engine,
):

    called = False

    def fake_build():

        nonlocal called

        called = True

    monkeypatch.setattr(
        engine,
        "connect",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_financial_ratios",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_companies",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_peer_groups",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "validate",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "build_master_dataframe",
        fake_build,
    )

    engine.prepare()

    assert called
def test_prepare_propagates_validation_error(
    monkeypatch,
    engine,
):

    monkeypatch.setattr(
        engine,
        "connect",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_financial_ratios",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_companies",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_peer_groups",
        lambda: None,
    )

    def raise_error():

        raise PeerValidationError(
            "Validation failed"
        )

    monkeypatch.setattr(
        engine,
        "validate",
        raise_error,
    )

    with pytest.raises(
        PeerValidationError
    ):

        engine.prepare()
def test_prepare_pipeline_order(
    monkeypatch,
    engine,
):

    calls = []

    monkeypatch.setattr(
        engine,
        "connect",
        lambda: calls.append("connect"),
    )

    monkeypatch.setattr(
        engine,
        "load_financial_ratios",
        lambda: calls.append("financial"),
    )

    monkeypatch.setattr(
        engine,
        "load_companies",
        lambda: calls.append("companies"),
    )

    monkeypatch.setattr(
        engine,
        "load_peer_groups",
        lambda: calls.append("peer"),
    )

    monkeypatch.setattr(
        engine,
        "validate",
        lambda: calls.append("validate"),
    )

    monkeypatch.setattr(
        engine,
        "build_master_dataframe",
        lambda: calls.append("master"),
    )

    engine.prepare()

    assert calls == [

        "connect",

        "financial",

        "companies",

        "peer",

        "validate",

        "master",

    ]
def test_prepare_returns_none(
    monkeypatch,
    engine,
):

    monkeypatch.setattr(
        engine,
        "connect",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_financial_ratios",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_companies",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "load_peer_groups",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "validate",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "build_master_dataframe",
        lambda: None,
    )

    assert engine.prepare() is None
# ==========================================================
# PERCENTILE CALCULATION
# ==========================================================

def test_compute_metric_percentile_higher_is_better():

    values = pd.Series([10, 20, 30])

    result = PeerAnalyticsEngine.compute_metric_percentile(
        values,
        higher_is_better=True,
    )

    assert result.max() == 100.0
    assert result.min() > 0
def test_compute_metric_percentile_lower_is_better():

    values = pd.Series([10, 20, 30])

    result = PeerAnalyticsEngine.compute_metric_percentile(
        values,
        higher_is_better=False,
    )

    assert result.iloc[0] > result.iloc[1]
    assert result.iloc[1] > result.iloc[2]
def test_percentile_contains_no_nan():

    values = pd.Series([10, 20, 30])

    result = PeerAnalyticsEngine.compute_metric_percentile(
        values,
        True,
    )

    assert result.notna().all()
def test_percentile_is_between_zero_and_hundred():

    values = pd.Series([5, 8, 11, 25])

    result = PeerAnalyticsEngine.compute_metric_percentile(
        values,
        True,
    )

    assert result.between(0, 100).all()
def test_percentile_handles_nulls():

    values = pd.Series([10, None, 30])

    result = PeerAnalyticsEngine.compute_metric_percentile(
        values,
        True,
    )

    assert len(result) == 3
# ==========================================================
# PEER PERCENTILES
# ==========================================================

def test_compute_peer_percentiles(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    assert "return_on_equity_pct_percentile" in prepared_engine.master_df.columns
def test_peer_percentile_column_created_for_every_metric(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    for metric in PEER_METRICS:

        column = f"{metric.column}_percentile"

        assert column in prepared_engine.master_df.columns
def test_percentiles_are_numeric(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    column = "return_on_equity_pct_percentile"

    assert pd.api.types.is_numeric_dtype(
        prepared_engine.master_df[column]
    )
def test_percentiles_are_not_null(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    column = "return_on_equity_pct_percentile"

    assert prepared_engine.master_df[column].notna().all()
def test_percentiles_between_zero_and_hundred(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    column = "return_on_equity_pct_percentile"

    assert prepared_engine.master_df[column].between(
        0,
        100,
    ).all()
def test_compute_peer_percentiles_without_master_dataframe(
    engine,
):

    with pytest.raises(
        PeerAnalyticsException
    ):

        engine.compute_peer_percentiles()
# ==========================================================
# PEER SCORES
# ==========================================================

def test_compute_peer_scores(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    assert "peer_score" in prepared_engine.master_df.columns
def test_peer_rank_column_created(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    assert "peer_rank" in prepared_engine.master_df.columns
def test_peer_scores_are_numeric(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    assert pd.api.types.is_numeric_dtype(
        prepared_engine.master_df["peer_score"]
    )
def test_peer_scores_not_null(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    assert prepared_engine.master_df[
        "peer_score"
    ].notna().all()
def test_peer_rank_starts_from_one(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    assert prepared_engine.master_df[
        "peer_rank"
    ].min() == 1
def test_peer_score_sorted_descending(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    scores = prepared_engine.master_df.sort_values(
        "peer_score",
        ascending=False,
    )

    assert scores.iloc[0]["peer_score"] >= scores.iloc[-1]["peer_score"]
def test_compute_peer_scores_without_percentiles(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    with pytest.raises(
        PeerAnalyticsException
    ):

        prepared_engine.compute_peer_scores()
def test_compute_peer_scores_returns_dataframe(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    df = prepared_engine.compute_peer_scores()

    assert isinstance(
        df,
        pd.DataFrame,
    )
def test_best_company_receives_rank_one(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    best = prepared_engine.master_df.sort_values(
        "peer_score",
        ascending=False,
    ).iloc[0]

    assert best["peer_rank"] == 1
def test_peer_rank_is_integer(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.compute_peer_percentiles()

    prepared_engine.compute_peer_scores()

    assert pd.api.types.is_integer_dtype(
        prepared_engine.master_df["peer_rank"]
    )
# ==========================================================
# EXPORTS
# ==========================================================

def test_export_sqlite(
    prepared_engine,
):
    prepared_engine.connect()
    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    prepared_engine.execute_transaction()


def test_export_excel(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    prepared_engine.export_excel()

    files = list(
        prepared_engine.output_dir.glob("*.xlsx")
    )

    assert len(files) == 1


def test_export_excel_file_exists(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    prepared_engine.export_excel()

    assert (
        prepared_engine.output_dir /
        "peer_comparison.xlsx"
    ).exists()


def test_export_without_scores(
    engine,
):

    with pytest.raises(
        PeerAnalyticsException
    ):

        engine.export_excel()


# ==========================================================
# RADAR CHARTS
# ==========================================================

def test_generate_radar_chart(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    company = prepared_engine.master_df.iloc[0]

    chart = prepared_engine.generate_radar_chart(
        company["company_id"]
    )

    assert chart.exists()


def test_generate_all_radar_charts(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    prepared_engine.generate_all_radar_charts()

    pngs = list(
        prepared_engine.chart_dir.glob("*.png")
    )

    assert len(pngs) == len(
        prepared_engine.master_df
    )


def test_generate_radar_invalid_company(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    with pytest.raises(
        PeerAnalyticsException
    ):

        prepared_engine.generate_radar_chart(
            -999
        )


# ==========================================================
# SUMMARY
# ==========================================================

def test_summary(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    summary = prepared_engine.summary()

    assert isinstance(
        summary,
        dict,
    )


def test_summary_contains_company_count(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    summary = prepared_engine.summary()

    assert "companies" in summary


def test_summary_contains_peer_groups(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    summary = prepared_engine.summary()

    assert "peer_groups" in summary


# ==========================================================
# PREVIEW
# ==========================================================

def test_preview(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    preview = prepared_engine.preview()

    assert isinstance(
        preview,
        pd.DataFrame,
    )


def test_preview_default_rows(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    preview = prepared_engine.preview()

    assert len(preview) <= 5


def test_preview_custom_rows(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    preview = prepared_engine.preview(2)

    assert len(preview) == 2


# ==========================================================
# STATUS
# ==========================================================

def test_status(
    prepared_engine,
):

    status = prepared_engine.status()

    assert isinstance(
        status,
        dict,
    )


def test_status_contains_master_ready(
    prepared_engine,
):

    status = prepared_engine.status()

    assert "master_ready" in status


# ==========================================================
# RESET
# ==========================================================

def test_reset(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    prepared_engine.reset()

    assert prepared_engine.master_df is None


def test_reset_financial_dataframe(
    prepared_engine,
):

    prepared_engine.reset()

    assert prepared_engine.financial_df is None


def test_reset_company_dataframe(
    prepared_engine,
):

    prepared_engine.reset()

    assert prepared_engine.company_df is None


def test_reset_peer_dataframe(
    prepared_engine,
):

    prepared_engine.reset()

    assert prepared_engine.peer_df is None


# ==========================================================
# __repr__
# ==========================================================

def test_repr(
    prepared_engine,
):

    text = repr(
        prepared_engine
    )

    assert "PeerAnalyticsEngine" in text


# ==========================================================
# AVAILABLE METRICS
# ==========================================================

def test_available_metrics():

    metrics = PeerAnalyticsEngine.available_metrics()

    assert isinstance(
        metrics,
        list,
    )


def test_available_metrics_not_empty():

    metrics = PeerAnalyticsEngine.available_metrics()

    assert len(metrics) > 0


# ==========================================================
# DATASET SUMMARY
# ==========================================================

def test_dataset_summary(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    summary = prepared_engine.dataset_summary()

    assert isinstance(
        summary,
        dict,
    )


def test_dataset_summary_contains_rows(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    summary = prepared_engine.dataset_summary()

    assert "rows" in summary


def test_dataset_summary_contains_columns(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()

    summary = prepared_engine.dataset_summary()

    assert "columns" in summary


# ==========================================================
# TOP COMPANIES
# ==========================================================

def test_top_companies(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    df = prepared_engine.top_companies()

    assert isinstance(
        df,
        pd.DataFrame,
    )


def test_top_companies_limit(
    prepared_engine,
):

    prepared_engine.build_master_dataframe()
    prepared_engine.compute_peer_percentiles()
    prepared_engine.compute_peer_scores()

    df = prepared_engine.top_companies(2)

    assert len(df) == 2


# ==========================================================
# RUN PIPELINE
# ==========================================================

def test_run_pipeline(
    monkeypatch,
    engine,
):

    monkeypatch.setattr(
        engine,
        "prepare",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "keep_latest_year",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "remove_duplicates",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "compute_peer_percentiles",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "compute_peer_scores",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "execute_transaction",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "generate_reports",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "close",
        lambda: None,
    )

    engine.master_df = pd.DataFrame({

        "peer_group_name": [],

        "company_id": [],

        "peer_score": [],

    })

    result = engine.run()

    assert isinstance(
        result,
        pd.DataFrame,
    )


def test_run_calls_close(
    monkeypatch,
    engine,
):

    closed = False

    def fake_close():

        nonlocal closed

        closed = True

    monkeypatch.setattr(
        engine,
        "prepare",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "keep_latest_year",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "remove_duplicates",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "compute_peer_percentiles",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "compute_peer_scores",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "execute_transaction",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "generate_reports",
        lambda: None,
    )

    monkeypatch.setattr(
        engine,
        "close",
        fake_close,
    )

    engine.master_df = pd.DataFrame({

        "peer_group_name": [],

        "company_id": [],

        "peer_score": [],

    })

    engine.run()

    assert closed