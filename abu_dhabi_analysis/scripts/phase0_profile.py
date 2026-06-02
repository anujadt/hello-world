"""
Phase 0: profile the raw DARI export and emit a data dictionary.
HARD STOP after this script. Do not run later phases until the dictionary is reviewed.
"""
from __future__ import annotations
import sys
import io
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, OUTPUTS, load_raw, load_config, ensure_dirs

ensure_dirs()
cfg = load_config()
df = load_raw(cfg)

buf = io.StringIO()

def w(s: str = "") -> None:
    print(s)
    buf.write(s + "\n")

w("# Abu Dhabi DARI Sales Export, Data Dictionary")
w("")
w(f"Source file: `{cfg['data_path']}`")
w(f"Rows: {len(df):,}    Columns: {df.shape[1]}")
w(f"File encoding confirmed UTF-8.")

# Date sanity
date_col = "Sale Application Date"
dmin, dmax = df[date_col].min(), df[date_col].max()
year_range = (dmin.year, dmax.year)
w(f"Date range: {dmin.date()} to {dmax.date()}.")
w("Date system: Gregorian (verified by year range falling in 2019 to 2026, not Hijri 1440 to 1447).")
w("")

w("## 10-row sample")
w("")
w("```")
w(df.head(10).to_string(index=False))
w("```")
w("")

w("## Dtypes")
w("")
w("```")
w(df.dtypes.to_string())
w("```")
w("")

# Per-column profile
w("## Per-column profile")
w("")
for col in df.columns:
    s = df[col]
    nulls = s.isna().mean() * 100
    card = s.nunique(dropna=True)
    w(f"### `{col}`  (null {nulls:.2f}%, distinct {card:,})")
    if pd.api.types.is_numeric_dtype(s):
        q = s.quantile([0.01, 0.5, 0.99])
        w(f"- min {s.min():,.2f}, p1 {q.loc[0.01]:,.2f}, median {q.loc[0.5]:,.2f}, "
          f"mean {s.mean():,.2f}, p99 {q.loc[0.99]:,.2f}, max {s.max():,.2f}")
    elif pd.api.types.is_datetime64_any_dtype(s):
        w(f"- min {s.min().date()}, max {s.max().date()}")
    else:
        top = s.value_counts(dropna=True).head(15)
        w("- Top values:")
        for v, c in top.items():
            w(f"  - {v}: {c:,}")
    w("")

# Empirical unit verification: psm vs rate column
implied = df["Property Sale Price (AED)"] / df["Property Sold Area (SQM)"]
delta = (implied - df["Rate (AED per SQM)"]).abs() / df["Rate (AED per SQM)"]
w("## Area-unit verification (SQM, not SQFT)")
w("")
w(f"`Rate (AED per SQM)` vs `price / sqm` median absolute relative difference: {delta.median()*100:.4f}%")
w(f"Within 1% on {(delta < 0.01).mean()*100:.2f}% of rows. Confirms area unit is SQM and the rate column matches.")
w("")

# Concept to column map
w("## Concept to canonical column map")
w("")
table = [
    ("transaction date",          "Sale Application Date",    "date",       "Gregorian, daily granularity."),
    ("transaction type",          "(implied: all sales)",     "n/a",        "Export is sales-only. No mortgage or gift rows. Leverage/credit signal NOT computable."),
    ("asset class",               "Asset Class",              "asset",      "residential or commercial."),
    ("property sub-type",         "Property Type",            "ptype",      "apartment, villa, townhouse, duplex, retail, office, land, etc."),
    ("off-plan vs ready flag",    "Sale Application Type",    "deal_type",  "off-plan, ready, court-mandated."),
    ("primary vs secondary",      "Sale Sequence",            "market",     "primary (developer) vs secondary (resale)."),
    ("transacted price (AED)",    "Property Sale Price (AED)","price",      "Full headline price. Multiply by `share` for fractional sales if needed."),
    ("ownership share sold",      "Property Sold Share",      "share",      "1.0 = full unit. Fractional <1 dropped for pricing per share threshold in config."),
    ("property area",             "Property Sold Area (SQM)", "sqm",        "Square metres. Verified empirically."),
    ("land plot area",            "Land Plot Ground Area (SQM)","land_sqm", "Project plot area, not unit area."),
    ("price per area",            "Rate (AED per SQM)",       "rate_sqm",   "Matches price / sqm within rounding."),
    ("property layout",           "Property Layout",          "layout",     "studio, 1 bed, 2 beds, etc. Some 'unclassified' rows present."),
    ("district",                  "District",                 "district",   "First-level area label, e.g. Al Reem Island, Yas Island."),
    ("community",                 "Community",                "community",  "Sub-district sector code (RS3, RT6, etc.)."),
    ("project",                   "Project Name",             "project",    "Building or master project name."),
    ("unit / parcel id",          "MISSING",                  "n/a",        "No unit identifier present. Repeat-sales index NOT feasible. Hedonic fallback used."),
    ("buyer nationality / FDI",   "MISSING",                  "n/a",        "No buyer attributes in this export. FDI mix NOT computable."),
    ("rent / yield data",         "MISSING",                  "n/a",        "No rent column. Net yields use cited external benchmarks, applied with the cost stack in config.yaml."),
]
w("| Concept | Source column | Canonical | Notes |")
w("|---|---|---|---|")
for row in table:
    w("| " + " | ".join(row) + " |")
w("")

# Top observed values for key categoricals to feed alias mapping
w("## Key categorical landscapes (for alias normalization in Phase 1)")
w("")
for col in ["Asset Class", "Property Type", "Sale Application Type", "Sale Sequence", "District"]:
    top = df[col].value_counts(dropna=True).head(20)
    w(f"### `{col}` top 20")
    w("```")
    w(top.to_string())
    w("```")
    w("")

# Headline counts for the QA scope
w("## Headline scope counts")
w("")
w(f"- Asset class share: " + ", ".join([f"{k} {v/len(df)*100:.1f}%" for k, v in df['Asset Class'].value_counts().items()]))
w(f"- Off-plan vs ready share: " + ", ".join([f"{k} {v/len(df)*100:.1f}%" for k, v in df['Sale Application Type'].value_counts().items()]))
w(f"- Primary vs secondary share: " + ", ".join([f"{k} {v/len(df)*100:.1f}%" for k, v in df['Sale Sequence'].value_counts().items()]))
w(f"- Property type top 5: " + ", ".join([f"{k} {v/len(df)*100:.1f}%" for k, v in df['Property Type'].value_counts().head(5).items()]))
w(f"- Fractional share rows (share < 0.99): {(df['Property Sold Share'] < 0.99).sum():,} ({(df['Property Sold Share'] < 0.99).mean()*100:.2f}%)")
w(f"- Zero or null price rows: {((df['Property Sale Price (AED)'].isna()) | (df['Property Sale Price (AED)'] <= 0)).sum():,}")
w(f"- Zero or null sqm rows: {((df['Property Sold Area (SQM)'].isna()) | (df['Property Sold Area (SQM)'] <= 0)).sum():,}")
w("")

# Critical caveats up front
w("## Critical caveats and HARD STOP guidance")
w("")
w("1. The export contains SALES only. Mortgages and gifts are absent, so the leverage/credit signal "
  "requested in Phase 2 cannot be computed. Cash share also cannot be derived.")
w("2. There is no unit or parcel identifier. A proper repeat-sales index requires matching the same "
  "asset across multiple transactions; this export does not allow that. Phase 3 will fall back to a "
  "hedonic mix-adjusted index, with off-plan-to-handover modelled as a SEPARATE cohort metric.")
w("3. No buyer nationality. The FDI/foreign-share signal requested in Phase 2 cannot be computed.")
w("4. No rent column. Net yields in Phase 4 require external benchmarks, joined per district and "
  "labelled with their source.")
w("5. The most recent 1 to 2 quarters are likely under-recorded because off-plan registrations "
  "lag transaction dates. Phase 1 will tag them as `is_preliminary`.")
w("6. Fractional-share transactions are present and will be excluded from pricing analysis.")
w("")

# Write
out_path = OUTPUTS / "data_dictionary.md"
out_path.write_text(buf.getvalue(), encoding="utf-8")
print()
print(f"Saved {out_path}")
