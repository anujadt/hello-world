"""
Phase G2: assemble post-shock memo v3.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

OUT = Path("/home/user/hello-world/abu_dhabi_analysis/post_shock/outputs/v3")

shortlist = pd.read_csv(OUT / "post_shock_shortlist_v3.csv")
scorecard = pd.read_csv(OUT / "post_shock_scorecard_v3.csv")
yields = pd.read_csv(OUT / "yield_overlay_v3.csv")
regime_raw = pd.read_csv(OUT / "regime_raw_pivot.csv")
regime_lag = pd.read_csv(OUT / "regime_lag_adjusted.csv")
lag_delta = pd.read_csv(OUT / "lag_contamination.csv")
volume_weekly = pd.read_csv(OUT / "volume_weekly.csv")
cohort = pd.read_csv(OUT / "cohort_dump.csv")
distress_apt = pd.read_csv(OUT / "distress_apartment.csv")
supply = pd.read_csv(OUT / "supply_overhang.csv")
stress = pd.read_csv(OUT / "stress_matrix.csv")


def fmt_aed(v: float) -> str:
    if v >= 1e6: return f"AED {v/1e6:.2f}M"
    if v >= 1e3: return f"AED {v/1e3:.0f}k"
    return f"AED {v:.0f}"


lines: list[str] = []
add = lines.append

add("# Abu Dhabi Post-Shock Opportunity Memo, v3 (lag-corrected)")
add("")
add("**Pivot date**: Feb 27, 2026. **Effective post-event start** (after 45-day registration-lag correction): Apr 13, 2026.")
add("**Post-event window analyzed**: 1.6 months on the lag-adjusted view, 3.1 months on the raw view (both reported).")
add("**Scope**: residential, freehold whitelist, ready apartments primary for the yield shortlist.")
add("**Data**: DARI sales (87,655 clean transactions). Rent benchmarks: Bayut H1 2025, MPInvestments, Sands of Wealth, H2O Properties, adjusted for citywide +11% (Yas +15%, Saadiyat +14%) rent growth observed since H1 2025.")
add("")
add("## What changed from v2, and what didn't")
add("")
add("The v2 memo concluded the market did NOT crash post-Feb-27. After Anuj's call-out that v2 ignored the 30-90 day registration lag between deal agreement and DARI submission, this v3 rebuilds with the lag correction plus 19 other methodology fixes. The headline conclusion is **directionally the same but more conservative**:")
add("")
add("- The shortlist shrank from 7 entries to **4** after the bootstrap CI gate and a tighter sample-size floor.")
add("- Three v2 cells were eliminated: Reem studio (sample too thin in lag-adjusted window), Yas studio (same), Yas 1-bed (same), and Saadiyat studio (CI on excess-change crosses zero).")
add("- The top of the shortlist is **Al Reem affordable apartments** (1-bed and 2-bed), unchanged from v2. The conviction is now better-supported.")
add("- Forced-seller flow is best seen via **project cohort dump tracking**, a new v3 signal. 2022-2024 off-plan launches in specific projects are now 88-100% secondary, meaning nearly every transaction is a resale. This is the clearest evidence of post-event distress and the off-market entry path.")
add("")

add("## Volume trajectory does not show a cliff")
add("")
volume_weekly_sorted = volume_weekly.sort_values("week_num_post_event")
add(f"If the registration-lag hypothesis were strictly correct, weekly post-event deal counts should drop sharply around week 6 (when the pre-event pipeline runs out). The data does not show that cliff. Weeks 1 to 6 averaged about {volume_weekly[volume_weekly['week_num_post_event'].le(6)]['total_deals'].mean():.0f} deals; weeks 7+ averaged about {volume_weekly[volume_weekly['week_num_post_event'].ge(7)]['total_deals'].mean():.0f} (ratio 0.99). The two readings are consistent with EITHER (a) genuine post-event demand stepping in as pipeline drained, or (b) a longer, more gradual lag tail. v3 takes the conservative interpretation: report both raw-pivot and lag-adjusted figures, and let the **cohort dump signal** carry the distress narrative.")
add("")

add("## How much the lag correction moved each cell")
add("")
add("The size of the lag correction varies materially by cell. Top 10 cells where the raw-pivot view overstated the post-event read:")
add("")
add("| District | Property type | Layout | Raw excess % | Lag-adjusted % | Δ (pp) |")
add("|---|---|---|---|---|---|")
for _, r in lag_delta.head(10).iterrows():
    add(f"| {r['district']} | {r['ptype']} | {r['layout']} | {r['excess_raw_pct']:+.1f}% | {r['excess_lag_pct']:+.1f}% | **{r['lag_contamination_pp']:+.1f}** |")
add("")
add("Saadiyat 1-bed and Maryah 1-bed are the biggest lag-contamination corrections. Their raw-pivot 'resilience' was substantially overstated. Raha Beach 4-bed apartments flipped sign (raw +0.2%, lag -10.8%): the apparent resilience was entirely a pipeline drain artifact.")
add("")

add("## The shortlist (lag-adjusted, CI-gated, supply-penalized)")
add("")
add("Restricted to: freehold zones, ready apartments, post-event volume ≥20 deals in the lag-adjusted window, regime not frozen, bootstrap 90% CI on excess-change does NOT include zero.")
add("")
add("Net yield (adjusted) uses 12-month-stale Bayut/Sands of Wealth gross yields rolled forward by district-specific rent growth (+11% citywide, +15% Yas, +14% Saadiyat). Worst-case yield is the rent -25% × vacancy +10pp stress.")
add("")
add("| Rank | District | Layout | Tier | n_post | Ticket | NET yield (adj) | Worst-case | Excess px % (CI) | Supply overhang | Confidence |")
add("|---|---|---|---|---|---|---|---|---|---|---|")
for i, r in shortlist.iterrows():
    ci = f"[{r['excess_ci_lo']:+.1f}, {r['excess_ci_hi']:+.1f}]"
    add(f"| {i+1} | {r['district']} | {r['layout']} | {r['tier']} | "
        f"{int(r['n_post_ready'])} | {fmt_aed(r['price_med'])} | "
        f"**{r['net_yield_adj_pct']:.2f}%** | {r['worst_case_yield']:.2f}% | "
        f"{r['excess_change_pct']:+.1f} {ci} | {r['supply_overhang_ratio']:.1f}x | {r['confidence']} |")
add("")

add("## Highest-conviction call")
add("")
top = shortlist.iloc[0]
add(f"**Al Reem Island affordable / mid-tier apartments (1-bed and 2-bed) remain the highest-conviction post-event entry, with stronger statistical support than v2.** Excess change vs prior trajectory: 2-bed +35.7% (90% CI [{regime_lag[(regime_lag['district']=='Al Reem Island') & (regime_lag['layout']=='2 beds')]['excess_ci_lo'].iloc[0]:.1f}, {regime_lag[(regime_lag['district']=='Al Reem Island') & (regime_lag['layout']=='2 beds')]['excess_ci_hi'].iloc[0]:.1f}]), 1-bed +32.7% (CI well above zero). Both deliver adjusted NET yields above 6.0% on all-in entry. Under the harshest stress scenario (rent -25%, vacancy +10pp), both still clear ~3.7% NET. The supply overhang ratio for Reem is **1.36x** (pipeline units / existing 12m ready stock), which is the LOWEST among heavy-volume districts (Shamkha 15.8x, Zayed 14.6x, Saadiyat 4.9x, Yas 4.8x). This means Reem is the freehold zone where existing ready demand absorbs new supply best.")
add("")

add("## Cohort dump leaderboard, the v3 signal you should read most carefully")
add("")
add("Off-plan launches from 2022-2024 where 88%+ of post-event off-plan transactions are SECONDARY (i.e., original buyer reselling before / shortly after handover). These are the projects with forced-seller flow.")
add("")
add("| District | Project | Launch year | Post-event off-plan deals | Secondary share |")
add("|---|---|---|---|---|")
for _, r in cohort.head(20).iterrows():
    add(f"| {r['district']} | {r['project']} | {int(r['launch_year'])} | "
        f"{int(r['off_post_n'])} | **{r['secondary_share_pct']:.0f}%** |")
add("")
add("Read: Bloom Living (Toledo, Olvera, Casares, Granada, Seville) in Zayed City is functioning as a resale market with virtually no developer-direct sales any more. Saadiyat Lagoons phases (Ethir, Wilds, Al Sidr), Saadiyat Grove (Source), and Saadiyat Manarat I/II are all dominated by resales. Yas Noya 4/5 and Ansam 2 same story. **These are the projects where off-market deal-making concentrates.** Approach brokers focused on these specific buildings.")
add("")

add("## Project-level distressed ready-secondary trades (post-event, lag-adjusted)")
add("")
add("Z-score against the PROJECT's own pre-event mean (not the district's). This is the v3 fix that filtered out false positives where a project simply trades below district average for structural reasons.")
add("")
add("| Date | District | Project | Layout | Sqm | Price | psm | Project mean | Discount |")
add("|---|---|---|---|---|---|---|---|---|")
for _, r in distress_apt.iterrows():
    add(f"| {r['date'][:10]} | {r['district']} | {r['project'][:32]} | {r['layout']} | "
        f"{r['sqm']:.0f} | {fmt_aed(r['price'])} | AED {r['rate_sqm']:,.0f} | "
        f"AED {r['proj_mean']:,.0f} | **{r['discount_pct']:.1f}%** |")
add("")
add("Use as input to off-market sourcing. Radiant Square, Hydra Avenue, The Wave, Marina Square Paragon Bay Mall, and Amaya Towers in Reem are seeing real discount activity. Ansam Phase 1 on Yas and Al Muneera on Raha Beach show occasional one-off discount prints.")
add("")

add("## Supply overhang vs current ready stock")
add("")
add("Allocates the announced 14,444-unit Aldar+Bloom+Modon AD-city pipeline across districts by their pre-event off-plan share, then divides by current 12-month ready transaction volume. Higher = future supply that needs to absorb.")
add("")
add("| District | Allocated pipeline units | Current 12m ready stock | Overhang ratio |")
add("|---|---|---|---|")
for _, r in supply.sort_values("supply_overhang_ratio", ascending=False).iterrows():
    if pd.isna(r["supply_overhang_ratio"]):
        continue
    add(f"| {r['district']} | {r['allocated_pipeline_units']:.0f} | {r['ready_stock_12m']:.0f} | **{r['supply_overhang_ratio']:.1f}x** |")
add("")

add("## The 3x3 stress matrix for shortlist cells")
add("")
add("Worst-case (rent -25% × vacancy +10pp) net yield by shortlist cell:")
add("")
add("| Cell | Base NET yield | Rent -10% / Vac +0 | Rent -25% / Vac +10 |")
add("|---|---|---|---|")
for _, r in shortlist.iterrows():
    cell = stress[(stress["district"] == r["district"]) & (stress["ptype"] == r["ptype"]) & (stress["layout"] == r["layout"])]
    base = cell[(cell["rent_haircut_pct"] == 10) & (cell["vacancy_add_pp"] == 0)]["net_yield_pct"].iloc[0] if len(cell) else None
    worst = cell[(cell["rent_haircut_pct"] == 25) & (cell["vacancy_add_pp"] == 10)]["net_yield_pct"].iloc[0] if len(cell) else None
    add(f"| {r['district']} {r['layout']} | {r['net_yield_adj_pct']:.2f}% | {base:.2f}% | **{worst:.2f}%** |")
add("")
add("Read: every shortlist cell holds positive NET yield even under the harshest stress, but with thin margin. Al Reem 3-bed (3.14%) and Yas 2-bed (3.71%) are the most fragile of the four; Reem 1-bed and 2-bed are the most robust.")
add("")

add("## What I would NOT chase, updated for v3")
add("")
add("- **Bloom Living Zayed sub-projects** (Toledo, Olvera, Casares, Granada, Seville): 90-100% secondary share post-event signals widespread forced-seller flow. Supply overhang in Zayed is 14.6x. Even if entry looks cheap, ready absorption is years away.")
add("- **Saadiyat Lagoons phases (Ethir, Wilds, Al Sidr) and Saadiyat Manarat I/II**: same pattern. Saadiyat 2-bed luxury also has NET yield collapse problem from heavy service charges.")
add("- **Al Shamkha plots and villas**: supply overhang 15.8x is the worst in the freehold whitelist. The Reeman Living 1/2 cohort is 92-96% secondary. Pure land speculation, not yield product.")
add("- **Off-plan launches in Yas during 2026**: Ansam Phase 2 (96% secondary), Noya 4/5 (93-100%), Sustainable City Phase 1 (100%) tell you the launch cycle is over-supplied. Buy ready secondary if you want Yas exposure.")
add("- **Saadiyat studios and 1-bed**: failed v3's CI gate. The raw +56% excess change collapsed to +36% on lag adjustment, and the CI on that estimate is wide. Probably more vulnerable than v2 implied.")
add("")

add("## Caveats v3")
add("")
add("1. The 45-day lag is a population median. Some segments lag 30 days, some lag 90+ days. The lag-adjusted view is an approximation, not ground truth.")
add("2. Rent adjustment of +11/+14/+15% applied uniformly within district. Real rent moves vary by project and product.")
add("3. Supply overhang ratio uses an evenly-weighted allocation of the 14,444-unit Aldar/Bloom/Modon AD-city pipeline by pre-event off-plan share. Actual project siting may concentrate more or less in specific districts.")
add("4. Mortgage approval lag (30-90 days) is layered on top of registration lag. Real demand response may not fully appear until July-August 2026 data we do not have.")
add("5. UAE cooling-off period (5-30 days) introduces positive selection: registered post-event deals are buyers who chose not to cancel. The full picture of demand impact requires listing-side data we do not have.")
add("6. Bootstrap CIs use only the post-event sample. Pre-event median is treated as fixed. A fully Bayesian view would joint-distribute over both.")
add("7. Project-level distress detection requires the project to have ≥10 pre-event ready-secondary deals. Newer projects with thinner pre-event histories cannot be benchmarked this way.")
add("8. Volume of new listings, days on market, and mortgage rejection rates are NOT in DARI and would meaningfully improve the post-event read.")
add("")

text = "\n".join(lines)
assert "—" not in text, "Em dash detected"
(OUT / "post_shock_memo_v3.md").write_text(text, encoding="utf-8")
print(f"Saved {OUT / 'post_shock_memo_v3.md'} ({len(text):,} chars)")
