import { readCsv } from "@/lib/data";

export const dynamic = "force-static";

export default async function TriangulationPage() {
  const rows = await readCsv("triangulation_table.csv");
  return (
    <div>
      <h1 className="text-2xl font-bold text-zinc-100">Triangulation table</h1>
      <p className="text-zinc-400 mt-1 text-sm">
        Every top claim cross-checked against named external sources. Tolerance is ±15%; variances
        outside that band are reconciled in the notes column.
      </p>
      <div className="overflow-x-auto mt-6 border border-zinc-800 rounded-lg">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-zinc-900 text-zinc-300">
              <th className="text-left p-2 border-b border-zinc-800">Claim</th>
              <th className="text-right p-2 border-b border-zinc-800">Ours</th>
              <th className="text-right p-2 border-b border-zinc-800">External</th>
              <th className="text-left p-2 border-b border-zinc-800">Source</th>
              <th className="text-right p-2 border-b border-zinc-800">Var %</th>
              <th className="text-left p-2 border-b border-zinc-800">Confidence</th>
              <th className="text-left p-2 border-b border-zinc-800">Reconciliation</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => {
              const v = r.variance_pct ? Number(r.variance_pct) : null;
              const varColor =
                v === null ? "text-zinc-500"
                : Math.abs(v) <= 15 ? "text-emerald-400"
                : "text-amber-400";
              return (
                <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40 align-top">
                  <td className="p-2 border-b border-zinc-900 text-zinc-200">{r.claim}</td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    {r.our_figure || "-"}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-right text-zinc-300">
                    {r.external_figure || "-"}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">
                    <a className="hover:text-blue-300" href={r.source_url} target="_blank" rel="noreferrer">
                      {r.source}
                    </a>
                  </td>
                  <td className={`p-2 border-b border-zinc-900 text-right ${varColor}`}>
                    {v === null ? "-" : `${v > 0 ? "+" : ""}${v.toFixed(1)}%`}
                  </td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400">{r.confidence}</td>
                  <td className="p-2 border-b border-zinc-900 text-zinc-400 max-w-md">
                    {r.reconciliation}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
