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
  const [memo, shortlist, distress, dump] = await Promise.all([
    readMemo(),
    readCsv("shortlist.csv"),
    readCsv("distress.csv"),
    readCsv("dump.csv"),
  ]);

  return (
    <div className="space-y-12">
      <header>
        <div className="inline-block text-[10px] uppercase tracking-wide bg-amber-950/40 border border-amber-900/40 text-amber-300 px-2 py-0.5 rounded">
          New analysis
        </div>
        <h1 className="text-2xl font-bold text-zinc-100 mt-2">Post-shock opportunity scan</h1>
        <p className="text-zinc-400 mt-1 text-sm max-w-3xl">
          Pivot date Feb 27, 2026. Pre-event 12-month baseline, post-event 3.2-month window, with a same-period
          control one year prior to back out seasonality. Restricted to freehold zones and ready apartments.
        </p>
      </header>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Highest-conviction shortlist</h2>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Rank</th>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Layout</th>
                <th className="text-left p-2 border-b border-zinc-800">Tier</th>
                <th className="text-right p-2 border-b border-zinc-800">Ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Post psm</th>
                <th className="text-right p-2 border-b border-zinc-800">NET yield</th>
                <th className="text-right p-2 border-b border-zinc-800">Stress NET</th>
                <th className="text-left p-2 border-b border-zinc-800">Regime</th>
                <th className="text-left p-2 border-b border-zinc-800">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {shortlist.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{i + 1}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-100">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.layout}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.tier}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.price_med))}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.psm_post_ready))}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-emerald-300 font-semibold">{Number(r.net_yield_pct).toFixed(2)}%</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.stress_net_yield_pct).toFixed(2)}%</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.regime_class}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Off-plan dump signal by district</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Off-plan secondary share is the % of off-plan deals that are resold by their original buyer rather than
          sold by the developer. Large positive Δ = forced sellers exiting their positions, often before handover.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-right p-2 border-b border-zinc-800">Pre share</th>
                <th className="text-right p-2 border-b border-zinc-800">Post avg share</th>
                <th className="text-right p-2 border-b border-zinc-800">Δ ppt</th>
                <th className="text-right p-2 border-b border-zinc-800">Max weekly</th>
              </tr>
            </thead>
            <tbody>
              {dump.map((r, i) => {
                const delta = Number(r.dump_signal_pp);
                const color =
                  delta >= 30 ? "text-red-300" : delta >= 10 ? "text-amber-300" : delta < 0 ? "text-emerald-300" : "text-zinc-300";
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{Number(r.pre_share_pct).toFixed(1)}%</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{Number(r.avg_post_share_pct).toFixed(1)}%</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${color}`}>
                      {delta >= 0 ? "+" : ""}{delta.toFixed(1)}
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.max_post_share_pct).toFixed(0)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Distressed-trade leaderboard</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Individual ready-secondary transactions that printed more than 1.5 standard deviations below their district&apos;s
          pre-event mean. Use as the input to off-market broker conversations.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Date</th>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-left p-2 border-b border-zinc-800">Project</th>
                <th className="text-left p-2 border-b border-zinc-800">Layout</th>
                <th className="text-right p-2 border-b border-zinc-800">SQM</th>
                <th className="text-right p-2 border-b border-zinc-800">Price</th>
                <th className="text-right p-2 border-b border-zinc-800">psm</th>
                <th className="text-right p-2 border-b border-zinc-800">vs district mean</th>
              </tr>
            </thead>
            <tbody>
              {distress.slice(0, 25).map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.date.slice(0, 10)}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300 max-w-xs truncate">{r.project}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.layout}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.sqm).toFixed(0)}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.price))}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">AED {Number(r.rate_sqm).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-red-300 font-semibold">{pct(r.discount_pct, 1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="markdown-body">
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Full memo</h2>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{memo}</ReactMarkdown>
      </section>
    </div>
  );
}
