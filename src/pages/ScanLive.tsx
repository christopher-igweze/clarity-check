import { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Shield, CheckCircle2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { fetchRepoContents } from "@/lib/github";
import { streamSurfaceScan } from "@/lib/api";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";

interface LogEntry {
  agent: string;
  message: string;
  type: "log" | "finding" | "summary" | "error" | "system";
  color: string;
}

const agentColors: Record<string, string> = {
  Agent_Scanner: "text-neon-green",
  Agent_Visionary: "text-neon-cyan",
  Agent_Planner: "text-neon-purple",
  Agent_Builder: "text-neon-orange",
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
  const [rawContent, setRawContent] = useState("");
  const [reportId, setReportId] = useState<string | null>(null);
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

        // Step 3: Start surface scan
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
            setStatus("completed");
            addLog({ agent: "System", message: "Scan completed successfully.", type: "system", color: "text-primary" });

            // Update report status
            await supabase
              .from("scan_reports")
              .update({
                status: "completed",
                completed_at: new Date().toISOString(),
                report_data: { raw_response: fullResponse },
              })
              .eq("id", report.id);
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
      <div className="fixed inset-0 grid-pattern opacity-40 pointer-events-none" />

      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/dashboard")}>
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Vibe</span>
            <span className="text-foreground">2Prod</span>
          </span>
        </div>
        <div className="flex items-center gap-2">
          {status === "scanning" && (
            <span className="flex items-center gap-2 text-sm text-neon-green">
              <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse-neon" />
              Scanning...
            </span>
          )}
          {status === "completed" && (
            <span className="flex items-center gap-2 text-sm text-primary">
              <CheckCircle2 className="w-4 h-4" />
              Complete
            </span>
          )}
          {status === "error" && (
            <span className="flex items-center gap-2 text-sm text-neon-red">
              <AlertTriangle className="w-4 h-4" />
              Error
            </span>
          )}
        </div>
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-6 pt-8">
        <h1 className="text-2xl font-bold mb-1">The Thinking Stream</h1>
        <p className="text-sm text-muted-foreground mb-6">
          {state?.repoUrl && <span className="font-mono text-xs">{state.repoUrl}</span>}
        </p>

        <div className="glass-strong rounded-xl overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
            <div className="w-3 h-3 rounded-full bg-neon-red/80" />
            <div className="w-3 h-3 rounded-full bg-neon-orange/80" />
            <div className="w-3 h-3 rounded-full bg-neon-green/80" />
            <span className="ml-3 text-xs font-mono text-muted-foreground">agent-swarm-output</span>
          </div>
          <div ref={terminalRef} className="p-6 font-mono text-sm min-h-[500px] max-h-[600px] overflow-y-auto space-y-1">
            {logs.map((log, i) => (
              <p key={i}>
                <span className={log.color}>▸ {log.agent}:</span>{" "}
                <span className="text-muted-foreground">{log.message}</span>
              </p>
            ))}
            {(status === "fetching" || status === "scanning") && (
              <p className="text-primary animate-pulse-neon">█</p>
            )}
          </div>
        </div>

        {status === "completed" && reportId && (
          <div className="mt-6 flex justify-end">
            <Button onClick={() => navigate(`/report/${reportId}`)} className="neon-glow-green">
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
      </main>
    </div>
  );
};

export default ScanLive;
