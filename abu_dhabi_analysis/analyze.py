"""
Abu Dhabi Real Estate — Investor Intelligence Report
Analyzing 114k+ transactions to surface alpha for an investor.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 140,
    "font.size": 9,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

SRC = "/root/.claude/uploads/87146dfe-f525-41fc-a638-d5be328ee62f/17939a6b-recent_sales_2.csv"
OUT = Path("/home/user/hello-world/abu_dhabi_analysis")
OUT.mkdir(exist_ok=True)

df = pd.read_csv(SRC, parse_dates=["Sale Application Date"])
df.columns = [c.strip() for c in df.columns]

# Rename for ease
df = df.rename(columns={
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
    "Asset Class": "asset",
    "Property Type": "ptype",
})

# Clean
for c in ["sqm", "land_sqm", "price", "share", "rate_sqm"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Filter sane records
df = df[(df["price"] > 0) & (df["sqm"] > 0) & (df["rate_sqm"] > 0)]
df = df[df["share"] > 0.99]  # Full-share deals only — cleaner for psf comps
df["year"] = df["date"].dt.year
df["ym"] = df["date"].dt.to_period("M").dt.to_timestamp()
df["psf"] = df["rate_sqm"] / 10.764  # AED per sqft for international comp

print(f"Dataset: {len(df):,} clean full-share transactions")
print(f"Date range: {df['date'].min().date()} → {df['date'].max().date()}")
print(f"Total volume: AED {df['price'].sum()/1e9:.1f}B")
print()

# ── EXECUTIVE NUMBERS ──────────────────────────────────────
print("="*70)
print("MARKET SNAPSHOT")
print("="*70)
total_val = df["price"].sum()
median_price = df["price"].median()
median_rate = df["rate_sqm"].median()
print(f"Transactions analyzed   : {len(df):,}")
print(f"Aggregate sales value   : AED {total_val/1e9:.2f}B  (≈USD {total_val/1e9/3.67:.2f}B)")
print(f"Median ticket           : AED {median_price/1e6:.2f}M")
print(f"Median rate             : AED {median_rate:,.0f}/sqm (AED {median_rate/10.764:,.0f}/sqft)")
print(f"Off-plan share          : {(df['deal_type']=='off-plan').mean()*100:.1f}%")
print(f"Primary market share    : {(df['market']=='primary').mean()*100:.1f}%")
print(f"Residential share       : {(df['asset']=='residential').mean()*100:.1f}%")
print()

# ── TIME TREND ─────────────────────────────────────────────
monthly = df.groupby("ym").agg(
    deals=("price", "size"),
    volume=("price", "sum"),
    median_rate=("rate_sqm", "median"),
    median_price=("price", "median"),
).reset_index()
print("="*70)
print("12-MONTH PRICE TRAJECTORY (median AED/SQM)")
print("="*70)
last12 = monthly.tail(13)
first = last12.iloc[0]["median_rate"]
last = last12.iloc[-1]["median_rate"]
print(f"Start ({last12.iloc[0]['ym'].strftime('%b %Y')}): AED {first:,.0f}/sqm")
print(f"End   ({last12.iloc[-1]['ym'].strftime('%b %Y')}): AED {last:,.0f}/sqm")
print(f"Δ                       : {(last/first-1)*100:+.1f}% in 12 months")
print()

# ── DISTRICT LEAGUE TABLE ──────────────────────────────────
district = df.groupby("district").agg(
    deals=("price", "size"),
    volume_bn=("price", lambda x: x.sum()/1e9),
    median_rate=("rate_sqm", "median"),
    median_price=("price", "median"),
    off_plan_pct=("deal_type", lambda x: (x=="off-plan").mean()*100),
).round(2).sort_values("volume_bn", ascending=False)
print("="*70)
print("DISTRICT LEAGUE TABLE — by aggregate AED volume")
print("="*70)
print(district.head(15).to_string())
print()

# ── 12M PRICE MOMENTUM by DISTRICT ─────────────────────────
cutoff_now = df["date"].max()
cutoff_12 = cutoff_now - pd.DateOffset(months=12)
cutoff_24 = cutoff_now - pd.DateOffset(months=24)
recent = df[df["date"] > cutoff_12]
prior  = df[(df["date"] > cutoff_24) & (df["date"] <= cutoff_12)]

mom = pd.DataFrame({
    "deals_12m": recent.groupby("district").size(),
    "rate_now": recent.groupby("district")["rate_sqm"].median(),
    "rate_prior": prior.groupby("district")["rate_sqm"].median(),
}).dropna()
mom = mom[mom["deals_12m"] >= 200]
mom["yoy_%"] = (mom["rate_now"]/mom["rate_prior"] - 1) * 100
mom = mom.sort_values("yoy_%", ascending=False)
print("="*70)
print("PRICE MOMENTUM — last 12m vs prior 12m (min 200 deals)")
print("="*70)
print(mom.round(1).to_string())
print()

# ── LIQUIDITY ──────────────────────────────────────────────
liq = recent.groupby("district").agg(
    deals_12m=("price", "size"),
    median_days_between=("date", lambda x: 365/max(len(x),1)),
    volume_12m_bn=("price", lambda x: x.sum()/1e9),
).sort_values("deals_12m", ascending=False)
print("="*70)
print("LIQUIDITY — TRADING ACTIVITY (last 12 months)")
print("="*70)
print(liq.head(12).round(3).to_string())
print()

# ── PROJECT-LEVEL ALPHA — best price growth ────────────────
proj_now = recent.groupby(["district","project"])["rate_sqm"].agg(["median","size"])
proj_prior = prior.groupby(["district","project"])["rate_sqm"].median()
proj = proj_now.join(proj_prior.rename("rate_prior"), how="inner")
proj.columns = ["rate_now","deals_12m","rate_prior"]
proj = proj[proj["deals_12m"] >= 30]
proj["yoy_%"] = (proj["rate_now"]/proj["rate_prior"] - 1) * 100
top_winners = proj.sort_values("yoy_%", ascending=False).head(15)
top_losers  = proj.sort_values("yoy_%").head(10)
print("="*70)
print("PROJECT WINNERS — top 15 YoY price growth (min 30 deals)")
print("="*70)
print(top_winners.round(1).to_string())
print()
print("="*70)
print("PROJECT LAGGARDS — bottom 10 (potential value buys OR avoid)")
print("="*70)
print(top_losers.round(1).to_string())
print()

# ── OFF-PLAN vs READY SPREAD (the carry trade) ────────────
spread = df[df["date"] > cutoff_12].groupby(["district","deal_type"])["rate_sqm"].median().unstack()
spread = spread.dropna()
spread["off_vs_ready_%"] = (spread["off-plan"]/spread["ready"] - 1) * 100
spread = spread.sort_values("off_vs_ready_%")
print("="*70)
print("OFF-PLAN vs READY SPREAD — where new builds trade at discount/premium")
print("="*70)
print(spread.round(0).to_string())
print()

# ── LAYOUT ECONOMICS ──────────────────────────────────────
layout = recent[recent["asset"]=="residential"].groupby("layout").agg(
    deals=("price","size"),
    median_price=("price","median"),
    median_rate=("rate_sqm","median"),
    median_sqm=("sqm","median"),
).sort_values("deals", ascending=False).head(12)
print("="*70)
print("RESIDENTIAL LAYOUT MIX — last 12m")
print("="*70)
print(layout.round(0).to_string())
print()

# ── ENTRY-LEVEL HUNTING GROUNDS ───────────────────────────
entry = recent[(recent["asset"]=="residential") & (recent["price"] < 1_500_000)]
entry_district = entry.groupby("district").agg(
    deals=("price","size"),
    median_price=("price","median"),
    median_rate=("rate_sqm","median"),
).sort_values("deals", ascending=False).head(10)
print("="*70)
print("SUB-1.5M ENTRY POINTS — where the volume is")
print("="*70)
print(entry_district.round(0).to_string())
print()

# Save tables to CSV for later reference
district.to_csv(OUT/"district_league.csv")
mom.to_csv(OUT/"momentum_yoy.csv")
top_winners.to_csv(OUT/"project_winners.csv")
top_losers.to_csv(OUT/"project_laggards.csv")
spread.to_csv(OUT/"offplan_vs_ready.csv")
monthly.to_csv(OUT/"monthly_trend.csv", index=False)

# ── CHARTS ────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

# 1. Monthly volume + price
ax = axes[0,0]
ax2 = ax.twinx()
ax.bar(monthly["ym"], monthly["volume"]/1e9, width=22, color="#1f77b4", alpha=0.4, label="Volume (AED B)")
ax2.plot(monthly["ym"], monthly["median_rate"], color="#d62728", linewidth=2, label="Median AED/SQM")
ax.set_title("Abu Dhabi monthly volume vs median rate")
ax.set_ylabel("Volume (AED B)"); ax2.set_ylabel("AED / SQM")
ax.tick_params(axis='x', rotation=45)
ax2.spines["top"].set_visible(False)

# 2. Top districts by 12m volume
ax = axes[0,1]
top12 = liq.head(10).iloc[::-1]
ax.barh(top12.index, top12["volume_12m_bn"], color="#2ca02c")
ax.set_title("Top 10 districts — last 12m AED volume (B)")
ax.set_xlabel("AED Billion")

# 3. Momentum scatter — risk vs reward
ax = axes[1,0]
sizes = (mom["deals_12m"]/mom["deals_12m"].max() * 600).clip(20, 600)
sc = ax.scatter(mom["rate_now"], mom["yoy_%"], s=sizes,
                c=mom["yoy_%"], cmap="RdYlGn", alpha=0.75, edgecolors="black", linewidths=0.5)
for d in mom.index:
    ax.annotate(d, (mom.loc[d,"rate_now"], mom.loc[d,"yoy_%"]), fontsize=7, alpha=0.85)
ax.axhline(0, color="grey", linestyle="--", linewidth=0.7)
ax.set_xlabel("Median rate AED/SQM (current)"); ax.set_ylabel("YoY price growth %")
ax.set_title("Momentum map — bubble size = liquidity")

# 4. Off-plan discount/premium
ax = axes[1,1]
sp = spread.head(12)
colors = ["#d62728" if v > 0 else "#2ca02c" for v in sp["off_vs_ready_%"]]
ax.barh(sp.index, sp["off_vs_ready_%"], color=colors)
ax.axvline(0, color="black", linewidth=0.5)
ax.set_title("Off-plan vs ready price spread by district\n(<0 = off-plan cheaper)")
ax.set_xlabel("Off-plan premium over ready (%)")

plt.tight_layout()
plt.savefig(OUT/"abu_dhabi_dashboard.png", bbox_inches="tight")
print(f"Saved dashboard → {OUT/'abu_dhabi_dashboard.png'}")

# Second figure: Project winners and yield proxy
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))
ax = axes2[0]
tw = top_winners.head(12).iloc[::-1]
labels = [f"{p[:28]}… ({d[:12]})" if len(p)>28 else f"{p} ({d[:12]})" for d,p in tw.index]
ax.barh(labels, tw["yoy_%"], color="#2ca02c")
ax.set_title("Top project price winners (YoY % growth)")
ax.set_xlabel("YoY %")

# Layout vs ticket bubble
ax = axes2[1]
lay = recent[recent["asset"]=="residential"].groupby("layout").agg(
    deals=("price","size"), median_price=("price","median"), median_rate=("rate_sqm","median"),
).sort_values("deals", ascending=False).head(10)
ax.scatter(lay["median_price"]/1e6, lay["median_rate"],
           s=lay["deals"]/lay["deals"].max()*800, alpha=0.7, c="#1f77b4", edgecolors="black")
for l in lay.index:
    ax.annotate(l, (lay.loc[l,"median_price"]/1e6, lay.loc[l,"median_rate"]), fontsize=8)
ax.set_xlabel("Median ticket (AED M)")
ax.set_ylabel("Median rate AED/SQM")
ax.set_title("Layout economics — bubble = transaction count")

plt.tight_layout()
plt.savefig(OUT/"abu_dhabi_winners.png", bbox_inches="tight")
print(f"Saved winners → {OUT/'abu_dhabi_winners.png'}")
