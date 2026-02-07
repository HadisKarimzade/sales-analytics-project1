from pathlib import Path
import pandas as pd


def ensure_dirs(paths):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def to_datetime_series(s):
    return pd.to_datetime(s, errors="coerce")


def to_float_series(s):
    return pd.to_numeric(s, errors="coerce")
