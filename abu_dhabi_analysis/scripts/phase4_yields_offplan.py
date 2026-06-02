"""
Phase 4: NET rental yields with cost stack + off-plan IRR + forward overlay.

Net yield formula per district:
  gross_yield = external published figure (tier and ptype-specific where available)
  net_yield = gross_yield * (1 - vacancy)  -  (annual service charge / all-in entry price)
  all_in_entry = price * (1 + adm_transfer + agent_fee + optional mortgage_reg)

Off-plan IRR: time the staged payments against config milestones, assume resale at
secondary median psm in the handover quarter (or at last observed if no later data).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUTPUTS, CHARTS, PARQUET, EXTERNAL, load_config

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
COSTS = cfg["costs"]
TIER_SC = COSTS["service_charge_aed_per_sqft"]
TRIANG_TOL = cfg["triangulation"]["variance_tolerance_pct"]

df = pd.read_parquet(PARQUET)
res = df[df["cut"] == "residential"].copy()

today = res["date"].max()
t12 = today - pd.DateOffset(months=12)
res12 = res[res["date"] > t12]

# Load external yield benchmark
yld = pd.read_csv(EXTERNAL / "external_yield_benchmark.csv")

# ── 4.1 NET yields per district + tier ─────────────────────
print("=== 4.1 NET yields per district + tier ===")
def all_in_price_factor(leveraged: bool = False) -> float:
    f = 1 + COSTS["adm_transfer_fee_pct"] + COSTS["agent_fee_pct"]
    if leveraged:
        f += COSTS["mortgage_reg_fee_pct"]
    return f

def annual_service_charge_aed(psm: float, tier: str, sqm_median: float) -> float:
    """Service charge AED/sqft per tier converted to total AED for a median-sized unit."""
    sqft = sqm_median * 10.764
    return TIER_SC[tier] * sqft

records = []
gross_lookup = {}
for _, row in yld.iterrows():
    key = (row["district"], row["asset_kind"])
    gross_lookup[key] = (float(row["gross_yield_pct"]), row["source"])

# Apply to each district x tier we have prices for
for district in res12["district"].dropna().unique():
    g = res12[(res12["district"] == district) & (res12["ptype"] == "apartment")]
    if len(g) < 30:
        continue
    median_psm = g["rate_sqm"].median()
    median_sqm = g["sqm"].median()
    median_price = g["price"].median()
    all_in = median_price * all_in_price_factor(leveraged=False)
    sc_annual = annual_service_charge_aed(median_psm, g["tier"].mode().iloc[0] if not g["tier"].mode().empty else "midtier", median_sqm)

    # Pick a gross yield. Prefer district+apartment, else asset_kind=apartment, else fall back to citywide 6.5%
    gross_pct, src = gross_lookup.get((district, "apartment"), (None, None))
    if gross_pct is None:
        gross_pct, src = gross_lookup.get((district, "apartment_midtier"), (None, None))
    if gross_pct is None:
        gross_pct = 6.5
        src = "Citywide apartment mid-range (Bayut 2025 generic)"

    annual_gross_rent = (gross_pct/100) * median_price  # gross yield is on PURCHASE price by convention
    after_vacancy = annual_gross_rent * (1 - COSTS["vacancy_rate_pct"])
    net_annual = after_vacancy - sc_annual
    net_yield_on_allin = net_annual / all_in * 100

    records.append({
        "district": district,
        "median_price_aed": round(median_price, 0),
        "median_psm_aed": round(median_psm, 0),
        "median_sqm": round(median_sqm, 1),
        "all_in_price_aed": round(all_in, 0),
        "gross_yield_pct": gross_pct,
        "gross_source": src,
        "annual_service_charge_aed": round(sc_annual, 0),
        "vacancy_pct": COSTS["vacancy_rate_pct"] * 100,
        "net_yield_pct_on_allin": round(net_yield_on_allin, 2),
        "deals_12m": len(g),
    })
ny = pd.DataFrame(records).sort_values("net_yield_pct_on_allin", ascending=False)
ny.to_csv(OUTPUTS / "net_yields_by_district.csv", index=False)
print(ny.to_string(index=False))

fig, ax = plt.subplots(figsize=(11, 6.5))
top = ny.head(12).iloc[::-1]
ax.barh(top["district"], top["net_yield_pct_on_allin"], color="#2ca02c")
for i, (d, gy, ny_v) in enumerate(zip(top["district"], top["gross_yield_pct"], top["net_yield_pct_on_allin"])):
    ax.text(ny_v + 0.05, i, f"gross {gy:.1f}% / net {ny_v:.1f}%", va="center", fontsize=8)
ax.set_xlabel("NET yield (%) on all-in entry price")
plt.title("Net yields after service charges, vacancy, and transaction stack: Reem and Yas lead")
plt.tight_layout(); plt.savefig(CHARTS / "phase4_01_net_yields.png", bbox_inches="tight"); plt.close()

# ── 4.2 Cross-check broker yields vs DARI-implied yield ───
# Not applicable directly (no rent data in DARI), but we can note variance vs external
# in the triangulation table.

# ── 4.3 Off-plan IRR model ─────────────────────────────────
print("\n=== 4.3 Off-plan payment-plan IRR ===")
plan_pct = cfg["offplan_irr"]["payment_plan_default"]
plan_m   = cfg["offplan_irr"]["milestone_months"]
assert sum(plan_pct) == 100, "Payment plan must sum to 100"

def irr_monthly(cashflows):
    """Bisection IRR on monthly periods, robust against the overflow that Newton hit."""
    def npv(r):
        return sum(c / (1+r)**i for i, c in enumerate(cashflows))
    lo, hi = -0.05, 0.20  # monthly bounds, -60%/+790% annual ish
    if npv(lo) * npv(hi) > 0:
        return float("nan")
    for _ in range(200):
        mid = (lo + hi) / 2
        v = npv(mid)
        if abs(v) < 1e-6:
            return mid
        if v * npv(lo) < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2

# Load historical off-plan-to-handover uplift to anchor a realistic forward exit
oth_path = OUTPUTS / "offplan_to_handover.csv"
hist_uplift = {}
if oth_path.exists():
    oth_df = pd.read_csv(oth_path)
    hist_uplift = oth_df.groupby("district")["uplift_pct"].median().to_dict()

# Forward appreciation assumption from Cushman 2026 consensus (cited).
FORWARD_ANNUAL_PCT = 6.0  # external consensus midpoint; flagged in memo

irr_rows = []
for district in res12["district"].dropna().unique():
    g = res[res["district"] == district]
    g_now_off = g[(g["deal_type"] == "off-plan") & (g["ptype"] == "apartment") & (g["date"] > t12)]
    g_now_rdy = g[(g["deal_type"] == "ready") & (g["ptype"] == "apartment") & (g["date"] > t12)]
    if len(g_now_off) < 30 or len(g_now_rdy) < 30:
        continue
    p_off = g_now_off["rate_sqm"].median()
    p_rdy_spot = g_now_rdy["rate_sqm"].median()

    # Three exit scenarios at handover (max(plan_m) months out, default 36):
    years_out = max(plan_m) / 12.0
    # A: exit at today's ready psm (no time appreciation, conservative)
    exit_A = p_rdy_spot
    # B: exit at historical uplift-implied ready psm (off-plan launch psm * (1+median historical uplift))
    median_uplift = hist_uplift.get(district)
    exit_B = p_off * (1 + median_uplift/100) if median_uplift is not None else None
    # C: exit at today's ready psm grown by external forward consensus rate
    exit_C = p_rdy_spot * (1 + FORWARD_ANNUAL_PCT/100) ** years_out

    def model_irr(exit_psm):
        if exit_psm is None: return float("nan")
        flows = [0.0] * (max(plan_m) + 1)
        for pct, m in zip(plan_pct, plan_m):
            flows[m] = -pct
        flows[max(plan_m)] += exit_psm / p_off * 100
        m = irr_monthly(flows)
        if np.isnan(m): return float("nan")
        return ((1 + m) ** 12 - 1) * 100

    irr_rows.append({
        "district": district,
        "off_plan_psm_now": round(p_off, 0),
        "ready_psm_now":    round(p_rdy_spot, 0),
        "median_historical_uplift_pct": round(median_uplift, 1) if median_uplift is not None else None,
        "irr_scenario_A_spot": round(model_irr(exit_A), 1),
        "irr_scenario_B_historical_uplift": round(model_irr(exit_B), 1) if exit_B is not None else None,
        "irr_scenario_C_forward6_pct": round(model_irr(exit_C), 1),
        "deals_off_12m": len(g_now_off),
        "deals_rdy_12m": len(g_now_rdy),
    })

irr = pd.DataFrame(irr_rows).sort_values("irr_scenario_C_forward6_pct", ascending=False)
irr.to_csv(OUTPUTS / "offplan_irr.csv", index=False)
print(irr.to_string(index=False))

# Chart: scenario C (forward consensus) vs scenario A (spot)
fig, ax = plt.subplots(figsize=(11, 5.5))
top = irr.head(12).iloc[::-1]
y = np.arange(len(top))
ax.barh(y - 0.2, top["irr_scenario_C_forward6_pct"], height=0.4, color="#2ca02c", label="C: forward +6%/y appreciation")
ax.barh(y + 0.2, top["irr_scenario_A_spot"], height=0.4, color="#ff7f0e", label="A: spot exit (no appreciation)")
ax.set_yticks(y); ax.set_yticklabels(top["district"])
ax.axvline(0, color="black", linewidth=0.5)
ax.set_xlabel("Modeled annual IRR (%) on off-plan staged payment plan")
ax.legend(loc="lower right")
plt.title("Off-plan IRR: even at +6%/y forward appreciation, only a handful of districts beat 8%")
plt.tight_layout(); plt.savefig(CHARTS / "phase4_02_offplan_irr.png", bbox_inches="tight"); plt.close()

# ── 4.4 Off-plan vs ready price gap trend by district ─────
print("\n=== 4.4 Off-plan vs ready price gap by district (apartments only, last 24m) ===")
t24 = today - pd.DateOffset(months=24)
apt = res[(res["ptype"] == "apartment") & (res["date"] > t24)].copy()
apt["window"] = np.where(apt["date"] > t12, "last_12m", "prior_12m")

gap = (
    apt.groupby(["district","window","deal_type"])["rate_sqm"]
    .median().unstack("deal_type").reset_index()
)
gap = gap.dropna(subset=["off-plan","ready"])
gap["premium_pct"] = (gap["off-plan"]/gap["ready"] - 1) * 100
gap_pivot = gap.pivot(index="district", columns="window", values="premium_pct")
gap_pivot = gap_pivot.dropna()
gap_pivot["delta_pp"] = gap_pivot["last_12m"] - gap_pivot["prior_12m"]
gap_pivot = gap_pivot.sort_values("last_12m", ascending=False)
gap_pivot.to_csv(OUTPUTS / "offplan_vs_ready_premium_trend.csv")
print(gap_pivot.round(1).to_string())

# ── 4.5 Off-plan resale liquidity ─────────────────────────
print("\n=== 4.5 Off-plan secondary-market resale activity ===")
# For each district, secondary-market off-plan rows (deal_type=off-plan AND market=secondary)
# indicate flipping liquidity.
sec_off = res12[(res12["deal_type"] == "off-plan") & (res12["market"] == "secondary")]
sec_share = sec_off.groupby("district").size().rename("offplan_secondary_deals_12m")
all_off = res12[res12["deal_type"] == "off-plan"].groupby("district").size().rename("offplan_total_deals_12m")
liq = pd.concat([sec_share, all_off], axis=1).fillna(0)
liq["resell_share_pct"] = (liq["offplan_secondary_deals_12m"] / liq["offplan_total_deals_12m"].replace(0, np.nan) * 100).round(1)
liq = liq.sort_values("offplan_total_deals_12m", ascending=False).head(15)
liq.to_csv(OUTPUTS / "offplan_resale_liquidity.csv")
print(liq.to_string())

# ── 4.6 Forward overlay (external) ─────────────────────────
print("\n=== 4.6 Forward overlay, summary ===")
pipeline = pd.read_csv(EXTERNAL / "external_pipeline.csv")
print(pipeline.to_string(index=False))

print("\nPhase 4 complete. CSVs and charts saved.")
