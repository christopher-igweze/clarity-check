import { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Shield, CheckCircle2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { fetchRepoContents } from "@/lib/github";
import { streamSurfaceScan, callSecurityReview, streamDeepProbe } from "@/lib/api";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";
import { ScanSequence } from "@/components/ScanSequence";

interface LogEntry {
  agent: string;
  message: string;
  type: "log" | "finding" | "summary" | "error" | "system" | "probe";
  color: string;
}

interface DeepProbeResults {
  install_ok?: boolean;
  build_ok?: boolean;
  tests_ok?: boolean;
  tests_passed?: number | null;
  tests_failed?: number | null;
  audit_vulnerabilities?: number;
  results?: Record<string, unknown>;
}

const agentColors: Record<string, string> = {
  Agent_Auditor: "text-neon-green",
  Agent_Visionary: "text-neon-cyan",
  Agent_Architect: "text-neon-purple",
  Agent_SRE: "text-neon-orange",
  Agent_Security: "text-neon-red",
  Agent_Educator: "text-primary",
  System: "text-muted-foreground",
};

const ScanLive = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const state = location.state as {
    projectId: string;
    repoUrl: string;
    vibePrompt?: string;
    tier: string;
  } | null;

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState<"fetching" | "scanning" | "completed" | "error">("fetching");
  const [sequenceComplete, setSequenceComplete] = useState(false);
  const [finalHealthScore, setFinalHealthScore] = useState<number | null>(null);
  const [rawContent, setRawContent] = useState("");
  const [reportId, setReportId] = useState<string | null>(null);
  const collectedFindings = useRef<Array<{ category: string; severity: string; title: string; description: string; file_path?: string; line_number?: number }>>([]);
  const collectedSummary = useRef<{ health_score: number; security_score: number; reliability_score: number; scalability_score: number } | null>(null);
  const deepProbeResults = useRef<DeepProbeResults | null>(null);
  const terminalRef = useRef<HTMLDivElement>(null);

  const addLog = (entry: LogEntry) => {
    setLogs((prev) => [...prev, entry]);
  };

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    if (!state || !user) return;

    const runScan = async () => {
      try {
        // Step 1: Fetch repo contents
        addLog({ agent: "System", message: `Fetching repository: ${state.repoUrl}...`, type: "system", color: "text-muted-foreground" });

        const repoContent = await fetchRepoContents(state.repoUrl);
        setRawContent(repoContent);
        const fileCount = (repoContent.match(/📄/g) || []).length;
        addLog({ agent: "System", message: `Repository fetched. ${fileCount} files found.`, type: "system", color: "text-muted-foreground" });

        // Step 2: Create scan report
        const { data: report, error: reportError } = await supabase
          .from("scan_reports")
          .insert({
            project_id: state.projectId,
            user_id: user.id,
            scan_tier: state.tier,
            status: "scanning",
            started_at: new Date().toISOString(),
          })
          .select()
          .single();

        if (reportError) throw reportError;
        setReportId(report.id);

        // Step 3: Run deep probe if tier is "deep"
        if (state.tier === "deep") {
          setStatus("scanning");
          addLog({ agent: "Agent_SRE", message: "Starting Tier 2 Deep Probe via Daytona sandbox...", type: "probe", color: "text-neon-orange" });

          await new Promise<void>((resolve, reject) => {
            streamDeepProbe({
              repoUrl: state.repoUrl,
              onEvent: (event) => {
                if (event.type === "probe_step") {
                  addLog({
                    agent: "Agent_SRE",
                    message: `🔬 ${event.message || event.step} [${event.status}]`,
                    type: "probe",
                    color: "text-neon-orange",
                  });
                } else if (event.type === "probe_result") {
                  const icon = event.exit_code === 0 ? "✅" : "❌";
                  const duration = event.duration_ms ? ` (${(event.duration_ms / 1000).toFixed(1)}s)` : "";
                  addLog({
                    agent: "Agent_SRE",
                    message: `${icon} ${event.step}: exit ${event.exit_code}${duration}`,
                    type: "probe",
                    color: event.exit_code === 0 ? "text-neon-green" : "text-neon-red",
                  });
                  // Show truncated stdout for failures
                  if (event.exit_code !== 0 && event.stdout) {
                    const preview = event.stdout.slice(0, 200);
                    addLog({ agent: "Agent_SRE", message: `   └─ ${preview}`, type: "probe", color: "text-muted-foreground" });
                  }
                } else if (event.type === "probe_summary") {
                  deepProbeResults.current = {
                    install_ok: event.install_ok,
                    build_ok: event.build_ok,
                    tests_ok: event.tests_ok,
                    tests_passed: event.tests_passed,
                    tests_failed: event.tests_failed,
                    audit_vulnerabilities: event.audit_vulnerabilities,
                    results: event.results as Record<string, unknown>,
                  };
                  addLog({
                    agent: "Agent_SRE",
                    message: `🔬 Deep Probe Summary: Install ${event.install_ok ? "✅" : "❌"} | Build ${event.build_ok ? "✅" : "❌"} | Tests ${event.tests_ok ? "✅" : "❌"} | Audit vulns: ${event.audit_vulnerabilities || 0}`,
                    type: "summary",
                    color: "text-neon-orange",
                  });
                } else if (event.type === "probe_error") {
                  addLog({ agent: "Agent_SRE", message: `❌ ${event.message}`, type: "error", color: "text-neon-red" });
                }
              },
              onDone: () => resolve(),
            }).catch(reject);
          });

          addLog({ agent: "System", message: "Deep probe complete. Starting surface scan...", type: "system", color: "text-primary" });
        }

        // Step 4: Start surface scan
        setStatus("scanning");
        addLog({ agent: "Agent_Scanner", message: "Starting Tier 1 Surface Scan via Gemini 3 Pro...", type: "log", color: "text-neon-green" });

        let fullResponse = "";
        await streamSurfaceScan({
          repoContent,
          repoUrl: state.repoUrl,
          vibePrompt: state.vibePrompt,
          onDelta: (chunk) => {
            fullResponse += chunk;
            // Try to parse lines as structured output
            const lines = fullResponse.split("\n");
            fullResponse = lines.pop() || ""; // Keep incomplete line

            for (const line of lines) {
              const trimmed = line.trim();
              if (!trimmed) continue;

              try {
                const parsed = JSON.parse(trimmed);
                if (parsed.type === "log") {
                  addLog({
                    agent: parsed.agent || "Agent_Scanner",
                    message: parsed.message,
                    type: "log",
                    color: agentColors[parsed.agent] || "text-neon-green",
                  });
                } else if (parsed.type === "finding") {
                  collectedFindings.current.push({
                    category: parsed.category || "security",
                    severity: parsed.severity,
                    title: parsed.title,
                    description: parsed.description || "",
                    file_path: parsed.file_path,
                    line_number: parsed.line_number,
                  });

                  const severityEmoji = {
                    critical: "🔴",
                    high: "🟠",
                    medium: "🟡",
                    low: "🟢",
                  }[parsed.severity] || "⚪";

                  addLog({
                    agent: "Agent_Scanner",
                    message: `${severityEmoji} [${parsed.severity.toUpperCase()}] ${parsed.title} — ${parsed.file_path || "general"}`,
                    type: "finding",
                    color: parsed.severity === "critical" ? "text-neon-red" : "text-neon-orange",
                  });
                } else if (parsed.type === "summary") {
                  collectedSummary.current = {
                    health_score: parsed.health_score,
                    security_score: parsed.security_score,
                    reliability_score: parsed.reliability_score,
                    scalability_score: parsed.scalability_score,
                  };
                  addLog({
                    agent: "Agent_Scanner",
                    message: `Scan complete. Health Score: ${parsed.health_score}/100 | Security: ${parsed.security_score} | Reliability: ${parsed.reliability_score} | Scalability: ${parsed.scalability_score}`,
                    type: "summary",
                    color: "text-primary",
                  });
                }
              } catch {
                // Not JSON - show as raw log
                if (trimmed.length > 3) {
                  addLog({
                    agent: "Agent_Scanner",
                    message: trimmed,
                    type: "log",
                    color: "text-neon-green",
                  });
                }
              }
            }
          },
          onDone: async () => {
            addLog({ agent: "System", message: "Surface scan completed. Starting security review...", type: "system", color: "text-primary" });

            const summary = collectedSummary.current;

            // Update report with scores
            await supabase
              .from("scan_reports")
              .update({
                status: "reviewing",
                completed_at: new Date().toISOString(),
                report_data: { raw_response: fullResponse, deep_probe: deepProbeResults.current ? JSON.parse(JSON.stringify(deepProbeResults.current)) : undefined } as any,
                ...(summary ? {
                  health_score: summary.health_score,
                  security_score: summary.security_score,
                  reliability_score: summary.reliability_score,
                  scalability_score: summary.scalability_score,
                } : {}),
              })
              .eq("id", report.id);

            // Update project health score
            if (summary) {
              await supabase
                .from("projects")
                .update({
                  latest_health_score: summary.health_score,
                  scan_count: (await supabase.from("projects").select("scan_count").eq("id", state.projectId).single()).data?.scan_count! + 1,
                })
                .eq("id", state.projectId);
            }

            // Persist findings as action_items
            if (collectedFindings.current.length > 0 && user) {
              const items = collectedFindings.current.map((f) => ({
                project_id: state.projectId,
                scan_report_id: report.id,
                user_id: user.id,
                category: f.category,
                severity: f.severity,
                title: f.title,
                description: f.description,
                file_path: f.file_path || null,
                line_number: f.line_number || null,
              }));
              await supabase.from("action_items").insert(items);
            }

            // Run Agent_Security validation
            addLog({ agent: "Agent_Security", message: "🛡️ Validating scan findings for false positives...", type: "log", color: "text-neon-red" });
            try {
              const securityResult = await callSecurityReview({
                reviewType: "validate_findings",
                findings: collectedFindings.current,
              });

              const secContent = securityResult.choices?.[0]?.message?.content || "";
              let securityReview = null;
              try {
                securityReview = JSON.parse(secContent);
              } catch {
                // Try to extract JSON from markdown code blocks
                const jsonMatch = secContent.match(/```(?:json)?\s*([\s\S]*?)```/);
                if (jsonMatch) {
                  try { securityReview = JSON.parse(jsonMatch[1]); } catch { /* ignore */ }
                }
              }

              if (securityReview) {
                await supabase
                  .from("scan_reports")
                  .update({ security_review: securityReview as any })
                  .eq("id", report.id);
                addLog({ agent: "Agent_Security", message: `🛡️ Security review complete. Verdict recorded.`, type: "log", color: "text-neon-red" });
              } else {
                addLog({ agent: "Agent_Security", message: `🛡️ Security review returned unstructured response. Saved as raw.`, type: "log", color: "text-neon-orange" });
                await supabase
                  .from("scan_reports")
                  .update({ security_review: { raw: secContent } as any })
                  .eq("id", report.id);
              }
            } catch (secErr) {
              console.error("Security review error:", secErr);
              addLog({ agent: "Agent_Security", message: `🛡️ Security review failed: ${secErr instanceof Error ? secErr.message : "Unknown error"}`, type: "error", color: "text-neon-red" });
            }

            // Mark as completed
            await supabase
              .from("scan_reports")
              .update({ status: "completed" })
              .eq("id", report.id);

            setFinalHealthScore(summary?.health_score ?? 72);
            setStatus("completed");
            addLog({ agent: "System", message: "All agents complete. Report ready.", type: "system", color: "text-primary" });
          },
        });
      } catch (err) {
        console.error("Scan error:", err);
        setStatus("error");
        addLog({
          agent: "System",
          message: `Error: ${err instanceof Error ? err.message : "Unknown error"}`,
          type: "error",
          color: "text-neon-red",
        });
      }
    };

    runScan();
  }, []);

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-pattern opacity-20 pointer-events-none" />

      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/dashboard")}>
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-emerald">Ship</span>
            <span className="text-foreground">Safe</span>
          </span>
        </div>
        <div className="flex items-center gap-2">
          {(status === "fetching" || status === "scanning") && !sequenceComplete && (
            <span className="flex items-center gap-2 text-sm font-mono text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot" />
              Initializing
            </span>
          )}
          {(status === "fetching" || status === "scanning") && sequenceComplete && (
            <span className="flex items-center gap-2 text-sm font-mono text-violet-400">
              <span className="w-2 h-2 rounded-full bg-violet-500 pulse-dot" />
              Scanning
            </span>
          )}
          {status === "completed" && (
            <span className="flex items-center gap-2 text-sm font-mono text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              Complete
            </span>
          )}
          {status === "error" && (
            <span className="flex items-center gap-2 text-sm font-mono text-rose-500">
              <AlertTriangle className="w-4 h-4" />
              Error
            </span>
          )}
        </div>
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-6 pt-8">
        {/* ── SCAN SEQUENCE (plays first) ── */}
        {!sequenceComplete && (
          <div className="glass rounded-xl p-8">
            <ScanSequence
              onComplete={() => setSequenceComplete(true)}
              repoUrl={state?.repoUrl}
              healthScore={finalHealthScore ?? 72}
            />
          </div>
        )}

        {/* ── TERMINAL (shows after sequence) ── */}
        {sequenceComplete && (
          <>
            <h1 className="text-2xl font-bold mb-1">Agent Stream</h1>
            <p className="text-sm text-muted-foreground mb-6">
              {state?.repoUrl && <span className="font-mono text-xs text-muted-foreground/60">{state.repoUrl}</span>}
            </p>

            <div className="glass rounded-xl overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400/80" />
                <span className="ml-3 text-[11px] font-mono text-muted-foreground">agent-swarm · live</span>
              </div>
              <div ref={terminalRef} className="p-6 font-mono text-sm min-h-[500px] max-h-[600px] overflow-y-auto space-y-1">
                {logs.map((log, i) => (
                  <p key={i}>
                    <span className={log.color}>▸ {log.agent}:</span>{" "}
                    <span className="text-muted-foreground">{log.message}</span>
                  </p>
                ))}
                {(status === "fetching" || status === "scanning") && (
                  <p className="text-emerald-400 animate-pulse">█</p>
                )}
              </div>
            </div>

            {status === "completed" && reportId && (
              <div className="mt-6 flex justify-end">
                <Button onClick={() => navigate(`/report/${reportId}`)} className="glow-emerald">
                  View Health Report
                </Button>
              </div>
            )}

            {status === "error" && (
              <div className="mt-6 flex justify-end gap-3">
                <Button variant="outline" onClick={() => navigate("/scan/new")}>
                  Try Again
                </Button>
                <Button variant="outline" onClick={() => navigate("/dashboard")}>
                  Dashboard
                </Button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default ScanLive;
