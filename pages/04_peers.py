"""
04_peers.py - Peer Comparison Screen

Features:
- Peer Group Dropdown (11 groups)
- Radar Chart (plotly.graph_objects.Scatterpolar) comparing selected company vs peer group average across 8 metrics
- Side-by-Side KPI Comparison Table highlighting benchmark company row
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
from src.dashboard.utils.db import get_companies, get_ratios, get_peers, get_valuation

st.set_page_config(page_title="Nifty 100 Analytics - Peer Comparison", layout="wide")

st.title("🥊 Peer Group Comparison & Relative Valuation")

peers_df = get_peers()

if peers_df.empty or 'peer_group_name' not in peers_df.columns:
    st.warning("Peer group dataset not available.")
    st.stop()

peer_groups = sorted(peers_df['peer_group_name'].dropna().unique().tolist())

col_group, col_comp = st.columns([1, 1])

with col_group:
    selected_group = st.selectbox("Select Peer Group", peer_groups, index=0)

# Filter peer group companies
group_companies = peers_df[peers_df['peer_group_name'] == selected_group].copy()
company_list = group_companies['company_id'].tolist()

with col_comp:
    selected_ticker = st.selectbox("Select Target Company", company_list, index=0)

# Fetch financial data for peer companies
all_companies = get_companies()
ratios_df = get_ratios(year="2024")
if ratios_df.empty:
    ratios_df = get_ratios()

# Filter latest ratios for group
group_ratios = ratios_df[ratios_df['company_id'].isin(company_list)].sort_values('year').groupby('company_id').last().reset_index()

# Merge metadata
group_data = pd.merge(group_companies, all_companies[['id', 'company_name', 'broad_sector']], left_on='company_id', right_on='id', how='left')
group_data = pd.merge(group_data, group_ratios, on='company_id', how='left')

# Prepare 8 metrics for comparison
# 1. ROE (%), 2. ROCE (%), 3. Net Profit Margin (%), 4. D/E, 5. Interest Coverage, 6. Asset Turnover, 7. Rev CAGR 5Y (%), 8. Composite Score
metrics_keys = [
    'return_on_equity_pct',
    'return_on_capital_employed_pct',
    'net_profit_margin_pct',
    'debt_to_equity',
    'interest_coverage',
    'asset_turnover',
    'revenue_cagr_5yr',
    'composite_quality_score'
]

metrics_labels = [
    'ROE (%)',
    'ROCE (%)',
    'NPM (%)',
    'D/E (inv)',
    'ICR',
    'Asset Turnover',
    'Rev CAGR 5Y (%)',
    'Quality Score'
]

# Clean up metric values
for m in metrics_keys:
    if m not in group_data.columns:
        group_data[m] = np.nan
    group_data[m] = pd.to_numeric(group_data[m], errors='coerce').fillna(0.0)

# Invert D/E for radar chart so higher is better
group_data['de_radar'] = np.where(group_data['debt_to_equity'] > 0, 1.0 / (1.0 + group_data['debt_to_equity']), 1.0)

radar_metrics = [
    'return_on_equity_pct',
    'return_on_capital_employed_pct',
    'net_profit_margin_pct',
    'de_radar',
    'interest_coverage',
    'asset_turnover',
    'revenue_cagr_5yr',
    'composite_quality_score'
]

# Calculate averages for radar normalization
target_row = group_data[group_data['company_id'] == selected_ticker]

if not target_row.empty:
    target_vals = target_row.iloc[0][radar_metrics].values.astype(float)
    avg_vals = group_data[radar_metrics].mean().values.astype(float)

    # Normalize metrics 0 to 100 relative to max in group for nice radar chart
    max_vals = group_data[radar_metrics].max().values.astype(float)
    max_vals = np.where(max_vals == 0, 1.0, max_vals)

    target_norm = (target_vals / max_vals) * 100
    avg_norm = (avg_vals / max_vals) * 100

    st.markdown("---")
    r_col, t_col = st.columns([1, 1])

    with r_col:
        st.subheader(f"Radar Analysis: {selected_ticker} vs Group Average")
        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=target_norm,
            theta=metrics_labels,
            fill='toself',
            name=f"{selected_ticker} (Target)",
            line=dict(color='#1f77b4', width=3)
        ))

        fig_radar.add_trace(go.Scatterpolar(
            r=avg_norm,
            theta=metrics_labels,
            fill='toself',
            name=f"{selected_group} Average",
            line=dict(color='#ff7f0e', width=2, dash='dash')
        ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=420,
            margin=dict(t=40, b=40, l=40, r=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with t_col:
        st.subheader(f"Group Companies Summary ({len(group_data)} companies)")
        
        table_df = pd.DataFrame({
            'Ticker': group_data['company_id'],
            'Company Name': group_data['company_name'],
            'Is Benchmark': group_data['is_benchmark'].map({True: '⭐ Benchmark', False: 'Peer'}),
            'ROE (%)': group_data['return_on_equity_pct'].round(1),
            'D/E': group_data['debt_to_equity'].round(2),
            'ICR': group_data['interest_coverage'].round(1),
            'Quality Score': group_data['composite_quality_score'].round(2)
        })

        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True
        )
