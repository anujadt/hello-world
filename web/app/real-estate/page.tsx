import Link from "next/link";
import { projectBySlug } from "@/lib/projects";

export default function RealEstateOverview() {
  const project = projectBySlug("real-estate")!;
  return (
    <div>
      <h1 className="text-2xl font-bold text-zinc-100">Overview</h1>
      <p className="text-zinc-400 mt-1">
        Outputs from a Claude Code analysis of the Abu Dhabi DARI / ADREC residential transaction
        export (2019 to 2026). 114,485 raw rows; 87,655 clean transactions; AED 265.9B aggregate
        value. Every figure traces to either the parquet or a named external source.
      </p>

      <div className="grid sm:grid-cols-2 gap-3 mt-8">
        {project.pages.filter((p) => p.href !== "/real-estate").map((p) => (
          <Link
            key={p.href}
            href={p.href}
            className="block p-4 rounded-lg border border-zinc-800 bg-zinc-900 hover:border-zinc-700"
          >
            <div className="font-semibold text-zinc-100">{p.label}</div>
          </Link>
        ))}
      </div>

      <div className="mt-10 text-xs text-zinc-500 border-t border-zinc-900 pt-4">
        Built from <code className="bg-zinc-900 px-1 rounded">abu_dhabi_analysis/outputs</code>.
        Triangulated against ADREC 2025, Bayut H1 2025, Engel & Volkers, Cushman & Wakefield Core.
      </div>
    </div>
  );
}
