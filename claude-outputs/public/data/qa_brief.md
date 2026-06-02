# Phase 1, Cleaning QA Brief

Raw rows loaded: 114,485

## Filter chain (residential + commercial)

- Drop court-mandated: dropped 769, remaining 113,716
- Drop price < AED 100,000 or null: dropped 928, remaining 112,788
- Drop sqm null or zero: dropped 4,241, remaining 108,547
- Drop rate_sqm null or zero: dropped 0, remaining 108,547
- Drop share < 0.99: dropped 835, remaining 107,712
- Keep residential core + commercial scope only: dropped 14,637, remaining 93,075
- Drop exact duplicates on date, district, project, sqm, price, layout, deal_type, market: dropped 5,420, remaining 87,655

## Tier breakpoints (data-driven, residential trailing 12m AED/SQM terciles)

- Affordable:  rate_sqm <= 15,452
- Mid-tier:    15,452 < rate_sqm <= 21,450
- Luxury:      rate_sqm >  21,450

## Outlier trimming (within ptype x tier strata, p0.5 to p99.5)

Rows trimmed: 896 (1.02% of pre-trim).

## Preliminary-quarter flag

Quarters flagged as preliminary: ['2026Q1', '2026Q2']
Rows in preliminary window: 12,406 (14.3%)

## Headline clean-dataset summary

- Total clean rows: 86,759
- Residential cut: 85,555
- Commercial cut:  1,204
- Date range: 2019-01-02 to 2026-06-02
- Aggregate value: AED 265.90B
- Median ticket: AED 1.81M (residential AED 1.80M)
- Median AED/SQM: residential 13,568, commercial 12,084

## Top 15 districts by clean transaction count

```
cut                 commercial  residential  total
district                                          
Al Reem Island             897        22082  22979
Yas Island                   4        19944  19948
Al Saadiyat Island          49         9535   9584
Al Reef                     34         6013   6047
Khalifa City                 2         3558   3560
Al Raha Beach               45         3107   3152
Zayed City                   0         2950   2950
Hudayriyat Island            0         2445   2445
Al Layyan                    0         1793   1793
Al Shamkha                   9         1685   1694
Al Bahyah                    1         1516   1517
Fahid Island                 0         1509   1509
Al Jubail Island             1         1213   1214
Al Maryah Island             7          989    996
Al Samhah                    9          688    697
```

## Residential tier distribution

```
            deals  median_psm  median_price
tier                                       
affordable  52783     11509.0     1521877.0
luxury      13399     27464.0     3369850.0
midtier     19373     17764.0     2050000.0
```

## Masdar City verification

After project-name reclassification, Masdar City carries 529 clean rows.

## Surprises and call-outs to remember in later phases

1. Residential complex rows can carry very large aggregate ticket sizes (handover bulk transfers). When computing district-level median AED/SQM, this is fine, but for total VOLUME their share will spike in particular quarters. Phase 2 should highlight these spikes.
2. The preliminary-quarter flag covers the two most recent quarters per config. Headline YoY momentum in Phase 2 onward should annotate when a comparison touches the preliminary window.
3. Within-strata trimming removed a small share of rows but preserves real fat tails inside each tier; do not interpret post-trim p99 figures as the actual market high.
4. Commercial volume is small relative to residential. Cell-n thresholds in Phase 2 will suppress most fine-grained commercial cuts; we will report commercial at district x deal_type level only.

