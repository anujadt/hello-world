"""
Shared loaders, paths, and column mapping for the Abu Dhabi DARI analysis.
Every script imports from here.
"""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
OUTPUTS = ROOT / "outputs"
CHARTS = OUTPUTS / "charts"
EXTERNAL = ROOT / "external"
PARQUET = OUTPUTS / "clean_transactions.parquet"

# Canonical column mapping. Source column on the left, canonical name on the right.
COLUMN_MAP = {
    "Asset Class": "asset",
    "Property Type": "ptype",
    "Sale Application Date": "date",
    "Property Sold Area (SQM)": "sqm",
    "Land Plot Ground Area (SQM)": "land_sqm",
    "Property Layout": "layout",
    "District": "district",
    "Community": "community",
    "Project Name": "project",
    "Property Sale Price (AED)": "price",
    "Property Sold Share": "share",
    "Rate (AED per SQM)": "rate_sqm",
    "Sale Application Type": "deal_type",
    "Sale Sequence": "market",
}

# District label normalization. Maps observed source labels to a single canonical English label.
# Populated after Phase 0 inspection if needed.
DISTRICT_ALIASES: dict[str, str] = {
    # "Yas": "Yas Island",  # add aliases here once Phase 0 confirms variants
}


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_raw(cfg: dict | None = None) -> pd.DataFrame:
    """Load the raw DARI CSV with date parsing. Encoding detection handled here."""
    cfg = cfg or load_config()
    path = cfg["data_path"]
    # UTF-8 expected; fall back to Windows-1256 if it errors.
    try:
        df = pd.read_csv(path, parse_dates=["Sale Application Date"], encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, parse_dates=["Sale Application Date"], encoding="windows-1256")
    df.columns = [c.strip() for c in df.columns]
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=COLUMN_MAP).copy()
    for c in ["sqm", "land_sqm", "price", "share", "rate_sqm"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "district" in df.columns and DISTRICT_ALIASES:
        df["district"] = df["district"].replace(DISTRICT_ALIASES)
    return df


def ensure_dirs() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    CHARTS.mkdir(parents=True, exist_ok=True)
    EXTERNAL.mkdir(parents=True, exist_ok=True)


def fmt_aed(x: float) -> str:
    if x >= 1e9:
        return f"AED {x/1e9:.2f}B"
    if x >= 1e6:
        return f"AED {x/1e6:.2f}M"
    if x >= 1e3:
        return f"AED {x/1e3:.1f}k"
    return f"AED {x:.0f}"
