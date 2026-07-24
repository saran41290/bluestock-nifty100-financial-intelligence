"""
=========================================================
NIFTY100 Platform
Sprint 3

Command Line Interface

Author : Saranya
=========================================================
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .engine import ScreenerConfig
from .engine import ScreenerEngine
from .presets import (
    get_preset,
    list_presets,
    save_preset_yaml,
)

# ---------------------------------------------------------
# Logger
# ---------------------------------------------------------

logger = logging.getLogger(__name__)

if not logger.handlers:

    logging.basicConfig(

        level=logging.INFO,

        format="%(asctime)s | %(levelname)s | %(message)s",

    )

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

DATA = ROOT / "supporting_datasets"

CONFIG = ROOT / "config"

OUTPUT = ROOT / "output"

DEFAULT_CONFIG = CONFIG / "screener_config.yaml"


# ---------------------------------------------------------
# Engine Factory
# ---------------------------------------------------------


def create_engine() -> ScreenerEngine:

    return ScreenerEngine(

        ratios_path=DATA / "financial_ratios.xlsx",

        market_cap_path=DATA / "market_cap.xlsx",

        sectors_path=DATA / "sectors.xlsx",

        peer_groups_path=DATA / "peer_groups.xlsx",

        config_path=DEFAULT_CONFIG,

    )


# ---------------------------------------------------------
# Apply Preset
# ---------------------------------------------------------


def apply_preset(
    engine: ScreenerEngine,
    preset_name: str,
):

    preset = get_preset(
        preset_name
    )

    engine.config = ScreenerConfig(

        filters=preset.filters,

        sort_by=preset.sort_by,

        ascending=preset.ascending,

    )

    logger.info(

        "Loaded preset : %s",

        preset.name,

    )


# ---------------------------------------------------------
# Pretty Console Output
# ---------------------------------------------------------


def header(title: str):

    print()

    print("=" * 70)

    print(title)

    print("=" * 70)


def success(msg: str):

    print(f"✔ {msg}")


def error(msg: str):

    print(f"✖ {msg}")


# ---------------------------------------------------------
# Commands
# ---------------------------------------------------------


def cmd_list_presets(_):

    header("Available Presets")

    for preset in list_presets():

        print(f" • {preset}")

    print()


def cmd_validate(_):

    engine = create_engine()

    engine.load_config()

    engine.load_data()

    engine.validate()

    success("Configuration is valid.")


def cmd_preview(args):

    engine = create_engine()

    engine.load_data()

    engine.validate()

    engine.build_master_dataframe()

    apply_preset(

        engine,

        args.preset,

    )

    engine.keep_latest_year()

    engine.remove_duplicates()

    screened = engine.apply_filters()

    screened = engine.calculate_composite_score(

        screened

    )

    screened = engine.sort_results(

        screened

    )

    header(

        f"Top {args.rows} Companies"

    )

    print(

        screened.head(args.rows)

    )


# ---------------------------------------------------------
# Parser
# ---------------------------------------------------------


def build_parser():

    parser = argparse.ArgumentParser(

        prog="screen",

        description="NIFTY100 Screener",

    )

    sub = parser.add_subparsers(

        dest="command",

        required=True,

    )

    # ---------------------------------------------
    # list-presets
    # ---------------------------------------------

    p = sub.add_parser(

        "list-presets",

        help="Show all presets",

    )

    p.set_defaults(

        func=cmd_list_presets,

    )

    # ---------------------------------------------
    # validate-config
    # ---------------------------------------------

    p = sub.add_parser(

        "validate-config",

        help="Validate datasets",

    )

    p.set_defaults(

        func=cmd_validate,

    )

    # ---------------------------------------------
    # preview
    # ---------------------------------------------

    p = sub.add_parser(

        "preview",

        help="Preview screening",

    )

    p.add_argument(

        "--preset",

        required=True,

    )

    p.add_argument(

        "--rows",

        default=10,

        type=int,

    )

    p.set_defaults(

        func=cmd_preview,

    )

    return parser

# ---------------------------------------------------------
# Run Screener
# ---------------------------------------------------------


def cmd_run(args):

    engine = create_engine()

    engine.load_data()

    engine.validate()

    engine.build_master_dataframe()

    if args.preset:

        apply_preset(

            engine,

            args.preset,

        )

    else:

        engine.load_config()

    engine.keep_latest_year()

    engine.remove_duplicates()

    screened = engine.apply_filters()

    screened = engine.calculate_composite_score(
        screened
    )

    screened = engine.sort_results(
        screened
    )

    output = Path(args.output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    engine.export_excel(
        screened,
        output,
    )

    summary = engine.screening_summary(
        screened
    )

    header("Screening Summary")

    print(f"Total Companies     : {summary['total_companies']}")
    print(f"Selected Companies  : {summary['selected_companies']}")
    print(f"Selection %         : {summary['selection_percentage']}")
    print(f"Average Score       : {summary['average_composite_score']}")

    if "sector_distribution" in summary:

        print()

        print("Sector Distribution")

        print("-------------------")

        for sector, count in summary[
            "sector_distribution"
        ].items():

            print(f"{sector:<25} {count}")

    print()

    success(
        f"Results exported to\n{output}"
    )


# ---------------------------------------------------------
# Export Preset
# ---------------------------------------------------------


def cmd_export(args):

    preset = get_preset(
        args.preset
    )

    output = Path(
        args.output
    )

    save_preset_yaml(
        preset,
        output,
    )

    success(
        f"Preset exported to\n{output}"
    )


# ---------------------------------------------------------
# Extend Parser
# ---------------------------------------------------------


def extend_parser(parser):

    sub = next(

        action

        for action in parser._actions

        if isinstance(
            action,
            argparse._SubParsersAction,
        )

    )

    # ---------------------------------------------
    # run
    # ---------------------------------------------

    p = sub.add_parser(

        "run",

        help="Run screener",

    )

    p.add_argument(

        "--preset",

        help="Built-in preset",

    )

    p.add_argument(

        "--output",

        default=str(
            OUTPUT /
            "screening.xlsx"
        ),

        help="Excel output",

    )

    p.set_defaults(

        func=cmd_run,

    )

    # ---------------------------------------------
    # export-preset
    # ---------------------------------------------

    p = sub.add_parser(

        "export-preset",

        help="Export preset YAML",

    )

    p.add_argument(

        "--preset",

        required=True,

    )

    p.add_argument(

        "--output",

        required=True,

    )

    p.set_defaults(

        func=cmd_export,

    )

    return parser


# ---------------------------------------------------------
# Execute
# ---------------------------------------------------------


def execute(args):

    args.func(args)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------


def main(argv=None):

    parser = extend_parser(

        build_parser()

    )

    args = parser.parse_args(argv)

    try:

        execute(args)

        return 0

    except KeyboardInterrupt:

        print()

        error("Interrupted")

        return 130

    except Exception as exc:

        logger.exception(exc)

        error(str(exc))

        return 1


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------


if __name__ == "__main__":

    sys.exit(

        main()

    )