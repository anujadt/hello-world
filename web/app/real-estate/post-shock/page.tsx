import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const dynamic = "force-static";

const DATA = path.join(process.cwd(), "public", "data", "real-estate", "post-shock");
const V35 = path.join(process.cwd(), "public", "data", "real-estate", "v3_5");

async function readCsv(name: string) {
  const raw = await fs.readFile(path.join(DATA, name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true }) as Record<string, string>[];
}

async function readV35(name: string) {
  const raw = await fs.readFile(path.join(V35, name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true }) as Record<string, string>[];
}

async function readMemo() {
  return fs.readFile(path.join(DATA, "memo.md"), "utf8");
}

function fmtAed(n: number): string {
  if (Number.isNaN(n)) return "-";
  if (n >= 1e6) return `AED ${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `AED ${(n / 1e3).toFixed(0)}k`;
  return `AED ${n.toFixed(0)}`;
}

function pct(s: string, digits = 2): string {
  const n = Number(s);
  if (Number.isNaN(n)) return "-";
  return `${n >= 0 ? "+" : ""}${n.toFixed(digits)}%`;
}

export default async function PostShockPage() {
  const [
    memo, shortlist, distress, cohort, lag, supply, irrBase, irrLead, sourcing, triRefresh,
    lagGrid, poissonCIs, cohortExcess,
  ] = await Promise.all([
    readMemo(),
    readCsv("shortlist.csv"),
    readCsv("distress.csv"),
    readCsv("cohort.csv"),
    readCsv("lag_contamination.csv"),
    readCsv("supply.csv"),
    readCsv("irr_base_matrix.csv"),
    readCsv("irr_lead_full_matrix.csv"),
    readCsv("sourcing_briefs.csv"),
    readCsv("triangulation_refresh.csv"),
    readV35("lag_sensitivity_grid.csv"),
    readV35("poisson_vol_cis.csv"),
    readV35("cohort_excess_vs_baseline.csv"),
  ]);

  // v3.5 join lookups
  const lagFor = (district: string, layout: string) =>
    lagGrid.find((r) => r.district === district && r.layout === layout && r.ptype === "apartment");
  const ciFor = (district: string, layout: string) =>
    poissonCIs.find((r) => r.district === district && r.layout === layout && r.ptype === "apartment");
  const excessFor = (district: string, project: string) =>
    cohortExcess.find((r) => r.district === district && r.project === project);
  void irrBase;
  void irrLead;
  void sourcing;
  void triRefresh;
  void lag;
  void supply;

  // Pivot the lead full IRR matrix into scenario rows x (ltv, horizon) columns.
  const ltvs = [0, 50, 70];
  const horizons = [3, 5, 7];
  const irrCell = (scenario: string, ltv: number, h: number) => {
    const row = irrLead.find(
      (r) => r.scenario === scenario && Number(r.ltv_pct) === ltv && Number(r.horizon_y) === h,
    );
    return row ? Number(row.irr_pct) : NaN;
  };

  return (
    <div className="space-y-12">
      <header>
        <div className="inline-block text-[10px] uppercase tracking-wide bg-amber-950/40 border border-amber-900/40 text-amber-300 px-2 py-0.5 rounded">
          v3, lag-corrected
        </div>
        <h1 className="text-2xl font-bold text-zinc-100 mt-2">Post-shock opportunity scan</h1>
        <p className="text-zinc-400 mt-1 text-sm max-w-3xl">
          Pivot Feb 27, 2026; effective post-event start Apr 13 after 45-day registration-lag correction.
          Bootstrap 90% CI gate on excess-change. Supply-penalized composite. Rent benchmarks adjusted
          for 12-month staleness. Ready apartments only.
        </p>
      </header>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Lag-adjusted shortlist (4 entries that survived all gates)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Filters applied: freehold zones, ready apartments, post-event n ≥ 20, regime not frozen,
          bootstrap 90% CI on excess-change does not include zero. Worst-case yield = rent -25%, vacancy +10pp.
          The two rightmost columns are v3.5 additions: lag-sensitivity tag across {"{30, 45, 60, 90}"}-day
          assumed registration lags, and 90% Poisson CI on the volume ratio (CI excluding 1.0 means the
          velocity change is statistically significant).
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Rank</th>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Layout</th>
                <th className="text-right p-2 border-b border-zinc-800">n</th>
                <th className="text-right p-2 border-b border-zinc-800">Ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">NET (adj)</th>
                <th className="text-right p-2 border-b border-zinc-800">Worst-case</th>
                <th className="text-right p-2 border-b border-zinc-800">Excess % (CI)</th>
                <th className="text-right p-2 border-b border-zinc-800">Supply x</th>
                <th className="text-left p-2 border-b border-zinc-800">Confidence</th>
                <th className="text-left p-2 border-b border-zinc-800">Lag sensitivity</th>
                <th className="text-left p-2 border-b border-zinc-800">Vol-ratio CI (90%)</th>
              </tr>
            </thead>
            <tbody>
              {shortlist.map((r, i) => {
                const frag = lagFor(r.district, r.layout);
                const ci = ciFor(r.district, r.layout);
                const fragTag = frag?.fragility ?? "n/a";
                const fragColor =
                  fragTag === "FRAGILE" ? "bg-red-950/40 border-red-900/40 text-red-300"
                  : fragTag === "wide-band" ? "bg-amber-950/40 border-amber-900/40 text-amber-300"
                  : fragTag === "stable" ? "bg-emerald-950/40 border-emerald-900/40 text-emerald-300"
                  : "bg-zinc-900 border-zinc-800 text-zinc-500";
                const ciExcludesOne = ci?.vol_ci_excludes_one === "True";
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-zinc-300">{i + 1}</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-100">{r.district}</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.layout}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.n_post_ready}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.price_med))}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-emerald-300 font-semibold">{Number(r.net_yield_adj_pct).toFixed(2)}%</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-amber-300">{Number(r.worst_case_yield).toFixed(2)}%</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                      {pct(r.excess_change_pct, 1)}{" "}
                      <span className="text-zinc-600">[{Number(r.excess_ci_lo).toFixed(1)}, {Number(r.excess_ci_hi).toFixed(1)}]</span>
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.supply_overhang_ratio).toFixed(1)}x</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.confidence}</td>
                    <td className="p-2 border-b border-zinc-900">
                      <span className={`text-[10px] uppercase tracking-wide px-2 py-0.5 rounded border ${fragColor}`}>
                        {fragTag}
                      </span>
                      {frag && (
                        <span className="text-[10px] text-zinc-500 ml-2">
                          ±{frag.px_max_swing_pp}pp swing
                        </span>
                      )}
                    </td>
                    <td className={`p-2 border-b border-zinc-900 ${ciExcludesOne ? "text-emerald-300" : "text-amber-300"}`}>
                      {ci ? (
                        <>
                          [{Number(ci.vol_ratio_ci_lo).toFixed(2)}, {Number(ci.vol_ratio_ci_hi).toFixed(2)}]
                          <span className="text-[10px] text-zinc-500 ml-2">
                            {ciExcludesOne ? "sig" : "n.s."}
                          </span>
                        </>
                      ) : "-"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Cohort dump leaderboard, where forced sellers are concentrating</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          For each 2022-2024 off-plan launch, the share of post-event off-plan transactions that are SECONDARY
          (original buyer reselling) rather than primary (developer selling). v3.5 fix: also shown is the matched
          pre-shock baseline secondary share at the same months-since-launch, and the excess over baseline.
          The 92% claim now reads as &quot;X pp above what pre-shock projects normally show at this maturity&quot;.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Project</th>
                <th className="text-right p-2 border-b border-zinc-800">Launch</th>
                <th className="text-right p-2 border-b border-zinc-800">Post-event deals</th>
                <th className="text-right p-2 border-b border-zinc-800">Secondary share</th>
                <th className="text-right p-2 border-b border-zinc-800">Matched baseline</th>
                <th className="text-right p-2 border-b border-zinc-800">Excess over baseline</th>
              </tr>
            </thead>
            <tbody>
              {cohort.slice(0, 25).map((r, i) => {
                const sec = Number(r.secondary_share_pct);
                const color = sec >= 95 ? "text-red-300" : sec >= 85 ? "text-amber-300" : "text-zinc-400";
                const excessRow = excessFor(r.district, r.project);
                const baseline = excessRow ? Number(excessRow.baseline_secondary_pct) : NaN;
                const excess = excessRow ? Number(excessRow.excess_over_baseline_pp) : NaN;
                const excessColor =
                  excess >= 60 ? "text-red-300"
                  : excess >= 30 ? "text-amber-300"
                  : excess >= 10 ? "text-zinc-200"
                  : "text-zinc-500";
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.project}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.launch_year}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.off_post_n}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${color}`}>
                      {sec.toFixed(0)}%
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">
                      {Number.isNaN(baseline) ? "-" : `${baseline.toFixed(0)}%`}
                    </td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${excessColor}`}>
                      {Number.isNaN(excess) ? "-" : `+${excess.toFixed(0)} pp`}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          Read: the 92% secondary-share claim was always going to be somewhat normal for a 2-3 year
          old off-plan launch (matched baseline is typically 20-35%). The signal is the EXCESS over
          baseline. Bloom Living Olvera (+74 pp above matched baseline) and similar are still
          materially anomalous post-shock.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Project-level distressed ready-secondary trades</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Z-score against the PROJECT&apos;s own pre-event mean (not the district mean, the v3 fix).
          Only trades printing more than 1.5 std below their own project history are flagged. Apartments only.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Date</th>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Project</th>
                <th className="text-left p-2 border-b border-zinc-800">Layout</th>
                <th className="text-right p-2 border-b border-zinc-800">Sqm</th>
                <th className="text-right p-2 border-b border-zinc-800">Price</th>
                <th className="text-right p-2 border-b border-zinc-800">psm</th>
                <th className="text-right p-2 border-b border-zinc-800">vs project mean</th>
              </tr>
            </thead>
            <tbody>
              {distress.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.date.slice(0, 10)}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300 max-w-xs truncate">{r.project}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.layout}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.sqm).toFixed(0)}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.price))}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.rate_sqm).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-red-300 font-semibold">
                    {pct(r.discount_pct, 1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Lag-correction effect by cell</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          How much the registration-lag adjustment moved each cell&apos;s excess-change read. Larger Δ
          means the raw-pivot view was more contaminated by pre-event pipeline.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Property type</th>
                <th className="text-left p-2 border-b border-zinc-800">Layout</th>
                <th className="text-right p-2 border-b border-zinc-800">Raw excess</th>
                <th className="text-right p-2 border-b border-zinc-800">Lag-adjusted</th>
                <th className="text-right p-2 border-b border-zinc-800">Δ pp</th>
              </tr>
            </thead>
            <tbody>
              {lag.slice(0, 12).map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.ptype}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.layout}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{pct(r.excess_raw_pct, 1)}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{pct(r.excess_lag_pct, 1)}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-amber-300 font-semibold">
                    {Number(r.lag_contamination_pp) >= 0 ? "+" : ""}{Number(r.lag_contamination_pp).toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Supply overhang by district</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Allocated share of the 14,444-unit Aldar/Bloom/Modon AD-city pipeline (allocated by pre-event
          off-plan share), divided by current 12-month ready stock. Lower = less future supply pressure.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-right p-2 border-b border-zinc-800">Allocated units</th>
                <th className="text-right p-2 border-b border-zinc-800">12m ready stock</th>
                <th className="text-right p-2 border-b border-zinc-800">Overhang ratio</th>
              </tr>
            </thead>
            <tbody>
              {supply
                .filter((r) => r.supply_overhang_ratio && r.supply_overhang_ratio !== "")
                .sort((a, b) => Number(b.supply_overhang_ratio) - Number(a.supply_overhang_ratio))
                .map((r, i) => {
                  const v = Number(r.supply_overhang_ratio);
                  const color = v >= 5 ? "text-red-300" : v >= 2 ? "text-amber-300" : "text-emerald-300";
                  return (
                    <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                      <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                      <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                        {Number(r.allocated_pipeline_units).toFixed(0)}
                      </td>
                      <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                        {Number(r.ready_stock_12m).toFixed(0)}
                      </td>
                      <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${color}`}>
                        {v.toFixed(1)}x
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Levered IRR, lead pick (Al Reem 2-bed)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Full scenario matrix. Mortgage 5.25% / 25y, 2% ADM + 2% agent in, 2% agent out, net rent
          grows with the scenario. Positive carry (6.08% net yield &gt; 5.25% debt) makes leverage
          accretive. Entry AED 1.77M, net rent ~AED 112k/yr.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Scenario</th>
                {ltvs.map((l) =>
                  horizons.map((h) => (
                    <th key={`${l}-${h}`} className="text-right p-2 border-b border-zinc-800">
                      LTV{l} / {h}y
                    </th>
                  )),
                )}
              </tr>
            </thead>
            <tbody>
              {["bear", "base", "bull"].map((scen) => (
                <tr key={scen} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200 capitalize">
                    {scen}
                    <span className="text-zinc-600 ml-1">
                      {scen === "bear" ? "(0%/yr)" : scen === "base" ? "(+6%/yr)" : "(+10%/yr)"}
                    </span>
                  </td>
                  {ltvs.map((l) =>
                    horizons.map((h) => {
                      const v = irrCell(scen, l, h);
                      const color =
                        v >= 15 ? "text-emerald-300" : v >= 8 ? "text-zinc-200" : "text-amber-300";
                      return (
                        <td
                          key={`${scen}-${l}-${h}`}
                          className={`p-2 border-b border-zinc-900 text-right font-semibold ${color}`}
                        >
                          {Number.isNaN(v) ? "-" : `${v.toFixed(1)}%`}
                        </td>
                      );
                    }),
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500 mt-3">
          Base-case IRR across all four shortlist cells (price +6%/yr, rent +3%/yr): each delivers
          ~10% unlevered rising to ~18% at LTV-70. Even the bear case (flat prices) stays positive on
          yield carry. Full per-cell matrix in <code className="bg-zinc-900 px-1 rounded">irr_base_matrix.csv</code>.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Off-market sourcing briefs</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          For each cohort-dump project (≥75% secondary share post-event), the detail a broker needs:
          deal count, layout-weighted psm range, ticket range, and last print date. These are the
          buildings where forced-seller inventory concentrates.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Project</th>
                <th className="text-right p-2 border-b border-zinc-800">Deals</th>
                <th className="text-right p-2 border-b border-zinc-800">2nd share</th>
                <th className="text-right p-2 border-b border-zinc-800">Median psm</th>
                <th className="text-right p-2 border-b border-zinc-800">psm p10-p90</th>
                <th className="text-right p-2 border-b border-zinc-800">Median ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Last print</th>
              </tr>
            </thead>
            <tbody>
              {sourcing.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.project}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.post_event_deals}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-amber-300">{Number(r.secondary_share_pct).toFixed(0)}%</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.median_psm).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">
                    {Number(r.psm_p10).toLocaleString(undefined, { maximumFractionDigits: 0 })}–
                    {Number(r.psm_p90).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.median_price))}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{r.last_print_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Triangulation refresh (Q1/Q2 2026 sources)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          v3 findings cross-checked against freshly published 2026 reports. Notable: my Reem psm matches
          published within 2%, and ValuStrat&apos;s 88.1% occupancy implies my 7% base vacancy is
          optimistic, so the +5pp stress case is the realistic working number.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Claim</th>
                <th className="text-left p-2 border-b border-zinc-800">My finding</th>
                <th className="text-left p-2 border-b border-zinc-800">External</th>
                <th className="text-left p-2 border-b border-zinc-800">Source</th>
                <th className="text-left p-2 border-b border-zinc-800">Variance</th>
              </tr>
            </thead>
            <tbody>
              {triRefresh.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40 align-top">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.claim}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400 max-w-xs">{r.my_finding}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400 max-w-xs">{r.external_figure}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-500">
                    <a className="hover:text-blue-300" href={r.source_url} target="_blank" rel="noreferrer">
                      {r.source}
                    </a>
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.variance}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="markdown-body">
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Full memo v3</h2>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{memo}</ReactMarkdown>
      </section>
    </div>
  );
}
