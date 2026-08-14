"""
archive_deliverables.py

Script to copy and package all 23 mandatory deliverables into output/final_deliverables/
Day 45 Final Deliverable Archival.
"""

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_DIR = PROJECT_ROOT / "output" / "final_deliverables"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

DELIVERABLE_MAP = {
    # Sprint 1
    "nifty100.db": PROJECT_ROOT / "db" / "nifty100.db",
    "load_audit.csv": PROJECT_ROOT / "output" / "load_audit.csv",
    "validation_failures.csv": PROJECT_ROOT / "output" / "validation_failures.csv",
    "exploratory_queries.sql": PROJECT_ROOT / "notebooks" / "exploratory_queries.sql",
    
    # Sprint 2
    "financial_ratios.xlsx": PROJECT_ROOT / "supporting_datasets" / "financial_ratios.xlsx",
    "capital_allocation.csv": PROJECT_ROOT / "output" / "capital_allocation.csv",
    
    # Sprint 3
    "screener_output.xlsx": PROJECT_ROOT / "output" / "screener_output.xlsx",
    "screener_config.yaml": PROJECT_ROOT / "config" / "screener_config.yaml",
    "peer_comparison.xlsx": PROJECT_ROOT / "output" / "peer_comparison.xlsx",
    "radar_charts": PROJECT_ROOT / "reports" / "radar_charts",
    
    # Sprint 4
    "dashboard_app.py": PROJECT_ROOT / "src" / "dashboard" / "app.py",
    "valuation_summary.xlsx": PROJECT_ROOT / "output" / "valuation_summary.xlsx",
    "valuation_flags.csv": PROJECT_ROOT / "output" / "valuation_flags.csv",
    
    # Sprint 5
    "cashflow_intelligence.xlsx": PROJECT_ROOT / "output" / "cashflow_intelligence.xlsx",
    "pros_cons_generated.csv": PROJECT_ROOT / "output" / "pros_cons_generated.csv",
    "analysis_parsed.csv": PROJECT_ROOT / "output" / "analysis_parsed.csv",
    "tearsheets": PROJECT_ROOT / "reports" / "tearsheets",
    "sector_reports": PROJECT_ROOT / "reports" / "sector",
    "portfolio_report": PROJECT_ROOT / "reports" / "portfolio",
    
    # Sprint 6
    "cluster_labels.csv": PROJECT_ROOT / "output" / "cluster_labels.csv",
    "outlier_report.csv": PROJECT_ROOT / "output" / "outlier_report.csv",
    "portfolio_stats.csv": PROJECT_ROOT / "output" / "portfolio_stats.csv",
    "perf_notes.md": PROJECT_ROOT / "output" / "perf_notes.md",
    "api_main.py": PROJECT_ROOT / "src" / "api" / "main.py",
    "openapi.json": PROJECT_ROOT / "docs" / "openapi.json",
    "postman_collection.json": PROJECT_ROOT / "docs" / "postman_collection.json",
    "pytest_report.html": PROJECT_ROOT / "reports" / "pytest_report.html",
    "analyst_guide.pdf": PROJECT_ROOT / "docs" / "analyst_guide.pdf",
    "acceptance_checklist.pdf": PROJECT_ROOT / "docs" / "acceptance_checklist.pdf",
    "elbow_plot.png": PROJECT_ROOT / "reports" / "elbow_plot.png",
    "correlation_heatmap.png": PROJECT_ROOT / "reports" / "correlation_heatmap.png",
}

print(f"Archiving deliverables to {FINAL_DIR}...")
copied_count = 0

for name, src in DELIVERABLE_MAP.items():
    if src.exists():
        dst = FINAL_DIR / name
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        copied_count += 1
        print(f"  [OK] Copied {name}")
    else:
        print(f"  [!] Missing source: {src}")

print(f"\nArchived {copied_count}/{len(DELIVERABLE_MAP)} primary deliverables successfully into {FINAL_DIR}")
