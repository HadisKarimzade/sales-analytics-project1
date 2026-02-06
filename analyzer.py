"""
SalesAnalyzer: loading, cleaning, analysis, exports, visualization.

Also includes a Strategy design pattern for missing-value handling.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from algorithms import compare_search_timing, compare_sort_timing
from utils import normalize_status, parse_money, to_datetime_series


# -------- Strategy Pattern (for missing values) --------

class MissingValueStrategy:
    """Strategy interface."""
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError


class DropMissingStrategy(MissingValueStrategy):
    """Drop rows with critical missing values."""
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        critical = ["order_id", "customer_id", "order_date", "product_category", "product_name", "quantity", "unit_price", "order_amount", "status"]
        return df.dropna(subset=critical)


class FillStatusStrategy(MissingValueStrategy):
    """Fill missing status with 'pending' (common business assumption)."""
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["status"] = df["status"].fillna("pending")
        return df


@dataclass
class SalesAnalyzer:
    raw_csv_path: Path
    clean_csv_path: Path
    output_dir: Path
    figures_dir: Path

    def load_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.raw_csv_path)
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleaning steps (documented):
        1) Standardize column names
        2) Parse dates
        3) Normalize status
        4) Convert numeric columns (quantity, unit_price, order_amount)
        5) Remove duplicates
        6) Handle missing values with Strategy (fill status -> drop critical)
        """
        df = df.copy()
        df.columns = [c.strip() for c in df.columns]

        # Parse + standardize date
        df["order_date"] = to_datetime_series(df["order_date"])

        # Normalize status
        df["status"] = df["status"].apply(normalize_status)

        # Numeric parsing
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = df["unit_price"].apply(parse_money)
        df["order_amount"] = df["order_amount"].apply(parse_money)

        # Basic validity
        df = df[df["quantity"] > 0]
        df = df[df["unit_price"] >= 0]
        df = df[df["order_amount"] >= 0]

        # Remove duplicates
        df = df.drop_duplicates()

        # Strategies
        df = FillStatusStrategy().apply(df)
        df = DropMissingStrategy().apply(df)

        # Final types
        df["quantity"] = df["quantity"].astype(int)
        df["unit_price"] = df["unit_price"].astype(float)
        df["order_amount"] = df["order_amount"].astype(float)
        df["order_date"] = pd.to_datetime(df["order_date"]).dt.date  # store as date
        df["status"] = df["status"].astype(str)

        return df

    def export_clean_data(self, df_clean: pd.DataFrame) -> None:
        df_clean.to_csv(self.clean_csv_path, index=False)

    # -------- Analytics & Business Insights --------

    def run_analytics_and_exports(self, df: pd.DataFrame) -> Tuple[str, Dict[str, Path]]:
        """
        Answers 8+ business questions and exports CSV outputs.
        Returns (report_text, exports_dict).
        """
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])

        completed = df[df["status"] == "completed"].copy()

        # Q1 Total revenue
        total_revenue = completed["order_amount"].sum()

        # Q2 Average order value (AOV)
        aov = completed.groupby("order_id")["order_amount"].sum().mean()

        # Q3 Customer count
        customer_count = df["customer_id"].nunique()

        # Q4 Most profitable category
        revenue_by_cat = completed.groupby("product_category")["order_amount"].sum().sort_values(ascending=False)
        top_category = revenue_by_cat.index[0] if len(revenue_by_cat) else "N/A"

        # Q5 Top 10 customers by lifetime value (sum of completed order_amount)
        customer_ltv = completed.groupby("customer_id")["order_amount"].sum().sort_values(ascending=False)
        top_customers = customer_ltv.head(10).reset_index().rename(columns={"order_amount": "lifetime_value"})
        top_customers_path = self.output_dir / "top_customers.csv"
        top_customers.to_csv(top_customers_path, index=False)

        # Q6 Repeat customer rate (customers with >1 completed order)
        orders_per_customer = completed.groupby("customer_id")["order_id"].nunique()
        repeat_rate = (orders_per_customer.gt(1).mean() * 100) if len(orders_per_customer) else 0.0

        # Q7 Monthly trend in sales (completed)
        completed["month"] = completed["order_date"].dt.to_period("M").astype(str)
        monthly_revenue = completed.groupby("month")["order_amount"].sum().sort_index()
        monthly_growth = monthly_revenue.pct_change().replace([np.inf, -np.inf], np.nan) * 100

        # Q8 Cancelled vs completed percentage
        status_pct = (df["status"].value_counts(normalize=True) * 100).round(2)

        # Q9 Average order size by category (quantity per order line)
        avg_qty_by_cat = df.groupby("product_category")["quantity"].mean().sort_values(ascending=False)

        # Q10 Outliers (unusually large orders) using IQR on completed order_amount
        q1 = completed["order_amount"].quantile(0.25)
        q3 = completed["order_amount"].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        outliers = completed[completed["order_amount"] > upper][["order_id", "customer_id", "order_amount"]].sort_values("order_amount", ascending=False)

        # Export top products
        top_products = completed.groupby(["product_category", "product_name"])["order_amount"].sum().sort_values(ascending=False).head(10).reset_index()
        top_products_path = self.output_dir / "top_products.csv"
        top_products.to_csv(top_products_path, index=False)

        # Customer segmentation by spending tier (quartiles)
        ltv = customer_ltv.copy()
        if len(ltv) >= 4:
            tiers = pd.qcut(ltv, 4, labels=["Bronze", "Silver", "Gold", "Platinum"])
            segmentation = tiers.value_counts().sort_index()
        else:
            segmentation = pd.Series(dtype=int)

        # Build report text
        lines: List[str] = []
        lines.append("Sales Analytics Summary")
        lines.append("=" * 26)
        lines.append(f"Customers (unique): {customer_count}")
        lines.append(f"Total revenue (completed): {total_revenue:.2f}")
        lines.append(f"Average order value (AOV): {aov:.2f}")
        lines.append(f"Most profitable category: {top_category}")
        lines.append(f"Repeat customer rate (completed): {repeat_rate:.2f}%")
        lines.append("")
        lines.append("Revenue by category (completed):")
        for cat, rev in revenue_by_cat.items():
            lines.append(f"  - {cat}: {rev:.2f}")
        lines.append("")
        lines.append("Order status distribution (%):")
        for st, p in status_pct.items():
            lines.append(f"  - {st}: {p:.2f}%")
        lines.append("")
        lines.append("Average quantity by category:")
        for cat, v in avg_qty_by_cat.items():
            lines.append(f"  - {cat}: {v:.2f}")
        lines.append("")
        lines.append("Monthly revenue (completed):")
        for m, rev in monthly_revenue.items():
            g = monthly_growth.get(m, np.nan)
            if pd.isna(g):
                lines.append(f"  - {m}: {rev:.2f}")
            else:
                lines.append(f"  - {m}: {rev:.2f}  (growth {g:.2f}%)")
        lines.append("")
        lines.append(f"Outlier threshold (IQR upper bound): {upper:.2f}")
        lines.append(f"Outliers count (completed): {len(outliers)}")
        if len(outliers):
            lines.append("Top outliers:")
            for _, r in outliers.head(5).iterrows():
                lines.append(f"  - order {r['order_id']} | customer {r['customer_id']} | amount {r['order_amount']:.2f}")
        lines.append("")
        if len(segmentation):
            lines.append("Customer segmentation (by lifetime value quartiles):")
            for tier, cnt in segmentation.items():
                lines.append(f"  - {tier}: {cnt}")

        report_text = "\n".join(lines)
        exports = {
            "top_customers": top_customers_path,
            "top_products": top_products_path,
        }
        return report_text, exports

    # -------- Algorithmic Analysis --------

    def run_algorithmic_analysis(self, df: pd.DataFrame) -> str:
        """
        Implements custom sort/search and compares with built-ins using timeit.
        Also documents Big-O briefly.
        """
        # Use order_amount list for timing
        amounts = df["order_amount"].dropna().astype(float).tolist()
        if len(amounts) < 10:
            return "Algorithmic Analysis\n=\nNot enough data for timing comparisons."

        # Sorting timing
        sort_res = compare_sort_timing(amounts[:2000], repeats=3)  # cap to keep runtime reasonable
        sorted_amounts = sorted(amounts)

        # Searching timing
        target = sorted_amounts[len(sorted_amounts)//2]
        search_res = compare_search_timing(sorted_amounts, target, repeats=2000)

        lines = []
        lines.append("Algorithmic Analysis")
        lines.append("=" * 20)
        lines.append("Custom sort: merge_sort (O(n log n)), Built-in: sorted() (Timsort, optimized)")
        lines.append(f"Sorting timing (3 runs on n={min(len(amounts), 2000)}):")
        lines.append(f"  - custom merge_sort: {sort_res.custom_seconds:.6f}s")
        lines.append(f"  - built-in sorted(): {sort_res.builtin_seconds:.6f}s")
        lines.append(f"  - relative (custom/builtin): {sort_res.speedup:.2f}x")
        lines.append("")
        lines.append("Custom search: binary_search (O(log n)), Built-in: 'in' (linear on list, O(n))")
        lines.append(f"Searching timing (2000 runs on n={len(sorted_amounts)}):")
        lines.append(f"  - custom binary_search: {search_res.custom_seconds:.6f}s")
        lines.append(f"  - built-in 'in': {search_res.builtin_seconds:.6f}s")
        lines.append(f"  - relative (custom/builtin): {search_res.speedup:.2f}x")
        lines.append("")
        lines.append("Why built-ins can be faster:")
        lines.append("- Python built-ins are highly optimized and implemented in C, reducing Python-level overhead.")
        lines.append("- They use efficient algorithms and memory operations under the hood.")
        return "\n".join(lines)

    # -------- Visualizations --------

    def create_visualizations(self, df: pd.DataFrame) -> List[Path]:
        df = df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])
        completed = df[df["status"] == "completed"].copy()

        paths: List[Path] = []

        # 1) Bar chart: revenue by category
        rev_by_cat = completed.groupby("product_category")["order_amount"].sum().sort_values(ascending=False)
        plt.figure()
        plt.bar(rev_by_cat.index.astype(str), rev_by_cat.values)
        plt.title("Revenue by Category (Completed)")
        plt.xlabel("Category")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45, ha="right")
        p1 = self.figures_dir / "revenue_by_category.png"
        plt.tight_layout()
        plt.savefig(p1)
        plt.close()
        paths.append(p1)

        # 2) Line chart: monthly revenue trend
        completed["month"] = completed["order_date"].dt.to_period("M").dt.to_timestamp()
        monthly = completed.groupby("month")["order_amount"].sum().sort_index()
        plt.figure()
        plt.plot(monthly.index, monthly.values)
        plt.title("Monthly Revenue Trend (Completed)")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.xticks(rotation=45, ha="right")
        p2 = self.figures_dir / "monthly_revenue_trend.png"
        plt.tight_layout()
        plt.savefig(p2)
        plt.close()
        paths.append(p2)

        # 3) Histogram: order amount distribution
        plt.figure()
        plt.hist(completed["order_amount"].values, bins=20)
        plt.title("Order Amount Distribution (Completed)")
        plt.xlabel("Order Amount")
        plt.ylabel("Frequency")
        p3 = self.figures_dir / "order_amount_distribution.png"
        plt.tight_layout()
        plt.savefig(p3)
        plt.close()
        paths.append(p3)

        return paths

    # -------- Reporting --------

    def write_summary_report(self, body: str, figure_paths: List[Path], exports: Dict[str, Path]) -> None:
        out_path = self.output_dir / "summary_report.txt"
        lines = [body, "\n", "Exports", "=" * 7]
        for k, p in exports.items():
            lines.append(f"{k}: {p}")
        lines.append("")
        lines.append("Figures")
        lines.append("=" * 7)
        for p in figure_paths:
            lines.append(str(p))
        out_path.write_text("\n".join(lines), encoding="utf-8")
