import { supabase } from "@/integrations/supabase/client";
import { getCurrentUserId } from "@/integrations/clerk/tokenStore";

// Get the user's GitHub token from their profile
async function getGitHubToken(): Promise<string | null> {
  const userId = getCurrentUserId();
  if (!userId) return null;

  const { data } = await supabase
    .from("profiles")
    .select("github_access_token")
    .eq("user_id", userId)
    .single();

  return (data as any)?.github_access_token || null;
}

// Fetch GitHub repo contents via GitHub API
export async function fetchRepoContents(repoUrl: string): Promise<string> {
  const match = repoUrl.match(/github\.com\/([^/]+)\/([^/]+)/);
  if (!match) throw new Error("Invalid GitHub URL");

  const [, owner, repo] = match;
  const cleanRepo = repo.replace(/\.git$/, "");

  const token = await getGitHubToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  // Fetch file tree
  const treeRes = await fetch(
    `https://api.github.com/repos/${owner}/${cleanRepo}/git/trees/main?recursive=1`,
    { headers }
  );

  if (!treeRes.ok) {
    const masterRes = await fetch(
      `https://api.github.com/repos/${owner}/${cleanRepo}/git/trees/master?recursive=1`,
      { headers }
    );
    if (!masterRes.ok) throw new Error("Could not fetch repo tree. Is the repo public, or have you connected GitHub in Settings?");
    const masterData = await masterRes.json();
    return await buildRepoContent(owner, cleanRepo, masterData.tree, headers);
  }

  const treeData = await treeRes.json();
  return await buildRepoContent(owner, cleanRepo, treeData.tree, headers);
}

interface TreeItem {
  path: string;
  type: string;
  size?: number;
}

async function buildRepoContent(owner: string, repo: string, tree: TreeItem[], headers: Record<string, string>): Promise<string> {
  const relevantFiles = tree.filter((item: TreeItem) => {
    if (item.type !== "blob") return false;
    if (item.size && item.size > 100000) return false;
    
    const ext = item.path.split(".").pop()?.toLowerCase();
    const relevantExtensions = [
      "ts", "tsx", "js", "jsx", "py", "rb", "go", "rs", "java",
      "json", "yaml", "yml", "toml", "env", "md",
      "css", "scss", "html", "sql", "sh", "dockerfile",
    ];
    const relevantNames = [
      "package.json", "tsconfig.json", ".env", ".env.example",
      "Dockerfile", "docker-compose.yml", "Makefile",
      ".gitignore", "requirements.txt", "Cargo.toml", "go.mod",
    ];

    return relevantExtensions.includes(ext || "") || relevantNames.includes(item.path.split("/").pop() || "");
  });

  let content = `File tree:\n${tree.map((i: TreeItem) => `${i.type === "tree" ? "📁" : "📄"} ${i.path}`).join("\n")}\n\n`;

  const priorityFiles = relevantFiles
    .sort((a: TreeItem, b: TreeItem) => {
      const priority = (p: string) => {
        if (p.includes("package.json")) return 0;
        if (p.includes(".env")) return 1;
        if (p.includes("config")) return 2;
        if (p.includes("auth")) return 3;
        if (p.includes("api")) return 4;
        if (p.includes("index")) return 5;
        return 10;
      };
      return priority(a.path) - priority(b.path);
    })
    .slice(0, 30);

  for (const file of priorityFiles) {
    try {
      const res = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/contents/${file.path}`,
        { headers }
      );
      if (res.ok) {
        const data = await res.json();
        if (data.content) {
          const decoded = atob(data.content);
          content += `\n--- ${file.path} ---\n${decoded}\n`;
        }
      }
    } catch {
      // Skip files that can't be fetched
    }
  }

  return content;
}
