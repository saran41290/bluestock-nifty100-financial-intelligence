"""
=========================================================
NIFTY100 Platform
Sprint 3 - Equity Screener Engine

Loads all supporting datasets
Creates a master dataframe
Applies configurable screening rules

Author : Saranya
=========================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import yaml

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
# Custom Exceptions
# ---------------------------------------------------------

class ScreenerException(Exception):
    """Base Exception"""


class ConfigurationError(ScreenerException):
    """Configuration Error"""


class ValidationError(ScreenerException):
    """Dataset Validation Error"""


# ---------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------

@dataclass
class FilterRule:
    metric: str
    operator: str
    value: object


@dataclass
class ScreenerConfig:

    filters: List[FilterRule]

    sort_by: str = "composite_score"

    ascending: bool = False


# ---------------------------------------------------------
# Screener Engine
# ---------------------------------------------------------

class ScreenerEngine:

    REQUIRED_RATIO_COLUMNS = [

        "company_id",
        "year",

        "return_on_equity_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",

        "debt_to_equity",
        "interest_coverage",

        "asset_turnover",

        "free_cash_flow_cr",

        "earnings_per_share",

        "book_value_per_share",

        "dividend_payout_ratio_pct",

        "total_debt_cr",

        "cash_from_operations_cr",
    ]

    REQUIRED_MARKET_COLUMNS = [

        "company_id",

        "market_cap_crore",

        "enterprise_value_crore",

        "pe_ratio",

        "pb_ratio",

        "ev_ebitda",

        "dividend_yield_pct",
    ]

    REQUIRED_SECTOR_COLUMNS = [

        "company_id",

        "broad_sector",

        "sub_sector",

        "market_cap_category",
    ]

    REQUIRED_PEER_COLUMNS = [

        "company_id",

        "peer_group_name",

        "is_benchmark",
    ]

    # -----------------------------------------------------

    def __init__(
        self,
        ratios_path: str,
        market_cap_path: str,
        sectors_path: str,
        peer_groups_path: str,
        config_path: str,
    ):

        self.ratios_path = Path(ratios_path)

        self.market_path = Path(market_cap_path)

        self.sectors_path = Path(sectors_path)

        self.peer_path = Path(peer_groups_path)

        self.config_path = Path(config_path)

        self.config: Optional[ScreenerConfig] = None

        self.ratios_df: Optional[pd.DataFrame] = None

        self.market_df: Optional[pd.DataFrame] = None

        self.sector_df: Optional[pd.DataFrame] = None

        self.peer_df: Optional[pd.DataFrame] = None

        self.master_df: Optional[pd.DataFrame] = None

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    def load_config(self):

        logger.info("Loading screener configuration...")

        if not self.config_path.exists():

            raise ConfigurationError(
                f"{self.config_path} not found."
            )

        with open(
            self.config_path,
            "r",
            encoding="utf8",
        ) as file:

            cfg = yaml.safe_load(file)

        filters = []

        for item in cfg.get("filters", []):

            filters.append(

                FilterRule(

                    metric=item["metric"],

                    operator=item["operator"],

                    value=item["value"],
                )
            )

        self.config = ScreenerConfig(

            filters=filters,

            sort_by=cfg.get(
                "sort_by",
                "composite_score",
            ),

            ascending=cfg.get(
                "ascending",
                False,
            ),
        )

        logger.info(
            "Loaded %d filter rules.",
            len(filters),
        )


    def load_preset(
    self,
    preset_name: str,
    ):

        """
        Load configuration from a built-in preset.
        """

        from .presets import get_preset

        preset = get_preset(preset_name)

        self.config = ScreenerConfig(
            filters=preset.filters,
            sort_by=preset.sort_by,
            ascending=preset.ascending,
        )

        logger.info(
            "Loaded preset: %s",
            preset.name,
        )
    # ---------------------------------------------------------
    # Dataset Loading
    # ---------------------------------------------------------

    def load_data(self):

        logger.info("Loading supporting datasets...")

        self.ratios_df = pd.read_excel(
            self.ratios_path
        )

        self.market_df = pd.read_excel(
            self.market_path
        )

        self.sector_df = pd.read_excel(
            self.sectors_path
        )

        self.peer_df = pd.read_excel(
            self.peer_path
        )

        logger.info(
            "Financial Ratios : %d",
            len(self.ratios_df),
        )

        logger.info(
            "Market Cap : %d",
            len(self.market_df),
        )

        logger.info(
            "Sector Mapping : %d",
            len(self.sector_df),
        )

        logger.info(
            "Peer Groups : %d",
            len(self.peer_df),
        )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_columns(
        dataframe: pd.DataFrame,
        required: List[str],
        dataset: str,
    ):

        missing = [
            col
            for col in required
            if col not in dataframe.columns
        ]

        if missing:

            raise ValidationError(

                f"{dataset} missing columns : {missing}"

            )

    def validate(self):

        logger.info("Validating datasets...")

        self._validate_columns(
            self.ratios_df,
            self.REQUIRED_RATIO_COLUMNS,
            "financial_ratios",
        )

        self._validate_columns(
            self.market_df,
            self.REQUIRED_MARKET_COLUMNS,
            "market_cap",
        )

        self._validate_columns(
            self.sector_df,
            self.REQUIRED_SECTOR_COLUMNS,
            "sectors",
        )

        self._validate_columns(
            self.peer_df,
            self.REQUIRED_PEER_COLUMNS,
            "peer_groups",
        )

        logger.info("Validation successful.")

    # ---------------------------------------------------------
    # Master DataFrame
    # ---------------------------------------------------------

    def build_master_dataframe(self):

        logger.info(
            "Building Master DataFrame..."
        )

        df = self.ratios_df.copy()

        market = self.market_df.drop(
            columns=["id", "year"],
            errors="ignore",
        )

        sectors = self.sector_df.drop(
            columns=["id"],
            errors="ignore",
        )

        peers = self.peer_df.drop(
            columns=["id"],
            errors="ignore",
        )

        df = df.merge(

            market,

            how="left",

            on="company_id",

        )

        df = df.merge(

            sectors,

            how="left",

            on="company_id",

        )

        df = df.merge(

            peers,

            how="left",

            on="company_id",

        )

        logger.info(
            "Master dataframe created."
        )

        logger.info(
            "Shape : %s",
            df.shape,
        )

        self.master_df = df

        return df

    # ---------------------------------------------------------
    # Preparation
    # ---------------------------------------------------------

    def prepare(
        self,
        preset=None,
    ):

        self.load_config()
            
        self.load_data()

        self.validate()

        return self.build_master_dataframe()
    
    # ---------------------------------------------------------
    # Comparison Operators
    # ---------------------------------------------------------

    @staticmethod
    def _compare(series, operator, value):

        if operator == ">":
            return series > value

        if operator == ">=":
            return series >= value

        if operator == "<":
            return series < value

        if operator == "<=":
            return series <= value

        if operator == "==":
            return series == value

        if operator == "!=":
            return series != value

        raise ConfigurationError(
            f"Unsupported operator : {operator}"
        )

    # ---------------------------------------------------------
    # Numeric Filter
    # ---------------------------------------------------------

    def _apply_numeric_filter(
        self,
        df: pd.DataFrame,
        column: str,
        operator: str,
        value,
    ) -> pd.DataFrame:

        if column not in df.columns:

            raise ValidationError(
                f"{column} not found."
            )

        mask = self._compare(
            df[column],
            operator,
            value,
        )

        logger.info(
            "%s %s %s -> %d rows",
            column,
            operator,
            value,
            mask.sum(),
        )

        return df.loc[mask].copy()

    # ---------------------------------------------------------
    # Text Filter
    # ---------------------------------------------------------

    def _apply_text_filter(
        self,
        df: pd.DataFrame,
        column: str,
        operator: str,
        value,
    ) -> pd.DataFrame:

        if column not in df.columns:

            raise ValidationError(
                f"{column} not found."
            )

        values = (
            df[column]
            .fillna("")
            .astype(str)
            .str.lower()
        )

        value = str(value).lower()

        if operator == "==":

            mask = values == value

        elif operator == "!=":

            mask = values != value

        elif operator.lower() == "contains":

            mask = values.str.contains(
                value,
                regex=False,
            )

        else:

            raise ConfigurationError(
                f"Invalid text operator : {operator}"
            )

        logger.info(
            "%s %s %s -> %d rows",
            column,
            operator,
            value,
            mask.sum(),
        )

        return df.loc[mask].copy()

    # ---------------------------------------------------------
    # Debt To Equity Filter
    # ---------------------------------------------------------

    def _apply_de_filter(
        self,
        df: pd.DataFrame,
        operator: str,
        value,
    ) -> pd.DataFrame:

        if "broad_sector" not in df.columns:

            return self._apply_numeric_filter(
                df,
                "debt_to_equity",
                operator,
                value,
            )

        financial = (
            df["broad_sector"]
            .fillna("")
            .str.lower()
            == "financial"
        )

        exempt = df.loc[
            financial
        ]

        others = df.loc[
            ~financial
        ]

        filtered = self._apply_numeric_filter(
            others,
            "debt_to_equity",
            operator,
            value,
        )

        result = pd.concat(
            [
                exempt,
                filtered,
            ],
            ignore_index=True,
        )

        logger.info(
            "Debt/Equity filter : %d companies",
            len(result),
        )

        return result

    # ---------------------------------------------------------
    # Interest Coverage
    # ---------------------------------------------------------

    def _apply_icr_filter(
        self,
        df: pd.DataFrame,
        operator: str,
        value,
    ) -> pd.DataFrame:

        temp = df.copy()

        debt_free = (
            temp["total_debt_cr"]
            .fillna(0)
            <= 0
        )

        temp.loc[
            debt_free,
            "interest_coverage",
        ] = float("inf")

        return self._apply_numeric_filter(
            temp,
            "interest_coverage",
            operator,
            value,
        )

    # ---------------------------------------------------------
    # Dispatch Filter
    # ---------------------------------------------------------

    def _apply_filter(
        self,
        df: pd.DataFrame,
        rule: FilterRule,
    ) -> pd.DataFrame:

        metric = rule.metric

        if metric == "debt_to_equity":

            return self._apply_de_filter(
                df,
                rule.operator,
                rule.value,
            )

        if metric == "interest_coverage":

            return self._apply_icr_filter(
                df,
                rule.operator,
                rule.value,
            )

        text_columns = {

            "broad_sector",

            "sub_sector",

            "peer_group_name",

            "market_cap_category",

        }

        if metric in text_columns:

            return self._apply_text_filter(
                df,
                metric,
                rule.operator,
                rule.value,
            )

        return self._apply_numeric_filter(
            df,
            metric,
            rule.operator,
            rule.value,
        )

    # ---------------------------------------------------------
    # Apply All Filters
    # ---------------------------------------------------------

    def apply_filters(self):

        if self.master_df is None:

            raise ScreenerException(
                "Call prepare() first."
            )

        result = self.master_df.copy()

        logger.info(
            "Initial companies : %d",
            len(result),
        )

        for index, rule in enumerate(
            self.config.filters,
            start=1,
        ):

            before = len(result)

            result = self._apply_filter(
                result,
                rule,
            )

            after = len(result)

            logger.info(
                "Rule %02d | %d -> %d",
                index,
                before,
                after,
            )

            if result.empty:

                logger.warning(
                    "No companies remaining."
                )

                break

        result = result.reset_index(
            drop=True
        )

        logger.info(
            "Filtering completed."
        )

        return result

    # ---------------------------------------------------------
    # Available Metrics
    # ---------------------------------------------------------

    @staticmethod
    def supported_metrics():

        return [

            "return_on_equity_pct",

            "net_profit_margin_pct",

            "operating_profit_margin_pct",

            "debt_to_equity",

            "interest_coverage",

            "asset_turnover",

            "free_cash_flow_cr",

            "market_cap_crore",

            "enterprise_value_crore",

            "pe_ratio",

            "pb_ratio",

            "ev_ebitda",

            "dividend_yield_pct",

            "broad_sector",

            "sub_sector",

            "peer_group_name",

            "market_cap_category",

            "earnings_per_share",

            "book_value_per_share",

            "dividend_payout_ratio_pct",

            "total_debt_cr",

            "cash_from_operations_cr",

        ]
    
        # ---------------------------------------------------------
    # Composite Score
    # ---------------------------------------------------------

    def calculate_composite_score(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate a normalized composite quality score.

        Weighting:
        ROE                     30%
        Net Profit Margin       20%
        Operating Margin        20%
        Interest Coverage       10%
        Asset Turnover          10%
        Free Cash Flow          10%
        """

        logger.info("Calculating composite score...")

        result = df.copy()

        metrics = {

            "return_on_equity_pct": 30,

            "net_profit_margin_pct": 20,

            "operating_profit_margin_pct": 20,

            "interest_coverage": 10,

            "asset_turnover": 10,

            "free_cash_flow_cr": 10,

        }

        score = pd.Series(
            0.0,
            index=result.index,
        )

        total_weight = sum(
            metrics.values()
        )

        for column, weight in metrics.items():

            if column not in result.columns:

                logger.warning(
                    "%s not found.",
                    column,
                )

                continue

            values = result[column].fillna(0)

            minimum = values.min()

            maximum = values.max()

            if minimum == maximum:

                normalized = pd.Series(
                    50,
                    index=result.index,
                )

            else:

                normalized = (
                    (
                        values - minimum
                    )
                    /
                    (
                        maximum - minimum
                    )
                ) * 100

            score += (
                normalized * weight
            )

        result["composite_score"] = (
            score / total_weight
        ).round(2)

        logger.info(
            "Composite score calculated."
        )

        return result

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------

    def sort_results(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        logger.info(
            "Sorting results..."
        )

        sort_column = self.config.sort_by

        if sort_column not in df.columns:

            logger.warning(
                "%s missing. Using composite_score.",
                sort_column,
            )

            sort_column = "composite_score"

        return (
            df.sort_values(
                by=sort_column,
                ascending=self.config.ascending,
            )
            .reset_index(drop=True)
        )

    # ---------------------------------------------------------
    # Screening Summary
    # ---------------------------------------------------------

    def screening_summary(
        self,
        df: pd.DataFrame,
    ) -> Dict:

        logger.info(
            "Preparing summary..."
        )

        summary = {

            "total_companies": len(
                self.master_df
            ),

            "selected_companies": len(df),

            "selection_percentage": round(

                len(df)
                /
                len(self.master_df)
                * 100,

                2,

            ),

            "average_composite_score": round(

                df["composite_score"].mean(),

                2,

            ),

        }

        if "broad_sector" in df.columns:

            summary["sector_distribution"] = (

                df["broad_sector"]

                .value_counts()

                .to_dict()

            )

        return summary

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def export_excel(
        self,
        df: pd.DataFrame,
        output_file: str,
    ):

        logger.info(
            "Exporting results..."
        )

        output = Path(output_file)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with pd.ExcelWriter(
            output,
            engine="openpyxl",
        ) as writer:

            df.to_excel(

                writer,

                sheet_name="Screened Companies",

                index=False,

            )

        logger.info(
            "Excel exported."
        )

    # ---------------------------------------------------------
    # Run Pipeline
    # ---------------------------------------------------------

    def run(
    self,
    output_file: str = "output/screener_output.xlsx",
    preset: Optional[str] = None,
    ) -> pd.DataFrame:
        
        logger.info(
            "=" * 70
        )

        logger.info(
            "Sprint 3 Screener Started"
        )

        self.prepare(preset=preset)

        self.keep_latest_year()

        self.remove_duplicates()

        screened = self.apply_filters()

        screened = self.calculate_composite_score(
            screened
        )

        screened = self.sort_results(
            screened
        )

        self.export_excel(
            screened,
            output_file,
        )

        summary = self.screening_summary(
            screened
        )

        logger.info(
            "=" * 70
        )

        logger.info(
            "Total Companies : %d",
            summary["total_companies"],
        )

        logger.info(
            "Selected : %d",
            summary["selected_companies"],
        )

        logger.info(
            "Selection %% : %.2f",
            summary["selection_percentage"],
        )

        logger.info(
            "Average Score : %.2f",
            summary["average_composite_score"],
        )

        logger.info(
            "=" * 70
        )

        return screened

    # ---------------------------------------------------------
    # Latest Financial Year
    # ---------------------------------------------------------

    def keep_latest_year(self) -> pd.DataFrame:
        """
        Keep only the latest financial year for each company.
        """

        if self.master_df is None:
            raise ScreenerException(
                "Master dataframe not available."
            )

        logger.info(
            "Keeping latest financial year..."
        )

        df = self.master_df.copy()

        df = (
            df.sort_values("year")
              .groupby("company_id", as_index=False)
              .tail(1)
              .reset_index(drop=True)
        )

        self.master_df = df

        logger.info(
            "Latest-year dataframe : %d companies",
            len(df),
        )

        return df

    # ---------------------------------------------------------
    # Remove Duplicates
    # ---------------------------------------------------------

    def remove_duplicates(self) -> pd.DataFrame:

        if self.master_df is None:
            raise ScreenerException(
                "Master dataframe not available."
            )

        before = len(self.master_df)

        self.master_df = (
            self.master_df
            .drop_duplicates(
                subset="company_id"
            )
            .reset_index(drop=True)
        )

        after = len(self.master_df)

        logger.info(
            "Duplicates removed : %d",
            before - after,
        )

        return self.master_df

    # ---------------------------------------------------------
    # Missing Value Report
    # ---------------------------------------------------------

    def missing_value_report(self) -> pd.DataFrame:

        if self.master_df is None:
            raise ScreenerException(
                "Master dataframe not available."
            )

        report = pd.DataFrame({

            "column": self.master_df.columns,

            "missing":

                self.master_df
                .isna()
                .sum()
                .values,

            "missing_pct":

                (
                    self.master_df
                    .isna()
                    .mean()
                    * 100
                ).round(2).values,

        })

        report = report.sort_values(
            "missing",
            ascending=False,
        )

        return report

    # ---------------------------------------------------------
    # Available Filters
    # ---------------------------------------------------------

    def available_filters(self):

        return {

            "Financial Ratios": [

                "return_on_equity_pct",

                "net_profit_margin_pct",

                "operating_profit_margin_pct",

                "interest_coverage",

                "debt_to_equity",

                "asset_turnover",

                "free_cash_flow_cr",

                "cash_from_operations_cr",

                "total_debt_cr",

                "earnings_per_share",

                "book_value_per_share",

                "dividend_payout_ratio_pct",

            ],

            "Market Metrics": [

                "market_cap_crore",

                "enterprise_value_crore",

                "pe_ratio",

                "pb_ratio",

                "ev_ebitda",

                "dividend_yield_pct",

            ],

            "Classification": [

                "broad_sector",

                "sub_sector",

                "peer_group_name",

                "market_cap_category",

            ]

        }

    # ---------------------------------------------------------
    # Dataset Summary
    # ---------------------------------------------------------

    def dataset_summary(self) -> Dict:

        if self.master_df is None:
            raise ScreenerException(
                "Master dataframe not available."
            )

        return {

            "rows": len(self.master_df),

            "columns": len(self.master_df.columns),

            "companies":

                self.master_df[
                    "company_id"
                ].nunique(),

            "financial_years":

                sorted(
                    self.master_df[
                        "year"
                    ].unique()
                ),

        }

    # ---------------------------------------------------------
    # Preview
    # ---------------------------------------------------------

    def preview(
        self,
        rows: int = 5,
    ) -> pd.DataFrame:

        if self.master_df is None:
            raise ScreenerException(
                "Master dataframe not available."
            )

        return self.master_df.head(rows)

    # ---------------------------------------------------------
    # Reset
    # ---------------------------------------------------------

    def reset(self):

        self.master_df = None

        self.ratios_df = None

        self.market_df = None

        self.sector_df = None

        self.peer_df = None

        logger.info(
            "Engine reset."
        )