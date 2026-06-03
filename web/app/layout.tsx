import "./globals.css";
import Link from "next/link";
import type { Metadata, Viewport } from "next";
import { PROJECTS } from "@/lib/projects";

export const metadata: Metadata = {
  title: "anujadt / hello-world",
  description: "Showcase of projects built with Claude Code.",
};
export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-zinc-900 bg-zinc-950">
            <div className="max-w-6xl mx-auto px-6 md:px-8 h-14 flex items-center justify-between">
              <Link href="/" className="font-semibold text-zinc-100 tracking-tight">
                anujadt / <span className="text-zinc-400">hello-world</span>
              </Link>
              <nav className="flex items-center gap-4 text-sm">
                {PROJECTS.map((p) =>
                  p.externalUrl ? (
                    <a
                      key={p.slug}
                      href={p.externalUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="text-zinc-400 hover:text-zinc-100"
                    >
                      {p.title.split(" ").slice(0, 3).join(" ")}
                      <span className="ml-1 text-zinc-600">↗</span>
                    </a>
                  ) : (
                    <Link
                      key={p.slug}
                      href={`/${p.slug}`}
                      className="text-zinc-400 hover:text-zinc-100"
                    >
                      {p.title.split(" ").slice(0, 3).join(" ")}
                      {p.status === "protected" && <span className="ml-1 text-zinc-600">·🔒</span>}
                    </Link>
                  ),
                )}
                <Link
                  href="https://github.com/anujadt/hello-world"
                  className="text-zinc-500 hover:text-zinc-300"
                  target="_blank"
                  rel="noreferrer"
                >
                  GitHub
                </Link>
              </nav>
            </div>
          </header>
          <main className="max-w-6xl mx-auto px-6 md:px-8 py-8 md:py-10">{children}</main>
          <footer className="border-t border-zinc-900 mt-16">
            <div className="max-w-6xl mx-auto px-6 md:px-8 py-6 text-xs text-zinc-500 flex justify-between">
              <span>Built with Claude Code</span>
              <span>{new Date().getFullYear()}</span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
