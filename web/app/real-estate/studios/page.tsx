import { promises as fs } from "node:fs";
import path from "node:path";
import { parse } from "csv-parse/sync";

export const dynamic = "force-static";

const DATA = path.join(process.cwd(), "public", "data", "real-estate", "studios");

async function readCsv(name: string) {
  const raw = await fs.readFile(path.join(DATA, name), "utf8");
  return parse(raw, { columns: true, skip_empty_lines: true }) as Record<string, string>[];
}

function fmtPct(s: string | undefined, digits = 0): string {
  if (s === undefined || s === "" || s === "NaN") return "-";
  const n = Number(s);
  if (Number.isNaN(n)) return "-";
  return `${n >= 0 ? "+" : ""}${n.toFixed(digits)}%`;
}

function pctColor(s: string | undefined): string {
  if (s === undefined || s === "" || s === "NaN") return "text-zinc-500";
  const n = Number(s);
  if (Number.isNaN(n)) return "text-zinc-500";
  if (n <= -30) return "text-red-300";
  if (n <= -10) return "text-amber-300";
  if (n >= 30) return "text-emerald-300";
  if (n >= 10) return "text-emerald-400";
  return "text-zinc-300";
}

function trendColor(t: string): string {
  switch (t) {
    case "sustained decline":
    case "down from peak":
      return "bg-red-950/40 border-red-900/40 text-red-300";
    case "sustained rise":
    case "rising / at peak":
      return "bg-emerald-950/40 border-emerald-900/40 text-emerald-300";
    case "mixed":
      return "bg-amber-950/40 border-amber-900/40 text-amber-300";
    default:
      return "bg-zinc-900 border-zinc-800 text-zinc-400";
  }
}

export default async function StudiosPage() {
  const [citywide, byDistrict, priceTrend] = await Promise.all([
    readCsv("studio_yoy_citywide.csv"),
    readCsv("studio_yoy_by_district.csv"),
    readCsv("studio_yoy_price.csv"),
  ]);

  const aprMay = citywide.filter((r) => r.window === "Apr+May");
  const aprOnly = citywide.filter((r) => r.window === "April only");
  const mayOnly = citywide.filter((r) => r.window === "May only");

  return (
    <div className="space-y-12">
      <header>
        <div className="inline-block text-[10px] uppercase tracking-wide bg-sky-950/40 border border-sky-900/40 text-sky-300 px-2 py-0.5 rounded">
          Focused cut
        </div>
        <h1 className="text-2xl font-bold text-zinc-100 mt-2">Ready-studio velocity, YoY (2023+)</h1>
        <p className="text-zinc-400 mt-1 text-sm max-w-3xl">
          Are ready studios selling slower year-over-year? Scope: residential, layout = studio,
          deal_type = ready, 2023 onward, registration-date basis (DARI Sale Application Date).
          April-May 2026 registrations approximately correspond to deals agreed late-February to
          mid-April 2026 given a 45-day median registration lag, so the Apr-May 2026 block is the
          first window where post-Feb-27 buying behaviour is visible at scale. Data ends 2026-06-02,
          so April-May is complete for every year shown.
        </p>
      </header>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Citywide answer</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          One headline number per window. <span className="text-zinc-300">Yes, studios sold materially
          slower citywide in April-May 2026 vs 2025 (-31%)</span>, but the picture changes when you split
          April from May. April-2026 was actually <em>up</em> 27% YoY (still mostly pre-shock pipeline);
          May-2026 fell off a cliff at -63% YoY (deals agreed late-March to mid-April, post-shock).
          Meanwhile median psm is <em>up</em> 25% YoY: fewer deals but at higher prices, the
          classic seller-holds-firm-buyer-steps-back pattern.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">Window</th>
                <th className="text-right p-2 border-b border-zinc-800">2023</th>
                <th className="text-right p-2 border-b border-zinc-800">2024</th>
                <th className="text-right p-2 border-b border-zinc-800">2025</th>
                <th className="text-right p-2 border-b border-zinc-800">2026</th>
                <th className="text-right p-2 border-b border-zinc-800">YoY 26 vs 25 (deals)</th>
                <th className="text-right p-2 border-b border-zinc-800">YoY 26 vs 25 (psm)</th>
              </tr>
            </thead>
            <tbody>
              {[
                { label: "Apr + May", rows: aprMay },
                { label: "April only", rows: aprOnly },
                { label: "May only", rows: mayOnly },
              ].map(({ label, rows }) => {
                const by = (y: string) => rows.find((r) => r.year === y);
                const last = by("2026");
                return (
                  <tr key={label} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                    <td className="p-2 border-b border-zinc-900 text-zinc-100 font-medium">{label}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{by("2023")?.deals ?? "-"}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{by("2024")?.deals ?? "-"}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{by("2025")?.deals ?? "-"}</td>
                    <td className="p-2 border-b border-zinc-900 text-right text-zinc-100 font-semibold">{by("2026")?.deals ?? "-"}</td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(last?.yoy_deals_pct)}`}>
                      {fmtPct(last?.yoy_deals_pct, 1)}
                    </td>
                    <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(last?.yoy_psm_pct)}`}>
                      {fmtPct(last?.yoy_psm_pct, 1)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
          The April-to-May 2026 transition is the lag fingerprint: April registrations still ran
          mostly on pre-shock contract pipeline; May registrations are the first month dominated by
          deals agreed AFTER Feb 27. Treat the May -63% as the cleaner read of post-shock studio
          buyer demand.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">By district (Apr+May counts, trend tag)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Trend classification on the 2023-2026 sequence: <em>sustained decline</em> = down every
          step; <em>down from peak</em> = last year well below max; <em>rising / at peak</em> = last
          year above all prior; <em>thin/new</em> = product wasn&apos;t trading earlier.
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-right p-2 border-b border-zinc-800">2023</th>
                <th className="text-right p-2 border-b border-zinc-800">2024</th>
                <th className="text-right p-2 border-b border-zinc-800">2025</th>
                <th className="text-right p-2 border-b border-zinc-800">2026</th>
                <th className="text-right p-2 border-b border-zinc-800">YoY 25/24</th>
                <th className="text-right p-2 border-b border-zinc-800">YoY 26/25</th>
                <th className="text-left p-2 border-b border-zinc-800">Trend</th>
              </tr>
            </thead>
            <tbody>
              {byDistrict.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-100">{r.district}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r["2023"]}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r["2024"]}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-400">{r["2025"]}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-100 font-semibold">{r["2026"]}</td>
                  <td className={`p-2 border-b border-zinc-900 text-right ${pctColor(r["yoy25_24"])}`}>
                    {fmtPct(r["yoy25_24"], 0)}
                  </td>
                  <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r["yoy26_25"])}`}>
                    {fmtPct(r["yoy26_25"], 0)}
                  </td>
                  <td className="p-2 border-b border-zinc-900">
                    <span className={`text-[10px] uppercase tracking-wide px-2 py-0.5 rounded border ${trendColor(r.trend)}`}>
                      {r.trend}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold text-zinc-100 mb-3">Median AED/SQM by district (Apr+May)</h2>
        <p className="text-xs text-zinc-500 mb-3 max-w-3xl">
          Price trend alongside the velocity. District-year cells with fewer than 5 trades are
          suppressed (medians on n&lt;5 are unreliable).
        </p>
        <div className="overflow-x-auto border border-zinc-800 rounded-lg">
          <table className="w-full text-xs">
            <thead className="bg-zinc-900 text-zinc-300">
              <tr>
                <th className="text-left p-2 border-b border-zinc-800">District</th>
                <th className="text-right p-2 border-b border-zinc-800">2023 psm</th>
                <th className="text-right p-2 border-b border-zinc-800">2024 psm</th>
                <th className="text-right p-2 border-b border-zinc-800">2025 psm</th>
                <th className="text-right p-2 border-b border-zinc-800">2026 psm</th>
                <th className="text-right p-2 border-b border-zinc-800">YoY 25/24 psm</th>
                <th className="text-right p-2 border-b border-zinc-800">YoY 26/25 psm</th>
              </tr>
            </thead>
            <tbody>
              {priceTrend.map((r, i) => (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                  <td className="p-2 border-b border-zinc-900 text-zinc-100">{r.district}</td>
                  {["2023", "2024", "2025", "2026"].map((y) => (
                    <td key={y} className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                      {r[y] && r[y] !== "" ? `AED ${Number(r[y]).toLocaleString()}` : "-"}
                    </td>
                  ))}
                  <td className={`p-2 border-b border-zinc-900 text-right ${pctColor(r["yoy25_24_pct"])}`}>
                    {fmtPct(r["yoy25_24_pct"], 0)}
                  </td>
                  <td className={`p-2 border-b border-zinc-900 text-right font-semibold ${pctColor(r["yoy26_25_pct"])}`}>
                    {fmtPct(r["yoy26_25_pct"], 0)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-zinc-100 mb-1">Read of the data</h2>
        <ul className="text-sm text-zinc-300 space-y-3 list-disc pl-5 max-w-3xl">
          <li>
            <strong>Yes, ready studios are selling slower YoY citywide</strong> in the post-shock
            window: April-May 2026 totalled 64 deals vs 93 in 2025 (-31%). The April-to-May split
            (-63% in May alone) shows that the slowdown sharpens as the lag-contaminated tail of
            pre-shock deals runs out.
          </li>
          <li>
            <strong>Al Reem Island is in sustained decline</strong> on studio velocity:
            55 → 16 → 12 → 9. This is a multi-year story (it predates Feb 27) and the post-shock
            window just continued it. Median psm has nonetheless risen from AED 13k to AED 19k over
            the same period: fewer, pricier transactions.
          </li>
          <li>
            <strong>Al Maryah Island fell -77% YoY</strong>, from 44 deals to 10. New ready inventory
            that came online in 2025 has stopped trading; likely because the cohort of original
            owners stopped flipping and end-user demand has not stepped in.
          </li>
          <li>
            <strong>Yas Island studios are rising</strong>, not falling: 8 deals in 2025 to 20 in
            2026 (+150%). Median psm dropped -16% on a wider supply base. This is consistent with
            the cohort-dump finding from the post-shock scan: Yas off-plan launches (Sustainable
            City, Noya, Ansam) are turning into ready-resale studio supply, and the price has come
            in to meet buyers.
          </li>
          <li>
            <strong>Khalifa City</strong> showed the same shape as Al Maryah but milder: -53% YoY
            from a 2025 peak. <strong>Al Layyan and Masdar City</strong> are still rising on small
            bases.
          </li>
        </ul>
      </section>
    </div>
  );
}
