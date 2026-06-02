# Abu Dhabi DARI Sales Export, Data Dictionary

Source file: `/root/.claude/uploads/87146dfe-f525-41fc-a638-d5be328ee62f/17939a6b-recent_sales_2.csv`
Rows: 114,485    Columns: 14
File encoding confirmed UTF-8.
Date range: 2019-01-02 to 2026-06-02.
Date system: Gregorian (verified by year range falling in 2019 to 2026, not Hijri 1440 to 1447).

## 10-row sample

```
Asset Class Property Type Sale Application Date  Property Sold Area (SQM)  Land Plot Ground Area (SQM) Property Layout       District Community                Project Name  Property Sale Price (AED)  Property Sold Share  Rate (AED per SQM) Sale Application Type Sale Sequence
residential     apartment            2026-06-02                     59.66                      8054.86          studio Al Reem Island       RS3         Radiant Elite Tower                   960000.0                  1.0        16091.183372              off-plan       primary
 commercial        retail            2026-06-01                    143.00                     25720.27      line store Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                  1388530.0                  1.0         9710.000000                 ready     secondary
residential        duplex            2026-06-01                    203.75                     25720.27          2 beds Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                  1978413.0                  1.0         9710.002454                 ready     secondary
residential     apartment            2026-06-01                    146.67                      5357.26          2 beds Al Reem Island       RT6     Rotana Residences North                  2680000.0                  1.0        18272.311993              off-plan       primary
 commercial        retail            2026-06-01                     50.15                     25720.27      line store Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                   486957.0                  1.0         9710.009970                 ready     secondary
 commercial        retail            2026-06-01                     59.58                     25720.27      line store Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                   578522.0                  1.0         9710.003357                 ready     secondary
residential        duplex            2026-06-01                    203.75                     25720.27          2 beds Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                  1978413.0                  1.0         9710.002454                 ready     secondary
 commercial        retail            2026-06-01                     78.00                     25720.27      line store Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                   757380.0                  1.0         9710.000000                 ready     secondary
 commercial        retail            2026-06-01                    298.00                     25720.27      line store Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                  2893580.0                  1.0         9710.000000                 ready     secondary
residential     apartment            2026-06-01                     51.70                     25720.27          studio Al Reem Island       RT3 Hydra Avenue (Hydra Towers)                   502007.0                  1.0         9710.000000                 ready     secondary
```

## Dtypes

```
Asset Class                               str
Property Type                             str
Sale Application Date          datetime64[us]
Property Sold Area (SQM)              float64
Land Plot Ground Area (SQM)           float64
Property Layout                           str
District                                  str
Community                                 str
Project Name                              str
Property Sale Price (AED)             float64
Property Sold Share                   float64
Rate (AED per SQM)                    float64
Sale Application Type                     str
Sale Sequence                             str
```

## Per-column profile

### `Asset Class`  (null 0.00%, distinct 10)
- Top values:
  - residential: 106,326
  - agricultural: 4,044
  - other: 2,149
  - commercial: 1,941
  - educational: 6
  - healthcare: 6
  - infrastructural: 6
  - industrial & storage: 3
  - religious: 3
  - recreational: 1

### `Property Type`  (null 0.00%, distinct 43)
- Top values:
  - apartment: 58,553
  - villa: 21,369
  - townhouse / attached villa: 13,279
  - plot for villa: 8,443
  - farm: 2,492
  - residential complex: 2,338
  - plot for farm: 1,553
  - duplex: 1,535
  - other: 1,400
  - office: 1,286
  - plot for residential complex: 467
  - other commercial plot: 374
  - retail: 282
  - plot for townhouse / attached villa: 218
  - mall / market / retail center: 208

### `Sale Application Date`  (null 0.00%, distinct 2,097)
- min 2019-01-02, max 2026-06-02

### `Property Sold Area (SQM)`  (null 3.78%, distinct 21,389)
- min 0.00, p1 31.53, median 153.57, mean 1,924.01, p99 33,489.00, max 12,474,855.21

### `Land Plot Ground Area (SQM)`  (null 0.00%, distinct 19,864)
- min 0.00, p1 127.14, median 4,771.04, mean 31,040.40, p99 250,493.84, max 12,474,855.21

### `Property Layout`  (null 0.00%, distinct 15)
- Top values:
  - unclassified: 25,430
  - 2 beds: 23,890
  - 1 bed: 20,985
  - 3 beds: 15,247
  - 4 beds: 9,973
  - studio: 9,930
  - 5 beds: 5,004
  - 6+ beds: 2,261
  - medium (50 to 500 sqm): 1,231
  - line store: 275
  - 5+ beds: 202
  - maxi (over 1000 sqm): 34
  - large (500 to 1000 sqm): 16
  - small (up to 50 sqm): 5
  - anchor store: 2

### `District`  (null 0.00%, distinct 132)
- Top values:
  - Al Reem Island: 25,242
  - Yas Island: 21,371
  - Al Saadiyat Island: 10,377
  - Al Reef: 6,425
  - Al Shamkhah: 5,863
  - Al Hidayriyyat: 4,863
  - Khalifa City: 4,840
  - Zayed City: 4,161
  - Al Rahah: 3,270
  - Al Faqa': 2,744
  - Al Bahyah: 2,693
  - Al Layyan: 2,000
  - Al Jubail Island: 1,668
  - Fahid Island: 1,520
  - Al Samhah: 1,314

### `Community`  (null 0.00%, distinct 927)
- Top values:
  - YN7: 6,596
  - Al Reef: 6,435
  - RT3: 5,837
  - YS1: 5,745
  - Al Hidayriyyat Island: 4,863
  - RT1: 4,124
  - SDN8: 3,915
  - MZ12: 3,772
  - SH36: 3,403
  - YS2: 2,916
  - RS6: 2,897
  - YS3_06: 2,724
  - SE45_05: 2,626
  - SDE3: 2,398
  - SH35: 2,310

### `Project Name`  (null 0.00%, distinct 365)
- Top values:
  - Private: 15,772
  - Marina Square, Paragon Bay Mall: 4,124
  - Al Reef Downtown: 2,838
  - Gardenia Bay: 2,629
  - Wadeem (Plots): 1,763
  - Water's Edge - Precinct B: 1,737
  - Radiant Square: 1,543
  - Ansam - Phase 2 - The Golf Collection: 1,459
  - Hydra Avenue (Hydra Towers): 1,450
  - Water's Edge - Precinct A: 1,378
  - Bal Ghaiylam: 1,303
  - The Sustainable City - Yas Island - Phase 1: 1,158
  - Al Reef Townhouses - Arabian Village: 1,153
  - Al Reef 2: 1,106
  - Reem Hills - Phase 2D: 1,057

### `Property Sale Price (AED)`  (null 0.00%, distinct 49,187)
- min 0.00, p1 101,926.08, median 1,787,436.23, mean 3,373,516.70, p99 22,648,661.32, max 2,486,500,000.00

### `Property Sold Share`  (null 0.00%, distinct 545)
- min 0.00, p1 0.50, median 1.00, mean 0.99, p99 1.00, max 1.00

### `Rate (AED per SQM)`  (null 3.80%, distinct 79,177)
- min 0.00, p1 11.45, median 12,582.92, mean 18,627.40, p99 45,638.66, max 120,000,000.00

### `Sale Application Type`  (null 0.00%, distinct 3)
- Top values:
  - off-plan: 69,000
  - ready: 44,716
  - court-mandated: 769

### `Sale Sequence`  (null 0.00%, distinct 2)
- Top values:
  - primary: 75,549
  - secondary: 38,934

## Area-unit verification (SQM, not SQFT)

`Rate (AED per SQM)` vs `price / sqm` median absolute relative difference: 0.0000%
Within 1% on 96.14% of rows. Confirms area unit is SQM and the rate column matches.

## Concept to canonical column map

| Concept | Source column | Canonical | Notes |
|---|---|---|---|
| transaction date | Sale Application Date | date | Gregorian, daily granularity. |
| transaction type | (implied: all sales) | n/a | Export is sales-only. No mortgage or gift rows. Leverage/credit signal NOT computable. |
| asset class | Asset Class | asset | residential or commercial. |
| property sub-type | Property Type | ptype | apartment, villa, townhouse, duplex, retail, office, land, etc. |
| off-plan vs ready flag | Sale Application Type | deal_type | off-plan, ready, court-mandated. |
| primary vs secondary | Sale Sequence | market | primary (developer) vs secondary (resale). |
| transacted price (AED) | Property Sale Price (AED) | price | Full headline price. Multiply by `share` for fractional sales if needed. |
| ownership share sold | Property Sold Share | share | 1.0 = full unit. Fractional <1 dropped for pricing per share threshold in config. |
| property area | Property Sold Area (SQM) | sqm | Square metres. Verified empirically. |
| land plot area | Land Plot Ground Area (SQM) | land_sqm | Project plot area, not unit area. |
| price per area | Rate (AED per SQM) | rate_sqm | Matches price / sqm within rounding. |
| property layout | Property Layout | layout | studio, 1 bed, 2 beds, etc. Some 'unclassified' rows present. |
| district | District | district | First-level area label, e.g. Al Reem Island, Yas Island. |
| community | Community | community | Sub-district sector code (RS3, RT6, etc.). |
| project | Project Name | project | Building or master project name. |
| unit / parcel id | MISSING | n/a | No unit identifier present. Repeat-sales index NOT feasible. Hedonic fallback used. |
| buyer nationality / FDI | MISSING | n/a | No buyer attributes in this export. FDI mix NOT computable. |
| rent / yield data | MISSING | n/a | No rent column. Net yields use cited external benchmarks, applied with the cost stack in config.yaml. |

## Key categorical landscapes (for alias normalization in Phase 1)

### `Asset Class` top 20
```
Asset Class
residential             106326
agricultural              4044
other                     2149
commercial                1941
educational                  6
healthcare                   6
infrastructural              6
industrial & storage         3
religious                    3
recreational                 1
```

### `Property Type` top 20
```
Property Type
apartment                                 58553
villa                                     21369
townhouse / attached villa                13279
plot for villa                             8443
farm                                       2492
residential complex                        2338
plot for farm                              1553
duplex                                     1535
other                                      1400
office                                     1286
plot for residential complex                467
other commercial plot                       374
retail                                      282
plot for townhouse / attached villa         218
mall / market / retail center               208
other residential plot                      172
other mixed-use plot                        160
plot for mall / market / retail center       78
penthouse                                    53
other plot                                   51
```

### `Sale Application Type` top 20
```
Sale Application Type
off-plan          69000
ready             44716
court-mandated      769
```

### `Sale Sequence` top 20
```
Sale Sequence
primary      75549
secondary    38934
```

### `District` top 20
```
District
Al Reem Island            25242
Yas Island                21371
Al Saadiyat Island        10377
Al Reef                    6425
Al Shamkhah                5863
Al Hidayriyyat             4863
Khalifa City               4840
Zayed City                 4161
Al Rahah                   3270
Al Faqa'                   2744
Al Bahyah                  2693
Al Layyan                  2000
Al Jubail Island           1668
Fahid Island               1520
Al Samhah                  1314
Al Maryah Island           1025
Ghadeer Al Tayr             810
Ain Al Faydah               801
Mohamed Bin Zayed City      699
Bani Yas                    690
```

## Headline scope counts

- Asset class share: residential 92.9%, agricultural 3.5%, other 1.9%, commercial 1.7%, educational 0.0%, healthcare 0.0%, infrastructural 0.0%, industrial & storage 0.0%, religious 0.0%, recreational 0.0%
- Off-plan vs ready share: off-plan 60.3%, ready 39.1%, court-mandated 0.7%
- Primary vs secondary share: primary 66.0%, secondary 34.0%
- Property type top 5: apartment 51.1%, villa 18.7%, townhouse / attached villa 11.6%, plot for villa 7.4%, farm 2.2%
- Fractional share rows (share < 0.99): 1,552 (1.36%)
- Zero or null price rows: 61
- Zero or null sqm rows: 4,356

## Critical caveats and HARD STOP guidance

1. The export contains SALES only. Mortgages and gifts are absent, so the leverage/credit signal requested in Phase 2 cannot be computed. Cash share also cannot be derived.
2. There is no unit or parcel identifier. A proper repeat-sales index requires matching the same asset across multiple transactions; this export does not allow that. Phase 3 will fall back to a hedonic mix-adjusted index, with off-plan-to-handover modelled as a SEPARATE cohort metric.
3. No buyer nationality. The FDI/foreign-share signal requested in Phase 2 cannot be computed.
4. No rent column. Net yields in Phase 4 require external benchmarks, joined per district and labelled with their source.
5. The most recent 1 to 2 quarters are likely under-recorded because off-plan registrations lag transaction dates. Phase 1 will tag them as `is_preliminary`.
6. Fractional-share transactions are present and will be excluded from pricing analysis.

