"""
03_screener.py - Screener Screen

Features:
- 10 Metric Sliders in sidebar: ROE min, D/E max, FCF min, Revenue CAGR min, PAT CAGR min, OPM min, P/E max, P/B max, Dividend Yield min, ICR min
- 6 Preset Strategy Buttons: Quality, Value, Growth, Dividend, Debt-Free, Turnaround
- Dynamic Live Results Table
- CSV Export Download Button
- Result Count Label
"""

import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import streamlit as st
import pandas as pd
import numpy as np
from src.dashboard.utils.db import get_companies, get_ratios, get_valuation

st.set_page_config(page_title="Nifty 100 Analytics - Screener", layout="wide")

st.title("⚡ Interactive Stock Screener")
st.markdown("Filter all 92 Nifty 100 companies based on customized fundamental parameters and investment presets.")

# Initialize session state for sliders if not set
default_values = {
    'roe_min': 0.0,
    'de_max': 5.0,
    'fcf_min': -5000.0,
    'rev_cagr_min': -50.0,
    'pat_cagr_min': -50.0,
    'opm_min': 0.0,
    'pe_max': 150.0,
    'pb_max': 50.0,
    'div_yield_min': 0.0,
    'icr_min': 0.0
}

for k, v in default_values.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Preset Callback Functions
def apply_preset(preset_name):
    if preset_name == "Quality":
        st.session_state['roe_min'] = 18.0
        st.session_state['de_max'] = 0.5
        st.session_state['fcf_min'] = 0.0
        st.session_state['opm_min'] = 15.0
        st.session_state['icr_min'] = 4.0
    elif preset_name == "Value":
        st.session_state['pe_max'] = 20.0
        st.session_state['pb_max'] = 2.5
        st.session_state['roe_min'] = 12.0
        st.session_state['de_max'] = 1.0
    elif preset_name == "Growth":
        st.session_state['rev_cagr_min'] = 15.0
        st.session_state['pat_cagr_min'] = 15.0
        st.session_state['roe_min'] = 15.0
    elif preset_name == "Dividend":
        st.session_state['div_yield_min'] = 2.0
        st.session_state['roe_min'] = 12.0
        st.session_state['de_max'] = 1.0
    elif preset_name == "Debt-Free":
        st.session_state['de_max'] = 0.05
        st.session_state['icr_min'] = 10.0
        st.session_state['roe_min'] = 15.0
    elif preset_name == "Turnaround":
        st.session_state['pat_cagr_min'] = 20.0
        st.session_state['fcf_min'] = 0.0
        st.session_state['opm_min'] = 10.0
    elif preset_name == "Reset":
        for k, v in default_values.items():
            st.session_state[k] = v

# Top Presets Bar
st.markdown("##### Quick Investment Presets")
pcol1, pcol2, pcol3, pcol4, pcol5, pcol6, pcol7 = st.columns(7)
with pcol1:
    st.button("🏆 Quality", on_click=apply_preset, args=("Quality",), use_container_width=True)
with pcol2:
    st.button("💎 Value", on_click=apply_preset, args=("Value",), use_container_width=True)
with pcol3:
    st.button("🚀 Growth", on_click=apply_preset, args=("Growth",), use_container_width=True)
with pcol4:
    st.button("💰 Dividend", on_click=apply_preset, args=("Dividend",), use_container_width=True)
with pcol5:
    st.button("🛡️ Debt-Free", on_click=apply_preset, args=("Debt-Free",), use_container_width=True)
with pcol6:
    st.button("🔄 Turnaround", on_click=apply_preset, args=("Turnaround",), use_container_width=True)
with pcol7:
    st.button("🧹 Reset", on_click=apply_preset, args=("Reset",), use_container_width=True)

st.markdown("---")

# Sidebar Sliders
st.sidebar.header("Filter Criteria Sliders")
st.sidebar.slider("Min ROE (%)", 0.0, 50.0, key='roe_min')
st.sidebar.slider("Max Debt / Equity", 0.0, 5.0, key='de_max')
st.sidebar.slider("Min Free Cash Flow (Cr)", -5000.0, 50000.0, step=500.0, key='fcf_min')
st.sidebar.slider("Min Revenue CAGR 5Y (%)", -50.0, 100.0, key='rev_cagr_min')
st.sidebar.slider("Min PAT CAGR 5Y (%)", -50.0, 100.0, key='pat_cagr_min')
st.sidebar.slider("Min Operating Profit Margin (%)", 0.0, 100.0, key='opm_min')
st.sidebar.slider("Max P/E Ratio", 0.0, 150.0, key='pe_max')
st.sidebar.slider("Max P/B Ratio", 0.0, 50.0, key='pb_max')
st.sidebar.slider("Min Dividend Yield (%)", 0.0, 10.0, key='div_yield_min')
st.sidebar.slider("Min Interest Coverage Ratio", 0.0, 50.0, key='icr_min')

# Fetch Data & Build Master Dataset
companies_df = get_companies()
ratios_df = get_ratios(year="2024")
if ratios_df.empty:
    ratios_df = get_ratios()

# Deduplicate ratios to 1 row per company (latest year)
ratios_latest = ratios_df.sort_values("year").groupby("company_id").last().reset_index()
valuation_df = get_valuation()

master = pd.merge(companies_df, ratios_latest, left_on='id', right_on='company_id', how='left')
master = pd.merge(master, valuation_df[['company_id', 'P/E', 'P/B', 'FCF_yield_pct', 'flag']], left_on='id', right_on='company_id', how='left')

# Populate metrics with defaults if missing
master['roe'] = master['return_on_equity_pct'].fillna(master['roe_percentage']).fillna(0.0)
master['de'] = master['debt_to_equity'].fillna(0.0)
master['fcf'] = master['free_cash_flow'].fillna(0.0)
master['rev_cagr'] = master['revenue_cagr_5yr'].fillna(0.0)
master['pat_cagr'] = master['pat_cagr_5yr'].fillna(0.0)
master['opm'] = master['operating_profit_margin_pct'].fillna(0.0)
master['pe'] = master['pe_ratio'].fillna(master['P/E']).fillna(999.0)
master['pb'] = master['pb_ratio'].fillna(master['P/B']).fillna(999.0)
master['div_yield'] = master['dividend_yield_pct'].fillna(0.0)
master['icr'] = master['interest_coverage'].fillna(999.0)
master['score'] = master['composite_quality_score'].fillna(master['roe']).round(2)

# Apply Filter Conditions
filtered = master[
    (master['roe'] >= st.session_state['roe_min']) &
    (master['de'] <= st.session_state['de_max']) &
    (master['fcf'] >= st.session_state['fcf_min']) &
    (master['rev_cagr'] >= st.session_state['rev_cagr_min']) &
    (master['pat_cagr'] >= st.session_state['pat_cagr_min']) &
    (master['opm'] >= st.session_state['opm_min']) &
    (master['pe'] <= st.session_state['pe_max']) &
    (master['pb'] <= st.session_state['pb_max']) &
    (master['div_yield'] >= st.session_state['div_yield_min']) &
    (master['icr'] >= st.session_state['icr_min'])
].copy()

# Header Result Count Label
st.markdown(f"#### 🔍 **{len(filtered)}** companies match your filters (out of {len(companies_df)})")

if not filtered.empty:
    filtered_display = pd.DataFrame({
        'company_id': filtered['id'],
        'company_name': filtered['company_name'],
        'sector': filtered['broad_sector'],
        'composite_score': filtered['score'],
        'ROE (%)': filtered['roe'].round(1),
        'D/E': filtered['de'].round(2),
        'FCF (Cr)': filtered['fcf'].round(0),
        'Rev CAGR 5Y (%)': filtered['rev_cagr'].round(1),
        'PAT CAGR 5Y (%)': filtered['pat_cagr'].round(1),
        'OPM (%)': filtered['opm'].round(1),
        'P/E': filtered['pe'].replace(999.0, np.nan).round(1),
        'P/B': filtered['pb'].replace(999.0, np.nan).round(1),
        'Div Yield (%)': filtered['div_yield'].round(2),
        'Valuation Flag': filtered['flag'].fillna('Fair')
    }).sort_values(by='composite_score', ascending=False)

    st.dataframe(filtered_display, use_container_width=True, hide_index=True)

    # CSV Download Button
    csv_data = filtered_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Results to CSV",
        data=csv_data,
        file_name="screener_results.csv",
        mime="text/csv"
    )
else:
    st.info("No companies match the current filter sliders. Try relaxing the filter constraints or clicking 'Reset'.")
