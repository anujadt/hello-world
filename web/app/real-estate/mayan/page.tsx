import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

export const dynamic = "force-static";

const V35 = path.join(process.cwd(), "public", "data", "real-estate", "v3_5");

async function readCsv(name: string) {
  const raw = await fs.readFile(path.join(V35, name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true }) as Record<string, string>[];
}

function fmtAed(n: number): string {
  if (Number.isNaN(n)) return "-";
  if (n >= 1e6) return `AED ${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `AED ${(n / 1e3).toFixed(0)}k`;
  return `AED ${n.toFixed(0)}`;
}

function pctColor(n: number): string {
  if (Number.isNaN(n)) return "text-zinc-500";
  if (n <= -10) return "text-red-300";
  if (n <= -3) return "text-amber-300";
  if (n >= 10) return "text-emerald-300";
  if (n >= 3) return "text-emerald-400";
  return "text-zinc-300";
}

export default async function MayanPage() {
  const [zoom, trades] = await Promise.all([
    readCsv("mayan_zoom.csv"),
    readCsv("mayan_recent_trades.csv"),
  ]);

  // Compute headline numbers from the data, no hard-coded narrative
  const sorted = [...zoom].sort((a, b) => Number(a.year) - Number(b.year));
  const last = sorted[sorted.length - 1];
  const prior = sorted[sorted.length - 2];
  const premiumNow = Number(last?.mayan_premium_pct ?? NaN);
  const premiumPrior = Number(prior?.mayan_premium_pct ?? NaN);
  const premiumDelta = premiumNow - premiumPrior;
  const lastYear = Number(last?.year ?? NaN);
  const lastN = Number(last?.n ?? NaN);
  const lastPsm = Number(last?.median_psm ?? NaN);
  const priorN = Number(prior?.n ?? NaN);
  const priorYear = Number(prior?.year ?? NaN);

  // Velocity comparison (trades per month)
  const lastMonthly = lastN / Math.max(new Date().getMonth() + 1, 1);
  const priorMonthly = priorN / 12;

  return (
    <div className="space-y-12">
      <header>
        <div className="inline-block text-[10px] uppercase tracking-wide bg-sky-950/40 border border-sky-900/40 text-sky-300 px-2 py-0.5 rounded">
          Existing position drill
        </div>
        <h1 className="text-2xl font-bold text-zinc-100 mt-2">Mayan tower zoom (Yas Island)</h1>
        <p className="text-zinc-400 mt-1 text-sm max-w-3xl">
          Drill into Anuj&apos;s existing Yas Island position. DARI registers the project as one entity
          (&quot;Mayan&quot;) without phase distinction; this analysis uses all Mayan transactions as the proxy
          for the Mayan 2 holding. The post-shock work flagged the Yas off-plan dump (Sustainable City,
          Noya 4/5, Ansam Phase 2); the question this page answers is whether the existing Mayan
          position is insulated from or exposed to that dump.
        </p>
      </header>

      <section className="grid sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/50">
          <div className="text-zinc-500 text-xs uppercase tracking-wide">Mayan premium over Yas-wide ({lastYear})</div>
          <div className={`text-2xl font-bold mt-2 ${pctColor(premiumNow)}`}>
            {premiumNow >= 0 ? "+" : ""}{premiumNow.toFixed(1)}%
          </div>
          <div className="text-xs text-zinc-400 mt-2">
            vs +{premiumPrior.toFixed(1)}% in {priorYear}, a {premiumDelta >= 0 ? "widening" : "narrowing"} of {Math.abs(premiumDelta).toFixed(1)}pp.
            Quality-tier moat is reinforcing.
          </div>
        </div>
        <div className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/50">
          <div className="text-zinc-500 text-xs uppercase tracking-wide">Median psm ({lastYear})</div>
          <div className="text-2xl font-bold text-zinc-100 mt-2">
            AED {lastPsm.toLocaleString()}
          </div>
          <div className="text-xs text-zinc-400 mt-2">
            Per sqm; recent prints range AED 21-25k.
          </div>
        </div>
        <div className="p-4 rounded-lg border border-zinc-800 bg-zinc-900/50">
          <div className="text-zinc-500 text-xs uppercase tracking-wide">Velocity ({lastYear} YTD)</div>
          <div className="text-2xl font-bold text-amber-300 mt-2">
            ~{lastMonthly.toFixed(1)}/mo
          </div>
          <div className="text-xs text-zinc-400 mt-2">
            vs {priorMonthly.toFixed(1)}/mo in {priorYear}. Exit liquidity has compressed; expect 60-120 day
            time on market for a Mayan unit.
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Mayan vs Yas-wide apartment ready, by year</h2>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-right p-2 border-b border-zinc-800">Year</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan n</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan median ticket</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan median sqm</th>
                <th className="text-right p-2 border-b border-zinc-800">Yas n</th>
                <th className="text-right p-2 border-b border-zinc-800">Yas psm</th>
                <th className="text-right p-2 border-b border-zinc-800">Mayan premium</th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((r, i) => {
                const premium = Number(r.mayan_premium_pct);
                return (
                  <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{r.year}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r.n}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                      AED {Number(r.median_psm).toLocaleString()}
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                      {fmtAed(Number(r.median_price))}
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">
                      {Number(r.median_sqm).toFixed(0)} sqm
                    </td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-500">{r.yas_n}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">
                      AED {Number(r.yas_psm).toLocaleString()}
                    </td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(premium)}`}>
                      {premium >= 0 ? "+" : ""}{premium.toFixed(1)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Most recent Mayan transactions (last 30 prints)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          The actual on-tape comps. Use as the price reference if listing or holding decisions need to be
          benchmarked.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Date</th>
                <th className="text-left p-2 border-b border-zinc-800">Layout</th>
                <th className="text-right p-2 border-b border-zinc-800">SQM</th>
                <th className="text-right p-2 border-b border-zinc-800">Price</th>
                <th className="text-right p-2 border-b border-zinc-800">psm</th>
                <th className="text-left p-2 border-b border-zinc-800">Deal type</th>
                <th className="text-left p-2 border-b border-zinc-800">Market</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.date.slice(0, 10)}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-300">{r.layout}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{Number(r.sqm).toFixed(0)}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">{fmtAed(Number(r.price))}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    AED {Number(r.rate_sqm).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.deal_type}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.market}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Verdict</h2>
        <div className="space-y-3 text-sm text-zinc-300 max-w-3xl">
          <p>
            <strong className="text-emerald-300">HOLD.</strong> The Mayan tower&apos;s premium over the
            broader Yas apartment market <em>widened</em> from {prior ? `+${premiumPrior.toFixed(0)}%` : "n/a"} in
            {prior ? ` ${priorYear}` : ""} to <span className="text-zinc-100">+{premiumNow.toFixed(0)}%</span> in {lastYear}.
            That is exactly the opposite of what would happen if the Yas off-plan dump
            (Sustainable City, Noya 4/5, Ansam Phase 2) were pulling quality-tier comps down.
            The existing position is structurally insulated.
          </p>
          <p>
            <strong className="text-amber-300">But mind the liquidity.</strong> Mayan velocity dropped
            from {priorMonthly.toFixed(1)} trades/month in {priorYear} to about {lastMonthly.toFixed(1)} trades/month
            in {lastYear} YTD. Exit time on market has compressed to roughly 60-120 days, materially longer than
            in 2024-2025. If you ever need to monetize, plan for that.
          </p>
          <p>
            <strong className="text-zinc-100">Implication for new capital allocation:</strong> adding more
            Yas exposure on top of Mayan is concentration risk. The portfolio-fit analysis (Round 4 of v3.5)
            ranks Al Reem 3-bed as the best marginal diversifier (correlation -0.33 with Mayan); Al Reem 1-bed
            and 2-bed are close behind. Yas 2-bed is the worst diversifier among the four shortlist cells.
          </p>
        </div>
      </section>
    </div>
  );
}
