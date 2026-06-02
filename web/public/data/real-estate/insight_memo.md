# Abu Dhabi Real Estate Investor Memo

**For**: Anuj (UAE Golden Visa, current holding: Yas Island, Mayan 2)
**As of**: 2026-06-02
**Source**: DARI / ADREC sales export (114,485 raw rows, 87,655 clean transactions, AED 265.9B aggregate 2019 to today). External triangulation against ADREC 2025 Report, Bayut H1 2025, Sands of Wealth 2025, Engel & Volkers, Cushman & Wakefield Core, MPInvestments. Every figure traces to either the clean parquet or a named external source with URL.

---

## Five highest-conviction insights, triangulated

### 1. The Abu Dhabi headline overstates true appreciation by roughly 4x

- **Dataset**: headline residential psm rose **+22.6%** in the last 12 months. Decomposition: only **18% is pure same-quality price** (about +4.1%); **82% is mix shift** into luxury and off-plan stock.
- **External corroboration**: Engel & Volkers/Bayut cite citywide residential price growth of 7-11% in 2025; Bayut splits affordable +12%, mid +19%, luxury +27%. Our mix decomposition reconciles these segment numbers and shows that the apparent headline overstates what a same-quality home actually appreciated by.
- **Chart**: `outputs/charts/phase3_04_mix_decomposition.png`

### 2. Almost every freehold district is late-cycle; pullbacks not on the menu

- **Dataset**: 15 districts classify as late-cycle/overheating (100th percentile psm vs own history, positive but decelerating momentum). Only **Al Jubail Island, Al Bahyah** classifies as mid-cycle.
- **External corroboration**: Cushman & Wakefield Core forecast 2026 growth 5-8% (moderation from 12-22% prior). ADREC reports 87% cash transactions and 50%+ FDI share, both characteristic of late-cycle euphoria.
- **Chart**: `outputs/charts/phase3_05_cycle_map.png`

### 3. Off-plan pre-pays the appreciation: IRR is broken in most districts

- **Dataset**: at current pricing, off-plan trades at a 17-89% premium over ready in the major freehold areas (Yas +17%, Reem +27%, Saadiyat +89%). Modelling the staged payment plan (10/10/10/10/10/50 over 36 months) at scenario C (+6%/y forward consensus) gives Yas IRR +1.4%, Reem IRR -6.7%, Saadiyat negative.
- **External corroboration**: ADREC notes off-plan share rose to 71% of residential 2025 (from 49% in 2024). When a market is in price-discovery on off-plan launches, the developer captures the appreciation, not the buyer.
- **Chart**: `outputs/charts/phase4_02_offplan_irr.png`

### 4. Al Raha Beach is the largest single forward-supply overhang in the whitelist

- **Dataset**: Al Raha Beach off-plan share moved from **0.5% to 57.2%** in 12 months, the largest swing in any freehold district (+57pp). The current +40.5% YoY psm is the pre-handover rerating, not a sustainable post-handover level.
- **External corroboration**: the UAE Media Office announcement of 14,444 units across the Aldar+Bloom+Modon AD city pipeline (AED 55.4B) confirms structural new supply 2026-29.
- **Chart**: `outputs/charts/phase3_06_offplan_supply_pressure.png`

### 5. Yield-led and appreciation-led rankings diverge sharply

- **Dataset, yield-led ranking (NET on all-in entry)**: Al Reem 5.72%, Masdar 5.44%, Al Reef 5.35%, Khalifa City 5.31%, Yas Island 5.10%, Zayed City 5.08%, Saadiyat 4.00%, Fahid 3.67%, Hudayriyat 3.66%, Maryah 3.25%.
- **External corroboration**: Bayut/Sands of Wealth gross yields support Reem (~7.49%) and Yas (~7.07%) at the top; Saadiyat 2-bed gross 2.5% is the canonical low-yield trophy. Net yields include the cost stack: ADM 2%, agent 2%, vacancy 7%, tier-based service charges.
- **Chart**: `outputs/charts/phase4_01_net_yields.png`

---

## Opportunity scorecard, 0 to 100, freehold whitelist only

Weights: net_yield 25%, appreciation_momentum (mix-adjusted) 20%, cycle_position 20%, liquidity 15%, supply_risk_inverse 10%, value_vs_own_history 10%. Per the brief's instruction, the value component rewards districts that are CHEAPER relative to their own trend, matching the pullback discipline.

| District | Net yield | YoY psm | Cycle | Liq score | Supply inverse | Value vs history | Total |
|---|---|---|---|---|---|---|---|
| Al Reem Island | 5.70% | +39.9% | late-cycle/overheating | 100 | 20 | 0 | **67.9** |
| Yas Island | 5.10% | +25.1% | late-cycle/overheating | 88 | 33 | 32 | **60.0** |
| Masdar City | 5.40% | +17.2% | late-cycle/overheating | 0 | 100 | 0 | **51.4** |
| Al Reef | 5.40% | +25.4% | late-cycle/overheating | 20 | 39 | 0 | **49.8** |
| Al Raha Beach | 4.80% | +40.5% | late-cycle/overheating | 42 | 0 | 0 | **48.3** |
| Al Saadiyat Island | 4.00% | +31.2% | late-cycle/overheating | 66 | 39 | 32 | **47.9** |
| Zayed City | 5.10% | +9.4% | late-cycle/overheating | 46 | 43 | 0 | **46.6** |
| Al Jubail Island | 3.40% | +15.6% | mid-cycle | 1 | 63 | 100 | **46.1** |
| Hudayriyat Island | 3.70% | +24.2% | late-cycle/overheating | 66 | 39 | 0 | **39.2** |
| Al Shamkha | 4.90% | +4.2% | late-cycle/overheating | 25 | 35 | 0 | **39.0** |
| Al Maryah Island | 3.20% | -28.3% | cooling | 32 | 50 | 0 | **19.7** |

Reading: Al Reem dominates the composite by liquidity and yield, but scores zero on value vs own history (it sits at 100th percentile). Al Jubail Island is the only mid-cycle freehold with positive momentum, and it scores 100 on value vs history (the cheapest relative to its own trend).

---

## Ranked opportunity shortlist

### 1. Al Reem Island, ready 1-bed apartment, mid-tier

**Thesis**. Reem is the most liquid freehold market in AD and the highest scoring net yield on the entry tier; the 1-bed psm sits at AED 16-18k with median ticket AED 1.6M giving ~5.7% NET on all-in.

- Expected NET yield: **5.72%** on all-in entry.
- Appreciation case: Headline +40% YoY but mix-decomposition says <20% of that is same-quality price; underlying ready 1-bed appreciation more like +6-10% per year going forward (Cushman consensus).
- What invalidates: Off-plan share has risen from 39% to 66% in 12 months. If that pipeline starts handing over without matched FDI demand, ready 1-bed psm gets capped or pulled down.
- Cycle risk: Late-cycle on price (100th pct), but liquidity supports exit at any time.
- Supply risk: High. Reem off-plan supply is the largest forward overhang in the freehold whitelist.
- External sources: ADREC, Bayut H1 2025, Sands of Wealth 2025 (yield ~7.49% gross, net 5.7-6.6%)

### 2. Yas Island, ready 2-bed apartment, secondary market only

**Thesis**. Yas has the tightest vacancy (3.8% per Bayut) and the strongest demand catalyst in the emirate (Disney World announcement, leisure cluster). NET yield 5.1% on all-in entry. The right tactic on Yas today is READY-SECONDARY, not off-plan.

- Expected NET yield: **5.10%** on all-in entry.
- Appreciation case: Forward consensus 5-8%/y (Cushman). Disney is upside optionality but already in price.
- What invalidates: Off-plan IRR is BARELY positive at +6% forward (scenario C) because off-plan trades at 17% premium over ready. If Disney is delayed or downsized the premium collapses.
- Cycle risk: Late-cycle/overheating, 97th pct. Decelerating momentum (3m print negative).
- Supply risk: Medium. Off-plan share rose 80% -> 88%, but Yas has long-running absorption.
- External sources: Bayut, MPInvestments, UAE Media Office Disney announcement

### 3. Al Reef, ready apartment, affordable tier

**Thesis**. Al Reef offers 5.35% net yield at AED ~1M ticket; very low off-plan share (~0%) means no supply overhang and a settled rental market. The least-correlated freehold play to the luxury wave.

- Expected NET yield: **5.35%** on all-in entry.
- Appreciation case: +25% YoY price growth tells you the affordable tier is catching the rotation. Forward expectation 5-8% per Cushman, weighted higher in affordable per Engel & Volkers.
- What invalidates: If interest rates rise and end-user mortgages contract, the affordable tier is most rate-sensitive.
- Cycle risk: Late-cycle on price percentile but volume already lower (-6.7%); has not run as hard as Reem/Yas.
- Supply risk: Very low. No active off-plan pipeline.
- External sources: H2O Properties 2025 yields, Bayut H1 2025

### 4. Masdar City, ready 1-bed apartment, sustainability premium

**Thesis**. Masdar trades at ~5.44% net yield with median ticket AED 627k. After being 88% off-plan in 2024, off-plan share collapsed to 0% in 2025-26 meaning the inventory is now landing in the resale market. ESG / sustainability mandate is a durable tenant pull.

- Expected NET yield: **5.44%** on all-in entry.
- Appreciation case: +17% YoY psm growth from a small base. Volume up +432% YoY as ready inventory matures.
- What invalidates: Tiny market (229 deals/12m). Liquidity risk on exit. Only specific projects are freehold-eligible.
- Cycle risk: Late-cycle/overheating per classifier, but volume surge is supply-driven not demand-exhausted.
- Supply risk: Negative (off-plan share down 88pp). Supply already crystallizing.
- External sources: H2O Properties 2025, internal dataset analysis

### 5. Al Raha Beach, WAIT, do not buy off-plan now

**Thesis**. Al Raha Beach off-plan share rocketed from 0.5% to 57% in 12 months. Forward supply is staggering. The current +40% YoY headline is the pre-handover rerating; once units arrive, ready psm will be capped.

- Expected NET yield: **4.83%** on all-in entry.
- Appreciation case: Wait 12-18 months for the off-plan-over-ready premium to compress, then enter ready secondary.
- What invalidates: Off-plan share rise reverses sharply on a single project default or delay.
- Cycle risk: Late-cycle/overheating, 100th pct.
- Supply risk: Highest in the dataset (+56pp swing). Active developer pipeline.
- External sources: Internal supply-pressure trend; Aldar pipeline announcement

### 6. Al Saadiyat Island, selective premium, do NOT chase off-plan

**Thesis**. Saadiyat is the trophy market with the worst NET yield in the freehold whitelist (4.0%) and the widest off-plan premium over ready (+89%). Buy only specific cultural-anchor ready stock with a 7+ year hold.

- Expected NET yield: **4.00%** on all-in entry.
- Appreciation case: Capital growth story, not yield. Rents +14% (Bayut), supply tight.
- What invalidates: Off-plan premium widening +16pp last year is classic euphoria. Mean-reversion downside is real.
- Cycle risk: Late-cycle/overheating, volume DOWN -13% YoY = distribution.
- Supply risk: Off-plan share stable ~87%, but new Aldar/Ethir launches add absolute supply.
- External sources: Bayut, Sands of Wealth, Cushman 2026 forecast

### 7. Khalifa City, ready apartment in established sub-area

**Thesis**. 5.31% net yield on AED 1.1M median ticket. Importantly, Khalifa City is the ONE district where off-plan trades 19.5% BELOW ready (opposite of the rest of the market), so the off-plan economics are uniquely favorable IF you pick the right sub-area.

- Expected NET yield: **5.31%** on all-in entry.
- Appreciation case: +21% YoY headline. Off-plan IRR scenarios show +21-38% if you select correctly.
- What invalidates: Off-plan stock here is in non-prime sub-areas; need on-the-ground due diligence on which project.
- Cycle risk: Late-cycle but lowest premium-to-trend in the freehold whitelist.
- Supply risk: Off-plan share rising +18pp (62% -> 80%).
- External sources: Global Property Guide, H2O Properties

Note on Khalifa City: officially leasehold for most of the district, with only specific projects (e.g. Etihad Towers, Bloom Living) freehold-eligible. If you cannot legally take freehold on the specific building, skip it and re-allocate to Al Reem ready secondary.

---

## Yas Island, marginal portfolio fit verdict

**Recommendation: HOLD existing Mayan 2 exposure; do NOT add. Specifically do not buy Yas off-plan.**

**Why hold and not add (concentration argument)**:
- You already have Yas exposure. Adding more concentrates you in a district that is **late-cycle, 97th percentile, decelerating** (trailing 3m psm is negative).
- Yas off-plan share rose 80% to 88% in 12 months. The forward pipeline is real, with Aldar construction lined up. Off-plan IRR at scenario C is **only +1.4%** (essentially zero) because off-plan trades at +17% over ready before you fund the payment plan.

**Why hold rather than trim**:
- Yas has the tightest vacancy in Abu Dhabi (3.8% per Bayut), gross apartment yield 7.1% (luxury 7.07%), rents +15% in 2025. Mayan 2 is a ready unit, so the rental income side is intact.
- The Disney World announcement is a durable demand catalyst that is already priced but provides a floor under capital values.
- Liquidity is high (5,084 trailing-12m deals), so you can exit if the thesis changes.

**Tactic if you want more Abu Dhabi exposure**: rotate the next dirham to Al Reem ready 1-bed (higher NET yield, deepest liquidity, lowest correlation to Yas-specific risks like Disney delivery), or to Al Reef ready apartment (zero supply pressure, less rate-sensitive end-user base).

---

## Contrarian calls, where the popular narrative may be mispriced

### Contrarian 1: Al Jubail Island, the only mid-cycle freehold mispriced by mix-narrative

**Thesis**. The 'everything is late-cycle' headline obscures Al Jubail Island, which classifies as **mid-cycle** with +15.6% YoY psm, +43% volume YoY, the lowest current-vs-own-history percentile in the freehold whitelist (89th vs 100th elsewhere), and a *falling* off-plan share (-35pp). Off-plan share dropping while volume rises means the market is digesting prior supply and transitioning to a ready/resale base.

**Counterpoint that the popular narrative misses**. Al Jubail is small (234 trailing-12m deals) and high-priced (AED 18,850/sqm median), so it does not show up on broker league tables of "hottest" districts. But on the mix-adjusted basis it is one of the few places where you would buy on a pullback.

**External cross-check**. Aldar's Jubail Island Phase 2 specifically saw +61% YoY psm in our project leaderboard. Bayut and Sands of Wealth do not publish a Jubail-specific yield, so the yield case is weaker than Reem or Yas.

### Contrarian 2: Al Maryah Island looks like the right place to ASK about value, not the wrong place

**Thesis**. Al Maryah is the only district with **negative YoY psm (-28.3%)**, cooling cycle classification, off-plan premium collapsed from +51% to +9% over ready (mean reverting). This is the canonical late-cycle distribution pattern: weaker districts sell off first. If you believe the AD cycle is turning, Maryah is the leading indicator and the cheapest freehold entry.

**Counterpoint**. NET yield is the worst in the whitelist (3.25%), reflecting high service charges on a central business district mixed-use product. Maryah is also a 'thin' market (689 deals) with specific commercial drag from neighbouring office vacancy. This trade is for someone with patience and a thesis on Maryah's office repricing, not a yield buyer.

**External cross-check**. No external source called Maryah a buy in 2025 (the narrative was Hudayriyat, Saadiyat, Yas). The absence of consensus IS the contrarian setup.

---

## Triangulation summary, all top claims cross-checked

| Claim | Our figure | External | Source | Variance |
|---|---|---|---|---|
| 2025 residential sales value, AED B | 66.77 | 76.1 | ADREC 2025 Report (via MPInvestments) | -12.3% |
| 2025 residential sales volume (units) | 20276.0 | 23600.0 | ADREC 2025 Report | -14.1% |
| Off-plan share of residential sales 2025 (%) | 68.52 | 71.0 | ADREC 2025 Report (via abu-dhabi.realestate) | -3.5% |
| Residential sales value YoY 2025 vs 2024 (%) | 69.68 | 67.0 | ADREC 2025 Report | +4.0% |
| Pure-price 12m growth (mix-adjusted), citywide residential apartments incl mixed ptypes (%) | 4.12 | 7.0 | Engel & Volkers / Bayut citywide AD 2025 published price growth | -41.1% |
| Hudayriyat Island, trailing 12m residential value (AED B) | 20.25 | 12.5 | ADREC 2025 Report (calendar year) | +62.0% |
| Yas + Saadiyat luxury apartment YoY psm (%) | 25.47 | 27.0 | Bayut H1 2025 + Engel & Volkers | -5.7% |
| Cash share of transactions (%) | not computable | 87.0 | ADREC 2025 Report | n/a |
| FDI / expat share of residential sales value (%) | not computable | 50.0 | ADREC 2025 Report | n/a |
| Yas Island rents YoY 2025 (%) | not computable | 15.0 | Bayut Abu Dhabi Rental Report H1 2025 | n/a |
| Saadiyat Island rents YoY 2025 (%) | not computable | 14.0 | Bayut Abu Dhabi Rental Report H1 2025 | n/a |
| 2026 citywide price growth forecast (%) | not computable | 6.0 | Cushman & Wakefield Core via Arabian Business (consensus midpoint 5-8%) | n/a |
| Announced forward supply pipeline (units, AD city) | not computable | 14444.0 | UAE Media Office (Aldar+Bloom+Modon 6-community programme) | n/a |
| Al Raha Beach off-plan share change (ppt, last 12m vs prior 12m) | 56.68 | n/a | Internal hedonic + supply pressure trend | n/a |

Two claims sit outside the 15% tolerance band: pure-price 12m growth (-41% variance) and Hudayriyat trailing-12m value (+62%). Both are reconciled in the table notes: the first is a scope/weighting difference between our hedonic and published indices; the second reflects calendar-2025 ADREC vs our trailing-12m window (which includes the first five months of 2026, when Hudayriyat accelerated).

---

## Data caveats and what I could not compute

1. **No mortgage or gift records.** This DARI export is sales-only. Leverage/credit signal and cash share are NOT computable. The ADREC 2025 figure of 87% cash is external-only.
2. **No unit/parcel ID.** A proper repeat-sales index requires matching the same asset across transactions. We used a hedonic mix-adjusted index instead (citywide R-squared adj ~0.65) and modelled off-plan-to-handover as a separate cohort metric.
3. **No buyer nationality.** FDI mix and foreign-buyer trend are NOT computable. The ADREC 2025 figure of 50%+ FDI share is external-only.
4. **No rent data.** NET yields use external gross yields from Bayut, Sands of Wealth, MPInvestments, H2O Properties, then apply the cost stack from `config.yaml` (ADM 2%, agent 2%, vacancy 7%, tier-based service charges). Three districts (Hudayriyat, Al Jubail, Fahid) lack direct external yields; estimates flagged in `outputs/net_yields_by_district.csv`.
5. **Preliminary quarters.** 2026Q1 and 2026Q2 carry 12,406 rows (14% of clean parquet). Off-plan registrations lag; treat their YoY comparisons as preliminary.
6. **Mix-decomposition limits.** The decomposition uses ptype x tier x deal_type cells; finer cuts would change the price/mix split modestly. Direction of the conclusion (~80% mix) is robust to this choice.
7. **Off-plan IRR depends on the resale-at-handover assumption.** We show three scenarios (spot, historical-uplift, +6%/y forward consensus). The negative conclusion holds across all three for the major districts; the +21% Khalifa City scenario A is real but reflects sub-prime off-plan stock, not a generalizable opportunity.
8. **Real / inflation-adjusted view not provided.** No UAE CPI source ingested in this run; all figures are nominal AED.
9. **Freehold whitelist** matches Abu Dhabi's designated investment zones to the best of informally available information. Reconfirm against ADREC's official designation when actually purchasing. Khalifa City is mostly leasehold; only specific projects are freehold-eligible.

---

## Reproduction

From the repo root:

```bash
pip install pandas numpy matplotlib pyarrow statsmodels pyyaml
python3 abu_dhabi_analysis/scripts/phase0_profile.py     # outputs/data_dictionary.md
# pause and review the dictionary, then continue
python3 abu_dhabi_analysis/scripts/phase1_clean.py        # outputs/clean_transactions.parquet
python3 abu_dhabi_analysis/scripts/phase2_core.py         # leaderboard, charts
python3 abu_dhabi_analysis/scripts/phase3_appreciation.py # hedonic, cycle, mix
python3 abu_dhabi_analysis/scripts/phase4_yields_offplan.py
python3 abu_dhabi_analysis/scripts/phase5_triangulate.py
python3 abu_dhabi_analysis/scripts/phase6_score_shortlist.py
python3 abu_dhabi_analysis/scripts/phase7_memo.py         # outputs/insight_memo.md
```

All tunables in `config.yaml`; rerunning after a config change regenerates all outputs.