import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export const dynamic = "force-static";

const DATA = path.join(process.cwd(), "public", "data", "real-estate", "post-shock");

async function readCsv(name: string) {
  const raw = await fs.readFile(path.join(DATA, name), "utf8");
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
  const [memo, shortlist, distress, cohort, lag, supply] = await Promise.all([
    readMemo(),
    readCsv("shortlist.csv"),
    readCsv("distress.csv"),
    readCsv("cohort.csv"),
    readCsv("lag_contamination.csv"),
    readCsv("supply.csv"),
  ]);

  return (
    <div className="space-y-12">
      <header>
        <div className="inline-block text-[10px] uppercase tracking-wide bg-amber-950/40 border border-amber-900/40 text-amber-300 px-2 py-0.5 rounded">
          v3 — lag-corrected
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
              </tr>
            </thead>
            <tbody>
              {shortlist.map((r, i) => (
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
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Cohort dump leaderboard — where forced sellers are concentrating</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          For each 2022-2024 off-plan launch, the share of post-event off-plan transactions that are SECONDARY
          (original buyer reselling) rather than primary (developer selling). Above 80% means the project is
          functionally a resale market and original investors are exiting. This is the off-market entry path.
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
              </tr>
            </thead>
            <tbody>
              {cohort.slice(0, 25).map((r, i) => {
                const sec = Number(r.secondary_share_pct);
                const color = sec >= 95 ? "text-red-300" : sec >= 85 ? "text-amber-300" : "text-zinc-400";
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                    <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.project}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.launch_year}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.off_post_n}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${color}`}>
                      {sec.toFixed(0)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
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

      <section className="markdown-body">
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Full memo v3</h2>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{memo}</ReactMarkdown>
      </section>
    </div>
  );
}
