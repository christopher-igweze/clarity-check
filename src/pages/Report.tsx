import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Shield, ArrowLeft, AlertTriangle, Lock, Bug, TrendingUp, Lightbulb, CheckCircle2, XCircle } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";

interface Finding {
  type: string;
  category: string;
  severity: string;
  title: string;
  description: string;
  file_path?: string;
  line_number?: number;
}

interface Summary {
  type: string;
  health_score: number;
  security_score: number;
  reliability_score: number;
  scalability_score: number;
  total_findings: number;
}

interface ReportData {
  raw_response: string;
}

const severityConfig: Record<string, { color: string; label: string; emoji: string }> = {
  critical: { color: "bg-neon-red text-primary-foreground", label: "Critical", emoji: "🔴" },
  high: { color: "bg-neon-orange text-primary-foreground", label: "High", emoji: "🟠" },
  medium: { color: "bg-yellow-500 text-primary-foreground", label: "Medium", emoji: "🟡" },
  low: { color: "bg-neon-green text-primary-foreground", label: "Low", emoji: "🟢" },
};

const categoryConfig: Record<string, { icon: typeof Lock; color: string; label: string }> = {
  security: { icon: Lock, color: "text-neon-red", label: "Security" },
  reliability: { icon: Bug, color: "text-neon-orange", label: "Reliability" },
  scalability: { icon: TrendingUp, color: "text-neon-cyan", label: "Scalability" },
};

function ScoreGauge({ score, label, size = "lg" }: { score: number; label: string; size?: "sm" | "lg" }) {
  const radius = size === "lg" ? 70 : 36;
  const stroke = size === "lg" ? 8 : 5;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const svgSize = (radius + stroke) * 2;

  const scoreColor =
    score >= 80 ? "hsl(var(--neon-green))" :
    score >= 50 ? "hsl(var(--neon-orange))" :
    "hsl(var(--neon-red))";

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={svgSize} height={svgSize} className="transform -rotate-90">
        <circle cx={radius + stroke} cy={radius + stroke} r={radius} fill="none" stroke="hsl(var(--secondary))" strokeWidth={stroke} />
        <circle
          cx={radius + stroke} cy={radius + stroke} r={radius} fill="none"
          stroke={scoreColor} strokeWidth={stroke}
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{ width: svgSize, height: svgSize }}>
        <span className={`font-bold ${size === "lg" ? "text-4xl" : "text-lg"}`}>{score}</span>
        {size === "lg" && <span className="text-xs text-muted-foreground">/ 100</span>}
      </div>
      <span className={`font-medium ${size === "lg" ? "text-sm" : "text-xs"} text-muted-foreground`}>{label}</span>
    </div>
  );
}

const Report = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [scanTier, setScanTier] = useState("");
  const [repoName, setRepoName] = useState("");

  useEffect(() => {
    if (!id) return;

    const loadReport = async () => {
      const { data: report } = await supabase
        .from("scan_reports")
        .select("*, projects(repo_name, repo_url)")
        .eq("id", id)
        .single();

      if (!report) {
        setLoading(false);
        return;
      }

      setScanTier(report.scan_tier);
      const project = report.projects as unknown as { repo_name: string; repo_url: string } | null;
      setRepoName(project?.repo_name || project?.repo_url || "Unknown");

      // Use direct scores if available
      if (report.health_score) {
        setSummary({
          type: "summary",
          health_score: report.health_score,
          security_score: report.security_score || 0,
          reliability_score: report.reliability_score || 0,
          scalability_score: report.scalability_score || 0,
          total_findings: 0,
        });
      }

      // Parse raw_response from report_data for findings
      const reportData = report.report_data as unknown as ReportData | null;
      if (reportData?.raw_response) {
        const parsedFindings: Finding[] = [];
        let parsedSummary: Summary | null = null;

        for (const line of reportData.raw_response.split("\n")) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          try {
            const obj = JSON.parse(trimmed);
            if (obj.type === "finding") parsedFindings.push(obj);
            if (obj.type === "summary") parsedSummary = obj;
          } catch {
            // skip non-JSON lines
          }
        }

        setFindings(parsedFindings);
        if (parsedSummary && !report.health_score) setSummary(parsedSummary);
      }

      // Also load action_items for this report
      const { data: actionItems } = await supabase
        .from("action_items")
        .select("*")
        .eq("scan_report_id", id);

      if (actionItems && actionItems.length > 0 && findings.length === 0) {
        setFindings(actionItems.map((item) => ({
          type: "finding",
          category: item.category,
          severity: item.severity,
          title: item.title,
          description: item.description || "",
          file_path: item.file_path || undefined,
          line_number: item.line_number || undefined,
        })));
      }

      setLoading(false);
    };

    loadReport();
  }, [id]);

  const groupedFindings = findings.reduce<Record<string, Finding[]>>((acc, f) => {
    const cat = f.category || "other";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(f);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse-neon" />
          Loading report...
        </div>
      </div>
    );
  }

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
        <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}>
          <ArrowLeft className="w-4 h-4 mr-1" /> Dashboard
        </Button>
      </nav>

      <main className="relative z-10 max-w-5xl mx-auto px-6 pt-8 pb-20">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-1">Production Health Report</h1>
          <p className="text-muted-foreground font-mono text-sm">{repoName}</p>
          <Badge variant="outline" className="mt-2 text-xs">{scanTier === "deep" ? "🔬 Deep Probe" : "⚡ Surface Scan"}</Badge>
        </div>

        {/* Score Dashboard */}
        {summary && (
          <Card className="glass-strong mb-8">
            <CardContent className="pt-8 pb-8">
              <div className="flex flex-col md:flex-row items-center justify-around gap-8">
                <div className="relative">
                  <ScoreGauge score={summary.health_score} label="Health Score" size="lg" />
                </div>
                <Separator orientation="vertical" className="hidden md:block h-32" />
                <div className="grid grid-cols-3 gap-8">
                  <div className="relative">
                    <ScoreGauge score={summary.security_score} label="Security" size="sm" />
                  </div>
                  <div className="relative">
                    <ScoreGauge score={summary.reliability_score} label="Reliability" size="sm" />
                  </div>
                  <div className="relative">
                    <ScoreGauge score={summary.scalability_score} label="Scalability" size="sm" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Findings by Category */}
        {Object.entries(groupedFindings).map(([category, categoryFindings]) => {
          const config = categoryConfig[category] || { icon: AlertTriangle, color: "text-muted-foreground", label: category };
          const Icon = config.icon;

          return (
            <div key={category} className="mb-8">
              <div className="flex items-center gap-2 mb-4">
                <Icon className={`w-5 h-5 ${config.color}`} />
                <h2 className="text-xl font-semibold">{config.label}</h2>
                <Badge variant="secondary" className="ml-2">{categoryFindings.length}</Badge>
              </div>

              <div className="space-y-3">
                {categoryFindings.map((finding, i) => {
                  const sev = severityConfig[finding.severity] || severityConfig.low;
                  return (
                    <Card key={i} className="glass hover:border-primary/20 transition-colors">
                      <CardContent className="py-4 px-5">
                        <div className="flex items-start gap-3">
                          <span className="text-lg mt-0.5">{sev.emoji}</span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap mb-1">
                              <span className="font-semibold text-sm">{finding.title}</span>
                              <Badge className={`${sev.color} text-[10px] px-1.5 py-0`}>{sev.label}</Badge>
                            </div>
                            <p className="text-sm text-muted-foreground leading-relaxed">{finding.description}</p>
                            {finding.file_path && (
                              <p className="text-xs font-mono text-muted-foreground mt-1.5">
                                📄 {finding.file_path}{finding.line_number ? `:${finding.line_number}` : ""}
                              </p>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          );
        })}

        {findings.length === 0 && !summary && (
          <Card className="glass">
            <CardContent className="py-16 text-center">
              <CheckCircle2 className="w-12 h-12 text-primary mx-auto mb-4" />
              <p className="text-muted-foreground">No findings yet. The report will populate after a scan completes.</p>
            </CardContent>
          </Card>
        )}

        {findings.length === 0 && summary && (
          <Card className="glass">
            <CardContent className="py-16 text-center">
              <CheckCircle2 className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">Clean Bill of Health</h3>
              <p className="text-muted-foreground">No issues found. Your codebase looks production-ready.</p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default Report;
