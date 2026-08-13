"""
Script to generate docs/analyst_guide.pdf (10-Page Comprehensive Platform User Guide).
Sprint 6 Day 44 Deliverable.
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = DOCS_DIR / "analyst_guide.pdf"


def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#002B49'),
        alignment=1,
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=30
    )

    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#002B49'),
        spaceBefore=15,
        spaceAfter=10
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#005B94'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#222222'),
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeCustom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#111111'),
        backColor=colors.HexColor('#F4F6F8'),
        borderPadding=6,
        spaceAfter=10
    )

    story = []

    # PAGE 1: Title & Overview
    story.append(Spacer(1, 40))
    story.append(Paragraph("NIFTY 100 FINANCIAL INTELLIGENCE PLATFORM", title_style))
    story.append(Paragraph("ANALYST USER GUIDE & TECHNICAL MANUAL", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#002B49'), spaceAfter=20))
    
    story.append(Paragraph("1. Executive Summary & Introduction", h1_style))
    story.append(Paragraph(
        "Welcome to the Nifty 100 Financial Intelligence Platform — an end-to-end data engineering, fundamental analytics, "
        "and quantitative intelligence platform built for financial analysts, equity researchers, and portfolio managers. "
        "The platform processes 10+ years of historical financial statement data across 92 constituent companies of the Nifty 100 Index.",
        body_style
    ))
    story.append(Paragraph(
        "This comprehensive guide details the operational workflows, Streamlit dashboard screens, stock screening strategies, "
        "automated PDF tearsheet generation, REST API endpoints, performance tuning, and troubleshooting procedures.",
        body_style
    ))
    
    table_data = [
        ["Platform Module", "Primary Component", "Key Technologies"],
        ["ETL Pipeline", "Data cleaner & normalizer", "Python, Pandas, SQLite3"],
        ["Financial Ratio Engine", "50+ KPI Calculator", "NumPy, SciPy"],
        ["Investment Screener", "Preset & custom filter engine", "YAML, Pandas Query"],
        ["Streamlit Dashboard", "8 Interactive Screens", "Streamlit, Plotly"],
        ["REST API", "16 FastAPI endpoints", "FastAPI, Uvicorn, Pydantic"],
        ["ML Clustering", "KMeans 5-cluster model", "scikit-learn, StandardScaler"],
        ["Reporting Engine", "Tearsheet & summary PDFs", "ReportLab, Matplotlib"]
    ]
    t = Table(table_data, colWidths=[150, 210, 180])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002B49')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(PageBreak())

    # PAGE 2: Quick Start & System Requirements
    story.append(Paragraph("2. System Setup & Launch Instructions", h1_style))
    story.append(Paragraph("Follow these quick-start steps to set up and launch the platform environment locally:", body_style))
    
    story.append(Paragraph("Step 1: Clone Repository & Create Virtual Environment", h2_style))
    story.append(Paragraph("python3 -m venv .venv<br/>source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate", code_style))
    
    story.append(Paragraph("Step 2: Install Dependencies", h2_style))
    story.append(Paragraph("pip install -r requirements.txt", code_style))
    
    story.append(Paragraph("Step 3: Build SQLite Database (ETL Load)", h2_style))
    story.append(Paragraph("python src/etl/loader.py", code_style))

    story.append(Paragraph("Step 4: Compute Ratios & Populated Tables", h2_style))
    story.append(Paragraph("python src/analytics/ratio_engine.py", code_style))

    story.append(Paragraph("Step 5: Launch Streamlit Analytics Dashboard", h2_style))
    story.append(Paragraph("streamlit run src/dashboard/app.py", code_style))

    story.append(Paragraph("Step 6: Start REST API Server", h2_style))
    story.append(Paragraph("uvicorn src.api.main:app --port 8000 --reload", code_style))
    story.append(PageBreak())

    # PAGE 3: Dashboard Navigation - Screens 1 & 2
    story.append(Paragraph("3. Dashboard Navigation — Screens 1 & 2", h1_style))
    story.append(Paragraph("Screen 01: Executive Overview (pages/01_home.py)", h2_style))
    story.append(Paragraph(
        "The Home Screen provides a high-level executive dashboard featuring 6 key summary KPI tiles (Average ROE, Median P/E, Median D/E, Average OPM, FCF Positive Count, Total Universe Market Cap). "
        "It includes a Plotly sector distribution donut chart, a Top-5 Quality Leaderboard, and a dynamic FY year selector slider (FY19–FY24).",
        body_style
    ))
    
    story.append(Paragraph("Screen 02: Company Profile (pages/02_profile.py)", h2_style))
    story.append(Paragraph(
        "The Company Profile screen offers deep-dive analysis for individual stock tickers. Features include ticker search autocomplete, "
        "company header metadata (Logo, Business Description, BSE/NSE links), 6 KPI tiles, 10-Year Revenue & Net Profit bar chart, "
        "10-Year ROE & ROCE trendline chart, and automated Pros & Cons badges.",
        body_style
    ))
    story.append(PageBreak())

    # PAGE 4: Dashboard Navigation - Screens 3 & 4
    story.append(Paragraph("4. Dashboard Navigation — Screens 3 & 4", h1_style))
    story.append(Paragraph("Screen 03: Investment Screener (pages/03_screener.py)", h2_style))
    story.append(Paragraph(
        "The Stock Screener allows multi-parameter filtering across 15+ financial metrics using sidebar range sliders. "
        "It includes 6 preset strategy buttons (Buffett Style, Benjamin Graham, Peter Lynch, Quality Compounders, Low Debt, Dividend Growth), "
        "a live-updating results table with sortable columns, and an instant CSV download exporter.",
        body_style
    ))

    story.append(Paragraph("Screen 04: Peer Comparison (pages/04_peers.py)", h2_style))
    story.append(Paragraph(
        "The Peer Comparison module enables head-to-head analysis across 11 industry peer groups (e.g. Private Banks, IT Services, FMCG). "
        "It displays an 8-axis Scatterpolar radar chart comparing company performance against peer group average, alongside a side-by-side benchmark comparison table.",
        body_style
    ))
    story.append(PageBreak())

    # PAGE 5: Dashboard Navigation - Screens 5 & 6
    story.append(Paragraph("5. Dashboard Navigation — Screens 5 & 6", h1_style))
    story.append(Paragraph("Screen 05: Trend Analysis (pages/05_trends.py)", h2_style))
    story.append(Paragraph(
        "The Multi-Metric Trend Analysis screen allows analysts to select any company and overlay up to 3 financial metrics over a 10-year historical window. "
        "Features YoY percentage change annotations, sparklines, and growth trajectory visualizers.",
        body_style
    ))

    story.append(Paragraph("Screen 06: Sector Analysis (pages/06_sectors.py)", h2_style))
    story.append(Paragraph(
        "The Sector Analysis screen provides sector rotation and relative positioning insights. Features an interactive Plotly bubble chart "
        "(X=Revenue, Y=ROE, Size=Market Cap, Color=Sub-Sector) and sector median financial ratio comparison bar charts across all 11 broad sectors.",
        body_style
    ))
    story.append(PageBreak())

    # PAGE 6: Dashboard Navigation - Screens 7 & 8
    story.append(Paragraph("6. Dashboard Navigation — Screens 7 & 8", h1_style))
    story.append(Paragraph("Screen 07: Capital Allocation Map (pages/07_capital.py)", h2_style))
    story.append(Paragraph(
        "The Capital Allocation Map visualizes how companies generate and deploy cash flow across 8 capital allocation archetypes "
        "(Reinvestor, Shareholder Returns, Deleveraging, Cash Accumulator, Growth Funded by Debt, Liquidating Assets, Distress Signal, Pre-Revenue). "
        "Features a full-universe Plotly Treemap with click-to-filter drilldowns.",
        body_style
    ))

    story.append(Paragraph("Screen 08: Annual Reports Repository (pages/08_reports.py)", h2_style))
    story.append(Paragraph(
        "The Annual Reports Repository provides direct access to 1,585 annual report PDF filing URLs sourced from BSE India. "
        "Includes ticker filter dropdowns, year selectors, and URL validation badges.",
        body_style
    ))
    story.append(PageBreak())

    # PAGE 7: Stock Screener Strategy Reference
    story.append(Paragraph("7. Investment Screener Strategy Reference", h1_style))
    story.append(Paragraph("The platform provides 6 legendary investment strategy presets pre-configured in config/screener_config.yaml:", body_style))

    screener_table = [
        ["Preset Name", "Core Filter Criteria", "Ranking Metric"],
        ["Buffett Style", "ROE > 20%, D/E < 0.5, OPM > 18%, FCF > 0", "Composite Score (desc)"],
        ["Benjamin Graham", "P/E < 20, P/B < 2.0, D/E < 1.0, Current Ratio > 1.5", "FCF Yield (desc)"],
        ["Peter Lynch", "PAT CAGR 5yr > 18%, Revenue CAGR > 15%, ROE > 18%", "PAT CAGR 5yr (desc)"],
        ["Quality Compounders", "ROE > 15%, D/E < 1.0, FCF > 0, Rev CAGR > 10%", "Composite Score (desc)"],
        ["Low Debt Champions", "D/E = 0, ROE > 12%, Revenue > 5,000 Cr", "ROE (desc)"],
        ["Dividend Growth", "Dividend Yield > 2%, Payout < 80%, FCF > 0", "Dividend Yield (desc)"]
    ]
    t2 = Table(screener_table, colWidths=[130, 270, 140])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002B49')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    story.append(PageBreak())

    # PAGE 8: REST API Reference & Example Calls
    story.append(Paragraph("8. REST API Reference & Example Commands", h1_style))
    story.append(Paragraph("The platform exposes 16 FastAPI REST endpoints running on port 8000 under the /api/v1 prefix:", body_style))

    story.append(Paragraph("Example 1: Health Check Endpoint", h2_style))
    story.append(Paragraph("curl -X GET http://localhost:8000/api/v1/health", code_style))

    story.append(Paragraph("Example 2: Get List of Companies", h2_style))
    story.append(Paragraph("curl -X GET 'http://localhost:8000/api/v1/companies?sector=Information%20Technology'", code_style))

    story.append(Paragraph("Example 3: Run Stock Screener Filter", h2_style))
    story.append(Paragraph("curl -X GET 'http://localhost:8000/api/v1/screener?min_roe=15&max_de=1.0'", code_style))

    story.append(Paragraph("Example 4: Download PDF Tearsheet Binary", h2_style))
    story.append(Paragraph("curl -X GET 'http://localhost:8000/api/v1/companies/TCS/tearsheet' --output TCS_tearsheet.pdf", code_style))
    story.append(PageBreak())

    # PAGE 9: ML Clustering Archetypes
    story.append(Paragraph("9. ML Clustering & Archetype Profiles", h1_style))
    story.append(Paragraph(
        "KMeans clustering (n_clusters=5, random_state=42) segments all 92 companies based on StandardScaler normalized financial profiles "
        "(ROE, D/E, Revenue CAGR 5yr, FCF CAGR 5yr, OPM).",
        body_style
    ))

    cluster_table = [
        ["Cluster ID", "Archetype Name", "Key Financial Characteristics"],
        ["Cluster 0", "High-Quality Compounders", "High ROE (>25%), Low D/E (<0.3), Strong FCF Generation"],
        ["Cluster 1", "Defensive Dividend Payers", "Stable Cash Flow, High Dividend Yield, Moderate Growth"],
        ["Cluster 2", "Value & Commodity Cyclicals", "Cyclical OPM, Moderate Debt, Volatile Earnings"],
        ["Cluster 3", "High-Leverage Utilities/PSUs", "High Debt-to-Equity (>1.5), Capital Intensive, Regulated"],
        ["Cluster 4", "Emerging Fast Growers", "High Revenue CAGR (>20%), Reinvesting Cash Flow"]
    ]
    t3 = Table(cluster_table, colWidths=[80, 160, 300])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002B49')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9FAFB')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t3)
    story.append(PageBreak())

    # PAGE 10: Troubleshooting & FAQ
    story.append(Paragraph("10. Troubleshooting & FAQ", h1_style))
    story.append(Paragraph("Issue 1: SQLite Database Connection Errors", h2_style))
    story.append(Paragraph("Resolution: Ensure db/nifty100.db exists. Re-run 'python src/etl/loader.py' to rebuild SQLite tables.", body_style))

    story.append(Paragraph("Issue 2: Port 8000 or 8501 Already in Use", h2_style))
    story.append(Paragraph("Resolution: Specify custom ports using 'uvicorn src.api.main:app --port 8001' or 'streamlit run src/dashboard/app.py --server.port 8502'.", body_style))

    story.append(Paragraph("Issue 3: PDF Generation Overflow in ReportLab", h2_style))
    story.append(Paragraph("Resolution: Verify ReportLab is version >= 4.1. Table cells auto-wrap text using Paragraph flowables.", body_style))

    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#002B49'), spaceAfter=15))
    story.append(Paragraph("Nifty 100 Financial Intelligence Platform — Internal Analyst Guide v1.0", subtitle_style))

    doc.build(story)
    print(f"Generated {PDF_PATH}")


if __name__ == "__main__":
    build_pdf()
