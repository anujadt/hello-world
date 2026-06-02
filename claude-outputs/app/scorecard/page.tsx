import { readCsv } from "@/lib/data";

export const dynamic = "force-static";

const COLS: { key: string; label: string; align?: "right" }[] = [
  { key: "district", label: "District" },
  { key: "net_yield_pct", label: "Net yield %", align: "right" },
  { key: "yoy_psm_pct", label: "YoY psm %", align: "right" },
  { key: "cycle_class", label: "Cycle" },
  { key: "deals_12m", label: "Deals 12m", align: "right" },
  { key: "supply_change_pp", label: "Supply Δ pp", align: "right" },
  { key: "pct_vs_own_history", label: "Own-history pct", align: "right" },
  { key: "s_yield", label: "S: yield", align: "right" },
  { key: "s_momentum", label: "S: momentum", align: "right" },
  { key: "s_cycle", label: "S: cycle", align: "right" },
  { key: "s_liquidity", label: "S: liq", align: "right" },
  { key: "s_supply_inv", label: "S: supply-inv", align: "right" },
  { key: "s_value", label: "S: value", align: "right" },
  { key: "total", label: "Total" },
];

function fmt(v: string, key: string): string {
  if (v === undefined || v === null || v === "") return "-";
  const n = Number(v);
  if (Number.isNaN(n)) return v;
  if (key === "deals_12m") return Math.round(n).toLocaleString();
  if (key.startsWith("s_") || key === "total" || key === "pct_vs_own_history") return n.toFixed(1);
  return n.toFixed(2);
}

export default async function ScorecardPage() {
  const rows = (await readCsv("area_scorecard.csv")).sort(
    (a, b) => Number(b.total) - Number(a.total),
  );
  return (
    <div>
      <h1 className="text-2xl font-bold text-zinc-100">Freehold scorecard</h1>
      <p className="text-zinc-400 mt-1 text-sm">
        Weights: net yield 25%, momentum (mix-adjusted) 20%, cycle position 20%, liquidity 15%,
        supply risk inverse 10%, value vs own history 10%. The value component rewards districts
        cheaper relative to their own trend (pullback discipline).
      </p>
      <div className="overflow-x-auto mt-6 border border-zinc-800 rounded-lg">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-zinc-900 text-zinc-300">
              {COLS.map((c) => (
                <th
                  key={c.key}
                  className={`p-2 border-b border-zinc-800 ${c.align === "right" ? "text-right" : "text-left"}`}
                >
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="odd:bg-zinc-950 even:bg-zinc-900/40">
                {COLS.map((c) => {
                  const val = fmt(r[c.key], c.key);
                  const isTotal = c.key === "total";
                  return (
                    <td
                      key={c.key}
                      className={`p-2 border-b border-zinc-900 ${
                        c.align === "right" ? "text-right" : ""
                      } ${isTotal ? "font-semibold text-zinc-100" : "text-zinc-300"}`}
                    >
                      {val}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
