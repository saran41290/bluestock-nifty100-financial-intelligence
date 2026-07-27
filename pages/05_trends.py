"""
05_trends.py - Trend Analysis Screen

Features:
- Company Search Box (autocomplete with 92 tickers)
- Multi-Metric Selector (overlay up to 3 metrics)
- 10-Year Line Chart with YoY % Change annotations on data points using Plotly
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.dashboard.utils.db import get_companies, get_pl, get_bs, get_cf, get_ratios

st.set_page_config(page_title="Nifty 100 Analytics - Trend Analysis", layout="wide")

st.title("📈 Multi-Metric 10-Year Trend Analysis")
st.markdown("Analyze historical performance, growth trajectories, and year-over-year % changes across financial metrics.")

companies_df = get_companies()
company_options = [f"{row['id']} - {row['company_name']}" for _, row in companies_df.iterrows()]

col_search, col_metrics = st.columns([1, 2])

with col_search:
    search_input = st.selectbox("Select Company", company_options, index=0)
    selected_ticker = search_input.split(" - ")[0].strip()

# Metric dictionary mapping display name to dataframe column and source table
metric_dict = {
    "Sales / Revenue (Cr)": ("sales", "pl"),
    "Net Profit (Cr)": ("net_profit", "pl"),
    "Operating Profit (Cr)": ("operating_profit", "pl"),
    "Operating Profit Margin (%)": ("opm_percentage", "pl"),
    "EPS (₹)": ("eps", "pl"),
    "Total Assets (Cr)": ("total_assets", "bs"),
    "Borrowings / Debt (Cr)": ("borrowings", "bs"),
    "Operating Cash Flow (Cr)": ("operating_activity", "cf"),
    "ROE (%)": ("return_on_equity_pct", "ratio"),
    "ROCE (%)": ("return_on_capital_employed_pct", "ratio"),
    "Debt to Equity": ("debt_to_equity", "ratio")
}

with col_metrics:
    selected_metrics = st.multiselect(
        "Select up to 3 Metrics to Overlay",
        options=list(metric_dict.keys()),
        default=["Sales / Revenue (Cr)", "Net Profit (Cr)"],
        max_selections=3
    )

if not selected_metrics:
    st.info("Please select at least one metric to display trends.")
    st.stop()

# Fetch history data tables
pl_df = get_pl(selected_ticker)
bs_df = get_bs(selected_ticker)
cf_df = get_cf(selected_ticker)
ratio_df = get_ratios(selected_ticker)

# Combine historical metrics into a single master time series dataframe
history_map = {}

for m_name in selected_metrics:
    col_name, source = metric_dict[m_name]
    if source == "pl" and not pl_df.empty:
        s_df = pl_df[['year', col_name]].copy()
    elif source == "bs" and not bs_df.empty:
        s_df = bs_df[['year', col_name]].copy()
    elif source == "cf" and not cf_df.empty:
        s_df = cf_df[['year', col_name]].copy()
    elif source == "ratio" and not ratio_df.empty:
        s_df = ratio_df[['year', col_name]].copy()
    else:
        s_df = pd.DataFrame(columns=['year', col_name])
    
    s_df.rename(columns={col_name: m_name}, inplace=True)
    history_map[m_name] = s_df

# Merge time-series dataframes on 'year'
if history_map:
    merged_ts = list(history_map.values())[0]
    for df in list(history_map.values())[1:]:
        merged_ts = pd.merge(merged_ts, df, on='year', how='outer')
    
    merged_ts = merged_ts.sort_values('year').dropna(subset=['year'])
else:
    merged_ts = pd.DataFrame()

if merged_ts.empty:
    st.warning("No historical metric data available for the selected company.")
    st.stop()

st.markdown("---")

# Plotly Multi-Metric Line Chart with YoY Annotations
fig = go.Figure()
colors = ['#1f77b4', '#2ca02c', '#ff7f0e']

for idx, m_name in enumerate(selected_metrics):
    if m_name not in merged_ts.columns:
        continue
    
    series = merged_ts[m_name].astype(float)
    years = merged_ts['year'].tolist()
    
    # Calculate YoY % change
    yoy_pct = series.pct_change() * 100
    
    # Format hover text and data annotations
    hover_texts = []
    text_labels = []
    
    for val, yoy in zip(series, yoy_pct):
        if pd.isna(val):
            hover_texts.append("N/A")
            text_labels.append("")
        elif pd.isna(yoy):
            hover_texts.append(f"Value: {val:,.1f}")
            text_labels.append(f"{val:,.1f}")
        else:
            sign = "+" if yoy >= 0 else ""
            hover_texts.append(f"Value: {val:,.1f}<br>YoY: {sign}{yoy:.1f}%")
            text_labels.append(f"{val:,.1f} ({sign}{yoy:.0f}%)")

    fig.add_trace(go.Scatter(
        x=years,
        y=series,
        mode='lines+markers+text',
        name=m_name,
        text=text_labels,
        textposition="top center",
        hovertext=hover_texts,
        hoverinfo="text+name+x",
        line=dict(color=colors[idx % len(colors)], width=3),
        marker=dict(size=8)
    ))

fig.update_layout(
    title=f"10-Year Historical Trends for {selected_ticker}",
    xaxis_title="Financial Year",
    yaxis_title="Metric Value",
    height=500,
    margin=dict(t=50, b=40, l=40, r=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Data Table Display below chart
st.markdown("##### Historical Data Table")
st.dataframe(merged_ts.set_index('year'), use_container_width=True)
