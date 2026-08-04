"""
src/reports/portfolio_summary.py

Sprint 5 - Day 35: Portfolio Summary PDF Generator

Generates reports/portfolio/portfolio_summary.pdf containing one page per company
in alphabetical order by ticker with top 6 KPIs and trend arrows (up/down/flat).
"""

from __future__ import annotations

import os
import sqlite3
import logging
from pathlib import Path
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
PORTFOLIO_DIR = PROJECT_ROOT / "reports" / "portfolio"


class PortfolioSummaryCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(8.0 * inch, 0.4 * inch, f"Portfolio Executive Summary  |  Page {self._pageNumber} of {num_pages}")
            self.drawString(0.5 * inch, 0.4 * inch, "CONFIDENTIAL — NIFTY 100 PORTFOLIO MONITORING REPORT")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(0.5 * inch, 0.55 * inch, 8.0 * inch, 0.55 * inch)
            super().showPage()
        super().save()


class PortfolioSummaryGenerator:
    def __init__(self, db_path: Path = DB_PATH, output_dir: Path = OUTPUT_DIR, reports_dir: Path = PORTFOLIO_DIR):
        self.db_path = db_path
        self.output_dir = output_dir
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.title_style = ParagraphStyle(
            'PortTitle', parent=self.styles['Heading1'],
            fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.white
        )
        self.subtitle_style = ParagraphStyle(
            'PortSub', parent=self.styles['Normal'],
            fontName='Helvetica', fontSize=10, leading=12, textColor=colors.HexColor("#E2E8F0")
        )
        self.heading_style = ParagraphStyle(
            'PortHeading', parent=self.styles['Heading2'],
            fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=6
        )
        self.cell_title = ParagraphStyle(
            'CellTitle', parent=self.styles['Normal'],
            fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor("#64748B")
        )
        self.cell_val = ParagraphStyle(
            'CellVal', parent=self.styles['Normal'],
            fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor("#1E3A8A")
        )
        self.body_text = ParagraphStyle(
            'BodyText', parent=self.styles['Normal'],
            fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#1E293B")
        )

    def compute_trend(self, curr: float | None, prev: float | None) -> str:
        """
        Returns trend arrow string:
        ↑ (Green) if improved (> 2% increase)
        ↓ (Red) if declined (> 2% decrease)
        → (Gray) if flat (within 2%)
        """
        if curr is None or prev is None or pd.isna(curr) or pd.isna(prev) or prev == 0:
            return " <font color='#64748B'><b>→</b></font>"

        pct_change = ((curr - prev) / abs(prev)) * 100.0

        if pct_change > 2.0:
            return " <font color='#065F46'><b>↑ (+{:.1f}%)</b></font>".format(pct_change)
        elif pct_change < -2.0:
            return " <font color='#991B1B'><b>↓ ({:.1f}%)</b></font>".format(pct_change)
        else:
            return " <font color='#64748B'><b>→ ({:.1f}%)</b></font>".format(pct_change)

    def generate_portfolio_pdf(self):
        conn = sqlite3.connect(self.db_path)
        companies = pd.read_sql_query("SELECT * FROM companies ORDER BY id ASC", conn)
        pnl = pd.read_sql_query("SELECT * FROM profitandloss ORDER BY company_id, year", conn)
        ratios = pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY company_id, year", conn)

        try:
            peer = pd.read_sql_query("SELECT company_id, peer_group_name FROM peer_percentiles", conn)
            sector_map = dict(zip(peer["company_id"], peer["peer_group_name"]))
        except Exception:
            sector_map = {}

        conn.close()

        pdf_path = self.reports_dir / "portfolio_summary.pdf"
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            leftMargin=0.5*inch, rightMargin=0.5*inch,
            topMargin=0.4*inch, bottomMargin=0.6*inch
        )

        story = []

        total_companies = len(companies)

        for idx, (_, c_row) in enumerate(companies.iterrows()):
            cid = c_row["id"]
            c_name = c_row.get("company_name", cid)
            sector = sector_map.get(cid, "Nifty 100")

            c_pnl = pnl[pnl["company_id"] == cid].sort_values("year")
            c_rat = ratios[ratios["company_id"] == cid].sort_values("year")

            # Calculate 6 KPIs with trend arrows
            # 1. Sales
            sales_curr = c_pnl.iloc[-1]["sales"] if not c_pnl.empty else None
            sales_prev = c_pnl.iloc[-2]["sales"] if len(c_pnl) >= 2 else None
            sales_trend = self.compute_trend(sales_curr, sales_prev)
            sales_str = f"₹ {sales_curr:.0f} Cr" if sales_curr else "N/A"

            # 2. Net Profit
            np_curr = c_pnl.iloc[-1]["net_profit"] if not c_pnl.empty else None
            np_prev = c_pnl.iloc[-2]["net_profit"] if len(c_pnl) >= 2 else None
            np_trend = self.compute_trend(np_curr, np_prev)
            np_str = f"₹ {np_curr:.0f} Cr" if np_curr else "N/A"

            # 3. ROE %
            roe_curr = c_row.get("roe_percentage", 15.0)
            roe_prev = c_rat.iloc[-2]["return_on_equity_pct"] if len(c_rat) >= 2 else 15.0
            roe_trend = self.compute_trend(roe_curr, roe_prev)
            roe_str = f"{roe_curr:.1f}%"

            # 4. ROCE %
            roce_curr = c_row.get("roce_percentage", 18.0)
            roce_prev = c_rat.iloc[-2]["return_on_capital_employed_pct"] if len(c_rat) >= 2 else 18.0
            roce_trend = self.compute_trend(roce_curr, roce_prev)
            roce_str = f"{roce_curr:.1f}%"

            # 5. OPM %
            opm_curr = c_rat.iloc[-1]["operating_profit_margin_pct"] if not c_rat.empty else None
            opm_prev = c_rat.iloc[-2]["operating_profit_margin_pct"] if len(c_rat) >= 2 else None
            opm_trend = self.compute_trend(opm_curr, opm_prev)
            opm_str = f"{opm_curr:.1f}%" if opm_curr else "N/A"

            # 6. Debt to Equity
            de_curr = c_rat.iloc[-1]["debt_to_equity"] if not c_rat.empty else None
            de_prev = c_rat.iloc[-2]["debt_to_equity"] if len(c_rat) >= 2 else None
            de_trend = self.compute_trend(de_prev, de_curr) # inverted: lower debt is better!
            de_str = "0.00x" if de_curr == 0 else f"{de_curr:.2f}x" if de_curr else "N/A"

            # Header
            h1 = Paragraph(f"<b>{c_name.upper()}</b> ({cid})", self.title_style)
            h2 = Paragraph(f"Sector: {sector}  |  Nifty 100 Portfolio Summary Card", self.subtitle_style)
            htable = Table([[h1], [h2]], colWidths=[7.2*inch])
            htable.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(htable)
            story.append(Spacer(1, 15))

            # 6 KPI Tiles
            kpi_cell = lambda title, val_str, trend_str: [
                Paragraph(f"<font size=7 color='#64748B'><b>{title.upper()}</b></font>", self.cell_title),
                Paragraph(f"{val_str}{trend_str}", self.cell_val)
            ]

            kpi_data = [
                [
                    kpi_cell("Revenue (Latest)", sales_str, sales_trend),
                    kpi_cell("Net Profit (Latest)", np_str, np_trend),
                    kpi_cell("Return on Equity", roe_str, roe_trend),
                ],
                [
                    kpi_cell("ROCE %", roce_str, roce_trend),
                    kpi_cell("Operating Margin", opm_str, opm_trend),
                    kpi_cell("Debt to Equity", de_str, de_trend),
                ]
            ]

            kpi_table = Table(kpi_data, colWidths=[2.4*inch, 2.4*inch, 2.4*inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                ('PADDING', (0,0), (-1,-1), 10),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ]))

            story.append(Paragraph("<b>TOP 6 FINANCIAL KPIS & TREND SIGNALS</b>", self.heading_style))
            story.append(kpi_table)
            story.append(Spacer(1, 20))

            # Summary Text Block
            about = str(c_row.get("about_company", "Nifty 100 constituent company."))
            story.append(Paragraph("<b>COMPANY PROFILE & EXECUTIVE SUMMARY</b>", self.heading_style))
            story.append(Paragraph(about, self.body_text))

            # PageBreak between companies (except last page)
            if idx < total_companies - 1:
                story.append(PageBreak())

        doc.build(story, canvasmaker=PortfolioSummaryCanvas)
        logger.info(f"Generated Portfolio Summary PDF ({total_companies} pages) to {pdf_path}")
        return pdf_path


if __name__ == "__main__":
    generator = PortfolioSummaryGenerator()
    generator.generate_portfolio_pdf()
