# Abu Dhabi Post-Shock Opportunity Memo, v3 (lag-corrected)

**Pivot date**: Feb 27, 2026. **Effective post-event start** (after 45-day registration-lag correction): Apr 13, 2026.
**Post-event window analyzed**: 1.6 months on the lag-adjusted view, 3.1 months on the raw view (both reported).
**Scope**: residential, freehold whitelist, ready apartments primary for the yield shortlist.
**Data**: DARI sales (87,655 clean transactions). Rent benchmarks: Bayut H1 2025, MPInvestments, Sands of Wealth, H2O Properties, adjusted for citywide +11% (Yas +15%, Saadiyat +14%) rent growth observed since H1 2025.

## What changed from v2, and what didn't

The v2 memo concluded the market did NOT crash post-Feb-27. After Anuj's call-out that v2 ignored the 30-90 day registration lag between deal agreement and DARI submission, this v3 rebuilds with the lag correction plus 19 other methodology fixes. The headline conclusion is **directionally the same but more conservative**:

- The shortlist shrank from 7 entries to **4** after the bootstrap CI gate and a tighter sample-size floor.
- Three v2 cells were eliminated: Reem studio (sample too thin in lag-adjusted window), Yas studio (same), Yas 1-bed (same), and Saadiyat studio (CI on excess-change crosses zero).
- The top of the shortlist is **Al Reem affordable apartments** (1-bed and 2-bed), unchanged from v2. The conviction is now better-supported.
- Forced-seller flow is best seen via **project cohort dump tracking**, a new v3 signal. 2022-2024 off-plan launches in specific projects are now 88-100% secondary, meaning nearly every transaction is a resale. This is the clearest evidence of post-event distress and the off-market entry path.

## Volume trajectory does not show a cliff

If the registration-lag hypothesis were strictly correct, weekly post-event deal counts should drop sharply around week 6 (when the pre-event pipeline runs out). The data does not show that cliff. Weeks 1 to 6 averaged about 458 deals; weeks 7+ averaged about 454 (ratio 0.99). The two readings are consistent with EITHER (a) genuine post-event demand stepping in as pipeline drained, or (b) a longer, more gradual lag tail. v3 takes the conservative interpretation: report both raw-pivot and lag-adjusted figures, and let the **cohort dump signal** carry the distress narrative.

## How much the lag correction moved each cell

The size of the lag correction varies materially by cell. Top 10 cells where the raw-pivot view overstated the post-event read:

| District | Property type | Layout | Raw excess % | Lag-adjusted % | Δ (pp) |
|---|---|---|---|---|---|
| Al Saadiyat Island | apartment | 1 bed | +56.0% | +36.2% | **+19.9** |
| Al Maryah Island | apartment | 1 bed | +78.4% | +63.5% | **+15.0** |
| Al Saadiyat Island | apartment | 2 beds | +49.4% | +37.2% | **+12.2** |
| Al Raha Beach | apartment | 4 beds | +0.2% | -10.8% | **+11.0** |
| Zayed City | apartment | 2 beds | +10.5% | +2.3% | **+8.3** |
| Fahid Island | apartment | 1 bed | +6.9% | +0.2% | **+6.7** |
| Al Reef | townhouse / attached villa | 3 beds | +18.0% | +12.9% | **+5.1** |
| Al Jubail Island | villa | 4 beds | +5.5% | +1.3% | **+4.2** |
| Al Raha Beach | apartment | 2 beds | +36.9% | +35.3% | **+1.6** |
| Yas Island | apartment | 2 beds | +32.0% | +30.6% | **+1.4** |

Saadiyat 1-bed and Maryah 1-bed are the biggest lag-contamination corrections. Their raw-pivot 'resilience' was substantially overstated. Raha Beach 4-bed apartments flipped sign (raw +0.2%, lag -10.8%): the apparent resilience was entirely a pipeline drain artifact.

## The shortlist (lag-adjusted, CI-gated, supply-penalized)

Restricted to: freehold zones, ready apartments, post-event volume ≥20 deals in the lag-adjusted window, regime not frozen, bootstrap 90% CI on excess-change does NOT include zero.

Net yield (adjusted) uses 12-month-stale Bayut/Sands of Wealth gross yields rolled forward by district-specific rent growth (+11% citywide, +15% Yas, +14% Saadiyat). Worst-case yield is the rent -25% × vacancy +10pp stress.

| Rank | District | Layout | Tier | n_post | Ticket | NET yield (adj) | Worst-case | Excess px % (CI) | Supply overhang | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Al Reem Island | 2 beds | affordable | 83 | AED 1.77M | **6.08%** | 3.78% | +35.7 [+34.7, +36.5] | 1.4x | high |
| 2 | Al Reem Island | 1 bed | midtier | 76 | AED 1.20M | **6.18%** | 3.72% | +32.7 [+29.9, +35.0] | 1.4x | high |
| 3 | Al Reem Island | 3 beds | midtier | 28 | AED 2.78M | **5.21%** | 3.14% | +24.9 [+19.0, +28.8] | 1.4x | medium |
| 4 | Yas Island | 2 beds | midtier | 20 | AED 2.37M | **5.99%** | 3.71% | +30.6 [+27.6, +33.0] | 4.8x | medium |

## Highest-conviction call

**Al Reem Island affordable / mid-tier apartments (1-bed and 2-bed) remain the highest-conviction post-event entry, with stronger statistical support than v2.** Excess change vs prior trajectory: 2-bed +35.7% (90% CI [34.7, 36.6]), 1-bed +32.7% (CI well above zero). Both deliver adjusted NET yields above 6.0% on all-in entry. Under the harshest stress scenario (rent -25%, vacancy +10pp), both still clear ~3.7% NET. The supply overhang ratio for Reem is **1.36x** (pipeline units / existing 12m ready stock), which is the LOWEST among heavy-volume districts (Shamkha 15.8x, Zayed 14.6x, Saadiyat 4.9x, Yas 4.8x). This means Reem is the freehold zone where existing ready demand absorbs new supply best.

## Cohort dump leaderboard, the v3 signal you should read most carefully

Off-plan launches from 2022-2024 where 88%+ of post-event off-plan transactions are SECONDARY (i.e., original buyer reselling before / shortly after handover). These are the projects with forced-seller flow.

| District | Project | Launch year | Post-event off-plan deals | Secondary share |
|---|---|---|---|---|
| Al Saadiyat Island | Louvre Residences | 2022 | 10 | **100%** |
| Al Saadiyat Island | Saadiyat Lagoons - Phase 2 - Ethir | 2023 | 6 | **100%** |
| Al Saadiyat Island | Saadiyat Grove - The Source | 2023 | 5 | **100%** |
| Zayed City | Bloom Living - Toledo | 2022 | 11 | **100%** |
| Yas Island | The Sustainable City - Yas Island - Phase 1 | 2023 | 36 | **100%** |
| Zayed City | Bloom Living - Olvera | 2024 | 6 | **100%** |
| Yas Island | Noya - Phase 5 - Yas Park Views | 2022 | 19 | **100%** |
| Zayed City | Bloom Living - Casares | 2023 | 8 | **100%** |
| Zayed City | Bloom Living - Granada 1 | 2024 | 11 | **100%** |
| Al Shamkha | Reeman Living 2 | 2023 | 24 | **96%** |
| Yas Island | Ansam - Phase 2 - The Golf Collection | 2022 | 44 | **95%** |
| Yas Island | Noya - Phase 4 - Yas Park Gate | 2022 | 15 | **93%** |
| Al Saadiyat Island | Nouran Living | 2024 | 26 | **92%** |
| Al Shamkha | Reeman Living | 2023 | 51 | **92%** |
| Zayed City | Bloom Living - Seville | 2024 | 11 | **91%** |
| Al Saadiyat Island | Saadiyat Lagoons - Phase 2 - Al Sidr | 2023 | 17 | **88%** |
| Al Saadiyat Island | Manarat Living I | 2023 | 16 | **88%** |
| Al Saadiyat Island | Saadiyat Lagoons - Wilds - Phase 1 | 2022 | 13 | **77%** |
| Al Saadiyat Island | Manarat Living II | 2024 | 13 | **77%** |
| Yas Island | Gardenia Bay | 2023 | 124 | **76%** |

Read: Bloom Living (Toledo, Olvera, Casares, Granada, Seville) in Zayed City is functioning as a resale market with virtually no developer-direct sales any more. Saadiyat Lagoons phases (Ethir, Wilds, Al Sidr), Saadiyat Grove (Source), and Saadiyat Manarat I/II are all dominated by resales. Yas Noya 4/5 and Ansam 2 same story. **These are the projects where off-market deal-making concentrates.** Approach brokers focused on these specific buildings.

## Project-level distressed ready-secondary trades (post-event, lag-adjusted)

Z-score against the PROJECT's own pre-event mean (not the district's). This is the v3 fix that filtered out false positives where a project simply trades below district average for structural reasons.

| Date | District | Project | Layout | Sqm | Price | psm | Project mean | Discount |
|---|---|---|---|---|---|---|---|---|
| 2026-04-27 | Al Reem Island | Radiant Square | 3 beds | 144 | AED 854k | AED 5,948 | AED 13,065 | **-54.5%** |
| 2026-04-20 | Al Reem Island | Hydra Avenue (Hydra Towers) | studio | 39 | AED 300k | AED 7,614 | AED 12,074 | **-36.9%** |
| 2026-04-24 | Yas Island | Ansam - Phase 1 | 3 beds | 392 | AED 5.25M | AED 13,392 | AED 19,166 | **-30.1%** |
| 2026-04-30 | Al Reef | Al Reef Downtown | 4 beds | 167 | AED 1.00M | AED 5,999 | AED 8,473 | **-29.2%** |
| 2026-04-30 | Al Raha Beach | Al Muneera (Mainland) | 2 beds | 145 | AED 1.52M | AED 10,513 | AED 14,613 | **-28.1%** |
| 2026-04-27 | Al Reem Island | The Wave | 1 bed | 92 | AED 920k | AED 10,044 | AED 13,111 | **-23.4%** |
| 2026-04-28 | Al Reem Island | Marina Square, Paragon Bay Mall | 2 beds | 124 | AED 1.23M | AED 9,879 | AED 12,348 | **-20.0%** |
| 2026-04-30 | Al Reem Island | Amaya Towers | 2 beds | 151 | AED 1.61M | AED 10,673 | AED 12,322 | **-13.4%** |

Use as input to off-market sourcing. Radiant Square, Hydra Avenue, The Wave, Marina Square Paragon Bay Mall, and Amaya Towers in Reem are seeing real discount activity. Ansam Phase 1 on Yas and Al Muneera on Raha Beach show occasional one-off discount prints.

## Supply overhang vs current ready stock

Allocates the announced 14,444-unit Aldar+Bloom+Modon AD-city pipeline across districts by their pre-event off-plan share, then divides by current 12-month ready transaction volume. Higher = future supply that needs to absorb.

| District | Allocated pipeline units | Current 12m ready stock | Overhang ratio |
|---|---|---|---|
| Al Shamkha | 348 | 22 | **15.8x** |
| Zayed City | 951 | 65 | **14.6x** |
| Al Saadiyat Island | 1827 | 372 | **4.9x** |
| Yas Island | 3434 | 719 | **4.8x** |
| Al Jubail Island | 148 | 96 | **1.5x** |
| Al Reem Island | 3982 | 2922 | **1.4x** |
| Al Maryah Island | 338 | 477 | **0.7x** |
| Al Raha Beach | 342 | 602 | **0.6x** |

## The 3x3 stress matrix for shortlist cells

Worst-case (rent -25% × vacancy +10pp) net yield by shortlist cell:

| Cell | Base NET yield | Rent -10% / Vac +0 | Rent -25% / Vac +10 |
|---|---|---|---|
| Al Reem Island 2 beds | 6.08% | 5.38% | **3.78%** |
| Al Reem Island 1 bed | 6.18% | 5.44% | **3.72%** |
| Al Reem Island 3 beds | 5.21% | 4.58% | **3.14%** |
| Yas Island 2 beds | 5.99% | 5.30% | **3.71%** |

Read: every shortlist cell holds positive NET yield even under the harshest stress, but with thin margin. Al Reem 3-bed (3.14%) and Yas 2-bed (3.71%) are the most fragile of the four; Reem 1-bed and 2-bed are the most robust.

## What I would NOT chase, updated for v3

- **Bloom Living Zayed sub-projects** (Toledo, Olvera, Casares, Granada, Seville): 90-100% secondary share post-event signals widespread forced-seller flow. Supply overhang in Zayed is 14.6x. Even if entry looks cheap, ready absorption is years away.
- **Saadiyat Lagoons phases (Ethir, Wilds, Al Sidr) and Saadiyat Manarat I/II**: same pattern. Saadiyat 2-bed luxury also has NET yield collapse problem from heavy service charges.
- **Al Shamkha plots and villas**: supply overhang 15.8x is the worst in the freehold whitelist. The Reeman Living 1/2 cohort is 92-96% secondary. Pure land speculation, not yield product.
- **Off-plan launches in Yas during 2026**: Ansam Phase 2 (96% secondary), Noya 4/5 (93-100%), Sustainable City Phase 1 (100%) tell you the launch cycle is over-supplied. Buy ready secondary if you want Yas exposure.
- **Saadiyat studios and 1-bed**: failed v3's CI gate. The raw +56% excess change collapsed to +36% on lag adjustment, and the CI on that estimate is wide. Probably more vulnerable than v2 implied.

## Caveats v3

1. The 45-day lag is a population median. Some segments lag 30 days, some lag 90+ days. The lag-adjusted view is an approximation, not ground truth.
2. Rent adjustment of +11/+14/+15% applied uniformly within district. Real rent moves vary by project and product.
3. Supply overhang ratio uses an evenly-weighted allocation of the 14,444-unit Aldar/Bloom/Modon AD-city pipeline by pre-event off-plan share. Actual project siting may concentrate more or less in specific districts.
4. Mortgage approval lag (30-90 days) is layered on top of registration lag. Real demand response may not fully appear until July-August 2026 data we do not have.
5. UAE cooling-off period (5-30 days) introduces positive selection: registered post-event deals are buyers who chose not to cancel. The full picture of demand impact requires listing-side data we do not have.
6. Bootstrap CIs use only the post-event sample. Pre-event median is treated as fixed. A fully Bayesian view would joint-distribute over both.
7. Project-level distress detection requires the project to have ≥10 pre-event ready-secondary deals. Newer projects with thinner pre-event histories cannot be benchmarked this way.
8. Volume of new listings, days on market, and mortgage rejection rates are NOT in DARI and would meaningfully improve the post-event read.
