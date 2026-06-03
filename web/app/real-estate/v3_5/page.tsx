import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

export const dynamic = "force-static";

const DATA = path.join(process.cwd(), "public", "data", "real-estate", "v3_5");

async function readCsv(name: string) {
  const raw = await fs.readFile(path.join(DATA, name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true }) as Record<string, string>[];
}

function fmtAed(n: number): string {
  if (Number.isNaN(n)) return "-";
  if (n >= 1e6) return `AED ${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `AED ${(n / 1e3).toFixed(0)}k`;
  return `AED ${n.toFixed(0)}`;
}

function pct(s: string | undefined, digits = 1): string {
  if (s === undefined || s === "" || s === "NaN" || s === "null") return "-";
  const n = Number(s);
  if (Number.isNaN(n)) return "-";
  return `${n >= 0 ? "+" : ""}${n.toFixed(digits)}%`;
}

function pctColor(s: string | undefined): string {
  if (s === undefined || s === "" || s === "NaN") return "text-zinc-500";
  const n = Number(s);
  if (Number.isNaN(n)) return "text-zinc-500";
  if (n <= -10) return "text-red-300";
  if (n <= -3) return "text-amber-300";
  if (n >= 10) return "text-emerald-300";
  if (n >= 3) return "text-emerald-400";
  return "text-zinc-300";
}

function voteColor(v: string): string {
  if (v.startsWith("INFLOW")) return "bg-emerald-950/40 border-emerald-900/40 text-emerald-300";
  if (v.startsWith("OUTFLOW")) return "bg-red-950/40 border-red-900/40 text-red-300";
  return "bg-amber-950/40 border-amber-900/40 text-amber-300";
}

export default async function V35Page() {
  const [
    drill, triggers, mayanZoom, mayanTrades, counter,
    inflow, portfolio, holm, lagGrid, cohortVsBaseline,
    yieldsHonest, irrCompare,
  ] = await Promise.all([
    readCsv("shortlist_project_drill.csv"),
    readCsv("trigger_prices.csv"),
    readCsv("mayan_zoom.csv"),
    readCsv("mayan_recent_trades.csv"),
    readCsv("counterfactual_baseline.csv"),
    readCsv("inflow_outflow_synthesis.csv"),
    readCsv("portfolio_recommendation.csv"),
    readCsv("holm_bonferroni.csv"),
    readCsv("lag_sensitivity_grid.csv"),
    readCsv("cohort_excess_vs_baseline.csv"),
    readCsv("yields_honest.csv"),
    readCsv("irr_lead_compare.csv"),
  ]);

  const _holmPasses = holm.filter((r) => r["passes_holm_at_0.10"] === "True");
  const fragileCells = lagGrid.filter((r) => r.fragility === "FRAGILE");
  const stableCells = lagGrid.filter((r) => r.fragility === "stable");
  void _holmPasses;

  return (
    <div className="space-y-12">
      <header>
        <div className="inline-block text-[10px] uppercase tracking-wide bg-purple-950/40 border border-purple-900/40 text-purple-300 px-2 py-0.5 rounded">
          v3.5 refinements
        </div>
        <h1 className="text-2xl font-bold text-zinc-100 mt-2">Four-round critical refinement of the post-shock work</h1>
        <p className="text-zinc-400 mt-1 text-sm max-w-3xl">
          Eighteen specific improvements across statistical rigor (Round 1), decision quality (Round 2),
          engineering / security (Round 3), and strategic framing (Round 4). Headline takeaways: the
          v3 shortlist survives multiple-comparison correction; the lead pick&apos;s honest yield drops
          0.4pp after fixing vacancy and mortgage assumptions; the event itself was a net-inflow event
          to AED real assets, not a distress catalyst.
        </p>
      </header>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Verdict: inflow, not outflow</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          The single biggest reframe. The Feb 27 event was treated as a shock pivot but the data says
          it was a flight-to-safety bid for AED-denominated assets. Six of eight signals vote inflow;
          two are mixed (studios + ultra-luxury Hudayriyat villas). The cohort dump is intra-market
          reallocation (off-plan exiting into ready), not aggregate distress.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Signal</th>
                <th className="text-left p-2 border-b border-zinc-800">Value</th>
                <th className="text-left p-2 border-b border-zinc-800">Interpretation</th>
                <th className="text-left p-2 border-b border-zinc-800">Vote</th>
              </tr>
            </thead>
            <tbody>
              {inflow.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.signal}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.value}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400 max-w-md">{r.interpretation}</td>
                  <td className="p-2 border-b border-zinc-900">
                    <span className={`text-[10px] uppercase tracking-wide px-2 py-0.5 rounded border ${voteColor(r.vote)}`}>
                      {r.vote}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Mayan zoom (Anuj&apos;s existing position)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          DARI registers all Mayan phases as one project. Of the 823 historical Mayan transactions in
          this dataset, 17 occurred in 2026. The Mayan tower premium over Yas-wide apartments
          <strong className="text-zinc-300"> widened from +12% in 2025 to +40% in 2026</strong>; the
          existing position is structurally insulated from the Yas off-plan dump in Sustainable City,
          Noya 4/5, and Ansam Phase 2 that the post-shock work flagged.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-right p-2 border-b border-zinc-800">Year</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan n</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan median ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Yas apartment psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan premium</th>
              </tr>
            </thead>
            <tbody>
              {mayanZoom.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{r.year}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.n}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.median_psm).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                    {fmtAed(Number(r.median_price))}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                    AED {Number(r.yas_psm).toLocaleString()}
                  </td>
                  <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r.mayan_premium_pct)}`}>
                    {pct(r.mayan_premium_pct, 1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          Read: Mayan is the quality-tier moat on Yas. The bid widened in 2026. Hold. But velocity is
          thin: 1.4 trades/month YTD 2026 vs ~5/month 2025, so exit liquidity has compressed. Time on
          market on a Mayan unit is likely 60-120 days.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Honest yields (12% vacancy, 6.25% mortgage)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          v3 used 7% vacancy and 5.25% mortgage. ValuStrat Q1 2026 occupancy implies 12% vacancy.
          CBRE quotes the 2026 UAE residential mortgage market at 6.0-6.5%. Replacing both gives the
          honest yield numbers. Lead pick (Al Reem 2-bed) net yield 6.08% → 5.70% (-0.38pp). The
          conviction story holds but with less margin.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Layout</th>
                <th className="text-right p-2 border-b border-zinc-800">Ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">v3 (7% vac) NET</th>
                <th className="text-right p-2 border-b border-zinc-800">Honest (12% vac) NET</th>
                <th className="text-right p-2 border-b border-zinc-800">Δ pp</th>
              </tr>
            </thead>
            <tbody>
              {yieldsHonest.slice(0, 15).map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.layout}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                    {fmtAed(Number(r.price_med))}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                    {Number(r.net_yield_adj_pct).toFixed(2)}%
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-emerald-300 font-semibold">
                    {Number(r.net_yield_honest_pct).toFixed(2)}%
                  </td>
                  <td className={`p-2 border-b border-zinc-900 text-right ${pctColor(r.delta_from_optimistic_pp)}`}>
                    {Number(r.delta_from_optimistic_pp).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Trigger prices per shortlist cell</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          BUY below p25 of post-event psm; WAIT inside p25-p75; SELL signal above p90.
          Backstopped by an invalidation rule that downgrades conviction if velocity collapses or
          cohort dump appears.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Cell</th>
                <th className="text-right p-2 border-b border-zinc-800">BUY psm ≤</th>
                <th className="text-right p-2 border-b border-zinc-800">BUY ticket (median sqm)</th>
                <th className="text-left p-2 border-b border-zinc-800">WAIT band psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Current psm</th>
                <th className="text-right p-2 border-b border-zinc-800">SELL signal psm ≥</th>
                <th className="text-right p-2 border-b border-zinc-800">Net yield at current</th>
              </tr>
            </thead>
            <tbody>
              {triggers.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">
                    {r.district} {r.layout}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-emerald-300 font-semibold">
                    AED {Number(r.buy_psm_max).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    {fmtAed(Number(r.buy_ticket_at_median_sqm))}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.wait_range_psm}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.current_median_psm).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-red-300 font-semibold">
                    AED {Number(r.sell_signal_psm_min).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    {Number(r.honest_net_yield_at_current_pct).toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          Invalidation rule (applies to all cells): If post-event monthly volume falls below 50% of
          pre-event pace for 2 consecutive months, OR cohort-dump signal appears for matched projects,
          OR rent index drops more than 10%, downgrade conviction by one tier.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Counterfactual baseline</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          v3 measured &quot;excess change&quot; against a short de-seasoning window. The proper baseline is the
          2024Q3-2025Q4 trajectory extrapolated forward. Negative deviation here means the segment is
          BELOW the trend line; positive means above.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District / Layout</th>
                <th className="text-right p-2 border-b border-zinc-800">Trend slope/Q</th>
                <th className="text-right p-2 border-b border-zinc-800">Projected 2026Q2</th>
                <th className="text-right p-2 border-b border-zinc-800">Actual 2026Q2</th>
                <th className="text-right p-2 border-b border-zinc-800">Deviation</th>
              </tr>
            </thead>
            <tbody>
              {counter.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">
                    {r.district} {r.layout}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                    AED {Number(r.fit_slope_aed_per_q).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.projected_2026Q2).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.actual_2026Q2).toLocaleString()}
                  </td>
                  <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r.deviation_Q2_pct)}`}>
                    {pct(r.deviation_Q2_pct, 1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          Reads more conservatively than the v3 +35% excess narrative. Yas 2-bed actual 2026Q2 is
          12.3% below trend; Reem 2-bed is 7.6% below trend. Reem 3-bed is 9.6% ABOVE trend (the
          outperformer in the shortlist).
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Portfolio fit (correlation with Mayan)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Marginal diversification benefit of each shortlist cell vs Anuj&apos;s existing Mayan position.
          Quarterly-return correlation. Lower = better diversifier. <strong className="text-zinc-300">
          Al Reem 3-bed is the BEST diversifier at -0.33 correlation (negatively correlated)</strong>;
          all four shortlist cells qualify as strong diversifiers.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Cell</th>
                <th className="text-right p-2 border-b border-zinc-800">Correlation w/ Mayan</th>
                <th className="text-left p-2 border-b border-zinc-800">Verdict</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.map((r, i) => {
                const c = Number(r.corr_with_mayan);
                const color = c < 0.0 ? "text-emerald-300" : c < 0.3 ? "text-emerald-400" : c < 0.6 ? "text-amber-300" : "text-red-300";
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-zinc-100">{r.cell}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${color}`}>
                      {c.toFixed(2)}
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.verdict}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Shortlist drill: top projects per cell</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          The shortlist names segments. This drills to specific projects with broker-actionable
          detail. Take this to brokers focused on these buildings.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Cell</th>
                <th className="text-left p-2 border-b border-zinc-800">Project</th>
                <th className="text-right p-2 border-b border-zinc-800">Deals</th>
                <th className="text-right p-2 border-b border-zinc-800">Median psm</th>
                <th className="text-right p-2 border-b border-zinc-800">psm p10-p90</th>
                <th className="text-right p-2 border-b border-zinc-800">Median ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Median sqm</th>
              </tr>
            </thead>
            <tbody>
              {drill.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.shortlist_cell}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.project}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.n_post_event}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.median_psm).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">
                    {Number(r.psm_p10).toLocaleString()}-{Number(r.psm_p90).toLocaleString()}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    {fmtAed(Number(r.median_ticket))}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.median_sqm}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Statistical-rigor diagnostics</h2>
        <div className="grid sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/50">
            <div className="text-zinc-500 text-xs uppercase tracking-wide">Holm-Bonferroni at family-wise α=0.10</div>
            <div className="text-2xl font-bold text-emerald-300 mt-2">All 4 shortlist cells PASS</div>
            <div className="text-xs text-zinc-400 mt-2">
              The multiple-comparison critique doesn&apos;t remove any picks. 36 of 53 cells significant
              after FDR control.
            </div>
          </div>
          <div className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/50">
            <div className="text-zinc-500 text-xs uppercase tracking-wide">Lag sensitivity (30/45/60/90d)</div>
            <div className="text-2xl font-bold text-zinc-100 mt-2">{stableCells.length} stable · {fragileCells.length} fragile</div>
            <div className="text-xs text-zinc-400 mt-2">
              Findings that flip sign or volume-class under any reasonable lag value are flagged.
            </div>
          </div>
          <div className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/50">
            <div className="text-zinc-500 text-xs uppercase tracking-wide">Counterfactual deviation</div>
            <div className="text-2xl font-bold text-amber-300 mt-2">Reem 2-bed -7.6%</div>
            <div className="text-xs text-zinc-400 mt-2">
              vs the 2024Q3-2025Q4 trend line. The +35% excess vs short baseline reads as -7.6% below
              the proper counterfactual. Reem 3-bed is +9.6% above trend.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
