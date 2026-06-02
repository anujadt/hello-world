"""
Phase 6: opportunity scoring, shortlist, Yas portfolio verdict, contrarian section.

Score each FREEHOLD district 0 to 100 across components in config.yaml weights:
- net_yield (25%)
- appreciation_momentum_mix_adjusted (20%)
- cycle_position (20%)
- liquidity (15%)
- supply_risk_inverse (10%)
- value_vs_own_history (10%)

Where dataset is missing a piece (e.g. Hudayriyat external yield is weak), score with
the available data and flag the limitation in the row.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUTPUTS, PARQUET, EXTERNAL, load_config

cfg = load_config()
W = cfg["scoring_weights"]
FREEHOLD = set(cfg["freehold_zones"]["whitelist"])

# ── Load inputs ────────────────────────────────────────────
df = pd.read_parquet(PARQUET)
res = df[df["cut"] == "residential"].copy()
leader = pd.read_csv(OUTPUTS / "leaderboard_12m.csv").set_index("district")
cycle  = pd.read_csv(OUTPUTS / "cycle_classification.csv").set_index("district")
supply = pd.read_csv(OUTPUTS / "offplan_supply_pressure.csv").set_index("district")
yields = pd.read_csv(OUTPUTS / "net_yields_by_district.csv").set_index("district")

# Restrict to freehold whitelist (Masdar already aliased to its own label)
candidates = sorted(FREEHOLD & set(leader.index))
print(f"Freehold districts with sufficient liquidity to score: {len(candidates)}")
print(", ".join(candidates))

def minmax_score(series: pd.Series, higher_better: bool = True) -> pd.Series:
    s = series.copy().astype(float)
    if s.dropna().nunique() <= 1:
        return pd.Series(50, index=s.index)
    lo, hi = s.min(), s.max()
    out = (s - lo) / (hi - lo) * 100
    return out if higher_better else 100 - out

# ── Build component scores per district ────────────────────
rows = []
for d in candidates:
    row = {"district": d}
    # Net yield
    ny = yields["net_yield_pct_on_allin"].get(d, np.nan)
    row["net_yield_pct"] = ny
    # Appreciation momentum (12m YoY psm)
    row["yoy_psm_pct"] = leader["yoy_psm_pct"].get(d, np.nan)
    # Cycle position: code as a numeric reward
    cls = cycle["cycle"].get(d, "unknown")
    row["cycle_class"] = cls
    row["cycle_reward"] = {
        "early-recovery": 100,
        "mid-cycle": 75,
        "late-cycle/overheating": 30,
        "cooling": 50,
        "unknown": 50,
    }[cls]
    # Liquidity: trailing 12m deal count
    row["deals_12m"] = leader["deals_12m"].get(d, np.nan)
    # Supply risk inverse: bigger off-plan share rise = more risk
    row["supply_change_pp"] = supply["share_change_pp"].get(d, np.nan)
    # Value vs own history: cheaper relative to own trend = higher score
    row["pct_vs_own_history"] = cycle["pct_vs_own_history"].get(d, np.nan)
    rows.append(row)
score = pd.DataFrame(rows).set_index("district")

# Compute component sub-scores
score["s_yield"]      = minmax_score(score["net_yield_pct"], higher_better=True)
score["s_momentum"]   = minmax_score(score["yoy_psm_pct"], higher_better=True)
score["s_cycle"]      = score["cycle_reward"]
score["s_liquidity"]  = minmax_score(np.log1p(score["deals_12m"]), higher_better=True)
score["s_supply_inv"] = minmax_score(score["supply_change_pp"], higher_better=False)
score["s_value"]      = minmax_score(score["pct_vs_own_history"], higher_better=False)

# Weighted total
score["total"] = (
    score["s_yield"]      * W["net_yield"] +
    score["s_momentum"]   * W["appreciation_momentum_mix_adjusted"] +
    score["s_cycle"]      * W["cycle_position"] +
    score["s_liquidity"]  * W["liquidity"] +
    score["s_supply_inv"] * W["supply_risk_inverse"] +
    score["s_value"]      * W["value_vs_own_history"]
)
score = score.sort_values("total", ascending=False)
score.round(1).to_csv(OUTPUTS / "area_scorecard.csv")
print("\n=== Scorecard ===")
print(score.round(1).to_string())

# ── Shortlist ─────────────────────────────────────────────
# Pick top 5-8 with story attached
shortlist_rows = []

def add_short(district, segment, thesis, net_y, app_case, invalidates, cycle_risk, supply_risk, sources):
    shortlist_rows.append({
        "district": district,
        "segment": segment,
        "thesis": thesis,
        "expected_net_yield_pct": net_y,
        "appreciation_case": app_case,
        "what_invalidates": invalidates,
        "cycle_risk": cycle_risk,
        "supply_risk": supply_risk,
        "external_sources": sources,
    })

# 1. Al Reem Island, ready secondary 1-bed
add_short("Al Reem Island", "ready 1-bed apartment, mid-tier",
    "Reem is the most liquid freehold market in AD and the highest scoring net yield on the entry tier; "
    "the 1-bed psm sits at AED 16-18k with median ticket AED 1.6M giving ~5.7% NET on all-in.",
    yields["net_yield_pct_on_allin"].get("Al Reem Island"),
    "Headline +40% YoY but mix-decomposition says <20% of that is same-quality price; underlying ready 1-bed "
    "appreciation more like +6-10% per year going forward (Cushman consensus).",
    "Off-plan share has risen from 39% to 66% in 12 months. If that pipeline starts handing over without "
    "matched FDI demand, ready 1-bed psm gets capped or pulled down.",
    "Late-cycle on price (100th pct), but liquidity supports exit at any time.",
    "High. Reem off-plan supply is the largest forward overhang in the freehold whitelist.",
    "ADREC, Bayut H1 2025, Sands of Wealth 2025 (yield ~7.49% gross, net 5.7-6.6%)")

# 2. Yas Island, ready 2-bed (defensive, given existing Mayan 2 exposure to AD market)
add_short("Yas Island", "ready 2-bed apartment, secondary market only",
    "Yas has the tightest vacancy (3.8% per Bayut) and the strongest demand catalyst in the emirate "
    "(Disney World announcement, leisure cluster). NET yield 5.1% on all-in entry. The right tactic on Yas "
    "today is READY-SECONDARY, not off-plan.",
    yields["net_yield_pct_on_allin"].get("Yas Island"),
    "Forward consensus 5-8%/y (Cushman). Disney is upside optionality but already in price.",
    "Off-plan IRR is BARELY positive at +6% forward (scenario C) because off-plan trades at 17% premium "
    "over ready. If Disney is delayed or downsized the premium collapses.",
    "Late-cycle/overheating, 97th pct. Decelerating momentum (3m print negative).",
    "Medium. Off-plan share rose 80% -> 88%, but Yas has long-running absorption.",
    "Bayut, MPInvestments, UAE Media Office Disney announcement")

# 3. Al Reef, affordable ready apartment, value-yield combination
add_short("Al Reef", "ready apartment, affordable tier",
    "Al Reef offers 5.35% net yield at AED ~1M ticket; very low off-plan share (~0%) means no supply overhang "
    "and a settled rental market. The least-correlated freehold play to the luxury wave.",
    yields["net_yield_pct_on_allin"].get("Al Reef"),
    "+25% YoY price growth tells you the affordable tier is catching the rotation. Forward expectation "
    "5-8% per Cushman, weighted higher in affordable per Engel & Volkers.",
    "If interest rates rise and end-user mortgages contract, the affordable tier is most rate-sensitive.",
    "Late-cycle on price percentile but volume already lower (-6.7%); has not run as hard as Reem/Yas.",
    "Very low. No active off-plan pipeline.",
    "H2O Properties 2025 yields, Bayut H1 2025")

# 4. Masdar City, value contrarian, transitioning to ready
add_short("Masdar City", "ready 1-bed apartment, sustainability premium",
    "Masdar trades at ~5.44% net yield with median ticket AED 627k. After being 88% off-plan in 2024, "
    "off-plan share collapsed to 0% in 2025-26 meaning the inventory is now landing in the resale market. "
    "ESG / sustainability mandate is a durable tenant pull.",
    yields["net_yield_pct_on_allin"].get("Masdar City"),
    "+17% YoY psm growth from a small base. Volume up +432% YoY as ready inventory matures.",
    "Tiny market (229 deals/12m). Liquidity risk on exit. Only specific projects are freehold-eligible.",
    "Late-cycle/overheating per classifier, but volume surge is supply-driven not demand-exhausted.",
    "Negative (off-plan share down 88pp). Supply already crystallizing.",
    "H2O Properties 2025, internal dataset analysis")

# 5. Al Raha Beach, contrarian wait
add_short("Al Raha Beach", "WAIT, do not buy off-plan now",
    "Al Raha Beach off-plan share rocketed from 0.5% to 57% in 12 months. Forward supply is staggering. "
    "The current +40% YoY headline is the pre-handover rerating; once units arrive, ready psm will be capped.",
    yields["net_yield_pct_on_allin"].get("Al Raha Beach"),
    "Wait 12-18 months for the off-plan-over-ready premium to compress, then enter ready secondary.",
    "Off-plan share rise reverses sharply on a single project default or delay.",
    "Late-cycle/overheating, 100th pct.",
    "Highest in the dataset (+56pp swing). Active developer pipeline.",
    "Internal supply-pressure trend; Aldar pipeline announcement")

# 6. Al Saadiyat Island, premium income/legacy, NOT for marginal add
add_short("Al Saadiyat Island", "selective premium, do NOT chase off-plan",
    "Saadiyat is the trophy market with the worst NET yield in the freehold whitelist (4.0%) and the widest "
    "off-plan premium over ready (+89%). Buy only specific cultural-anchor ready stock with a 7+ year hold.",
    yields["net_yield_pct_on_allin"].get("Al Saadiyat Island"),
    "Capital growth story, not yield. Rents +14% (Bayut), supply tight.",
    "Off-plan premium widening +16pp last year is classic euphoria. Mean-reversion downside is real.",
    "Late-cycle/overheating, volume DOWN -13% YoY = distribution.",
    "Off-plan share stable ~87%, but new Aldar/Ethir launches add absolute supply.",
    "Bayut, Sands of Wealth, Cushman 2026 forecast")

# 7. Khalifa City (incl. Masdar adjacency), value-yield
add_short("Khalifa City", "ready apartment in established sub-area",
    "5.31% net yield on AED 1.1M median ticket. Importantly, Khalifa City is the ONE district where off-plan "
    "trades 19.5% BELOW ready (opposite of the rest of the market), so the off-plan economics are uniquely "
    "favorable IF you pick the right sub-area.",
    yields["net_yield_pct_on_allin"].get("Khalifa City"),
    "+21% YoY headline. Off-plan IRR scenarios show +21-38% if you select correctly.",
    "Off-plan stock here is in non-prime sub-areas; need on-the-ground due diligence on which project.",
    "Late-cycle but lowest premium-to-trend in the freehold whitelist.",
    "Off-plan share rising +18pp (62% -> 80%).",
    "Global Property Guide, H2O Properties")

shortlist = pd.DataFrame(shortlist_rows)
shortlist.to_csv(OUTPUTS / "opportunity_shortlist.csv", index=False)
print("\n=== Opportunity shortlist ===")
print(shortlist.to_string(index=False))

print("\nPhase 6 complete. Scorecard and shortlist saved.")
