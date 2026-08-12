"""
src/analytics/clustering.py

Sprint 6 - Day 36 & Day 37: Financial Archetype Clustering & Portfolio Statistics

Implements KMeans clustering (k=5) across Nifty 100 companies, cluster profiling,
elbow curve generation, correlation matrix heatmaps, sector outlier detection,
and portfolio percentile statistics.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = PROJECT_ROOT / "reports"
SECTORS_EXCEL = PROJECT_ROOT / "supporting_datasets" / "sectors.xlsx"

CLUSTER_NAMES = {
    0: "High-Quality Compounders",
    1: "High-Leverage Financials",
    2: "Emerging Growth",
    3: "Value Cyclicals & Turnaround",
    4: "High-Margin Defensive"
}

FEATURE_COLUMNS = [
    "return_on_equity_pct",
    "debt_to_equity",
    "revenue_cagr_5yr",
    "fcf_cagr_5yr",
    "operating_profit_margin_pct"
]

CORE_10_KPIS = [
    "return_on_equity_pct",
    "return_on_capital_employed_pct",
    "debt_to_equity",
    "interest_coverage",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "cfo_quality_score",
    "asset_turnover"
]


class FinancialClusteringEngine:
    """
    Executes financial metric imputation, scaling, KMeans clustering,
    elbow plot generation, cluster profiling, correlation analysis, and outlier detection.
    """

    def __init__(self, db_path: Path = DB_PATH, output_dir: Path = OUTPUT_DIR, reports_dir: Path = REPORTS_DIR):
        self.db_path = db_path
        self.output_dir = output_dir
        self.reports_dir = reports_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> pd.DataFrame:
        """Loads latest financial ratios, computes 5yr FCF CAGR, and merges broad sector mapping."""
        conn = sqlite3.connect(self.db_path)
        companies_df = pd.read_sql_query("SELECT id AS company_id, company_name FROM companies", conn)

        # Financial ratios for latest year
        ratios_df = pd.read_sql_query("""
            SELECT r.company_id, r.year, r.return_on_equity_pct, r.return_on_capital_employed_pct,
                   r.debt_to_equity, r.interest_coverage, r.operating_profit_margin_pct,
                   r.net_profit_margin_pct, r.revenue_cagr_5yr, r.pat_cagr_5yr,
                   r.cfo_quality_score, r.asset_turnover
            FROM financial_ratios r
            INNER JOIN (
                SELECT company_id, MAX(year) as max_yr FROM financial_ratios GROUP BY company_id
            ) latest ON r.company_id = latest.company_id AND r.year = latest.max_yr
        """, conn)

        # FCF calculation from cashflow table
        cf_df = pd.read_sql_query("SELECT company_id, year, operating_activity, investing_activity FROM cashflow ORDER BY company_id, year", conn)
        conn.close()

        cf_df["fcf"] = cf_df["operating_activity"].fillna(0) + cf_df["investing_activity"].fillna(0)
        fcf_cagr_map = {}
        for cid, group in cf_df.groupby("company_id"):
            group = group.sort_values("year")
            if len(group) >= 5:
                latest = group.iloc[-1]["fcf"]
                prior = group.iloc[-5]["fcf"]
                if prior > 0 and latest > 0:
                    cagr = ((latest / prior) ** (1/5) - 1) * 100
                elif prior <= 0 and latest > 0:
                    cagr = 50.0
                elif prior > 0 and latest <= 0:
                    cagr = -50.0
                else:
                    cagr = 0.0
                fcf_cagr_map[cid] = round(cagr, 2)
            else:
                fcf_cagr_map[cid] = np.nan

        # Sector mapping
        sectors_map = {}
        if SECTORS_EXCEL.exists():
            sec_excel = pd.read_excel(SECTORS_EXCEL)
            sectors_map = dict(zip(sec_excel["company_id"], sec_excel["broad_sector"]))

        df = companies_df.merge(ratios_df, on="company_id", how="left")
        df["fcf_cagr_5yr"] = df["company_id"].map(fcf_cagr_map)
        df["broad_sector"] = df["company_id"].map(sectors_map).fillna("Financial Services")

        return df

    def preprocess_features(self, df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
        """Imputes missing values with sector median, clips extreme outliers, and scales features."""
        df_clean = df.copy()

        # Winsorize / clip extreme outliers before scaling
        df_clean["return_on_equity_pct"] = df_clean["return_on_equity_pct"].clip(lower=-50, upper=100)
        df_clean["debt_to_equity"] = df_clean["debt_to_equity"].clip(lower=0, upper=20)
        df_clean["revenue_cagr_5yr"] = df_clean["revenue_cagr_5yr"].clip(lower=-50, upper=100)
        df_clean["fcf_cagr_5yr"] = df_clean["fcf_cagr_5yr"].clip(lower=-100, upper=200)
        df_clean["operating_profit_margin_pct"] = df_clean["operating_profit_margin_pct"].clip(lower=-50, upper=100)

        # Impute missing values with sector median
        for feat in FEATURE_COLUMNS:
            sector_medians = df_clean.groupby("broad_sector")[feat].transform("median")
            df_clean[feat] = df_clean[feat].fillna(sector_medians)
            df_clean[feat] = df_clean[feat].fillna(df_clean[feat].median())

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_clean[FEATURE_COLUMNS])

        return df_clean, X_scaled

    def generate_elbow_plot(self, X_scaled: np.ndarray):
        """Generates and saves KMeans elbow plot (k=2..10)."""
        inertias = []
        k_range = range(2, 11)
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X_scaled)
            inertias.append(km.inertia_)

        plt.figure(figsize=(8, 5))
        plt.plot(k_range, inertias, "bo-", linewidth=2, markersize=8)
        plt.axvline(x=5, color="red", linestyle="--", label="Chosen k=5")
        plt.title("KMeans Clustering Elbow Curve (Inertia vs k)", fontsize=12, fontweight="bold")
        plt.xlabel("Number of Clusters (k)", fontsize=10)
        plt.ylabel("Inertia (Within-Cluster Sum of Squares)", fontsize=10)
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend()
        plt.tight_layout()

        elbow_path = self.reports_dir / "elbow_plot.png"
        plt.savefig(elbow_path, dpi=300)
        plt.close()
        logger.info(f"Elbow plot saved to {elbow_path}")

    def run_clustering(self) -> pd.DataFrame:
        """Performs KMeans clustering, computes distances from centroids, and exports cluster labels."""
        df_raw = self.load_data()
        df_clean, X_scaled = self.preprocess_features(df_raw)

        # Elbow plot
        self.generate_elbow_plot(X_scaled)

        # Fit KMeans k=5
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        cluster_ids = kmeans.fit_predict(X_scaled)
        df_clean["cluster_id"] = cluster_ids
        df_clean["cluster_name"] = df_clean["cluster_id"].map(CLUSTER_NAMES)

        # Calculate Euclidean distance from assigned centroid
        centroids = kmeans.cluster_centers_
        distances = []
        for i, row in enumerate(X_scaled):
            cid = cluster_ids[i]
            dist = np.linalg.norm(row - centroids[cid])
            distances.append(round(float(dist), 4))

        df_clean["distance_from_centroid"] = distances

        # Export cluster_labels.csv
        export_cols = ["company_id", "cluster_id", "cluster_name", "distance_from_centroid"]
        cluster_labels_csv = self.output_dir / "cluster_labels.csv"
        df_clean[export_cols].to_csv(cluster_labels_csv, index=False)
        logger.info(f"Exported cluster labels for {len(df_clean)} companies to {cluster_labels_csv}")

        # Update SQLite table `cluster_labels`
        conn = sqlite3.connect(self.db_path)
        df_clean[export_cols].to_sql("cluster_labels", conn, if_exists="replace", index=False)
        conn.close()
        logger.info("Saved cluster_labels table in SQLite database.")

        return df_clean

    def generate_correlation_heatmap(self, df: pd.DataFrame):
        """Generates Pearson correlation heatmap of 10 KPIs across all 92 companies."""
        corr_df = df[CORE_10_KPIS].corr(method="pearson")

        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True, linewidths=0.5)
        plt.title("KPI Pearson Correlation Heatmap (Nifty 100)", fontsize=12, fontweight="bold")
        plt.tight_layout()

        heatmap_path = self.reports_dir / "correlation_heatmap.png"
        plt.savefig(heatmap_path, dpi=300)
        plt.close()
        logger.info(f"Correlation heatmap saved to {heatmap_path}")

    def generate_outlier_report(self, df: pd.DataFrame):
        """Detects sector outliers (|Z-score| > 3) per broad sector and exports output/outlier_report.csv."""
        outliers = []
        for feat in CORE_10_KPIS:
            if feat not in df.columns:
                continue
            for sector, group in df.groupby("broad_sector"):
                vals = group[feat].dropna()
                if len(vals) < 3:
                    continue
                mean_val = vals.mean()
                std_val = vals.std(ddof=0)
                if std_val == 0:
                    continue
                for idx, row in group.iterrows():
                    v = row[feat]
                    if pd.notna(v):
                        z = (v - mean_val) / std_val
                        if abs(z) > 3.0:
                            outliers.append({
                                "company_id": row["company_id"],
                                "company_name": row.get("company_name", row["company_id"]),
                                "broad_sector": sector,
                                "metric": feat,
                                "value": round(float(v), 2),
                                "sector_mean": round(float(mean_val), 2),
                                "sector_std": round(float(std_val), 2),
                                "z_score": round(float(z), 2)
                            })

        outlier_df = pd.DataFrame(outliers)
        if outlier_df.empty:
            outlier_df = pd.DataFrame(columns=["company_id", "company_name", "broad_sector", "metric", "value", "sector_mean", "sector_std", "z_score"])
        outlier_csv = self.output_dir / "outlier_report.csv"
        outlier_df.to_csv(outlier_csv, index=False)
        logger.info(f"Exported {len(outlier_df)} outliers to {outlier_csv}")

    def generate_portfolio_stats(self, df: pd.DataFrame):
        """Computes P10, P25, P50, P75, P90, Mean, and Std for 10 core KPIs across all 92 companies."""
        stats_list = []
        for feat in CORE_10_KPIS:
            if feat not in df.columns:
                continue
            series = df[feat].dropna()
            if series.empty:
                continue
            stats_list.append({
                "kpi": feat,
                "p10": round(float(series.quantile(0.10)), 2),
                "p25": round(float(series.quantile(0.25)), 2),
                "p50": round(float(series.quantile(0.50)), 2),
                "p75": round(float(series.quantile(0.75)), 2),
                "p90": round(float(series.quantile(0.90)), 2),
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2),
            })

        stats_df = pd.DataFrame(stats_list)
        stats_csv = self.output_dir / "portfolio_stats.csv"
        stats_df.to_csv(stats_csv, index=False)
        logger.info(f"Exported portfolio stats to {stats_csv}")


def main():
    engine = FinancialClusteringEngine()
    df_clustered = engine.run_clustering()
    engine.generate_correlation_heatmap(df_clustered)
    engine.generate_outlier_report(df_clustered)
    engine.generate_portfolio_stats(df_clustered)
    print("Days 36 & 37 analytics completed successfully.")


if __name__ == "__main__":
    main()
