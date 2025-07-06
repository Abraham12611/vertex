import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const apiKey = process.env.GROQ_API_KEY;
  const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: `You are “Vertex Blueprint,” an expert DevRel architect trusted by top developer-tool startups.\nYour task:\n1. Parse the following JSON input under the key project_info.\n2. Produce a single JSON response following blueprint_schema strictly.\n### blueprint_schema\n{ audience_analysis: {...}, content_audit: {...}, competitive_benchmarking: {...}, information_architecture: {...}, tone_voice_branding: {...}, workflow_recommendations: {...}, gaps_risks: {...}, deliverables: { documentation_roadmap: {...}, style_guide: {...}, collaboration_plan: {...} } }\n– Keep each nested object concise yet actionable.\n– Wherever data is missing, infer best-guess based on industry standards but label as \"assumption\": true.\n– Use language appropriate for senior engineers and PMs.\n– Return only JSON matching the schema; no prose.` },
        { role: "user", content: JSON.stringify({ project_info: body }) }
      ],
      response_format: { type: "json_object" }
    })
  });
  const data = await groqRes.json();
  return NextResponse.json(data);
}