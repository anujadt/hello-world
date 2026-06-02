import "./globals.css";
import Link from "next/link";
import type { Metadata, Viewport } from "next";

export const metadata: Metadata = {
  title: "claude-outputs",
  description: "Private dashboard for Claude Code analysis outputs.",
  robots: { index: false, follow: false },
};
export const viewport: Viewport = { width: "device-width", initialScale: 1 };

const NAV = [
  { href: "/", label: "Overview" },
  { href: "/memo", label: "Insight memo" },
  { href: "/scorecard", label: "Scorecard" },
  { href: "/shortlist", label: "Shortlist" },
  { href: "/triangulation", label: "Triangulation" },
  { href: "/charts", label: "Charts" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex">
          <aside className="w-56 shrink-0 border-r border-zinc-900 bg-zinc-950 p-4 hidden md:block">
            <div className="text-zinc-100 font-semibold mb-1">claude-outputs</div>
            <div className="text-xs text-zinc-500 mb-6">Private dashboard</div>
            <nav className="space-y-1 text-sm">
              {NAV.map((n) => (
                <Link
                  key={n.href}
                  href={n.href}
                  className="block px-3 py-2 rounded hover:bg-zinc-900 text-zinc-300 hover:text-zinc-100"
                >
                  {n.label}
                </Link>
              ))}
            </nav>
            <div className="mt-10 pt-4 border-t border-zinc-900 text-xs text-zinc-500">
              <Link href="/api/logout" className="hover:text-zinc-300">Sign out</Link>
            </div>
          </aside>
          <main className="flex-1 p-6 md:p-10 max-w-5xl">{children}</main>
        </div>
      </body>
    </html>
  );
}
