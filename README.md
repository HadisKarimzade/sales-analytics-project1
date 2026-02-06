# Sales Analytics Platform (Mini Project II)

This project loads a raw sales dataset (`data/sales_data.csv`), cleans it, performs analytics, implements custom
sorting/searching algorithms with performance comparisons, generates charts, and exports reports.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Outputs:
- `data/sales_clean.csv` (cleaned dataset)
- `output/summary_report.txt` (key metrics + answers)
- `output/top_customers.csv`, `output/top_products.csv`
- `output/figures/*.png` (charts)

## Project structure

```
sales_analytics/
  main.py
  models.py
  analyzer.py
  algorithms.py
  utils.py
  data/
  output/
```
This project analyzes sales data using Python, Pandas, and OOP principles.


