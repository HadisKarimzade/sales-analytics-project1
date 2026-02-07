from pathlib import Path
from analyzer import SalesAnalyzer
from utils import ensure_dirs


def main():
    root = Path(__file__).resolve().parent
    data_dir = root / "data"
    out_dir = root / "output"
    fig_dir = out_dir / "figures"
    ensure_dirs([data_dir, out_dir, fig_dir])

    analyzer = SalesAnalyzer(
        raw_csv=data_dir / "sales_data.csv",
        clean_csv=data_dir / "sales_clean.csv",
        out_dir=out_dir,
        fig_dir=fig_dir,
    )

    df = analyzer.clean_data(analyzer.load_data())
    analyzer.export_clean(df)

    report_text, exports = analyzer.analytics(df)
    algo_text = analyzer.algorithm_report(df)
    figs = analyzer.visuals(df)

    analyzer.write_report(report_text + "\n\n" + algo_text, figs, exports)
    print("✅ Done.")


if __name__ == "__main__":
    main()