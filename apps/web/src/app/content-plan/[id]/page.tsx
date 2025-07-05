"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

function parseContentPlan(markdown: string) {
  // Parse Markdown into API docs and articles
  const apiDocs: { title: string; outline: string }[] = [];
  const articles: { title: string; outline: string }[] = [];
  let current = null;
  const lines = markdown.split(/\r?\n/);
  let section: "api" | "articles" | null = null;
  let lastTitle = "";
  lines.forEach(line => {
    if (/^##\s*API Documentation/i.test(line)) section = "api";
    else if (/^##\s*Technical Guides/i.test(line)) section = "articles";
    else if (/^-\s*Title:\s*(.+)/i.test(line)) {
      lastTitle = line.replace(/^-\s*Title:\s*/i, "").trim();
    } else if (/^-\s*Outline:\s*(.+)/i.test(line)) {
      const outline = line.replace(/^-\s*Outline:\s*/i, "").trim();
      if (section === "api") apiDocs.push({ title: lastTitle, outline });
      else if (section === "articles") articles.push({ title: lastTitle, outline });
      lastTitle = "";
    }
  });
  return { apiDocs, articles };
}

export default function ContentPlanPage() {
  const params = useParams();
  const id = params?.id as string;
  const [contentPlan, setContentPlan] = useState("");
  const [loading, setLoading] = useState(true);
  const [apiDocs, setApiDocs] = useState<{ title: string; outline: string }[]>([]);
  const [articles, setArticles] = useState<{ title: string; outline: string }[]>([]);

  useEffect(() => {
    if (!id) return;
    const plan = localStorage.getItem(`content_plan_${id}`);
    if (plan) {
      setContentPlan(plan);
      const { apiDocs, articles } = parseContentPlan(plan);
      setApiDocs(apiDocs);
      setArticles(articles);
      setLoading(false);
    }
  }, [id]);

  return (
    <div className="flex flex-col items-center min-h-screen bg-[#09090b] py-12">
      <h2 className="text-3xl font-bold mb-8 text-white">Content Plan</h2>
      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[300px]">
          <span className="animate-spin inline-block w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full mb-4" />
          <span className="text-gray-300 text-lg">Loading content plan...</span>
        </div>
      ) : (
        <div className="w-full max-w-4xl">
          <h3 className="text-xl font-semibold mb-4 text-white">API Documentation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {apiDocs.map((doc, i) => (
              <div key={i} className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                <div className="text-lg font-semibold mb-2 text-white">{doc.title}</div>
                <div className="text-gray-200 whitespace-pre-wrap">{doc.outline}</div>
              </div>
            ))}
          </div>
          <h3 className="text-xl font-semibold mb-4 text-white">Technical Guides & Articles</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {articles.map((art, i) => (
              <div key={i} className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                <div className="text-lg font-semibold mb-2 text-white">{art.title}</div>
                <div className="text-gray-200 whitespace-pre-wrap">{art.outline}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}