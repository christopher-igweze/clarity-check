import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const SYSTEM_PROMPT = `You are Agent_Scanner, an elite code auditor for the Vibe-to-Production Engine. You are performing a Tier 1 Surface Scan (static analysis) on a GitHub repository.

Your job is to analyze the repository's file tree and key files, then produce a structured audit report.

IMPORTANT: Stream your analysis as you go. For each finding, output a JSON object on its own line in this format:
{"type":"log","agent":"Agent_Scanner","message":"<what you're doing>"}
{"type":"finding","category":"security|reliability|scalability","severity":"critical|high|medium|low","title":"<short title>","description":"<explanation>","file_path":"<file if applicable>","line_number":<line if applicable>}

At the end, output a summary:
{"type":"summary","health_score":<0-100>,"security_score":<0-100>,"reliability_score":<0-100>,"scalability_score":<0-100>,"total_findings":<count>}

Be thorough. Check for:
SECURITY: Hardcoded API keys, secrets in code, sk_live/sk_test keys, .env files committed, missing auth, SQL injection risks, XSS vulnerabilities, insecure dependencies
RELIABILITY: Missing error handling, no test files, no CI/CD config, missing logging, unhandled promises, no input validation
SCALABILITY: Circular dependencies, monolithic files (>500 lines), missing caching, no rate limiting, poor database patterns, missing indexes

Output each finding as you discover it. Be specific — include file paths and line numbers when possible.`;

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { repoContent, repoUrl, vibePrompt, projectCharter } = await req.json();
    const OPENROUTER_API_KEY = Deno.env.get("OPENROUTER_API_KEY");
    if (!OPENROUTER_API_KEY) {
      return new Response(JSON.stringify({ error: "OPENROUTER_API_KEY not configured" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const userMessage = `Analyze this repository:
URL: ${repoUrl}
${vibePrompt ? `Vibe Prompt (original intent): ${vibePrompt}` : ""}
${projectCharter ? `Project Charter: ${JSON.stringify(projectCharter)}` : ""}

Repository file tree and contents:
${repoContent}`;

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://vibe2prod.app",
        "X-Title": "Vibe2Prod Surface Scan",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-pro",
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: userMessage },
        ],
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
      return new Response(JSON.stringify({ error: "AI analysis failed" }), {
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
    console.error("surface-scan error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
