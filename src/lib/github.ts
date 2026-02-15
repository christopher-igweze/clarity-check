// Fetch GitHub repo contents via GitHub API (public repos only for now)
export async function fetchRepoContents(repoUrl: string): Promise<string> {
  // Extract owner/repo from URL
  const match = repoUrl.match(/github\.com\/([^/]+)\/([^/]+)/);
  if (!match) throw new Error("Invalid GitHub URL");

  const [, owner, repo] = match;
  const cleanRepo = repo.replace(/\.git$/, "");

  // Fetch file tree
  const treeRes = await fetch(
    `https://api.github.com/repos/${owner}/${cleanRepo}/git/trees/main?recursive=1`
  );

  if (!treeRes.ok) {
    // Try 'master' branch
    const masterRes = await fetch(
      `https://api.github.com/repos/${owner}/${cleanRepo}/git/trees/master?recursive=1`
    );
    if (!masterRes.ok) throw new Error("Could not fetch repo tree. Is the repo public?");
    const masterData = await masterRes.json();
    return await buildRepoContent(owner, cleanRepo, masterData.tree);
  }

  const treeData = await treeRes.json();
  return await buildRepoContent(owner, cleanRepo, treeData.tree);
}

interface TreeItem {
  path: string;
  type: string;
  size?: number;
}

async function buildRepoContent(owner: string, repo: string, tree: TreeItem[]): Promise<string> {
  const relevantFiles = tree.filter((item: TreeItem) => {
    if (item.type !== "blob") return false;
    if (item.size && item.size > 100000) return false; // Skip files > 100KB
    
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

  // Build file tree string
  let content = `File tree:\n${tree.map((i: TreeItem) => `${i.type === "tree" ? "📁" : "📄"} ${i.path}`).join("\n")}\n\n`;

  // Fetch content of key files (limit to 30 most important)
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
        `https://api.github.com/repos/${owner}/${repo}/contents/${file.path}`
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
