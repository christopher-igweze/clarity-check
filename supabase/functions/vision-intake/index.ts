import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const SYSTEM_PROMPT = `You are Agent_Visionary, a Senior Product Manager for the Vibe-to-Production Engine. Your job is to understand the user's application before any code audit begins.

You have access to the repository URL and optionally a "vibe prompt" (the original prompt used to generate the code).

Your goal is to ask exactly 3 clarifying questions (one at a time) to understand:
1. What is the core purpose of this application? Who are the target users?
2. What are the critical features that must NOT be broken during any refactoring?
3. What is the deployment target and scale expectations?

After the user answers all 3 questions, generate a project_charter as a JSON object:
{"type":"charter","charter":{"purpose":"...","target_users":"...","critical_features":["..."],"deployment_target":"...","scale_expectations":"...","constraints":["..."]}}

Be conversational, friendly, and concise. You're a Senior PM, not a robot. Use the repo URL and vibe prompt context to make your questions specific and relevant.`;

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { messages, repoUrl, vibePrompt } = await req.json();
    const OPENROUTER_API_KEY = Deno.env.get("OPENROUTER_API_KEY");
    if (!OPENROUTER_API_KEY) {
      return new Response(JSON.stringify({ error: "OPENROUTER_API_KEY not configured" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const contextMessage = `Repository URL: ${repoUrl}
${vibePrompt ? `Vibe Prompt: ${vibePrompt}` : "No vibe prompt provided."}`;

    const fullMessages = [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content: contextMessage },
      ...messages,
    ];

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://vibe2prod.app",
        "X-Title": "Vibe2Prod Vision Intake",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-pro",
        messages: fullMessages,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error("OpenRouter error:", response.status, errText);
      if (response.status === 429) {
        return new Response(JSON.stringify({ error: "Rate limited. Please try again later." }), {
          status: 429,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      return new Response(JSON.stringify({ error: "Vision intake failed" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(response.body, {
      headers: {
        ...corsHeaders,
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
      },
    });
  } catch (e) {
    console.error("vision-intake error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
