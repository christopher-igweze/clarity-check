const FUNCTIONS_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1`;

type StreamCallback = (text: string) => void;

export async function streamSurfaceScan({
  repoContent,
  repoUrl,
  vibePrompt,
  projectCharter,
  onDelta,
  onDone,
}: {
  repoContent: string;
  repoUrl: string;
  vibePrompt?: string;
  projectCharter?: Record<string, unknown>;
  onDelta: StreamCallback;
  onDone: () => void;
}) {
  const resp = await fetch(`${FUNCTIONS_URL}/surface-scan`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
    },
    body: JSON.stringify({ repoContent, repoUrl, vibePrompt, projectCharter }),
  });

  if (!resp.ok || !resp.body) {
    const err = await resp.text();
    throw new Error(err || "Failed to start scan");
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let newlineIndex: number;
    while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
      let line = buffer.slice(0, newlineIndex);
      buffer = buffer.slice(newlineIndex + 1);

      if (line.endsWith("\r")) line = line.slice(0, -1);
      if (line.startsWith(":") || line.trim() === "") continue;
      if (!line.startsWith("data: ")) continue;

      const jsonStr = line.slice(6).trim();
      if (jsonStr === "[DONE]") {
        onDone();
        return;
      }

      try {
        const parsed = JSON.parse(jsonStr);
        const content = parsed.choices?.[0]?.delta?.content;
        if (content) onDelta(content);
      } catch {
        buffer = line + "\n" + buffer;
        break;
      }
    }
  }

  // Final flush
  if (buffer.trim()) {
    for (let raw of buffer.split("\n")) {
      if (!raw) continue;
      if (raw.endsWith("\r")) raw = raw.slice(0, -1);
      if (!raw.startsWith("data: ")) continue;
      const jsonStr = raw.slice(6).trim();
      if (jsonStr === "[DONE]") continue;
      try {
        const parsed = JSON.parse(jsonStr);
        const content = parsed.choices?.[0]?.delta?.content;
        if (content) onDelta(content);
      } catch { /* ignore */ }
    }
  }

  onDone();
}

export async function callSecurityReview({
  reviewType,
  content,
  findings,
  codeChanges,
  projectCharter,
}: {
  reviewType: "validate_findings" | "code_review" | "full_scan";
  content?: string;
  findings?: unknown[];
  codeChanges?: unknown;
  projectCharter?: Record<string, unknown>;
}) {
  const resp = await fetch(`${FUNCTIONS_URL}/security-review`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
    },
    body: JSON.stringify({ reviewType, content, findings, codeChanges, projectCharter }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(err || "Security review failed");
  }

  return resp.json();
}

export type DeepProbeCallback = (event: {
  type: string;
  step?: string;
  status?: string;
  agent?: string;
  message?: string;
  exit_code?: number;
  stdout?: string;
  stderr?: string;
  duration_ms?: number;
  install_ok?: boolean;
  build_ok?: boolean;
  tests_ok?: boolean;
  tests_passed?: number | null;
  tests_failed?: number | null;
  audit_vulnerabilities?: number;
  results?: Record<string, unknown>;
}) => void;

export async function streamDeepProbe({
  repoUrl,
  githubToken,
  onEvent,
  onDone,
}: {
  repoUrl: string;
  githubToken?: string;
  onEvent: DeepProbeCallback;
  onDone: () => void;
}) {
  const resp = await fetch(`${FUNCTIONS_URL}/deep-probe`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
    },
    body: JSON.stringify({ repoUrl, githubToken }),
  });

  if (!resp.ok || !resp.body) {
    const err = await resp.text();
    throw new Error(err || "Failed to start deep probe");
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let newlineIndex: number;
    while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
      let line = buffer.slice(0, newlineIndex);
      buffer = buffer.slice(newlineIndex + 1);

      if (line.endsWith("\r")) line = line.slice(0, -1);
      if (line.startsWith(":") || line.trim() === "") continue;
      if (!line.startsWith("data: ")) continue;

      const jsonStr = line.slice(6).trim();
      if (jsonStr === "[DONE]") {
        onDone();
        return;
      }

      try {
        const parsed = JSON.parse(jsonStr);
        onEvent(parsed);
      } catch {
        buffer = line + "\n" + buffer;
        break;
      }
    }
  }

  onDone();
}

export async function streamVisionIntake({
  messages,
  repoUrl,
  vibePrompt,
  onDelta,
  onDone,
}: {
  messages: { role: string; content: string }[];
  repoUrl: string;
  vibePrompt?: string;
  onDelta: StreamCallback;
  onDone: () => void;
}) {
  const resp = await fetch(`${FUNCTIONS_URL}/vision-intake`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
    },
    body: JSON.stringify({ messages, repoUrl, vibePrompt }),
  });

  if (!resp.ok || !resp.body) {
    const err = await resp.text();
    throw new Error(err || "Failed to start vision intake");
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let newlineIndex: number;
    while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
      let line = buffer.slice(0, newlineIndex);
      buffer = buffer.slice(newlineIndex + 1);

      if (line.endsWith("\r")) line = line.slice(0, -1);
      if (line.startsWith(":") || line.trim() === "") continue;
      if (!line.startsWith("data: ")) continue;

      const jsonStr = line.slice(6).trim();
      if (jsonStr === "[DONE]") {
        onDone();
        return;
      }

      try {
        const parsed = JSON.parse(jsonStr);
        const content = parsed.choices?.[0]?.delta?.content;
        if (content) onDelta(content);
      } catch {
        buffer = line + "\n" + buffer;
        break;
      }
    }
  }

  onDone();
}
