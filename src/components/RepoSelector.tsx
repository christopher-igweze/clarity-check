import { useState, useEffect, useRef } from "react";
import { GitBranch, Search, Star, Lock, Globe, Loader2, ChevronDown } from "lucide-react";
import { Input } from "@/components/ui/input";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";

interface GitHubRepo {
  full_name: string;
  html_url: string;
  description: string | null;
  stargazers_count: number;
  language: string | null;
  private: boolean;
  updated_at: string;
}

interface RepoSelectorProps {
  value: string;
  onChange: (url: string) => void;
}

export function RepoSelector({ value, onChange }: RepoSelectorProps) {
  const { user } = useAuth();
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [loading, setLoading] = useState(false);
  const [githubConnected, setGithubConnected] = useState(false);
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!user) return;
    const fetchRepos = async () => {
      const { data: profile } = await supabase
        .from("profiles")
        .select("github_access_token, github_username")
        .eq("user_id", user.id)
        .single();

      const token = (profile as any)?.github_access_token;
      if (!token) return;

      setGithubConnected(true);
      setLoading(true);

      try {
        const res = await fetch("https://api.github.com/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setRepos(data);
        }
      } catch (err) {
        console.error("Failed to fetch repos:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchRepos();
  }, [user]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const filtered = repos.filter((r) =>
    r.full_name.toLowerCase().includes(search.toLowerCase()) ||
    r.description?.toLowerCase().includes(search.toLowerCase())
  );

  const langColors: Record<string, string> = {
    TypeScript: "bg-blue-500",
    JavaScript: "bg-yellow-400",
    Python: "bg-green-500",
    Rust: "bg-orange-500",
    Go: "bg-cyan-500",
    Java: "bg-red-500",
    Ruby: "bg-red-400",
  };

  const formatDate = (d: string) => {
    const diff = Date.now() - new Date(d).getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return "today";
    if (days === 1) return "yesterday";
    if (days < 30) return `${days}d ago`;
    return `${Math.floor(days / 30)}mo ago`;
  };

  return (
    <div ref={containerRef} className="relative">
      <label className="text-sm font-medium mb-2 block">GitHub Repository</label>
      <div className="relative">
        <GitBranch className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground z-10" />
        <Input
          value={value}
          onChange={(e) => { onChange(e.target.value); setOpen(false); }}
          onFocus={() => githubConnected && repos.length > 0 && setOpen(true)}
          placeholder={githubConnected ? "Search your repos or paste a URL..." : "https://github.com/user/repo"}
          className="pl-10 pr-10 bg-secondary border-border"
        />
        {githubConnected && repos.length > 0 && (
          <button
            type="button"
            onClick={() => setOpen(!open)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ChevronDown className={`w-4 h-4 transition-transform ${open ? "rotate-180" : ""}`} />}
          </button>
        )}
      </div>

      {open && githubConnected && (
        <div className="absolute z-50 w-full mt-1 rounded-xl border border-border bg-secondary/95 backdrop-blur-xl shadow-2xl overflow-hidden">
          <div className="p-2 border-b border-border">
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filter repositories..."
                className="w-full pl-8 pr-3 py-1.5 text-sm bg-transparent border-none outline-none placeholder:text-muted-foreground"
                autoFocus
              />
            </div>
          </div>
          <div className="max-h-[280px] overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center py-8 text-sm text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin mr-2" /> Loading repos...
              </div>
            ) : filtered.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">No repos found</div>
            ) : (
              filtered.map((repo) => (
                <button
                  key={repo.full_name}
                  type="button"
                  onClick={() => {
                    onChange(repo.html_url);
                    setOpen(false);
                    setSearch("");
                  }}
                  className="w-full flex items-start gap-3 px-3 py-2.5 text-left hover:bg-primary/5 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      {repo.private ? (
                        <Lock className="w-3 h-3 text-neon-orange shrink-0" />
                      ) : (
                        <Globe className="w-3 h-3 text-muted-foreground shrink-0" />
                      )}
                      <span className="text-sm font-medium truncate">{repo.full_name}</span>
                    </div>
                    {repo.description && (
                      <p className="text-xs text-muted-foreground truncate mt-0.5">{repo.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0 text-[10px] text-muted-foreground mt-0.5">
                    {repo.language && (
                      <span className="flex items-center gap-1">
                        <span className={`w-2 h-2 rounded-full ${langColors[repo.language] || "bg-muted-foreground"}`} />
                        {repo.language}
                      </span>
                    )}
                    {repo.stargazers_count > 0 && (
                      <span className="flex items-center gap-0.5">
                        <Star className="w-2.5 h-2.5" /> {repo.stargazers_count}
                      </span>
                    )}
                    <span>{formatDate(repo.updated_at)}</span>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
