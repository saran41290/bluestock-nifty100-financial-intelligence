"""
business_queries.py

Executes business SQL queries and exports results to CSV.
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("db") / "nifty100.db"
OUTPUT_DIR = Path("output") / "queries"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


QUERIES = {

    # --------------------------------------------------------
    # Top ROE
    # --------------------------------------------------------

    "top_roe": """

    SELECT

        company_name,
        roe_percentage

    FROM vw_company_summary

    ORDER BY roe_percentage DESC;

    """,

    # --------------------------------------------------------
    # Top ROCE
    # --------------------------------------------------------

    "top_roce": """

    SELECT

        company_name,
        roce_percentage

    FROM vw_company_summary

    ORDER BY roce_percentage DESC;

    """,

    # --------------------------------------------------------
    # Highest Book Value
    # --------------------------------------------------------

    "book_value": """

    SELECT

        company_name,
        book_value

    FROM vw_company_summary

    ORDER BY book_value DESC;

    """,

    # --------------------------------------------------------
    # Profit Growth
    # --------------------------------------------------------

    "profit_growth": """

    SELECT

        company_id,
        compounded_profit_growth

    FROM vw_analysis_summary

    ORDER BY compounded_profit_growth DESC;

    """,

    # --------------------------------------------------------
    # Sales Growth
    # --------------------------------------------------------

    "sales_growth": """

    SELECT

        company_id,
        compounded_sales_growth

    FROM vw_analysis_summary

    ORDER BY compounded_sales_growth DESC;

    """,

    # --------------------------------------------------------
    # Stock CAGR
    # --------------------------------------------------------

    "stock_cagr": """

    SELECT

        company_id,
        stock_price_cagr

    FROM vw_analysis_summary

    ORDER BY stock_price_cagr DESC;

    """,

    # --------------------------------------------------------
    # Latest Profit
    # --------------------------------------------------------

    "latest_profit": """

    SELECT

    company_id,

    year,

    net_profit

    FROM vw_latest_profit

    ORDER BY net_profit DESC;

    """,

    # --------------------------------------------------------
    # Latest Sales
    # --------------------------------------------------------

    "latest_sales": """

    SELECT

    company_id,

    year,

    sales

    FROM vw_latest_profit

    ORDER BY sales DESC;

    """,

    # --------------------------------------------------------
    # Latest Cash Flow
    # --------------------------------------------------------

    "cashflow": """

    SELECT

    company_id,

    year,

    net_cash_flow

    FROM vw_latest_cashflow

    ORDER BY net_cash_flow DESC;

    """

}


def main():

   
    print("----------------BUSINESS SQL QUERIES--------------------")
    

    conn = sqlite3.connect(DB_PATH)

    for name, sql in QUERIES.items():

        df = pd.read_sql_query(sql, conn)

        file = OUTPUT_DIR / f"{name}.csv"

        df.to_csv(file, index=False)

        print(f"{name:<20} {len(df):>5} rows")

    conn.close()
    
    print("----------------ALL QUERY RESULTS EXPORTED-----------------")

if __name__ == "__main__":
    main()