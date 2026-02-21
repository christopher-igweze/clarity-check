import { getClerkToken } from "@/integrations/clerk/tokenStore";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const API_URL = `${API_BASE_URL}/api`;
export const TIER1_ENABLED = String(import.meta.env.VITE_TIER1_ENABLED ?? "true").toLowerCase() !== "false";
export const BUILD_CONTROL_PLANE_ENABLED =
  String(import.meta.env.VITE_BUILD_CONTROL_PLANE_ENABLED ?? "true").toLowerCase() === "true";

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

export type BuildRunResponse = {
  buildId: string;
  status: string;
};

export type BuildRuntimeTick = {
  build_id: string;
  runtime_id: string;
  executed_nodes: string[];
  pending_nodes: string[];
  active_level?: number | null;
  level_started?: number | null;
  level_completed?: number | null;
  finished: boolean;
};

export type BuildStatusEvent = {
  event: string;
  payload: {
    event_type?: string;
    build_id?: string;
    timestamp?: string;
    payload?: Record<string, unknown>;
    message?: string;
  };
};

export type BuildReplanAction = "CONTINUE" | "MODIFY_DAG" | "REDUCE_SCOPE" | "ABORT";

export type ReplanDecisionResponse = {
  decision_id: string;
  action: BuildReplanAction;
  reason: string;
  created_at: string;
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
  const resp = await fetch(`${API_URL}/vision-intake`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      messages,
      repo_url: repoUrl,
      vibe_prompt: vibePrompt,
    }),
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

export async function createBuildRun({
  repoUrl,
  objective,
  metadata,
}: {
  repoUrl: string;
  objective: string;
  metadata?: Record<string, unknown>;
}): Promise<BuildRunResponse> {
  const resp = await fetch(`${API_BASE_URL}/v1/builds`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      repo_url: repoUrl,
      objective,
      metadata: metadata || {},
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to create orchestration build");
  }
  const data = await resp.json();
  return {
    buildId: data.build_id as string,
    status: data.status as string,
  };
}

export async function getBuildRun(buildId: string): Promise<{ status: string }> {
  const resp = await fetch(`${API_BASE_URL}/v1/builds/${buildId}`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to fetch build status");
  }
  const data = await resp.json();
  return { status: data.status as string };
}

export async function resumeBuildRun({
  buildId,
  reason,
}: {
  buildId: string;
  reason?: string;
}): Promise<{ status: string }> {
  const resp = await fetch(`${API_BASE_URL}/v1/builds/${buildId}/resume`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({ reason: reason || "manual_resume_from_ui" }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to resume build");
  }
  const data = await resp.json();
  return { status: data.status as string };
}

export async function abortBuildRun({
  buildId,
  reason,
}: {
  buildId: string;
  reason?: string;
}): Promise<{ status: string }> {
  const resp = await fetch(`${API_BASE_URL}/v1/builds/${buildId}/abort`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({ reason: reason || "manual_abort_from_ui" }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to abort build");
  }
  const data = await resp.json();
  return { status: data.status as string };
}

export async function submitReplanDecision({
  buildId,
  action,
  reason,
}: {
  buildId: string;
  action: BuildReplanAction;
  reason: string;
}): Promise<ReplanDecisionResponse> {
  const resp = await fetch(`${API_BASE_URL}/v1/builds/${buildId}/replan`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      action,
      reason,
      replacement_nodes: [],
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to submit replan decision");
  }
  return (await resp.json()) as ReplanDecisionResponse;
}

export async function bootstrapBuildRuntime(buildId: string): Promise<{ runtimeId: string }> {
  const resp = await fetch(`${API_BASE_URL}/v1/builds/${buildId}/runtime/bootstrap`, {
    method: "POST",
    headers: await getAuthHeaders(),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to bootstrap runtime");
  }
  const data = await resp.json();
  return { runtimeId: data.runtime_id as string };
}

export async function tickBuildRuntime(buildId: string): Promise<BuildRuntimeTick> {
  const resp = await fetch(`${API_BASE_URL}/v1/builds/${buildId}/runtime/tick`, {
    method: "POST",
    headers: await getAuthHeaders(),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to tick runtime");
  }
  return (await resp.json()) as BuildRuntimeTick;
}

export async function streamBuildEvents({
  buildId,
  onEvent,
  onDone,
}: {
  buildId: string;
  onEvent: (event: BuildStatusEvent) => void;
  onDone: () => void;
}) {
  const resp = await fetch(`${API_BASE_URL}/v1/builds/${buildId}/events`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });

  if (!resp.ok || !resp.body) {
    const err = await resp.text();
    throw new Error(err || "Failed to stream build events");
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

    let payload: BuildStatusEvent["payload"] = {};
    try {
      payload = JSON.parse(dataStr);
    } catch {
      payload = { message: dataStr };
    }

    onEvent({ event: eventType, payload });
    if (eventType === "BUILD_FINISHED" || eventType === "error" || eventType === "timeout") {
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

export type ProgramCampaign = {
  campaign_id: string;
  name: string;
  repos: string[];
  runs_per_repo: number;
  created_by: string;
  created_at: string;
};

export type ProgramPolicyProfile = {
  profile_id: string;
  name: string;
  blocked_commands: string[];
  restricted_paths: string[];
  created_by: string;
  created_at: string;
};

export type ProgramPolicyResult = {
  action: "ALLOW" | "BLOCK";
  reason: string;
  violation_code?: string | null;
};

export type ProgramSecretRef = {
  secret_id: string;
  name: string;
  masked_value: string;
  cipher_digest: string;
  created_at: string;
};

export type ProgramSecretMetadata = {
  secret_id: string;
  name: string;
  cipher_digest: string;
  cipher_length: number;
};

export type ProgramCampaignReport = {
  generated_at: string;
  summary: {
    repo_count: number;
    run_count: number;
    avg_success_rate: number;
    max_duration_cv: number;
    repos: Array<{
      repo: string;
      language: string;
      run_count: number;
      success_count: number;
      success_rate: number;
      mean_duration_ms: number;
      duration_stddev_ms: number;
      duration_cv: number;
    }>;
  };
  gate: {
    passed: boolean;
    reasons: string[];
  };
  rubric: {
    passed: boolean;
    release_ready: boolean;
    score: number;
    reasons: string[];
  };
  recommendations: string[];
};

export async function createValidationCampaign({
  name,
  repos,
  runsPerRepo,
}: {
  name: string;
  repos: string[];
  runsPerRepo: number;
}): Promise<ProgramCampaign> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/campaigns`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      name,
      repos,
      runs_per_repo: runsPerRepo,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to create validation campaign");
  }
  return (await resp.json()) as ProgramCampaign;
}

export async function getValidationCampaign(campaignId: string): Promise<ProgramCampaign> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/campaigns/${campaignId}`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to fetch validation campaign");
  }
  return (await resp.json()) as ProgramCampaign;
}

export async function ingestCampaignRun({
  campaignId,
  repo,
  language,
  runId,
  status,
  durationMs,
  findingsTotal,
}: {
  campaignId: string;
  repo: string;
  language: string;
  runId: string;
  status: "completed" | "failed" | "aborted";
  durationMs: number;
  findingsTotal?: number;
}): Promise<{ status: string; run_id: string }> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/campaigns/${campaignId}/runs`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      repo,
      language,
      run_id: runId,
      status,
      duration_ms: durationMs,
      findings_total: findingsTotal ?? 0,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to ingest campaign run");
  }
  return (await resp.json()) as { status: string; run_id: string };
}

export async function getCampaignReport(campaignId: string): Promise<ProgramCampaignReport> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/campaigns/${campaignId}/report`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to fetch campaign report");
  }
  return (await resp.json()) as ProgramCampaignReport;
}

export async function createPolicyProfile({
  name,
  blockedCommands,
  restrictedPaths,
}: {
  name: string;
  blockedCommands: string[];
  restrictedPaths: string[];
}): Promise<ProgramPolicyProfile> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/policy-profiles`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      name,
      blocked_commands: blockedCommands,
      restricted_paths: restrictedPaths,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to create policy profile");
  }
  return (await resp.json()) as ProgramPolicyProfile;
}

export async function evaluatePolicyCheck({
  profileId,
  command,
  path,
  buildId,
}: {
  profileId: string;
  command: string;
  path?: string;
  buildId?: string;
}): Promise<ProgramPolicyResult> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/policy-check`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      profile_id: profileId,
      command,
      path: path ?? null,
      build_id: buildId ?? null,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to evaluate policy check");
  }
  return (await resp.json()) as ProgramPolicyResult;
}

export async function createProgramSecret({
  name,
  value,
}: {
  name: string;
  value: string;
}): Promise<ProgramSecretRef> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/secrets`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({ name, value }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to store program secret");
  }
  return (await resp.json()) as ProgramSecretRef;
}

export async function listProgramSecrets(): Promise<ProgramSecretRef[]> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/secrets`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to list program secrets");
  }
  return (await resp.json()) as ProgramSecretRef[];
}

export async function getProgramSecretMetadata(secretId: string): Promise<ProgramSecretMetadata> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/secrets/${secretId}`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to fetch secret metadata");
  }
  return (await resp.json()) as ProgramSecretMetadata;
}

export async function createIdempotentCheckpoint({
  buildId,
  idempotencyKey,
  reason,
}: {
  buildId: string;
  idempotencyKey: string;
  reason: string;
}): Promise<{
  checkpoint_id: string;
  replayed: boolean;
  status: string;
  reason: string;
}> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/week12/idempotent-checkpoints`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      build_id: buildId,
      idempotency_key: idempotencyKey,
      reason,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to create idempotent checkpoint");
  }
  return (await resp.json()) as {
    checkpoint_id: string;
    replayed: boolean;
    status: string;
    reason: string;
  };
}

export async function getProgramSloSummary(): Promise<{
  total_builds: number;
  completed_builds: number;
  failed_builds: number;
  aborted_builds: number;
  running_builds: number;
  success_rate: number;
  mean_cycle_seconds: number;
}> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/slo-summary`, {
    method: "GET",
    headers: {
      Authorization: (await getAuthHeaders()).Authorization,
    },
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to fetch SLO summary");
  }
  return (await resp.json()) as {
    total_builds: number;
    completed_builds: number;
    failed_builds: number;
    aborted_builds: number;
    running_builds: number;
    success_rate: number;
    mean_cycle_seconds: number;
  };
}

export async function upsertReleaseChecklist(payload: {
  releaseId: string;
  securityReview: boolean;
  sloDashboard: boolean;
  rollbackTested: boolean;
  docsComplete: boolean;
  runbooksReady: boolean;
}): Promise<{
  release_id: string;
  security_review: boolean;
  slo_dashboard: boolean;
  rollback_tested: boolean;
  docs_complete: boolean;
  runbooks_ready: boolean;
}> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/checklist`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      release_id: payload.releaseId,
      security_review: payload.securityReview,
      slo_dashboard: payload.sloDashboard,
      rollback_tested: payload.rollbackTested,
      docs_complete: payload.docsComplete,
      runbooks_ready: payload.runbooksReady,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to upsert release checklist");
  }
  return (await resp.json()) as {
    release_id: string;
    security_review: boolean;
    slo_dashboard: boolean;
    rollback_tested: boolean;
    docs_complete: boolean;
    runbooks_ready: boolean;
  };
}

export async function upsertRollbackDrill(payload: {
  releaseId: string;
  passed: boolean;
  durationMinutes: number;
  issuesFound: string[];
}): Promise<{
  release_id: string;
  passed: boolean;
  duration_minutes: number;
  issues_found: string[];
}> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/rollback-drills`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      release_id: payload.releaseId,
      passed: payload.passed,
      duration_minutes: payload.durationMinutes,
      issues_found: payload.issuesFound,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to upsert rollback drill");
  }
  return (await resp.json()) as {
    release_id: string;
    passed: boolean;
    duration_minutes: number;
    issues_found: string[];
  };
}

export async function decideGoLive(payload: {
  releaseId: string;
  validationReleaseReady: boolean;
}): Promise<{
  release_id: string;
  status: "GO" | "NO_GO";
  reasons: string[];
}> {
  const resp = await fetch(`${API_BASE_URL}/v1/program/go-live-decision`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      release_id: payload.releaseId,
      validation_release_ready: payload.validationReleaseReady,
    }),
  });
  if (!resp.ok) {
    throw await toApiError(resp, "Failed to compute go-live decision");
  }
  return (await resp.json()) as {
    release_id: string;
    status: "GO" | "NO_GO";
    reasons: string[];
  };
}
