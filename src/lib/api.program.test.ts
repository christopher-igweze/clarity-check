import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/integrations/clerk/tokenStore", () => ({
  getClerkToken: vi.fn(async () => "test-token"),
}));

import {
  createIdempotentCheckpoint,
  createPolicyProfile,
  createProgramSecret,
  createValidationCampaign,
  decideGoLive,
  evaluatePolicyCheck,
  listProgramSecrets,
} from "@/lib/api";

describe("program ops api", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("creates validation campaign via canonical alias", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({
          campaign_id: "c-1",
          name: "campaign",
          repos: ["repo-a"],
          runs_per_repo: 3,
          created_by: "u1",
          created_at: "2026-02-20T00:00:00Z",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );
    global.fetch = fetchMock as unknown as typeof fetch;

    const campaign = await createValidationCampaign({
      name: "campaign",
      repos: ["repo-a"],
      runsPerRepo: 3,
    });

    expect(campaign.campaign_id).toBe("c-1");
    expect(fetchMock.mock.calls[0]?.[0]).toBe("http://localhost:8000/v1/program/campaigns");
  });

  it("creates and evaluates policy profile via canonical alias", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            profile_id: "p-1",
            name: "strict",
            blocked_commands: ["rm -rf"],
            restricted_paths: [],
            created_by: "u1",
            created_at: "2026-02-20T00:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            action: "BLOCK",
            reason: "blocked_command:rm -rf",
            violation_code: "blocked_command",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      );
    global.fetch = fetchMock as unknown as typeof fetch;

    const profile = await createPolicyProfile({
      name: "strict",
      blockedCommands: ["rm -rf"],
      restrictedPaths: [],
    });
    expect(profile.profile_id).toBe("p-1");

    const decision = await evaluatePolicyCheck({
      profileId: profile.profile_id,
      command: "rm -rf /tmp/app",
      path: "/tmp/app",
      buildId: "b-1",
    });
    expect(decision.action).toBe("BLOCK");
    expect(fetchMock.mock.calls[1]?.[0]).toBe("http://localhost:8000/v1/program/policy-check");
  });

  it("stores secret and performs week12/week16 actions", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            secret_id: "s-1",
            name: "token",
            masked_value: "to***en",
            cipher_digest: "abcd1234abcd1234",
            created_at: "2026-02-20T00:00:00Z",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify([
            {
              secret_id: "s-1",
              name: "token",
              masked_value: "***",
              cipher_digest: "abcd1234abcd1234",
              created_at: "2026-02-20T00:00:00Z",
            },
          ]),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            checkpoint_id: "cp-1",
            replayed: false,
            status: "running",
            reason: "checkpoint",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            release_id: "r-1",
            status: "GO",
            reasons: [],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      );
    global.fetch = fetchMock as unknown as typeof fetch;

    const secret = await createProgramSecret({ name: "token", value: "plaintext" });
    expect(secret.secret_id).toBe("s-1");

    const list = await listProgramSecrets();
    expect(list).toHaveLength(1);

    const cp = await createIdempotentCheckpoint({
      buildId: "b-1",
      idempotencyKey: "k-1",
      reason: "checkpoint",
    });
    expect(cp.replayed).toBe(false);

    const decision = await decideGoLive({
      releaseId: "r-1",
      validationReleaseReady: true,
    });
    expect(decision.status).toBe("GO");
  });
});
