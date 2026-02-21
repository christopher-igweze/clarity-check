import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/integrations/clerk/tokenStore", () => ({
  getClerkToken: vi.fn(async () => "test-token"),
}));

import {
  abortBuildRun,
  bootstrapBuildRuntime,
  createBuildRun,
  getBuildRuntimeWorkerHealth,
  previewBuildDag,
  resumeBuildRun,
  streamBuildEvents,
  submitReplanDecision,
} from "@/lib/api";

const TEST_API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

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
      metadata: { scan_mode: "autonomous" },
    });

    expect(result).toEqual({ buildId: "build-123", status: "running" });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`${TEST_API_BASE_URL}/v1/builds`);
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit;
    expect(init.method).toBe("POST");
    expect(init.headers).toMatchObject({ Authorization: "Bearer test-token" });
    const body = JSON.parse(String(init.body));
    expect(body.metadata.scan_mode).toBe("autonomous");
  });

  it("previews build DAG against v1 preview endpoint", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({
          scan_mode: "autonomous",
          planner_profile: "agentic_llm_v1",
          planner_trace: { profile: "agentic_llm_v1" },
          dag: [
            { node_id: "scan", title: "Scan", agent: "scanner", depends_on: [] },
            { node_id: "plan", title: "Plan", agent: "planner", depends_on: ["scan"] },
          ],
          dag_levels: [["scan"], ["plan"]],
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      )
    );
    global.fetch = fetchMock as unknown as typeof fetch;

    const result = await previewBuildDag({
      repoUrl: "https://github.com/octocat/Hello-World",
      objective: "preview orchestration",
      metadata: { autonomous_planner_profile: "agentic_llm_v1" },
    });

    expect(result.planner_profile).toBe("agentic_llm_v1");
    expect(result.dag).toHaveLength(2);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`${TEST_API_BASE_URL}/v1/builds/preview-dag`);
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

  it("posts resume and abort control actions", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ status: "running" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ status: "aborted" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        })
      );
    global.fetch = fetchMock as unknown as typeof fetch;

    const resumed = await resumeBuildRun({ buildId: "build-123", reason: "resume-test" });
    const aborted = await abortBuildRun({ buildId: "build-123", reason: "abort-test" });

    expect(resumed.status).toBe("running");
    expect(aborted.status).toBe("aborted");
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`${TEST_API_BASE_URL}/v1/builds/build-123/resume`);
    expect(fetchMock.mock.calls[1]?.[0]).toBe(`${TEST_API_BASE_URL}/v1/builds/build-123/abort`);
  });

  it("submits replan decisions to control plane", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({
          decision_id: "d-123",
          action: "REDUCE_SCOPE",
          reason: "manual_scope_reduction_from_scan_live",
          created_at: "2026-02-20T00:00:00Z",
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }
      )
    );
    global.fetch = fetchMock as unknown as typeof fetch;

    const result = await submitReplanDecision({
      buildId: "build-123",
      action: "REDUCE_SCOPE",
      reason: "manual_scope_reduction_from_scan_live",
    });

    expect(result.action).toBe("REDUCE_SCOPE");
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toBe(`${TEST_API_BASE_URL}/v1/builds/build-123/replan`);
  });

  it("parses runtime bootstrap and worker health contracts", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            runtime_id: "runtime-123",
            metadata: {
              runtime_worker_enabled: true,
              runtime_client_tick_fallback_enabled: false,
              runtime_watchdog_nudge_enabled: true,
              runtime_watchdog_stale_seconds: 30,
            },
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            build_id: "build-123",
            worker_enabled: true,
            worker_stale: true,
            nudge_allowed: true,
            stale_after_seconds: 30,
            last_runtime_event_at: "2026-02-21T12:00:00Z",
          }),
          {
            status: 200,
            headers: { "Content-Type": "application/json" },
          }
        )
      );
    global.fetch = fetchMock as unknown as typeof fetch;

    const bootstrap = await bootstrapBuildRuntime("build-123");
    const health = await getBuildRuntimeWorkerHealth("build-123");

    expect(bootstrap.runtimeId).toBe("runtime-123");
    expect(bootstrap.runtimeWorkerEnabled).toBe(true);
    expect(bootstrap.runtimeClientFallbackEnabled).toBe(false);
    expect(bootstrap.runtimeWatchdogNudgeEnabled).toBe(true);
    expect(bootstrap.runtimeWatchdogStaleSeconds).toBe(30);
    expect(health.nudge_allowed).toBe(true);

    expect(fetchMock.mock.calls[0]?.[0]).toBe(`${TEST_API_BASE_URL}/v1/builds/build-123/runtime/bootstrap`);
    expect(fetchMock.mock.calls[1]?.[0]).toBe(`${TEST_API_BASE_URL}/v1/builds/build-123/runtime/worker-health`);
  });
});
