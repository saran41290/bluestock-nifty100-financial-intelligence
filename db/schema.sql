PRAGMA foreign_keys = ON;

-- Drop Existing Tables

DROP TABLE IF EXISTS prosandcons;
DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS analysis;
DROP TABLE IF EXISTS cashflow;
DROP TABLE IF EXISTS balancesheet;
DROP TABLE IF EXISTS profitandloss;
DROP TABLE IF EXISTS companies;


-- Companies
CREATE TABLE companies (

    id TEXT PRIMARY KEY,

    company_logo TEXT,

    company_name TEXT NOT NULL,

    chart_link TEXT,

    about_company TEXT,

    website TEXT,

    nse_profile TEXT,

    bse_profile TEXT,

    face_value REAL,

    book_value REAL,

    roce_percentage REAL,

    roe_percentage REAL
);


-- Profit & Loss
CREATE TABLE profitandloss (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    year TEXT NOT NULL,

    sales REAL,

    expenses REAL,

    operating_profit REAL,

    opm_percentage REAL,

    other_income REAL,

    interest REAL,

    depreciation REAL,

    profit_before_tax REAL,

    tax_percentage REAL,

    net_profit REAL,

    eps REAL,

    dividend_payout REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- Balance Sheet

CREATE TABLE balancesheet (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    year TEXT NOT NULL,

    equity_capital REAL,

    reserves REAL,

    borrowings REAL,

    other_liabilities REAL,

    total_liabilities REAL,

    fixed_assets REAL,

    cwip REAL,

    investments REAL,

    other_asset REAL,

    total_assets REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);


-- Cash Flow
CREATE TABLE cashflow (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    year TEXT NOT NULL,

    operating_activity REAL,

    investing_activity REAL,

    financing_activity REAL,

    net_cash_flow REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);


-- Analysis
CREATE TABLE analysis (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    compounded_sales_growth REAL,

    compounded_profit_growth REAL,

    stock_price_cagr REAL,

    roe REAL,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);


-- Documents
CREATE TABLE documents (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    Year TEXT,

    Annual_Report TEXT,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);


-- Pros & Cons
CREATE TABLE prosandcons (

    id INTEGER PRIMARY KEY,

    company_id TEXT NOT NULL,

    pros TEXT,

    cons TEXT,

    FOREIGN KEY(company_id)
        REFERENCES companies(id)
);

-- Useful Indexes

CREATE INDEX idx_profit_company
ON profitandloss(company_id);

CREATE INDEX idx_profit_year
ON profitandloss(year);

CREATE INDEX idx_balance_company
ON balancesheet(company_id);

CREATE INDEX idx_balance_year
ON balancesheet(year);

CREATE INDEX idx_cash_company
ON cashflow(company_id);

CREATE INDEX idx_cash_year
ON cashflow(year);

CREATE INDEX idx_analysis_company
ON analysis(company_id);

CREATE INDEX idx_documents_company
ON documents(company_id);

CREATE INDEX idx_pros_company
ON prosandcons(company_id);

-- Financial Ratio Engine
-- Sprint 2

CREATE TABLE IF NOT EXISTS financial_ratios (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company_id TEXT NOT NULL,

    UNIQUE(company_id, year),

    year TEXT NOT NULL,

    
    -- Profitability    

    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,

    return_on_equity_pct REAL,
    return_on_assets_pct REAL,
    return_on_capital_employed_pct REAL,

    
    -- Leverage    

    debt_to_equity REAL,
    interest_coverage REAL,

    high_leverage_flag INTEGER DEFAULT 0,

    icr_label TEXT,

    
    -- Efficiency    

    asset_turnover REAL,

    
    -- Cash Flow    

    free_cash_flow_label TEXT,

    capex_label TEXT,

    fcf_conversion_label TEXT,

    cfo_quality_label TEXT,

    capital_allocation TEXT,

    cfo_quality_score REAL

    
    -- CAGR    

    revenue_cagr_3yr REAL,
    revenue_cagr_5yr REAL,
    revenue_cagr_10yr REAL,

    pat_cagr_3yr REAL,
    pat_cagr_5yr REAL,
    pat_cagr_10yr REAL,

    eps_cagr_3yr REAL,
    eps_cagr_5yr REAL,
    eps_cagr_10yr REAL,

    
    -- Flags    

    revenue_cagr_flag TEXT,

    pat_cagr_flag TEXT,

    eps_cagr_flag TEXT,

    
    -- Composite    

    composite_quality_score REAL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(company_id) REFERENCES companies(id)

);

CREATE INDEX idx_ratio_company
ON financial_ratios(company_id);

CREATE INDEX idx_ratio_year
ON financial_ratios(year);

CREATE INDEX idx_ratio_company_year
ON financial_ratios(company_id, year);