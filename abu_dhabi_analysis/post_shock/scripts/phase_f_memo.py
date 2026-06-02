"""
Phase F: assemble the post-shock memo.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

OUT = Path("/home/user/hello-world/abu_dhabi_analysis/post_shock/outputs")

regime = pd.read_csv(OUT / "regime_comparison.csv")
shortlist = pd.read_csv(OUT / "post_shock_shortlist.csv")
scorecard = pd.read_csv(OUT / "post_shock_scorecard.csv")
yields = pd.read_csv(OUT / "yield_overlay_ready.csv")
distress = pd.read_csv(OUT / "distress_flags.csv")
dump = pd.read_csv(OUT / "offplan_dump_summary.csv")

lines: list[str] = []
add = lines.append


def fmt_aed(v: float) -> str:
    if v >= 1e6: return f"AED {v/1e6:.2f}M"
    if v >= 1e3: return f"AED {v/1e3:.0f}k"
    return f"AED {v:.0f}"


add("# Abu Dhabi Post-Shock Opportunity Memo")
add("")
add("**Pivot date**: Feb 27, 2026. **Post-event window**: Feb 27, 2026 to Jun 2, 2026 (3.2 months).")
add("**Scope**: residential, freehold whitelist, ready apartments primary (yield only realizes on ready).")
add("**Data**: DARI / ADREC sales (87,655 clean transactions). Rent benchmarks: Bayut H1 2025, MPInvestments, Sands of Wealth, H2O Properties.")
add("")
add("## The headline you did not expect")
add("")
add("The Feb 27 event was supposed to dislocate prices. **It did not, in most freehold zones.** "
    "After subtracting normal Feb-Jun seasonality, headline psm in the major freehold districts is **HIGHER** "
    "than the pre-event trajectory, not lower. Volume is also up. This is not a panic; it is closer to a flight-to-safety bid. ")
add("")

reem_1b = regime[(regime["district"] == "Al Reem Island") & (regime["layout"] == "1 bed")]
yas_1b = regime[(regime["district"] == "Yas Island") & (regime["layout"] == "1 bed")]
saad_st = regime[(regime["district"] == "Al Saadiyat Island") & (regime["layout"] == "studio")]

add("Three numbers to anchor:")
add("")
if len(reem_1b):
    r = reem_1b.iloc[0]
    add(f"- **Al Reem 1-bed apartments**: post-event psm AED {r['psm_post']:,.0f}, "
        f"excess (de-seasoned) change **{r['excess_change_pct']:+.1f}%**, volume {r['vol_change_ratio']:.1f}x prior pace, "
        f"regime = **{r['regime_class']}**.")
if len(yas_1b):
    r = yas_1b.iloc[0]
    add(f"- **Yas Island 1-bed apartments**: post-event psm AED {r['psm_post']:,.0f}, "
        f"excess change **{r['excess_change_pct']:+.1f}%**, volume {r['vol_change_ratio']:.1f}x prior pace, "
        f"regime = **{r['regime_class']}**.")
if len(saad_st):
    r = saad_st.iloc[0]
    add(f"- **Saadiyat studios**: post-event psm AED {r['psm_post']:,.0f}, "
        f"excess change **{r['excess_change_pct']:+.1f}%**, volume {r['vol_change_ratio']:.1f}x prior pace, "
        f"regime = **{r['regime_class']}** (the one segment that did show real dislocation).")
add("")
add("Where the shock IS visible is in the **off-plan secondary share**: investors caught off-plan "
    "in Al Shamkha, Zayed City, Saadiyat, and Yas are quietly reselling their positions, often before handover. "
    "Ready-market clearing prices held; off-plan inventory got dumped to the next buyer at undisclosed discounts. "
    "This is the asymmetric opportunity, but it lives off-tape.")
add("")
add("## Off-plan dump signal by district (post-event vs pre-event baseline)")
add("")
add("| District | Pre-event off-plan secondary share | Post-event average | Δ ppt |")
add("|---|---|---|---|")
for _, r in dump.iterrows():
    add(f"| {r['district']} | {r['pre_share_pct']:.1f}% | {r['avg_post_share_pct']:.1f}% | "
        f"**{r['dump_signal_pp']:+.1f}** |")
add("")
add("Read: Al Shamkha and Zayed City show the largest forced-seller flows. The implication is **off-market deals "
    "below sticker** if you can reach the right brokers. Al Reem and Al Raha Beach are NOT showing dump signal; "
    "owners are holding.")
add("")
add("## Top yield-led opportunities, post-event ready entries")
add("")
add("Restricted to freehold zones, ready apartments, post-event volume gate (≥30 deals in the 3.2-month window). ")
add("Net yield uses Bayut/Sands of Wealth gross yields minus 7% vacancy minus tier-based service charge "
    "(AED 12/18/28 per sqft for affordable/mid/luxury), divided by all-in entry (price plus 2% ADM transfer plus 2% agent).")
add("")
add("| Rank | District | Layout | Tier | Post psm | Median ticket | NET yield | Stress NET (-15% rent) | Regime | Confidence |")
add("|---|---|---|---|---|---|---|---|---|---|")
for i, r in shortlist.iterrows():
    add(f"| {i+1} | {r['district']} | {r['layout']} | {r['tier']} | "
        f"AED {r['psm_post_ready']:,.0f} | {fmt_aed(r['price_med'])} | "
        f"**{r['net_yield_pct']:.2f}%** | {r['stress_net_yield_pct']:.2f}% | "
        f"{r['regime_class']} | {r['confidence']} |")
add("")

add("## Highest-conviction call, in one paragraph")
add("")
add("**Al Reem Island affordable apartments (studio / 1-bed / 2-bed) are the highest-conviction post-event entry.** "
    "All three of these segments score above 70 on the composite, deliver NET yields of 5.4% to 6.0% on all-in entry, "
    "hold above 4.4% NET even under a 15% rent stress, and have transacted **800+ deals in the post-event window**. "
    "The off-plan dump signal in Reem is **negative** (forced sellers are NOT exiting Reem), meaning the ready market "
    "has the bid. Median 1-bed ticket sits at AED 1.20M; studios at AED 567k. Liquidity is the deepest in the entire "
    "freehold dataset. The downside risk is the 14,444-unit Aldar+Bloom+Modon AD-city pipeline announced pre-event, "
    "which still threatens to compress ready psm 2027-29 if delivery accelerates without matching demand. Buy ready, "
    "not off-plan, to insulate from that.")
add("")

add("## Distressed-trade leaderboard (off-market hunting list)")
add("")
add("These are individual READY-SECONDARY transactions in the post-event window that printed more than 1.5 std below the district's pre-event mean. They are the realised discounts.")
add("")
add("| Date | District | Project | Layout | Sqm | Price | psm | District mean psm | Discount |")
add("|---|---|---|---|---|---|---|---|---|")
for _, r in distress.head(12).iterrows():
    add(f"| {r['date'][:10]} | {r['district']} | {r['project'][:30]} | {r['layout']} | "
        f"{r['sqm']:.0f} | {fmt_aed(r['price'])} | AED {r['rate_sqm']:,.0f} | "
        f"AED {r['ref_mean']:,.0f} | **{r['discount_pct']:.1f}%** |")
add("")
add("Use this as the input to off-market broker conversations. Even if these specific units are gone, "
    "comparable inventory in those projects is likely on offer at similar discounts.")
add("")

add("## What I would NOT chase")
add("")

frozen = scorecard[scorecard["regime_class"] == "frozen"] if "regime_class" in scorecard.columns else pd.DataFrame()
struct = scorecard[scorecard["regime_class"] == "structural decline"] if "regime_class" in scorecard.columns else pd.DataFrame()

add("- **Saadiyat 2-bed luxury**: NET yield collapsed to 1.15% per Sands of Wealth (heavy service charges). "
    "Trophy capital play only, not income. Excess change +49% suggests it has already rerated.")
add("- **Al Jubail 4-bed villas**: NET yield 3.1% on AED 9.5M entry. Thin market (7 deals). Capital intensive without yield support.")
add("- **Yas off-plan** specifically: the off-plan secondary share is up to 37% post-event vs 13% pre. "
    "Avoid off-plan launches in Yas right now; wait for handover discount cycle to surface.")
add("- **Al Shamkha villa plots**: even with the highest dump signal (+61pp off-plan secondary share), "
    "the product is plots not ready stock. No rent yield. Pure land speculation.")
add("")

add("## Caveats")
add("")
add("1. **Three-month sample**. Post-event window is 3.2 months. Single-cell medians on n<50 carry wide confidence bands. "
    "Shortlist entries below 50 deals are marked 'medium' or 'low' confidence.")
add("2. **Rents are pre-event benchmarks**. Bayut and Sands of Wealth published rent indices for 2025 H1, before Feb 27. "
    "Post-event rent path is unknown. The stress test at -15% rent is the discipline anchor; do not lean on the current-rent number alone.")
add("3. **Seasonality control**. The de-seasoning subtracts the same Feb-Jun period one year prior. "
    "If 2025 Feb-Jun was itself unusual, the excess change is biased.")
add("4. **Off-plan dump prices are off-tape**. The shortlist uses on-tape ready medians. Actual off-market off-plan resale prices "
    "are NOT in the DARI export and are likely 5 to 15% below registered prices in distressed deals.")
add("5. **Forward supply overhang**. The Aldar+Bloom+Modon 14,444-unit AD-city pipeline announced pre-event will land 2026-29. "
    "Even resilient segments could face price pressure if delivery accelerates. Phase 3 supply-pressure trajectory is the watchlist.")
add("6. **Freehold-only**. Khalifa City has selective freehold projects; Al Reef, Yas, Saadiyat, Reem, Raha Beach, Hudayriyat, "
    "Jubail, Fahid are confirmed freehold. Anything outside the whitelist not in scope.")
add("")

text = "\n".join(lines)
assert "—" not in text, "Em dash detected"
(OUT / "post_shock_memo.md").write_text(text, encoding="utf-8")
print(f"Saved {OUT / 'post_shock_memo.md'} ({len(text):,} chars)")
