"""
Phase 1: build canonical clean parquet from the DARI raw export.

Scope per user direction:
  - Residential core: apartment, villa, townhouse/attached villa, duplex, residential complex.
  - Commercial parallel cut: retail, office, mall/market/retail center.
  - Exclude court-mandated. Exclude fractional shares and zero/null prices/sqm.
  - Outlier trim WITHIN ptype x tier strata, not globally.

Output:
  outputs/clean_transactions.parquet            (residential + commercial unified, with a `cut` column)
  outputs/clean_residential.parquet             (convenience cut)
  outputs/clean_commercial.parquet              (convenience cut)
  outputs/qa_brief.md                           (filter counts, trim counts, surprises)
"""
from __future__ import annotations
import sys
import io
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (
    OUTPUTS, PARQUET,
    load_raw, load_config, standardize_columns, ensure_dirs,
    reclassify_masdar, RESIDENTIAL_PTYPES, COMMERCIAL_PTYPES, EXCLUDED_DEAL_TYPES,
)

ensure_dirs()
cfg = load_config()

buf = io.StringIO()
def w(s: str = "") -> None:
    print(s)
    buf.write(s + "\n")

raw = load_raw(cfg)
raw_n = len(raw)
w("# Phase 1, Cleaning QA Brief")
w("")
w(f"Raw rows loaded: {raw_n:,}")
w("")

df = standardize_columns(raw)
df = reclassify_masdar(df)

# ── Filter chain with counts ───────────────────────────────
w("## Filter chain (residential + commercial)")
w("")
step_log = []

# 1. Drop court-mandated
n0 = len(df)
df = df[~df["deal_type"].isin(EXCLUDED_DEAL_TYPES)]
step_log.append(("Drop court-mandated", n0 - len(df), len(df)))

# 2. Positive price
n0 = len(df)
df = df[df["price"].notna() & (df["price"] >= cfg["cleaning"]["min_price_aed"])]
step_log.append((f"Drop price < AED {cfg['cleaning']['min_price_aed']:,} or null", n0 - len(df), len(df)))

# 3. Positive sqm
n0 = len(df)
df = df[df["sqm"].notna() & (df["sqm"] > 0)]
step_log.append(("Drop sqm null or zero", n0 - len(df), len(df)))

# 4. Positive rate
n0 = len(df)
df = df[df["rate_sqm"].notna() & (df["rate_sqm"] > 0)]
step_log.append(("Drop rate_sqm null or zero", n0 - len(df), len(df)))

# 5. Full-share only for pricing
n0 = len(df)
df = df[df["share"] >= cfg["cleaning"]["share_threshold"]]
step_log.append((f"Drop share < {cfg['cleaning']['share_threshold']}", n0 - len(df), len(df)))

# 6. Keep only residential and commercial scoped ptypes
n0 = len(df)
keep_set = RESIDENTIAL_PTYPES | COMMERCIAL_PTYPES
df = df[df["ptype"].isin(keep_set)]
step_log.append(("Keep residential core + commercial scope only", n0 - len(df), len(df)))

# 7. Deduplicate exact duplicates
n0 = len(df)
dup_cols = ["date", "district", "project", "sqm", "price", "layout", "deal_type", "market"]
df = df.drop_duplicates(subset=dup_cols, keep="first")
step_log.append(("Drop exact duplicates on " + ", ".join(dup_cols), n0 - len(df), len(df)))

for label, dropped, remaining in step_log:
    w(f"- {label}: dropped {dropped:,}, remaining {remaining:,}")
w("")

# ── Tag cut: residential vs commercial ─────────────────────
df["cut"] = np.where(df["ptype"].isin(RESIDENTIAL_PTYPES), "residential", "commercial")

# ── Tier assignment (data-driven, trailing 12m) ────────────
today = df["date"].max()
t12 = today - pd.DateOffset(months=12)
res_recent = df[(df["cut"] == "residential") & (df["date"] > t12)]
tier_edges = res_recent["rate_sqm"].quantile([1/3, 2/3]).values.tolist()
w(f"## Tier breakpoints (data-driven, residential trailing 12m AED/SQM terciles)")
w("")
w(f"- Affordable:  rate_sqm <= {tier_edges[0]:,.0f}")
w(f"- Mid-tier:    {tier_edges[0]:,.0f} < rate_sqm <= {tier_edges[1]:,.0f}")
w(f"- Luxury:      rate_sqm >  {tier_edges[1]:,.0f}")
w("")

def to_tier(x):
    if x <= tier_edges[0]:
        return "affordable"
    if x <= tier_edges[1]:
        return "midtier"
    return "luxury"
df["tier"] = df["rate_sqm"].apply(to_tier)

# ── Within-strata outlier trim ─────────────────────────────
lo_pct, hi_pct = cfg["cleaning"]["outlier_trim_percentiles"]
lo, hi = lo_pct / 100, hi_pct / 100

before = len(df)
# Compute per-stratum bounds, then filter with a join-back mask.
bounds = (
    df.groupby(["cut", "ptype", "tier"])["rate_sqm"]
    .quantile([lo, hi])
    .unstack()
    .rename(columns={lo: "lo", hi: "hi"})
    .reset_index()
)
counts = df.groupby(["cut", "ptype", "tier"]).size().rename("n").reset_index()
bounds = bounds.merge(counts, on=["cut", "ptype", "tier"])
# Where a stratum has fewer than 30 rows, do not trim it (set bounds wide).
bounds.loc[bounds["n"] < 30, "lo"] = df["rate_sqm"].min()
bounds.loc[bounds["n"] < 30, "hi"] = df["rate_sqm"].max()

df = df.merge(bounds[["cut", "ptype", "tier", "lo", "hi"]], on=["cut", "ptype", "tier"], how="left")
df = df[(df["rate_sqm"] >= df["lo"]) & (df["rate_sqm"] <= df["hi"])].drop(columns=["lo", "hi"])
trimmed = before - len(df)
w(f"## Outlier trimming (within ptype x tier strata, p{lo_pct} to p{hi_pct})")
w("")
w(f"Rows trimmed: {trimmed:,} ({trimmed/before*100:.2f}% of pre-trim).")
w("")

# ── Time keys & preliminary flag ───────────────────────────
df["year"] = df["date"].dt.year
df["quarter"] = df["date"].dt.to_period("Q").astype(str)
df["ym"] = df["date"].dt.to_period("M").dt.to_timestamp()
prelim_q = cfg["cleaning"]["preliminary_quarters"]
last_quarter = df["date"].max().to_period("Q")
prelim_set = {str(last_quarter - i) for i in range(prelim_q)}
df["is_preliminary"] = df["quarter"].isin(prelim_set)

w(f"## Preliminary-quarter flag")
w("")
w(f"Quarters flagged as preliminary: {sorted(prelim_set)}")
w(f"Rows in preliminary window: {df['is_preliminary'].sum():,} ({df['is_preliminary'].mean()*100:.1f}%)")
w("")

# ── Final write ────────────────────────────────────────────
out_cols = [
    "date", "year", "quarter", "ym", "is_preliminary",
    "cut", "asset", "ptype", "layout", "tier",
    "district", "community", "project",
    "sqm", "land_sqm", "price", "share", "rate_sqm",
    "deal_type", "market",
]
df = df[out_cols].reset_index(drop=True)
df["psf"] = df["rate_sqm"] / 10.764  # AED per sqft

df.to_parquet(PARQUET, index=False)
df[df["cut"] == "residential"].to_parquet(OUTPUTS / "clean_residential.parquet", index=False)
df[df["cut"] == "commercial"].to_parquet(OUTPUTS / "clean_commercial.parquet", index=False)

# ── Headline summary ───────────────────────────────────────
w("## Headline clean-dataset summary")
w("")
w(f"- Total clean rows: {len(df):,}")
w(f"- Residential cut: {(df['cut']=='residential').sum():,}")
w(f"- Commercial cut:  {(df['cut']=='commercial').sum():,}")
w(f"- Date range: {df['date'].min().date()} to {df['date'].max().date()}")
w(f"- Aggregate value: AED {df['price'].sum()/1e9:.2f}B")
w(f"- Median ticket: AED {df['price'].median()/1e6:.2f}M (residential AED {df[df['cut']=='residential']['price'].median()/1e6:.2f}M)")
w(f"- Median AED/SQM: residential {df[df['cut']=='residential']['rate_sqm'].median():,.0f}, "
  f"commercial {df[df['cut']=='commercial']['rate_sqm'].median():,.0f}")
w("")

# Top districts in clean set
w("## Top 15 districts by clean transaction count")
w("")
w("```")
w(df.groupby(["district","cut"]).size().unstack(fill_value=0).assign(total=lambda x: x.sum(axis=1)).sort_values("total", ascending=False).head(15).to_string())
w("```")
w("")

# Tier sanity
w("## Residential tier distribution")
w("")
res = df[df["cut"]=="residential"]
tier_view = res.groupby("tier").agg(
    deals=("price","size"),
    median_psm=("rate_sqm","median"),
    median_price=("price","median"),
).round(0)
w("```")
w(tier_view.to_string())
w("```")
w("")

# Masdar verification
mas_n = (df["district"] == "Masdar City").sum()
w(f"## Masdar City verification")
w("")
w(f"After project-name reclassification, Masdar City carries {mas_n} clean rows.")
w("")

# Surprises / call-outs
w("## Surprises and call-outs to remember in later phases")
w("")
w("1. Residential complex rows can carry very large aggregate ticket sizes (handover bulk transfers). "
  "When computing district-level median AED/SQM, this is fine, but for total VOLUME their share will spike "
  "in particular quarters. Phase 2 should highlight these spikes.")
w("2. The preliminary-quarter flag covers the two most recent quarters per config. Headline YoY momentum "
  "in Phase 2 onward should annotate when a comparison touches the preliminary window.")
w("3. Within-strata trimming removed a small share of rows but preserves real fat tails inside each tier; "
  "do not interpret post-trim p99 figures as the actual market high.")
w("4. Commercial volume is small relative to residential. Cell-n thresholds in Phase 2 will suppress most "
  "fine-grained commercial cuts; we will report commercial at district x deal_type level only.")
w("")

(OUTPUTS / "qa_brief.md").write_text(buf.getvalue(), encoding="utf-8")
print(f"\nSaved {PARQUET}")
print(f"Saved {OUTPUTS / 'qa_brief.md'}")
