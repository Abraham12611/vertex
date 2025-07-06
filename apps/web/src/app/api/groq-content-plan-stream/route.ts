import { NextRequest } from "next/server";

export const runtime = "edge";

export async function POST(req: NextRequest) {
  const { form } = await req.json();
  const apiKey = process.env.GROQ_API_KEY;
  const groqRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "deepseek-r1-distill-llama-70b",
      messages: [
        {
          role: "user",
          content: `Generate a content plan for a developer product.\n- List at least 5 API documentation topics (titles) with a 1-2 sentence outline for each.\n- List at least 5 technical guides or articles (titles) with a 1-2 sentence outline for each.\nFormat as Markdown with headings:\n## API Documentation\n- Title: ...\n  - Outline: ...\n## Technical Guides & Articles\n- Title: ...\n  - Outline: ...\nProject Info: ${JSON.stringify(form, null, 2)}`,
        }
      ],
      temperature: 0.6,
      max_completion_tokens: 1024,
      top_p: 0.95,
      stream: true
    })
  });

  return new Response(groqRes.body, {
    status: 200,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store"
    }
  });
}