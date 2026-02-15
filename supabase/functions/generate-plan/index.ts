import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const SYSTEM_PROMPT = `You are Agent_Planner, a senior software architect for the Vibe-to-Production Engine. You receive the raw scan findings from Agent_Scanner and must generate a prioritized action plan.

For each finding, create a "mission" with:
- Priority: critical (🔴), high (🟠), medium (🟡), low (🟢)
- Specific files to modify
- Risk assessment (what breaks if you don't fix this)
- Recommended approach (step-by-step)
- Estimated effort (quick fix / moderate / significant refactor)
- Dependencies (what must be fixed first)

Group missions by category (security, reliability, scalability).
Order by priority within each group.

Output as a JSON array:
[{"id":"<uuid>","priority":"critical|high|medium|low","category":"security|reliability|scalability","title":"<action title>","files":["<file paths>"],"risk":"<what happens if unfixed>","approach":"<step by step>","effort":"quick|moderate|significant","dependencies":["<mission ids if any>"]}]

Be specific and actionable. Reference actual file paths from the findings.`;

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { findings, projectCharter } = await req.json();
    const OPENROUTER_API_KEY = Deno.env.get("OPENROUTER_API_KEY");
    if (!OPENROUTER_API_KEY) {
      return new Response(JSON.stringify({ error: "OPENROUTER_API_KEY not configured" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const userMessage = `${projectCharter ? `Project Charter:\n${JSON.stringify(projectCharter, null, 2)}\n\n` : ""}Scan Findings:\n${JSON.stringify(findings, null, 2)}`;

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://vibe2prod.app",
        "X-Title": "Vibe2Prod Action Plan",
      },
      body: JSON.stringify({
        model: "anthropic/claude-sonnet-4",
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: userMessage },
        ],
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error("OpenRouter error:", response.status, errText);
      return new Response(JSON.stringify({ error: "Plan generation failed" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error("generate-plan error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
