"""
Studio-only YoY velocity analysis.
Scope: READY studios (deal_type == ready), residential, layout == studio, year >= 2023.
Basis: registration date (Sale Application Date) for clean YoY across all years.
Note: April-May 2026 registrations approximately correspond to deals agreed late-Feb
to mid-April 2026 given a 45-day median registration lag. The Apr-May window is
COMPLETE for every year including 2026 (data runs to 2026-06-02), so YoY is fair.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path("/home/user/hello-world/abu_dhabi_analysis")
PARQUET = ROOT / "outputs" / "clean_transactions.parquet"
OUT = ROOT / "post_shock" / "outputs" / "studios"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(PARQUET)
df["date"] = pd.to_datetime(df["date"])
s = df[
    (df["cut"] == "residential")
    & (df["layout"] == "studio")
    & (df["deal_type"] == "ready")
].copy()
s["year"] = s["date"].dt.year
s["month"] = s["date"].dt.month
s = s[s["year"] >= 2023]

print(f"Total ready-studio rows 2023+: {len(s):,}")
print()

# ───── Citywide April+May, April only, May only ─────
def yoy_block(months: list[int], label: str) -> pd.DataFrame:
    sub = s[s["month"].isin(months)]
    cnt = sub.groupby("year").size().rename("deals")
    med_psm = sub.groupby("year")["rate_sqm"].median().round(0).rename("median_psm")
    med_price = sub.groupby("year")["price"].median().round(0).rename("median_price")
    out = pd.concat([cnt, med_psm, med_price], axis=1).reset_index()
    out["yoy_deals_pct"] = (out["deals"].pct_change() * 100).round(1)
    out["yoy_psm_pct"] = (out["median_psm"].pct_change() * 100).round(1)
    out["window"] = label
    return out[["window", "year", "deals", "yoy_deals_pct", "median_psm", "yoy_psm_pct", "median_price"]]

city = pd.concat([
    yoy_block([4, 5], "Apr+May"),
    yoy_block([4], "April only"),
    yoy_block([5], "May only"),
], ignore_index=True)
city.to_csv(OUT / "studio_yoy_citywide.csv", index=False)
print("=" * 78)
print("CITYWIDE READY STUDIO, YoY by Apr+May / April / May")
print("=" * 78)
print(city.to_string(index=False))
print()

# ───── Per-district April+May counts and price ─────
am = s[s["month"].isin([4, 5])]
piv_cnt = am.groupby(["district", "year"]).size().unstack(fill_value=0)
for y in [2023, 2024, 2025, 2026]:
    if y not in piv_cnt.columns:
        piv_cnt[y] = 0
piv_cnt = piv_cnt[[2023, 2024, 2025, 2026]]
piv_cnt["total_4y"] = piv_cnt.sum(axis=1)
piv_cnt["yoy24_23"] = ((piv_cnt[2024] / piv_cnt[2023].replace(0, pd.NA)) - 1) * 100
piv_cnt["yoy25_24"] = ((piv_cnt[2025] / piv_cnt[2024].replace(0, pd.NA)) - 1) * 100
piv_cnt["yoy26_25"] = ((piv_cnt[2026] / piv_cnt[2025].replace(0, pd.NA)) - 1) * 100

# Classify trend
def classify(row) -> str:
    yrs = [row[2023], row[2024], row[2025], row[2026]]
    nonzero = [y for y in yrs if y > 0]
    if len(nonzero) < 2:
        return "thin/new"
    seq = yrs
    diffs = [seq[i + 1] - seq[i] for i in range(3)]
    last = seq[3]
    prev_max = max(seq[:3])
    if all(d <= 0 for d in diffs):
        return "sustained decline"
    if all(d >= 0 for d in diffs):
        return "sustained rise"
    if last >= prev_max:
        return "rising / at peak"
    if last < prev_max * 0.5:
        return "down from peak"
    return "mixed"

piv_cnt["trend"] = piv_cnt.apply(classify, axis=1)
piv_cnt = piv_cnt.sort_values("total_4y", ascending=False)
piv_cnt.round(1).to_csv(OUT / "studio_yoy_by_district.csv")

print("=" * 78)
print("READY STUDIO, Apr+May, per district (count by year + YoY% + trend tag)")
print("=" * 78)
print(piv_cnt.round(0).head(15).to_string())
print()

# ───── Per-district median psm trend (Apr+May) ─────
piv_psm = am.groupby(["district", "year"])["rate_sqm"].median().unstack()
piv_n = am.groupby(["district", "year"]).size().unstack(fill_value=0)
# Mask psm where sample < 5
for y in piv_psm.columns:
    piv_psm.loc[piv_n[y] < 5, y] = pd.NA
for y in [2023, 2024, 2025, 2026]:
    if y not in piv_psm.columns:
        piv_psm[y] = pd.NA
piv_psm = piv_psm[[2023, 2024, 2025, 2026]]
piv_psm["yoy26_25_pct"] = ((piv_psm[2026] / piv_psm[2025]) - 1) * 100
piv_psm["yoy25_24_pct"] = ((piv_psm[2025] / piv_psm[2024]) - 1) * 100
piv_psm = piv_psm.dropna(how="all").round(0)
piv_psm.to_csv(OUT / "studio_yoy_price.csv")

print("=" * 78)
print("READY STUDIO, Apr+May, median AED/sqm by district (cells with n<5 suppressed)")
print("=" * 78)
print(piv_psm.to_string())
print()
print(f"Outputs in {OUT}")
