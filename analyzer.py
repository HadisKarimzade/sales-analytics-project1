import pandas as pd
import matplotlib.pyplot as plt
from algorithms import merge_sort, linear_search, binary_search
from utils import to_datetime_series, to_float_series
import timeit


class SalesAnalyzer:

    def __init__(self, raw_csv, clean_csv, out_dir, fig_dir):
        self.raw_csv = raw_csv
        self.clean_csv = clean_csv
        self.out_dir = out_dir
        self.fig_dir = fig_dir

    # ---------- Load & Clean ----------

    def load_data(self):
        return pd.read_csv(self.raw_csv)

    def clean_data(self, df):
        df["order_date"] = to_datetime_series(df["order_date"])
        df["order_amount"] = to_float_series(df["order_amount"])

        df = df.dropna()
        df = df.drop_duplicates()

        return df

    def export_clean(self, df):
        df.to_csv(self.clean_csv, index=False)

    # ---------- Analytics ----------

    def analytics(self, df):

        completed = df[df["status"] == "completed"]

        total_revenue = completed["order_amount"].sum()
        aov = completed["order_amount"].mean()
        customer_count = df["customer_id"].nunique()

        revenue_by_category = completed.groupby("product_category")["order_amount"].sum()
        top_category = revenue_by_category.idxmax()

        cancel_rate = (df["status"] == "cancelled").mean() * 100

        df["month"] = df["order_date"].dt.month
        monthly_revenue = completed.groupby("month")["order_amount"].sum()

        avg_order_by_cat = df.groupby("product_category")["order_amount"].mean()

        outliers = df[df["order_amount"] > df["order_amount"].mean() * 3]

        report = f"""
Total Revenue: {total_revenue:.2f}
Average Order Value: {aov:.2f}
Customer Count: {customer_count}
Top Category: {top_category}
Cancelled Rate: {cancel_rate:.2f}%
Outliers Count: {len(outliers)}

Monthly Revenue:
{monthly_revenue}

Average Order by Category:
{avg_order_by_cat}
"""

        return report, {}

    # ---------- Algorithms ----------

    def algorithm_report(self, df):

        amounts = df["order_amount"].tolist()

        t_sort_custom = timeit.timeit(lambda: merge_sort(amounts), number=20)
        t_sort_builtin = timeit.timeit(lambda: sorted(amounts), number=20)

        target = amounts[len(amounts)//2]

        t_linear = timeit.timeit(lambda: linear_search(amounts, target), number=200)
        t_binary = timeit.timeit(lambda: binary_search(sorted(amounts), target), number=200)

        report = f"""
Algorithms Timing:

Custom sort: {t_sort_custom:.4f}s
Built-in sort: {t_sort_builtin:.4f}s

Linear search: {t_linear:.4f}s
Binary search: {t_binary:.4f}s

Big-O:
Sort: O(n log n)
Linear search: O(n)
Binary search: O(log n)
"""

        return report

    # ---------- Visuals ----------

    def visuals(self, df):

        paths = []

        completed = df[df["status"] == "completed"]

        # Bar chart
        cat_rev = completed.groupby("product_category")["order_amount"].sum()
        p1 = self.fig_dir / "category_revenue.png"
        cat_rev.plot(kind="bar")
        plt.savefig(p1)
        plt.close()
        paths.append(p1)

        # Line chart
        completed["month"] = completed["order_date"].dt.month
        monthly = completed.groupby("month")["order_amount"].sum()
        p2 = self.fig_dir / "monthly_revenue.png"
        monthly.plot()
        plt.savefig(p2)
        plt.close()
        paths.append(p2)

        # Histogram
        p3 = self.fig_dir / "order_distribution.png"
        plt.hist(df["order_amount"], bins=20)
        plt.savefig(p3)
        plt.close()
        paths.append(p3)

        return paths

    # ---------- Report ----------

    def write_report(self, text, figs, exports):

        path = self.out_dir / "summary_report.txt"

        with open(path, "w") as f:
            f.write(text)
            f.write("\nFigures:\n")
            for p in figs:
                f.write(str(p) + "\n")
