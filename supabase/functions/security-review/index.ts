import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const SYSTEM_PROMPT = `You are Agent_Security, the Security Officer and Gatekeeper for the Vibe-to-Production Engine. You are powered by DeepSeek V3.2 Reasoner, chosen for your gold-medal reasoning capabilities at efficient cost.

Your job is to perform a security review on code changes, scan findings, or proposed fixes. You have VETO POWER — if a change introduces a vulnerability, you must reject it.

For each item you review, output a JSON object:

When reviewing scan findings (validating Agent_Auditor's work):
{"type":"validation","finding_id":"<id>","verdict":"confirmed|false_positive|escalated","confidence":<0-100>,"reasoning":"<why>"}

When reviewing code changes (from Agent_SRE):
{"type":"code_review","verdict":"approved|vetoed","vulnerabilities_found":[{"type":"<vuln type>","severity":"critical|high|medium|low","file":"<path>","description":"<detail>"}],"reasoning":"<overall assessment>"}

Check for:
- Hardcoded secrets (API keys, tokens, passwords, sk_live, sk_test)
- SQL injection risks (raw SQL queries, unsanitized inputs)
- XSS vulnerabilities (unescaped user input in HTML/JSX)
- CSRF vulnerabilities
- Insecure authentication patterns
- Missing input validation
- Exposed sensitive data in logs or responses
- Insecure dependency versions (known CVEs)
- Missing rate limiting on sensitive endpoints
- Improper error handling that leaks stack traces
- SOC 2 compliance issues

Be thorough but fair. Don't flag theoretical risks — focus on concrete, exploitable vulnerabilities. When you veto, provide specific remediation steps.`;

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { reviewType, content, findings, codeChanges, projectCharter } = await req.json();
    const OPENROUTER_API_KEY = Deno.env.get("OPENROUTER_API_KEY");
    if (!OPENROUTER_API_KEY) {
      return new Response(JSON.stringify({ error: "OPENROUTER_API_KEY not configured" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    let userMessage = "";
    if (reviewType === "validate_findings") {
      userMessage = `Validate these scan findings for false positives and missed issues:\n${JSON.stringify(findings, null, 2)}`;
    } else if (reviewType === "code_review") {
      userMessage = `Review these code changes for security vulnerabilities:\n${JSON.stringify(codeChanges, null, 2)}`;
    } else if (reviewType === "full_scan") {
      userMessage = `Perform a full security scan on this codebase:\n${content}`;
    }

    if (projectCharter) {
      userMessage += `\n\nProject Charter (context):\n${JSON.stringify(projectCharter, null, 2)}`;
    }

    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${OPENROUTER_API_KEY}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://vibe2prod.app",
        "X-Title": "Vibe2Prod Security Review",
      },
      body: JSON.stringify({
        model: "deepseek/deepseek-reasoner",
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: userMessage },
        ],
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
      return new Response(JSON.stringify({ error: "Security review failed" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error("security-review error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
