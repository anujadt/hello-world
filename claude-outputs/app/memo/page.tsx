import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { readMarkdown } from "@/lib/data";

export const dynamic = "force-static";

export default async function MemoPage() {
  const md = await readMarkdown("insight_memo.md");
  return (
    <div className="markdown-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{md}</ReactMarkdown>
    </div>
  );
}
