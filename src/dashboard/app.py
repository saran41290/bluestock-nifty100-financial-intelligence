"""
app.py

Main Streamlit Entry Point for Nifty 100 Analytics Dashboard (Sprint 4 - Day 22)

Sidebar navigation to all 8 screens:
1. Home Overview (01_home.py)
2. Company Profile (02_profile.py)
3. Stock Screener (03_screener.py)
4. Peer Comparison (04_peers.py)
5. Trend Analysis (05_trends.py)
6. Sector Analysis (06_sectors.py)
7. Capital Allocation Map (07_capital.py)
8. Annual Reports (08_reports.py)
"""

import sys
from pathlib import Path
import streamlit as st

# Locate Project Root and add to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PAGES_DIR = PROJECT_ROOT / "pages"

# Configure Page Setup
st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Bluestock Fintech Platform
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# Build Navigation using st.Page and st.navigation
pages = [
    st.Page(str(PAGES_DIR / "01_home.py"), title="Home Overview", icon="🏠"),
    st.Page(str(PAGES_DIR / "02_profile.py"), title="Company Profile", icon="🏢"),
    st.Page(str(PAGES_DIR / "03_screener.py"), title="Stock Screener", icon="⚡"),
    st.Page(str(PAGES_DIR / "04_peers.py"), title="Peer Comparison", icon="🥊"),
    st.Page(str(PAGES_DIR / "05_trends.py"), title="Trend Analysis", icon="📈"),
    st.Page(str(PAGES_DIR / "06_sectors.py"), title="Sector Analysis", icon="🌐"),
    st.Page(str(PAGES_DIR / "07_capital.py"), title="Capital Allocation Map", icon="🗺️"),
    st.Page(str(PAGES_DIR / "08_reports.py"), title="Annual Reports", icon="📄"),
]

# Render Navigation Sidebar
st.sidebar.title("🔷 Bluestock Fintech")
st.sidebar.caption("Nifty 100 Financial Intelligence")

pg = st.navigation(pages)
pg.run()
