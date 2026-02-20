import { getClerkToken } from "@/integrations/clerk/tokenStore";

const FUNCTIONS_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1`;
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const API_URL = `${API_BASE_URL}/api`;
export const TIER1_ENABLED = String(import.meta.env.VITE_TIER1_ENABLED ?? "true").toLowerCase() !== "false";

type StreamCallback = (text: string) => void;
type ApiError = Error & { code?: string; status?: number; payload?: unknown };

async function toApiError(resp: Response, fallback: string): Promise<ApiError> {
  let payload: unknown = null;
  let message = fallback;
  let code: string | undefined;

  try {
    payload = await resp.json();
    const detail = (payload as { detail?: unknown })?.detail;
    if (typeof detail === "string") {
      message = detail;
    } else if (detail && typeof detail === "object") {
      const detailObj = detail as { message?: string; code?: string };
      message = detailObj.message || fallback;
      code = detailObj.code;
    }
  } catch {
    const text = await resp.text();
    if (text) message = text;
  }

  const err = new Error(message) as ApiError;
  err.status = resp.status;
  err.code = code;
  err.payload = payload;
  return err;
}

async function getAuthHeaders() {
  const token = await getClerkToken();
  const devToken = import.meta.env.DEV ? import.meta.env.VITE_LOCAL_DEV_BEARER_TOKEN : undefined;

  if (!token && !devToken) {
    throw new Error("Missing authenticated session. Ensure Clerk is signed in or set VITE_LOCAL_DEV_BEARER_TOKEN for local development.");
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token ?? devToken}`,
  };
}

export async function startAudit({
  repoUrl,
  vibePrompt,
  projectIntake,
  primer,
  projectCharter,
}: {
  repoUrl: string;
  projectIntake: {
    project_origin: "inspired" | "external";
    product_summary: string;
    target_users: string;
    sensitive_data: Array<"payments" | "pii" | "health" | "auth_secrets" | "none" | "not_sure">;
    must_not_break_flows: string[];
    deployment_target: string;
    scale_expectation: string;
  };
  primer?: {
    primer_json: Record<string, unknown>;
    summary: string;
    repo_sha: string;
    confidence: number;
    failure_reason?: string | null;
  };
  vibePrompt?: string;
  projectCharter?: Record<string, unknown>;
}) {
  const resp = await fetch(`${API_URL}/audit`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      repo_url: repoUrl,
      vibe_prompt: vibePrompt,
      project_intake: projectIntake,
      primer,
      project_charter: projectCharter,
    }),
  });

  if (!resp.ok) {
    throw await toApiError(resp, "Failed to start audit");
  }

  const data = await resp.json();
  return {
    scanId: data.scan_id as string,
    status: data.status as string,
    tier: (data.tier as string | undefined) || "free",
    quotaRemaining: (typeof data.quota_remaining === "number" ? data.quota_remaining : null) as number | null,
    message: data.message as string,
  };
}

export async function getLimits(): Promise<{
  tier: "free";
  month_key: string;
  reports_generated: number;
  reports_limit: number;
  reports_remaining: number;
  project_count: number;
  project_limit: number;
  loc_cap: number;
}> {
  const resp = await fetch(`${API_URL}/limits`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to fetch limits");
  }
  return await resp.json();
}

export type ReportArtifactType = "markdown" | "agent_markdown" | "pdf";

export async function getReportArtifact(
  scanId: string,
  artifactType: ReportArtifactType = "markdown",
): Promise<{
  scan_id: string;
  artifact_type: ReportArtifactType;
  content: string;
  expires_at: string;
  mime_type: string;
  content_encoding: "utf-8" | "base64";
  filename: string;
}> {
  const params = new URLSearchParams({ artifact_type: artifactType });
  const resp = await fetch(`${API_URL}/report-artifacts/${scanId}?${params.toString()}`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to load report artifact");
  }
  return await resp.json();
}

export async function runPrimer({
  repoUrl,
}: {
  repoUrl: string;
}): Promise<{
  project_id: string;
  cached: boolean;
  primer: {
    primer_json: Record<string, unknown>;
    summary: string;
    repo_sha: string;
    confidence: number;
    failure_reason: string | null;
  };
  suggested_flows: string[];
}> {
  const resp = await fetch(`${API_URL}/primer`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({ repo_url: repoUrl }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(err || "Failed to run primer");
  }

  return await resp.json();
}

export async function getGithubAuthUrl({
  redirectUri,
}: {
  redirectUri: string;
}): Promise<{ auth_url: string }> {
  const resp = await fetch(`${API_URL}/github-oauth`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      action: "get_auth_url",
      redirect_uri: redirectUri,
    }),
  });

  if (!resp.ok) {
    throw await toApiError(resp, "Failed to get GitHub auth URL");
  }
  return await resp.json();
}

export async function exchangeGithubCode({
  code,
  redirectUri,
  state,
}: {
  code: string;
  redirectUri: string;
  state: string;
}): Promise<{
  github_username?: string;
  avatar_url?: string | null;
  connected: boolean;
}> {
  const resp = await fetch(`${API_URL}/github-oauth`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      action: "exchange_code",
      code,
      redirect_uri: redirectUri,
      state,
    }),
  });

  if (!resp.ok) {
    throw await toApiError(resp, "Failed to connect GitHub");
  }
  return await resp.json();
}

export async function disconnectGithub(): Promise<{ connected: boolean }> {
  const resp = await fetch(`${API_URL}/github-oauth`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({ action: "disconnect" }),
  });

  if (!resp.ok) {
    throw await toApiError(resp, "Failed to disconnect GitHub");
  }
  return await resp.json();
}

export type ScanStatusEvent = {
  event: string;
  payload: {
    event_type?: string;
    agent?: string;
    message?: string;
    level?: "info" | "warn" | "error" | "success";
    data?: Record<string, unknown>;
    timestamp?: string;
  };
};

export async function streamScanStatus({
  scanId,
  onEvent,
  onDone,
}: {
  scanId: string;
  onEvent: (event: ScanStatusEvent) => void;
  onDone: () => void;
}) {
  const resp = await fetch(`${API_URL}/status/${scanId}`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });

  if (!resp.ok || !resp.body) {
    const err = await resp.text();
    throw new Error(err || "Failed to stream scan status");
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let doneCalled = false;

  const safeDone = () => {
    if (doneCalled) return;
    doneCalled = true;
    onDone();
  };

  const findEventDelimiter = (s: string) => {
    // sse-starlette uses CRLF by default; handle both LF and CRLF delimiters.
    const lf = s.indexOf("\n\n");
    const crlf = s.indexOf("\r\n\r\n");

    if (lf === -1) return crlf === -1 ? null : { index: crlf, length: 4 };
    if (crlf === -1) return { index: lf, length: 2 };
    return lf < crlf ? { index: lf, length: 2 } : { index: crlf, length: 4 };
  };

  const dispatchEventBlock = (block: string) => {
    const lines = block.split(/\r?\n/);
    let eventType = "message";
    const dataLines: string[] = [];

    for (const line of lines) {
      const clean = line.endsWith("\r") ? line.slice(0, -1) : line;
      if (clean.startsWith(":") || clean.trim() === "") continue;
      if (clean.startsWith("event:")) {
        eventType = clean.slice(6).trim();
      } else if (clean.startsWith("data:")) {
        dataLines.push(clean.slice(5).trim());
      }
    }

    const dataStr = dataLines.join("\n");
    if (!dataStr) return;

    let payload: ScanStatusEvent["payload"] = {};
    try {
      payload = JSON.parse(dataStr);
    } catch {
      payload = { message: dataStr };
    }

    onEvent({ event: eventType, payload });

    if (eventType === "scan_complete" || eventType === "scan_error" || eventType === "timeout") {
      safeDone();
    }
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    let delim: { index: number; length: number } | null;
    while ((delim = findEventDelimiter(buffer)) !== null) {
      const chunk = buffer.slice(0, delim.index);
      buffer = buffer.slice(delim.index + delim.length);
      if (chunk.trim()) {
        dispatchEventBlock(chunk);
      }
    }
  }

  if (buffer.trim()) {
    dispatchEventBlock(buffer);
  }

  safeDone();
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
    headers: await getAuthHeaders(),
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
        buffer = `${line}\n${buffer}`;
        break;
      }
    }
  }

  onDone();
}
