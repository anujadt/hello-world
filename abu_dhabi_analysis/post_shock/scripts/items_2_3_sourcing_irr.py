"""
Items 2 and 3: off-market sourcing briefs + levered IRR on the shortlist.

Item 2: for each cohort-dump project (high post-event secondary share), pull the
        post-event (lag-adjusted) transaction detail a broker needs: layout mix,
        sqm range, price range, psm range, primary vs secondary split, recent prints.

Item 3: levered IRR for each shortlist cell across cash / LTV-50 / LTV-70,
        3 / 5 / 7 year horizons, and bear / base / bull price-recovery paths.
        Full 3x3x3 matrix for the lead pick (Al Reem 2-bed).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import yaml

ROOT = Path("/home/user/hello-world/abu_dhabi_analysis")
PARQUET = ROOT / "outputs" / "clean_transactions.parquet"
V3 = ROOT / "post_shock" / "outputs" / "v3"
OUT = V3  # write alongside the other v3 outputs
with open(ROOT / "config.yaml") as f:
    CFG = yaml.safe_load(f)
COSTS = CFG["costs"]

PIVOT = pd.Timestamp("2026-02-27")
LAG_PIVOT = PIVOT + pd.Timedelta(days=45)
POST_END = pd.Timestamp("2026-06-02")

df = pd.read_parquet(PARQUET)
res = df[df["cut"] == "residential"].copy()
res["date"] = pd.to_datetime(res["date"])
post_lag = res[(res["date"] >= LAG_PIVOT) & (res["date"] <= POST_END)]

# ─────────────────────────────────────────────────────────────
# ITEM 2: off-market sourcing briefs
# ─────────────────────────────────────────────────────────────
print("=" * 70)
print("ITEM 2: off-market sourcing briefs (cohort-dump projects)")
print("=" * 70)

cohort = pd.read_csv(V3 / "cohort_dump.csv")
target_projects = cohort[cohort["secondary_share_pct"] >= 75]["project"].tolist()

briefs = []
for proj in target_projects:
    g = post_lag[post_lag["project"] == proj]
    if len(g) == 0:
        continue
    sec = g[g["market"] == "secondary"]
    layouts = g["layout"].value_counts().to_dict()
    layout_str = ", ".join(f"{k}:{v}" for k, v in layouts.items())
    briefs.append({
        "district": g["district"].mode().iloc[0],
        "project": proj,
        "post_event_deals": len(g),
        "secondary_deals": len(sec),
        "secondary_share_pct": round(len(sec) / len(g) * 100, 0),
        "layout_mix": layout_str,
        "median_psm": round(g["rate_sqm"].median(), 0),
        "psm_p10": round(g["rate_sqm"].quantile(0.1), 0),
        "psm_p90": round(g["rate_sqm"].quantile(0.9), 0),
        "median_price": round(g["price"].median(), 0),
        "price_min": round(g["price"].min(), 0),
        "price_max": round(g["price"].max(), 0),
        "median_sqm": round(g["sqm"].median(), 0),
        "last_print_date": g["date"].max().date().isoformat(),
    })

briefs_df = pd.DataFrame(briefs).sort_values("post_event_deals", ascending=False)
briefs_df.to_csv(OUT / "sourcing_briefs.csv", index=False)
print(briefs_df.head(25).to_string(index=False))
print()

# ─────────────────────────────────────────────────────────────
# ITEM 3: levered IRR on the shortlist
# ─────────────────────────────────────────────────────────────
print("=" * 70)
print("ITEM 3: levered IRR scenarios")
print("=" * 70)

yields = pd.read_csv(V3 / "yield_overlay_v3.csv")
shortlist = pd.read_csv(V3 / "post_shock_shortlist_v3.csv")

# Financing + cost assumptions (stated, all overridable)
MORTGAGE_RATE = 0.0525     # UAE resident mortgage ~5.25%
MORTGAGE_TERM_Y = 25
MORTGAGE_REG_FEE = COSTS["mortgage_reg_fee_pct"]  # 0.25% of loan
ADM = COSTS["adm_transfer_fee_pct"]               # 2%
AGENT_BUY = COSTS["agent_fee_pct"]                # 2%
AGENT_SELL = 0.02                                  # 2% on exit

# Scenarios: (price growth %/yr, rent growth %/yr)
SCENARIOS = {
    "bear":  (0.00, 0.00),
    "base":  (0.06, 0.03),   # Cushman consensus price; conservative rent
    "bull":  (0.10, 0.05),
}
LTVS = [0.0, 0.5, 0.7]
HORIZONS = [3, 5, 7]


def amort_payment(principal: float, rate: float, term_y: int) -> float:
    """Annual amortizing payment (12 monthly payments summed)."""
    if principal <= 0:
        return 0.0
    r = rate / 12
    n = term_y * 12
    m = principal * r / (1 - (1 + r) ** -n)
    return m * 12


def loan_balance(principal: float, rate: float, term_y: int, years_elapsed: int) -> float:
    if principal <= 0:
        return 0.0
    r = rate / 12
    n = term_y * 12
    k = years_elapsed * 12
    m = principal * r / (1 - (1 + r) ** -n)
    # remaining balance after k payments
    bal = principal * (1 + r) ** k - m * ((1 + r) ** k - 1) / r
    return max(bal, 0.0)


def irr(cashflows: list[float]) -> float:
    """Annual IRR via bisection. cashflows[0] is t0 (negative equity)."""
    def npv(rate: float) -> float:
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))
    lo, hi = -0.95, 5.0
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


def compute_irr(price: float, net_rent0: float, ltv: float, horizon: int,
                price_g: float, rent_g: float) -> dict:
    all_in_cost = price * (1 + ADM + AGENT_BUY)
    loan = ltv * price
    reg_fee = loan * MORTGAGE_REG_FEE
    equity_in = all_in_cost - loan + reg_fee
    debt_service = amort_payment(loan, MORTGAGE_RATE, MORTGAGE_TERM_Y)

    flows = [-equity_in]
    for yr in range(1, horizon + 1):
        noi = net_rent0 * (1 + rent_g) ** (yr - 1)
        levered_cf = noi - debt_service
        if yr == horizon:
            sale_price = price * (1 + price_g) ** horizon
            net_sale = sale_price * (1 - AGENT_SELL)
            bal = loan_balance(loan, MORTGAGE_RATE, MORTGAGE_TERM_Y, horizon)
            terminal = net_sale - bal
            levered_cf += terminal
        flows.append(levered_cf)
    annual_irr = irr(flows)
    # equity multiple
    total_in = -flows[0]
    total_out = sum(flows[1:])
    em = (total_out + 0) / total_in if total_in else float("nan")
    return {"irr_pct": round(annual_irr * 100, 1) if not np.isnan(annual_irr) else None,
            "equity_in": round(equity_in, 0),
            "equity_multiple": round(em, 2)}


# Build the cell list from the shortlist, pulling net_rent from yields
cells = []
for _, s in shortlist.iterrows():
    y = yields[(yields["district"] == s["district"]) & (yields["ptype"] == s["ptype"]) & (yields["layout"] == s["layout"])]
    if len(y) == 0:
        continue
    yrow = y.iloc[0]
    price = float(yrow["price_med"])
    all_in = float(yrow["all_in_entry"])
    net_rent0 = float(yrow["net_yield_adj_pct"]) / 100 * all_in
    cells.append({
        "district": s["district"], "ptype": s["ptype"], "layout": s["layout"],
        "price": price, "net_rent0": net_rent0,
    })

# Base-case (base scenario) summary across LTV x horizon for every shortlist cell
rows = []
for c in cells:
    for ltv in LTVS:
        for h in HORIZONS:
            pg, rg = SCENARIOS["base"]
            r = compute_irr(c["price"], c["net_rent0"], ltv, h, pg, rg)
            rows.append({
                "district": c["district"], "layout": c["layout"],
                "scenario": "base", "ltv_pct": int(ltv * 100), "horizon_y": h,
                **r,
            })
base_matrix = pd.DataFrame(rows)
base_matrix.to_csv(OUT / "irr_base_matrix.csv", index=False)
print("\nBase-case levered IRR (price +6%/yr, rent +3%/yr), all shortlist cells:")
print(base_matrix.to_string(index=False))

# Full 3x3x3 for the lead pick (Al Reem 2-bed)
lead = next((c for c in cells if c["district"] == "Al Reem Island" and c["layout"] == "2 beds"), cells[0])
full_rows = []
for scen, (pg, rg) in SCENARIOS.items():
    for ltv in LTVS:
        for h in HORIZONS:
            r = compute_irr(lead["price"], lead["net_rent0"], ltv, h, pg, rg)
            full_rows.append({
                "scenario": scen, "ltv_pct": int(ltv * 100), "horizon_y": h, **r,
            })
full_df = pd.DataFrame(full_rows)
full_df.to_csv(OUT / "irr_lead_full_matrix.csv", index=False)
print(f"\nFull 3x3x3 IRR matrix for lead pick: Al Reem 2-bed (entry AED {lead['price']/1e6:.2f}M, "
      f"net rent AED {lead['net_rent0']/1e3:.0f}k/yr):")
print(full_df.to_string(index=False))
print()
print("Item 2 + 3 complete. Saved sourcing_briefs.csv, irr_base_matrix.csv, irr_lead_full_matrix.csv")
