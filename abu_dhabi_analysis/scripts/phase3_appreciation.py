"""
Phase 3: appreciation, mix decomposition, cycle classification.

Outputs:
  outputs/hedonic_citywide_path.csv      mix-adjusted quarterly index, citywide
  outputs/hedonic_district_paths.csv     per-district indices (top by liquidity)
  outputs/offplan_to_handover.csv        cohort uplift, separate from hedonic
  outputs/mix_decomposition.csv          within vs mix shift
  outputs/momentum_trio.csv              3m/12m/quarter-yoy per district
  outputs/cycle_classification.csv       early-recovery / mid / late / cooling
  outputs/offplan_supply_pressure.csv    24m offplan-share trajectory
  charts: phase3_*.png
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUTPUTS, CHARTS, PARQUET, load_config

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 140,
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

cfg = load_config()
MIN_N = cfg["cleaning"]["min_cell_n"]

df = pd.read_parquet(PARQUET)
res = df[df["cut"] == "residential"].copy()
res["log_psm"] = np.log(res["rate_sqm"])
res["q_dummy"] = res["quarter"].astype(str)

def save_chart(name: str) -> Path:
    path = CHARTS / f"phase3_{name}.png"
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path

# ── 3.1 Citywide hedonic index ─────────────────────────────
# log(psm) ~ C(ptype) + C(district) + C(layout) + C(deal_type) + C(market) + C(quarter)
print("=== 3.1 Hedonic citywide index ===")

# Drop layouts with too few obs to avoid singular design.
layout_counts = res["layout"].value_counts()
keep_layouts = layout_counts[layout_counts >= 100].index
sub = res[res["layout"].isin(keep_layouts)].copy()

formula = "log_psm ~ C(ptype) + C(district) + C(layout) + C(deal_type) + C(market) + C(q_dummy)"
model = ols(formula, data=sub).fit(cov_type="HC1")
print(f"Citywide hedonic R2 adj: {model.rsquared_adj:.4f}, n={int(model.nobs):,}")

# Extract quarter coefficients as the citywide path. Baseline quarter is the first sorted quarter.
quarters_sorted = sorted(sub["q_dummy"].unique())
baseline_q = quarters_sorted[0]
coef_idx = [name for name in model.params.index if name.startswith("C(q_dummy)")]
path = {baseline_q: 1.0}
for name in coef_idx:
    # Format: C(q_dummy)[T.2019Q2]
    q = name.split("T.")[1].rstrip("]")
    path[q] = float(np.exp(model.params[name]))
hed_city = pd.Series(path).sort_index().rename("citywide_hedonic_index")
hed_city.to_csv(OUTPUTS / "hedonic_citywide_path.csv", header=True)

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(range(len(hed_city)), hed_city.values * 100, color="#1f77b4", linewidth=2)
ax.set_xticks(range(0, len(hed_city), max(1, len(hed_city)//8)))
ax.set_xticklabels([hed_city.index[i] for i in range(0, len(hed_city), max(1, len(hed_city)//8))], rotation=45)
ax.axhline(100, color="grey", linestyle="--", linewidth=0.7)
final = hed_city.iloc[-1] * 100
plt.title(f"Mix-adjusted citywide AED/SQM index up {final-100:+.0f}% vs Q1 2019 (R2 adj {model.rsquared_adj:.2f})")
ax.set_ylabel("Index, baseline 2019Q1 = 100")
save_chart("01_hedonic_citywide_index")

# ── 3.2 Per-district hedonic paths ─────────────────────────
print("\n=== 3.2 Per-district hedonic paths (top 10 by liquidity) ===")
top_districts = res["district"].value_counts().head(10).index.tolist()
district_paths = {}
for d in top_districts:
    sub_d = sub[sub["district"] == d]
    if sub_d["q_dummy"].nunique() < 8 or len(sub_d) < 500:
        continue
    # Use a simpler model per district (no district fixed effect needed)
    try:
        m = ols("log_psm ~ C(ptype) + C(layout) + C(deal_type) + C(market) + C(q_dummy)", data=sub_d).fit(cov_type="HC1")
    except Exception:
        continue
    qs = sorted(sub_d["q_dummy"].unique())
    base = qs[0]
    p = {base: 1.0}
    for name in m.params.index:
        if name.startswith("C(q_dummy)"):
            q = name.split("T.")[1].rstrip("]")
            p[q] = float(np.exp(m.params[name]))
    district_paths[d] = pd.Series(p).sort_index()

dp_df = pd.DataFrame(district_paths)
dp_df.to_csv(OUTPUTS / "hedonic_district_paths.csv")

fig, ax = plt.subplots(figsize=(11, 5.5))
for d, s in district_paths.items():
    ax.plot(range(len(s)), s.values * 100, label=d, linewidth=1.6)
ax.axhline(100, color="grey", linestyle="--", linewidth=0.6)
labels_full = sorted({q for s in district_paths.values() for q in s.index})
ax.set_xticks(range(0, len(labels_full), max(1, len(labels_full)//8)))
ax.set_xticklabels([labels_full[i] for i in range(0, len(labels_full), max(1, len(labels_full)//8))], rotation=45)
ax.legend(loc="upper left", fontsize=7, ncol=2)
ax.set_ylabel("Mix-adjusted index (own baseline = 100)")
plt.title("Hedonic paths diverge by district; Reem, Raha Beach, Hudayriyat are the steepest ascents")
save_chart("02_hedonic_district_paths")

# ── 3.3 Off-plan-to-handover cohort uplift ─────────────────
print("\n=== 3.3 Off-plan-to-handover uplift by district ===")
# For each district x project, find median off-plan psm during launch year and
# median ready psm during the FOLLOWING years. Difference = handover uplift signal.
oth_rows = []
for d in res["district"].dropna().unique():
    g = res[res["district"] == d]
    if len(g) < 500:
        continue
    off = g[g["deal_type"] == "off-plan"]
    rdy = g[g["deal_type"] == "ready"]
    if len(off) < MIN_N or len(rdy) < MIN_N:
        continue
    # Cohort by launch year of off-plan
    for yr, off_yr in off.groupby("year"):
        if len(off_yr) < MIN_N:
            continue
        # Ready resales in subsequent two years
        rdy_next = rdy[rdy["year"].between(yr+1, yr+3)]
        if len(rdy_next) < MIN_N:
            continue
        off_med = off_yr["rate_sqm"].median()
        rdy_med = rdy_next["rate_sqm"].median()
        oth_rows.append({
            "district": d, "launch_year": int(yr),
            "off_plan_psm": off_med, "ready_psm_next1to3y": rdy_med,
            "uplift_pct": (rdy_med/off_med - 1) * 100,
            "off_plan_n": len(off_yr), "ready_next_n": len(rdy_next),
        })
oth = pd.DataFrame(oth_rows).sort_values(["district","launch_year"])
oth.to_csv(OUTPUTS / "offplan_to_handover.csv", index=False)
print(oth.round(1).head(30).to_string(index=False))

# Aggregate per district: average uplift across cohorts
oth_agg = oth.groupby("district").agg(
    cohorts=("uplift_pct","size"),
    median_uplift_pct=("uplift_pct","median"),
).sort_values("median_uplift_pct", ascending=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
top_o = oth_agg.head(12).iloc[::-1]
ax.barh(top_o.index, top_o["median_uplift_pct"],
        color=["#2ca02c" if v >= 0 else "#d62728" for v in top_o["median_uplift_pct"]])
ax.set_xlabel("Median off-plan launch psm to ready psm uplift (% across cohorts)")
plt.title("Off-plan to handover uplift: where buying off-plan has historically repriced into a ready premium")
save_chart("03_offplan_to_handover_uplift")

# ── 3.4 Mix-vs-price decomposition ─────────────────────────
print("\n=== 3.4 Mix vs price decomposition, latest 12m vs prior 12m ===")
today = res["date"].max()
t12 = today - pd.DateOffset(months=12)
t24 = today - pd.DateOffset(months=24)
A = res[res["date"] > t12]            # current period
B = res[(res["date"] > t24) & (res["date"] <= t12)]  # prior period

# Define cells by ptype x tier x deal_type
cell_cols = ["ptype","tier","deal_type"]
A_cell = A.groupby(cell_cols).agg(n_A=("rate_sqm","size"), psm_A=("rate_sqm","median")).reset_index()
B_cell = B.groupby(cell_cols).agg(n_B=("rate_sqm","size"), psm_B=("rate_sqm","median")).reset_index()
merged = A_cell.merge(B_cell, on=cell_cols, how="outer").fillna(0)
total_A = merged["n_A"].sum(); total_B = merged["n_B"].sum()
merged["w_A"] = merged["n_A"] / total_A
merged["w_B"] = merged["n_B"] / total_B

# Headline: difference in weighted means
headline_A = (merged["w_A"] * merged["psm_A"].fillna(0)).sum()
headline_B = (merged["w_B"] * merged["psm_B"].fillna(0)).sum()
# Counterfactual: A weights with B prices (price effect at A mix), B weights with A prices (mix effect)
counter_priceA_mixB = (merged["w_B"] * merged["psm_A"].fillna(0)).sum()
counter_priceB_mixA = (merged["w_A"] * merged["psm_B"].fillna(0)).sum()

price_effect = counter_priceA_mixB - headline_B          # holding mix at B, prices moved A
mix_effect   = headline_A - counter_priceA_mixB           # then mix shifted
total_change = headline_A - headline_B

mix_share = mix_effect / total_change if total_change else np.nan
print(f"Headline weighted psm now: AED {headline_A:,.0f}, prior: AED {headline_B:,.0f}")
print(f"Total change: AED {total_change:+,.0f} ({total_change/headline_B*100:+.1f}%)")
print(f"  Pure price effect:  AED {price_effect:+,.0f}  ({price_effect/total_change*100:+.1f}% of change)")
print(f"  Mix-shift effect:   AED {mix_effect:+,.0f}    ({mix_effect/total_change*100:+.1f}% of change)")

mix_table = pd.DataFrame({
    "metric": ["weighted_psm_now","weighted_psm_prior","total_change","price_effect","mix_effect"],
    "value":  [headline_A, headline_B, total_change, price_effect, mix_effect],
})
mix_table.to_csv(OUTPUTS / "mix_decomposition.csv", index=False)

fig, ax = plt.subplots(figsize=(7.5, 4.5))
bars = ax.bar(["Headline change","Pure price","Mix shift"],
              [total_change, price_effect, mix_effect],
              color=["#1f77b4","#2ca02c","#ff7f0e"])
for b, v in zip(bars, [total_change, price_effect, mix_effect]):
    ax.text(b.get_x()+b.get_width()/2, v + (50 if v>=0 else -200), f"AED {v:+,.0f}", ha="center", fontsize=9)
ax.axhline(0, color="grey", linewidth=0.5)
ax.set_ylabel("Change in weighted psm (AED)")
share_pct = mix_share*100 if not np.isnan(mix_share) else 0
plt.title(f"Headline psm growth: {(1-mix_share)*100:.0f}% pure price, {share_pct:.0f}% mix shift (luxury/off-plan)")
save_chart("04_mix_decomposition")

# ── 3.5 Momentum trio per district ─────────────────────────
print("\n=== 3.5 Momentum trio per district ===")
def medians(window_start, window_end, district):
    g = res[(res["district"] == district) & (res["date"] > window_start) & (res["date"] <= window_end)]
    return (g["rate_sqm"].median(), len(g))

m_rows = []
t3 = today - pd.DateOffset(months=3); t6 = today - pd.DateOffset(months=6)
last_q_end = today; last_q_start = today - pd.DateOffset(months=3)
yoy_q_end = today - pd.DateOffset(months=12); yoy_q_start = yoy_q_end - pd.DateOffset(months=3)

for d in res["district"].dropna().unique():
    g = res[res["district"] == d]
    if len(g) < 200:
        continue
    m_now3, n_now3 = medians(t3, today, d)
    m_prior3, n_prior3 = medians(t6, t3, d)
    m_now12, n_now12 = medians(t12, today, d)
    m_prior12, n_prior12 = medians(t24, t12, d)
    m_lq, n_lq = medians(last_q_start, last_q_end, d)
    m_yq, n_yq = medians(yoy_q_start, yoy_q_end, d)

    if not (n_now3 >= MIN_N and n_prior3 >= MIN_N and n_now12 >= MIN_N and n_prior12 >= MIN_N):
        continue
    delta_3m = (m_now3/m_prior3 - 1) * 100 if m_prior3 else np.nan
    delta_12m = (m_now12/m_prior12 - 1) * 100 if m_prior12 else np.nan
    delta_qyoy = (m_lq/m_yq - 1) * 100 if m_yq and n_lq >= MIN_N and n_yq >= MIN_N else np.nan
    # Accel: 3m > 12m delta (recent stronger than annual)
    accel = "accelerating" if (not np.isnan(delta_3m) and not np.isnan(delta_12m) and delta_3m > delta_12m + 5) else \
            "decelerating" if (not np.isnan(delta_3m) and not np.isnan(delta_12m) and delta_3m < delta_12m - 5) else "flat"
    m_rows.append({
        "district": d, "deals_12m": n_now12,
        "delta_3m_pct": delta_3m, "delta_12m_pct": delta_12m, "delta_qyoy_pct": delta_qyoy,
        "momentum": accel,
    })
mom = pd.DataFrame(m_rows).sort_values("delta_12m_pct", ascending=False)
mom.to_csv(OUTPUTS / "momentum_trio.csv", index=False)
print(mom.round(1).to_string(index=False))

# ── 3.6 Cycle classification ───────────────────────────────
print("\n=== 3.6 Cycle classification ===")
# For each major district, compute:
#  - current psm vs own 2019-2026 percentile
#  - momentum direction (12m)
#  - volume trend (last 12m vs prior 12m)
# Then classify.
cyc_rows = []
for d in res["district"].dropna().unique():
    g_all = res[res["district"] == d]
    g_now = g_all[g_all["date"] > t12]
    g_prior = g_all[(g_all["date"] > t24) & (g_all["date"] <= t12)]
    if len(g_now) < MIN_N or len(g_prior) < MIN_N:
        continue
    # Build a quarterly median series for the district then rank current
    qs = g_all.groupby("quarter")["rate_sqm"].median()
    cur = qs.iloc[-1]
    pct = (qs <= cur).mean() * 100
    mom12 = g_now["rate_sqm"].median() / g_prior["rate_sqm"].median() - 1
    vol_change = len(g_now) / len(g_prior) - 1
    # Classification rules
    if mom12 > 0.10 and pct < 70 and vol_change > 0:
        cls = "early-recovery"
    elif mom12 > 0.05 and pct < 90 and vol_change > -0.05:
        cls = "mid-cycle"
    elif mom12 > 0.0 and (pct >= 90 or vol_change < -0.10):
        cls = "late-cycle/overheating"
    elif mom12 <= 0.0:
        cls = "cooling"
    else:
        cls = "mid-cycle"
    cyc_rows.append({
        "district": d, "psm_now": cur, "pct_vs_own_history": pct,
        "yoy_pct": mom12*100, "vol_change_pct": vol_change*100,
        "cycle": cls, "deals_12m": len(g_now),
    })
cyc = pd.DataFrame(cyc_rows).sort_values(["cycle","yoy_pct"], ascending=[True, False])
cyc.to_csv(OUTPUTS / "cycle_classification.csv", index=False)
print(cyc.round(1).to_string(index=False))

# Cycle chart: scatter price-percentile vs momentum, color by class
fig, ax = plt.subplots(figsize=(10, 6))
color_map = {
    "early-recovery": "#1f77b4",
    "mid-cycle": "#2ca02c",
    "late-cycle/overheating": "#d62728",
    "cooling": "#9467bd",
}
for cls, sub_c in cyc.groupby("cycle"):
    ax.scatter(sub_c["pct_vs_own_history"], sub_c["yoy_pct"],
               s=np.clip(sub_c["deals_12m"]/10, 30, 600),
               color=color_map.get(cls, "grey"), alpha=0.7, label=cls, edgecolors="black", linewidths=0.5)
for _, r in cyc.iterrows():
    if r["deals_12m"] > 500:
        ax.annotate(r["district"], (r["pct_vs_own_history"], r["yoy_pct"]),
                    fontsize=7, alpha=0.85, xytext=(3,3), textcoords="offset points")
ax.axvline(70, color="grey", linestyle="--", linewidth=0.5)
ax.axhline(0, color="grey", linestyle="--", linewidth=0.5)
ax.set_xlabel("Current AED/SQM percentile vs own 2019-2026 history")
ax.set_ylabel("Trailing 12m YoY psm growth (%)")
ax.legend(loc="lower right")
plt.title("Cycle map: top-right = late-cycle / overheating, bottom-left = early-recovery candidates")
save_chart("05_cycle_map")

# ── 3.7 Off-plan supply pressure ───────────────────────────
print("\n=== 3.7 Off-plan supply pressure (24m share trajectory) ===")
oss_rows = []
for d in res["district"].dropna().unique():
    g_now = res[(res["district"] == d) & (res["date"] > t12)]
    g_prior = res[(res["district"] == d) & (res["date"] > t24) & (res["date"] <= t12)]
    if len(g_now) < MIN_N or len(g_prior) < MIN_N:
        continue
    share_now = (g_now["deal_type"] == "off-plan").mean() * 100
    share_prior = (g_prior["deal_type"] == "off-plan").mean() * 100
    oss_rows.append({
        "district": d,
        "offplan_share_12m_pct": share_now,
        "offplan_share_prior12m_pct": share_prior,
        "share_change_pp": share_now - share_prior,
        "deals_12m": len(g_now),
    })
oss = pd.DataFrame(oss_rows).sort_values("share_change_pp", ascending=False)
oss.to_csv(OUTPUTS / "offplan_supply_pressure.csv", index=False)
print(oss.round(1).to_string(index=False))

fig, ax = plt.subplots(figsize=(10, 5.5))
top_oss = oss.head(15).iloc[::-1]
ax.barh(top_oss["district"], top_oss["share_change_pp"],
        color=["#d62728" if v >= 10 else "#ff7f0e" if v > 0 else "#2ca02c" for v in top_oss["share_change_pp"]])
ax.set_xlabel("Change in off-plan share, ppts (last 12m vs prior 12m)")
plt.title("Forward supply pressure: rising off-plan share signals future inventory that could cap prices")
save_chart("06_offplan_supply_pressure")

# ── 3.8 Seasonality ────────────────────────────────────────
print("\n=== 3.8 Seasonality ===")
res["month_num"] = res["date"].dt.month
seasonal = res.groupby(["year","month_num"]).size().unstack()
fig, ax = plt.subplots(figsize=(10, 5))
for yr in seasonal.index:
    if pd.isna(yr):
        continue
    ax.plot(range(1, 13), seasonal.loc[yr].reindex(range(1,13)).fillna(0).values,
            linewidth=1.4 if yr in [2024, 2025, 2026] else 0.7,
            alpha=0.95 if yr in [2024, 2025, 2026] else 0.5,
            label=str(int(yr)))
ax.set_xticks(range(1,13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
ax.legend(ncol=2, fontsize=7)
ax.set_ylabel("Monthly residential deals")
plt.title("Seasonality is real but mild: H2 typically heavier; 2024-25 broke the pattern with a sustained surge")
save_chart("07_seasonality")

print("\nPhase 3 complete. Charts saved to outputs/charts/phase3_*.png")
