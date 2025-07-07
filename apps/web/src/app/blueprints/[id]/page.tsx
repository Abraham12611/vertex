"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter, useParams } from "next/navigation";
import DOMPurify from "dompurify";
import { marked } from "marked";

function parseSections(text: string) {
  // Split by headings like '## Section Name' (Markdown style)
  const sections: { title: string; content: string }[] = [];
  const regex = /^##\s*(.+?)\n([\s\S]*?)(?=^##|$)/gm;
  let match;
  while ((match = regex.exec(text)) !== null) {
    sections.push({ title: match[1].trim(), content: match[2].trim() });
  }
  return sections.length > 0 ? sections : [{ title: "Comprehensive Analysis", content: text.trim() }];
}

function randomMetric(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function generateMockSEOMetrics() {
  return {
    seoAnalysisMetrics: {
      on_page: {
        metaTitleLength: randomMetric(40, 60),
        metaDescriptionLength: randomMetric(120, 160),
        headingStructure: randomMetric(1, 10),
        keywordDensity: randomMetric(1, 5),
        imageAltAttributes: randomMetric(5, 20),
        urlStructure: randomMetric(1, 10),
        contentWordCount: randomMetric(800, 2500),
        internalLinksPerPage: randomMetric(3, 15),
      },
      off_page: {
        totalBacklinks: randomMetric(100, 10000),
        referringDomains: randomMetric(20, 500),
        domainAuthority: randomMetric(10, 100),
        pageAuthority: randomMetric(10, 100),
        linkingRootDomains: randomMetric(10, 300),
        followNofollowRatio: randomMetric(30, 100),
        topAnchorTexts: randomMetric(5, 20),
      },
      technical: {
        pageLoadTime: randomMetric(1, 5),
        timeToFirstByte: randomMetric(100, 800),
        mobileUsabilityErrors: randomMetric(0, 5),
        structuredDataErrors: randomMetric(0, 3),
        crawlErrors: randomMetric(0, 5),
        httpsImplementation: randomMetric(0, 1),
        xmlSitemapIssues: randomMetric(0, 2),
        robotsTxtIssues: randomMetric(0, 2),
      },
      performance: {
        organicTraffic: randomMetric(1000, 100000),
        organicClickThroughRate: randomMetric(1, 20),
        bounceRate: randomMetric(20, 80),
        pagesPerSession: randomMetric(1, 10),
        averageSessionDuration: randomMetric(30, 300),
        indexedPages: randomMetric(10, 1000),
      },
    },
    competitorAnalysisMetrics: {
      domain_metrics: {
        competitorDomainAuthority: randomMetric(10, 100),
        competitorOrganicTraffic: randomMetric(1000, 100000),
        competitorTotalBacklinks: randomMetric(100, 10000),
        competitorReferringDomains: randomMetric(20, 500),
      },
      keyword_metrics: {
        sharedKeywords: randomMetric(10, 1000),
        keywordGap: randomMetric(10, 500),
        competitorTopRankingKeywords: randomMetric(10, 100),
        estimatedKeywordTrafficValue: randomMetric(1000, 100000),
      },
      content_metrics: {
        competitorTopPages: randomMetric(5, 20),
        contentWordCount: randomMetric(800, 2500),
        contentFreshness: randomMetric(1, 12),
        socialShares: randomMetric(10, 1000),
      },
      backlink_metrics: {
        competitorLinkVelocity: randomMetric(1, 20),
        competitorNewLostLinks: randomMetric(0, 10),
        competitorLinkDiversity: randomMetric(1, 10),
        competitorTopLinkingDomains: randomMetric(5, 20),
      },
      ad_metrics: {
        competitorPaidKeywords: randomMetric(10, 100),
        adCopyAnalysis: randomMetric(1, 10),
        estimatedPPCSpend: randomMetric(1000, 100000),
      },
    },
  };
}

export default function BlueprintDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const [form, setForm] = useState<any>(null);
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [edited, setEdited] = useState("");
  const [saved, setSaved] = useState(true);
  const [sections, setSections] = useState<{ title: string; content: string }[]>([]);
  const analysisRef = useRef<HTMLDivElement>(null);
  const [progressDots, setProgressDots] = useState(0);
  const [contentPlanLoading, setContentPlanLoading] = useState(true);
  const [contentPlanReady, setContentPlanReady] = useState(false);
  const [mockMetrics, setMockMetrics] = useState<any>(null);

  // Progress dots animation
  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setProgressDots(d => (d + 1) % 4);
    }, 400);
    return () => clearInterval(interval);
  }, [loading]);

  // Load form data on mount
  useEffect(() => {
    if (!id) return;
    const data = localStorage.getItem(`blueprint_form_${id}`);
    if (data) setForm(JSON.parse(data));
    else setError("No form data found for this blueprint.");
  }, [id]);

  // On mount, send to Groq API and stream output
  useEffect(() => {
    if (!form) return;
    let abort = false;
    setLoading(true);
    setError(null);
    setAnalysis("");
    setEdited("");
    setEditing(false);
    setSaved(true);
    setSections([]);
    async function fetchAnalysis() {
      try {
        const res = await fetch("/api/groq-blueprint-stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ form }),
        });
        if (!res.body) throw new Error("No response body");
        const reader = res.body.getReader();
        let text = "";
        let fullText = "";
        let decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          if (abort) break;
          const chunk = decoder.decode(value);
          // Parse each line for 'data: ...'
          chunk.split(/\r?\n/).forEach(line => {
            if (line.startsWith("data:")) {
              const json = line.slice(5).trim();
              if (json === "[DONE]") return;
              try {
                const parsed = JSON.parse(json);
                const delta = parsed.choices?.[0]?.delta?.content;
                if (delta) {
                  text += delta;
                  fullText += delta;
                  setAnalysis(text);
                  if (analysisRef.current) {
                    analysisRef.current.scrollTop = analysisRef.current.scrollHeight;
                  }
                }
              } catch {}
            }
          });
        }
        setLoading(false);
        // Parse sections after streaming is done
        setSections(parseSections(text));
      } catch (err) {
        setError("Failed to generate analysis.");
        setLoading(false);
      }
    }
    fetchAnalysis();
    return () => { abort = true; };
  }, [form]);

  // Parallel: Fire content plan request
  useEffect(() => {
    if (!form || !id) return;
    setContentPlanLoading(true);
    setContentPlanReady(false);
    async function fetchContentPlan() {
      try {
        const res = await fetch("/api/groq-content-plan-stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ form }),
        });
        if (!res.body) throw new Error("No response body");
        const reader = res.body.getReader();
        let text = "";
        let decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          chunk.split(/\r?\n/).forEach(line => {
            if (line.startsWith("data:")) {
              const json = line.slice(5).trim();
              if (json === "[DONE]") return;
              try {
                const parsed = JSON.parse(json);
                const delta = parsed.choices?.[0]?.delta?.content;
                if (delta) {
                  text += delta;
                }
              } catch {}
            }
          });
        }
        localStorage.setItem(`content_plan_${id}`, text);
        setContentPlanLoading(false);
        setContentPlanReady(true);
      } catch {
        setContentPlanLoading(false);
        setContentPlanReady(false);
      }
    }
    fetchContentPlan();
  }, [form, id]);

  // Generate mock SEO/competitor metrics after analysis is done
  useEffect(() => {
    if (!loading && !mockMetrics) {
      setMockMetrics(generateMockSEOMetrics());
    }
  }, [loading, mockMetrics]);

  // Autosave edits
  useEffect(() => {
    if (!id || !editing) return;
    localStorage.setItem(`blueprint_analysis_${id}`, edited);
    setSaved(false);
    const timeout = setTimeout(() => setSaved(true), 800);
    return () => clearTimeout(timeout);
  }, [edited, id, editing]);

  function handleEdit() {
    setEditing(true);
    setEdited(analysis);
  }

  function handleChange(e: any) {
    setEdited(e.target.value);
  }

  function handlePublish() {
    alert("Plan published! (demo)");
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen text-red-500 text-lg">{error}</div>;
  }
  if (!form) {
    return <div className="flex items-center justify-center min-h-screen text-gray-500 text-lg">Loading form data...</div>;
  }

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-[#F5F7FA] to-[#E9ECF0]">
      <main className="flex-1 flex flex-col min-h-screen">
        {/* Top Bar */}
        <div className="flex items-center justify-between px-10 py-6 border-b border-gray-200 bg-white/70 backdrop-blur-md sticky top-0 z-10">
          <nav className="flex items-center gap-2 text-sm text-gray-500">
            <button onClick={() => router.push('/dashboard')} className="hover:underline">Dashboard</button>
            <span>/</span>
            <span className="text-gray-700 font-semibold">Blueprint</span>
            <span>/</span>
            <span className="text-gray-700">{id}</span>
          </nav>
          <button
            className="px-6 py-2 rounded-full bg-[#007AFF] text-white font-semibold shadow hover:-translate-y-0.5 hover:shadow-lg transition-all"
            onClick={handlePublish}
          >
            Publish Plan
          </button>
        </div>
        {/* Analysis/Editor */}
        <div className="flex-1 flex flex-col items-center justify-start px-10 py-8 w-full">
          <h2 className="text-2xl font-bold mb-4">Comprehensive Analysis</h2>
          {loading ? (
            <div className="w-full max-w-3xl flex flex-col items-center justify-center min-h-[300px]">
              <div className="flex items-center gap-2 mb-4">
                <span className="animate-spin inline-block w-6 h-6 border-4 border-blue-300 border-t-transparent rounded-full" />
                <span className="text-gray-500 text-lg">Generating analysis{'.'.repeat(progressDots)}</span>
              </div>
              <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                <div className="h-2 bg-blue-400 animate-pulse rounded-full" style={{ width: `${Math.min(100, analysis.length / 10)}%` }} />
              </div>
            </div>
          ) : !editing ? (
            <div className="w-full max-w-3xl">
              {sections.map(section => (
                <div key={section.title} className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6 mb-6">
                  <div className="text-lg font-semibold mb-2 text-white">{section.title}</div>
                  <div className="prose prose-invert max-w-none text-gray-100" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(section.content)) }} />
                </div>
              ))}
              <button
                className="mt-6 px-6 py-2 rounded-full bg-gray-200 text-gray-700 font-semibold shadow hover:bg-gray-300"
                onClick={handleEdit}
              >
                Edit Analysis
              </button>
            </div>
          ) : (
            <>
              <textarea
                className="w-full max-w-3xl min-h-[300px] rounded-xl border border-gray-200 px-4 py-3 text-base font-mono bg-white/80 shadow-inner"
                value={edited}
                onChange={handleChange}
              />
              <div className="mt-2 text-xs text-gray-400">
                {saved ? "All changes saved." : "Saving..."}
              </div>
            </>
          )}
          {!contentPlanReady ? (
            <div className="w-full max-w-3xl flex flex-col items-center justify-center min-h-[100px] mt-8">
              <span className="animate-spin inline-block w-6 h-6 border-4 border-blue-300 border-t-transparent rounded-full mb-2" />
              <span className="text-gray-500 text-base">Generating content plan...</span>
            </div>
          ) : (
            <button
              className="mt-8 px-8 py-3 rounded-full bg-[#007AFF] text-white text-lg font-semibold shadow-lg transition-transform hover:-translate-y-1 hover:shadow-2xl"
              onClick={() => router.push(`/content-plan/${id}`)}
            >
              View Content Plan
            </button>
          )}

          {/* SEO/Competitor Metrics Section */}
          {mockMetrics && (
            <div className="w-full max-w-4xl mt-12">
              <h3 className="text-xl font-bold mb-4">SEO & Competitor Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* On-page SEO */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">On-Page SEO</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.seoAnalysisMetrics.on_page).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
                {/* Off-page SEO */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Off-Page SEO</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.seoAnalysisMetrics.off_page).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
                {/* Technical SEO */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Technical SEO</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.seoAnalysisMetrics.technical).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
                {/* Performance */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Performance</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.seoAnalysisMetrics.performance).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                {/* Competitor Domain Metrics */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Competitor Domain Metrics</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.competitorAnalysisMetrics.domain_metrics).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
                {/* Competitor Keyword Metrics */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Competitor Keyword Metrics</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.competitorAnalysisMetrics.keyword_metrics).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
                {/* Competitor Content Metrics */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Competitor Content Metrics</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.competitorAnalysisMetrics.content_metrics).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
                {/* Competitor Backlink Metrics */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Competitor Backlink Metrics</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.competitorAnalysisMetrics.backlink_metrics).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
                {/* Competitor Ad Metrics */}
                <div className="rounded-2xl bg-[#18181b] shadow-xl border border-[#27272a] p-6">
                  <div className="text-lg font-semibold mb-2 text-white">Competitor Ad Metrics</div>
                  <ul className="text-gray-100">
                    {Object.entries(mockMetrics.competitorAnalysisMetrics.ad_metrics).map(([k, v]) => (
                      <li key={k}><b>{k}:</b> {v}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}