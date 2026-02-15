import { Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";

const ScanLive = () => {
  const navigate = useNavigate();

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
      </nav>

      <main className="relative z-10 max-w-4xl mx-auto px-6 pt-12">
        <h1 className="text-3xl font-bold mb-2">Scanning...</h1>
        <p className="text-muted-foreground mb-8">The Thinking Stream — watch agents analyze your code in real-time.</p>

        <div className="glass-strong rounded-xl overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
            <div className="w-3 h-3 rounded-full bg-neon-red/80" />
            <div className="w-3 h-3 rounded-full bg-neon-orange/80" />
            <div className="w-3 h-3 rounded-full bg-neon-green/80" />
            <span className="ml-3 text-xs font-mono text-muted-foreground">the-thinking-stream</span>
          </div>
          <div className="p-6 font-mono text-sm min-h-[400px]">
            <p className="text-muted-foreground">Waiting for scan to start...</p>
            <p className="text-primary animate-pulse-neon mt-2">█</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ScanLive;
