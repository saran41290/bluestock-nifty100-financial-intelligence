-- Exploratory Queries for Nifty 100 Financial Intelligence Database
-- Target Database: nifty100.db (SQLite)

-- 1. Count Total Active Companies
SELECT COUNT(*) AS total_companies FROM companies;

-- 2. Data Health Check: Coverage of Financial Statements (P&L, BS, Cash Flow) per Company
SELECT 
    c.company_id,
    c.company_name,
    COUNT(DISTINCT p.year) AS pnl_years,
    COUNT(DISTINCT b.year) AS bs_years,
    COUNT(DISTINCT f.year) AS cf_years
FROM companies c
LEFT JOIN profitandloss p ON c.company_id = p.company_id
LEFT JOIN balancesheet b ON c.company_id = b.company_id
LEFT JOIN cashflow f ON c.company_id = f.company_id
GROUP BY c.company_id, c.company_name
ORDER BY pnl_years DESC;

-- 3. Top 10 High ROE Companies (Latest Fiscal Year)
SELECT company_id, year, return_on_equity_pct, net_profit_margin_pct, debt_to_equity
FROM financial_ratios
WHERE year = 2024
ORDER BY return_on_equity_pct DESC
LIMIT 10;

-- 4. Quality Screener: Companies with High ROE, Low Debt/Equity, and Positive FCF
SELECT 
    r.company_id,
    c.company_name,
    c.sector,
    r.return_on_equity_pct,
    r.debt_to_equity,
    r.free_cash_flow,
    r.revenue_cagr_5yr
FROM financial_ratios r
JOIN companies c ON r.company_id = c.company_id
WHERE r.year = 2024
  AND r.return_on_equity_pct >= 15.0
  AND r.debt_to_equity <= 1.0
  AND r.free_cash_flow > 0
ORDER BY r.return_on_equity_pct DESC;

-- 5. Sector Peer Aggregation & Averages
SELECT 
    c.sector,
    COUNT(DISTINCT c.company_id) AS company_count,
    AVG(r.return_on_equity_pct) AS avg_roe,
    AVG(r.net_profit_margin_pct) AS avg_net_margin,
    AVG(r.revenue_cagr_5yr) AS avg_rev_cagr_5yr
FROM companies c
JOIN financial_ratios r ON c.company_id = r.company_id
WHERE r.year = 2024
GROUP BY c.sector
ORDER BY avg_roe DESC;
