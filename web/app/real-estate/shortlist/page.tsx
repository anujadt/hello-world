import { readCsv } from "@/lib/data";

export const dynamic = "force-static";

export default async function ShortlistPage() {
  const rows = await readCsv("real-estate", "opportunity_shortlist.csv");
  return (
    <div>
      <h1 className="text-2xl font-bold text-zinc-100">Opportunity shortlist</h1>
      <p className="text-zinc-400 mt-1 text-sm">
        Ranked entries. Each carries a thesis, the expected NET yield on all-in entry, what would
        invalidate the call, cycle risk, supply risk, and external sources.
      </p>
      <div className="space-y-4 mt-6">
        {rows.map((r, i) => (
          <article
            key={i}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-900/50"
          >
            <header className="flex items-baseline justify-between">
              <h2 className="text-base font-semibold text-zinc-100">
                {i + 1}. {r.district}
              </h2>
              <span className="text-xs text-zinc-400">{r.segment}</span>
            </header>
            <p className="text-sm text-zinc-300 mt-2 leading-relaxed">{r.thesis}</p>
            <dl className="grid sm:grid-cols-2 gap-x-6 gap-y-2 mt-4 text-xs">
              <Row k="Expected NET yield" v={`${r.expected_net_yield_pct}%`} />
              <Row k="Appreciation case" v={r.appreciation_case} />
              <Row k="What invalidates" v={r.what_invalidates} />
              <Row k="Cycle risk" v={r.cycle_risk} />
              <Row k="Supply risk" v={r.supply_risk} />
              <Row k="External sources" v={r.external_sources} />
            </dl>
          </article>
        ))}
      </div>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-zinc-500">{k}</dt>
      <dd className="text-zinc-200 mt-0.5">{v}</dd>
    </div>
  );
}
