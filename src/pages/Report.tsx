import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Shield, ArrowLeft, AlertTriangle, Lock, Bug, TrendingUp, CheckCircle2, Circle, Clock, RefreshCw, Lightbulb, Briefcase, ShieldCheck, ShieldAlert, ShieldX, Terminal, XCircle } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { getClerkToken } from "@/integrations/clerk/tokenStore";

interface ActionItem {
  id: string;
  category: string;
  severity: string;
  title: string;
  description: string | null;
  file_path: string | null;
  line_number: number | null;
  fix_status: string;
  why_it_matters: string | null;
  cto_perspective: string | null;
}

interface Summary {
  health_score: number;
  security_score: number;
  reliability_score: number;
  scalability_score: number;
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

const statusConfig: Record<string, { icon: typeof Circle; label: string; next: string }> = {
  open: { icon: Circle, label: "Open", next: "in_progress" },
  in_progress: { icon: Clock, label: "In Progress", next: "fixed" },
  fixed: { icon: CheckCircle2, label: "Fixed", next: "open" },
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
      <div className="relative" style={{ width: svgSize, height: svgSize }}>
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
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold ${size === "lg" ? "text-4xl" : "text-lg"}`}>{score}</span>
          {size === "lg" && <span className="text-xs text-muted-foreground">/ 100</span>}
        </div>
      </div>
      <span className={`font-medium ${size === "lg" ? "text-sm" : "text-xs"} text-muted-foreground`}>{label}</span>
    </div>
  );
}

const Report = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [actionItems, setActionItems] = useState<ActionItem[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [securityReview, setSecurityReview] = useState<any>(null);
  const [deepProbe, setDeepProbe] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [scanTier, setScanTier] = useState("");
  const [repoName, setRepoName] = useState("");
  const [projectId, setProjectId] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [filter, setFilter] = useState<"all" | "open" | "in_progress" | "fixed">("all");
  const [educationCards, setEducationCards] = useState<Record<string, { why_it_matters: string; cto_perspective: string }>>({});
  const [educationLoading, setEducationLoading] = useState(false);
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const loadReport = async () => {
      // Load report + project info
      const { data: report } = await supabase
        .from("scan_reports")
        .select("*, projects(repo_name, repo_url)")
        .eq("id", id)
        .single();

      if (!report) { setLoading(false); return; }

      setScanTier(report.scan_tier);
      setProjectId(report.project_id);
      setSecurityReview((report as any).security_review || null);
      const reportData = (report as any).report_data as any;
      setDeepProbe(reportData?.deep_probe || null);
      const project = report.projects as unknown as { repo_name: string; repo_url: string } | null;
      setRepoName(project?.repo_name || project?.repo_url || "Unknown");
      setRepoUrl(project?.repo_url || "");

      if (report.health_score) {
        setSummary({
          health_score: report.health_score,
          security_score: report.security_score || 0,
          reliability_score: report.reliability_score || 0,
          scalability_score: report.scalability_score || 0,
        });
      }

      // Load action items
      const { data: items } = await supabase
        .from("action_items")
        .select("*")
        .eq("scan_report_id", id)
        .order("created_at", { ascending: true });

      if (items) setActionItems(items);
      setLoading(false);
    };

    loadReport();
  }, [id]);

  const toggleStatus = async (item: ActionItem) => {
    const nextStatus = statusConfig[item.fix_status]?.next || "open";
    const { error } = await supabase
      .from("action_items")
      .update({ fix_status: nextStatus })
      .eq("id", item.id);

    if (error) {
      toast({ title: "Error", description: "Failed to update status.", variant: "destructive" });
      return;
    }

    setActionItems((prev) =>
      prev.map((ai) => ai.id === item.id ? { ...ai, fix_status: nextStatus } : ai)
    );
  };

  const fetchEducation = async () => {
    if (actionItems.length === 0) return;
    setEducationLoading(true);
    try {
      const findings = actionItems.slice(0, 10).map((item) => ({
        id: item.id,
        title: item.title,
        description: item.description,
        category: item.category,
        severity: item.severity,
        file_path: item.file_path,
      }));

      const token = await getClerkToken();
      if (!token) throw new Error("Authentication token missing. Please sign in again.");

      const resp = await fetch(`${import.meta.env.VITE_SUPABASE_URL}/functions/v1/generate-education`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ findings }),
      });

      if (!resp.ok) throw new Error("Failed to generate education cards");
      const data = await resp.json();
      const content = data.choices?.[0]?.message?.content || "";

      // Parse JSON objects from response
      const cards: Record<string, { why_it_matters: string; cto_perspective: string }> = {};
      for (const line of content.split("\n")) {
        try {
          const obj = JSON.parse(line.trim());
          if (obj.finding_id) cards[obj.finding_id] = { why_it_matters: obj.why_it_matters, cto_perspective: obj.cto_perspective };
        } catch {
          // Try parsing entire content as JSON array
        }
      }

      // If no line-by-line parsing worked, try as array
      if (Object.keys(cards).length === 0) {
        try {
          const arr = JSON.parse(content);
          if (Array.isArray(arr)) {
            arr.forEach((obj: { finding_id: string; why_it_matters: string; cto_perspective: string }) => {
              if (obj.finding_id) cards[obj.finding_id] = { why_it_matters: obj.why_it_matters, cto_perspective: obj.cto_perspective };
            });
          }
        } catch { /* ignore */ }
      }

      setEducationCards(cards);

      // Persist to action_items
      for (const [itemId, card] of Object.entries(cards)) {
        await supabase
          .from("action_items")
          .update({ why_it_matters: card.why_it_matters, cto_perspective: card.cto_perspective })
          .eq("id", itemId);
      }
    } catch (err) {
      toast({ title: "Error", description: "Failed to generate educational cards.", variant: "destructive" });
    }
    setEducationLoading(false);
  };

  const handleRescan = () => {
    if (projectId && repoUrl) {
      navigate("/scan/live", {
        state: { projectId, repoUrl, tier: scanTier || "surface" },
      });
    }
  };

  const filteredItems = filter === "all" ? actionItems : actionItems.filter((i) => i.fix_status === filter);

  const groupedFindings = filteredItems.reduce<Record<string, ActionItem[]>>((acc, f) => {
    const cat = f.category || "other";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(f);
    return acc;
  }, {});

  const counts = {
    all: actionItems.length,
    open: actionItems.filter((i) => i.fix_status === "open").length,
    in_progress: actionItems.filter((i) => i.fix_status === "in_progress").length,
    fixed: actionItems.filter((i) => i.fix_status === "fixed").length,
  };

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
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-1">Production Health Report</h1>
            <p className="text-muted-foreground font-mono text-sm">{repoName}</p>
            <Badge variant="outline" className="mt-2 text-xs">{scanTier === "deep" ? "🔬 Deep Probe" : "⚡ Surface Scan"}</Badge>
          </div>
          <div className="flex items-center gap-2">
            {actionItems.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={fetchEducation}
                disabled={educationLoading}
                className="border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/10"
              >
                <Lightbulb className="w-4 h-4 mr-1" />
                {educationLoading ? "Generating..." : "Why This Matters"}
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={handleRescan}>
              <RefreshCw className="w-4 h-4 mr-1" /> Rescan
            </Button>
          </div>
        </div>

        {/* Score Dashboard */}
        {summary && (
          <Card className="glass-strong mb-8">
            <CardContent className="pt-8 pb-8">
              <div className="flex flex-col md:flex-row items-center justify-around gap-8">
                <ScoreGauge score={summary.health_score} label="Health Score" size="lg" />
                <Separator orientation="vertical" className="hidden md:block h-32" />
                <div className="grid grid-cols-3 gap-8">
                  <ScoreGauge score={summary.security_score} label="Security" size="sm" />
                  <ScoreGauge score={summary.reliability_score} label="Reliability" size="sm" />
                  <ScoreGauge score={summary.scalability_score} label="Scalability" size="sm" />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Deep Probe Results */}
        {deepProbe && (
          <Card className="glass-strong mb-8 border-neon-orange/20">
            <CardContent className="pt-6 pb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-neon-orange/10 flex items-center justify-center">
                  <Terminal className="w-5 h-5 text-neon-orange" />
                </div>
                <div>
                  <h2 className="text-lg font-bold">Deep Probe Results</h2>
                  <p className="text-xs text-muted-foreground">Agent_SRE • Daytona Sandbox</p>
                </div>
                <Badge className="ml-auto bg-neon-orange/20 text-neon-orange border-neon-orange/30 text-[10px]">Dynamic</Badge>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                {[
                  { label: "Install", ok: deepProbe.install_ok },
                  { label: "Build", ok: deepProbe.build_ok },
                  { label: "Tests", ok: deepProbe.tests_ok },
                  { label: "Audit", ok: (deepProbe.audit_vulnerabilities || 0) === 0 },
                ].map((item) => (
                  <div key={item.label} className={`rounded-lg p-3 text-center ${item.ok ? "bg-neon-green/10 border border-neon-green/20" : "bg-neon-red/10 border border-neon-red/20"}`}>
                    {item.ok ? (
                      <CheckCircle2 className="w-6 h-6 mx-auto mb-1 text-neon-green" />
                    ) : (
                      <XCircle className="w-6 h-6 mx-auto mb-1 text-neon-red" />
                    )}
                    <span className="text-xs font-semibold">{item.label}</span>
                  </div>
                ))}
              </div>

              {(deepProbe.tests_passed !== null || deepProbe.tests_failed !== null) && (
                <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
                  {deepProbe.tests_passed !== null && <span className="text-neon-green">✅ {deepProbe.tests_passed} passed</span>}
                  {deepProbe.tests_failed !== null && deepProbe.tests_failed > 0 && <span className="text-neon-red">❌ {deepProbe.tests_failed} failed</span>}
                </div>
              )}

              {deepProbe.audit_vulnerabilities > 0 && (
                <div className="text-xs p-2 rounded bg-neon-orange/5 border border-neon-orange/10">
                  <span className="font-semibold text-neon-orange">⚠️ npm audit:</span> {deepProbe.audit_vulnerabilities} vulnerabilities found
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Security Officer Verdict */}
        {securityReview && (
          <Card className="glass-strong mb-8 border-neon-red/20">
            <CardContent className="pt-6 pb-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-neon-red/10 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-neon-red" />
                </div>
                <div>
                  <h2 className="text-lg font-bold">Security Officer Verdict</h2>
                  <p className="text-xs text-muted-foreground">Agent_Security • DeepSeek Reasoner</p>
                </div>
              </div>

              {securityReview.raw ? (
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">{securityReview.raw}</p>
              ) : Array.isArray(securityReview) ? (
                <div className="space-y-3">
                  {securityReview.map((item: any, i: number) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-secondary/50">
                      {item.verdict === "confirmed" ? (
                        <ShieldAlert className="w-4 h-4 text-neon-orange mt-0.5 shrink-0" />
                      ) : item.verdict === "false_positive" ? (
                        <ShieldX className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
                      ) : (
                        <ShieldCheck className="w-4 h-4 text-neon-green mt-0.5 shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={item.verdict === "confirmed" ? "destructive" : "secondary"} className="text-[10px]">
                            {item.verdict}
                          </Badge>
                          {item.confidence && (
                            <span className="text-[10px] text-muted-foreground">{item.confidence}% confidence</span>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground">{item.reasoning}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : securityReview.verdict ? (
                <div className="flex items-start gap-3 p-4 rounded-lg bg-secondary/50">
                  {securityReview.verdict === "approved" ? (
                    <ShieldCheck className="w-6 h-6 text-neon-green shrink-0" />
                  ) : (
                    <ShieldX className="w-6 h-6 text-neon-red shrink-0" />
                  )}
                  <div>
                    <p className="font-semibold text-sm mb-1">
                      {securityReview.verdict === "approved" ? "✅ Approved" : "🚫 Vetoed"}
                    </p>
                    <p className="text-xs text-muted-foreground">{securityReview.reasoning}</p>
                    {securityReview.vulnerabilities_found?.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {securityReview.vulnerabilities_found.map((v: any, i: number) => (
                          <div key={i} className="text-xs p-2 rounded bg-neon-red/5 border border-neon-red/10">
                            <span className="font-semibold text-neon-red">[{v.severity?.toUpperCase()}]</span>{" "}
                            {v.type}: {v.description}
                            {v.file && <span className="block font-mono text-muted-foreground mt-0.5">📄 {v.file}</span>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">{JSON.stringify(securityReview, null, 2)}</p>
              )}
            </CardContent>
          </Card>
        )}
        {/* Fix Status Filter */}
        {actionItems.length > 0 && (
          <div className="flex items-center gap-2 mb-6 flex-wrap">
            {(["all", "open", "in_progress", "fixed"] as const).map((f) => (
              <Button
                key={f}
                variant={filter === f ? "default" : "outline"}
                size="sm"
                onClick={() => setFilter(f)}
                className={filter === f ? "" : "border-border"}
              >
                {f === "all" ? "All" : statusConfig[f]?.label || f}
                <Badge variant="secondary" className="ml-1.5 text-[10px] px-1.5">{counts[f]}</Badge>
              </Button>
            ))}
          </div>
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
                {categoryFindings.map((item) => {
                  const sev = severityConfig[item.severity] || severityConfig.low;
                  const status = statusConfig[item.fix_status] || statusConfig.open;
                  const StatusIcon = status.icon;

                  return (
                    <Card key={item.id} className={`glass hover:border-primary/20 transition-colors ${item.fix_status === "fixed" ? "opacity-60" : ""}`}>
                      <CardContent className="py-4 px-5">
                        <div className="flex items-start gap-3">
                          <button
                            onClick={() => toggleStatus(item)}
                            className="mt-1 shrink-0 group"
                            title={`Click to mark as ${status.next}`}
                          >
                            <StatusIcon className={`w-5 h-5 transition-colors ${
                              item.fix_status === "fixed" ? "text-neon-green" :
                              item.fix_status === "in_progress" ? "text-neon-orange" :
                              "text-muted-foreground group-hover:text-primary"
                            }`} />
                          </button>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 flex-wrap mb-1">
                              <span className={`font-semibold text-sm ${item.fix_status === "fixed" ? "line-through" : ""}`}>{item.title}</span>
                              <Badge className={`${sev.color} text-[10px] px-1.5 py-0`}>{sev.label}</Badge>
                              {item.fix_status !== "open" && (
                                <Badge variant="outline" className="text-[10px] px-1.5 py-0">{status.label}</Badge>
                              )}
                            </div>
                            {item.description && (
                              <p className="text-sm text-muted-foreground leading-relaxed">{item.description}</p>
                            )}
                            {item.file_path && (
                              <p className="text-xs font-mono text-muted-foreground mt-1.5">
                                📄 {item.file_path}{item.line_number ? `:${item.line_number}` : ""}
                              </p>
                             )}
                            {/* Education Cards */}
                            {(educationCards[item.id] || item.why_it_matters) && (
                              <div className="mt-3 space-y-2">
                                <button
                                  onClick={() => setExpandedCard(expandedCard === item.id ? null : item.id)}
                                  className="text-xs text-neon-cyan hover:underline flex items-center gap-1"
                                >
                                  <Lightbulb className="w-3 h-3" />
                                  {expandedCard === item.id ? "Hide insights" : "Why this matters"}
                                </button>
                                {expandedCard === item.id && (
                                  <div className="space-y-2 pl-4 border-l-2 border-neon-cyan/30">
                                    <div>
                                      <span className="text-[10px] font-semibold text-neon-cyan uppercase tracking-wider flex items-center gap-1">
                                        <Lightbulb className="w-3 h-3" /> Why This Matters
                                      </span>
                                      <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                                        {educationCards[item.id]?.why_it_matters || item.why_it_matters}
                                      </p>
                                    </div>
                                    <div>
                                      <span className="text-[10px] font-semibold text-neon-orange uppercase tracking-wider flex items-center gap-1">
                                        <Briefcase className="w-3 h-3" /> CTO's Perspective
                                      </span>
                                      <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">
                                        {educationCards[item.id]?.cto_perspective || item.cto_perspective}
                                      </p>
                                    </div>
                                  </div>
                                )}
                              </div>
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

        {actionItems.length === 0 && !summary && (
          <Card className="glass">
            <CardContent className="py-16 text-center">
              <CheckCircle2 className="w-12 h-12 text-primary mx-auto mb-4" />
              <p className="text-muted-foreground">No findings yet. The report will populate after a scan completes.</p>
            </CardContent>
          </Card>
        )}

        {actionItems.length === 0 && summary && (
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
