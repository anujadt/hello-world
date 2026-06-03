"""
Item 4: triangulation refresh against post-event (Q1/Q2 2026) external sources.

Compares the v3 post-shock findings to freshly published 2026 reports
(ValuStrat Q1 2026 via Nasluxury, CBRE Q1 2026, ADREC 2025, Engel & Volkers,
99acres Al Reem rates, Sands of Wealth Yas rates).
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

ROOT = Path("/home/user/hello-world/abu_dhabi_analysis")
V3 = ROOT / "post_shock" / "outputs" / "v3"

yields = pd.read_csv(V3 / "yield_overlay_v3.csv")
reem_1b = yields[(yields["district"] == "Al Reem Island") & (yields["layout"] == "1 bed")]["psm_post_ready"].iloc[0]
yas_apt = yields[(yields["district"] == "Yas Island") & (yields["ptype"] == "apartment")]["psm_post_ready"].median()

rows = [
    {
        "claim": "Citywide apartment price direction post-Feb-27",
        "my_finding": "Resilient/up; Reem excess +33 to +36% vs trajectory, no broad crash",
        "external_figure": "ValuStrat Q1 2026: apartments +22.7% YoY, villas +13.4%",
        "source": "ValuStrat Q1 2026 (via Nasluxury)",
        "source_url": "https://nasluxury.com/blogs/abu-dhabi-real-estate-q1-2026-what-the-valustrat-data-really-means-for-buyers-and-investors/",
        "variance": "Direction matches (continued appreciation, not crash)",
        "confidence": "high",
        "reconciliation": "My excess-change is vs own pre-event trajectory (de-seasoned); ValuStrat is raw YoY. Both confirm the market kept rising through the event window. Validates the v3 'no broad crash' conclusion.",
    },
    {
        "claim": "Al Reem Island apartment AED/SQM",
        "my_finding": f"1-bed AED {reem_1b:,.0f}/sqm (lag-adjusted post-event median)",
        "external_figure": "Al Reem AED 15,290/sqm (2026)",
        "source": "99acres Al Reem rates 2026",
        "source_url": "https://www.99acres.com/property-rates-and-price-trends-in-al-reem-island-abu-dhabi-prffid",
        "variance": f"{(reem_1b/15290 - 1)*100:+.1f}%",
        "confidence": "high",
        "reconciliation": "Within ~2% of published Al Reem psm. Strong corroboration of the entry-price basis for the lead pick.",
    },
    {
        "claim": "Yas Island apartment AED/SQM",
        "my_finding": f"Apartment median AED {yas_apt:,.0f}/sqm (lag-adjusted)",
        "external_figure": "Yas Island AED 21,790/sqm (2026)",
        "source": "Sands of Wealth 2026",
        "source_url": "https://sandsofwealth.com/blogs/news/abu-dhabi-how-much-apartment",
        "variance": f"{(yas_apt/21790 - 1)*100:+.1f}%",
        "confidence": "medium",
        "reconciliation": "My figure is the median across all Yas apartment layouts in ready-secondary; the published headline skews to newer/larger luxury stock. Mix difference explains the gap.",
    },
    {
        "claim": "Distress breadth post-event",
        "my_finding": "Distress concentrated (cohort dump in specific 2022-24 launches); broad ready market resilient",
        "external_figure": "Most properties sell 1-4% below initial asking; sellers retain pricing power",
        "source": "Sands of Wealth / Engel & Volkers 2026",
        "source_url": "https://www.engelvoelkers.com/ae/en/resources/abu-dhabi-property-market",
        "variance": "Strong agreement",
        "confidence": "high",
        "reconciliation": "Both say aggregate distress is shallow. My cohort-dump signal locates WHERE the forced sellers are (specific off-plan launches), which the aggregate 1-4% figure masks.",
    },
    {
        "claim": "Citywide occupancy / vacancy",
        "my_finding": "Assumed 7% vacancy in base net yield (stress tests at 12% and 17%)",
        "external_figure": "Occupancy 88.1% (implies ~11.9% vacancy)",
        "source": "ValuStrat Q1 2026",
        "source_url": "https://nasluxury.com/blogs/abu-dhabi-real-estate-q1-2026-what-the-valustrat-data-really-means-for-buyers-and-investors/",
        "variance": "My base 7% is optimistic; actual ~12%",
        "confidence": "high",
        "reconciliation": "IMPORTANT: my base-case 7% vacancy understates the citywide ~12% vacancy. The +5pp stress (12% vacancy) is therefore the realistic case, not a stress. Use the stress-adjusted yields as the working numbers.",
    },
    {
        "claim": "2025 residential transactions",
        "my_finding": "~20,276 clean residential sales (2025)",
        "external_figure": "21,279 residential sales (+47.43% YoY)",
        "source": "ADREC 2025 annual",
        "source_url": "https://adrec.gov.ae/en/Market_Reports",
        "variance": f"{(20276/21279 - 1)*100:+.1f}%",
        "confidence": "high",
        "reconciliation": "Within 5%; my cleaning drops court-mandated, fractional-share, and sub-AED-100k rows. Scope difference fully explains the gap.",
    },
    {
        "claim": "Cash transaction share",
        "my_finding": "Not computable (DARI sales-only export, no mortgage flag)",
        "external_figure": "~80% cash (down from 87% in 2025)",
        "source": "ADREC 2026",
        "source_url": "https://www.cbre.ae/insights/figures/uae-real-estate-market-review-q1-2026",
        "variance": "External only",
        "confidence": "external-only",
        "reconciliation": "Cash share easing from 87% to 80% signals modest financing uptick, supporting the leverage case in the IRR model (positive carry at 5.25% vs 6.08% net yield).",
    },
]

df = pd.DataFrame(rows)
df.to_csv(V3 / "triangulation_refresh.csv", index=False)
print(df[["claim", "my_finding", "external_figure", "variance", "confidence"]].to_string(index=False))
print(f"\nSaved {V3 / 'triangulation_refresh.csv'}")
