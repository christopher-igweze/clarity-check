import { supabase } from "@/integrations/supabase/client";

const FUNCTIONS_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1`;
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const API_URL = `${API_BASE_URL}/api`;

type StreamCallback = (text: string) => void;

async function getAuthHeaders() {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  if (!token) {
    throw new Error("Missing authenticated session.");
  }

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

export async function startAudit({
  repoUrl,
  scanTier,
  vibePrompt,
  projectCharter,
}: {
  repoUrl: string;
  scanTier: "surface" | "deep";
  vibePrompt?: string;
  projectCharter?: Record<string, unknown>;
}) {
  const resp = await fetch(`${API_URL}/audit`, {
    method: "POST",
    headers: await getAuthHeaders(),
    body: JSON.stringify({
      repo_url: repoUrl,
      scan_tier: scanTier,
      vibe_prompt: vibePrompt,
      project_charter: projectCharter,
    }),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(err || "Failed to start audit");
  }

  const data = await resp.json();
  return {
    scanId: data.scan_id as string,
    status: data.status as string,
    message: data.message as string,
  };
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

  const dispatchEventBlock = (block: string) => {
    const lines = block.split("\n");
    let eventType = "message";
    const dataLines: string[] = [];

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventType = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trim());
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
      onDone();
    }
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    let splitIndex: number;
    while ((splitIndex = buffer.indexOf("\n\n")) !== -1) {
      const chunk = buffer.slice(0, splitIndex);
      buffer = buffer.slice(splitIndex + 2);
      if (chunk.trim()) {
        dispatchEventBlock(chunk);
      }
    }
  }

  if (buffer.trim()) {
    dispatchEventBlock(buffer);
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
        buffer = `${line}\n${buffer}`;
        break;
      }
    }
  }

  onDone();
}
