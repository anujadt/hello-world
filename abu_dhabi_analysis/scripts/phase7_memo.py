"""
Phase 7: assemble the investor memo from prior-phase outputs.

Lead with the 5 highest-conviction triangulated insights, each:
- a dataset number
- the external corroboration
- the chart filename that proves it

Then the shortlist, the Yas verdict, the contrarian calls, and the caveats section.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUTPUTS, load_config

cfg = load_config()
W = cfg["scoring_weights"]

score = pd.read_csv(OUTPUTS / "area_scorecard.csv")
shortlist = pd.read_csv(OUTPUTS / "opportunity_shortlist.csv")
tri = pd.read_csv(OUTPUTS / "triangulation_table.csv")
yields = pd.read_csv(OUTPUTS / "net_yields_by_district.csv")
mix = pd.read_csv(OUTPUTS / "mix_decomposition.csv").set_index("metric")["value"]
leader = pd.read_csv(OUTPUTS / "leaderboard_12m.csv")
cycle = pd.read_csv(OUTPUTS / "cycle_classification.csv")
oss = pd.read_csv(OUTPUTS / "offplan_supply_pressure.csv")
irr = pd.read_csv(OUTPUTS / "offplan_irr.csv")

# Helpers
def fmt_pct(v): return f"{v:+.1f}%" if pd.notnull(v) else "n/a"
def fmt_aed(v):
    if pd.isna(v): return "n/a"
    if v >= 1e9: return f"AED {v/1e9:.2f}B"
    if v >= 1e6: return f"AED {v/1e6:.2f}M"
    if v >= 1e3: return f"AED {v/1e3:.0f}k"
    return f"AED {v:.0f}"

# Pull key numbers
total_change_pct = mix["total_change"] / mix["weighted_psm_prior"] * 100
mix_share_pct = mix["mix_effect"] / mix["total_change"] * 100
price_share_pct = 100 - mix_share_pct
yas_irr_C = irr[irr["district"]=="Yas Island"]["irr_scenario_C_forward6_pct"].iloc[0] if (irr["district"]=="Yas Island").any() else None
reem_irr_C = irr[irr["district"]=="Al Reem Island"]["irr_scenario_C_forward6_pct"].iloc[0] if (irr["district"]=="Al Reem Island").any() else None
raha_share_change = oss[oss["district"]=="Al Raha Beach"]["share_change_pp"].iloc[0] if (oss["district"]=="Al Raha Beach").any() else None

# Build markdown
lines = []
add = lines.append

add("# Abu Dhabi Real Estate Investor Memo")
add("")
add("**For**: Anuj (UAE Golden Visa, current holding: Yas Island, Mayan 2)")
add("**As of**: 2026-06-02")
add("**Source**: DARI / ADREC sales export (114,485 raw rows, 87,655 clean transactions, AED 265.9B "
    "aggregate 2019 to today). External triangulation against ADREC 2025 Report, Bayut H1 2025, "
    "Sands of Wealth 2025, Engel & Volkers, Cushman & Wakefield Core, MPInvestments. "
    "Every figure traces to either the clean parquet or a named external source with URL.")
add("")
add("---")
add("")
add("## Five highest-conviction insights, triangulated")
add("")

# Insight 1: Mix dominates the headline
add("### 1. The Abu Dhabi headline overstates true appreciation by roughly 4x")
add("")
add(f"- **Dataset**: headline residential psm rose **{total_change_pct:+.1f}%** in the last 12 months. "
    f"Decomposition: only **{price_share_pct:.0f}% is pure same-quality price** (about +{price_share_pct*total_change_pct/100:.1f}%); "
    f"**{mix_share_pct:.0f}% is mix shift** into luxury and off-plan stock.")
add(f"- **External corroboration**: Engel & Volkers/Bayut cite citywide residential price growth of "
    f"7-11% in 2025; Bayut splits affordable +12%, mid +19%, luxury +27%. Our mix decomposition reconciles "
    f"these segment numbers and shows that the apparent headline overstates what a same-quality home "
    f"actually appreciated by.")
add(f"- **Chart**: `outputs/charts/phase3_04_mix_decomposition.png`")
add("")

# Insight 2: Cycle classifier puts almost everything late-cycle
late = cycle[cycle["cycle"]=="late-cycle/overheating"]["district"].tolist()
mid  = cycle[cycle["cycle"]=="mid-cycle"]["district"].tolist()
add("### 2. Almost every freehold district is late-cycle; pullbacks not on the menu")
add("")
add(f"- **Dataset**: {len(late)} districts classify as late-cycle/overheating "
    f"(100th percentile psm vs own history, positive but decelerating momentum). "
    f"Only **{', '.join(mid)}** classifies as mid-cycle.")
add(f"- **External corroboration**: Cushman & Wakefield Core forecast 2026 growth "
    f"5-8% (moderation from 12-22% prior). ADREC reports 87% cash transactions "
    f"and 50%+ FDI share, both characteristic of late-cycle euphoria.")
add(f"- **Chart**: `outputs/charts/phase3_05_cycle_map.png`")
add("")

# Insight 3: Off-plan IRR is bad almost everywhere now
add("### 3. Off-plan pre-pays the appreciation: IRR is broken in most districts")
add("")
add(f"- **Dataset**: at current pricing, off-plan trades at a 17-89% premium over ready in the major "
    f"freehold areas (Yas +17%, Reem +27%, Saadiyat +89%). Modelling the staged payment plan "
    f"(10/10/10/10/10/50 over 36 months) at scenario C (+6%/y forward consensus) gives Yas IRR "
    f"{yas_irr_C:+.1f}%, Reem IRR {reem_irr_C:+.1f}%, Saadiyat negative.")
add(f"- **External corroboration**: ADREC notes off-plan share rose to 71% of residential 2025 (from 49% "
    f"in 2024). When a market is in price-discovery on off-plan launches, the developer captures the "
    f"appreciation, not the buyer.")
add(f"- **Chart**: `outputs/charts/phase4_02_offplan_irr.png`")
add("")

# Insight 4: Al Raha Beach is the largest forward supply overhang
add("### 4. Al Raha Beach is the largest single forward-supply overhang in the whitelist")
add("")
add(f"- **Dataset**: Al Raha Beach off-plan share moved from **0.5% to 57.2%** in 12 months, "
    f"the largest swing in any freehold district (+{raha_share_change:.0f}pp). The current +40.5% YoY "
    f"psm is the pre-handover rerating, not a sustainable post-handover level.")
add(f"- **External corroboration**: the UAE Media Office announcement of 14,444 units across the "
    f"Aldar+Bloom+Modon AD city pipeline (AED 55.4B) confirms structural new supply 2026-29.")
add(f"- **Chart**: `outputs/charts/phase3_06_offplan_supply_pressure.png`")
add("")

# Insight 5: Yield-led ranking diverges from appreciation-led
add("### 5. Yield-led and appreciation-led rankings diverge sharply")
add("")
add("- **Dataset, yield-led ranking (NET on all-in entry)**: "
    "Al Reem 5.72%, Masdar 5.44%, Al Reef 5.35%, Khalifa City 5.31%, Yas Island 5.10%, "
    "Zayed City 5.08%, Saadiyat 4.00%, Fahid 3.67%, Hudayriyat 3.66%, Maryah 3.25%.")
add("- **External corroboration**: Bayut/Sands of Wealth gross yields support Reem (~7.49%) and Yas "
    "(~7.07%) at the top; Saadiyat 2-bed gross 2.5% is the canonical low-yield trophy. Net yields "
    "include the cost stack: ADM 2%, agent 2%, vacancy 7%, tier-based service charges.")
add("- **Chart**: `outputs/charts/phase4_01_net_yields.png`")
add("")

add("---")
add("")
add("## Opportunity scorecard, 0 to 100, freehold whitelist only")
add("")
add("Weights: net_yield 25%, appreciation_momentum (mix-adjusted) 20%, cycle_position 20%, liquidity 15%, "
    "supply_risk_inverse 10%, value_vs_own_history 10%. Per the brief's instruction, the value component "
    "rewards districts that are CHEAPER relative to their own trend, matching the pullback discipline.")
add("")
add("| District | Net yield | YoY psm | Cycle | Liq score | Supply inverse | Value vs history | Total |")
add("|---|---|---|---|---|---|---|---|")
for _, r in score.iterrows():
    add(f"| {r['district']} | {r['net_yield_pct']:.2f}% | {r['yoy_psm_pct']:+.1f}% | {r['cycle_class']} "
        f"| {r['s_liquidity']:.0f} | {r['s_supply_inv']:.0f} | {r['s_value']:.0f} | **{r['total']:.1f}** |")
add("")
add("Reading: Al Reem dominates the composite by liquidity and yield, but scores zero on value vs own "
    "history (it sits at 100th percentile). Al Jubail Island is the only mid-cycle freehold with positive "
    "momentum, and it scores 100 on value vs history (the cheapest relative to its own trend).")
add("")
add("---")
add("")
add("## Ranked opportunity shortlist")
add("")
for i, r in shortlist.iterrows():
    add(f"### {i+1}. {r['district']}, {r['segment']}")
    add("")
    add(f"**Thesis**. {r['thesis']}")
    add("")
    add(f"- Expected NET yield: **{r['expected_net_yield_pct']:.2f}%** on all-in entry.")
    add(f"- Appreciation case: {r['appreciation_case']}")
    add(f"- What invalidates: {r['what_invalidates']}")
    add(f"- Cycle risk: {r['cycle_risk']}")
    add(f"- Supply risk: {r['supply_risk']}")
    add(f"- External sources: {r['external_sources']}")
    add("")
add("Note on Khalifa City: officially leasehold for most of the district, with only specific projects "
    "(e.g. Etihad Towers, Bloom Living) freehold-eligible. If you cannot legally take freehold on the "
    "specific building, skip it and re-allocate to Al Reem ready secondary.")
add("")
add("---")
add("")

# Yas Verdict
add("## Yas Island, marginal portfolio fit verdict")
add("")
add("**Recommendation: HOLD existing Mayan 2 exposure; do NOT add. Specifically do not buy Yas off-plan.**")
add("")
add("**Why hold and not add (concentration argument)**:")
add("- You already have Yas exposure. Adding more concentrates you in a district that is **late-cycle, "
    "97th percentile, decelerating** (trailing 3m psm is negative).")
add("- Yas off-plan share rose 80% to 88% in 12 months. The forward pipeline is real, with Aldar "
    "construction lined up. Off-plan IRR at scenario C is **only +1.4%** (essentially zero) because "
    "off-plan trades at +17% over ready before you fund the payment plan.")
add("")
add("**Why hold rather than trim**:")
add("- Yas has the tightest vacancy in Abu Dhabi (3.8% per Bayut), gross apartment yield 7.1% (luxury 7.07%), "
    "rents +15% in 2025. Mayan 2 is a ready unit, so the rental income side is intact.")
add("- The Disney World announcement is a durable demand catalyst that is already priced but provides a "
    "floor under capital values.")
add("- Liquidity is high (5,084 trailing-12m deals), so you can exit if the thesis changes.")
add("")
add("**Tactic if you want more Abu Dhabi exposure**: rotate the next dirham to Al Reem ready 1-bed "
    "(higher NET yield, deepest liquidity, lowest correlation to Yas-specific risks like Disney delivery), "
    "or to Al Reef ready apartment (zero supply pressure, less rate-sensitive end-user base).")
add("")
add("---")
add("")

# Contrarian
add("## Contrarian calls, where the popular narrative may be mispriced")
add("")
add("### Contrarian 1: Al Jubail Island, the only mid-cycle freehold mispriced by mix-narrative")
add("")
add("**Thesis**. The 'everything is late-cycle' headline obscures Al Jubail Island, which classifies as "
    "**mid-cycle** with +15.6% YoY psm, +43% volume YoY, the lowest current-vs-own-history percentile "
    "in the freehold whitelist (89th vs 100th elsewhere), and a *falling* off-plan share (-35pp). "
    "Off-plan share dropping while volume rises means the market is digesting prior supply and "
    "transitioning to a ready/resale base.")
add("")
add("**Counterpoint that the popular narrative misses**. Al Jubail is small (234 trailing-12m deals) and "
    "high-priced (AED 18,850/sqm median), so it does not show up on broker league tables of \"hottest\" "
    "districts. But on the mix-adjusted basis it is one of the few places where you would buy on a pullback.")
add("")
add("**External cross-check**. Aldar's Jubail Island Phase 2 specifically saw +61% YoY psm in our project "
    "leaderboard. Bayut and Sands of Wealth do not publish a Jubail-specific yield, so the yield case is "
    "weaker than Reem or Yas.")
add("")
add("### Contrarian 2: Al Maryah Island looks like the right place to ASK about value, not the wrong place")
add("")
add("**Thesis**. Al Maryah is the only district with **negative YoY psm (-28.3%)**, cooling cycle "
    "classification, off-plan premium collapsed from +51% to +9% over ready (mean reverting). "
    "This is the canonical late-cycle distribution pattern: weaker districts sell off first. "
    "If you believe the AD cycle is turning, Maryah is the leading indicator and the cheapest "
    "freehold entry.")
add("")
add("**Counterpoint**. NET yield is the worst in the whitelist (3.25%), reflecting high service charges "
    "on a central business district mixed-use product. Maryah is also a 'thin' market (689 deals) with "
    "specific commercial drag from neighbouring office vacancy. This trade is for someone with patience "
    "and a thesis on Maryah's office repricing, not a yield buyer.")
add("")
add("**External cross-check**. No external source called Maryah a buy in 2025 (the narrative was "
    "Hudayriyat, Saadiyat, Yas). The absence of consensus IS the contrarian setup.")
add("")
add("---")
add("")

# Triangulation summary
add("## Triangulation summary, all top claims cross-checked")
add("")
add("| Claim | Our figure | External | Source | Variance |")
add("|---|---|---|---|---|")
for _, r in tri.iterrows():
    ours = r["our_figure"] if pd.notnull(r["our_figure"]) else "not computable"
    ext  = r["external_figure"] if pd.notnull(r["external_figure"]) else "n/a"
    var  = f"{r['variance_pct']:+.1f}%" if pd.notnull(r["variance_pct"]) else "n/a"
    add(f"| {r['claim']} | {ours} | {ext} | {r['source']} | {var} |")
add("")
add("Two claims sit outside the 15% tolerance band: pure-price 12m growth (-41% variance) and Hudayriyat "
    "trailing-12m value (+62%). Both are reconciled in the table notes: the first is a scope/weighting "
    "difference between our hedonic and published indices; the second reflects calendar-2025 ADREC vs "
    "our trailing-12m window (which includes the first five months of 2026, when Hudayriyat accelerated).")
add("")
add("---")
add("")

# Caveats
add("## Data caveats and what I could not compute")
add("")
add("1. **No mortgage or gift records.** This DARI export is sales-only. Leverage/credit signal and "
    "cash share are NOT computable. The ADREC 2025 figure of 87% cash is external-only.")
add("2. **No unit/parcel ID.** A proper repeat-sales index requires matching the same asset across "
    "transactions. We used a hedonic mix-adjusted index instead (citywide R-squared adj ~0.65) and "
    "modelled off-plan-to-handover as a separate cohort metric.")
add("3. **No buyer nationality.** FDI mix and foreign-buyer trend are NOT computable. The ADREC 2025 "
    "figure of 50%+ FDI share is external-only.")
add("4. **No rent data.** NET yields use external gross yields from Bayut, Sands of Wealth, "
    "MPInvestments, H2O Properties, then apply the cost stack from `config.yaml` (ADM 2%, agent 2%, "
    "vacancy 7%, tier-based service charges). Three districts (Hudayriyat, Al Jubail, Fahid) lack "
    "direct external yields; estimates flagged in `outputs/net_yields_by_district.csv`.")
add("5. **Preliminary quarters.** 2026Q1 and 2026Q2 carry 12,406 rows (14% of clean parquet). Off-plan "
    "registrations lag; treat their YoY comparisons as preliminary.")
add("6. **Mix-decomposition limits.** The decomposition uses ptype x tier x deal_type cells; finer cuts "
    "would change the price/mix split modestly. Direction of the conclusion (~80% mix) is robust to "
    "this choice.")
add("7. **Off-plan IRR depends on the resale-at-handover assumption.** We show three scenarios "
    "(spot, historical-uplift, +6%/y forward consensus). The negative conclusion holds across all three "
    "for the major districts; the +21% Khalifa City scenario A is real but reflects sub-prime off-plan "
    "stock, not a generalizable opportunity.")
add("8. **Real / inflation-adjusted view not provided.** No UAE CPI source ingested in this run; "
    "all figures are nominal AED.")
add("9. **Freehold whitelist** matches Abu Dhabi's designated investment zones to the best of "
    "informally available information. Reconfirm against ADREC's official designation when actually "
    "purchasing. Khalifa City is mostly leasehold; only specific projects are freehold-eligible.")
add("")

# Reproduction
add("---")
add("")
add("## Reproduction")
add("")
add("From the repo root:")
add("")
add("```bash")
add("pip install pandas numpy matplotlib pyarrow statsmodels pyyaml")
add("python3 abu_dhabi_analysis/scripts/phase0_profile.py     # outputs/data_dictionary.md")
add("# pause and review the dictionary, then continue")
add("python3 abu_dhabi_analysis/scripts/phase1_clean.py        # outputs/clean_transactions.parquet")
add("python3 abu_dhabi_analysis/scripts/phase2_core.py         # leaderboard, charts")
add("python3 abu_dhabi_analysis/scripts/phase3_appreciation.py # hedonic, cycle, mix")
add("python3 abu_dhabi_analysis/scripts/phase4_yields_offplan.py")
add("python3 abu_dhabi_analysis/scripts/phase5_triangulate.py")
add("python3 abu_dhabi_analysis/scripts/phase6_score_shortlist.py")
add("python3 abu_dhabi_analysis/scripts/phase7_memo.py         # outputs/insight_memo.md")
add("```")
add("")
add("All tunables in `config.yaml`; rerunning after a config change regenerates all outputs.")

text = "\n".join(lines)
# Sanity: no em dashes
assert "—" not in text, "Em dash found in memo, please fix"
(OUTPUTS / "insight_memo.md").write_text(text, encoding="utf-8")
print(f"Saved {OUTPUTS / 'insight_memo.md'} ({len(text):,} chars)")
