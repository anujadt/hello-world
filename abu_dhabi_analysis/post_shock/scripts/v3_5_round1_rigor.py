"""
Round 1 statistical rigor improvements on the v3 post-shock analysis.

Adds:
- Lag sensitivity grid: re-run regime classification at lag = {30, 45, 60, 90} days.
  A finding that flips sign or class across this grid is fragile.
- Poisson confidence intervals on YoY count ratios (volume_change_ratio).
- Cohort baseline: pre-shock distribution of secondary share by months-since-launch.
  Compares 2026 cohorts to their MATCHED pre-shock baseline, so the 92% secondary
  share claim is anchored to a null hypothesis.
- Holm-Bonferroni FDR correction on the per-cell CI gate used in the shortlist.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT = Path("/home/user/hello-world/abu_dhabi_analysis")
PARQUET = ROOT / "outputs" / "clean_transactions.parquet"
V3 = ROOT / "post_shock" / "outputs" / "v3"
OUT = ROOT / "post_shock" / "outputs" / "v3_5"
OUT.mkdir(parents=True, exist_ok=True)

with open(ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)
FREEHOLD = set(CFG["freehold_zones"]["whitelist"])

PIVOT = pd.Timestamp("2026-02-27")
POST_END = pd.Timestamp("2026-06-02")
PRE_START = PIVOT - pd.DateOffset(months=12)

df = pd.read_parquet(PARQUET)
df["date"] = pd.to_datetime(df["date"])
res_fh = df[
    (df["cut"] == "residential")
    & (df["district"].isin(FREEHOLD))
    & (df["layout"].isin(["studio", "1 bed", "2 beds", "3 beds", "4 beds", "5 beds"]))
].copy()

# ─── 1. Lag sensitivity grid ──────────────────────────────────────
print("=" * 75)
print("Lag sensitivity grid: regime classification at lag = 30/45/60/90 days")
print("=" * 75)

GROUP = ["district", "ptype", "layout"]
MIN_PRE, MIN_POST = 10, 8


def regime_at_lag(days: int) -> pd.DataFrame:
    lag_pivot = PIVOT + pd.Timedelta(days=days)
    post_months = max((POST_END - lag_pivot).days / 30.4, 0.1)
    pre = res_fh[(res_fh["date"] >= PRE_START) & (res_fh["date"] <= PIVOT - pd.Timedelta(days=1))]
    post = res_fh[(res_fh["date"] >= lag_pivot) & (res_fh["date"] <= POST_END)]
    p = pre.groupby(GROUP).agg(n_pre=("price", "size"), psm_pre=("rate_sqm", "median")).reset_index()
    q = post.groupby(GROUP).agg(n_post=("price", "size"), psm_post=("rate_sqm", "median")).reset_index()
    m = p.merge(q, on=GROUP, how="outer").fillna({"n_pre": 0, "n_post": 0})
    m["n_pre"] = m["n_pre"].astype(int)
    m["n_post"] = m["n_post"].astype(int)
    m = m[(m["n_pre"] >= MIN_PRE) & (m["n_post"] >= MIN_POST)]
    m["naive_change_pct"] = (m["psm_post"] / m["psm_pre"] - 1) * 100
    m["vol_change_ratio"] = (m["n_post"] / post_months) / (m["n_pre"] / 12.0)
    m["lag_days"] = days
    return m[GROUP + ["lag_days", "n_post", "naive_change_pct", "vol_change_ratio"]]


frames = [regime_at_lag(d) for d in (30, 45, 60, 90)]
all_lags = pd.concat(frames)
# Pivot to wide: one row per cell, columns per lag
wide_px = all_lags.pivot_table(index=GROUP, columns="lag_days", values="naive_change_pct").reset_index()
wide_vol = all_lags.pivot_table(index=GROUP, columns="lag_days", values="vol_change_ratio").reset_index()
wide_px.columns = [f"px_pct_lag{c}" if isinstance(c, int) else c for c in wide_px.columns]
wide_vol.columns = [f"vol_ratio_lag{c}" if isinstance(c, int) else c for c in wide_vol.columns]
wide = wide_px.merge(wide_vol, on=GROUP)

# Flag fragility: sign flip in price change OR vol ratio crossing 1 across lags
px_cols = [c for c in wide.columns if c.startswith("px_pct_lag")]
vol_cols = [c for c in wide.columns if c.startswith("vol_ratio_lag")]
wide["px_sign_flip"] = wide[px_cols].apply(lambda r: (r.min() < 0) & (r.max() > 0), axis=1)
wide["vol_crosses_one"] = wide[vol_cols].apply(lambda r: (r.min() < 1) & (r.max() > 1), axis=1)
wide["px_max_swing_pp"] = (wide[px_cols].max(axis=1) - wide[px_cols].min(axis=1)).round(1)
wide["fragility"] = np.where(
    wide["px_sign_flip"] | wide["vol_crosses_one"], "FRAGILE",
    np.where(wide["px_max_swing_pp"] > 10, "wide-band", "stable"),
)
wide.round(2).to_csv(OUT / "lag_sensitivity_grid.csv", index=False)
print(wide.sort_values("px_max_swing_pp", ascending=False).head(15).round(1).to_string(index=False))
print()
print(f"Cells flagged FRAGILE under lag sensitivity: {(wide['fragility']=='FRAGILE').sum()}")
print(f"Cells stable across all four lags: {(wide['fragility']=='stable').sum()}")
print()

# ─── 2. Poisson CIs on YoY volume ratio ───────────────────────────
print("=" * 75)
print("Poisson CIs on YoY volume ratios (regime cells)")
print("=" * 75)

def poisson_ratio_ci(a: int, b: int, alpha: float = 0.10) -> tuple[float, float]:
    """Two-sided 90% CI on lambda_a / lambda_b for Poisson counts a, b.
    Using exact F-distribution method (Sahai-Khurshid). Returns (lo, hi)."""
    from scipy.stats import f as fdist
    if b == 0:
        return (float("nan"), float("nan"))
    lo = a / (a + (b + 1) * fdist.ppf(1 - alpha / 2, 2 * (b + 1), 2 * max(a, 1)))
    hi = ((a + 1) * fdist.ppf(1 - alpha / 2, 2 * (a + 1), 2 * b)) / b
    return (lo, hi)


regime_lag = pd.read_csv(V3 / "regime_lag_adjusted.csv")
# Note: pre-event is 12 months, post-event window is 3.2 months for raw or 1.6 for lag-45.
# Volume CI compares per-month rates, so normalize.
POST_MONTHS = (POST_END - (PIVOT + pd.Timedelta(days=45))).days / 30.4
PRE_MONTHS = 12.0
rows = []
try:
    from scipy.stats import f as fdist  # noqa
    have_scipy = True
except ImportError:
    have_scipy = False

for _, r in regime_lag.iterrows():
    n_pre = int(r["n_pre"])
    n_post = int(r["n_post"])
    # rate ratio = (n_post/POST_MONTHS) / (n_pre/PRE_MONTHS) = n_post * PRE_MONTHS / (n_pre * POST_MONTHS)
    # For Poisson CI on rate ratio we scale the offset
    # Simpler: bootstrap-free Wald on log ratio
    if n_pre > 0 and n_post > 0:
        log_ratio = np.log((n_post / POST_MONTHS) / (n_pre / PRE_MONTHS))
        se = np.sqrt(1 / n_pre + 1 / n_post)
        lo = float(np.exp(log_ratio - 1.645 * se))
        hi = float(np.exp(log_ratio + 1.645 * se))
    else:
        lo = hi = float("nan")
    rows.append({
        "district": r["district"], "ptype": r["ptype"], "layout": r["layout"],
        "n_pre": n_pre, "n_post": n_post,
        "vol_ratio": round(r["vol_change_ratio"], 2),
        "vol_ratio_ci_lo": round(lo, 2),
        "vol_ratio_ci_hi": round(hi, 2),
        "vol_ci_excludes_one": (lo > 1.0) or (hi < 1.0),
    })
pcis = pd.DataFrame(rows)
pcis.to_csv(OUT / "poisson_vol_cis.csv", index=False)
flipped = pcis[~pcis["vol_ci_excludes_one"]]
print(f"Cells where 90% Poisson CI on vol ratio crosses 1 (i.e. velocity change not significant): {len(flipped)} of {len(pcis)}")
print(pcis.sort_values("vol_ratio", ascending=False).head(12).to_string(index=False))
print()

# ─── 3. Cohort baseline ──────────────────────────────────────────
print("=" * 75)
print("Cohort baseline: pre-shock secondary share by months-since-launch")
print("=" * 75)

# For every project, find the first off-plan-primary registration as "launch".
# Then for each subsequent off-plan registration, compute months-since-launch and
# whether it was secondary. Aggregate the pre-shock baseline secondary share by
# bucket of months-since-launch. Compare to the post-event observed shares.
op = res_fh[res_fh["deal_type"] == "off-plan"].copy()
launch = op[op["market"] == "primary"].groupby(["district", "project"]).agg(
    launch_date=("date", "min"),
).reset_index()
op = op.merge(launch, on=["district", "project"], how="inner")
op["months_since_launch"] = ((op["date"] - op["launch_date"]).dt.days / 30.4).round(0).astype(int)
op["is_secondary"] = (op["market"] == "secondary").astype(int)
op["is_post_shock"] = op["date"] >= PIVOT
op = op[op["months_since_launch"] >= 0]

# Bin by 6-month buckets up to 60 months
op["bucket"] = (op["months_since_launch"] // 6) * 6
pre_baseline = op[~op["is_post_shock"]].groupby("bucket").agg(
    n=("is_secondary", "size"), secondary_share=("is_secondary", "mean"),
).reset_index()
pre_baseline["secondary_share_pct"] = (pre_baseline["secondary_share"] * 100).round(1)
post_obs = op[op["is_post_shock"]].groupby("bucket").agg(
    n=("is_secondary", "size"), secondary_share=("is_secondary", "mean"),
).reset_index()
post_obs["secondary_share_pct"] = (post_obs["secondary_share"] * 100).round(1)
baseline_compare = pre_baseline.merge(
    post_obs.rename(columns={"n": "n_post", "secondary_share_pct": "post_share_pct"}),
    on="bucket", how="left", suffixes=("_pre", "_post"),
)[["bucket", "n", "secondary_share_pct", "n_post", "post_share_pct"]]
baseline_compare["delta_pp"] = (baseline_compare["post_share_pct"] - baseline_compare["secondary_share_pct"]).round(1)
baseline_compare.to_csv(OUT / "cohort_baseline_secondary.csv", index=False)
print("Pre-shock vs post-shock secondary share by months-since-launch bucket:")
print(baseline_compare.to_string(index=False))
print()

# Now mark the v3 cohort dump leaderboard entries against the matched baseline
cohort = pd.read_csv(V3 / "cohort_dump.csv")
cohort["launch_date_dt"] = pd.to_datetime(cohort["launch_date"])
cohort["months_at_post_event_mid"] = ((PIVOT + pd.Timedelta(days=80) - cohort["launch_date_dt"]).dt.days / 30.4).round(0).astype(int)
cohort["baseline_bucket"] = (cohort["months_at_post_event_mid"] // 6) * 6
cohort = cohort.merge(
    pre_baseline[["bucket", "secondary_share_pct"]].rename(columns={
        "bucket": "baseline_bucket", "secondary_share_pct": "baseline_secondary_pct"
    }),
    on="baseline_bucket", how="left",
)
cohort["excess_over_baseline_pp"] = (cohort["secondary_share_pct"] - cohort["baseline_secondary_pct"]).round(1)
cohort = cohort[["district", "project", "launch_year", "off_post_n", "secondary_share_pct",
                 "baseline_secondary_pct", "excess_over_baseline_pp"]]
cohort = cohort.sort_values("excess_over_baseline_pp", ascending=False)
cohort.to_csv(OUT / "cohort_excess_vs_baseline.csv", index=False)
print("Cohort dump excess over matched-time-since-launch pre-shock baseline:")
print(cohort.head(20).to_string(index=False))
print()

# ─── 4. Holm-Bonferroni on shortlist CI gate ─────────────────────
print("=" * 75)
print("Holm-Bonferroni FDR control on per-cell excess-change tests")
print("=" * 75)

# Convert CIs into approximate p-values for the null that excess_change_pct == 0
# Using the half-width of the 90% CI as ~1.645 * SE (normal approx)
regime_lag = regime_lag.dropna(subset=["excess_ci_lo", "excess_ci_hi", "excess_change_pct"])
regime_lag["half_width"] = (regime_lag["excess_ci_hi"] - regime_lag["excess_ci_lo"]) / 2
regime_lag["approx_se"] = regime_lag["half_width"] / 1.645
regime_lag["z"] = regime_lag["excess_change_pct"] / regime_lag["approx_se"].replace(0, np.nan)
from scipy.stats import norm
regime_lag["p_two_sided"] = 2 * (1 - norm.cdf(regime_lag["z"].abs()))

# Holm-Bonferroni
sorted_p = regime_lag.sort_values("p_two_sided").reset_index(drop=True)
m = len(sorted_p)
sorted_p["holm_adj_alpha"] = 0.10 / (m - sorted_p.index)
sorted_p["passes_holm_at_0.10"] = sorted_p["p_two_sided"] < sorted_p["holm_adj_alpha"]
# Convert to step-down: once one fails, all subsequent fail
first_fail = sorted_p["passes_holm_at_0.10"].idxmin() if not sorted_p["passes_holm_at_0.10"].all() else m
if not sorted_p["passes_holm_at_0.10"].iloc[0]:
    first_fail = 0
sorted_p["passes_holm_at_0.10"] = sorted_p.index < first_fail if first_fail else False
# Actually re-derive properly: walk in p order, keep until first fails
holm_passes = []
for i, r in sorted_p.iterrows():
    if r["p_two_sided"] < r["holm_adj_alpha"]:
        holm_passes.append(True)
    else:
        holm_passes.append(False)
        # Once one fails Holm sets all subsequent to fail too
        for j in range(i + 1, len(sorted_p)):
            holm_passes.append(False)
        break
while len(holm_passes) < len(sorted_p):
    holm_passes.append(False)
sorted_p["passes_holm_at_0.10"] = holm_passes
sorted_p[GROUP + ["excess_change_pct", "p_two_sided", "holm_adj_alpha", "passes_holm_at_0.10", "n_post"]].round(4).to_csv(
    OUT / "holm_bonferroni.csv", index=False
)
n_passes = sum(holm_passes)
print(f"Cells passing Holm-Bonferroni at family-wise alpha=0.10: {n_passes} of {m}")
print()
print("Cells that PASS (these are the multiple-comparison-survivable findings):")
passed = sorted_p[sorted_p["passes_holm_at_0.10"]].copy()
print(passed[GROUP + ["excess_change_pct", "p_two_sided", "n_post"]].round(3).to_string(index=False))
print()

# Cross-check against v3 shortlist
shortlist = pd.read_csv(V3 / "post_shock_shortlist_v3.csv")
shortlist_passing = shortlist.merge(
    passed[GROUP], on=GROUP, how="inner",
)
print("v3 shortlist cells that survive Holm-Bonferroni:")
print(shortlist_passing[["district", "ptype", "layout", "net_yield_adj_pct", "total"]].to_string(index=False))
print()

# ─── Final summary ───────────────────────────────────────────────
print("=" * 75)
print("Round 1 statistical rigor SUMMARY")
print("=" * 75)
n_fragile = (wide["fragility"] == "FRAGILE").sum()
n_stable = (wide["fragility"] == "stable").sum()
n_noisy_vol = (~pcis["vol_ci_excludes_one"]).sum()
n_holm_pass = sum(holm_passes)
print(f"Lag sensitivity: {n_stable} of {len(wide)} cells stable across {{30,45,60,90}} day lags;"
      f" {n_fragile} flip sign or volume-class")
print(f"Poisson CIs: {len(pcis) - n_noisy_vol} of {len(pcis)} cells have vol-ratio CI excluding 1 (significant velocity change)")
print(f"Holm-Bonferroni: {n_holm_pass} of {m} cells pass multiple-comparison correction at family-wise alpha=0.10")
print()
print(f"Outputs in {OUT}")
