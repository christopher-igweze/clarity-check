import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/integrations/clerk/tokenStore", () => ({
  getClerkToken: vi.fn(async () => "test-token"),
}));

import { createBuildRun, streamBuildEvents } from "@/lib/api";

describe("build control-plane api", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("creates build run against v1 control plane", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ build_id: "build-123", status: "running" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );
    global.fetch = fetchMock as unknown as typeof fetch;

    const result = await createBuildRun({
      repoUrl: "https://github.com/octocat/Hello-World",
      objective: "run orchestration",
    });

    expect(result).toEqual({ buildId: "build-123", status: "running" });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toBe("http://localhost:8000/v1/builds");
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(init.method).toBe("POST");
    expect(init.headers).toMatchObject({ Authorization: "Bearer test-token" });
  });

  it("streams and parses build SSE events", async () => {
    const body = [
      'event: BUILD_STARTED\ndata: {"event_type":"BUILD_STARTED","payload":{"step":"start"}}\n\n',
      'event: BUILD_FINISHED\ndata: {"event_type":"BUILD_FINISHED","payload":{"final_status":"completed"}}\n\n',
    ].join("");

    const fetchMock = vi.fn(async () =>
      new Response(body, {
        status: 200,
        headers: { "Content-Type": "text/event-stream" },
      })
    );
    global.fetch = fetchMock as unknown as typeof fetch;

    const received: Array<{ event: string; payload: unknown }> = [];
    let doneCount = 0;

    await streamBuildEvents({
      buildId: "build-123",
      onEvent: (event) => received.push(event),
      onDone: () => {
        doneCount += 1;
      },
    });

    expect(received).toHaveLength(2);
    expect(received[0]?.event).toBe("BUILD_STARTED");
    expect(received[1]?.event).toBe("BUILD_FINISHED");
    expect(doneCount).toBe(1);
  });
});
