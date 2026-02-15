import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Shield, ArrowRight, Zap, Microscope, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "@/hooks/use-toast";
import { RepoSelector } from "@/components/RepoSelector";

const NewScan = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [repoUrl, setRepoUrl] = useState("");
  const [vibePrompt, setVibePrompt] = useState("");
  const [tier, setTier] = useState<"surface" | "deep">("surface");
  const [loading, setLoading] = useState(false);

  const handleStartScan = async () => {
    if (!repoUrl.trim() || !user) return;
    setLoading(true);

    try {
      // Extract repo name
      const match = repoUrl.match(/github\.com\/([^/]+)\/([^/]+)/);
      const repoName = match ? `${match[1]}/${match[2].replace(/\.git$/, "")}` : repoUrl;

      // Create project in DB
      const { data: project, error } = await supabase
        .from("projects")
        .insert({
          user_id: user.id,
          repo_url: repoUrl.trim(),
          repo_name: repoName,
          vibe_prompt: vibePrompt || null,
          latest_scan_tier: tier,
        })
        .select()
        .single();

      if (error) throw error;

      // Navigate to scan view with state
      navigate("/scan/live", {
        state: {
          projectId: project.id,
          repoUrl: repoUrl.trim(),
          vibePrompt,
          tier,
        },
      });
    } catch (err) {
      console.error(err);
      toast({
        title: "Error",
        description: "Failed to create project. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

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

      <main className="relative z-10 max-w-2xl mx-auto px-6 pt-12">
        <h1 className="text-3xl font-bold mb-2">New Scan</h1>
        <p className="text-muted-foreground mb-8">Connect your repo and choose a scan depth.</p>

        <div className="space-y-6">
          <RepoSelector value={repoUrl} onChange={setRepoUrl} />

          <div>
            <label className="text-sm font-medium mb-2 block">
              Vibe Prompt <span className="text-muted-foreground">(optional)</span>
            </label>
            <Textarea
              value={vibePrompt}
              onChange={(e) => setVibePrompt(e.target.value)}
              placeholder="The original prompt you used to generate this app, or a description of what it does..."
              className="bg-secondary border-border min-h-[100px]"
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-3 block">Scan Tier</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                onClick={() => setTier("surface")}
                className={`glass rounded-xl p-5 text-left transition-all ${
                  tier === "surface" ? "border-primary/50 neon-glow-green" : "hover:border-primary/20"
                }`}
              >
                <Zap className="w-6 h-6 text-neon-green mb-3" />
                <h3 className="font-semibold mb-1">⚡ Surface Scan</h3>
                <p className="text-xs text-muted-foreground">
                  Static analysis via Gemini 3 Pro. Fast (~15s). Finds hardcoded secrets, architecture issues.
                </p>
              </button>
              <button
                onClick={() => setTier("deep")}
                className={`glass rounded-xl p-5 text-left transition-all ${
                  tier === "deep" ? "border-accent/50 neon-glow-purple" : "hover:border-accent/20"
                }`}
              >
                <Microscope className="w-6 h-6 text-neon-purple mb-3" />
                <h3 className="font-semibold mb-1">🔬 Deep Probe</h3>
                <p className="text-xs text-muted-foreground">
                  Dynamic analysis via Daytona sandbox. Actually runs your code, tests, and build.
                </p>
              </button>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={handleStartScan}
              disabled={!repoUrl.trim() || loading}
              size="lg"
              className="flex-1 neon-glow-green text-base font-semibold"
            >
              {loading ? "Creating project..." : "Start Scan"}
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate("/vision-intake", { state: { repoUrl: repoUrl.trim(), vibePrompt } })}
              disabled={!repoUrl.trim()}
              size="lg"
              className="border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/10"
            >
              <MessageSquare className="mr-2 w-5 h-5" />
              Vision Intake First
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default NewScan;
