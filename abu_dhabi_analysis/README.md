# Abu Dhabi DARI Investor Analysis

Investor-grade analysis of the Abu Dhabi residential market built from a DARI / ADREC
sales export, with external triangulation, net yields, off-plan IRR, and a freehold-zone
opportunity scorecard. Tuned for a UAE Golden Visa investor.

## Repo layout

```
abu_dhabi_analysis/
  config.yaml          all tunables (tiers, costs, weights, freehold zones, tolerances)
  scripts/             Python pipeline, runnable end-to-end
  external/            cached external evidence (yield benchmarks, pipeline, sources)
  outputs/             computed tables, charts, memo, parquet
  legacy/              prior loose analysis preserved for reference
```

## Reproduce

```bash
pip install pandas numpy matplotlib pyarrow statsmodels pyyaml
bash abu_dhabi_analysis/scripts/run_all.sh
```

Or run phase by phase:

```bash
python3 abu_dhabi_analysis/scripts/phase0_profile.py        # data_dictionary.md
# Phase 0 is the HARD STOP per brief. Review the dictionary before continuing.
python3 abu_dhabi_analysis/scripts/phase1_clean.py          # clean_transactions.parquet, qa_brief.md
python3 abu_dhabi_analysis/scripts/phase2_core.py           # leaderboards, charts
python3 abu_dhabi_analysis/scripts/phase3_appreciation.py   # hedonic, mix decomp, cycle, supply
python3 abu_dhabi_analysis/scripts/phase4_yields_offplan.py # net yields, off-plan IRR, forward overlay
python3 abu_dhabi_analysis/scripts/phase5_triangulate.py    # triangulation_table.csv
python3 abu_dhabi_analysis/scripts/phase6_score_shortlist.py # area_scorecard.csv, opportunity_shortlist.csv
python3 abu_dhabi_analysis/scripts/phase7_memo.py           # insight_memo.md
```

## Deliverables

- `outputs/insight_memo.md`         the investor memo, lead with 5 highest-conviction insights
- `outputs/area_scorecard.csv`       0 to 100 freehold district scoring with visible components
- `outputs/opportunity_shortlist.csv` ranked shortlist with thesis, segment, NET yield, what invalidates
- `outputs/triangulation_table.csv`  every top claim cross-checked against named external sources
- `outputs/charts/`                  one PNG per claim, titled with the takeaway
- `outputs/clean_transactions.parquet` reproducible canonical clean dataset
- `outputs/data_dictionary.md`       concept-to-column map and per-column profile
- `outputs/qa_brief.md`              Phase 1 cleaning surprises and trim counts

## What is and isn't computable from this DARI export

Computable: sales volume and value, AED/SQM levels and growth, mix-adjusted price index,
off-plan vs ready spread, residential complex / handover bulk activity, cycle classification,
supply-pressure trajectory.

Not computable from this file alone (handled with external sources, fully labelled):
mortgage and gift records (leverage / cash share), unit-level repeat sales,
buyer nationality / FDI mix, in-dataset rental yields. See `external/sources.md`.
