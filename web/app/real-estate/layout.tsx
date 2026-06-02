import Link from "next/link";
import { projectBySlug } from "@/lib/projects";

export default function RealEstateLayout({ children }: { children: React.ReactNode }) {
  const project = projectBySlug("real-estate")!;
  return (
    <div className="grid md:grid-cols-[14rem_1fr] gap-6 md:gap-10">
      <aside className="hidden md:block">
        <div className="text-xs uppercase tracking-wide text-zinc-500">Project</div>
        <div className="font-semibold text-zinc-100 mt-1 leading-tight">{project.title}</div>
        <nav className="mt-5 space-y-1 text-sm">
          {project.pages.map((p) => (
            <Link
              key={p.href}
              href={p.href}
              className="block px-3 py-1.5 rounded hover:bg-zinc-900 text-zinc-300 hover:text-zinc-100"
            >
              {p.label}
            </Link>
          ))}
        </nav>
        <div className="mt-8 pt-4 border-t border-zinc-900 text-xs text-zinc-500 space-y-2">
          <Link href="/api/logout?project=real-estate" className="block hover:text-zinc-300">
            Sign out of this project
          </Link>
          <Link href="/" className="block hover:text-zinc-300">
            ← All projects
          </Link>
        </div>
      </aside>
      <main>{children}</main>
    </div>
  );
}
