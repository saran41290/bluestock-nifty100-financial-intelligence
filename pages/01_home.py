"""
01_home.py - Home Screen

Features:
- Sidebar year selector (2019 to 2024)
- 6 Summary KPI tiles at top: Average ROE, Median P/E, Median D/E, Total Companies, Median Revenue CAGR 5yr, Debt-Free Companies Count
- Sector Breakdown Donut Chart using Plotly (11 sectors with company count)
- Top-5 Companies by Composite Quality Score Table
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
from src.dashboard.utils.db import get_companies, get_ratios, get_sectors, get_valuation

st.set_page_config(page_title="Nifty 100 Analytics - Home", layout="wide")

st.title("📊 Nifty 100 Financial Intelligence — Executive Overview")
st.markdown("Comprehensive fundamental analysis, quality scoring, and valuation across 92 Nifty 100 companies.")

# Sidebar Year Selector
st.sidebar.header("Filter Options")
years = ["2024", "2023", "2022", "2021", "2020", "2019"]
selected_year = st.sidebar.selectbox("Select Financial Year", years, index=0)

# Fetch Data
companies_df = get_companies()
ratios_df = get_ratios(year=selected_year)
valuation_df = get_valuation()

# Merge companies with ratios for selected year
merged_df = pd.merge(companies_df, ratios_df, left_on='id', right_on='company_id', how='left')

# Calculate KPI values
total_companies = len(companies_df)

avg_roe = merged_df['return_on_equity_pct'].mean()
if pd.isna(avg_roe):
    avg_roe = merged_df['roe_percentage'].mean()

median_pe = merged_df['pe_ratio'].median() if 'pe_ratio' in merged_df.columns else np.nan
if pd.isna(median_pe) and 'P/E' in valuation_df.columns:
    median_pe = valuation_df['P/E'].median()

median_de = merged_df['debt_to_equity'].median() if 'debt_to_equity' in merged_df.columns else 0.0

median_cagr_5yr = merged_df['revenue_cagr_5yr'].median() if 'revenue_cagr_5yr' in merged_df.columns else 0.0

debt_free_count = (merged_df['debt_to_equity'] <= 0.05).sum() if 'debt_to_equity' in merged_df.columns else 0

# Display 6 KPI Tiles
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Total Companies", f"{total_companies}")
with col2:
    st.metric("Average ROE", f"{avg_roe:.1f}%" if pd.notna(avg_roe) else "N/A")
with col3:
    st.metric("Median P/E", f"{median_pe:.1f}x" if pd.notna(median_pe) else "N/A")
with col4:
    st.metric("Median D/E", f"{median_de:.2f}" if pd.notna(median_de) else "N/A")
with col5:
    st.metric("Median Rev CAGR 5Y", f"{median_cagr_5yr:.1f}%" if pd.notna(median_cagr_5yr) else "N/A")
with col6:
    st.metric("Debt-Free Count", f"{debt_free_count}")

st.markdown("---")

# Layout: Donut Chart & Top 5 Table
chart_col, table_col = st.columns([1, 1])

with chart_col:
    st.subheader("Sector Breakdown")
    sector_counts = companies_df['broad_sector'].value_counts().reset_index()
    sector_counts.columns = ['Broad Sector', 'Company Count']
    
    fig = px.pie(
        sector_counts,
        names='Broad Sector',
        values='Company Count',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Distribution across 11 Broad Sectors"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False, margin=dict(t=40, b=20, l=10, r=10), height=400)
    st.plotly_chart(fig, use_container_width=True)

with table_col:
    st.subheader(f"Top 5 Companies by Quality Score ({selected_year})")
    score_col = 'composite_quality_score'
    if score_col not in merged_df.columns or merged_df[score_col].isna().all():
        merged_df[score_col] = merged_df['roe_percentage']

    top5 = merged_df.sort_values(by=score_col, ascending=False).head(5)
    
    display_df = pd.DataFrame({
        'Rank': [1, 2, 3, 4, 5],
        'Ticker': top5['id'],
        'Company Name': top5['company_name'],
        'Sector': top5['broad_sector'],
        'ROE (%)': top5['return_on_equity_pct'].fillna(top5['roe_percentage']).round(1),
        'Quality Score': top5[score_col].round(2)
    })
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
