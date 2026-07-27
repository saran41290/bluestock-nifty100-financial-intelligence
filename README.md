# Bluestock Nifty 100 Financial Intelligence Platform

> An end-to-end Data Engineering & Analytics Platform for Nifty 100 companies — featuring an automated ETL pipeline, SQLite database engine, financial ratio calculator, investment screener, valuation module, and an interactive 8-screen Streamlit dashboard.

---

## 🚀 Quick Start — Launching the Dashboard

To launch the multi-page Streamlit analytics dashboard on `http://localhost:8501`:

```powershell
streamlit run src/dashboard/app.py
```

To run the integration & QA test suite:

```powershell
python tests/test_sprint4.py
```

---

## 📅 Sprint-by-Sprint Project Roadmap

```text
┌───────────────────────────────────────────────────────────────────────────────────┐
│                    NIFTY 100 PLATFORM DEVELOPMENT ROADMAP                         │
├─────────────────┬──────────────────┬──────────────────┬───────────────────────────┤
│    SPRINT 1     │     SPRINT 2     │     SPRINT 3     │         SPRINT 4          │
│ ETL & SQLite DB │ Ratio & CAGR     │ Screener & Peer  │ Streamlit Dashboard &     │
│   Ingestion     │    Engine        │   Percentiles    │     Valuation Module      │
├─────────────────┼──────────────────┼──────────────────┼───────────────────────────┤
│ • Excel ETL     │ • 50+ KPIs       │ • Screener Engine│ • 8-Screen Dashboard      │
│ • Schema Design │ • CAGR Engine    │ • 7 Presets      │ • Cached Data Loader      │
│ • Data Cleaner  │ • Cashflow KPIs  │ • Peer Ranking   │ • Valuation Engine        │
│ • Foreign Keys  │ • Quality Score  │ • SQL Views      │ • FCF Yield & Flags       │
│ • Normalization │ • Allocation CSV │ • Power BI Data  │ • Excel & CSV Exports     │
└─────────────────┴──────────────────┴──────────────────┴───────────────────────────┘
```

---

### 🔹 Sprint 1 — Data Ingestion & ETL Pipeline Engine
*Focus: Data Extraction, Cleaning, Schema Normalization, and SQLite Loading*

- **Multi-Source Ingestion**: Extracted raw financial datasets for 92 Nifty 100 companies from Excel files (`companies.xlsx`, `profitandloss.xlsx`, `balancesheet.xlsx`, `cashflow.xlsx`, `analysis.xlsx`, `documents.xlsx`, `prosandcons.xlsx`).
- **Data Normalization & Cleaning**: Stripped formatting artifacts, normalized company tickers, mapped standard line items, and sanitized missing/zero values.
- **Relational SQLite Schema (`db/schema.sql`)**: Designed a structured relational schema enforced with foreign key constraints, explicit data types, and performance indexes across 7 core tables.
- **Verification Suite**: Created database loader and validation scripts (`scripts/load_database.py`, `scripts/verify_database.py`) to confirm zero foreign key violations.

---

### 🔹 Sprint 2 — Financial Ratio Engine & CAGR Analysis
*Focus: Advanced Financial Ratio Calculation, Multi-Year CAGR, and Cashflow Metrics*

- **Financial Ratio Engine (`src/analytics/ratio_engine.py`, `ratios.py`)**: Built an automated calculation engine generating 50+ financial ratios across profitability, leverage, liquidity, and asset efficiency.
- **Multi-Period CAGR Engine (`src/analytics/cagr.py`)**: Computed 3-Year, 5-Year, and 10-Year Compound Annual Growth Rates (CAGR) for Revenue, Net Profit (PAT), and Earnings Per Share (EPS).
- **Cash Flow & Capital Allocation Analysis (`src/analytics/cashflow_kpis.py`)**:
  - Free Cash Flow (FCF) and Capex Intensity tracking.
  - CFO Quality Score and FCF Conversion Ratios.
  - Classification of companies into 8 Capital Allocation Patterns (e.g. *High Reinvestment Compounder*, *Deleveraging*, *Moderate Cash Generator*).
- **Composite Quality Scoring (`src/analytics/ranking.py`)**: Formulated a weighted composite quality score (0–100) evaluating profitability consistency, leverage safety, and growth stability.
- **Artifacts Generated**: Populated `financial_ratios` table in SQLite and exported `output/capital_allocation.csv`.

---

### 🔹 Sprint 3 — Investment Screener Engine & Peer Percentiles
*Focus: Rule-Based Screening Engine, Investment Strategies, and Relative Benchmarking*

- **Modular Screener Engine (`src/screener/engine.py`, `presets.py`, `cli.py`)**: Implemented a flexible filtering engine supporting multi-metric constraints and comparison operators.
- **Legendary Investment Presets**: Built pre-configured investment strategy filters:
  - 🏆 **Buffett Style**: High ROE (≥20%), low debt (D/E ≤0.5), strong margins (OPM ≥18%).
  - 💎 **Benjamin Graham**: Value-focused defensive criteria (P/E ≤20, P/B ≤2, D/E ≤1).
  - 🚀 **Peter Lynch**: Fast growers with high ROE (≥18%) and asset turnover (≥1.0).
  - 🛡️ **Quality Compounders**, **High ROE**, **Low Debt**, and **Dividend Growth**.
- **Peer Percentile & Ranking Engine (`src/analytics/peer.py`)**: Evaluated relative metric percentiles across 11 industry peer groups (`peer_percentiles` table).
- **Power BI Analytical Views (`scripts/create_views.py`)**: Created SQL analytical views (`vw_latest_company_metrics`, `vw_company_summary`) and dataset generator (`scripts/dashboard_dataset_generator.py`).

---

### 🔹 Sprint 4 — Dashboard & Valuation Module
*Focus: Interactive 8-Screen Streamlit Web Application and Valuation Engine*

- **Valuation Module (`src/analytics/valuation.py`)**:
  - **FCF Yield (%)**: `(Free Cash Flow / Market Cap) * 100`.
  - **Sector Median P/E**: Sector-level median P/E across 11 broad sectors.
  - **5-Year Median P/E**: Company-level historical median valuation.
  - **Valuation Flags**: `Caution` (P/E > 1.5× Sector Median), `Discount` (P/E < 0.7× Sector Median), or `Fair`.
  - **Reports Exported**: [output/valuation_summary.xlsx](file:///d:/My%20Drive/Bluestock%20Fintech/nifty100-platform/output/valuation_summary.xlsx) (92 companies) and [output/valuation_flags.csv](file:///d:/My%20Drive/Bluestock%20Fintech/nifty100-platform/output/valuation_flags.csv).

- **Shared Cached Data Loader (`src/dashboard/utils/db.py`)**:
  - Encapsulated database queries with `@st.cache_data(ttl=600)` for fast response times (<0.5s per page load).

- **8 Streamlit Dashboard Screens**:
  1. **🏠 Home Overview (`pages/01_home.py`)**: 6 summary KPI tiles, Plotly sector breakdown donut chart, top-5 quality leaderboard, dynamic sidebar year selector (FY19–FY24).
  2. **🏢 Company Profile (`pages/02_profile.py`)**: Ticker search box, company header card, 6 KPI tiles, 10Y Revenue/Profit bar chart, 10Y ROE/ROCE line chart, Pros & Cons badges (✔/✖).
  3. **⚡ Stock Screener (`pages/03_screener.py`)**: 10 metric sliders, 6 strategy preset buttons, dynamic results table with count label, CSV export button.
  4. **🥊 Peer Comparison (`pages/04_peers.py`)**: 11 peer groups, 8-metric Scatterpolar radar chart, side-by-side KPI comparison table with benchmark highlighting.
  5. **📈 Trend Analysis (`pages/05_trends.py`)**: Search box, multi-metric overlay selector (up to 3 metrics), 10Y line chart with YoY % change data annotations.
  6. **🌐 Sector Analysis (`pages/06_sectors.py`)**: Sector dropdown filter, positioning bubble chart (X=Revenue, Y=ROE, Size=Market Cap, Color=Sub-Sector), sector median KPI bar chart.
  7. **🗺️ Capital Allocation Map (`pages/07_capital.py`)**: Treemap of 92 companies grouped by 8 capital allocation patterns, interactive pattern selector.
  8. **📄 Annual Reports (`pages/08_reports.py`)**: Document repository per company, clickable BSE PDF links, red `Report unavailable` badge handling.

---

## 🛠️ Technology Stack

| Domain | Technologies Used |
| :--- | :--- |
| **Core Platform** | Python 3.12, Pandas, NumPy, SQLite3 |
| **Data Processing & ETL** | OpenPyXL, SQLAlchemy, PyYAML |
| **Analytics & Math** | Custom Ratio Engine, CAGR Engine, Peer Percentile Calculator |
| **Frontend & UI** | Streamlit (v1.60+), Custom CSS |
| **Data Visualization** | Plotly Express, Plotly Graph Objects (Scatterpolar, Treemap, Donut, Bar, Line) |
| **Quality Assurance** | Python `unittest` / Custom Test Suites |

---

## 📁 Repository Structure

```text
nifty100-platform/
│
├── pages/                  # 8 Streamlit Screen Modules
│   ├── 01_home.py          # 🏠 Executive Overview
│   ├── 02_profile.py       # 🏢 Company Profile
│   ├── 03_screener.py      # ⚡ Stock Screener
│   ├── 04_peers.py         # 🥊 Peer Comparison
│   ├── 05_trends.py        # 📈 Multi-Metric Trend Analysis
│   ├── 06_sectors.py       # 🌐 Sector Analysis
│   ├── 07_capital.py       # 🗺️ Capital Allocation Treemap
│   └── 08_reports.py       # 📄 Annual Reports Repository
│
├── src/
│   ├── analytics/          # Core Calculation Modules
│   │   ├── ratio_engine.py # Sprint 2 Financial Ratio Engine
│   │   ├── cagr.py         # Sprint 2 CAGR Calculator
│   │   ├── cashflow_kpis.py# Cash Flow & Capital Allocation
│   │   ├── peer.py         # Sprint 3 Peer Percentile Engine
│   │   └── valuation.py    # Sprint 4 Valuation & FCF Yield Engine
│   │
│   ├── dashboard/          # Dashboard Scaffold & Utilities
│   │   ├── app.py          # Main Streamlit Entry Point
│   │   └── utils/
│   │       └── db.py       # Cached Data Loader (@st.cache_data)
│   │
│   ├── database/           # SQLite Connection & Schema Management
│   └── screener/           # Screener Engine & Investment Presets
│
├── db/                     # SQLite Database & Schema
│   ├── nifty100.db         # SQLite Production Database
│   └── schema.sql          # Relational Database Schema Definition
│
├── datasets/               # Raw Input Excel Datasets
├── supporting_datasets/    # Market Cap, Sectors & Peer Datasets
├── output/                 # Generated Valuation Excel & CSV Reports
├── scripts/                # Utility & View Creation Scripts
├── tests/                  # Verification Test Suites
└── README.md               # Project Documentation
```

---

## 📝 Sprint 4 Retrospective & Technical Findings

- **Data Caching Efficiency**: Applied `@st.cache_data(ttl=600)` across SQLite data loaders in `db.py`. Company profile screen load time measured **< 0.5s** per ticker.
- **Robust Error Handling**: Handled companies with partial financial history gracefully without crashing, displaying clean `N/A` fallbacks.
- **Cross-Directory Compatibility**: Implemented robust `sys.path` resolution ensuring seamless dashboard execution regardless of launcher directory.

---

## 👤 Author & Acknowledgments

**Saranya D**  
*Bluestock Data Engineering Internship*  
