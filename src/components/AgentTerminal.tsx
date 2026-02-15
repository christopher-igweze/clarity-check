import { useEffect, useRef, useState, useCallback } from "react";
import { motion } from "framer-motion";

export interface TerminalLog {
  timestamp: string;
  agent: string;
  message: string;
}

interface AgentTerminalProps {
  logs?: TerminalLog[];
  /** If true, plays the built-in demo simulation */
  demo?: boolean;
  className?: string;
}

const AGENT_COLORS: Record<string, string> = {
  AUDITOR: "text-blue-400",
  SECURITY: "text-rose-500",
  ARCHITECT: "text-violet-500",
  SRE: "text-amber-400",
  EDUCATOR: "text-emerald-400",
  SYSTEM: "text-muted-foreground",
  SCANNER: "text-emerald-400",
};

const DEMO_SCRIPT: Omit<TerminalLog, "timestamp">[] = [
  { agent: "SYSTEM", message: "initializing agent swarm..." },
  { agent: "SYSTEM", message: "connecting to sandbox runtime..." },
  { agent: "AUDITOR", message: "scanning /src/index.ts..." },
  { agent: "AUDITOR", message: "scanning /src/auth.ts..." },
  { agent: "SECURITY", message: "detected hardcoded API key (line 42)" },
  { agent: "SECURITY", message: "exposed secret in /src/config/database.ts" },
  { agent: "AUDITOR", message: "scanning /src/routes/health.ts..." },
  { agent: "ARCHITECT", message: "mapping dependency graph..." },
  { agent: "AUDITOR", message: "scanning /src/middleware/cors.ts..." },
  { agent: "SECURITY", message: "CORS wildcard detected — origin: *" },
  { agent: "ARCHITECT", message: "circular dependency: auth.ts → db.ts → auth.ts" },
  { agent: "AUDITOR", message: "scanning /src/services/stripe.ts..." },
  { agent: "AUDITOR", message: "scanning /prisma/schema.prisma..." },
  { agent: "ARCHITECT", message: "no rate limiting middleware found" },
  { agent: "SRE", message: "Dockerfile missing — no containerization" },
  { agent: "SRE", message: "no CI/CD pipeline detected" },
  { agent: "AUDITOR", message: "scanning /src/utils/crypto.ts..." },
  { agent: "SECURITY", message: "weak hashing: MD5 used for password storage" },
  { agent: "ARCHITECT", message: "architecture analysis complete" },
  { agent: "EDUCATOR", message: "generating remediation guidance..." },
  { agent: "SYSTEM", message: "scan complete — 7 findings across 4 categories" },
];

const formatTimestamp = () => {
  const now = new Date();
  return [
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
    String(now.getSeconds()).padStart(2, "0"),
  ].join(":");
};

export const AgentTerminal = ({ logs: externalLogs, demo = false, className = "" }: AgentTerminalProps) => {
  const [internalLogs, setInternalLogs] = useState<TerminalLog[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  const isStreaming = useRef(false);

  const activeLogs = externalLogs ?? internalLogs;

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activeLogs.length]);

  // Demo simulation
  const runDemo = useCallback(() => {
    if (isStreaming.current) return;
    isStreaming.current = true;
    setInternalLogs([]);

    let i = 0;
    const interval = setInterval(() => {
      if (i >= DEMO_SCRIPT.length) {
        clearInterval(interval);
        isStreaming.current = false;
        return;
      }
      const entry = DEMO_SCRIPT[i];
      setInternalLogs((prev) => [
        ...prev,
        { ...entry, timestamp: formatTimestamp() },
      ]);
      i++;
    }, 220 + Math.random() * 180);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (demo && !externalLogs) runDemo();
  }, [demo, externalLogs, runDemo]);

  const getAgentColor = (agent: string) =>
    AGENT_COLORS[agent.toUpperCase()] ?? "text-muted-foreground";

  const isDone = demo && !isStreaming.current && internalLogs.length === DEMO_SCRIPT.length;
  const showCursor = externalLogs ? activeLogs.length > 0 : !isDone;

  return (
    <div
      className={`rounded-xl overflow-hidden glass ${className}`}
    >
      {/* Title bar */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/5">
        <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
        <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
        <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/80" />
        <span className="ml-3 font-mono text-[11px] text-muted-foreground select-none">
          agent-swarm · live
        </span>
        {showCursor && (
          <span className="ml-auto flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 pulse-dot" />
            <span className="font-mono text-[10px] text-emerald-400/70">streaming</span>
          </span>
        )}
      </div>

      {/* Log area */}
      <div
        ref={scrollRef}
        className="h-96 overflow-y-auto p-4 space-y-0.5 scroll-smooth"
        style={{
          scrollbarWidth: "thin",
          scrollbarColor: "hsl(0 0% 20%) transparent",
        }}
      >
        {activeLogs.map((log, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.15 }}
            className="flex gap-2 font-mono text-xs leading-relaxed"
          >
            <span className="text-muted-foreground/40 shrink-0 tabular-nums">
              {log.timestamp}
            </span>
            <span className={`shrink-0 font-semibold ${getAgentColor(log.agent)}`}>
              [{log.agent}]
            </span>
            <span className="text-muted-foreground">
              {log.message}
            </span>
          </motion.div>
        ))}

        {/* Blinking cursor */}
        {showCursor && (
          <div className="flex items-center gap-1 mt-1">
            <span className="font-mono text-xs text-emerald-400">▸</span>
            <motion.span
              className="inline-block w-2 h-4 bg-emerald-400"
              animate={{ opacity: [1, 0] }}
              transition={{ duration: 0.8, repeat: Infinity, repeatType: "reverse" }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
