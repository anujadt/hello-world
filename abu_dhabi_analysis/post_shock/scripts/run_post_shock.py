"""
Post-shock opportunity scan, pivot date 2026-02-27.

Phases A-F run end-to-end. Outputs to abu_dhabi_analysis/post_shock/outputs/.
Reads the regenerated parquet at abu_dhabi_analysis/outputs/clean_transactions.parquet
and the rent benchmark at abu_dhabi_analysis/external/rent_benchmark_by_layout.csv.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT = Path("/home/user/hello-world/abu_dhabi_analysis")
PARQUET = ROOT / "outputs" / "clean_transactions.parquet"
RENT_BENCH = ROOT / "external" / "rent_benchmark_by_layout.csv"
OUT = ROOT / "post_shock" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

with open(ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)

FREEHOLD = set(CFG["freehold_zones"]["whitelist"])
COSTS = CFG["costs"]

# Pivot windows
PIVOT = pd.Timestamp("2026-02-27")
PRE_START = PIVOT - pd.DateOffset(months=12)            # 2025-02-27
POST_END = pd.Timestamp("2026-06-02")                    # data end
CONTROL_START = PRE_START                                # 2025-02-27
CONTROL_END = pd.Timestamp("2025-06-02")                 # mirror of post window, one year prior
PRE_END = PIVOT - pd.Timedelta(days=1)
POST_START = PIVOT
POST_MONTHS = (POST_END - POST_START).days / 30.4

print(f"Pre  window: {PRE_START.date()} to {PRE_END.date()}  (12.0 mo)")
print(f"Post window: {POST_START.date()} to {POST_END.date()}  ({POST_MONTHS:.1f} mo)")
print(f"Control:     {CONTROL_START.date()} to {CONTROL_END.date()}  (same Feb-Jun year prior)")
print()

df = pd.read_parquet(PARQUET)
res = df[df["cut"] == "residential"].copy()
res["date"] = pd.to_datetime(res["date"])

# Aliases already applied during cleaning (Hudayriyat, Raha Beach, Shamkha, Masdar).
# Filter to freehold whitelist.
res_fh = res[res["district"].isin(FREEHOLD)].copy()
print(f"Total residential rows: {len(res):,}")
print(f"Freehold-only residential rows: {len(res_fh):,}")
print()

# Layout normalization: collapse rare layouts and stick with canonical names
LAYOUT_KEEP = {"studio", "1 bed", "2 beds", "3 beds", "4 beds", "5 beds"}
res_fh = res_fh[res_fh["layout"].isin(LAYOUT_KEEP)]

pre = res_fh[(res_fh["date"] >= PRE_START) & (res_fh["date"] <= PRE_END)]
post = res_fh[(res_fh["date"] >= POST_START) & (res_fh["date"] <= POST_END)]
ctrl = res_fh[(res_fh["date"] >= CONTROL_START) & (res_fh["date"] <= CONTROL_END)]

print(f"Pre  deals: {len(pre):,}    Post deals: {len(post):,}    Control deals: {len(ctrl):,}")
print()

# ── Phase A: regime split with YoY de-seasoning ───────────
print("=" * 70)
print("Phase A: regime comparison with YoY de-seasoning")
print("=" * 70)

GROUP = ["district", "ptype", "layout"]
MIN_PRE = 10
MIN_POST = 10

agg_pre = pre.groupby(GROUP).agg(
    n_pre=("price", "size"),
    psm_pre=("rate_sqm", "median"),
    psm_pre_mean=("rate_sqm", "mean"),
    psm_pre_std=("rate_sqm", "std"),
    sqm_med=("sqm", "median"),
    price_pre=("price", "median"),
).reset_index()

agg_post = post.groupby(GROUP).agg(
    n_post=("price", "size"),
    psm_post=("rate_sqm", "median"),
    price_post=("price", "median"),
).reset_index()

agg_ctrl = ctrl.groupby(GROUP).agg(
    n_ctrl=("price", "size"),
    psm_ctrl=("rate_sqm", "median"),
).reset_index()

# Pre-trimmed to same Feb-Jun window in 2025 = the control. So seasonal change
# is (control / 12-mo-pre-median). It captures how Feb-Jun normally compares.
regime = agg_pre.merge(agg_post, on=GROUP, how="outer").merge(agg_ctrl, on=GROUP, how="outer")
regime["n_pre"] = regime["n_pre"].fillna(0).astype(int)
regime["n_post"] = regime["n_post"].fillna(0).astype(int)
regime["n_ctrl"] = regime["n_ctrl"].fillna(0).astype(int)

regime = regime[(regime["n_pre"] >= MIN_PRE) & (regime["n_post"] >= MIN_POST)]
regime["naive_change_pct"] = (regime["psm_post"] / regime["psm_pre"] - 1) * 100
# Seasonal factor: control vs full pre-year median (this is how Feb-Jun normally diverges from 12-mo pre)
regime["seasonal_change_pct"] = np.where(
    regime["n_ctrl"] >= MIN_PRE,
    (regime["psm_ctrl"] / regime["psm_pre"] - 1) * 100,
    np.nan,
)
regime["excess_change_pct"] = regime["naive_change_pct"] - regime["seasonal_change_pct"].fillna(0)
regime["vol_pre_monthly"] = regime["n_pre"] / 12.0
regime["vol_post_monthly"] = regime["n_post"] / POST_MONTHS
regime["vol_change_ratio"] = regime["vol_post_monthly"] / regime["vol_pre_monthly"]


def classify(row) -> str:
    e = row["excess_change_pct"]
    v = row["vol_change_ratio"]
    if pd.isna(e) or pd.isna(v):
        return "unclassified"
    if e > -3 and v > 0.5:
        return "resilient"
    if e < -5 and v > 1.0:
        return "panic distribution"
    if e < -3 and v < 0.4:
        return "frozen"
    if e < -10 and 0.4 <= v <= 1.0:
        return "structural decline"
    if e < 0:
        return "soft"
    return "stable/up"


regime["regime_class"] = regime.apply(classify, axis=1)
regime = regime.sort_values(["regime_class", "excess_change_pct"])
regime.to_csv(OUT / "regime_comparison.csv", index=False)
print(regime.round(2).to_string(index=False))
print()
print("Regime class counts:")
print(regime["regime_class"].value_counts().to_string())
print()


# ── Phase B: distressed-trade detection (READY ONLY) ──────
print("=" * 70)
print("Phase B: distressed trades, post-event ready-secondary only")
print("=" * 70)

# District-level pre-event mean and std (residential, all ptypes) used as reference
dist_ref = (
    pre.groupby("district")["rate_sqm"]
    .agg(["mean", "std", "size"])
    .rename(columns={"mean": "ref_mean", "std": "ref_std", "size": "ref_n"})
    .reset_index()
)

ready_post = post[(post["deal_type"] == "ready") & (post["market"] == "secondary")].merge(
    dist_ref, on="district", how="left",
)
ready_post = ready_post[ready_post["ref_n"] >= 50]  # need enough pre-event reference
ready_post["z"] = (ready_post["rate_sqm"] - ready_post["ref_mean"]) / ready_post["ref_std"]
ready_post["discount_pct"] = (ready_post["rate_sqm"] / ready_post["ref_mean"] - 1) * 100

distress = ready_post[ready_post["z"] <= -1.5].copy()
distress = distress.sort_values("discount_pct").head(50)
distress_cols = [
    "date", "district", "community", "project", "ptype", "layout",
    "sqm", "price", "rate_sqm", "ref_mean", "z", "discount_pct",
]
distress[distress_cols].to_csv(OUT / "distress_flags.csv", index=False)
print(f"Distressed trades (z <= -1.5) in post-event ready-secondary: {len(distress)}")
print(distress[distress_cols].head(15).round(2).to_string(index=False))
print()


# ── Phase C: off-plan secondary share trajectory ──────────
print("=" * 70)
print("Phase C: off-plan secondary share trajectory post-event")
print("=" * 70)

post_with_week = post.copy()
post_with_week["week"] = post_with_week["date"].dt.to_period("W").dt.start_time
off_post = post_with_week[post_with_week["deal_type"] == "off-plan"]
off_sec_share = (
    off_post.groupby(["district", "week"])
    .apply(lambda g: (g["market"] == "secondary").mean() * 100, include_groups=False)
    .rename("offplan_secondary_share_pct")
    .reset_index()
)

# Pre-event baseline for the same metric per district
pre_off = pre[pre["deal_type"] == "off-plan"]
pre_baseline = (
    pre_off.groupby("district")
    .apply(lambda g: (g["market"] == "secondary").mean() * 100, include_groups=False)
    .rename("offplan_secondary_share_pre_pct")
    .reset_index()
)
off_sec = off_sec_share.merge(pre_baseline, on="district", how="left")
off_sec["delta_pp"] = off_sec["offplan_secondary_share_pct"] - off_sec["offplan_secondary_share_pre_pct"]
off_sec = off_sec.sort_values(["district", "week"])
off_sec.to_csv(OUT / "offplan_dump_trajectory.csv", index=False)

# District-level summary: max weekly share post-event vs pre baseline
dump_summary = (
    off_sec.groupby("district")
    .agg(
        max_post_share_pct=("offplan_secondary_share_pct", "max"),
        avg_post_share_pct=("offplan_secondary_share_pct", "mean"),
        pre_share_pct=("offplan_secondary_share_pre_pct", "first"),
    )
    .reset_index()
)
dump_summary["dump_signal_pp"] = dump_summary["avg_post_share_pct"] - dump_summary["pre_share_pct"]
dump_summary = dump_summary.sort_values("dump_signal_pp", ascending=False)
dump_summary.to_csv(OUT / "offplan_dump_summary.csv", index=False)
print(dump_summary.round(1).to_string(index=False))
print()


# ── Phase D: yield overlay (READY ONLY) ───────────────────
print("=" * 70)
print("Phase D: net yield overlay on ready segments")
print("=" * 70)

rent = pd.read_csv(RENT_BENCH)

# For yield purposes use READY-secondary medians in post-event window (cleanest entry price)
ready_post_all = post[post["deal_type"] == "ready"].copy()
ready_agg = (
    ready_post_all.groupby(GROUP)
    .agg(
        n_post_ready=("price", "size"),
        psm_post_ready=("rate_sqm", "median"),
        sqm_med=("sqm", "median"),
        price_med=("price", "median"),
    )
    .reset_index()
)

merged = ready_agg.merge(rent, on=["district", "ptype", "layout"], how="inner")
merged = merged[merged["n_post_ready"] >= 5]  # ready volume gate; rent overlay needs at least 5

# Tier per cell (use prior-12m residential terciles already computed in cleaning).
# For simplicity classify by psm: affordable <15k, mid <22k, luxury otherwise.
def tier(psm: float) -> str:
    if psm <= 15000:
        return "affordable"
    if psm <= 22000:
        return "midtier"
    return "luxury"


merged["tier"] = merged["psm_post_ready"].apply(tier)
sc_per_sqft = CFG["costs"]["service_charge_aed_per_sqft"]
merged["service_charge_aed"] = merged.apply(
    lambda r: sc_per_sqft[r["tier"]] * (r["sqm_med"] * 10.764), axis=1,
)

merged["all_in_entry"] = merged["price_med"] * (
    1 + COSTS["adm_transfer_fee_pct"] + COSTS["agent_fee_pct"]
)
merged["annual_gross_rent"] = merged["gross_yield_pct"] / 100 * merged["price_med"]
merged["rent_after_vacancy"] = merged["annual_gross_rent"] * (1 - COSTS["vacancy_rate_pct"])
merged["net_rent"] = merged["rent_after_vacancy"] - merged["service_charge_aed"]
merged["net_yield_pct"] = merged["net_rent"] / merged["all_in_entry"] * 100

# Stress test: rent at 85%
merged["stress_gross_rent"] = merged["annual_gross_rent"] * 0.85
merged["stress_rent_after_vac"] = merged["stress_gross_rent"] * (1 - COSTS["vacancy_rate_pct"])
merged["stress_net_rent"] = merged["stress_rent_after_vac"] - merged["service_charge_aed"]
merged["stress_net_yield_pct"] = merged["stress_net_rent"] / merged["all_in_entry"] * 100

cols = [
    "district", "ptype", "layout", "tier", "n_post_ready",
    "psm_post_ready", "sqm_med", "price_med", "all_in_entry",
    "gross_yield_pct", "service_charge_aed",
    "net_yield_pct", "stress_net_yield_pct", "source",
]
merged = merged[cols].sort_values("net_yield_pct", ascending=False)
merged.to_csv(OUT / "yield_overlay_ready.csv", index=False)
print(merged.head(20).round(2).to_string(index=False))
print()


# ── Phase E: composite scorecard ──────────────────────────
print("=" * 70)
print("Phase E: composite scorecard and shortlist")
print("=" * 70)

# Join yield overlay with regime classification (need both)
score = merged.merge(
    regime[GROUP + ["regime_class", "excess_change_pct", "naive_change_pct", "vol_change_ratio", "n_post"]],
    on=GROUP, how="left",
)

# Distress count per district-ptype
distress_counts = (
    distress.groupby(["district", "ptype"]).size().rename("distress_count").reset_index()
)
score = score.merge(distress_counts, on=["district", "ptype"], how="left")
score["distress_count"] = score["distress_count"].fillna(0).astype(int)

# Supply-pressure inverse: pull from offplan_dump_summary
score = score.merge(
    dump_summary[["district", "dump_signal_pp"]], on="district", how="left",
)


# Min-max scoring helpers
def mm(s: pd.Series, higher_better: bool = True) -> pd.Series:
    x = s.astype(float)
    if x.dropna().nunique() <= 1:
        return pd.Series(50.0, index=x.index)
    lo, hi = x.min(), x.max()
    out = (x - lo) / (hi - lo) * 100
    return out if higher_better else 100 - out


score["s_yield"] = mm(score["net_yield_pct"], True)
score["s_stress_yield"] = mm(score["stress_net_yield_pct"], True)
score["s_panic"] = (score["regime_class"] == "panic distribution").astype(int) * 100
score["s_distress"] = mm(np.log1p(score["distress_count"]), True)
score["s_liquidity"] = mm(score["n_post"], True)
score["s_supply_inv"] = mm(score["dump_signal_pp"], False)

W = {
    "yield": 0.30,
    "stress": 0.15,
    "panic": 0.20,
    "distress": 0.15,
    "liquidity": 0.10,
    "supply_inv": 0.10,
}
score["total"] = (
    score["s_yield"] * W["yield"]
    + score["s_stress_yield"] * W["stress"]
    + score["s_panic"] * W["panic"]
    + score["s_distress"] * W["distress"]
    + score["s_liquidity"] * W["liquidity"]
    + score["s_supply_inv"] * W["supply_inv"]
)

# Hard filters
hard = score[
    (~score["regime_class"].isin(["frozen", "structural decline"]))
    & (score["n_post"] >= 30)
].copy()
hard = hard.sort_values("total", ascending=False)

scorecard_cols = [
    "district", "ptype", "layout", "tier",
    "n_post", "psm_post_ready", "price_med",
    "net_yield_pct", "stress_net_yield_pct",
    "naive_change_pct", "excess_change_pct", "vol_change_ratio",
    "regime_class", "distress_count", "dump_signal_pp",
    "s_yield", "s_stress_yield", "s_panic", "s_distress", "s_liquidity", "s_supply_inv",
    "total",
]
hard[scorecard_cols].round(2).to_csv(OUT / "post_shock_scorecard.csv", index=False)
print(hard[scorecard_cols].head(15).round(2).to_string(index=False))
print()

shortlist = hard.head(7).copy()
shortlist["confidence"] = shortlist["n_post"].apply(
    lambda n: "high" if n >= 100 else "medium" if n >= 50 else "low",
)
shortlist[scorecard_cols + ["confidence"]].round(2).to_csv(OUT / "post_shock_shortlist.csv", index=False)
print("Shortlist:")
print(shortlist[["district", "ptype", "layout", "total", "net_yield_pct", "regime_class", "confidence"]].round(2).to_string(index=False))
print()

# Save intermediate frames for memo step
score.to_csv(OUT / "_score_full.csv", index=False)
print("\nPhase E complete. Outputs in", OUT)
