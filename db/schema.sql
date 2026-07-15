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