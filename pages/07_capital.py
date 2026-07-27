"""
07_capital.py - Capital Allocation Map Screen

Features:
- Treemap of all 92 companies grouped by 8 Capital Allocation Patterns (Plotly treemap)
- Interactive pattern selection showing filtered list of companies in that pattern
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
from src.dashboard.utils.db import get_companies, get_ratios

st.set_page_config(page_title="Nifty 100 Analytics - Capital Allocation Map", layout="wide")

st.title("🗺️ Capital Allocation Pattern Map")
st.markdown("Visualize corporate capital deployment strategies, reinvestment rates, dividend payouts, and balance sheet deleveraging across all 92 Nifty 100 companies.")

companies_df = get_companies()
ratios_df = get_ratios(year="2024")
if ratios_df.empty:
    ratios_df = get_ratios()

# Deduplicate to latest year
ratios_latest = ratios_df.sort_values("year").groupby("company_id").last().reset_index()

master = pd.merge(companies_df, ratios_latest, left_on='id', right_on='company_id', how='left')

# Assign default capital allocation pattern if null
def assign_pattern(row):
    alloc = row.get('capital_allocation')
    if pd.notna(alloc) and str(alloc).strip():
        return str(alloc).strip()
    
    roe = row.get('return_on_equity_pct', row.get('roe_percentage', 0))
    de = row.get('debt_to_equity', 0)
    fcf = row.get('free_cash_flow', 0)
    
    if roe >= 18 and de <= 0.3 and fcf > 0:
        return "High Reinvestment Compounder"
    elif de > 0.8:
        return "Deleveraging / Debt Paydown"
    elif fcf > 1000 and roe >= 12:
        return "Moderate Growth Cash Generator"
    elif fcf < 0:
        return "Capital Intensive Reinvestor"
    else:
        return "Conservative Allocator"

master['Pattern'] = master.apply(assign_pattern, axis=1)

# Add market cap weight for box size in treemap
master['Weight'] = master['market_cap_crore'].fillna(10000.0) if 'market_cap_crore' in master.columns else 10000.0
master['Weight'] = np.where(master['Weight'] <= 0, 1000.0, master['Weight'])

st.markdown("---")

# -----------------------------------------------------
# Plotly Treemap
# -----------------------------------------------------
st.subheader("Treemap of Nifty 100 Companies by Capital Allocation Pattern")

fig_treemap = px.treemap(
    master,
    path=['Pattern', 'broad_sector', 'id'],
    values='Weight',
    color='Pattern',
    hover_name='company_name',
    color_discrete_sequence=px.colors.qualitative.Pastel,
    height=550,
    title="Corporate Capital Deployment Map"
)
fig_treemap.update_traces(textinfo="label+value")
fig_treemap.update_layout(margin=dict(t=40, b=20, l=10, r=10))

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------
# Filtered Company List by Pattern
# -----------------------------------------------------
st.subheader("Explore Companies by Capital Allocation Pattern")

pattern_options = ["All Patterns"] + sorted(master['Pattern'].unique().tolist())
selected_pattern = st.selectbox("Select Capital Allocation Pattern", pattern_options, index=0)

if selected_pattern != "All Patterns":
    filtered_companies = master[master['Pattern'] == selected_pattern].copy()
else:
    filtered_companies = master.copy()

st.markdown(f"#### Showing **{len(filtered_companies)}** companies under **'{selected_pattern}'**")

display_df = pd.DataFrame({
    'Ticker': filtered_companies['id'],
    'Company Name': filtered_companies['company_name'],
    'Broad Sector': filtered_companies['broad_sector'],
    'Capital Allocation Pattern': filtered_companies['Pattern'],
    'ROE (%)': filtered_companies['return_on_equity_pct'].fillna(filtered_companies['roe_percentage']).round(1),
    'D/E Ratio': filtered_companies['debt_to_equity'].round(2),
    'FCF (Cr)': filtered_companies['free_cash_flow'].round(0) if 'free_cash_flow' in filtered_companies.columns else np.nan
})

st.dataframe(display_df, use_container_width=True, hide_index=True)
