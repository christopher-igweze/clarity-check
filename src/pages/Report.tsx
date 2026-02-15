import { Shield } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Report = () => {
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

      <main className="relative z-10 max-w-5xl mx-auto px-6 pt-12">
        <h1 className="text-3xl font-bold mb-2">Production Health Report</h1>
        <p className="text-muted-foreground mb-8">Report shell — will be populated after scan completes.</p>

        <div className="glass rounded-xl p-16 text-center">
          <p className="text-muted-foreground">No report data yet. Run a scan first.</p>
        </div>
      </main>
    </div>
  );
};

export default Report;
