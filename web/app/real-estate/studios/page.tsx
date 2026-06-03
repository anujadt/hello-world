import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

export const dynamic = "force-static";

const DATA = path.join(process.cwd(), "public", "data", "real-estate", "studio_v2");

async function readCsv(name: string) {
  const raw = await fs.readFile(path.join(DATA, name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true }) as Record<string, string>[];
}

const MONTH = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function fmtAed(n: number | undefined | null): string {
  if (n === undefined || n === null || Number.isNaN(Number(n))) return "-";
  const x = Number(n);
  if (x >= 1e6) return `AED ${(x / 1e6).toFixed(2)}M`;
  if (x >= 1e3) return `AED ${(x / 1e3).toFixed(0)}k`;
  return `AED ${x.toFixed(0)}`;
}
function fmtNum(s: string | number | undefined | null, d = 0): string {
  if (s === undefined || s === null || s === "" || s === "NaN") return "-";
  const n = Number(s);
  if (Number.isNaN(n)) return "-";
  return n.toLocaleString(undefined, { maximumFractionDigits: d, minimumFractionDigits: d });
}
function fmtPct(s: string | number | undefined | null, d = 1): string {
  if (s === undefined || s === null || s === "" || s === "NaN") return "-";
  const n = Number(s);
  if (Number.isNaN(n)) return "-";
  return `${n >= 0 ? "+" : ""}${n.toFixed(d)}%`;
}
function pctColor(s: string | number | undefined | null, scale = 1): string {
  if (s === undefined || s === null || s === "" || s === "NaN") return "text-zinc-500";
  const n = Number(s);
  if (Number.isNaN(n)) return "text-zinc-500";
  if (n <= -30 * scale) return "text-red-300";
  if (n <= -10 * scale) return "text-amber-300";
  if (n >= 30 * scale) return "text-emerald-300";
  if (n >= 10 * scale) return "text-emerald-400";
  return "text-zinc-300";
}
function verdictTile(d: string) {
  if (d.startsWith("HOLD") || d === "Selective, not broad") return "border-amber-900/40 bg-amber-950/30 text-amber-300";
  if (d.startsWith("SELL")) return "border-red-900/40 bg-red-950/30 text-red-300";
  if (d === "Masdar City" || d.includes("Watch")) return "border-sky-900/40 bg-sky-950/30 text-sky-300";
  return "border-emerald-900/40 bg-emerald-950/30 text-emerald-300";
}

export default async function StudiosPage() {
  const [matrix, ytd, comp, hubYtd, overhang, yields, projects, mayan, mayanTrades, scorecard, verdicts, caveats] =
    await Promise.all([
      readCsv("citywide_month_matrix.csv"),
      readCsv("citywide_jan_may_ytd.csv"),
      readCsv("citywide_composition.csv"),
      readCsv("hub_jan_may_ytd.csv"),
      readCsv("hub_supply_overhang.csv"),
      readCsv("hub_yields.csv"),
      readCsv("hub_top_projects.csv"),
      readCsv("mayan_vs_yas_studio.csv"),
      readCsv("mayan_recent_trades.csv"),
      readCsv("d2_hub_scorecard.csv"),
      readCsv("verdicts.csv"),
      readCsv("caveats.csv"),
    ]);

  const hubs = Array.from(new Set(hubYtd.map((r) => r.district)));
  const d1 = verdicts.find((v) => v.decision.startsWith("D1"))!;
  const d2 = verdicts.find((v) => v.decision.startsWith("D2"))!;
  const d3 = verdicts.find((v) => v.decision.startsWith("D3"))!;
  const d4 = verdicts.find((v) => v.decision.startsWith("D4"))!;

  const mayMatrix = matrix.find((r) => Number(r.month) === 5);
  const ytd2025 = ytd.find((r) => r.year === "2025");
  const ytd2026 = ytd.find((r) => r.year === "2026");

  return (
    <div className="space-y-12">
      <header>
        <div className="inline-block text-[10px] uppercase tracking-wide bg-sky-950/40 border border-sky-900/40 text-sky-300 px-2 py-0.5 rounded">
          Decision-oriented · post-war reality
        </div>
        <h1 className="text-2xl font-bold text-zinc-100 mt-2">Ready studios: what changed, where to buy, when, and what to do with Mayan</h1>
        <p className="text-zinc-400 mt-1 text-sm max-w-3xl">
          The previous YoY-blended view conflated seasonality, trend, and shock. This rebuild
          separates them. The spine is the same-month matrix Jan-May across 2023-26 with a
          trend-extrapolated seasonal normal for each month, so 2026&apos;s &quot;new reality&quot; is
          the deviation from where the trend said the market should be. Lag = ~45 days, so May 2026
          is the first registration month dominated by deals agreed AFTER Feb 27. Scope: ready
          studios, six freehold studio hubs (Al Reem, Yas, Al Maryah, Al Saadiyat, Masdar, Khalifa).
        </p>
      </header>

      {/* Verdict tiles */}
      <section className="grid sm:grid-cols-4 gap-3">
        {[d1, d2, d3, d4].map((v) => (
          <div key={v.decision} className={`p-4 rounded-lg border ${verdictTile(v.verdict)}`}>
            <div className="text-[10px] uppercase tracking-wide text-zinc-500">{v.decision}</div>
            <div className="text-lg font-bold mt-1">{v.verdict}</div>
            <div className="text-xs text-zinc-400 mt-2 leading-relaxed">{v.rationale}</div>
          </div>
        ))}
      </section>

      {/* The Spine: month matrix with deviation */}
      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">The spine: same-month matrix with seasonal-trend deviation</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          For each calendar month, the trend-extrapolated normal is the linear projection of
          2023→2024→2025 values forward to 2026. The deviation column = (actual 2026 / projected
          2026 − 1). It strips seasonality and the trend, leaving only what 2026 itself did differently.
          May is the only month dominated by post-war deals.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800" rowSpan={2}>Month</th>
                <th className="text-right p-2 border-b border-zinc-800" colSpan={6}>Transaction count</th>
                <th className="text-right p-2 border-b border-zinc-800" colSpan={6}>Median psm (AED)</th>
              </tr>
              <tr>
                <th className="text-right p-2 border-b border-zinc-800">23</th>
                <th className="text-right p-2 border-b border-zinc-800">24</th>
                <th className="text-right p-2 border-b border-zinc-800">25</th>
                <th className="text-right p-2 border-b border-zinc-800">26</th>
                <th className="text-right p-2 border-b border-zinc-800 text-zinc-500">trend</th>
                <th className="text-right p-2 border-b border-zinc-800">dev %</th>
                <th className="text-right p-2 border-b border-zinc-800">23</th>
                <th className="text-right p-2 border-b border-zinc-800">24</th>
                <th className="text-right p-2 border-b border-zinc-800">25</th>
                <th className="text-right p-2 border-b border-zinc-800">26</th>
                <th className="text-right p-2 border-b border-zinc-800 text-zinc-500">trend</th>
                <th className="text-right p-2 border-b border-zinc-800">dev %</th>
              </tr>
            </thead>
            <tbody>
              {matrix.map((r, i) => {
                const isMay = Number(r.month) === 5;
                return (
                  <tr key={i} className={`${isMay ? "bg-sky-950/30" : "odd:bg-zinc-950 even:bg-zinc-900/40"}`}>
                    <td className="p-2 border-b border-zinc-900 text-zinc-100 font-medium">{MONTH[Number(r.month)]} {isMay && <span className="text-[9px] text-sky-400 ml-1">post-war</span>}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.count_2023}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.count_2024}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.count_2025}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-100 font-semibold">{r.count_2026_actual}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{fmtNum(r.count_2026_seasonal_trend, 0)}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r.count_deviation_pct)}`}>
                      {fmtPct(r.count_deviation_pct, 0)}
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{fmtNum(r.psm_2023, 0)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{fmtNum(r.psm_2024, 0)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{fmtNum(r.psm_2025, 0)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-100 font-semibold">{fmtNum(r.psm_2026_actual, 0)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{fmtNum(r.psm_2026_seasonal_trend, 0)}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r.psm_deviation_pct)}`}>
                      {fmtPct(r.psm_deviation_pct, 0)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          Reading it: <strong className="text-zinc-300">May 2026 count is {fmtPct(mayMatrix?.count_deviation_pct, 0)} vs the
          seasonal-trend normal</strong> (i.e. ~{Math.abs(Math.round(Number(mayMatrix?.count_deviation_pct ?? 0)))}% fewer
          studios cleared than the 2023-25 trajectory said they should), while
          median psm is <strong className="text-zinc-300">{fmtPct(mayMatrix?.psm_deviation_pct, 0)} above trend</strong>.
          That is the textbook seller-anchored, buyer-on-strike fingerprint: sellers are still pricing
          off Jan-Apr prints; buyers paused once the new regime became visible.
        </p>
      </section>

      {/* Jan-May YTD */}
      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Jan-May YTD aggregate (same window every year)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Same-window comparison using ALL 2026 data we have. Dispersion = p75 − p25 of median psm.
          Wider dispersion = more uncertainty = more negotiating room for a buyer.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-right p-2 border-b border-zinc-800">Year</th>
                <th className="text-right p-2 border-b border-zinc-800">Total n</th>
                <th className="text-right p-2 border-b border-zinc-800">Monthly avg</th>
                <th className="text-right p-2 border-b border-zinc-800">Median psm</th>
                <th className="text-right p-2 border-b border-zinc-800">p25-p75</th>
                <th className="text-right p-2 border-b border-zinc-800">Dispersion (pp)</th>
                <th className="text-right p-2 border-b border-zinc-800">Median ticket</th>
              </tr>
            </thead>
            <tbody>
              {ytd.map((r, i) => {
                const is26 = r.year === "2026";
                return (
                  <tr key={i} className={is26 ? "bg-sky-950/30" : "odd:bg-zinc-950 even:bg-zinc-900/40"}>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-100 font-medium">{r.year}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{r.n}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.monthly_avg_n}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">AED {fmtNum(r.median_psm)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{fmtNum(r.p25_psm)} – {fmtNum(r.p75_psm)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{fmtNum(r.dispersion_pp)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{fmtAed(Number(r.median_ticket))}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {ytd2026 && ytd2025 && (
          <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
            Compared to Jan-May 2025: count is { (Number(ytd2026.n) / Number(ytd2025.n) - 1 >= 0 ? "+" : "") }{((Number(ytd2026.n) / Number(ytd2025.n) - 1) * 100).toFixed(0)}%
            and median psm is { (Number(ytd2026.median_psm) / Number(ytd2025.median_psm) - 1 >= 0 ? "+" : "") }{((Number(ytd2026.median_psm) / Number(ytd2025.median_psm) - 1) * 100).toFixed(0)}%.
            Dispersion {Number(ytd2026.dispersion_pp) > Number(ytd2025.dispersion_pp) ? "WIDENED" : "narrowed"}
            ({fmtNum(ytd2025.dispersion_pp)} → {fmtNum(ytd2026.dispersion_pp)}); the wider the band, the more variance between
            asking prices, the more room to negotiate.
          </p>
        )}
      </section>

      {/* D1: Buy at all? + composition */}
      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">D1: Should you buy a studio at all right now?</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Studios are a yield play, not appreciation. The thesis lives or dies on the net yield level and
          the supply pipeline that caps future rent. Below: forward-supply read from the off-plan vs ready
          mix, then the supply overhang by hub.
        </p>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-semibold text-zinc-200 mb-2">Within-studio composition, Jan-May by year</h3>
            <div className="overflow-x-auto border border-zinc-800 rounded-lg">
              <table className="w-full text-xs">
                <thead className="bg-zinc-900 text-zinc-300">
                  <tr>
                    <th className="text-right p-2 border-b border-zinc-800">Year</th>
                    <th className="text-right p-2 border-b border-zinc-800">n</th>
                    <th className="text-right p-2 border-b border-zinc-800">Ready %</th>
                    <th className="text-right p-2 border-b border-zinc-800">Off-plan %</th>
                    <th className="text-right p-2 border-b border-zinc-800">2ndary %</th>
                  </tr>
                </thead>
                <tbody>
                  {comp.map((r, i) => (
                    <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                      <td className="p-2 border-b border-zinc-900 text-right text-zinc-100">{r.year}</td>
                      <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.n}</td>
                      <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtPct(r.ready_pct, 0)}</td>
                      <td className="p-2 border-b border-zinc-900 text-right text-amber-300">{fmtPct(r.offplan_pct, 0)}</td>
                      <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{fmtPct(r.secondary_pct, 0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-zinc-200 mb-2">Forward-supply overhang per hub</h3>
            <p className="text-xs text-zinc-500 mb-2">Off-plan studio sales (last 12m) / Ready studio sales (last 12m). Higher = more future inventory still to hand over.</p>
            <div className="overflow-x-auto border border-zinc-800 rounded-lg">
              <table className="w-full text-xs">
                <thead className="bg-zinc-900 text-zinc-300">
                  <tr>
                    <th className="text-left p-2 border-b border-zinc-800">Hub</th>
                    <th className="text-right p-2 border-b border-zinc-800">Off-plan 12m</th>
                    <th className="text-right p-2 border-b border-zinc-800">Ready 12m</th>
                    <th className="text-right p-2 border-b border-zinc-800">Overhang</th>
                  </tr>
                </thead>
                <tbody>
                  {overhang.map((r, i) => {
                    const v = Number(r.supply_overhang_ratio);
                    const color = v >= 8 ? "text-red-300" : v >= 3 ? "text-amber-300" : "text-emerald-300";
                    return (
                      <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                        <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                        <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.offplan_studio_sales_12m}</td>
                        <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.ready_studio_sales_12m}</td>
                        <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${color}`}>{v.toFixed(2)}x</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          The studio market is fundamentally split. <strong className="text-zinc-300">Yas (11.4x) and Reem (8.8x) have huge off-plan pipelines</strong>
          still to land, which will pressure rent in 2027-28. <strong className="text-emerald-300">Masdar has effectively zero overhang</strong> (existing stock came on in
          2025; no fresh off-plan pipeline). That is the headline asymmetry behind D2.
        </p>
      </section>

      {/* D2: Where? Hub scorecard + projects */}
      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">D2: Where? Hub scorecard + specific projects</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Composite weights: net yield 35%, velocity trend (2026 monthly avg / 2025 monthly avg) 30%,
          supply risk inverse 20%, 2026 absolute volume 15%. Net yield uses 12% vacancy (the ValuStrat-implied
          actual), tier service charges, and rent benchmarks adjusted +11-15% for rent growth since H1 2025.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Rank</th>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-right p-2 border-b border-zinc-800">Net yield</th>
                <th className="text-right p-2 border-b border-zinc-800">2026 vel/mo</th>
                <th className="text-right p-2 border-b border-zinc-800">vs 2025</th>
                <th className="text-right p-2 border-b border-zinc-800">Overhang</th>
                <th className="text-right p-2 border-b border-zinc-800">Composite</th>
              </tr>
            </thead>
            <tbody>
              {scorecard.map((r, i) => (
                <tr key={i} className={i === 0 ? "bg-emerald-950/20 odd:bg-emerald-950/30" : "odd:bg-zinc-950 even:bg-zinc-900/40"}>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{i + 1}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-100 font-medium">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-emerald-300 font-semibold">{r.net_yield_pct ? `${Number(r.net_yield_pct).toFixed(2)}%` : "-"}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{r.monthly_velocity_2026}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.velocity_vs_2025).toFixed(2)}x</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.supply_overhang).toFixed(1)}x</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-100 font-bold">{Number(r.composite).toFixed(0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h3 className="text-sm font-semibold text-zinc-200 mt-6 mb-2">Top ready-studio projects per hub (post-Apr-13 2026)</h3>
        <p className="text-xs text-zinc-500 mb-2">Broker-callable list. n is the post-lag-pivot transaction count. Targets in the top hub are bolded.</p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Project</th>
                <th className="text-right p-2 border-b border-zinc-800">n</th>
                <th className="text-right p-2 border-b border-zinc-800">Median psm</th>
                <th className="text-right p-2 border-b border-zinc-800">psm p10–p90</th>
                <th className="text-right p-2 border-b border-zinc-800">Median ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Median sqm</th>
                <th className="text-left p-2 border-b border-zinc-800">Last print</th>
              </tr>
            </thead>
            <tbody>
              {projects.map((r, i) => {
                const topHub = r.district === scorecard[0]?.district;
                return (
                  <tr key={i} className={`${topHub ? "bg-emerald-950/15" : ""} odd:bg-zinc-950 even:bg-zinc-900/40`}>
                    <td className={`p-2 border-b border-zinc-900 ${topHub ? "text-emerald-300 font-medium" : "text-zinc-200"}`}>{r.district}</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.project}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.n}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">AED {fmtNum(r.median_psm)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{fmtNum(r.psm_p10)} – {fmtNum(r.psm_p90)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.median_ticket))}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.median_sqm}</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-500">{r.last_print}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* D3: When? deviation trajectory + trigger */}
      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">D3: When? Deviation trajectory + entry trigger</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          The shock is propagating monthly. Until the May reading stops deteriorating, this is a
          falling knife on volume even with prices firm. Explicit entry trigger below.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg mb-4">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Month 2026</th>
                <th className="text-left p-2 border-b border-zinc-800">Deals were agreed in</th>
                <th className="text-left p-2 border-b border-zinc-800">Regime</th>
                <th className="text-right p-2 border-b border-zinc-800">Count dev vs trend</th>
                <th className="text-right p-2 border-b border-zinc-800">Psm dev vs trend</th>
              </tr>
            </thead>
            <tbody>
              {matrix.map((r, i) => {
                const m = Number(r.month);
                const agreed = ["", "Nov-Dec '25", "Dec-Jan", "mid-Jan to mid-Feb", "mid-Feb to mid-Mar", "mid-Mar to mid-Apr"];
                const regime = ["", "pre-war", "pre-war", "mostly pre-war", "straddles Feb 27", "first clean post-war"];
                const regColor = m === 5 ? "text-sky-300" : m === 4 ? "text-amber-300" : "text-zinc-400";
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-zinc-200">{MONTH[m]}</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-400">{agreed[m]}</td>
                    <td className={`p-2 border-b border-zinc-900 ${regColor}`}>{regime[m]}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r.count_deviation_pct)}`}>{fmtPct(r.count_deviation_pct, 0)}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r.psm_deviation_pct)}`}>{fmtPct(r.psm_deviation_pct, 0)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="p-4 rounded-lg border border-amber-900/40 bg-amber-950/20">
          <div className="text-xs text-amber-300 uppercase tracking-wide font-semibold">Entry trigger</div>
          <div className="text-sm text-zinc-200 mt-2 leading-relaxed">
            Wait for <strong>two consecutive months</strong> where the citywide ready-studio count deviation
            stops getting more negative (i.e. June or July 2026 reading less negative than May&apos;s
            {" "}{fmtPct(mayMatrix?.count_deviation_pct, 0)}). AND your target hub&apos;s monthly velocity
            recovers above 4 (Masdar already qualifies; Reem and Yas do not on velocity per month).
            Until those clear, only source off-market: sticker prices reflect the seller-anchor, not the
            clearing level.
          </div>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          What will move things: the next two months of registrations (which reflect June and early-July
          deals) tell you whether buyer activity is recovering or the demand vacuum is structural. A
          rebound to count-deviation around -20% would be the floor signal. A fall below -80% would
          force sellers to mark.
        </p>
      </section>

      {/* D4: Sell Mayan? */}
      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">D4: Sell your Mayan studio?</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Mayan studio premium over Yas-wide studio psm has gone parabolic on a tiny sample (3 trades in 2026).
          That paper mark is real but exit liquidity is essentially frozen.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-right p-2 border-b border-zinc-800">Year</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan n</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Yas-wide n</th>
                <th className="text-right p-2 border-b border-zinc-800">Yas-wide psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan premium</th>
              </tr>
            </thead>
            <tbody>
              {mayan.map((r, i) => {
                const prem = Number(r.mayan_premium_pct);
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-200">{r.year}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.n}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">AED {fmtNum(r.median_psm)}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{fmtAed(Number(r.median_price))}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{r.yas_n}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">AED {fmtNum(r.yas_psm)}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(prem * 0.5)}`}>
                      {fmtPct(r.mayan_premium_pct, 0)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <h3 className="text-sm font-semibold text-zinc-200 mt-6 mb-2">Recent Mayan ready-studio trades (last 10)</h3>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Date</th>
                <th className="text-right p-2 border-b border-zinc-800">sqm</th>
                <th className="text-right p-2 border-b border-zinc-800">Price</th>
                <th className="text-right p-2 border-b border-zinc-800">psm</th>
                <th className="text-left p-2 border-b border-zinc-800">Market</th>
              </tr>
            </thead>
            <tbody>
              {mayanTrades.slice(0, 10).map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.date}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.sqm).toFixed(0)}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.price))}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">AED {Number(r.rate_sqm).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.market}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="p-4 rounded-lg border border-amber-900/40 bg-amber-950/20 mt-4">
          <div className="text-xs text-amber-300 uppercase tracking-wide font-semibold">Mayan-specific call</div>
          <div className="text-sm text-zinc-200 mt-2 leading-relaxed">
            <strong>HOLD with conditions.</strong> The 2026 sample of 3 trades shows AED 21.9k, 30.3k, and 34.6k per sqm:
            real prints, but a thin sample anchored by two buyers willing to pay extreme premiums in a frozen
            market. The mark is rich and the bid for a Mayan studio is genuinely there at AED 1.4–1.7M ticket.
            Action: <strong>list at AED 30k/sqm (or roughly p75 of your unit&apos;s size band) for a
            6-month off-market window</strong>. If a serious buyer surfaces at that level, sell and redeploy.
            If no bite, hold for the yield: Yas net yield is still 6.4% on the honest assumptions, and the
            Mayan premium is the moat. Do NOT chase the bid down; the next-best D2 alternative
            (<strong>{scorecard[0]?.district}</strong>) requires a fresh AED ~570-700k of capital, not a Mayan exit.
          </div>
        </div>
      </section>

      {/* All hub Jan-May trajectory */}
      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Per-hub Jan-May YTD trajectory (the full picture)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Same-window aggregate per hub per year so you can see who is rising, flat, or thinning out.
          Single-digit-thin cells are flagged so you do not over-interpret.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-right p-2 border-b border-zinc-800">Year</th>
                <th className="text-right p-2 border-b border-zinc-800">n</th>
                <th className="text-right p-2 border-b border-zinc-800">Monthly avg</th>
                <th className="text-right p-2 border-b border-zinc-800">Median psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Median ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Median sqm</th>
              </tr>
            </thead>
            <tbody>
              {hubs.map((h) => hubYtd.filter((r) => r.district === h).map((r, i) => {
                const thin = Number(r.n) < 10;
                const is2026 = r.year === "2026";
                return (
                  <tr key={`${h}-${r.year}`} className={`${is2026 ? "bg-sky-950/20" : ""} ${i === 0 ? "border-t-2 border-zinc-800" : ""} odd:bg-zinc-950 even:bg-zinc-900/40`}>
                    <td className="p-2 border-b border-zinc-900 text-zinc-200">{i === 0 ? h : ""}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{r.year}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-100 font-medium">
                      {r.n}
                      {thin && <span className="text-[9px] text-amber-400 ml-1">thin</span>}
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.monthly_avg}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{r.median_psm ? `AED ${fmtNum(r.median_psm)}` : "-"}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.median_ticket ? fmtAed(Number(r.median_ticket)) : "-"}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{r.median_sqm ?? "-"}</td>
                  </tr>
                );
              }))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-semibold text-zinc-200 mb-2">Caveats</h3>
        <ul className="text-xs text-zinc-500 list-disc pl-5 max-w-3xl space-y-1">
          {caveats.map((r, i) => <li key={i}>{r.caveat}</li>)}
        </ul>
      </section>
    </div>
  );
}
