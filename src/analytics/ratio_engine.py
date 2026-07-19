"""
ratio_engine.py

Financial Ratio Engine

Sprint 2

Responsibilities
----------------
1. Load financial data from SQLite
2. Build company-wise financial history
3. Compute Ratios
4. Compute CAGR
5. Compute Cashflow KPIs
6. Populate financial_ratios table
7. Generate output files
"""

import csv
import logging
from pathlib import Path
from collections import defaultdict

import pandas as pd

from src.config import (
    OUTPUT_DIR,
    CAPITAL_ALLOCATION_CSV,
    RATIO_EDGE_CASE_LOG,
    RATIO_ENGINE_LOG,
    ERROR_LOG,
)

from src.database.database import DatabaseManager
from src.analytics.ratios import FinancialRatioCalculator
from src.analytics.cagr import CAGRCalculator
from src.analytics.cashflow_kpis import CashflowKPICalculator
from src.analytics.validator import FinancialValidator

class RatioEngine:
    """
    Financial Ratio Processing Engine.
    """

    # ----------------------------------------------------------

    def __init__(
    self,
    
    output_dir: str = "output",
):

        self.db = DatabaseManager()

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logger = logging.getLogger(
            self.__class__.__name__
        )

        self.logger.setLevel(logging.INFO)

        self.error_logger = logging.getLogger("RatioEngineError")
        self.edge_logger = logging.getLogger("RatioEngineEdge")

        self.edge_case_log = (
            self.output_dir /
            "ratio_edge_cases.log"
        )

        self.capital_allocation_csv = (
            self.output_dir /
            "capital_allocation.csv"
        )

        self._configure_logging()

    # ==========================================================
    # LOGGING
    # ==========================================================

    def _configure_logging(self):
        """
        Configure project loggers.
        """

        formatter = logging.Formatter(

            "%(asctime)s | %(levelname)s | %(message)s"

        )

        # --------------------------------------------------
        # Engine Logger
        # --------------------------------------------------

        if not self.logger.handlers:

            engine_handler = logging.FileHandler(

                RATIO_ENGINE_LOG,

                encoding="utf-8",

            )

            engine_handler.setFormatter(formatter)

            self.logger.addHandler(engine_handler)

            self.logger.setLevel(logging.INFO)

        # --------------------------------------------------
        # Error Logger
        # --------------------------------------------------

        if not self.error_logger.handlers:

            error_handler = logging.FileHandler(

                ERROR_LOG,

                encoding="utf-8",

            )

            error_handler.setFormatter(formatter)

            self.error_logger.addHandler(error_handler)

            self.error_logger.setLevel(logging.ERROR)

        # --------------------------------------------------
        # Edge Logger
        # --------------------------------------------------

        if not self.edge_logger.handlers:

            edge_handler = logging.FileHandler(

                RATIO_EDGE_CASE_LOG,

                encoding="utf-8",

            )

            edge_handler.setFormatter(formatter)

            self.edge_logger.addHandler(edge_handler)

            self.edge_logger.setLevel(logging.WARNING)
        # DATABASE
        

    def connect(self):

        self.db.connect()

        # ----------------------------------------------------------

    def close(self):

        self.db.close()

        
        # LOAD TABLES
    

    def load_companies(self) -> pd.DataFrame:

        return pd.read_sql_query(

            """
            SELECT *
            FROM companies
            """,

            self.db.connection,
        )

    # ----------------------------------------------------------

    def load_profit_loss(self):

        return pd.read_sql_query(

            """
            SELECT *
            FROM profitandloss
            WHERE year LIKE 'Mar %'
            ORDER BY company_id, year
            """,

            self.db.connection,
        )

    # ----------------------------------------------------------

    def load_balance_sheet(self):

        return pd.read_sql_query(

            """
            SELECT *
            FROM balancesheet
            WHERE year LIKE 'Mar %'
            ORDER BY company_id, year
            """,

            self.db.connection,
        )

    # ----------------------------------------------------------

    def load_cashflow(self):

        return pd.read_sql_query(

            """
            SELECT *
            FROM cashflow
            WHERE year LIKE 'Mar %'
            ORDER BY company_id, year
            """,

            self.db.connection,
        )

    
    # BUILD COMPANY HISTORY
    

    def build_company_history(
        self,
        pnl_df,
        balance_df,
        cashflow_df,
        ):
        """
        Creates

        company_history

        {
            company_id:
            {
                2021:{...},
                2022:{...}
            }
        }

        Used by CAGR engine.
        """

        history = defaultdict(dict)

        # -----------------------------
        # Profit & Loss
        # -----------------------------
        
        for _, row in pnl_df.iterrows():

            company = row["company_id"]

            year = str(row["year"])

            history[company].setdefault(
                year,
                {}
            )

            history[company][year].update(
                row.to_dict()
            )

        # -----------------------------
        # Balance Sheet
        # -----------------------------

        for _, row in balance_df.iterrows():

            company = row["company_id"]

            year = str(row["year"])

            history[company].setdefault(
                year,
                {}
            )

            history[company][year].update(
                row.to_dict()
            )

        # -----------------------------
        # Cash Flow
        # -----------------------------

        for _, row in cashflow_df.iterrows():

            company = row["company_id"]

            year = str(row["year"])

            history[company].setdefault(
                year,
                {}
            )

            history[company][year].update(
                row.to_dict()
            )

        return history

    
    # GET COMPANY YEARS
    

    @staticmethod
    def get_company_years(
        company_history,
        company_id,
        ):
        """
        Returns years in ascending order.
        """

        years = sorted(

            company_history[
                company_id
            ].keys()

        )

        return years

    
    # GET METRIC HISTORY
    

    @staticmethod
    def metric_history(
        company_history,
        company_id,
        years,
        column,
        ):
        """
        Returns one metric history.

        Example

        sales

        [120,140,180,220]
        """

        values = []

        for year in years:

            value = (

                company_history

                [company_id]

                [year]

                .get(column)

            )

            if value is None:

                continue

            values.append(value)

        return values
        
        
        # BUILD FINANCIAL RATIO RECORD
        

    def build_ratio_record(
        self,
        company_id,
        year,
        current,
        company_history,
        ):
        """
        Builds one financial ratio record for a
        company-year combination.
        """

        # -----------------------------------------
        # Historical Data
        # -----------------------------------------

        years = self.get_company_years(
            company_history,
            company_id,
        )

        sales_history = self.metric_history(
            company_history,
            company_id,
            years,
            "sales",
        )

        profit_history = self.metric_history(
            company_history,
            company_id,
            years,
            "net_profit",
        )

        eps_history = self.metric_history(
            company_history,
            company_id,
            years,
            "eps",
        )

        cfo_history = self.metric_history(
            company_history,
            company_id,
            years,
            "operating_activity",
        )

        # -----------------------------------------
        # Derived Values
        # -----------------------------------------

        equity = (
            current.get("equity_capital", 0)
            + current.get("reserves", 0)
        )

        capital_employed = (
            equity
            + current.get("borrowings", 0)
        )

        total_assets = current.get(
            "total_assets",
            0,
        )

        ebit = (
            current.get("operating_profit", 0)
            + current.get("other_income", 0)
        )

        # -----------------------------------------
        # Ratio Calculator
        # -----------------------------------------

        ratios = FinancialRatioCalculator.calculate_all(
            sales=current.get("sales"),
            net_profit=current.get("net_profit"),
            operating_profit=current.get("operating_profit"),
            source_opm=current.get("opm_percentage"),
            equity_capital=current.get("equity_capital"),
            reserves=current.get("reserves"),
            borrowings=current.get("borrowings"),
            interest=current.get("interest"),
            other_income=current.get("other_income"),
            investments=current.get("investments"),
            total_assets=current.get("total_assets"),
        )

        # -----------------------------------------
        # CAGR
        # -----------------------------------------

        cagr = (
            CAGRCalculator.calculate_all(
                sales=sales_history,
                profits=profit_history,
                eps=eps_history,
            )
        )

        # -----------------------------------------
        # Cashflow KPIs
        # -----------------------------------------

        cashflow = (
            CashflowKPICalculator.calculate_all(
                operating_activity=current.get(
                    "operating_activity",
                    0,
                ),
                investing_activity=current.get(
                    "investing_activity",
                    0,
                ),
                financing_activity=current.get(
                    "financing_activity",
                    0,
                ),
                operating_profit=current.get(
                    "operating_profit",
                    0,
                ),
                sales=current.get(
                    "sales",
                    0,
                ),
                cfo_history=cfo_history,
                pat_history=profit_history,
            )
        )

        # -----------------------------------------
        # Merge Everything
        # -----------------------------------------

        record = {

            "company_id": company_id,

            "year": year,

        }

        record.update(ratios)

        record.update(cagr)

        record.update(cashflow)

        return record

        
    # PROCESS ALL COMPANIES
    

    def process_company_history(
        self,
        company_history,
        ):
        """
        Computes ratios for every company
        and every available year.
        """

        records = []

        for company_id in company_history:

            years = self.get_company_years(
                company_history,
                company_id,
            )

            self.logger.info(
                "Processing %s (%d years)",
                company_id,
                len(years),
            )

            for year in years:

                current = (
                    company_history
                    [company_id]
                    [year]
                )
                validation = FinancialValidator.validate(current)

                if not validation.is_valid:

                    error_text = "; ".join(validation.errors)

                    self.logger.warning(
                        "%s %s skipped: %s",
                        company_id,
                        year,
                        error_text,
                    )

                    self.edge_logger.warning(
                        "%s,%s,%s",
                        company_id,
                        year,
                        error_text,
                    )
                    print(company_id, year, validation.errors)
                    continue

                try:

                    record = (
                        self.build_ratio_record(
                            company_id,
                            year,
                            current,
                            company_history,
                        )
                    )

                    records.append(record)

                except Exception:
                    raise

                    self.error_logger.exception(
                        "Failed %s %s : %s",
                        company_id,
                        year,
                        ex,
                    )

                    self.edge_logger.warning("%s | %s | %s", company_id,year, "; ".join(validation.errors),)

        self.logger.info(
            "Generated %d ratio records.",
            len(records),
        )

        return records
        
        
   
    # INSERT RECORDS
    def insert_ratio_records(
        self,
        records,
    ):
        """
        Inserts or updates financial ratios.
        """

        if not records:

            self.logger.warning(
                "No ratio records generated."
            )
            return

        cursor = self.db.connection.cursor()

        columns = list(records[0].keys())
       
        placeholders = ",".join(["?"] * len(columns))

        update_columns = [

            column

            for column in columns

            if column not in (
                "company_id",
                "year",
            )

        ]

        update_clause = ", ".join(

            f"{column}=excluded.{column}"

            for column in update_columns

        )

        sql = f"""
        INSERT INTO financial_ratios
        ({",".join(columns)})
        VALUES ({placeholders})
        ON CONFLICT(company_id, year)
        DO UPDATE SET
        {update_clause}
        """

        values = [

            tuple(

                record.get(column)

                for column in columns

            )

            for record in records

        ]
        cursor.executemany(

            sql,

            values,

        )

        self.logger.info(

            "Inserted %d financial ratio records.",

            len(values),

        )

        
        
    # CAPITAL ALLOCATION CSV
    

    def export_capital_allocation(
        self,
        records,
        ):
        """
        Writes

        output/capital_allocation.csv
        """

        rows = []

        for record in records:

            rows.append(

                {

                    "company_id":
                        record["company_id"],

                    "year":
                        record["year"],

                    "capital_allocation":
                        record.get(
                            "capital_allocation"
                        ),

                    "free_cash_flow":
                        record.get(
                            "free_cash_flow"
                        ),

                    "fcf_conversion":
                        record.get(
                            "fcf_conversion"
                        ),

                    "capex_intensity":
                        record.get(
                            "capex_intensity"
                        ),

                }

            )

        df = pd.DataFrame(rows)

        df.to_csv(

            self.capital_allocation_csv,

            index=False,

        )

        self.logger.info(

            "Capital allocation CSV created."

        )

        
    # EDGE CASE REPORT
    

    def export_edge_cases(
        self,
        records,
        ):
        """
        Appends interesting KPI edge cases.
        """

        with open(

            self.edge_case_log,

            "a",

            encoding="utf-8",

        ) as fp:

            for record in records:

                if (

                    record.get(
                        "high_leverage_flag"
                    )

                    or

                    record.get(
                        "revenue_cagr_flag"
                    )

                    or

                    record.get(
                        "pat_cagr_flag"
                    )

                    or

                    record.get(
                        "eps_cagr_flag"
                    )

                ):

                    fp.write(

                        f"{record['company_id']} | "

                        f"{record['year']} | "

                        f"HL={record.get('high_leverage_flag')} | "

                        f"REV={record.get('revenue_cagr_flag')} | "

                        f"PAT={record.get('pat_cagr_flag')} | "

                        f"EPS={record.get('eps_cagr_flag')}"

                        "\n"

                    )

        self.logger.info(

            "Edge case report generated."

        )

    def execute_transaction(
        self,
        records,
    ):
        """
        Executes all database writes in a
        single transaction.
        """

        conn = self.db.connection

        try:

            conn.execute("BEGIN")

            self.insert_ratio_records(records)

            conn.commit()

            self.logger.info(

                "Database transaction committed."

            )

            

        except Exception:

            conn.rollback()

            self.error_logger.exception(

                "Transaction rolled back."

            )

            raise

# ==========================================================
# RUN ENGINE
# ==========================================================

    def run(self):
        """
        Execute complete financial ratio engine.
        """

        self.logger.info("=" * 60)
        self.logger.info("Financial Ratio Engine Started")
        self.logger.info("=" * 60)

        try:

            # --------------------------------------------------
            # Connect
            # --------------------------------------------------

            self.connect()
            cursor = self.db.connection.cursor()

            
            
            
            # --------------------------------------------------
            # Load Data
            # --------------------------------------------------

            self.logger.info("Loading Profit & Loss")

            pnl_df = self.load_profit_loss()

            self.logger.info("Loading Balance Sheet")

            balance_df = self.load_balance_sheet()

            self.logger.info("Loading Cashflow")

            cashflow_df = self.load_cashflow()

            # --------------------------------------------------
            # Build History
            # --------------------------------------------------

            self.logger.info("Building Company History")

            company_history = self.build_company_history(

                pnl_df,

                balance_df,

                cashflow_df,

            )

            # --------------------------------------------------
            # Calculate KPIs
            # --------------------------------------------------

            self.logger.info("Generating Financial Ratios")

            records = self.process_company_history(

                company_history

            )

            # --------------------------------------------------
            # Database
            # --------------------------------------------------

            self.logger.info("Saving Financial Ratios")
            print(f"Generated records: {len(records)}")
            self.execute_transaction(records)

            # --------------------------------------------------
            # Reports
            # --------------------------------------------------

            self.logger.info("Exporting Reports")

            self.export_capital_allocation(records)

            self.export_edge_cases(records)

            self.logger.info(

                "Financial Ratio Engine Completed Successfully"

            )

        except Exception:

            self.error_logger.exception(

                "Ratio Engine Failed"

            )

            raise

        finally:

            self.close()

            self.logger.info(

                "Database Connection Closed"

            )
# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    from src.config import DATABASE_PATH

    engine = RatioEngine()

    engine.run()