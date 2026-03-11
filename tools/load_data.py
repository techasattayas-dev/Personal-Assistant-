"""
Tool: load_data — Load a data file and cache it for analysis.

Supports CSV, Excel (.xlsx), and JSON files.
Caches the loaded DataFrame as a pickle in .tmp/ for fast reuse by other tools.
"""

from pathlib import Path

import pandas as pd
from tabulate import tabulate


PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"
CACHE_PATH = TMP_DIR / "_cached_data.pkl"


def load_data(file_path: str) -> str:
    """Load a data file, cache it, and return a structural summary."""
    path = Path(file_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        return f"ERROR: File not found: {path}"

    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(path)
        elif suffix == ".json":
            df = pd.read_json(path)
        else:
            return f"ERROR: Unsupported file type '{suffix}'. Use CSV, XLSX, or JSON."
    except Exception as e:
        return f"ERROR: Failed to load file: {e}"

    # Cache for other tools
    TMP_DIR.mkdir(exist_ok=True)
    df.to_pickle(CACHE_PATH)

    # Build summary
    lines = [
        f"Data loaded successfully from: {path.name}",
        f"Rows: {len(df):,}  |  Columns: {len(df.columns)}",
        "",
        "Column Details:",
    ]

    col_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = df[col].isnull().sum()
        unique = df[col].nunique()
        col_info.append([col, dtype, nulls, unique])

    lines.append(tabulate(col_info, headers=["Column", "Type", "Nulls", "Unique"], tablefmt="simple"))
    lines.append("")
    lines.append("Preview (first 5 rows):")
    lines.append(tabulate(df.head(), headers="keys", tablefmt="simple", showindex=False))

    return "\n".join(lines)


def get_cached_df() -> pd.DataFrame | None:
    """Load the cached DataFrame. Returns None if no data is cached."""
    if CACHE_PATH.exists():
        return pd.read_pickle(CACHE_PATH)
    return None
