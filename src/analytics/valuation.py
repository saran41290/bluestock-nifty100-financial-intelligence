"""
valuation.py

Valuation Module for Nifty 100 Platform (Sprint 4 - Day 26)

Responsibilities:
-----------------
1. Load market cap, valuation multiples, and sector data.
2. Compute FCF Yield (%) = FCF / Market Cap * 100.
3. Compute sector median P/E for each broad sector (latest year).
4. Compute 5-year median P/E per company.
5. Apply overvaluation/discount flags:
   - Caution: P/E > 1.5 * sector_median_pe
   - Discount: P/E < 0.7 * sector_median_pe
   - Fair: Otherwise
6. Generate output/valuation_summary.xlsx (92 companies) and output/valuation_flags.csv (Caution & Discount).
"""

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np


class ValuationEngine:
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]
        self.project_root = project_root
        self.db_path = self.project_root / "db" / "nifty100.db"
        self.market_cap_path = self.project_root / "supporting_datasets" / "market_cap.xlsx"
        self.sectors_path = self.project_root / "supporting_datasets" / "sectors.xlsx"
        self.output_dir = self.project_root / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        # 1. Load companies info from SQLite
        conn = sqlite3.connect(self.db_path)
        companies_df = pd.read_sql_query("SELECT id AS company_id, company_name FROM companies", conn)
        
        # Load FCF from financial_ratios table in SQLite (latest year per company)
        ratios_df = pd.read_sql_query("""
            SELECT company_id, year, free_cash_flow 
            FROM financial_ratios 
            WHERE year = (SELECT MAX(year) FROM financial_ratios WHERE company_id = financial_ratios.company_id)
        """, conn)
        conn.close()

        # Deduplicate ratios_df by company_id
        ratios_df = ratios_df.sort_values("year").groupby("company_id").last().reset_index()

        # 2. Load market cap data
        mcap_df = pd.read_excel(self.market_cap_path)
        
        # Ensure year is integer/string consistent
        mcap_df['year_str'] = mcap_df['year'].astype(str)
        latest_year_str = str(mcap_df['year'].max())

        # 5-year median PE per company
        five_yr_pe = mcap_df.groupby('company_id')['pe_ratio'].median().reset_index()
        five_yr_pe.rename(columns={'pe_ratio': '5yr_median_PE'}, inplace=True)

        # Filter latest year market cap data
        latest_mcap = mcap_df[mcap_df['year_str'] == latest_year_str].copy()

        # 3. Load sector info
        sectors_df = pd.read_excel(self.sectors_path)
        
        # Merge datasets
        df = pd.merge(companies_df, sectors_df[['company_id', 'broad_sector', 'sub_sector']], on='company_id', how='left')
        df = pd.merge(df, latest_mcap[['company_id', 'market_cap_crore', 'enterprise_value_crore', 'pe_ratio', 'pb_ratio', 'ev_ebitda', 'dividend_yield_pct']], on='company_id', how='left')
        df = pd.merge(df, five_yr_pe, on='company_id', how='left')
        df = pd.merge(df, ratios_df[['company_id', 'free_cash_flow']], on='company_id', how='left')

        # Fallback for missing broad_sector
        df['broad_sector'] = df['broad_sector'].fillna('Other')

        # 4. Compute FCF Yield %
        # FCF Yield = (free_cash_flow / market_cap_crore) * 100
        df['FCF_yield_pct'] = np.where(
            (df['market_cap_crore'].notna()) & (df['market_cap_crore'] > 0) & (df['free_cash_flow'].notna()),
            (df['free_cash_flow'] / df['market_cap_crore']) * 100,
            np.nan
        )
        df['FCF_yield_pct'] = df['FCF_yield_pct'].round(2)

        # 5. Compute sector median P/E
        sector_medians = df.groupby('broad_sector')['pe_ratio'].median().to_dict()
        df['sector_median_PE'] = df['broad_sector'].map(sector_medians)

        # PE vs sector median %
        df['PE_vs_sector_median_pct'] = np.where(
            (df['pe_ratio'].notna()) & (df['sector_median_PE'].notna()) & (df['sector_median_PE'] > 0),
            ((df['pe_ratio'] - df['sector_median_PE']) / df['sector_median_PE']) * 100,
            np.nan
        )
        df['PE_vs_sector_median_pct'] = df['PE_vs_sector_median_pct'].round(2)

        # 6. Apply Overvaluation / Discount flags
        def get_flag(row):
            pe = row['pe_ratio']
            sec_med = row['sector_median_PE']
            if pd.isna(pe) or pd.isna(sec_med) or sec_med <= 0:
                return 'Fair'
            if pe > (sec_med * 1.5):
                return 'Caution'
            elif pe < (sec_med * 0.7):
                return 'Discount'
            else:
                return 'Fair'

        df['flag'] = df.apply(get_flag, axis=1)

        # Format column names for summary file as required:
        # company_id, company_name, sector, P/E, P/B, EV/EBITDA, FCF_yield_pct, 5yr_median_PE, PE_vs_sector_median_pct, flag
        summary_df = pd.DataFrame({
            'company_id': df['company_id'],
            'company_name': df['company_name'],
            'sector': df['broad_sector'],
            'P/E': df['pe_ratio'].round(2),
            'P/B': df['pb_ratio'].round(2),
            'EV/EBITDA': df['ev_ebitda'].round(2),
            'FCF_yield_pct': df['FCF_yield_pct'],
            '5yr_median_PE': df['5yr_median_PE'].round(2),
            'PE_vs_sector_median_pct': df['PE_vs_sector_median_pct'],
            'flag': df['flag']
        })

        # Save summary Excel file
        summary_excel_path = self.output_dir / "valuation_summary.xlsx"
        summary_df.to_excel(summary_excel_path, index=False)
        print(f"Saved {len(summary_df)} rows to {summary_excel_path}")

        # Save valuation flags CSV (Caution & Discount only)
        flags_df = summary_df[summary_df['flag'].isin(['Caution', 'Discount'])].copy()
        flags_csv_path = self.output_dir / "valuation_flags.csv"
        flags_df.to_csv(flags_csv_path, index=False)
        print(f"Saved {len(flags_df)} flagged companies to {flags_csv_path}")

        return summary_df, flags_df


if __name__ == "__main__":
    engine = ValuationEngine()
    engine.run()
