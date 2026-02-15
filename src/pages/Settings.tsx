import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Shield, ArrowLeft, User, LogOut, Github, Check, Loader2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast } from "@/hooks/use-toast";

const FUNCTIONS_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1`;

const Settings = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, signOut } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [githubUsername, setGithubUsername] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [githubConnected, setGithubConnected] = useState(false);
  const [saving, setSaving] = useState(false);
  const [connectingGithub, setConnectingGithub] = useState(false);

  useEffect(() => {
    if (!user) return;
    const loadProfile = async () => {
      const { data } = await supabase
        .from("profiles")
        .select("*")
        .eq("user_id", user.id)
        .single();
      if (data) {
        setDisplayName(data.display_name || "");
        setGithubUsername(data.github_username || "");
        setAvatarUrl(data.avatar_url || "");
        setGithubConnected(!!(data as any).github_access_token);
      }
    };
    loadProfile();
  }, [user]);

  // Handle GitHub OAuth callback
  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) return;

    // Wait for user to be available (auth session may still be loading)
    if (!user) {
      console.log("GitHub OAuth: waiting for auth session...");
      return;
    }

    const exchangeCode = async () => {
      setConnectingGithub(true);
      try {
        console.log("GitHub OAuth: exchanging code...");
        const resp = await fetch(`${FUNCTIONS_URL}/github-oauth`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
          },
          body: JSON.stringify({
            action: "exchange_code",
            code,
            redirect_uri: `${window.location.origin}/settings`,
          }),
        });

        const data = await resp.json();
        console.log("GitHub OAuth response:", resp.status, data);
        if (!resp.ok) throw new Error(data.error || "Failed to connect GitHub");

        // Save token to profile
        const { error: updateError } = await supabase
          .from("profiles")
          .update({
            github_username: data.github_username,
            avatar_url: data.avatar_url,
            github_access_token: data.access_token,
          } as any)
          .eq("user_id", user.id);

        if (updateError) {
          console.error("Profile update error:", updateError);
          throw new Error("Failed to save GitHub token");
        }

        setGithubUsername(data.github_username);
        setAvatarUrl(data.avatar_url);
        setGithubConnected(true);
        toast({ title: "GitHub Connected", description: `Connected as ${data.github_username}` });

        // Clean URL
        window.history.replaceState({}, "", "/settings");
      } catch (err) {
        console.error("GitHub OAuth error:", err);
        toast({ title: "Error", description: err instanceof Error ? err.message : "Failed to connect GitHub", variant: "destructive" });
      }
      setConnectingGithub(false);
    };
    exchangeCode();
  }, [searchParams, user]);

  const handleConnectGithub = async () => {
    setConnectingGithub(true);
    try {
      const resp = await fetch(`${FUNCTIONS_URL}/github-oauth`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
        },
        body: JSON.stringify({
          action: "get_auth_url",
          redirect_uri: `${window.location.origin}/settings`,
        }),
      });

      const data = await resp.json();
      if (!resp.ok) throw new Error(data.error || "Failed to get auth URL");

      window.location.href = data.auth_url;
    } catch (err) {
      console.error(err);
      toast({ title: "Error", description: err instanceof Error ? err.message : "Failed to start GitHub auth", variant: "destructive" });
      setConnectingGithub(false);
    }
  };

  const handleDisconnectGithub = async () => {
    if (!user) return;
    await supabase
      .from("profiles")
      .update({ github_access_token: null, github_username: null } as any)
      .eq("user_id", user.id);
    setGithubConnected(false);
    setGithubUsername("");
    toast({ title: "GitHub Disconnected" });
  };

  const handleSave = async () => {
    if (!user) return;
    setSaving(true);
    const { error } = await supabase
      .from("profiles")
      .update({ display_name: displayName })
      .eq("user_id", user.id);

    if (error) {
      toast({ title: "Error", description: "Failed to update profile.", variant: "destructive" });
    } else {
      toast({ title: "Saved", description: "Profile updated successfully." });
    }
    setSaving(false);
  };

  const handleSignOut = async () => {
    await signOut();
    navigate("/");
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
        <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}>
          <ArrowLeft className="w-4 h-4 mr-1" /> Dashboard
        </Button>
      </nav>

      <main className="relative z-10 max-w-2xl mx-auto px-6 pt-8 pb-20">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        {/* GitHub Connection */}
        <Card className="glass mb-6">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Github className="w-5 h-5" /> GitHub Connection
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Connect your GitHub account to scan private repositories and create PRs.
            </p>
            {githubConnected ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm">
                  <Check className="w-4 h-4 text-neon-green" />
                  <span>Connected as <strong>{githubUsername}</strong></span>
                </div>
                <Button variant="outline" size="sm" onClick={handleDisconnectGithub} className="border-destructive/30 text-destructive hover:bg-destructive/10">
                  Disconnect
                </Button>
              </div>
            ) : (
              <Button onClick={handleConnectGithub} disabled={connectingGithub}>
                {connectingGithub ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Connecting...</>
                ) : (
                  <><Github className="w-4 h-4 mr-2" /> Connect GitHub</>
                )}
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Profile */}
        <Card className="glass mb-6">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <User className="w-5 h-5" /> Profile
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              {avatarUrl && (
                <img src={avatarUrl} alt="avatar" className="w-16 h-16 rounded-full border-2 border-border" />
              )}
              <div>
                <p className="font-semibold">{githubUsername || user?.email}</p>
                <p className="text-sm text-muted-foreground">{user?.email}</p>
              </div>
            </div>

            <Separator />

            <div>
              <label className="text-sm font-medium mb-2 block">Display Name</label>
              <Input
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Your display name"
                className="bg-secondary border-border"
              />
            </div>

            <Button onClick={handleSave} disabled={saving} className="neon-glow-green">
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </CardContent>
        </Card>

        {/* Account */}
        <Card className="glass">
          <CardHeader>
            <CardTitle className="text-lg">Account</CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={handleSignOut} className="border-destructive/30 text-destructive hover:bg-destructive/10">
              <LogOut className="w-4 h-4 mr-2" /> Sign Out
            </Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Settings;
