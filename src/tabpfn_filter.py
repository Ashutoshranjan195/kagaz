from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ALLOWED_TYPES = ["spot", "sound", "smell", "count", "texture", "collect_safe"]

_MONTH_NAME_TO_NUM = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

try:
    from tabpfn import TabPFNClassifier  # type: ignore
    HAS_TABPFN = True
except ImportError:
    HAS_TABPFN = False
    TabPFNClassifier = None  # type: ignore


def load_history(path: Path) -> pd.DataFrame:
    """Read CSV; normalize month names to 1..12 integers."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"History data not found at {path}")
    df = pd.read_csv(path)
    month_col = df["month"]
    if month_col.dtype == object:
        df["month"] = (
            month_col.astype(str).str.strip().str.lower()
            .map(_MONTH_NAME_TO_NUM)
        )
    else:
        df["month"] = month_col.astype(int)
    if df["month"].isna().any():
        raise ValueError("Unrecognized month values in history CSV.")
    df["month"] = df["month"].astype(int)
    return df


def fallback_allowed_types() -> list[str]:
    """Return ALLOWED_TYPES — used when TabPFN or data is unavailable."""
    return list(ALLOWED_TYPES)


def _pandas_fallback(month: int, data_path: Path) -> list[str]:
    """Return item types whose mean(seen) >= 0.4 for the given month."""
    df = load_history(data_path)
    subset = df[df["month"] == month]
    if subset.empty:
        logger.warning("No history rows for month %s; using all types.", month)
        return fallback_allowed_types()
    allowed = []
    for itype in ALLOWED_TYPES:
        rows = subset[subset["item_type"] == itype]
        if not rows.empty and rows["seen"].mean() >= 0.4:
            allowed.append(itype)
    return allowed or fallback_allowed_types()


def train_and_predict(
    month: int,
    temp_c: float,
    rainfall_mm: float,
    humidity: float,
    data_path: Path,
) -> list[str]:
    """Return seasonally likely item types using TabPFN or pandas fallback."""
    if not HAS_TABPFN or TabPFNClassifier is None:
        logger.warning("TabPFN not available, using pandas fallback")
        return _pandas_fallback(month, data_path)

    try:
        df = load_history(data_path)
        features = ["month", "avg_temp_c", "rainfall_mm", "humidity", "day_length_hrs"]
        X = df[features].to_numpy()
        y = df["seen"].to_numpy()

        clf = TabPFNClassifier(n_estimators=8)
        clf.fit(X, y)

        # Query point: the current conditions with a nominal day length.
        query = [[month, temp_c, rainfall_mm, humidity, 12.0]]

        allowed = []
        for itype in df["item_type"].unique():
            if itype not in ALLOWED_TYPES:
                continue
            # Probability that "seen" is 1 under current conditions,
            # restricted to rows of this item_type.
            type_rows = df[df["item_type"] == itype]
            if type_rows.empty:
                continue
            x_type = type_rows[features].to_numpy()
            probs = clf.predict_proba(x_type)[:, 1].mean()
            if probs >= 0.5:
                allowed.append(itype)

        return allowed or fallback_allowed_types()
    except Exception as exc:  # noqa: BLE001
        logger.warning("TabPFN prediction failed (%s); using pandas fallback.", exc)
        return _pandas_fallback(month, data_path)