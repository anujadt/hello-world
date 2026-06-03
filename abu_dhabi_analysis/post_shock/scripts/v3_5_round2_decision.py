"""
Round 2 decision-quality improvements.

- Drill: per shortlist cell, top 5 specific projects with deal count, psm range,
  ticket range, sqm range. Bridges the gap between segment-level findings and
  actionable broker-call list.
- Mayan 2 zoom: pull every transaction in Mayan 2 (Anuj's existing Yas Island
  studio holding), compute psm trajectory, compare to Yas-wide. Asks whether
  his own asset is in or insulated from the Yas off-plan dump.
- Rerun yields at 12% vacancy (the ValuStrat-implied actual occupancy) and
  IRR with mortgage rate 6.25% (2026 UAE market vs my stale 5.25%). Honest
  numbers replace the optimistic ones.
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
COSTS = CFG["costs"]

PIVOT = pd.Timestamp("2026-02-27")
LAG_PIVOT = PIVOT + pd.Timedelta(days=45)
POST_END = pd.Timestamp("2026-06-02")

df = pd.read_parquet(PARQUET)
df["date"] = pd.to_datetime(df["date"])
res = df[df["cut"] == "residential"].copy()
post_lag = res[(res["date"] >= LAG_PIVOT) & (res["date"] <= POST_END)]

# ─── 1. Drill the shortlist to specific projects ──────────────────
print("=" * 75)
print("DRILL: per shortlist cell, top 5 projects with broker-actionable detail")
print("=" * 75)

shortlist = pd.read_csv(V3 / "post_shock_shortlist_v3.csv")
drill_rows = []
for _, s in shortlist.iterrows():
    cell = post_lag[
        (post_lag["district"] == s["district"])
        & (post_lag["ptype"] == s["ptype"])
        & (post_lag["layout"] == s["layout"])
        & (post_lag["deal_type"] == "ready")
    ]
    if len(cell) == 0:
        continue
    by_proj = cell.groupby("project").agg(
        n=("price", "size"),
        median_psm=("rate_sqm", "median"),
        psm_p10=("rate_sqm", lambda x: x.quantile(0.1)),
        psm_p90=("rate_sqm", lambda x: x.quantile(0.9)),
        median_ticket=("price", "median"),
        ticket_min=("price", "min"),
        ticket_max=("price", "max"),
        median_sqm=("sqm", "median"),
        last_print=("date", "max"),
    ).reset_index().sort_values("n", ascending=False).head(8)
    for _, p in by_proj.iterrows():
        drill_rows.append({
            "shortlist_cell": f"{s['district']} {s['layout']}",
            "district": s["district"],
            "layout": s["layout"],
            "project": p["project"],
            "n_post_event": int(p["n"]),
            "median_psm": round(p["median_psm"], 0),
            "psm_p10": round(p["psm_p10"], 0),
            "psm_p90": round(p["psm_p90"], 0),
            "median_ticket": round(p["median_ticket"], 0),
            "ticket_min": round(p["ticket_min"], 0),
            "ticket_max": round(p["ticket_max"], 0),
            "median_sqm": round(p["median_sqm"], 1),
            "last_print": p["last_print"].date().isoformat(),
        })
drill = pd.DataFrame(drill_rows)
drill.to_csv(OUT / "shortlist_project_drill.csv", index=False)
for cell, sub in drill.groupby("shortlist_cell"):
    print(f"\n── {cell} (top {len(sub)} projects by deal count post-Apr-13) ──")
    print(sub[["project", "n_post_event", "median_psm", "psm_p10", "psm_p90",
               "median_ticket", "median_sqm", "last_print"]].to_string(index=False))
print()

# ─── 2. Mayan 2 zoom ─────────────────────────────────────────────
print("=" * 75)
print("MAYAN 2 ZOOM: Anuj's existing Yas Island position")
print("=" * 75)

# Try several plausible project name variants
mayan_mask = res["project"].str.contains("Mayan", case=False, na=False)
mayan = res[mayan_mask].copy()
print(f"Transactions matching 'Mayan' in project name: {len(mayan)}")
print(mayan["project"].value_counts().head(10).to_string())
print()

# Mayan 2 specifically
m2_mask = res["project"].str.contains(r"Mayan\s*2|Mayan-2|Mayan 2", case=False, na=False, regex=True)
m2 = res[m2_mask].copy()
print(f"Transactions matching 'Mayan 2': {len(m2)}")
if len(m2) > 0:
    m2["year"] = m2["date"].dt.year
    m2["quarter"] = m2["date"].dt.to_period("Q").astype(str)
    print("\nMayan 2 transaction summary by year:")
    summary = m2.groupby("year").agg(
        n=("price", "size"),
        median_psm=("rate_sqm", "median"),
        median_price=("price", "median"),
        median_sqm=("sqm", "median"),
    ).round(0)
    print(summary.to_string())
    print()
    print("Mayan 2 transaction summary by quarter, last 8 quarters:")
    q_summary = m2.groupby("quarter").agg(
        n=("price", "size"),
        median_psm=("rate_sqm", "median"),
    ).round(0).tail(8)
    print(q_summary.to_string())
    print()

    # Compare to Yas-wide same ptype, same layout (studio if Mayan 2 is studios)
    layout_mix = m2["layout"].value_counts()
    print(f"Mayan 2 layout mix: {layout_mix.to_dict()}")
    dominant_layout = m2["layout"].mode().iloc[0] if not m2["layout"].mode().empty else None
    if dominant_layout:
        yas_comp = res[
            (res["district"] == "Yas Island")
            & (res["layout"] == dominant_layout)
            & (res["deal_type"] == "ready")
        ].copy()
        yas_comp["year"] = yas_comp["date"].dt.year
        comp = yas_comp.groupby("year").agg(
            yas_n=("price", "size"),
            yas_median_psm=("rate_sqm", "median"),
        ).round(0)
        joint = summary.merge(comp, left_index=True, right_index=True, how="left").reset_index()
        joint["mayan2_premium_pct"] = ((joint["median_psm"] / joint["yas_median_psm"]) - 1) * 100
        joint = joint.round(1)
        joint.to_csv(OUT / "mayan2_zoom.csv", index=False)
        print(f"\nMayan 2 vs Yas Island {dominant_layout} ready, by year:")
        print(joint.to_string(index=False))
    m2.to_csv(OUT / "mayan2_transactions.csv", index=False)
else:
    print("No 'Mayan 2' specifically; will use all Mayan matches as proxy.")
print()

# ─── 3. Rerun yields at 12% vacancy + IRR at 6.25% mortgage ──────
print("=" * 75)
print("HONEST YIELDS: 12% vacancy (ValuStrat-implied), 6.25% mortgage (2026)")
print("=" * 75)

yields = pd.read_csv(V3 / "yield_overlay_v3.csv")
NEW_VACANCY = 0.12
ADM = COSTS["adm_transfer_fee_pct"]
AGENT_BUY = COSTS["agent_fee_pct"]
NEW_MORTGAGE_RATE = 0.0625

# We need annual_gross_rent_adj and service_charge_aed; not exported separately so
# reconstruct from price * adjusted_gross_yield_pct
yields["annual_gross_rent_adj_implied"] = yields["adjusted_gross_yield_pct"] / 100 * yields["price_med"]
yields["net_rent_at_12pct_vac"] = (
    yields["annual_gross_rent_adj_implied"] * (1 - NEW_VACANCY) - yields["service_charge_aed"]
)
yields["net_yield_honest_pct"] = (yields["net_rent_at_12pct_vac"] / yields["all_in_entry"] * 100).round(2)
yields["delta_from_optimistic_pp"] = (yields["net_yield_honest_pct"] - yields["net_yield_adj_pct"]).round(2)

honest = yields[[
    "district", "ptype", "layout", "tier", "n_post_ready", "psm_post_ready",
    "price_med", "all_in_entry", "net_yield_adj_pct", "net_yield_honest_pct",
    "delta_from_optimistic_pp"
]].sort_values("net_yield_honest_pct", ascending=False)
honest.to_csv(OUT / "yields_honest.csv", index=False)
print(honest.head(15).to_string(index=False))
print()

# Honest IRR for the shortlist
def amort_payment(p, r, t_y):
    if p <= 0: return 0.0
    r_m = r / 12
    n = t_y * 12
    return (p * r_m / (1 - (1 + r_m) ** -n)) * 12

def loan_balance(p, r, t_y, years):
    if p <= 0: return 0.0
    r_m = r / 12
    n = t_y * 12
    k = years * 12
    m = p * r_m / (1 - (1 + r_m) ** -n)
    return max(p * (1 + r_m) ** k - m * ((1 + r_m) ** k - 1) / r_m, 0.0)

def irr_bisect(cf):
    def npv(rate):
        return sum(c / (1 + rate) ** i for i, c in enumerate(cf))
    lo, hi = -0.95, 5.0
    if npv(lo) * npv(hi) > 0: return float("nan")
    for _ in range(200):
        mid = (lo + hi) / 2
        v = npv(mid)
        if abs(v) < 1e-6: return mid
        if v * npv(lo) < 0: hi = mid
        else: lo = mid
    return (lo + hi) / 2

irr_rows = []
shortlist = pd.read_csv(V3 / "post_shock_shortlist_v3.csv")
for _, s in shortlist.iterrows():
    y_row = honest[
        (honest["district"] == s["district"])
        & (honest["ptype"] == s["ptype"])
        & (honest["layout"] == s["layout"])
    ]
    if len(y_row) == 0: continue
    y = y_row.iloc[0]
    price = float(y["price_med"])
    net_rent0 = float(y["net_yield_honest_pct"]) / 100 * float(y["all_in_entry"])
    for ltv in [0.0, 0.5, 0.7]:
        for h in [3, 5, 7]:
            for scen, (pg, rg) in [("bear", (0.0, 0.0)), ("base", (0.06, 0.03)), ("bull", (0.10, 0.05))]:
                all_in = price * (1 + ADM + AGENT_BUY)
                loan = ltv * price
                equity_in = all_in - loan + loan * COSTS["mortgage_reg_fee_pct"]
                ds = amort_payment(loan, NEW_MORTGAGE_RATE, 25)
                flows = [-equity_in]
                for yr in range(1, h + 1):
                    noi = net_rent0 * (1 + rg) ** (yr - 1)
                    cf = noi - ds
                    if yr == h:
                        sale = price * (1 + pg) ** h
                        net_sale = sale * 0.98
                        cf += net_sale - loan_balance(loan, NEW_MORTGAGE_RATE, 25, h)
                    flows.append(cf)
                a = irr_bisect(flows)
                irr_rows.append({
                    "district": s["district"], "layout": s["layout"],
                    "scenario": scen, "ltv_pct": int(ltv * 100), "horizon_y": h,
                    "irr_honest_pct": round(a * 100, 1) if not np.isnan(a) else None,
                })
irr_honest = pd.DataFrame(irr_rows)
irr_honest.to_csv(OUT / "irr_honest_matrix.csv", index=False)

# Compare honest vs original for the lead pick
old_irr = pd.read_csv(V3 / "irr_lead_full_matrix.csv")
lead_old = old_irr.copy()
lead_old["district"] = "Al Reem Island"
lead_old["layout"] = "2 beds"
honest_lead = irr_honest[(irr_honest["district"] == "Al Reem Island") & (irr_honest["layout"] == "2 beds")]
compare = lead_old.merge(
    honest_lead.rename(columns={"irr_honest_pct": "irr_honest_pct"}),
    on=["scenario", "ltv_pct", "horizon_y", "district", "layout"], how="inner",
    suffixes=("_v3", "_honest"),
)
compare["delta_pp"] = (compare["irr_honest_pct"] - compare["irr_pct"]).round(1)
compare = compare[["scenario", "ltv_pct", "horizon_y", "irr_pct", "irr_honest_pct", "delta_pp"]]
compare.to_csv(OUT / "irr_lead_compare.csv", index=False)
print("Lead pick (Al Reem 2-bed): v3 IRR vs honest (12% vac, 6.25% mortgage):")
print(compare.to_string(index=False))
print()

print(f"Outputs in {OUT}")
