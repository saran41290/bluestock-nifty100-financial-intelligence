"""
06_sectors.py - Sector Analysis Screen

Features:
- Sector Dropdown selector (11 Broad Sectors or All)
- Bubble Chart (Plotly scatter): X = Revenue, Y = ROE, Bubble Size = Market Cap, Colour = Sub-Sector
- Sector Median KPI Bar Chart below bubble chart
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_ratios, get_valuation

st.set_page_config(page_title="Nifty 100 Analytics - Sector Analysis", layout="wide")

st.title("🌐 Sector Performance & Positioning Analysis")
st.markdown("Analyze sector dynamics, market cap weighting, profitability distribution, and median benchmark KPIs.")

companies_df = get_companies()
ratios_df = get_ratios(year="2024")
if ratios_df.empty:
    ratios_df = get_ratios()

# Deduplicate ratios to latest per company
ratios_latest = ratios_df.sort_values("year").groupby("company_id").last().reset_index()
valuation_df = get_valuation()

# Merge into dataset
sector_master = pd.merge(companies_df, ratios_latest, left_on='id', right_on='company_id', how='left')
sector_master = pd.merge(sector_master, valuation_df[['company_id', 'P/E', 'FCF_yield_pct']], left_on='id', right_on='company_id', how='left')

# Prepare Bubble Chart Variables
sector_master['Revenue'] = sector_master['revenue_cagr_5yr'].fillna(0)  # default
if 'sales' in sector_master.columns:
    sector_master['Revenue'] = sector_master['sales'].fillna(1000.0)

sector_master['ROE'] = sector_master['return_on_equity_pct'].fillna(sector_master['roe_percentage']).fillna(10.0)
sector_master['Market_Cap'] = sector_master['market_cap_crore'].fillna(10000.0) if 'market_cap_crore' in sector_master.columns else 10000.0
sector_master['Market_Cap'] = np.where(sector_master['Market_Cap'] <= 0, 1000.0, sector_master['Market_Cap'])

# Filter by Sector Dropdown
sector_list = ["All Sectors"] + sorted(companies_df['broad_sector'].dropna().unique().tolist())
selected_sector = st.selectbox("Filter by Sector", sector_list, index=0)

if selected_sector != "All Sectors":
    filtered_df = sector_master[sector_master['broad_sector'] == selected_sector].copy()
else:
    filtered_df = sector_master.copy()

st.markdown("---")

# -----------------------------------------------------
# Bubble Chart
# -----------------------------------------------------
st.subheader(f"Bubble Chart: Revenue vs ROE ({selected_sector})")
st.caption("Bubble Size = Market Cap (Cr), Color = Sub-Sector")

if not filtered_df.empty:
    fig_bubble = px.scatter(
        filtered_df,
        x="Revenue",
        y="ROE",
        size="Market_Cap",
        color="sub_sector",
        hover_name="company_name",
        hover_data=["id", "broad_sector", "sub_sector", "Revenue", "ROE"],
        text="id",
        size_max=60,
        height=500,
        title=f"Company Positioning Matrix - {selected_sector}"
    )
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(
        xaxis_title="Latest Sales / Revenue (₹ Cr)",
        yaxis_title="Return on Equity - ROE (%)",
        margin=dict(t=40, b=40, l=40, r=40)
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
else:
    st.info("No company data available for the selected sector.")

st.markdown("---")

# -----------------------------------------------------
# Sector Median KPI Bar Chart
# -----------------------------------------------------
st.subheader("Sector Median KPI Comparison")

sector_summary = sector_master.groupby('broad_sector').agg({
    'id': 'count',
    'ROE': 'median',
    'return_on_capital_employed_pct': 'median',
    'net_profit_margin_pct': 'median',
    'debt_to_equity': 'median'
}).reset_index()

sector_summary.columns = ['Broad Sector', 'Count', 'Median ROE (%)', 'Median ROCE (%)', 'Median NPM (%)', 'Median D/E']

# Bar chart of Median ROE across all sectors
fig_bar = px.bar(
    sector_summary.sort_values(by='Median ROE (%)', ascending=False),
    x='Broad Sector',
    y='Median ROE (%)',
    color='Median ROE (%)',
    text='Median ROE (%)',
    color_continuous_scale='Viridis',
    height=400,
    title="Median ROE (%) across Broad Sectors"
)
fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_bar.update_layout(xaxis_tickangle=-45, margin=dict(t=40, b=80, l=40, r=40))
st.plotly_chart(fig_bar, use_container_width=True)

# Detailed Sector Median Data Table
with st.expander("📊 View Detailed Sector Summary Table"):
    st.dataframe(sector_summary, use_container_width=True, hide_index=True)
