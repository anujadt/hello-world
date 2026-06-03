import Link from "next/link";
import { PROJECTS, Project } from "@/lib/projects";

function Badge({ p }: { p: Project }) {
  if (p.externalUrl) {
    return <span className="text-xs uppercase tracking-wide text-sky-400">External ↗</span>;
  }
  return (
    <span
      className={`text-xs uppercase tracking-wide ${p.status === "protected" ? "text-amber-400" : "text-emerald-400"}`}
    >
      {p.status === "protected" ? "🔒 Password" : "Public"}
    </span>
  );
}

function CardInner({ p }: { p: Project }) {
  return (
    <>
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-lg font-semibold text-zinc-100">{p.title}</h2>
        <Badge p={p} />
      </div>
      <p className="text-sm text-zinc-400 mt-2 leading-relaxed">{p.blurb}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {p.tags.map((t) => (
          <span
            key={t}
            className="text-[10px] uppercase tracking-wide bg-zinc-900 border border-zinc-800 text-zinc-400 px-2 py-0.5 rounded"
          >
            {t}
          </span>
        ))}
      </div>
    </>
  );
}

const CARD_CLASS =
  "group block p-5 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:border-zinc-600 hover:bg-zinc-900 transition";

export default function Landing() {
  return (
    <div>
      <section className="mb-10">
        <h1 className="text-3xl md:text-4xl font-bold text-zinc-100 tracking-tight">Projects</h1>
        <p className="text-zinc-400 mt-2 max-w-2xl">
          A growing showcase of work built with Claude Code. Some cards open an internal dashboard,
          some are password-gated, and some link out to separately deployed sites.
        </p>
      </section>

      <section className="grid sm:grid-cols-2 gap-4">
        {PROJECTS.map((p) =>
          p.externalUrl ? (
            <a
              key={p.slug}
              href={p.externalUrl}
              target="_blank"
              rel="noreferrer"
              className={CARD_CLASS}
            >
              <CardInner p={p} />
            </a>
          ) : (
            <Link key={p.slug} href={`/${p.slug}`} className={CARD_CLASS}>
              <CardInner p={p} />
            </Link>
          ),
        )}

        <div className="p-5 rounded-xl border border-dashed border-zinc-800 bg-zinc-950 text-zinc-500">
          <h2 className="text-lg font-semibold">More coming</h2>
          <p className="text-sm mt-2">
            Add an entry to <code className="bg-zinc-900 px-1 rounded">web/lib/projects.ts</code> with
            its own pages, or an <code className="bg-zinc-900 px-1 rounded">externalUrl</code> to link
            out to another live site.
          </p>
        </div>
      </section>
    </div>
  );
}
