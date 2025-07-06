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
          content: `Analyze the following project and return a comprehensive DevRel strategy analysis.\nProject Info: ${JSON.stringify(form, null, 2)}\nProvide step-by-step reasoning and recommendations.`,
        }
      ],
      temperature: 0.6,
      max_completion_tokens: 2048,
      top_p: 0.95,
      stream: true,
      reasoning_format: "parsed"
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