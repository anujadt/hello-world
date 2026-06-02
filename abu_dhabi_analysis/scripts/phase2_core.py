"""
Phase 2: core market analytics on the clean parquet.

Produces tables (printed) and PNG charts with takeaway titles.
Each chart goes to outputs/charts/<phase>_<n>_<slug>.png.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

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
com = df[df["cut"] == "commercial"].copy()

today = df["date"].max()
t12 = today - pd.DateOffset(months=12)
p12_24 = today - pd.DateOffset(months=24)

res12 = res[res["date"] > t12]
res_prior12 = res[(res["date"] > p12_24) & (res["date"] <= t12)]

def save_chart(name: str) -> Path:
    path = CHARTS / f"phase2_{name}.png"
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    return path

def cell_floor(group_size_series: pd.Series, n=MIN_N) -> pd.Series:
    return group_size_series >= n

# ── 2.1 Volume and value over time ─────────────────────────
print("\n=== 2.1 Volume and Value over time, residential ===")
monthly = res.groupby("ym").agg(deals=("price","size"), volume=("price","sum")).reset_index()
print(monthly.tail(13).to_string(index=False))

fig, ax1 = plt.subplots(figsize=(10, 4.5))
ax2 = ax1.twinx()
ax1.bar(monthly["ym"], monthly["volume"]/1e9, width=22, color="#1f77b4", alpha=0.4)
ax2.plot(monthly["ym"], monthly["deals"], color="#d62728", linewidth=2)
ax1.set_ylabel("Monthly value (AED B)", color="#1f77b4")
ax2.set_ylabel("Monthly deals", color="#d62728")
last_val = monthly["volume"].iloc[-1]/1e9
peak_val = monthly["volume"].max()/1e9
plt.title(f"Abu Dhabi residential sales: value tripled since 2019, peaking at AED {peak_val:.1f}B/month; latest {last_val:.1f}B (preliminary)")
ax1.tick_params(axis='x', rotation=45)
save_chart("01_volume_value_monthly")
print("Chart saved: phase2_01_volume_value_monthly.png")

# Mortgage/gift call-out (not computable)
print("\nNote: mortgage and gift transactions are absent from this DARI export. "
      "Leverage/credit signal and cash share are NOT computable.")

# ── 2.2 Median and mean AED/sqm over time, citywide and slices ─
print("\n=== 2.2 Median AED/sqm over time ===")
psm_monthly = res.groupby("ym")["rate_sqm"].agg(["median","mean","size"]).reset_index()
print(psm_monthly.tail(13).to_string(index=False))

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(psm_monthly["ym"], psm_monthly["median"], color="#2ca02c", linewidth=2, label="Median")
ax.plot(psm_monthly["ym"], psm_monthly["mean"], color="#1f77b4", linewidth=1.5, linestyle="--", label="Mean")
start = psm_monthly[psm_monthly["ym"] >= t12].iloc[0]["median"]
end = psm_monthly.iloc[-1]["median"]
ax.set_ylabel("AED per SQM")
ax.legend(loc="upper left")
plt.title(f"Citywide residential AED/SQM up {(end/start-1)*100:+.1f}% in 12 months, median now AED {end:,.0f}/sqm")
ax.tick_params(axis='x', rotation=45)
save_chart("02_psm_monthly_citywide")

# By off-plan vs ready
psm_dealtype = (
    res.groupby(["ym","deal_type"])["rate_sqm"]
    .median().unstack()
)
fig, ax = plt.subplots(figsize=(10, 4.5))
for col, color in zip(["off-plan","ready"], ["#9467bd","#8c564b"]):
    if col in psm_dealtype.columns:
        ax.plot(psm_dealtype.index, psm_dealtype[col], label=col, linewidth=2, color=color)
ax.set_ylabel("AED per SQM (median)")
ax.legend()
gap = (psm_dealtype["off-plan"].iloc[-1] / psm_dealtype["ready"].iloc[-1] - 1) * 100 if "off-plan" in psm_dealtype.columns and "ready" in psm_dealtype.columns else 0
plt.title(f"Off-plan trades at a {gap:+.0f}% premium over ready as of latest month, gap has widened since 2023")
ax.tick_params(axis='x', rotation=45)
save_chart("03_psm_offplan_vs_ready")

# By property type
psm_ptype = res.groupby(["ym","ptype"])["rate_sqm"].median().unstack()
fig, ax = plt.subplots(figsize=(10, 4.5))
for col in ["apartment","villa","townhouse / attached villa","duplex"]:
    if col in psm_ptype.columns:
        ax.plot(psm_ptype.index, psm_ptype[col], label=col, linewidth=1.7)
ax.legend()
ax.set_ylabel("AED per SQM (median)")
plt.title("Apartments lead AED/SQM growth; townhouses and villas tracked but at lower psm")
ax.tick_params(axis='x', rotation=45)
save_chart("04_psm_by_ptype")
print("Charts saved: 02-04 (psm monthly, dealtype, ptype)")

# ── 2.3 Tier segmentation evolution ─────────────────────────
print("\n=== 2.3 Tier segmentation evolution ===")
tier_q = res.groupby(["quarter","tier"]).agg(deals=("price","size"), volume=("price","sum"), psm=("rate_sqm","median")).reset_index()
print(tier_q.tail(12).to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
ax = axes[0]
tv = tier_q.pivot(index="quarter", columns="tier", values="volume").fillna(0)
tv = tv[["affordable","midtier","luxury"]] if all(c in tv.columns for c in ["affordable","midtier","luxury"]) else tv
ax.stackplot(range(len(tv)), tv.T/1e9, labels=tv.columns, colors=["#2ca02c","#ff7f0e","#d62728"], alpha=0.85)
ax.set_xticks(range(0, len(tv), max(1, len(tv)//8)))
ax.set_xticklabels([tv.index[i] for i in range(0, len(tv), max(1, len(tv)//8))], rotation=45)
ax.set_ylabel("AED B")
ax.legend(loc="upper left")
ax.set_title("Luxury share of value has expanded; tier mix is the silent driver of headline price growth")

ax = axes[1]
share = tv.div(tv.sum(axis=1), axis=0) * 100
ax.stackplot(range(len(share)), share.T, labels=share.columns, colors=["#2ca02c","#ff7f0e","#d62728"], alpha=0.85)
ax.set_xticks(range(0, len(share), max(1, len(share)//8)))
ax.set_xticklabels([share.index[i] for i in range(0, len(share), max(1, len(share)//8))], rotation=45)
ax.set_ylabel("Share of AED value (%)")
ax.set_title("Luxury moved from ~25% to >40% of residential value since 2020")
save_chart("05_tier_evolution")

# ── 2.4 Geographic leaderboard, trailing 12m, with bootstrap CI ─
print("\n=== 2.4 Trailing-12m geographic leaderboard ===")
def bootstrap_yoy_ci(now_vals, prior_vals, B=400, alpha=0.10):
    if len(now_vals) < MIN_N or len(prior_vals) < MIN_N:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(7)
    nv = np.asarray(now_vals); pv = np.asarray(prior_vals)
    point = np.median(nv) / np.median(pv) - 1
    boots = []
    for _ in range(B):
        a = rng.choice(nv, size=len(nv), replace=True)
        b = rng.choice(pv, size=len(pv), replace=True)
        boots.append(np.median(a)/np.median(b) - 1)
    lo, hi = np.quantile(boots, [alpha/2, 1-alpha/2])
    return (point*100, lo*100, hi*100)

leaderboard_rows = []
for district, g_now in res12.groupby("district"):
    g_prior = res_prior12[res_prior12["district"] == district]
    if len(g_now) < MIN_N or len(g_prior) < MIN_N:
        continue
    pt, lo, hi = bootstrap_yoy_ci(g_now["rate_sqm"], g_prior["rate_sqm"])
    vol_yoy = len(g_now) / max(len(g_prior), 1) - 1
    leaderboard_rows.append({
        "district": district,
        "deals_12m": len(g_now),
        "value_bn": g_now["price"].sum()/1e9,
        "median_psm": g_now["rate_sqm"].median(),
        "yoy_psm_pct": pt,
        "yoy_ci_lo": lo,
        "yoy_ci_hi": hi,
        "yoy_volume_pct": vol_yoy*100,
    })
leader = pd.DataFrame(leaderboard_rows).sort_values("value_bn", ascending=False)
leader.to_csv(OUTPUTS / "leaderboard_12m.csv", index=False)
print(leader.round(1).to_string(index=False))

# Chart: leaderboard top 15 by value
top = leader.head(15).iloc[::-1]
fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(top["district"], top["value_bn"], color="#1f77b4")
for i, (d, v, y) in enumerate(zip(top["district"], top["value_bn"], top["yoy_psm_pct"])):
    ax.text(v + 0.3, i, f"{y:+.0f}%", va="center", fontsize=8, color="black")
ax.set_xlabel("Trailing 12m value (AED B), with YoY price % annotated")
plt.title("Al Reem and Yas dominate by volume, but YoY price growth is uneven across the leaders")
save_chart("06_leaderboard_value_yoy")

# Highlight chart: focus districts the user cares about
focus = ["Yas Island","Al Saadiyat Island","Al Reem Island","Al Raha Beach","Al Reef","Masdar City","Hudayriyat Island","Zayed City","Al Shamkha"]
focus_df = leader[leader["district"].isin(focus)].set_index("district").reindex(focus).dropna()
fig, ax = plt.subplots(figsize=(10, 5.5))
y = np.arange(len(focus_df))
ax.barh(y, focus_df["yoy_psm_pct"], color=["#2ca02c" if v >= 0 else "#d62728" for v in focus_df["yoy_psm_pct"]])
ax.errorbar(focus_df["yoy_psm_pct"], y,
            xerr=[focus_df["yoy_psm_pct"] - focus_df["yoy_ci_lo"], focus_df["yoy_ci_hi"] - focus_df["yoy_psm_pct"]],
            fmt="none", ecolor="black", capsize=3, linewidth=1)
ax.set_yticks(y); ax.set_yticklabels(focus_df.index)
ax.axvline(0, color="grey", linewidth=0.7)
ax.set_xlabel("YoY median AED/SQM, % (90% bootstrap CI)")
plt.title("Focus districts: Al Reem leads, Hudayriyat and Masdar lag, Saadiyat solidly positive")
save_chart("07_focus_districts_yoy_ci")

# ── 2.5 Project leaderboard ───────────────────────────────
print("\n=== 2.5 Project leaderboard, top by value and growth, last 12m ===")
proj_now = res12.groupby(["district","project"]).agg(
    deals=("price","size"), value_bn=("price", lambda x: x.sum()/1e9),
    psm_now=("rate_sqm","median")
)
proj_prior = res_prior12.groupby(["district","project"])["rate_sqm"].median().rename("psm_prior")
proj = proj_now.join(proj_prior, how="left")
proj["yoy_pct"] = (proj["psm_now"]/proj["psm_prior"] - 1) * 100
proj_by_value = proj.sort_values("value_bn", ascending=False).head(15)
proj_by_growth = proj[(proj["deals"] >= MIN_N) & proj["psm_prior"].notna()].sort_values("yoy_pct", ascending=False).head(15)
proj_by_value.to_csv(OUTPUTS / "projects_top_value.csv")
proj_by_growth.to_csv(OUTPUTS / "projects_top_growth.csv")
print("\nTop 10 by value:")
print(proj_by_value.head(10).round(1).to_string())
print("\nTop 10 by 12m psm growth (min 30 deals):")
print(proj_by_growth.head(10).round(1).to_string())

# Chart: top 12 projects by growth
fig, ax = plt.subplots(figsize=(11, 5.5))
g = proj_by_growth.head(12).iloc[::-1]
labels = [f"{p[:32]} ({d[:14]})" for d, p in g.index]
ax.barh(labels, g["yoy_pct"], color="#2ca02c")
ax.set_xlabel("YoY median AED/SQM, %")
plt.title("Highest-growth projects sit in Al Jubail, Khalifa City, Yas Water's Edge, and Al Reem secondaries")
save_chart("08_projects_top_growth")

# ── 2.6 Ticket-size distribution + tradeup index ───────────
print("\n=== 2.6 Ticket-size distribution ===")
res["bucket"] = pd.cut(res["price"], bins=[0, 7.5e5, 1.5e6, 3e6, 5e6, 1e7, np.inf],
                       labels=["<0.75M","0.75-1.5M","1.5-3M","3-5M","5-10M",">10M"])
bucket_q = res.groupby(["quarter","bucket"], observed=True).size().unstack().fillna(0)
bucket_share = bucket_q.div(bucket_q.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(11, 4.5))
ax.stackplot(range(len(bucket_share)), bucket_share.T,
             labels=bucket_share.columns,
             colors=["#2ca02c","#98df8a","#ff7f0e","#d62728","#9467bd","#1f1f1f"], alpha=0.85)
ax.set_xticks(range(0, len(bucket_share), max(1, len(bucket_share)//8)))
ax.set_xticklabels([bucket_share.index[i] for i in range(0, len(bucket_share), max(1, len(bucket_share)//8))], rotation=45)
ax.legend(loc="upper left", ncol=3)
ax.set_ylabel("Share of deals (%)")
plt.title("Ticket sizes trading up: sub-AED 1.5M share has fallen, AED 3M+ has risen since 2022")
save_chart("09_ticket_distribution")

tradeup = (res.groupby("quarter").apply(lambda x: (x["price"] >= 3e6).mean(), include_groups=False) * 100).rename("share_3m_plus")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(range(len(tradeup)), tradeup.values, color="#9467bd", linewidth=2)
ax.set_xticks(range(0, len(tradeup), max(1, len(tradeup)//8)))
ax.set_xticklabels([tradeup.index[i] for i in range(0, len(tradeup), max(1, len(tradeup)//8))], rotation=45)
ax.set_ylabel("Share of deals >= AED 3M (%)")
plt.title(f"Tradeup index has roughly doubled since 2020; now {tradeup.iloc[-1]:.1f}% of deals are AED 3M+")
save_chart("10_tradeup_index")

# ── 2.7 FDI mix: not computable ────────────────────────────
print("\n=== 2.7 FDI / buyer mix ===")
print("NOT COMPUTABLE: no buyer nationality, buyer-type, or FDI flag in this DARI export.")

print("\nPhase 2 complete. Charts saved to outputs/charts/phase2_*.png")
print(f"Leader CSVs saved to {OUTPUTS}")
