"""
create_views.py

Creates analytical SQL views for Power BI.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path("db") / "nifty100.db"


VIEWS = {

    # ---------------------------------------------------------
    # Company Summary
    # ---------------------------------------------------------

    "vw_company_summary": """

    CREATE VIEW IF NOT EXISTS vw_company_summary AS

    SELECT

        id,
        company_name,
        website,
        face_value,
        book_value,
        roce_percentage,
        roe_percentage

    FROM companies;

    """,

    # ---------------------------------------------------------
    # Profit & Loss
    # ---------------------------------------------------------

    "vw_profit_summary": """

    CREATE VIEW IF NOT EXISTS vw_profit_summary AS

    SELECT

        company_id,

        year,

        sales,

        operating_profit,

        net_profit,

        eps,

        dividend_payout

    FROM profitandloss;

    """,

    # ---------------------------------------------------------
    # Balance Sheet
    # ---------------------------------------------------------

    "vw_balance_summary": """

    CREATE VIEW IF NOT EXISTS vw_balance_summary AS

    SELECT

        company_id,

        year,

        equity_capital,

        reserves,

        borrowings,

        total_assets,

        total_liabilities

    FROM balancesheet;

    """,

    # ---------------------------------------------------------
    # Cash Flow
    # ---------------------------------------------------------

    "vw_cashflow_summary": """

    CREATE VIEW IF NOT EXISTS vw_cashflow_summary AS

    SELECT

        company_id,

        year,

        operating_activity,

        investing_activity,

        financing_activity,

        net_cash_flow

    FROM cashflow;

    """,

    # ---------------------------------------------------------
    # Growth Analysis
    # ---------------------------------------------------------

    "vw_analysis_summary": """

    CREATE VIEW IF NOT EXISTS vw_analysis_summary AS

    SELECT

        company_id,

        compounded_sales_growth,

        compounded_profit_growth,

        stock_price_cagr,

        roe

    FROM analysis;

    """,
    #------------------------------------------------------------
    "vw_latest_profit": """

    CREATE VIEW IF NOT EXISTS vw_latest_profit AS

    SELECT *

    FROM profitandloss p

    WHERE id IN (

        SELECT MAX(id)

        FROM profitandloss

        GROUP BY company_id

    );

    """,
    #----------------------------------------------------------------
    "vw_latest_cashflow": """

    CREATE VIEW IF NOT EXISTS vw_latest_cashflow AS

    SELECT *

    FROM cashflow c

    WHERE id IN (

        SELECT MAX(id)

        FROM cashflow

        GROUP BY company_id

    );

    """,
    #---------------------------------------------------------------

    "vw_latest_balance": """

    CREATE VIEW IF NOT EXISTS vw_latest_balance AS

    SELECT *

    FROM balancesheet b

    WHERE id IN (

        SELECT MAX(id)

        FROM balancesheet

        GROUP BY company_id

    );

    """,

    #-----------------------------------------------------------------
    "vw_latest_balance": """

    CREATE VIEW IF NOT EXISTS vw_latest_balance AS

    SELECT *

    FROM balancesheet b

    WHERE id IN (

        SELECT MAX(id)

        FROM balancesheet

        GROUP BY company_id

    );

    """,
    #-----------------------------------------------------------------
    "vw_analysis_latest": """
    CREATE VIEW IF NOT EXISTS vw_analysis_latest AS

        SELECT

            company_id,

            MAX(CASE
                WHEN compounded_sales_growth LIKE 'TTM:%'
                OR compounded_sales_growth LIKE '1 Year:%'
                THEN compounded_sales_growth
            END) AS latest_sales_growth,

            MAX(CASE
                WHEN compounded_profit_growth LIKE 'TTM:%'
                OR compounded_profit_growth LIKE '1 Year:%'
                THEN compounded_profit_growth
            END) AS latest_profit_growth,

            MAX(CASE
                WHEN stock_price_cagr LIKE '1 Year:%'
                THEN stock_price_cagr
            END) AS latest_stock_cagr,

            MAX(CASE
                WHEN roe LIKE 'Last Year:%'
                THEN roe
            END) AS latest_roe

        FROM analysis

        GROUP BY company_id;
    """,
    #----------------------------------------------------------------
    "vw_latest_company_metrics": """

    CREATE VIEW IF NOT EXISTS vw_latest_company_metrics AS

    

    SELECT

        -------------------------------------------------
        -- Company Information
        -------------------------------------------------

        c.id                                 AS company_id,
        c.company_name                       AS company_name,
        c.website                            AS website,
        c.face_value                         AS face_value,
        c.book_value                         AS book_value,

        c.roe_percentage                     AS roe,
        c.roce_percentage                    AS roce,

        -------------------------------------------------
        -- Profitability
        -------------------------------------------------

        p.year                               AS latest_profit_year,
        p.sales                              AS latest_sales,
        p.operating_profit                   AS operating_profit,
        p.net_profit                         AS net_profit,
        p.eps                                AS eps,
        p.dividend_payout                    AS dividend,

        -------------------------------------------------
        -- Financial Health
        -------------------------------------------------

        b.year                               AS latest_balance_year,
        b.equity_capital                     AS equity_capital,
        b.reserves                           AS reserves,
        b.borrowings                         AS borrowings,
        b.total_assets                       AS total_assets,
        b.total_liabilities                  AS total_liabilities,

        -------------------------------------------------
        -- Cash Flow
        -------------------------------------------------

        cf.year                              AS latest_cashflow_year,
        cf.operating_activity                AS operating_cash_flow,
        cf.investing_activity                AS investing_cash_flow,
        cf.financing_activity                AS financing_cash_flow,
        cf.net_cash_flow                     AS net_cash_flow,

        -------------------------------------------------
        -- Growth Metrics
        -------------------------------------------------

        a.latest_sales_growth      AS sales_growth,
        a.latest_profit_growth     AS profit_growth,
        a.latest_stock_cagr        AS stock_cagr,
        a.latest_roe               AS analysis_roe

    FROM companies c

    LEFT JOIN vw_latest_profit p
    ON c.id = p.company_id

    LEFT JOIN vw_latest_balance b
    ON c.id = b.company_id

    LEFT JOIN vw_latest_cashflow cf
    ON c.id = cf.company_id

    LEFT JOIN vw_analysis_latest a
    ON c.id = a.company_id

    """,
    #------------------------------------------------------------------

}


def main():

    
    print("---------------CREATING SQL VIEWS-------------------------")
    

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    for view_name, sql in VIEWS.items():

        cursor.execute(f"DROP VIEW IF EXISTS {view_name}")

        cursor.execute(sql)

        print(f"Created : {view_name}")

    conn.commit()

    conn.close()

    print()
    print("---------------ALL SQL VIEWS CREATED--------------")
    


if __name__ == "__main__":
    main()