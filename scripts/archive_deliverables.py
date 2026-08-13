"""
Script to copy and package all 23 mandatory deliverables into output/final_deliverables/
Sprint 6 Day 44 Deliverable.
"""
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FINAL_DIR = PROJECT_ROOT / "output" / "final_deliverables"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

DELIVERABLE_MAP = {
    "nifty100.db": PROJECT_ROOT / "db" / "nifty100.db",
    "load_audit.csv": PROJECT_ROOT / "output" / "load_audit.csv",
    "validation_failures.csv": PROJECT_ROOT / "output" / "validation_failures.csv",
    "financial_ratios.xlsx": PROJECT_ROOT / "supporting_datasets" / "financial_ratios.xlsx",
    "capital_allocation.csv": PROJECT_ROOT / "output" / "capital_allocation.csv",
    "screener_output.xlsx": PROJECT_ROOT / "output" / "screener_output.xlsx",
    "screener_config.yaml": PROJECT_ROOT / "config" / "screener_config.yaml",
    "peer_comparison.xlsx": PROJECT_ROOT / "output" / "peer_comparison.xlsx",
    "valuation_summary.xlsx": PROJECT_ROOT / "output" / "valuation_summary.xlsx",
    "valuation_flags.csv": PROJECT_ROOT / "output" / "valuation_flags.csv",
    "cashflow_intelligence.xlsx": PROJECT_ROOT / "output" / "cashflow_intelligence.xlsx",
    "pros_cons_generated.csv": PROJECT_ROOT / "output" / "pros_cons_generated.csv",
    "analysis_parsed.csv": PROJECT_ROOT / "output" / "analysis_parsed.csv",
    "cluster_labels.csv": PROJECT_ROOT / "output" / "cluster_labels.csv",
    "outlier_report.csv": PROJECT_ROOT / "output" / "outlier_report.csv",
    "portfolio_stats.csv": PROJECT_ROOT / "output" / "portfolio_stats.csv",
    "perf_notes.md": PROJECT_ROOT / "output" / "perf_notes.md",
    "openapi.json": PROJECT_ROOT / "docs" / "openapi.json",
    "postman_collection.json": PROJECT_ROOT / "docs" / "postman_collection.json",
    "pytest_report.html": PROJECT_ROOT / "reports" / "pytest_report.html",
    "analyst_guide.pdf": PROJECT_ROOT / "docs" / "analyst_guide.pdf",
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

print(f"Archived {copied_count}/{len(DELIVERABLE_MAP)} primary deliverables successfully.")
