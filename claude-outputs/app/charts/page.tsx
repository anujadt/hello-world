import Image from "next/image";
import { listCharts } from "@/lib/data";

export const dynamic = "force-static";

function humanize(file: string): string {
  return file.replace(/\.png$/, "").replace(/^phase\d+_\d+_/, "").replace(/_/g, " ");
}

export default async function ChartsPage() {
  const charts = await listCharts();
  return (
    <div>
      <h1 className="text-2xl font-bold text-zinc-100">Chart gallery</h1>
      <p className="text-zinc-400 mt-1 text-sm">
        Each chart is the proof attached to a memo claim. Titles are written as the takeaway, not the variable.
      </p>
      <div className="grid sm:grid-cols-2 gap-6 mt-6">
        {charts.map((f) => (
          <figure key={f} className="border border-zinc-800 rounded-lg bg-zinc-900/40 p-3">
            <Image
              src={`/data/charts/${f}`}
              alt={humanize(f)}
              width={1200}
              height={700}
              className="w-full h-auto rounded"
              unoptimized
            />
            <figcaption className="text-xs text-zinc-400 mt-2">{humanize(f)}</figcaption>
          </figure>
        ))}
      </div>
    </div>
  );
}
