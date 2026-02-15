import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Shield, ArrowLeft, Plus, Clock, ExternalLink, Trash2 } from "lucide-react";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface Project {
  id: string;
  repo_url: string;
  repo_name: string | null;
  latest_health_score: number | null;
  latest_scan_tier: string | null;
  scan_count: number;
  vibe_prompt: string | null;
}

interface ScanReport {
  id: string;
  scan_tier: string;
  status: string;
  health_score: number | null;
  security_score: number | null;
  reliability_score: number | null;
  scalability_score: number | null;
  created_at: string;
  completed_at: string | null;
}

const ProjectDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [scans, setScans] = useState<ScanReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchData = async () => {
      const [projectRes, scansRes] = await Promise.all([
        supabase.from("projects").select("*").eq("id", id).single(),
        supabase.from("scan_reports").select("*").eq("project_id", id).order("created_at", { ascending: true }),
      ]);
      setProject(projectRes.data as Project | null);
      setScans((scansRes.data as ScanReport[]) || []);
      setLoading(false);
    };
    fetchData();
  }, [id]);

  const completedScans = scans.filter((s) => s.status === "completed" && s.health_score !== null);

  const chartData = completedScans.map((s) => ({
    date: new Date(s.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
    health: s.health_score,
    security: s.security_score,
    reliability: s.reliability_score,
    scalability: s.scalability_score,
  }));

  const handleDelete = async () => {
    if (!id) return;
    const { error } = await supabase.from("projects").delete().eq("id", id);
    if (error) {
      toast({ title: "Error", description: "Failed to delete project.", variant: "destructive" });
      return;
    }
    toast({ title: "Deleted", description: "Project deleted successfully." });
    navigate("/dashboard");
  };

  const scoreColor = (score: number | null) => {
    if (score === null) return "text-muted-foreground";
    if (score >= 80) return "text-neon-green";
    if (score >= 50) return "text-neon-orange";
    return "text-neon-red";
  };

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex items-center gap-3 text-muted-foreground">
          <div className="w-2 h-2 rounded-full bg-primary animate-pulse-neon" />
          Loading project...
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Project not found.</p>
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
        {/* Header */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-1">{project.repo_name || project.repo_url}</h1>
            <p className="text-muted-foreground font-mono text-sm">{project.repo_url}</p>
            <div className="flex items-center gap-2 mt-2">
              {project.latest_scan_tier && (
                <Badge variant="outline" className="text-xs">
                  {project.latest_scan_tier === "surface" ? "⚡ Surface" : "🔬 Deep"}
                </Badge>
              )}
              <span className="text-xs text-muted-foreground">{project.scan_count} scan{project.scan_count !== 1 ? "s" : ""}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => navigate("/scan/live", {
                state: { projectId: project.id, repoUrl: project.repo_url, tier: project.latest_scan_tier || "surface" },
              })}
              className="neon-glow-green"
            >
              <Plus className="w-4 h-4 mr-1" /> New Scan
            </Button>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" size="icon" className="border-destructive/30 text-destructive hover:bg-destructive/10">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Project</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will permanently delete this project and all its scan reports. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>

        {/* Current Score */}
        {project.latest_health_score !== null && (
          <Card className="glass-strong mb-8">
            <CardContent className="py-6 flex items-center gap-6">
              <div className={`text-5xl font-bold font-mono ${scoreColor(project.latest_health_score)}`}>
                {project.latest_health_score}
              </div>
              <div>
                <p className="font-semibold">Current Health Score</p>
                <p className="text-sm text-muted-foreground">
                  {project.latest_health_score >= 80 ? "Production-ready" :
                   project.latest_health_score >= 50 ? "Needs attention" : "Critical issues detected"}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Score Trend Chart */}
        {chartData.length >= 2 && (
          <Card className="glass mb-8">
            <CardHeader>
              <CardTitle className="text-lg">Score Trends</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis dataKey="date" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px",
                      color: "hsl(var(--foreground))",
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="health" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 4 }} name="Health" />
                  <Line type="monotone" dataKey="security" stroke="hsl(var(--neon-red))" strokeWidth={1.5} dot={{ r: 3 }} name="Security" />
                  <Line type="monotone" dataKey="reliability" stroke="hsl(var(--neon-orange))" strokeWidth={1.5} dot={{ r: 3 }} name="Reliability" />
                  <Line type="monotone" dataKey="scalability" stroke="hsl(var(--neon-cyan))" strokeWidth={1.5} dot={{ r: 3 }} name="Scalability" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {chartData.length === 1 && (
          <Card className="glass mb-8">
            <CardContent className="py-8 text-center">
              <p className="text-sm text-muted-foreground">Run at least 2 scans to see score trends over time.</p>
            </CardContent>
          </Card>
        )}

        {/* Scan History */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Scan History</h2>
          <div className="space-y-2">
            {scans.slice().reverse().map((scan) => (
              <div
                key={scan.id}
                className="glass rounded-lg px-5 py-3 flex items-center justify-between hover:border-primary/20 transition-colors cursor-pointer"
                onClick={() => scan.status === "completed" ? navigate(`/report/${scan.id}`) : undefined}
              >
                <div className="flex items-center gap-3">
                  <span className={`font-mono font-bold text-lg ${scoreColor(scan.health_score)}`}>
                    {scan.health_score ?? "—"}
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-[10px]">
                        {scan.scan_tier === "surface" ? "⚡" : "🔬"} {scan.scan_tier}
                      </Badge>
                      <Badge variant={scan.status === "completed" ? "default" : "secondary"} className="text-[10px]">
                        {scan.status}
                      </Badge>
                    </div>
                    {scan.health_score !== null && (
                      <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                        <span>🔒 {scan.security_score ?? "—"}</span>
                        <span>🐛 {scan.reliability_score ?? "—"}</span>
                        <span>📈 {scan.scalability_score ?? "—"}</span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {timeAgo(scan.created_at)}
                  </span>
                  {scan.status === "completed" && <ExternalLink className="w-3.5 h-3.5 text-muted-foreground" />}
                </div>
              </div>
            ))}
          </div>
        </div>

        {scans.length === 0 && (
          <Card className="glass">
            <CardContent className="py-16 text-center">
              <p className="text-muted-foreground">No scans yet. Start your first scan above.</p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default ProjectDetail;
