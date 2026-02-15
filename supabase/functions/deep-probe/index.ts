import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const DAYTONA_API = "https://app.daytona.io/api";
const DAYTONA_PROXY = "https://proxy.app.daytona.io/toolbox";

interface ProbeStep {
  name: string;
  label: string;
  command: string;
  timeout: number;
  cwd?: string;
}

const PROBE_STEPS: ProbeStep[] = [
  {
    name: "git_clone",
    label: "Cloning repository",
    command: "", // set dynamically
    timeout: 120,
  },
  {
    name: "detect_stack",
    label: "Detecting project stack",
    command: "ls -la /workspace/repo && cat /workspace/repo/package.json 2>/dev/null || echo 'NO_PACKAGE_JSON'",
    timeout: 10,
    cwd: "/workspace/repo",
  },
  {
    name: "npm_install",
    label: "Installing dependencies (Crash Test)",
    command: "cd /workspace/repo && npm install --no-audit --no-fund 2>&1",
    timeout: 180,
  },
  {
    name: "npm_build",
    label: "Building project (Build Test)",
    command: "cd /workspace/repo && npm run build 2>&1",
    timeout: 120,
  },
  {
    name: "npm_test",
    label: "Running test suite (Smoke Test)",
    command: "cd /workspace/repo && npm test 2>&1 || true",
    timeout: 120,
  },
  {
    name: "npm_audit",
    label: "Running npm audit",
    command: "cd /workspace/repo && npm audit --json 2>&1 || true",
    timeout: 30,
  },
];

function sseEvent(data: Record<string, unknown>): string {
  return `data: ${JSON.stringify(data)}\n\n`;
}

async function createSandbox(apiKey: string): Promise<string> {
  const resp = await fetch(`${DAYTONA_API}/sandbox`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ language: "typescript" }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Failed to create sandbox: ${resp.status} ${err}`);
  }

  const data = await resp.json();
  return data.id;
}

async function execCommand(
  apiKey: string,
  sandboxId: string,
  command: string,
  timeout: number
): Promise<{ exitCode: number; result: string }> {
  const resp = await fetch(`${DAYTONA_PROXY}/${sandboxId}/process/execute`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ command, timeout }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Command execution failed: ${resp.status} ${err}`);
  }

  const data = await resp.json();
  return { exitCode: data.exitCode ?? data.exit_code ?? -1, result: data.result ?? "" };
}

async function deleteSandbox(apiKey: string, sandboxId: string): Promise<void> {
  try {
    await fetch(`${DAYTONA_API}/sandbox/${sandboxId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${apiKey}` },
    });
  } catch (e) {
    console.error("Failed to delete sandbox:", e);
  }
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  const DAYTONA_API_KEY = Deno.env.get("DAYTONA_API_KEY");
  if (!DAYTONA_API_KEY) {
    return new Response(JSON.stringify({ error: "DAYTONA_API_KEY not configured" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const { repoUrl, githubToken } = await req.json();
    if (!repoUrl) {
      return new Response(JSON.stringify({ error: "repoUrl is required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Build clone URL (with token for private repos)
    let cloneUrl = repoUrl;
    if (githubToken) {
      cloneUrl = repoUrl.replace("https://github.com/", `https://x-access-token:${githubToken}@github.com/`);
    }

    const body = new ReadableStream({
      async start(controller) {
        const send = (data: Record<string, unknown>) => {
          controller.enqueue(new TextEncoder().encode(sseEvent(data)));
        };

        let sandboxId: string | null = null;

        try {
          // Create sandbox
          send({ type: "probe_step", step: "create_sandbox", status: "running", agent: "Agent_SRE", message: "Creating Daytona sandbox..." });
          const startTime = Date.now();
          sandboxId = await createSandbox(DAYTONA_API_KEY);
          send({
            type: "probe_result", step: "create_sandbox", exit_code: 0,
            stdout: `Sandbox ${sandboxId} created`, stderr: "",
            duration_ms: Date.now() - startTime, agent: "Agent_SRE",
          });

          // Set clone command
          const steps = [...PROBE_STEPS];
          steps[0].command = `git clone '${cloneUrl}' /workspace/repo 2>&1`;

          const results: Record<string, { exit_code: number; stdout: string; stderr: string; duration_ms: number }> = {};

          for (const step of steps) {
            send({ type: "probe_step", step: step.name, status: "running", agent: "Agent_SRE", message: step.label });
            const t0 = Date.now();

            try {
              const res = await execCommand(DAYTONA_API_KEY, sandboxId, step.command, step.timeout);
              const duration = Date.now() - t0;
              // Truncate large outputs
              const stdout = res.result.length > 10000 ? res.result.slice(0, 5000) + "\n...[truncated]...\n" + res.result.slice(-3000) : res.result;

              results[step.name] = { exit_code: res.exitCode, stdout, stderr: "", duration_ms: duration };
              send({
                type: "probe_result", step: step.name, exit_code: res.exitCode,
                stdout, stderr: "", duration_ms: duration, agent: "Agent_SRE",
              });

              // If install or clone fails, abort remaining steps
              if ((step.name === "git_clone" || step.name === "npm_install") && res.exitCode !== 0) {
                send({ type: "probe_step", step: "abort", status: "error", agent: "Agent_SRE", message: `${step.label} failed. Aborting remaining steps.` });
                break;
              }
            } catch (err) {
              const duration = Date.now() - t0;
              const errMsg = err instanceof Error ? err.message : String(err);
              results[step.name] = { exit_code: -1, stdout: "", stderr: errMsg, duration_ms: duration };
              send({
                type: "probe_result", step: step.name, exit_code: -1,
                stdout: "", stderr: errMsg, duration_ms: duration, agent: "Agent_SRE",
              });
            }
          }

          // Send final summary
          const buildPassed = results.npm_build?.exit_code === 0;
          const installPassed = results.npm_install?.exit_code === 0;
          const testOutput = results.npm_test?.stdout || "";
          const testPassed = results.npm_test?.exit_code === 0;

          // Parse test counts from output
          const testMatch = testOutput.match(/(\d+)\s+pass/i);
          const failMatch = testOutput.match(/(\d+)\s+fail/i);

          // Parse npm audit
          let auditVulns = 0;
          try {
            const auditJson = JSON.parse(results.npm_audit?.stdout || "{}");
            auditVulns = auditJson.metadata?.vulnerabilities?.total || 0;
          } catch { /* not json */ }

          send({
            type: "probe_summary", agent: "Agent_SRE",
            install_ok: installPassed,
            build_ok: buildPassed,
            tests_ok: testPassed,
            tests_passed: testMatch ? parseInt(testMatch[1]) : null,
            tests_failed: failMatch ? parseInt(failMatch[1]) : null,
            audit_vulnerabilities: auditVulns,
            results,
          });

        } catch (err) {
          const errMsg = err instanceof Error ? err.message : String(err);
          send({ type: "probe_error", agent: "Agent_SRE", message: errMsg });
        } finally {
          // Cleanup sandbox
          if (sandboxId) {
            send({ type: "probe_step", step: "cleanup", status: "running", agent: "Agent_SRE", message: "Cleaning up sandbox..." });
            await deleteSandbox(DAYTONA_API_KEY, sandboxId);
            send({ type: "probe_result", step: "cleanup", exit_code: 0, stdout: "Sandbox deleted", stderr: "", duration_ms: 0, agent: "Agent_SRE" });
          }
          controller.enqueue(new TextEncoder().encode("data: [DONE]\n\n"));
          controller.close();
        }
      },
    });

    return new Response(body, {
      headers: {
        ...corsHeaders,
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
      },
    });
  } catch (e) {
    console.error("deep-probe error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
