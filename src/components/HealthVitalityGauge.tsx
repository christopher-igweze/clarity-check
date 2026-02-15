import { useEffect, useState, useMemo } from "react";
import { motion } from "framer-motion";

interface HealthVitalityGaugeProps {
  score: number;
  size?: number;
}

export const HealthVitalityGauge = ({ score, size = 280 }: HealthVitalityGaugeProps) => {
  const [displayScore, setDisplayScore] = useState(0);

  // Animate score count-up
  useEffect(() => {
    let current = 0;
    const step = Math.max(1, Math.floor(score / 40));
    const interval = setInterval(() => {
      current += step;
      if (current >= score) {
        current = score;
        clearInterval(interval);
      }
      setDisplayScore(current);
    }, 25);
    return () => clearInterval(interval);
  }, [score]);

  const clampedScore = Math.max(0, Math.min(100, score));

  const { color, glowColor, label, badgeBg, badgeText } = useMemo(() => {
    if (clampedScore <= 50)
      return {
        color: "hsl(347, 77%, 50%)",
        glowColor: "hsl(347, 77%, 50%)",
        label: "CRITICAL INSTABILITY",
        badgeBg: "bg-rose-500/20",
        badgeText: "text-rose-400",
      };
    if (clampedScore <= 80)
      return {
        color: "hsl(38, 92%, 50%)",
        glowColor: "hsl(38, 92%, 50%)",
        label: "OPTIMIZATION REQUIRED",
        badgeBg: "bg-amber-500/20",
        badgeText: "text-amber-400",
      };
    return {
      color: "hsl(160, 84%, 39%)",
      glowColor: "hsl(160, 84%, 39%)",
      label: "PRODUCTION READY",
      badgeBg: "bg-emerald-500/20",
      badgeText: "text-emerald-400",
    };
  }, [clampedScore]);

  const cx = size / 2;
  const cy = size / 2 + 10;
  const radius = size / 2 - 30;
  const strokeWidth = 10;
  const trackRadius = radius;

  // Semi-circle arc (180°, from left to right)
  const arcLength = Math.PI * trackRadius;
  const filledLength = (clampedScore / 100) * arcLength;

  // Tick marks (21 ticks for 0-100)
  const ticks = Array.from({ length: 21 }, (_, i) => {
    const angle = Math.PI + (i / 20) * Math.PI; // 180° to 360°
    const isMajor = i % 5 === 0;
    const innerR = trackRadius - (isMajor ? 18 : 12);
    const outerR = trackRadius + (isMajor ? 6 : 3);
    return {
      x1: cx + innerR * Math.cos(angle),
      y1: cy + innerR * Math.sin(angle),
      x2: cx + outerR * Math.cos(angle),
      y2: cy + outerR * Math.sin(angle),
      isMajor,
    };
  });

  // Needle position
  const needleAngle = Math.PI + (clampedScore / 100) * Math.PI;
  const needleLen = trackRadius - 25;
  const needleX = cx + needleLen * Math.cos(needleAngle);
  const needleY = cy + needleLen * Math.sin(needleAngle);

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative" style={{ width: size, height: size / 2 + 40 }}>
        {/* Glow backdrop */}
        <div
          className="absolute inset-0 rounded-full opacity-30 blur-3xl"
          style={{
            background: `radial-gradient(ellipse at 50% 100%, ${glowColor}, transparent 70%)`,
          }}
        />

        <svg
          width={size}
          height={size / 2 + 40}
          viewBox={`0 0 ${size} ${size / 2 + 40}`}
          className="relative z-10"
        >
          {/* Glow filter */}
          <defs>
            <filter id="gauge-glow">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Tick marks */}
          {ticks.map((t, i) => (
            <line
              key={i}
              x1={t.x1} y1={t.y1}
              x2={t.x2} y2={t.y2}
              stroke={t.isMajor ? "hsl(0, 0%, 40%)" : "hsl(0, 0%, 20%)"}
              strokeWidth={t.isMajor ? 2 : 1}
              strokeLinecap="round"
            />
          ))}

          {/* Track (dim) */}
          <path
            d={`M ${cx - trackRadius} ${cy} A ${trackRadius} ${trackRadius} 0 0 1 ${cx + trackRadius} ${cy}`}
            fill="none"
            stroke="hsl(0, 0%, 12%)"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Filled arc */}
          <motion.path
            d={`M ${cx - trackRadius} ${cy} A ${trackRadius} ${trackRadius} 0 0 1 ${cx + trackRadius} ${cy}`}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={arcLength}
            initial={{ strokeDashoffset: arcLength }}
            animate={{ strokeDashoffset: arcLength - filledLength }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            filter="url(#gauge-glow)"
          />

          {/* Needle */}
          <motion.line
            x1={cx} y1={cy}
            initial={{ x2: cx - needleLen, y2: cy }}
            animate={{ x2: needleX, y2: needleY }}
            transition={{ duration: 1.2, ease: "easeOut" }}
            stroke="hsl(0, 0%, 85%)"
            strokeWidth={2}
            strokeLinecap="round"
          />
          <circle cx={cx} cy={cy} r={5} fill="hsl(0, 0%, 70%)" />
          <circle cx={cx} cy={cy} r={2} fill="hsl(0, 0%, 30%)" />
        </svg>

        {/* Score in center */}
        <div
          className="absolute z-20 flex flex-col items-center"
          style={{ left: cx, bottom: 12, transform: "translateX(-50%)" }}
        >
          <span
            className="font-mono text-6xl font-black tabular-nums leading-none"
            style={{ color }}
          >
            {displayScore}
          </span>
          <span className="font-mono text-xs text-muted-foreground mt-1">/100</span>
        </div>
      </div>

      {/* Badge */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1, duration: 0.4 }}
        className={`px-4 py-1.5 rounded-full ${badgeBg} border border-white/5`}
      >
        <span className={`font-mono text-xs font-bold tracking-widest ${badgeText}`}>
          {label}
        </span>
      </motion.div>
    </div>
  );
};
