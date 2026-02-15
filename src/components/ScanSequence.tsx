import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ScanSequenceProps {
  onComplete: () => void;
  fileCount?: number;
  healthScore?: number;
  repoUrl?: string;
}

// Realistic file paths for the matrix rain
const SAMPLE_FILES = [
  "src/index.ts", "src/App.tsx", "package.json", "tsconfig.json",
  "src/utils/auth.ts", "src/lib/db.ts", "src/hooks/useQuery.ts",
  "docker-compose.yml", ".env.example", "src/api/routes.ts",
  "src/middleware/cors.ts", "src/models/User.ts", "src/types/index.d.ts",
  "src/components/Header.tsx", "src/components/Footer.tsx",
  "tests/auth.test.ts", "tests/api.test.ts", "src/config/database.ts",
  "src/services/email.ts", "src/validators/schema.ts",
  "README.md", "Dockerfile", ".github/workflows/ci.yml",
  "src/routes/health.ts", "src/controllers/user.ts",
  "prisma/schema.prisma", "src/lib/redis.ts", "src/utils/crypto.ts",
  "src/middleware/rateLimit.ts", "src/services/stripe.ts",
  "next.config.js", "vite.config.ts", "tailwind.config.ts",
  "src/pages/Dashboard.tsx", "src/pages/Settings.tsx",
  "src/hooks/useAuth.ts", "src/context/ThemeProvider.tsx",
  "src/lib/api-client.ts", "src/utils/format.ts",
];

type Stage = "handshake" | "download" | "analysis" | "verdict";

export const ScanSequence = ({
  onComplete,
  fileCount = 1432,
  healthScore = 72,
  repoUrl = "",
}: ScanSequenceProps) => {
  const [stage, setStage] = useState<Stage>("handshake");
  const [handshakeProgress, setHandshakeProgress] = useState(0);
  const [indexedFiles, setIndexedFiles] = useState(0);
  const [matrixFiles, setMatrixFiles] = useState<string[]>([]);
  const [showScore, setShowScore] = useState(false);
  const [displayedScore, setDisplayedScore] = useState(0);
  const matrixInterval = useRef<ReturnType<typeof setInterval>>();

  // Stage 1: Handshake
  useEffect(() => {
    if (stage !== "handshake") return;
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 12 + 3;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        setHandshakeProgress(100);
        setTimeout(() => setStage("download"), 400);
      } else {
        setHandshakeProgress(Math.min(progress, 100));
      }
    }, 80);
    return () => clearInterval(interval);
  }, [stage]);

  // Stage 2: Download counter
  useEffect(() => {
    if (stage !== "download") return;
    let count = 0;
    const step = Math.max(1, Math.floor(fileCount / 60));
    const interval = setInterval(() => {
      count += Math.floor(Math.random() * step * 2) + 1;
      if (count >= fileCount) {
        count = fileCount;
        clearInterval(interval);
        setIndexedFiles(fileCount);
        setTimeout(() => setStage("analysis"), 300);
      } else {
        setIndexedFiles(count);
      }
    }, 30);
    return () => clearInterval(interval);
  }, [stage, fileCount]);

  // Stage 3: Matrix rain
  useEffect(() => {
    if (stage !== "analysis") return;
    let tick = 0;
    matrixInterval.current = setInterval(() => {
      tick++;
      const file = SAMPLE_FILES[Math.floor(Math.random() * SAMPLE_FILES.length)];
      setMatrixFiles((prev) => {
        const next = [...prev, file];
        return next.length > 24 ? next.slice(-24) : next;
      });
      if (tick > 80) {
        clearInterval(matrixInterval.current);
        setTimeout(() => setStage("verdict"), 200);
      }
    }, 45);
    return () => { if (matrixInterval.current) clearInterval(matrixInterval.current); };
  }, [stage]);

  // Stage 4: Verdict slam + score counter
  useEffect(() => {
    if (stage !== "verdict") return;
    const timer = setTimeout(() => {
      setShowScore(true);
      // Animate score number
      let current = 0;
      const step = Math.max(1, Math.floor(healthScore / 30));
      const scoreInterval = setInterval(() => {
        current += step;
        if (current >= healthScore) {
          current = healthScore;
          clearInterval(scoreInterval);
          setTimeout(onComplete, 1500);
        }
        setDisplayedScore(current);
      }, 30);
    }, 500);
    return () => clearTimeout(timer);
  }, [stage, healthScore, onComplete]);

  const getScoreColor = useCallback((score: number) => {
    if (score >= 80) return "text-emerald-400";
    if (score >= 50) return "text-amber-400";
    return "text-rose-500";
  }, []);

  const getScoreGlow = useCallback((score: number) => {
    if (score >= 80) return "glow-emerald";
    if (score >= 50) return "shadow-[0_0_40px_hsl(38_92%_50%/0.3)]";
    return "glow-rose";
  }, []);

  return (
    <div className="relative w-full min-h-[520px] flex flex-col items-center justify-center">
      {/* Subtle grid overlay */}
      <div className="absolute inset-0 grid-pattern opacity-20 pointer-events-none rounded-xl" />

      <AnimatePresence mode="wait">
        {/* ── STAGE 1: HANDSHAKE ── */}
        {stage === "handshake" && (
          <motion.div
            key="handshake"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col items-center gap-6 w-full max-w-md"
          >
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot" />
              <span className="font-mono text-xs text-emerald-400 tracking-wider uppercase">
                System Initialization
              </span>
            </div>

            <p className="font-mono text-sm text-muted-foreground">
              Authenticating with GitHub...
            </p>
            {repoUrl && (
              <p className="font-mono text-[11px] text-muted-foreground/50 truncate max-w-full">
                {repoUrl}
              </p>
            )}

            {/* Progress bar */}
            <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-emerald-400 rounded-full"
                style={{ width: `${handshakeProgress}%` }}
                transition={{ ease: "linear" }}
              />
            </div>
            <span className="font-mono text-xs text-muted-foreground">
              {Math.floor(handshakeProgress)}%
            </span>
          </motion.div>
        )}

        {/* ── STAGE 2: DOWNLOAD ── */}
        {stage === "download" && (
          <motion.div
            key="download"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col items-center gap-6"
          >
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-violet-500 pulse-dot" />
              <span className="font-mono text-xs text-violet-400 tracking-wider uppercase">
                Indexing Repository
              </span>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="font-mono text-sm text-muted-foreground">Files Indexed:</span>
              <motion.span
                className="font-mono text-4xl font-bold text-foreground tabular-nums"
                key={indexedFiles}
              >
                {indexedFiles.toLocaleString()}
              </motion.span>
            </div>

            {/* Micro progress ticks */}
            <div className="flex gap-[2px] h-4 items-end">
              {Array.from({ length: 40 }).map((_, i) => (
                <motion.div
                  key={i}
                  className="w-1 bg-violet-500/60 rounded-sm"
                  initial={{ height: 4 }}
                  animate={{ height: Math.random() * 14 + 4 }}
                  transition={{ duration: 0.15, repeat: Infinity, repeatType: "mirror", delay: i * 0.02 }}
                />
              ))}
            </div>
          </motion.div>
        )}

        {/* ── STAGE 3: ANALYSIS (Matrix Rain) ── */}
        {stage === "analysis" && (
          <motion.div
            key="analysis"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col items-center gap-4 w-full"
          >
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot" />
              <span className="font-mono text-xs text-emerald-400 tracking-wider uppercase">
                Analyzing Codebase
              </span>
            </div>

            {/* File matrix grid */}
            <div className="w-full max-w-lg grid grid-cols-3 gap-x-4 gap-y-0.5 overflow-hidden h-[280px] relative">
              <div className="absolute inset-x-0 top-0 h-12 bg-gradient-to-b from-background to-transparent z-10 pointer-events-none" />
              <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-background to-transparent z-10 pointer-events-none" />

              {matrixFiles.map((file, i) => (
                <motion.div
                  key={`${file}-${i}`}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: [0, 1, 0.3], x: 0 }}
                  transition={{ duration: 0.6 }}
                  className="font-mono text-[10px] text-emerald-400/70 truncate whitespace-nowrap"
                >
                  {file}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* ── STAGE 4: VERDICT ── */}
        {stage === "verdict" && (
          <motion.div
            key="verdict"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col items-center gap-6"
          >
            <AnimatePresence>
              {showScore && (
                <>
                  <motion.span
                    initial={{ opacity: 0, scale: 0.5, y: 30 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{
                      type: "spring",
                      stiffness: 400,
                      damping: 15,
                    }}
                    className="font-mono text-xs text-muted-foreground tracking-widest uppercase"
                  >
                    Health Score
                  </motion.span>

                  <motion.div
                    initial={{ opacity: 0, scale: 0.3 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{
                      type: "spring",
                      stiffness: 300,
                      damping: 12,
                      delay: 0.1,
                    }}
                    className={`relative ${getScoreGlow(healthScore)} rounded-full`}
                  >
                    <span
                      className={`font-mono text-8xl font-black tabular-nums ${getScoreColor(healthScore)}`}
                    >
                      {displayedScore}
                    </span>
                    <span className="font-mono text-2xl text-muted-foreground font-light">
                      /100
                    </span>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5, duration: 0.4 }}
                    className="font-mono text-xs text-muted-foreground"
                  >
                    Scan complete · Generating report...
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
