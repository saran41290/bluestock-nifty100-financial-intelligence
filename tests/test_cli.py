"""
Tests for src.screener.cli
"""

from pathlib import Path
from unittest.mock import MagicMock

import argparse
import pytest
import pandas as pd
import src.screener.cli as cli


# ---------------------------------------------------------
# Mock Engine
# ---------------------------------------------------------


class MockEngine:

    def __init__(self):

        self.config = None

    def load_config(self):
        pass

    def load_data(self):
        pass

    def validate(self):
        pass

    def build_master_dataframe(self):
        pass

    def keep_latest_year(self):
        pass

    def remove_duplicates(self):
        pass

    def apply_filters(self):

        return pd.DataFrame(
        {
            "company": [
                "ABC",
                "XYZ",
                "PQR",
                "LMN",
                "DEF",
            ],
            "composite_score": [
                95,
                92,
                90,
                88,
                85,
            ],
        }
    )

    def calculate_composite_score(self, df):

        return df

    def sort_results(self, df):

        return df.sort_values(
        "composite_score",
        ascending=False,
    )

    def export_excel(self, df, output):

        Path(output).touch()

    def screening_summary(self, df):

        return {

            "total_companies": 92,

            "selected_companies": 11,

            "selection_percentage": 11.96,

            "average_composite_score": 23.78,

            "sector_distribution": {

                "IT": 2,

                "Finance": 3,

            },

        }


# ---------------------------------------------------------
# Mock Preset
# ---------------------------------------------------------


class MockPreset:

    name = "Buffett"

    filters = []

    sort_by = "composite_score"

    ascending = False


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------


@pytest.fixture
def mock_engine(monkeypatch):

    monkeypatch.setattr(

        cli,

        "create_engine",

        lambda: MockEngine(),

    )


@pytest.fixture
def mock_presets(monkeypatch):

    monkeypatch.setattr(

        cli,

        "get_preset",

        lambda name: MockPreset(),

    )

    monkeypatch.setattr(

        cli,

        "list_presets",

        lambda: [

            "Buffett",

            "Peter Lynch",

            "Benjamin Graham",

        ],

    )


# ---------------------------------------------------------
# build_parser
# ---------------------------------------------------------


def test_build_parser():

    parser = cli.build_parser()

    assert isinstance(

        parser,

        argparse.ArgumentParser,

    )


# ---------------------------------------------------------
# list-presets
# ---------------------------------------------------------


def test_list_presets(

    mock_presets,

    capsys,

):

    args = MagicMock()

    cli.cmd_list_presets(args)

    output = capsys.readouterr().out

    assert "Buffett" in output

    assert "Peter Lynch" in output

    assert "Benjamin Graham" in output


# ---------------------------------------------------------
# validate-config
# ---------------------------------------------------------


def test_validate(

    mock_engine,

    capsys,

):

    args = MagicMock()

    cli.cmd_validate(args)

    output = capsys.readouterr().out

    assert "Configuration is valid" in output


# ---------------------------------------------------------
# preview
# ---------------------------------------------------------


def test_preview(

    mock_engine,

    mock_presets,

    capsys,

):

    args = MagicMock()

    args.preset = "Buffett"

    args.rows = 5

    cli.cmd_preview(args)

    output = capsys.readouterr().out

    assert "Top 5 Companies" in output

    # ---------------------------------------------------------
# run
# ---------------------------------------------------------


def test_run_with_preset(

    mock_engine,

    mock_presets,

    tmp_path,

    capsys,

):

    args = MagicMock()

    args.preset = "Buffett"

    args.output = tmp_path / "screening.xlsx"

    cli.cmd_run(args)

    assert args.output.exists()

    output = capsys.readouterr().out

    assert "Screening Summary" in output

    assert "Results exported" in output


# ---------------------------------------------------------
# run (yaml config)
# ---------------------------------------------------------


def test_run_without_preset(

    monkeypatch,

    tmp_path,

    capsys,

):

    engine = MockEngine()

    engine.load_config = MagicMock()

    monkeypatch.setattr(

        cli,

        "create_engine",

        lambda: engine,

    )

    args = MagicMock()

    args.preset = None

    args.output = tmp_path / "screening.xlsx"

    cli.cmd_run(args)

    engine.load_config.assert_called_once()

    assert args.output.exists()

    output = capsys.readouterr().out

    assert "Screening Summary" in output


# ---------------------------------------------------------
# export preset
# ---------------------------------------------------------


def test_export_preset(

    mock_presets,

    monkeypatch,

    tmp_path,

):

    output = tmp_path / "buffett.yaml"

    save_mock = MagicMock()

    monkeypatch.setattr(

        cli,

        "save_preset_yaml",

        save_mock,

    )

    args = MagicMock()

    args.preset = "Buffett"

    args.output = output

    cli.cmd_export(args)

    save_mock.assert_called_once()


# ---------------------------------------------------------
# execute
# ---------------------------------------------------------


def test_execute():

    called = []

    def fn(args):

        called.append(True)

    args = MagicMock()

    args.func = fn

    cli.execute(args)

    assert called == [True]


# ---------------------------------------------------------
# main success
# ---------------------------------------------------------


def test_main_success(

    monkeypatch,

):

    parser = MagicMock()

    args = MagicMock()

    args.func = lambda _: None

    parser.parse_args.return_value = args

    monkeypatch.setattr(

        cli,

        "build_parser",

        lambda: parser,

    )

    monkeypatch.setattr(

        cli,

        "extend_parser",

        lambda p: p,

    )

    assert cli.main([]) == 0


# ---------------------------------------------------------
# keyboard interrupt
# ---------------------------------------------------------


def test_main_keyboard_interrupt(

    monkeypatch,

):

    def interrupt(_):

        raise KeyboardInterrupt

    parser = MagicMock()

    args = MagicMock()

    args.func = interrupt

    parser.parse_args.return_value = args

    monkeypatch.setattr(

        cli,

        "build_parser",

        lambda: parser,

    )

    monkeypatch.setattr(

        cli,

        "extend_parser",

        lambda p: p,

    )

    assert cli.main([]) == 130


# ---------------------------------------------------------
# generic exception
# ---------------------------------------------------------


def test_main_exception(

    monkeypatch,

):

    def explode(_):

        raise RuntimeError("boom")

    parser = MagicMock()

    args = MagicMock()

    args.func = explode

    parser.parse_args.return_value = args

    monkeypatch.setattr(

        cli,

        "build_parser",

        lambda: parser,

    )

    monkeypatch.setattr(

        cli,

        "extend_parser",

        lambda p: p,

    )

    assert cli.main([]) == 1

    # ---------------------------------------------------------
# Invalid preset
# ---------------------------------------------------------


def test_preview_invalid_preset(

    monkeypatch,

):

    monkeypatch.setattr(

        cli,

        "get_preset",

        MagicMock(

            side_effect=ValueError(

                "Unknown preset"

            )

        ),

    )

    args = MagicMock()

    args.preset = "Invalid"

    args.rows = 5

    with pytest.raises(ValueError):

        cli.cmd_preview(args)


# ---------------------------------------------------------
# run invalid preset
# ---------------------------------------------------------


def test_run_invalid_preset(

    monkeypatch,

    tmp_path,

):

    monkeypatch.setattr(

        cli,

        "get_preset",

        MagicMock(

            side_effect=ValueError(

                "Unknown preset"

            )

        ),

    )

    monkeypatch.setattr(

        cli,

        "create_engine",

        lambda: MockEngine(),

    )

    args = MagicMock()

    args.preset = "Invalid"

    args.output = tmp_path / "screening.xlsx"

    with pytest.raises(ValueError):

        cli.cmd_run(args)


# ---------------------------------------------------------
# export invalid preset
# ---------------------------------------------------------


def test_export_invalid_preset(

    monkeypatch,

    tmp_path,

):

    monkeypatch.setattr(

        cli,

        "get_preset",

        MagicMock(

            side_effect=KeyError(

                "Unknown preset"

            )

        ),

    )

    args = MagicMock()

    args.preset = "Invalid"

    args.output = tmp_path / "preset.yaml"

    with pytest.raises(KeyError):

        cli.cmd_export(args)


# ---------------------------------------------------------
# apply preset
# ---------------------------------------------------------


def test_apply_preset(

    mock_engine,

    mock_presets,

):

    engine = MockEngine()

    cli.apply_preset(

        engine,

        "Buffett",

    )

    assert engine.config is not None

    assert engine.config.sort_by == "composite_score"

    assert engine.config.ascending is False


# ---------------------------------------------------------
# header helper
# ---------------------------------------------------------


def test_header(

    capsys,

):

    cli.header(

        "Demo"

    )

    output = capsys.readouterr().out

    assert "Demo" in output


# ---------------------------------------------------------
# success helper
# ---------------------------------------------------------


def test_success(

    capsys,

):

    cli.success(

        "Done"

    )

    output = capsys.readouterr().out

    assert "Done" in output


# ---------------------------------------------------------
# error helper
# ---------------------------------------------------------


def test_error(

    capsys,

):

    cli.error(

        "Failed"

    )

    output = capsys.readouterr().out

    assert "Failed" in output


# ---------------------------------------------------------
# parser commands
# ---------------------------------------------------------


def test_parser_has_commands():

    parser = cli.build_parser()

    parser = cli.extend_parser(

        parser

    )

    actions = [

        action

        for action in parser._actions

        if isinstance(

            action,

            argparse._SubParsersAction,

        )

    ]

    assert len(actions) == 1

    names = set(

        actions[0].choices.keys()

    )

    assert "run" in names

    assert "preview" in names

    assert "list-presets" in names

    assert "validate-config" in names

    assert "export-preset" in names


# ---------------------------------------------------------
# parser rejects unknown command
# ---------------------------------------------------------


def test_unknown_command():

    parser = cli.extend_parser(

        cli.build_parser()

    )

    with pytest.raises(

        SystemExit

    ):

        parser.parse_args(

            [

                "does-not-exist",

            ]

        )


# ---------------------------------------------------------
# output directory auto-create
# ---------------------------------------------------------


def test_output_directory_created(

    mock_engine,

    mock_presets,

    tmp_path,

):

    output = (

        tmp_path /

        "reports" /

        "screening.xlsx"

    )

    args = MagicMock()

    args.preset = "Buffett"

    args.output = output

    cli.cmd_run(

        args

    )

    assert output.exists()


# ---------------------------------------------------------
# execute propagates exceptions
# ---------------------------------------------------------


def test_execute_exception():

    def fn(_):

        raise RuntimeError(

            "boom"

        )

    args = MagicMock()

    args.func = fn

    with pytest.raises(

        RuntimeError

    ):

        cli.execute(

            args

        )


# ---------------------------------------------------------
# parser help
# ---------------------------------------------------------


def test_help(

    capsys,

):

    parser = cli.extend_parser(

        cli.build_parser()

    )

    with pytest.raises(

        SystemExit

    ):

        parser.parse_args(

            [

                "--help",

            ]

        )

    output = capsys.readouterr().out

    assert "usage:" in output.lower()


# ---------------------------------------------------------
# parser run help
# ---------------------------------------------------------


def test_run_help(

    capsys,

):

    parser = cli.extend_parser(

        cli.build_parser()

    )

    with pytest.raises(

        SystemExit

    ):

        parser.parse_args(

            [

                "run",

                "--help",

            ]

        )

    output = capsys.readouterr().out

    assert "output" in output.lower()


# ---------------------------------------------------------
# CLI module smoke test
# ---------------------------------------------------------


def test_cli_module_import():

    assert cli is not None