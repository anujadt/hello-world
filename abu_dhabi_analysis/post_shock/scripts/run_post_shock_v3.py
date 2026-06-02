"""
Post-shock opportunity scan v3, with registration-lag correction and 19 other fixes.

Run order in one go:
  Phase A2: volume trajectory + lag-adjusted regime split (raw vs lag-adjusted)
  Phase B3: project-level distress detection (apt / villa / plot split)
  Phase C2: cohort tracking of off-plan launches with forced-resale spikes
  Phase D3: yield overlay with rent staleness flag + adjustment overlay
  Phase E3: composite with supply penalty + bootstrap CI filter
  Phase F2: 3x3 stress matrix per shortlist cell

Outputs to abu_dhabi_analysis/post_shock/outputs/v3/.
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
PIPELINE = ROOT / "external" / "external_pipeline.csv"
SUPPLY_PRESSURE = ROOT / "outputs" / "offplan_supply_pressure.csv"  # may not exist; optional
OUT = ROOT / "post_shock" / "outputs" / "v3"
OUT.mkdir(parents=True, exist_ok=True)

with open(ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)
FREEHOLD = set(CFG["freehold_zones"]["whitelist"])
COSTS = CFG["costs"]

# Pivot windows
PIVOT = pd.Timestamp("2026-02-27")
LAG_DAYS = 45  # median registration lag
LAG_PIVOT = PIVOT + pd.Timedelta(days=LAG_DAYS)  # 2026-04-13
PRE_START = PIVOT - pd.DateOffset(months=12)
POST_END = pd.Timestamp("2026-06-02")
CONTROL_START = PIVOT - pd.DateOffset(months=12)
CONTROL_END = pd.Timestamp("2025-06-02")
LAG_CONTROL_END = pd.Timestamp("2025-06-02")  # same length
LAG_CONTROL_START = LAG_PIVOT - pd.DateOffset(months=12)  # noop conceptually, year prior

PRE_END = PIVOT - pd.Timedelta(days=1)
POST_RAW_START = PIVOT
POST_LAG_START = LAG_PIVOT
POST_RAW_MONTHS = (POST_END - POST_RAW_START).days / 30.4
POST_LAG_MONTHS = (POST_END - POST_LAG_START).days / 30.4

print(f"Pre window: {PRE_START.date()} to {PRE_END.date()}")
print(f"Post (raw pivot): {POST_RAW_START.date()} to {POST_END.date()}  ({POST_RAW_MONTHS:.1f} mo)")
print(f"Post (lag-adj +{LAG_DAYS}d): {POST_LAG_START.date()} to {POST_END.date()}  ({POST_LAG_MONTHS:.1f} mo)")
print()

df = pd.read_parquet(PARQUET)
res = df[df["cut"] == "residential"].copy()
res["date"] = pd.to_datetime(res["date"])
res_fh = res[res["district"].isin(FREEHOLD)].copy()

# Layout normalization, KEEP duplex separate now (v2 collapsed it)
LAYOUT_KEEP = {"studio", "1 bed", "2 beds", "3 beds", "4 beds", "5 beds"}
res_fh = res_fh[res_fh["layout"].isin(LAYOUT_KEEP)]
# v3 treats duplex separately, but in this dataset duplex layout strings already roll into apt ptype
# so we keep ptype as-is; sub-divisions handled by ptype field which we do not collapse.
print(f"Freehold residential rows after layout filter: {len(res_fh):,}")
print()

pre = res_fh[(res_fh["date"] >= PRE_START) & (res_fh["date"] <= PRE_END)]
post_raw = res_fh[(res_fh["date"] >= POST_RAW_START) & (res_fh["date"] <= POST_END)]
post_lag = res_fh[(res_fh["date"] >= POST_LAG_START) & (res_fh["date"] <= POST_END)]
ctrl = res_fh[(res_fh["date"] >= CONTROL_START) & (res_fh["date"] <= CONTROL_END)]

print(f"Pre deals: {len(pre):,}  Raw post: {len(post_raw):,}  Lag post: {len(post_lag):,}  Control: {len(ctrl):,}")
print()

# ── Phase A2: weekly volume trajectory ────────────────────
print("=" * 70)
print("Phase A2.a: weekly volume trajectory")
print("=" * 70)

vol_window = res_fh[(res_fh["date"] >= POST_RAW_START) & (res_fh["date"] <= POST_END)].copy()
vol_window["week"] = vol_window["date"].dt.to_period("W").dt.start_time
weekly = (
    vol_window.groupby(["week", "deal_type", "market"])
    .size()
    .rename("deals")
    .reset_index()
)
weekly_total = vol_window.groupby("week").size().rename("total_deals").reset_index()
weekly_total["week_num_post_event"] = ((weekly_total["week"] - POST_RAW_START).dt.days // 7) + 1
weekly_total.to_csv(OUT / "volume_weekly.csv", index=False)

print(weekly_total.to_string(index=False))
print()
print("Sanity: weeks 1-6 (Feb 27 to Apr 12) are the lag-contaminated zone.")
print(f"  Avg weekly deals weeks 1-6: {weekly_total[weekly_total['week_num_post_event'] <= 6]['total_deals'].mean():.0f}")
print(f"  Avg weekly deals weeks 7+: {weekly_total[weekly_total['week_num_post_event'] >= 7]['total_deals'].mean():.0f}")
print(f"  Cliff ratio (7+ / 1-6): {weekly_total[weekly_total['week_num_post_event'] >= 7]['total_deals'].mean() / max(weekly_total[weekly_total['week_num_post_event'] <= 6]['total_deals'].mean(), 1):.2f}")
print()

# ── Phase A2.b: regime split, raw pivot AND lag-adjusted ──
print("=" * 70)
print("Phase A2.b: regime split, raw vs lag-adjusted")
print("=" * 70)

GROUP = ["district", "ptype", "layout"]
MIN_PRE = 10
MIN_POST = 8

agg_pre = pre.groupby(GROUP).agg(
    n_pre=("price", "size"),
    psm_pre=("rate_sqm", "median"),
    psm_pre_mean=("rate_sqm", "mean"),
    psm_pre_std=("rate_sqm", "std"),
    sqm_med=("sqm", "median"),
    sqm_p10=("sqm", lambda s: s.quantile(0.1)),
    sqm_p90=("sqm", lambda s: s.quantile(0.9)),
    price_pre=("price", "median"),
).reset_index()
agg_ctrl = ctrl.groupby(GROUP).agg(
    n_ctrl=("price", "size"), psm_ctrl=("rate_sqm", "median"),
).reset_index()


def regime_for_window(post_df: pd.DataFrame, post_months: float, label: str) -> pd.DataFrame:
    p = post_df.groupby(GROUP).agg(
        n_post=("price", "size"),
        psm_post=("rate_sqm", "median"),
        psm_vals=("rate_sqm", lambda s: list(s)),
    ).reset_index()
    out = agg_pre.merge(p, on=GROUP, how="outer").merge(agg_ctrl, on=GROUP, how="outer")
    out["n_pre"] = out["n_pre"].fillna(0).astype(int)
    out["n_post"] = out["n_post"].fillna(0).astype(int)
    out["n_ctrl"] = out["n_ctrl"].fillna(0).astype(int)
    out = out[(out["n_pre"] >= MIN_PRE) & (out["n_post"] >= MIN_POST)].copy()
    out["naive_change_pct"] = (out["psm_post"] / out["psm_pre"] - 1) * 100
    out["seasonal_change_pct"] = np.where(
        out["n_ctrl"] >= MIN_PRE,
        (out["psm_ctrl"] / out["psm_pre"] - 1) * 100, np.nan,
    )
    out["excess_change_pct"] = out["naive_change_pct"] - out["seasonal_change_pct"].fillna(0)
    out["vol_pre_monthly"] = out["n_pre"] / 12.0
    out["vol_post_monthly"] = out["n_post"] / post_months
    out["vol_change_ratio"] = out["vol_post_monthly"] / out["vol_pre_monthly"]
    out["window_label"] = label
    return out


regime_raw = regime_for_window(post_raw, POST_RAW_MONTHS, "raw_pivot")
regime_lag = regime_for_window(post_lag, POST_LAG_MONTHS, "lag_adjusted")

# Bootstrap 90% CI on excess change per cell (lag-adjusted view)
rng = np.random.default_rng(7)


def bootstrap_excess_ci(row: pd.Series, B: int = 400) -> tuple[float, float]:
    psm_vals = row.get("psm_vals")
    if not isinstance(psm_vals, list) or len(psm_vals) < 3:
        return (np.nan, np.nan)
    pre_med = row["psm_pre"]
    seasonal = row["seasonal_change_pct"] if not pd.isna(row["seasonal_change_pct"]) else 0
    boots = []
    arr = np.asarray(psm_vals)
    for _ in range(B):
        sample = rng.choice(arr, size=len(arr), replace=True)
        med = np.median(sample)
        naive = (med / pre_med - 1) * 100
        boots.append(naive - seasonal)
    lo, hi = np.quantile(boots, [0.05, 0.95])
    return (float(lo), float(hi))


regime_lag[["excess_ci_lo", "excess_ci_hi"]] = regime_lag.apply(
    lambda r: pd.Series(bootstrap_excess_ci(r)), axis=1
)
regime_lag["ci_crosses_zero"] = (regime_lag["excess_ci_lo"] <= 0) & (regime_lag["excess_ci_hi"] >= 0)


def classify(e: float, v: float) -> str:
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


for r in (regime_raw, regime_lag):
    r["regime_class"] = r.apply(lambda x: classify(x["excess_change_pct"], x["vol_change_ratio"]), axis=1)

# Drop the bulky psm_vals before serializing
regime_raw_out = regime_raw.drop(columns=["psm_vals"], errors="ignore")
regime_lag_out = regime_lag.drop(columns=["psm_vals"], errors="ignore")
regime_raw_out.to_csv(OUT / "regime_raw_pivot.csv", index=False)
regime_lag_out.to_csv(OUT / "regime_lag_adjusted.csv", index=False)

# Lag delta: how much did the headline soften when we cut the contaminated weeks?
lag_delta = regime_raw[GROUP + ["excess_change_pct"]].rename(columns={"excess_change_pct": "excess_raw_pct"}).merge(
    regime_lag[GROUP + ["excess_change_pct"]].rename(columns={"excess_change_pct": "excess_lag_pct"}),
    on=GROUP, how="inner",
)
lag_delta["lag_contamination_pp"] = lag_delta["excess_raw_pct"] - lag_delta["excess_lag_pct"]
lag_delta = lag_delta.sort_values("lag_contamination_pp", ascending=False)
lag_delta.to_csv(OUT / "lag_contamination.csv", index=False)
print("Top 10 cells where lag adjustment moved the read most (raw - lag, larger = raw was overstated):")
print(lag_delta.head(10).round(2).to_string(index=False))
print()

# ── Phase B3: project-level distress detection ────────────
print("=" * 70)
print("Phase B3: project-level distress (z-score vs project's own pre-event)")
print("=" * 70)

proj_ref = (
    pre[pre["deal_type"] == "ready"].groupby(["district", "project"])["rate_sqm"]
    .agg(["mean", "std", "size"])
    .rename(columns={"mean": "proj_mean", "std": "proj_std", "size": "proj_n"})
    .reset_index()
)
proj_ref = proj_ref[proj_ref["proj_n"] >= 10]  # need enough pre-event base

ready_post_lag = post_lag[(post_lag["deal_type"] == "ready") & (post_lag["market"] == "secondary")].merge(
    proj_ref, on=["district", "project"], how="left"
)
ready_post_lag = ready_post_lag.dropna(subset=["proj_mean", "proj_std"])
ready_post_lag = ready_post_lag[ready_post_lag["proj_std"] > 100]  # avoid division blowups on tight clusters
ready_post_lag["z"] = (ready_post_lag["rate_sqm"] - ready_post_lag["proj_mean"]) / ready_post_lag["proj_std"]
ready_post_lag["discount_pct"] = (ready_post_lag["rate_sqm"] / ready_post_lag["proj_mean"] - 1) * 100

distress_all = ready_post_lag[ready_post_lag["z"] <= -1.5].copy()

# Split by product
def product_of(row):
    if row["ptype"] == "apartment":
        return "apartment"
    if "villa" in str(row["ptype"]):
        return "villa"
    if "plot" in str(row["ptype"]):
        return "plot"
    if row["ptype"] == "townhouse / attached villa":
        return "townhouse"
    if row["ptype"] == "duplex":
        return "duplex"
    return row["ptype"]


distress_all["product"] = distress_all.apply(product_of, axis=1)
cols = ["date", "district", "community", "project", "ptype", "layout", "sqm", "price",
        "rate_sqm", "proj_mean", "z", "discount_pct"]
distress_all = distress_all.sort_values("discount_pct")
distress_all[cols + ["product"]].to_csv(OUT / "distress_all.csv", index=False)

for prod in ("apartment", "villa", "plot", "townhouse"):
    sub = distress_all[distress_all["product"] == prod]
    if len(sub) == 0:
        continue
    sub[cols].to_csv(OUT / f"distress_{prod}.csv", index=False)
    print(f"\n{prod.upper()}: {len(sub)} distressed trades (project-level z <= -1.5)")
    print(sub[cols].head(8).round(2).to_string(index=False))
print()

# ── Phase C2: cohort tracking of off-plan launches ────────
print("=" * 70)
print("Phase C2: off-plan launch cohort vs current forced-resale share")
print("=" * 70)

# Identify each project's launch year as the year of its FIRST off-plan/primary transaction in the dataset
op_first = res_fh[(res_fh["deal_type"] == "off-plan") & (res_fh["market"] == "primary")].copy()
launch = op_first.groupby(["district", "project"]).agg(launch_date=("date", "min")).reset_index()
launch["launch_year"] = launch["launch_date"].dt.year

# For each project, what is the post-event off-plan secondary share?
op_post = post_lag[post_lag["deal_type"] == "off-plan"].copy()
op_post_total = op_post.groupby(["district", "project"]).size().rename("off_post_n")
op_post_secondary = op_post[op_post["market"] == "secondary"].groupby(["district", "project"]).size().rename("off_post_sec_n")

cohort = launch.merge(op_post_total, on=["district", "project"], how="left").merge(
    op_post_secondary, on=["district", "project"], how="left"
)
cohort["off_post_n"] = cohort["off_post_n"].fillna(0).astype(int)
cohort["off_post_sec_n"] = cohort["off_post_sec_n"].fillna(0).astype(int)
cohort["secondary_share_pct"] = np.where(
    cohort["off_post_n"] > 0,
    cohort["off_post_sec_n"] / cohort["off_post_n"] * 100, np.nan,
)
cohort = cohort[(cohort["off_post_n"] >= 5) & (cohort["launch_year"].between(2022, 2024))]
cohort = cohort.sort_values("secondary_share_pct", ascending=False)
cohort.to_csv(OUT / "cohort_dump.csv", index=False)
print(cohort.head(20).round(1).to_string(index=False))
print()

# ── Phase D3: yield overlay with rent adjustment ──────────
print("=" * 70)
print("Phase D3: yield overlay (READY ONLY, rent-adjusted)")
print("=" * 70)

rent = pd.read_csv(RENT_BENCH)
rent["rent_age_months"] = 12  # source is H1 2025

# Rent-growth overlay per district (from Bayut and prior Phase 5 triangulation)
rent_growth = {
    "Yas Island": 15.0,
    "Al Saadiyat Island": 14.0,
    "Al Reem Island": 11.0,
    "Al Raha Beach": 11.0,
    "Al Reef": 11.0,
    "Masdar City": 11.0,
    "Khalifa City": 11.0,
    "Zayed City": 11.0,
    "Al Maryah Island": 8.0,
    "Hudayriyat Island": 11.0,
    "Al Jubail Island": 9.0,
    "Fahid Island": 11.0,
    "Al Shamkha": 9.0,
}
rent["growth_pct_applied"] = rent["district"].map(rent_growth).fillna(10.0)
rent["adjusted_gross_yield_pct"] = rent["gross_yield_pct"] * (1 + rent["growth_pct_applied"] / 100)

# Use LAG-ADJUSTED post-event ready-secondary medians as the entry price
ready_post_for_yield = post_lag[post_lag["deal_type"] == "ready"].copy()
ready_agg = (
    ready_post_for_yield.groupby(GROUP)
    .agg(
        n_post_ready=("price", "size"),
        psm_post_ready=("rate_sqm", "median"),
        sqm_med=("sqm", "median"),
        sqm_p10=("sqm", lambda s: s.quantile(0.1)),
        sqm_p90=("sqm", lambda s: s.quantile(0.9)),
        price_med=("price", "median"),
    )
    .reset_index()
)
merged = ready_agg.merge(rent, on=["district", "ptype", "layout"], how="inner")
merged = merged[merged["n_post_ready"] >= 5]


def tier(psm: float) -> str:
    if psm <= 15000: return "affordable"
    if psm <= 22000: return "midtier"
    return "luxury"


merged["tier"] = merged["psm_post_ready"].apply(tier)
sc = CFG["costs"]["service_charge_aed_per_sqft"]
merged["service_charge_aed"] = merged.apply(lambda r: sc[r["tier"]] * (r["sqm_med"] * 10.764), axis=1)
merged["all_in_entry"] = merged["price_med"] * (1 + COSTS["adm_transfer_fee_pct"] + COSTS["agent_fee_pct"])

# Unadjusted net yield
merged["annual_gross_rent"] = merged["gross_yield_pct"] / 100 * merged["price_med"]
merged["net_rent"] = merged["annual_gross_rent"] * (1 - COSTS["vacancy_rate_pct"]) - merged["service_charge_aed"]
merged["net_yield_pct"] = merged["net_rent"] / merged["all_in_entry"] * 100

# Adjusted net yield (rents updated for staleness)
merged["annual_gross_rent_adj"] = merged["adjusted_gross_yield_pct"] / 100 * merged["price_med"]
merged["net_rent_adj"] = merged["annual_gross_rent_adj"] * (1 - COSTS["vacancy_rate_pct"]) - merged["service_charge_aed"]
merged["net_yield_adj_pct"] = merged["net_rent_adj"] / merged["all_in_entry"] * 100

# Sanity check: adjusted should be higher than unadjusted (rents grew)
diff = (merged["net_yield_adj_pct"] - merged["net_yield_pct"]).describe()
print("Adjustment effect (net_yield_adj minus net_yield, ppt):")
print(diff.round(3))
print()

yield_cols = [
    "district", "ptype", "layout", "tier", "n_post_ready",
    "psm_post_ready", "sqm_med", "sqm_p10", "sqm_p90",
    "price_med", "all_in_entry",
    "gross_yield_pct", "adjusted_gross_yield_pct", "growth_pct_applied", "rent_age_months",
    "service_charge_aed", "net_yield_pct", "net_yield_adj_pct", "source",
    # Keep these for stress matrix below; export only the public columns.
    "annual_gross_rent", "annual_gross_rent_adj",
]
merged_full = merged[yield_cols].sort_values("net_yield_adj_pct", ascending=False)
merged_full[[c for c in yield_cols if c not in ("annual_gross_rent", "annual_gross_rent_adj")]].to_csv(
    OUT / "yield_overlay_v3.csv", index=False
)
merged = merged_full
print(merged.head(15).round(2).to_string(index=False))
print()

# ── Phase F2: 3x3 stress matrix per cell ──────────────────
print("=" * 70)
print("Phase F2: 3x3 stress matrix (rent x vacancy)")
print("=" * 70)

stress_rows = []
rent_haircuts = [0.10, 0.15, 0.25]
vac_adds = [0.0, 0.05, 0.10]
base_vac = COSTS["vacancy_rate_pct"]

for _, r in merged.iterrows():
    base_rent = r["annual_gross_rent_adj"] if not pd.isna(r["net_yield_adj_pct"]) else r["annual_gross_rent"]
    base = base_rent
    for rh in rent_haircuts:
        for va in vac_adds:
            stressed_rent = base * (1 - rh)
            vac_factor = 1 - (base_vac + va)
            net = stressed_rent * vac_factor - r["service_charge_aed"]
            y = net / r["all_in_entry"] * 100
            stress_rows.append({
                "district": r["district"], "ptype": r["ptype"], "layout": r["layout"],
                "rent_haircut_pct": int(rh * 100), "vacancy_add_pp": int(va * 100),
                "net_yield_pct": round(y, 2),
            })
stress_df = pd.DataFrame(stress_rows)
stress_df.to_csv(OUT / "stress_matrix.csv", index=False)

# Per-cell worst case
worst = stress_df.loc[stress_df.groupby(["district", "ptype", "layout"])["net_yield_pct"].idxmin()]
worst = worst.rename(columns={"net_yield_pct": "worst_case_net_yield_pct"})
print("Worst-case (rent -25%, vacancy +10pp) net yield by cell, top 12:")
print(worst.sort_values("worst_case_net_yield_pct", ascending=False).head(12).to_string(index=False))
print()

# ── Phase E3: composite scoring with supply penalty + CI gate ─
print("=" * 70)
print("Phase E3: composite scorecard v3 (supply-penalized, CI-gated)")
print("=" * 70)

# Pipeline supply per district (announced units / current 12m ready stock as a normalizer)
pipeline = pd.read_csv(PIPELINE)
# Sum announced units across all rows mentioning each district (treating "multiple" as citywide spread)
ready_12m_stock = (
    res_fh[(res_fh["date"] >= POST_RAW_START - pd.DateOffset(months=12)) & (res_fh["deal_type"] == "ready")]
    .groupby("district").size().rename("ready_stock_12m").reset_index()
)
# 14444 units spread proxy: weight by district share of pre-event off-plan share
op_district = res_fh[(res_fh["deal_type"] == "off-plan") & (res_fh["date"] >= PRE_START) & (res_fh["date"] <= PRE_END)] \
    .groupby("district").size().rename("op_pre").reset_index()
op_district["op_share"] = op_district["op_pre"] / op_district["op_pre"].sum()
op_district["allocated_pipeline_units"] = op_district["op_share"] * 14444  # Aldar+Bloom+Modon AD city pipeline
op_district = op_district.merge(ready_12m_stock, on="district", how="left")
op_district["supply_overhang_ratio"] = op_district["allocated_pipeline_units"] / op_district["ready_stock_12m"].clip(lower=1)
op_district.to_csv(OUT / "supply_overhang.csv", index=False)
print("Supply overhang ratio (allocated future units / current ready 12m stock), by district:")
print(op_district.sort_values("supply_overhang_ratio", ascending=False).round(2).to_string(index=False))
print()

# Bring lag-adjusted regime, distress count by district+ptype, and yields together
score = merged.merge(
    regime_lag_out[GROUP + ["regime_class", "excess_change_pct", "excess_ci_lo", "excess_ci_hi",
                            "ci_crosses_zero", "vol_change_ratio", "n_post"]],
    on=GROUP, how="left",
)
distress_counts = distress_all.groupby(["district", "ptype"]).size().rename("distress_count").reset_index()
score = score.merge(distress_counts, on=["district", "ptype"], how="left")
score["distress_count"] = score["distress_count"].fillna(0).astype(int)
score = score.merge(op_district[["district", "supply_overhang_ratio"]], on="district", how="left")
score["supply_overhang_ratio"] = score["supply_overhang_ratio"].fillna(0)


def mm(s: pd.Series, higher_better: bool = True) -> pd.Series:
    x = s.astype(float)
    if x.dropna().nunique() <= 1:
        return pd.Series(50.0, index=x.index)
    lo, hi = x.min(), x.max()
    out = (x - lo) / (hi - lo) * 100
    return out if higher_better else 100 - out


# Worst-case yield (from stress matrix) carries more weight than base
worst_lookup = worst.set_index(["district", "ptype", "layout"])["worst_case_net_yield_pct"]
score["worst_case_yield"] = score.set_index(["district", "ptype", "layout"]).index.map(worst_lookup)
score["worst_case_yield"] = score["worst_case_yield"].fillna(score["net_yield_adj_pct"] * 0.7)

score["s_yield"] = mm(score["net_yield_adj_pct"], True)
score["s_worst_yield"] = mm(score["worst_case_yield"], True)
score["s_panic"] = (score["regime_class"] == "panic distribution").astype(int) * 100
score["s_distress"] = mm(np.log1p(score["distress_count"]), True)
score["s_liquidity"] = mm(score["n_post_ready"], True)
score["s_supply_inv"] = mm(score["supply_overhang_ratio"], False)

W = {
    "yield": 0.25,
    "worst_yield": 0.20,
    "panic": 0.15,
    "distress": 0.10,
    "liquidity": 0.15,
    "supply_inv": 0.15,
}
score["total"] = (
    score["s_yield"] * W["yield"]
    + score["s_worst_yield"] * W["worst_yield"]
    + score["s_panic"] * W["panic"]
    + score["s_distress"] * W["distress"]
    + score["s_liquidity"] * W["liquidity"]
    + score["s_supply_inv"] * W["supply_inv"]
)

# Hard filters
hard = score[
    (~score["regime_class"].isin(["frozen", "structural decline"]))
    & (score["n_post_ready"] >= 20)
    & (~score["ci_crosses_zero"].fillna(True))
].copy()
hard = hard.sort_values("total", ascending=False)

score_cols = [
    "district", "ptype", "layout", "tier",
    "n_post_ready", "psm_post_ready", "price_med",
    "net_yield_pct", "net_yield_adj_pct", "worst_case_yield",
    "excess_change_pct", "excess_ci_lo", "excess_ci_hi", "ci_crosses_zero",
    "vol_change_ratio", "regime_class", "distress_count", "supply_overhang_ratio",
    "s_yield", "s_worst_yield", "s_panic", "s_distress", "s_liquidity", "s_supply_inv",
    "total",
]
hard[score_cols].round(2).to_csv(OUT / "post_shock_scorecard_v3.csv", index=False)
print(hard[score_cols].head(15).round(2).to_string(index=False))
print()

# Shortlist with confidence tag
shortlist = hard.head(7).copy()
shortlist["confidence"] = shortlist["n_post_ready"].apply(
    lambda n: "high" if n >= 50 else "medium" if n >= 20 else "low",
)
shortlist[score_cols + ["confidence"]].round(2).to_csv(OUT / "post_shock_shortlist_v3.csv", index=False)
print("Shortlist v3:")
print(shortlist[["district", "ptype", "layout", "total", "net_yield_adj_pct", "worst_case_yield",
                 "regime_class", "ci_crosses_zero", "confidence"]].round(2).to_string(index=False))
print()

print("Phase A2-F2 complete. Outputs in", OUT)
