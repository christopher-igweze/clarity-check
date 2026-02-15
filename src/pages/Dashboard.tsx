import { useAuth } from "@/contexts/AuthContext";
import { Shield, LogOut, FolderGit2, Plus, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

interface Project {
  id: string;
  repo_url: string;
  repo_name: string | null;
  latest_health_score: number | null;
  latest_scan_tier: string | null;
  scan_count: number;
  created_at: string;
}

const Dashboard = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const githubUsername = user?.user_metadata?.user_name || user?.email || "User";
  const avatarUrl = user?.user_metadata?.avatar_url;

  useEffect(() => {
    if (!user) return;
    const fetchProjects = async () => {
      const { data } = await supabase
        .from("projects")
        .select("*")
        .order("created_at", { ascending: false });
      setProjects((data as Project[]) || []);
      setLoading(false);
    };
    fetchProjects();
  }, [user]);

  const scoreColor = (score: number | null) => {
    if (score === null) return "text-muted-foreground";
    if (score >= 80) return "text-neon-green";
    if (score >= 50) return "text-neon-orange";
    return "text-neon-red";
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-pattern opacity-40 pointer-events-none" />

      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/")}>
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Vibe</span>
            <span className="text-foreground">2Prod</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {avatarUrl && (
              <img src={avatarUrl} alt="avatar" className="w-8 h-8 rounded-full border border-border" />
            )}
            <span className="text-sm text-muted-foreground">{githubUsername}</span>
          </div>
          <Button variant="ghost" size="icon" onClick={signOut}>
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </nav>

      <main className="relative z-10 max-w-5xl mx-auto px-6 pt-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">My Projects</h1>
          <Button onClick={() => navigate("/scan/new")} className="neon-glow-green">
            <Plus className="w-4 h-4 mr-2" />
            New Scan
          </Button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : projects.length === 0 ? (
          <div className="glass rounded-xl p-16 text-center">
            <FolderGit2 className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">No projects yet</h2>
            <p className="text-muted-foreground mb-6">
              Connect a GitHub repo to get your first Production Health Score.
            </p>
            <Button onClick={() => navigate("/scan/new")} className="neon-glow-green">
              Scan Your First Repo
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {projects.map((project) => (
              <div
                key={project.id}
                className="glass rounded-xl p-6 flex items-center justify-between hover:border-primary/20 transition-colors cursor-pointer"
                onClick={() => navigate("/scan/new")}
              >
                <div className="flex items-center gap-4">
                  <div className={`text-3xl font-bold font-mono ${scoreColor(project.latest_health_score)}`}>
                    {project.latest_health_score ?? "—"}
                  </div>
                  <div>
                    <h3 className="font-semibold">{project.repo_name || project.repo_url}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {project.latest_scan_tier && (
                        <Badge variant="outline" className="text-xs">
                          {project.latest_scan_tier === "surface" ? "⚡ Surface" : "🔬 Deep"}
                        </Badge>
                      )}
                      <span className="text-xs text-muted-foreground">
                        {project.scan_count} scan{project.scan_count !== 1 ? "s" : ""}
                      </span>
                    </div>
                  </div>
                </div>
                <ExternalLink className="w-4 h-4 text-muted-foreground" />
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
