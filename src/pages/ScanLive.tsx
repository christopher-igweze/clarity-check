import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Shield, CheckCircle2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  abortBuildRun,
  bootstrapBuildRuntime,
  resumeBuildRun,
  streamBuildEvents,
  streamScanStatus,
  submitReplanDecision,
} from "@/lib/api";
import { ScanSequence } from "@/components/ScanSequence";

interface LogEntry {
  agent: string;
  message: string;
  type: "log" | "finding" | "summary" | "error" | "system";
  color: string;
}

const agentColors: Record<string, string> = {
  Agent_Scanner: "text-neon-green",
  Agent_Builder: "text-neon-orange",
  Agent_Security: "text-neon-red",
  Agent_Planner: "text-neon-purple",
  Agent_Educator: "text-primary",
  Orchestrator: "text-muted-foreground",
};

const ScanLive = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as {
    scanId?: string;
    buildId?: string;
    repoUrl: string;
    quotaRemaining?: number | null;
  } | null;

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState<"scanning" | "completed" | "error">("scanning");
  const [sequenceComplete, setSequenceComplete] = useState(false);
  const [finalHealthScore, setFinalHealthScore] = useState<number | null>(null);
  const [quotaRemaining, setQuotaRemaining] = useState<number | null>(state?.quotaRemaining ?? null);
  const [reportId, setReportId] = useState<string | null>(state?.scanId ?? null);
  const [buildRunStatus, setBuildRunStatus] = useState<string>("running");
  const terminalRef = useRef<HTMLDivElement>(null);
  const statusRef = useRef(status);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  const addLog = (entry: LogEntry) => {
    setLogs((prev) => [...prev, entry]);
  };

  const handleAbortBuild = async () => {
    if (!state?.buildId) return;
    try {
      const resp = await abortBuildRun({ buildId: state.buildId, reason: "manual_abort_from_scan_live" });
      setBuildRunStatus(resp.status);
      setStatus("error");
      addLog({
        agent: "System",
        message: "Build aborted by operator.",
        type: "system",
        color: "text-muted-foreground",
      });
    } catch (err) {
      addLog({
        agent: "System",
        message: `Abort failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        type: "error",
        color: "text-neon-red",
      });
    }
  };

  const handleResumeBuild = async () => {
    if (!state?.buildId) return;
    try {
      const resp = await resumeBuildRun({ buildId: state.buildId, reason: "manual_resume_from_scan_live" });
      setBuildRunStatus(resp.status);
      setStatus("scanning");
      addLog({
        agent: "System",
        message: "Build resumed.",
        type: "system",
        color: "text-muted-foreground",
      });
    } catch (err) {
      addLog({
        agent: "System",
        message: `Resume failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        type: "error",
        color: "text-neon-red",
      });
    }
  };

  const handleReduceScope = async () => {
    if (!state?.buildId) return;
    try {
      await submitReplanDecision({
        buildId: state.buildId,
        action: "REDUCE_SCOPE",
        reason: "manual_scope_reduction_from_scan_live",
      });
      addLog({
        agent: "Orchestrator",
        message: "Replan submitted: reduce scope.",
        type: "system",
        color: "text-muted-foreground",
      });
    } catch (err) {
      addLog({
        agent: "System",
        message: `Replan failed: ${err instanceof Error ? err.message : "Unknown error"}`,
        type: "error",
        color: "text-neon-red",
      });
    }
  };

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    if (!state?.scanId && !state?.buildId) {
      setStatus("error");
      addLog({
        agent: "System",
        message: "Missing scan/build id. Start a scan from the New Scan page.",
        type: "error",
        color: "text-neon-red",
      });
      return;
    }

    let cancelled = false;

    if (state?.buildId) {
      const buildId = state.buildId;
      addLog({
        agent: "System",
        message: `Connected to build ${buildId}. Running control-plane orchestration...`,
        type: "system",
        color: "text-muted-foreground",
      });

      streamBuildEvents({
        buildId,
        onEvent: ({ event, payload }) => {
          if (cancelled) return;
          const data = payload.payload || {};
          const message =
            payload.message ||
            (typeof data.reason === "string" ? data.reason : `${event} event received`);

          if (event === "BUILD_STATUS_CHANGED" && typeof data.to_status === "string") {
            setBuildRunStatus(data.to_status);
          }

          if (event === "BUILD_FINISHED") {
            const finalStatus = String(data.final_status || "completed").toLowerCase();
            setBuildRunStatus(finalStatus);
            setStatus(finalStatus === "completed" ? "completed" : "error");
            addLog({
              agent: "Orchestrator",
              message: `Build finished (${finalStatus}).`,
              type: finalStatus === "completed" ? "summary" : "error",
              color: finalStatus === "completed" ? "text-primary" : "text-neon-red",
            });
            return;
          }

          addLog({
            agent: "Orchestrator",
            message,
            type: event.includes("FAILED") ? "error" : "log",
            color: event.includes("FAILED") ? "text-neon-red" : "text-muted-foreground",
          });
        },
        onDone: () => {
          if (cancelled) return;
          if (statusRef.current === "scanning") {
            addLog({
              agent: "System",
              message: "Build stream closed.",
              type: "system",
              color: "text-muted-foreground",
            });
          }
        },
      }).catch((err) => {
        if (cancelled) return;
        setStatus("error");
        addLog({
          agent: "System",
          message: `Error: ${err instanceof Error ? err.message : "Unknown error"}`,
          type: "error",
          color: "text-neon-red",
        });
      });

      (async () => {
        try {
          await bootstrapBuildRuntime(buildId);
          addLog({
            agent: "System",
            message: "Runtime bootstrapped. Backend worker is driving orchestration.",
            type: "system",
            color: "text-muted-foreground",
          });
        } catch (err) {
          if (cancelled) return;
          addLog({
            agent: "System",
            message: `Runtime bootstrap warning: ${err instanceof Error ? err.message : "Unknown error"}`,
            type: "error",
            color: "text-neon-orange",
          });
        }
      })();
    } else if (state?.scanId) {
      addLog({
        agent: "System",
        message: `Connected to scan ${state.scanId}. Streaming agent events...`,
        type: "system",
        color: "text-muted-foreground",
      });

      streamScanStatus({
        scanId: state.scanId,
        onEvent: ({ event, payload }) => {
          if (cancelled) return;

          const agent = payload.agent || "Orchestrator";
          const level = payload.level || "info";
          const message = payload.message || `${event} event received`;
          const data = payload.data || {};

          if (event === "finding" && data.title) {
            const severity = String(data.severity || "unknown").toUpperCase();
            addLog({
              agent,
              message: `[${severity}] ${String(data.title)}${data.file_path ? ` — ${String(data.file_path)}` : ""}`,
              type: "finding",
              color: "text-neon-orange",
            });
            return;
          }

          if (event === "scan_complete") {
            const score = typeof data.health_score === "number" ? data.health_score : null;
            const remaining = typeof data.quota_remaining === "number" ? data.quota_remaining : null;
            setFinalHealthScore(score);
            setQuotaRemaining(remaining);
            setReportId(state.scanId);
            setStatus("completed");
            addLog({
              agent,
              message: `Audit complete. Health score: ${score ?? "N/A"}/100${remaining !== null ? ` • reports left: ${remaining}` : ""}`,
              type: "summary",
              color: "text-primary",
            });
            return;
          }

          if (event === "scan_error") {
            setStatus("error");
            addLog({
              agent,
              message,
              type: "error",
              color: "text-neon-red",
            });
            return;
          }

          addLog({
            agent,
            message,
            type: level === "error" ? "error" : "log",
            color: level === "error" ? "text-neon-red" : agentColors[agent] || "text-muted-foreground",
          });
        },
        onDone: () => {
          if (cancelled) return;
          if (statusRef.current === "scanning") {
            addLog({
              agent: "System",
              message: "SSE stream closed.",
              type: "system",
              color: "text-muted-foreground",
            });
          }
        },
      }).catch((err) => {
        if (cancelled) return;
        setStatus("error");
        addLog({
          agent: "System",
          message: `Error: ${err instanceof Error ? err.message : "Unknown error"}`,
          type: "error",
          color: "text-neon-red",
        });
      });
    }

    return () => {
      cancelled = true;
    };
  }, [state?.scanId, state?.buildId]);

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
          {status === "scanning" && !sequenceComplete && (
            <span className="flex items-center gap-2 text-sm font-mono text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot" />
              Initializing
            </span>
          )}
          {status === "scanning" && sequenceComplete && (
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
        {!sequenceComplete && (
          <div className="glass rounded-xl p-8">
            <ScanSequence onComplete={() => setSequenceComplete(true)} repoUrl={state?.repoUrl} healthScore={finalHealthScore ?? 72} />
          </div>
        )}

        {sequenceComplete && (
          <>
            <h1 className="text-2xl font-bold mb-1">Agent Stream</h1>
            <p className="text-sm text-muted-foreground mb-6">
              {state?.repoUrl && <span className="font-mono text-xs text-muted-foreground/60">{state.repoUrl}</span>}
            </p>

            {state?.buildId && (
              <div className="mb-4 flex flex-wrap items-center gap-2">
                <span className="text-xs font-mono text-muted-foreground">build status: {buildRunStatus}</span>
                {buildRunStatus === "running" && (
                  <>
                    <Button size="sm" variant="outline" onClick={handleReduceScope}>
                      Reduce Scope
                    </Button>
                    <Button size="sm" variant="outline" onClick={handleAbortBuild}>
                      Abort Build
                    </Button>
                  </>
                )}
                {(buildRunStatus === "paused" || buildRunStatus === "failed") && (
                  <Button size="sm" variant="outline" onClick={handleResumeBuild}>
                    Resume Build
                  </Button>
                )}
              </div>
            )}

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
                {status === "scanning" && <p className="text-emerald-400 animate-pulse">█</p>}
              </div>
            </div>

            {status === "completed" && reportId && (
              <div className="mt-6 flex items-center justify-between gap-4">
                <span className="text-xs text-muted-foreground">
                  {quotaRemaining !== null ? `Free reports remaining this month: ${quotaRemaining}` : ""}
                </span>
                <Button onClick={() => navigate(`/report/${reportId}`)} className="glow-emerald">
                  View Health Report
                </Button>
              </div>
            )}

            {status === "completed" && !reportId && (
              <div className="mt-6 flex justify-end gap-3">
                <Button variant="outline" onClick={() => navigate("/dashboard")}>
                  Back to Dashboard
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
