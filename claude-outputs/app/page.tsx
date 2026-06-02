import Link from "next/link";

export default function Overview() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-zinc-100">Overview</h1>
      <p className="text-zinc-400 mt-1">
        Outputs from a Claude Code analysis of the Abu Dhabi DARI / ADREC residential transaction
        export (2019 to 2026). Use the left nav to browse the memo, the scorecard, the shortlist,
        the triangulation against external sources, and the chart gallery.
      </p>

      <div className="grid sm:grid-cols-2 gap-3 mt-8">
        {[
          { href: "/memo", title: "Insight memo", body: "Five highest-conviction insights, Yas verdict, contrarian calls, caveats." },
          { href: "/scorecard", title: "Scorecard", body: "0 to 100 freehold district scoring with every component visible." },
          { href: "/shortlist", title: "Opportunity shortlist", body: "Ranked entries with thesis, expected NET yield, what invalidates." },
          { href: "/triangulation", title: "Triangulation", body: "Every top claim cross-checked against ADREC, Bayut, Cushman, others." },
          { href: "/charts", title: "Charts", body: "Every claim has a chart titled with its takeaway." },
        ].map((c) => (
          <Link
            key={c.href}
            href={c.href}
            className="block p-4 rounded-lg border border-zinc-800 bg-zinc-900 hover:border-zinc-700"
          >
            <div className="font-semibold text-zinc-100">{c.title}</div>
            <div className="text-sm text-zinc-400 mt-1">{c.body}</div>
          </Link>
        ))}
      </div>

      <div className="mt-10 text-xs text-zinc-500 border-t border-zinc-900 pt-4">
        Built from <code className="bg-zinc-900 px-1 rounded">abu_dhabi_analysis/outputs</code>.
        All figures trace to either the clean parquet or a named external source. No fabricated numbers.
      </div>
    </div>
  );
}
