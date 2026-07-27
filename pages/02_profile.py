"""
02_profile.py - Company Profile Screen

Features:
- Search box / dropdown with company name / ticker
- Company Card: Name, Sector, Sub-Sector, Ticker, About Description
- 6 KPI Tiles: ROE, ROCE, Net Profit Margin, D/E, Revenue CAGR 5yr, FCF (latest year)
- 10-Year Bar Chart: Revenue & Net Profit (Plotly)
- 10-Year Dual-Axis Line Chart: ROE & ROCE (Plotly)
- Pros and Cons badges (green check / red cross)
- Friendly fallback if ticker not found
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
from plotly.subplots import make_subplots
from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_bs,
    get_cf,
    get_prosandcons,
    get_valuation
)

st.set_page_config(page_title="Nifty 100 Analytics - Company Profile", layout="wide")

st.title("🏢 Company Detailed Profile")

companies_df = get_companies()

# Create options list formatted as "TICKER - Company Name"
company_options = [f"{row['id']} - {row['company_name']}" for _, row in companies_df.iterrows()]

search_input = st.selectbox(
    "Search Company (Type Ticker or Name)",
    options=company_options,
    index=0
)

# Extract ticker
selected_ticker = search_input.split(" - ")[0].strip() if search_input else None

# Filter company record
comp_match = companies_df[companies_df['id'].astype(str).str.upper() == str(selected_ticker).upper()]

if comp_match.empty:
    st.warning("⚠️ Ticker not found — please try another")
else:
    company = comp_match.iloc[0]
    
    # -----------------------------------------------------
    # Company Card Header
    # -----------------------------------------------------
    card_col1, card_col2 = st.columns([3, 1])
    with card_col1:
        st.header(f"{company['company_name']} ({company['id']})")
        st.markdown(f"**Broad Sector:** {company.get('broad_sector', 'N/A')}  |  **Sub-Sector:** {company.get('sub_sector', 'N/A')}  |  **NSE Ticker:** `{company['id']}`")
        if pd.notna(company.get('about_company')) and company['about_company']:
            st.info(f"**About:** {company['about_company']}")
    with card_col2:
        if pd.notna(company.get('website')) and company['website']:
            st.markdown(f"🌐 [Company Website]({company['website']})")
        if pd.notna(company.get('nse_profile')) and company['nse_profile']:
            st.markdown(f"📈 [NSE Profile]({company['nse_profile']})")

    st.markdown("---")

    # Fetch financial histories
    pl_df = get_pl(selected_ticker)
    ratios_df = get_ratios(selected_ticker)
    valuation_df = get_valuation(selected_ticker)
    prosandcons_df = get_prosandcons(selected_ticker)

    # -----------------------------------------------------
    # 6 KPI Tiles
    # -----------------------------------------------------
    latest_ratio = ratios_df.iloc[-1] if not ratios_df.empty else {}
    latest_val = valuation_df.iloc[0] if not valuation_df.empty else {}

    roe_val = latest_ratio.get('return_on_equity_pct', company.get('roe_percentage'))
    roce_val = latest_ratio.get('return_on_capital_employed_pct', company.get('roce_percentage'))
    npm_val = latest_ratio.get('net_profit_margin_pct')
    de_val = latest_ratio.get('debt_to_equity')
    cagr_val = latest_ratio.get('revenue_cagr_5yr')
    fcf_val = latest_ratio.get('free_cash_flow')

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("ROE (%)", f"{roe_val:.1f}%" if pd.notna(roe_val) else "N/A")
    with col2:
        st.metric("ROCE (%)", f"{roce_val:.1f}%" if pd.notna(roce_val) else "N/A")
    with col3:
        st.metric("Net Profit Margin", f"{npm_val:.1f}%" if pd.notna(npm_val) else "N/A")
    with col4:
        st.metric("Debt-to-Equity", f"{de_val:.2f}" if pd.notna(de_val) else "N/A")
    with col5:
        st.metric("Rev CAGR (5Y)", f"{cagr_val:.1f}%" if pd.notna(cagr_val) else "N/A")
    with col6:
        st.metric("Latest FCF (Cr)", f"₹{fcf_val:.0f}" if pd.notna(fcf_val) else "N/A")

    st.markdown("---")

    # -----------------------------------------------------
    # 10-Year Charts
    # -----------------------------------------------------
    chart_c1, chart_c2 = st.columns(2)

    with chart_c1:
        st.subheader("10-Year Revenue & Net Profit Trend")
        if not pl_df.empty and 'sales' in pl_df.columns:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(
                x=pl_df['year'],
                y=pl_df['sales'],
                name='Revenue (Sales)',
                marker_color='#1f77b4'
            ))
            fig_bar.add_trace(go.Bar(
                x=pl_df['year'],
                y=pl_df['net_profit'],
                name='Net Profit',
                marker_color='#2ca02c'
            ))
            fig_bar.update_layout(
                barmode='group',
                height=380,
                margin=dict(t=30, b=30, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No 10-year P&L data available for chart.")

    with chart_c2:
        st.subheader("10-Year ROE vs ROCE Trend")
        if not ratios_df.empty and 'return_on_equity_pct' in ratios_df.columns:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=ratios_df['year'],
                y=ratios_df['return_on_equity_pct'],
                mode='lines+markers',
                name='ROE (%)',
                line=dict(color='#ff7f0e', width=3)
            ))
            fig_line.add_trace(go.Scatter(
                x=ratios_df['year'],
                y=ratios_df['return_on_capital_employed_pct'],
                mode='lines+markers',
                name='ROCE (%)',
                line=dict(color='#9467bd', width=3)
            ))
            fig_line.update_layout(
                height=380,
                margin=dict(t=30, b=30, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No 10-year ratio trend data available for chart.")

    st.markdown("---")

    # -----------------------------------------------------
    # Pros and Cons Section
    # -----------------------------------------------------
    st.subheader("Pros & Cons Analysis")
    pro_col, con_col = st.columns(2)

    pros_list = []
    cons_list = []

    if not prosandcons_df.empty:
        p_row = prosandcons_df.iloc[0]
        if pd.notna(p_row.get('pros')) and p_row['pros']:
            pros_list = [p.strip() for p in str(p_row['pros']).split('\n') if p.strip()]
        if pd.notna(p_row.get('cons')) and p_row['cons']:
            cons_list = [c.strip() for c in str(p_row['cons']).split('\n') if c.strip()]

    # Generated fallback pros/cons if none exist in table
    if not pros_list:
        if pd.notna(roe_val) and roe_val >= 15:
            pros_list.append(f"Company has delivered a strong ROE of {roe_val:.1f}%.")
        if pd.notna(de_val) and de_val <= 0.5:
            pros_list.append("Company is virtually debt-free with low financial risk.")
        if pd.notna(fcf_val) and fcf_val > 0:
            pros_list.append(f"Strong cash generation with latest FCF of ₹{fcf_val:.0f} Cr.")
        if not pros_list:
            pros_list.append("Established market presence in Nifty 100 index.")

    if not cons_list:
        if pd.notna(de_val) and de_val > 1.0:
            cons_list.append(f"Company has higher leverage with D/E ratio of {de_val:.2f}.")
        if pd.notna(cagr_val) and cagr_val < 5:
            cons_list.append(f"Revenue growth has been sluggish (5Y CAGR: {cagr_val:.1f}%).")
        if not cons_list:
            cons_list.append("Exposed to macroeconomic cyclicality and commodity price risks.")

    with pro_col:
        st.markdown("##### ✅ Key Strengths (Pros)")
        for pro in pros_list:
            st.markdown(f"✔ **{pro}**")

    with con_col:
        st.markdown("##### ❌ Key Risks (Cons)")
        for con in cons_list:
            st.markdown(f"✖ **{con}**")
