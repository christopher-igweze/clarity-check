import { useAuth } from "@/contexts/AuthContext";
import { Shield, LogOut, FolderGit2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const githubUsername = user?.user_metadata?.user_name || user?.email || "User";
  const avatarUrl = user?.user_metadata?.avatar_url;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-pattern opacity-40 pointer-events-none" />

      {/* Nav */}
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

      {/* Content */}
      <main className="relative z-10 max-w-5xl mx-auto px-6 pt-12">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">My Projects</h1>
          <Button onClick={() => navigate("/scan/new")} className="neon-glow-green">
            <Plus className="w-4 h-4 mr-2" />
            New Scan
          </Button>
        </div>

        {/* Empty state */}
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
      </main>
    </div>
  );
};

export default Dashboard;
