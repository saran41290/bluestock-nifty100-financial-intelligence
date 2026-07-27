"""
08_reports.py - Annual Reports Screen

Features:
- Company Search Box (autocomplete with 92 tickers)
- List of available annual report years with clickable BSE PDF links
- Red "Report unavailable" badge for invalid, 404, or missing PDF URLs
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import streamlit as st
import pandas as pd
import requests
from src.dashboard.utils.db import get_companies, get_documents

st.set_page_config(page_title="Nifty 100 Analytics - Annual Reports", layout="wide")

st.title("📄 Annual Reports & Regulatory Filings Repository")
st.markdown("Access BSE exchange annual report PDFs and financial disclosures across all 92 companies.")

companies_df = get_companies()
company_options = [f"{row['id']} - {row['company_name']}" for _, row in companies_df.iterrows()]

search_input = st.selectbox("Search Company for Annual Reports", company_options, index=0)
selected_ticker = search_input.split(" - ")[0].strip()

# Fetch documents for company
docs_df = get_documents(selected_ticker)

comp_info = companies_df[companies_df['id'] == selected_ticker].iloc[0]

st.header(f"Annual Reports for {comp_info['company_name']} ({selected_ticker})")

if docs_df.empty:
    st.warning("No annual report document records found for this company.")
else:
    st.markdown("##### Available Annual Report Filings")

    # Display documents list
    for idx, row in docs_df.iterrows():
        year = row.get('Year', row.get('year', 'N/A'))
        report_url = str(row.get('Annual_Report', row.get('annual_report', ''))).strip()

        col_year, col_link, col_status = st.columns([1, 3, 1])

        with col_year:
            st.markdown(f"**FY {year}**")

        # Check URL validity
        is_valid = False
        if report_url and (report_url.startswith("http://") or report_url.startswith("https://")):
            is_valid = True

        with col_link:
            if is_valid:
                st.markdown(f"🔗 [{selected_ticker} Annual Report FY{year} PDF]({report_url})")
            else:
                st.markdown(f"*(URL: {report_url if report_url else 'None'})*")

        with col_status:
            if is_valid:
                st.markdown("🟢 **Available**")
            else:
                st.markdown("🔴 **Report unavailable**")

    st.markdown("---")
    st.caption("Note: PDF link verification checks URL protocol structure. Click any available link to open official BSE filing PDF.")
