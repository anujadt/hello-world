"""
Studios decision-oriented analysis. Replaces the YoY-blended studio page with:
- Citywide same-month-across-years matrix (count, median psm, p25/p75 dispersion)
- Trend-extrapolated seasonal normal per month and 2026 deviation from it
- Jan-May YTD aggregate (same-window every year) per hub
- D1 (buy at all?), D2 (where?), D3 (when?), D4 (sell Mayan?) decision blocks
- Hub-level net yield at honest assumptions (12% vacancy, 6.25% mortgage)
- Project drill for top hubs

Scope: ready studios (deal_type == ready, layout == studio, residential),
6 freehold studio hubs (Reem, Yas, Maryah, Saadiyat, Masdar, Khalifa).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT = Path("/home/user/hello-world/abu_dhabi_analysis")
PARQUET = ROOT / "outputs" / "clean_transactions.parquet"
OUT = ROOT / "post_shock" / "outputs" / "studio_v2"
OUT.mkdir(parents=True, exist_ok=True)
RENT_BENCH = ROOT / "external" / "rent_benchmark_by_layout.csv"

with open(ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)
COSTS = CFG["costs"]

HUBS = [
    "Al Reem Island", "Yas Island", "Al Maryah Island",
    "Al Saadiyat Island", "Masdar City", "Khalifa City",
]
PIVOT = pd.Timestamp("2026-02-27")

df = pd.read_parquet(PARQUET)
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month

# Ready studios only, residential
sR = df[(df.cut == "residential") & (df.layout == "studio") & (df.deal_type == "ready")].copy()
# All studios (any deal type) for forward-supply
sAll = df[(df.cut == "residential") & (df.layout == "studio")].copy()

print(f"Ready studios total: {len(sR):,};  All studios: {len(sAll):,}")
print()

# ─── 1. Citywide same-month x year matrix ───────────────────────────
print("=" * 78)
print("1. Citywide month x year matrix (ready studios)")
print("=" * 78)

sR23 = sR[sR.year >= 2023]
mat_count = sR23.pivot_table(index="month", columns="year", values="price", aggfunc="size", fill_value=0)
mat_psm = sR23.pivot_table(index="month", columns="year", values="rate_sqm", aggfunc="median")
mat_p25 = sR23.pivot_table(index="month", columns="year", values="rate_sqm", aggfunc=lambda x: x.quantile(0.25))
mat_p75 = sR23.pivot_table(index="month", columns="year", values="rate_sqm", aggfunc=lambda x: x.quantile(0.75))

# Trend-extrapolated seasonal normal: for each month, linear fit on
# 2023/2024/2025 -> project 2026.
def project_2026(series_by_year: pd.Series) -> float:
    pts = series_by_year.dropna()
    if len(pts) < 2:
        return float("nan")
    years = pts.index.astype(int).values
    vals = pts.values.astype(float)
    slope, intercept = np.polyfit(years, vals, 1)
    return float(slope * 2026 + intercept)

months = list(range(1, 6))  # Jan-May, where 2026 is complete
city_rows = []
for m in months:
    n_act = int(mat_count.loc[m, 2026]) if 2026 in mat_count.columns else 0
    psm_act = mat_psm.loc[m, 2026] if (2026 in mat_psm.columns and not pd.isna(mat_psm.loc[m, 2026])) else float("nan")
    n_proj = project_2026(mat_count.loc[m, [2023, 2024, 2025]])
    psm_proj = project_2026(mat_psm.loc[m, [2023, 2024, 2025]])
    city_rows.append({
        "month": m,
        "count_2023": int(mat_count.loc[m, 2023]),
        "count_2024": int(mat_count.loc[m, 2024]),
        "count_2025": int(mat_count.loc[m, 2025]),
        "count_2026_actual": n_act,
        "count_2026_seasonal_trend": round(n_proj, 0),
        "count_deviation_pct": round((n_act / n_proj - 1) * 100, 1) if n_proj > 0 else float("nan"),
        "psm_2023": round(mat_psm.loc[m, 2023], 0) if not pd.isna(mat_psm.loc[m, 2023]) else None,
        "psm_2024": round(mat_psm.loc[m, 2024], 0) if not pd.isna(mat_psm.loc[m, 2024]) else None,
        "psm_2025": round(mat_psm.loc[m, 2025], 0) if not pd.isna(mat_psm.loc[m, 2025]) else None,
        "psm_2026_actual": round(psm_act, 0) if not pd.isna(psm_act) else None,
        "psm_2026_seasonal_trend": round(psm_proj, 0) if not pd.isna(psm_proj) else None,
        "psm_deviation_pct": round((psm_act / psm_proj - 1) * 100, 1) if not pd.isna(psm_act) and not pd.isna(psm_proj) and psm_proj > 0 else None,
        "p25_2026": round(mat_p25.loc[m, 2026], 0) if (2026 in mat_p25.columns and not pd.isna(mat_p25.loc[m, 2026])) else None,
        "p75_2026": round(mat_p75.loc[m, 2026], 0) if (2026 in mat_p75.columns and not pd.isna(mat_p75.loc[m, 2026])) else None,
    })
city = pd.DataFrame(city_rows)
city.to_csv(OUT / "citywide_month_matrix.csv", index=False)
print(city.to_string(index=False))
print()

# Jan-May YTD same-window aggregate, all years
print("=" * 78)
print("Jan-May YTD aggregate (same window every year), citywide ready studios")
print("=" * 78)
ytd_rows = []
for y in [2023, 2024, 2025, 2026]:
    sub = sR23[(sR23.year == y) & (sR23.month.isin(months))]
    ytd_rows.append({
        "year": y,
        "n": len(sub),
        "monthly_avg_n": round(len(sub) / 5, 1),
        "median_psm": int(round(sub["rate_sqm"].median(), 0)) if len(sub) else None,
        "p25_psm": int(round(sub["rate_sqm"].quantile(0.25), 0)) if len(sub) else None,
        "p75_psm": int(round(sub["rate_sqm"].quantile(0.75), 0)) if len(sub) else None,
        "dispersion_pp": int(round(sub["rate_sqm"].quantile(0.75) - sub["rate_sqm"].quantile(0.25), 0)) if len(sub) else None,
        "median_ticket": int(round(sub["price"].median(), 0)) if len(sub) else None,
    })
ytd = pd.DataFrame(ytd_rows)
ytd.to_csv(OUT / "citywide_jan_may_ytd.csv", index=False)
print(ytd.to_string(index=False))
print()

# Within-studio composition trajectory (off-plan vs ready, primary vs secondary)
print("=" * 78)
print("Within-studio composition by year (forward-supply read)")
print("=" * 78)
sStud = sAll[sAll.year >= 2023].copy()
comp_rows = []
for y in [2023, 2024, 2025, 2026]:
    sub = sStud[(sStud.year == y) & (sStud.month.isin(months))]
    n = len(sub)
    if n == 0:
        comp_rows.append({"year": y, "n": 0})
        continue
    comp_rows.append({
        "year": y, "n": n,
        "ready_pct": round((sub.deal_type == "ready").mean() * 100, 1),
        "offplan_pct": round((sub.deal_type == "off-plan").mean() * 100, 1),
        "primary_pct": round((sub.market == "primary").mean() * 100, 1),
        "secondary_pct": round((sub.market == "secondary").mean() * 100, 1),
    })
comp = pd.DataFrame(comp_rows)
comp.to_csv(OUT / "citywide_composition.csv", index=False)
print(comp.to_string(index=False))
print()

# ─── 2. Per-hub Jan-May YTD ──────────────────────────────────────
print("=" * 78)
print("2. Per-hub Jan-May YTD (same window every year), READY studios")
print("=" * 78)

hub_year_rows = []
for h in HUBS:
    for y in [2023, 2024, 2025, 2026]:
        sub = sR23[(sR23.district == h) & (sR23.year == y) & (sR23.month.isin(months))]
        hub_year_rows.append({
            "district": h, "year": y, "n": len(sub),
            "monthly_avg": round(len(sub) / 5, 1),
            "median_psm": int(round(sub["rate_sqm"].median(), 0)) if len(sub) else None,
            "median_ticket": int(round(sub["price"].median(), 0)) if len(sub) else None,
            "p25_psm": int(round(sub["rate_sqm"].quantile(0.25), 0)) if len(sub) >= 3 else None,
            "p75_psm": int(round(sub["rate_sqm"].quantile(0.75), 0)) if len(sub) >= 3 else None,
            "median_sqm": round(sub["sqm"].median(), 0) if len(sub) else None,
        })
hub_year = pd.DataFrame(hub_year_rows)
hub_year.to_csv(OUT / "hub_jan_may_ytd.csv", index=False)
print(hub_year.to_string(index=False))
print()

# Forward supply overhang per hub (off-plan studio sales in last 12m)
twelve_ago = sR23.date.max() - pd.DateOffset(months=12)  # use sR23.date.max safely:
twelve_ago = pd.Timestamp("2026-06-02") - pd.DateOffset(months=12)
overhang_rows = []
sStud_all = df[(df.cut == "residential") & (df.layout == "studio")].copy()
for h in HUBS:
    op12 = sStud_all[(sStud_all.district == h) & (sStud_all.deal_type == "off-plan")
                     & (sStud_all.date > twelve_ago)]
    ready12 = sR[(sR.district == h) & (sR.date > twelve_ago)]
    overhang_rows.append({
        "district": h,
        "offplan_studio_sales_12m": len(op12),
        "ready_studio_sales_12m": len(ready12),
        "supply_overhang_ratio": round(len(op12) / max(len(ready12), 1), 2),
    })
overhang = pd.DataFrame(overhang_rows).sort_values("supply_overhang_ratio", ascending=False)
overhang.to_csv(OUT / "hub_supply_overhang.csv", index=False)
print("Forward studio supply overhang per hub (off-plan studio sales 12m / ready studio sales 12m):")
print(overhang.to_string(index=False))
print()

# Per-hub net yield (honest: 12% vac, 6.25% mortgage)
print("=" * 78)
print("Per-hub honest net yield (12% vacancy, tier service charge, all-in entry)")
print("=" * 78)
rent = pd.read_csv(RENT_BENCH)
rent_studio = rent[rent.layout == "studio"].copy()
RENT_GROWTH = {"Yas Island": 15, "Al Saadiyat Island": 14, "Al Reem Island": 11,
               "Al Maryah Island": 8, "Masdar City": 11, "Khalifa City": 11}

ADM = COSTS["adm_transfer_fee_pct"]
AGENT = COSTS["agent_fee_pct"]
VAC = 0.12  # honest
SC_PER_SQFT = COSTS["service_charge_aed_per_sqft"]

yield_rows = []
last12 = sR23[(sR23.date > twelve_ago)]
for h in HUBS:
    sub = last12[last12.district == h]
    if len(sub) < 3:
        yield_rows.append({"district": h, "n_last12m": len(sub)})
        continue
    psm = sub["rate_sqm"].median()
    sqm = sub["sqm"].median()
    price = sub["price"].median()
    all_in = price * (1 + ADM + AGENT)
    rrow = rent_studio[rent_studio.district == h]
    gross_yield_pct = float(rrow["gross_yield_pct"].iloc[0]) if len(rrow) else 6.5
    growth = RENT_GROWTH.get(h, 11)
    adj_gross = gross_yield_pct * (1 + growth / 100)
    tier = "affordable" if psm <= 15000 else "midtier" if psm <= 22000 else "luxury"
    sc = SC_PER_SQFT[tier] * (sqm * 10.764)
    annual_rent = adj_gross / 100 * price
    net = annual_rent * (1 - VAC) - sc
    net_yield = net / all_in * 100
    yield_rows.append({
        "district": h, "n_last12m": len(sub),
        "median_psm": int(round(psm, 0)),
        "median_ticket": int(round(price, 0)),
        "median_sqm": round(sqm, 1),
        "all_in_entry": int(round(all_in, 0)),
        "gross_yield_pct_adjusted": round(adj_gross, 2),
        "service_charge_aed": int(round(sc, 0)),
        "net_yield_pct": round(net_yield, 2),
        "tier": tier,
    })
yields = pd.DataFrame(yield_rows).sort_values("net_yield_pct", ascending=False, na_position="last")
yields.to_csv(OUT / "hub_yields.csv", index=False)
print(yields.to_string(index=False))
print()

# ─── 3. Project drill per hub (top studios projects, post-event) ─
print("=" * 78)
print("3. Top READY studio projects per hub (post-Apr-13, lag-adjusted)")
print("=" * 78)
LAG_PIVOT = PIVOT + pd.Timedelta(days=45)
POST_END = pd.Timestamp("2026-06-02")
proj_rows = []
for h in HUBS:
    sub = sR[(sR.district == h) & (sR.date >= LAG_PIVOT) & (sR.date <= POST_END)]
    if len(sub) == 0:
        continue
    by_p = sub.groupby("project").agg(
        n=("price", "size"),
        median_psm=("rate_sqm", "median"),
        psm_p10=("rate_sqm", lambda x: x.quantile(0.1)),
        psm_p90=("rate_sqm", lambda x: x.quantile(0.9)),
        median_ticket=("price", "median"),
        ticket_min=("price", "min"),
        ticket_max=("price", "max"),
        median_sqm=("sqm", "median"),
        last_print=("date", "max"),
    ).reset_index().sort_values("n", ascending=False).head(5)
    for _, p in by_p.iterrows():
        proj_rows.append({
            "district": h,
            "project": p["project"],
            "n": int(p["n"]),
            "median_psm": int(round(p["median_psm"], 0)),
            "psm_p10": int(round(p["psm_p10"], 0)),
            "psm_p90": int(round(p["psm_p90"], 0)),
            "median_ticket": int(round(p["median_ticket"], 0)),
            "ticket_min": int(round(p["ticket_min"], 0)),
            "ticket_max": int(round(p["ticket_max"], 0)),
            "median_sqm": round(p["median_sqm"], 1),
            "last_print": p["last_print"].date().isoformat(),
        })
projs = pd.DataFrame(proj_rows)
projs.to_csv(OUT / "hub_top_projects.csv", index=False)
print(projs.to_string(index=False))
print()

# ─── 4. Mayan studio deep dive (D4) ────────────────────────────
print("=" * 78)
print("4. Mayan studio analysis (D4: sell or hold)")
print("=" * 78)
mayan = df[df["project"].fillna("").str.match("^Mayan$", case=False) & (df.layout == "studio")].copy()
mayan_ready = mayan[mayan.deal_type == "ready"].copy()
print(f"Mayan studio rows (all): {len(mayan)}; ready only: {len(mayan_ready)}")

mayan_year = mayan_ready.groupby("year").agg(
    n=("price", "size"),
    median_psm=("rate_sqm", "median"),
    median_price=("price", "median"),
    median_sqm=("sqm", "median"),
).round(0).reset_index()

yas_ready_studio = sR[sR.district == "Yas Island"].copy()
yas_year = yas_ready_studio.groupby("year").agg(yas_n=("price","size"), yas_psm=("rate_sqm","median")).round(0).reset_index()
joint = mayan_year.merge(yas_year, on="year", how="left")
joint["mayan_premium_pct"] = ((joint["median_psm"] / joint["yas_psm"]) - 1) * 100
joint = joint.round(1)
joint.to_csv(OUT / "mayan_vs_yas_studio.csv", index=False)
print(joint.to_string(index=False))
print()

# Mayan recent ready-studio trades
mayan_recent = mayan_ready.sort_values("date", ascending=False).head(30)[
    ["date", "sqm", "price", "rate_sqm", "market"]
].copy()
mayan_recent["date"] = mayan_recent["date"].dt.date.astype(str)
mayan_recent.to_csv(OUT / "mayan_recent_trades.csv", index=False)
print("Last 10 Mayan ready-studio trades:")
print(mayan_recent.head(10).to_string(index=False))
print()

# ─── 5. Decision verdicts ───────────────────────────────────────
print("=" * 78)
print("5. Decision verdicts")
print("=" * 78)

# D1: Buy a studio at all? Synthesis using the headline data
city_dev_psm = city["psm_deviation_pct"].dropna()
city_dev_count = city["count_deviation_pct"].dropna()
may_dev = city[city.month == 5].iloc[0] if len(city[city.month == 5]) else None
top_yield_hub = yields.iloc[0] if len(yields) and not pd.isna(yields["net_yield_pct"].iloc[0]) else None

# D2: Where? composite of net yield, velocity (avg monthly count 2026 vs prior),
# supply risk (inverse overhang), price-vs-trend (lower = better entry)
d2_rows = []
for h in HUBS:
    hy = yields[yields.district == h]
    ny = float(hy["net_yield_pct"].iloc[0]) if len(hy) and "net_yield_pct" in hy.columns and not pd.isna(hy["net_yield_pct"].iloc[0]) else None
    h26 = hub_year[(hub_year.district == h) & (hub_year.year == 2026)]
    h25 = hub_year[(hub_year.district == h) & (hub_year.year == 2025)]
    vel26 = float(h26["monthly_avg"].iloc[0]) if len(h26) else 0
    vel25 = float(h25["monthly_avg"].iloc[0]) if len(h25) else 0
    vel_ratio = vel26 / vel25 if vel25 > 0 else float("nan")
    ohr = overhang[overhang.district == h]
    ohv = float(ohr["supply_overhang_ratio"].iloc[0]) if len(ohr) else 0
    d2_rows.append({
        "district": h,
        "net_yield_pct": ny,
        "monthly_velocity_2026": vel26,
        "velocity_vs_2025": round(vel_ratio, 2) if not pd.isna(vel_ratio) else None,
        "supply_overhang": ohv,
    })
d2 = pd.DataFrame(d2_rows)

# Composite score (higher better): yield (35%) + velocity_ratio (30%) + 1/(1+overhang) (20%) + 2026 absolute velocity (15%)
def mm(s, hi=True):
    x = s.astype(float)
    if x.dropna().nunique() <= 1:
        return pd.Series(50.0, index=x.index)
    lo, hh = x.min(), x.max()
    out = (x - lo) / (hh - lo) * 100
    return out if hi else 100 - out

d2["s_yield"] = mm(d2["net_yield_pct"], True)
d2["s_velocity_trend"] = mm(d2["velocity_vs_2025"].fillna(0), True)
d2["s_supply"] = mm(d2["supply_overhang"], False)
d2["s_absolute_volume"] = mm(d2["monthly_velocity_2026"], True)
d2["composite"] = (d2["s_yield"] * 0.35 + d2["s_velocity_trend"] * 0.30
                   + d2["s_supply"] * 0.20 + d2["s_absolute_volume"] * 0.15)
d2 = d2.sort_values("composite", ascending=False)
d2.to_csv(OUT / "d2_hub_scorecard.csv", index=False)
print("D2: hub scorecard (composite ranking, higher = better place to buy studio):")
print(d2.round(1).to_string(index=False))
print()

# D3: when? Deviation trajectory Jan-May
print("\nD3: deviation trajectory Jan-May 2026 (count and psm vs seasonal-trend normal):")
print(city[["month", "count_deviation_pct", "psm_deviation_pct"]].to_string(index=False))

# D4: Sell Mayan? Compare Mayan-ready-studio trajectory to Yas-wide and to best D2 alternative
print("\nD4: Mayan studio premium trajectory")
print(joint[["year", "n", "median_psm", "yas_psm", "mayan_premium_pct"]].to_string(index=False))

# Save a synthesized verdicts CSV
verdicts = [
    {"decision": "D1 buy a studio at all", "verdict": "Selective, not broad",
     "rationale": f"Citywide May 2026 count is {may_dev['count_deviation_pct'] if may_dev is not None else 'n/a'}% vs seasonal-trend normal; psm is {may_dev['psm_deviation_pct'] if may_dev is not None else 'n/a'}% above. Prices at all-time highs while volume signals demand caution; the trade is yield at a hub with supportive supply, not appreciation."},
    {"decision": "D2 where (top hub)", "verdict": d2.iloc[0]["district"] if len(d2) else "n/a",
     "rationale": f"Composite score {round(d2.iloc[0]['composite'],1) if len(d2) else 'n/a'}. Net yield {round(d2.iloc[0]['net_yield_pct'],2) if len(d2) and not pd.isna(d2.iloc[0]['net_yield_pct']) else 'n/a'}%, monthly velocity 2026 {d2.iloc[0]['monthly_velocity_2026'] if len(d2) else 'n/a'}, overhang {d2.iloc[0]['supply_overhang'] if len(d2) else 'n/a'}."},
    {"decision": "D3 when",
     "verdict": "Watch trajectory; enter only when May/June 2026 deviation stabilizes",
     "rationale": "Three post-war months is not enough to call a floor. Entry trigger: 2 consecutive months where citywide count deviation improves (less negative) AND your target hub's monthly velocity recovers above 4. Until then, source off-market only."},
    {"decision": "D4 sell Mayan studio",
     "verdict": "HOLD with conditions",
     "rationale": f"Mayan 2026 ready-studio median psm AED {int(joint.iloc[-1]['median_psm']) if len(joint) else 'n/a'} on n={int(joint.iloc[-1]['n']) if len(joint) else 'n/a'}; premium over Yas-wide {round(joint.iloc[-1]['mayan_premium_pct'],1) if len(joint) else 'n/a'}%. The mark is rich but exit liquidity is thin. Only sell if a specific buyer surfaces at p75+ pricing; otherwise hold for yield."}
]
pd.DataFrame(verdicts).to_csv(OUT / "verdicts.csv", index=False)
print("\nVerdicts saved to verdicts.csv")
print()

# Caveats
caveats = [
    "Three post-war months (Apr/May/Jun-partial 2026) cannot support a forecast. The forward read is direction, not magnitude.",
    "Per-district monthly counts are single-digit thin. The page uses Jan-May YTD per hub and citywide month matrix for citywide texture.",
    "Net yields use external Bayut/MPInvestments/Sands of Wealth gross yields adjusted +11-15% for rent growth since H1 2025, then a 12% vacancy and tier service charges (AED 12/18/28 per sqft) per the v3.5 honest assumptions.",
    "Mayan deep dive uses all-Mayan rows (DARI registers phases as one project).",
    "Seasonal-trend normal is a linear extrapolation of 2023-2025 same-month values. Robust to seasonality, fragile to structural breaks in the 2023-2025 trend.",
]
pd.DataFrame({"caveat": caveats}).to_csv(OUT / "caveats.csv", index=False)
print(f"Outputs in {OUT}")
