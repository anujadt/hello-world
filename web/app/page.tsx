import Link from "next/link";
import { PROJECTS } from "@/lib/projects";

export default function Landing() {
  return (
    <div>
      <section className="mb-10">
        <h1 className="text-3xl md:text-4xl font-bold text-zinc-100 tracking-tight">
          Projects
        </h1>
        <p className="text-zinc-400 mt-2 max-w-2xl">
          A growing showcase of work built with Claude Code. Each card opens its own dashboard.
          Some are public; others are gated by a per-project password.
        </p>
      </section>

      <section className="grid sm:grid-cols-2 gap-4">
        {PROJECTS.map((p) => (
          <Link
            key={p.slug}
            href={`/${p.slug}`}
            className="group block p-5 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:border-zinc-600 hover:bg-zinc-900 transition"
          >
            <div className="flex items-start justify-between gap-3">
              <h2 className={`text-lg font-semibold text-zinc-100 group-hover:${p.accent ?? "text-zinc-100"}`}>
                {p.title}
              </h2>
              <span className={`text-xs uppercase tracking-wide ${p.status === "protected" ? "text-amber-400" : "text-emerald-400"}`}>
                {p.status === "protected" ? "🔒 Password" : "Public"}
              </span>
            </div>
            <p className="text-sm text-zinc-400 mt-2 leading-relaxed">{p.blurb}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {p.tags.map((t) => (
                <span key={t} className="text-[10px] uppercase tracking-wide bg-zinc-900 border border-zinc-800 text-zinc-400 px-2 py-0.5 rounded">
                  {t}
                </span>
              ))}
            </div>
          </Link>
        ))}

        {/* Placeholder card teasing the future */}
        <div className="p-5 rounded-xl border border-dashed border-zinc-800 bg-zinc-950 text-zinc-500">
          <h2 className="text-lg font-semibold">More coming</h2>
          <p className="text-sm mt-2">
            Drop a folder into <code className="bg-zinc-900 px-1 rounded">web/public/data/&lt;slug&gt;/</code>{" "}
            and add an entry to <code className="bg-zinc-900 px-1 rounded">web/lib/projects.ts</code> to add a new project.
          </p>
        </div>
      </section>
    </div>
  );
}
