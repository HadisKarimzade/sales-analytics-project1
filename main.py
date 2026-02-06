"""
Entry point / orchestration.

Run:
    python main.py
"""
from pathlib import Path

from analyzer import SalesAnalyzer
from utils import ensure_dirs


def main() -> None:
    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"
    output_dir = project_root / "output"
    figures_dir = output_dir / "figures"
    ensure_dirs([data_dir, output_dir, figures_dir])

    raw_path = data_dir / "sales_data.csv"
    clean_path = data_dir / "sales_clean.csv"

    analyzer = SalesAnalyzer(
        raw_csv_path=raw_path,
        clean_csv_path=clean_path,
        output_dir=output_dir,
        figures_dir=figures_dir,
    )

    # 1) load + clean
    df_raw = analyzer.load_data()
    df_clean = analyzer.clean_data(df_raw)
    analyzer.export_clean_data(df_clean)

    # 2) analytics + exports
    report_text, exports = analyzer.run_analytics_and_exports(df_clean)

    # 3) algorithms + timing comparisons
    algo_report = analyzer.run_algorithmic_analysis(df_clean)

    # 4) visuals
    figure_paths = analyzer.create_visualizations(df_clean)

    # 5) final report
    analyzer.write_summary_report(report_text + "\n\n" + algo_report, figure_paths, exports)

    print("✅ Done.")
    print(f"Cleaned CSV: {clean_path}")
    print(f"Report: {output_dir/'summary_report.txt'}")
    print(f"Figures: {figures_dir}")


if __name__ == "__main__":
    main()
