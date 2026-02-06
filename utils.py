# Helper functions for validation and formatting

"""
Utility helpers (validation, formatting, dates).
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional
import re
import pandas as pd


def ensure_dirs(paths: Iterable[Path]) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)


def normalize_status(value: object) -> Optional[str]:
    """Normalize status to one of completed/cancelled/pending, or return None if unknown."""
    if value is None:
        return None
    s = str(value).strip().lower()
    if s in {"completed", "complete", "done"}:
        return "completed"
    if s in {"cancelled", "canceled"}:
        return "cancelled"
    if s in {"pending", "in progress", "processing"}:
        return "pending"
    return None


def parse_money(value: object) -> float | None:
    """Parse money-like values (e.g., '1,234.50', '$99') into float."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    s = s.replace(",", "")
    s = re.sub(r"[^0-9.\-]", "", s)
    if s in {"", "-", ".", "-."}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def to_datetime_series(series: pd.Series) -> pd.Series:
    """Convert a series to datetime (coerce errors to NaT)."""
    return pd.to_datetime(series, errors="coerce", infer_datetime_format=True)
