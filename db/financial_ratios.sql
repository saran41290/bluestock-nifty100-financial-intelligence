CREATE TABLE IF NOT EXISTS financial_ratios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id INTEGER NOT NULL,
    year TEXT NOT NULL,

    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,

    return_on_equity_pct REAL,
    return_on_capital_employed_pct REAL,
    return_on_assets_pct REAL,

    debt_to_equity REAL,
    interest_coverage REAL,
    interest_coverage_label TEXT,
    high_leverage_flag INTEGER,

    asset_turnover REAL,
    net_debt REAL,

    free_cash_flow REAL,
    cfo_quality_score REAL,
    cfo_quality_label TEXT,
    capex_intensity_pct REAL,
    capex_label TEXT,
    fcf_conversion_pct REAL,

    revenue_cagr_3yr REAL,
    revenue_cagr_5yr REAL,
    revenue_cagr_10yr REAL,

    pat_cagr_3yr REAL,
    pat_cagr_5yr REAL,
    pat_cagr_10yr REAL,

    eps_cagr_3yr REAL,
    eps_cagr_5yr REAL,
    eps_cagr_10yr REAL,

    revenue_cagr_flag TEXT,
    pat_cagr_flag TEXT,
    eps_cagr_flag TEXT,

    capital_allocation_pattern TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(company_id, year)
);