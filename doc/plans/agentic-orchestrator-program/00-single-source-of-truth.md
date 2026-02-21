# Agentic Orchestrator Program — Single Source of Truth (SSOT)

Last updated: February 21, 2026  
Repository: `/Users/christopher/Documents/AntiGravity/clarity-check`  
Primary branch in progress: `staging`  
Active PR: none (`#4` merged to `staging`)

## Purpose
This is the canonical implementation status document for the production hardening + platform integration track.

Use this doc to answer:
1. Where are we now?
2. What should be working right now?
3. What is left?
4. What should we build next?

If any other doc conflicts with this file, this file wins.

## Scope Covered by This SSOT
1. Build control plane (`/v1/builds*`).
2. Program control plane (`/v1/program*` canonical + week-prefixed compatibility routes).
3. Runtime ownership model (backend worker vs browser-driven ticks).
4. Release readiness product surface and validation workflow.
5. Security hardening baseline (capability checks, webhook replay protection, idempotency, secret handling).

## Current Architecture (As Implemented)
1. Execution runtime:
OpenHands/runner bridge + runtime gateway.
2. Orchestration state:
`BuildStore` + `ProgramStore` with normalized-table persistence adapters and snapshot fallback.
3. Durability:
Supabase normalized control-plane tables (`build_*`, `validation_*`, `program_*`) + snapshot fallback (`control_plane_state`) + optional local file fallback.
4. Ephemeral coordination:
Redis-backed nonce/idempotency/lease coordination with explicit fail-closed mode (`COORDINATION_FAIL_CLOSED=true`).
5. Runtime execution authority:
Backend `RuntimeWorker` drives runtime ticks with distributed lease + heartbeat ownership per build; frontend observes events and only uses guarded fallback ticking if worker is disabled/unhealthy.
6. API shape:
Canonical program APIs under `/v1/program/*` with week endpoints retained for compatibility.
7. UI surfaces:
`Dashboard`, `NewScan`, `ScanLive`, `ReleaseReadiness`, and `ProgramOps` (advanced).

## What Must Be Working Right Now

### A) Build Flow (Autonomous Default)
1. `NewScan` creates a `BuildRun` via `/v1/builds` when `VITE_BUILD_CONTROL_PLANE_ENABLED=true`.
2. `scan_mode` defaults to `autonomous` (explicitly passed in metadata from UI).
3. `ScanLive` streams build events and does not drive normal orchestration loops.
4. Backend runtime worker bootstraps/ticks builds to completion or fail state with lease ownership.
5. If worker is disabled/unhealthy, `ScanLive` uses a guarded tick safety fallback (backend API call) to prevent stuck `running` builds.

Expected user-visible behavior:
1. Starting a scan should create a build and open live stream.
2. Build status transitions should appear in live stream (`running`, `completed`/`failed`/`aborted`).
3. Buttons in live view should only send control actions (abort/resume/replan), not execute workflow loops.

### B) Deterministic Fallback Behavior
Fallback from autonomous to deterministic is backend-controlled and only applies when all are true:
1. Autonomous run node fails after retry budget path.
2. Build metadata includes `fallback_scan_mode=deterministic`.
3. Fallback has not already been applied.

Expected behavior:
1. Event `FALLBACK_MODE_SWITCHED` is emitted.
2. Build stays `running` and switches DAG to deterministic nodes.
3. Build can still complete successfully after fallback.

### C) Program APIs
Canonical APIs should work:
1. `/v1/program/campaigns`
2. `/v1/program/campaigns/{campaign_id}/runs`
3. `/v1/program/campaigns/{campaign_id}/report`
4. `/v1/program/policy-profiles`
5. `/v1/program/policy-check`
6. `/v1/program/secrets`
7. `/v1/program/slo-summary`
8. `/v1/program/checklist`
9. `/v1/program/rollback-drills`
10. `/v1/program/go-live-decision`
11. `/v1/program/webhook/ingest`
12. `/v1/program/idempotent-checkpoints`

Compatibility routes (`/v1/program/week*/*`) should continue to work during transition.

### D) Release Readiness UI
1. Dashboard links to `/release-readiness`.
2. Release Readiness page supports:
validation campaign lifecycle, checklist + rollback drill + go/no-go decision, and SLO summary retrieval.
3. Program Ops remains available as advanced/operator surface.

### E) Security Controls
1. Secret storage encrypts values and lists masked values.
2. Webhook ingest validates signature + timestamp and rejects replayed nonce.
3. Idempotent checkpoints replay correctly by key.
4. Capability enforcement exists and is controlled by `ENFORCE_CAPABILITY_AUTH`.

## Validation Snapshot (Current)
Last verified on February 21, 2026:
1. Backend tests: `91 passed` (`cd backend && PYTHONPATH=. pytest -q`).
2. Frontend unit tests: `10 passed` (`npm run test`).
3. Frontend production build: success (`npm run build`).

## Staging Setup Contract (Redis + JWT)

### Redis URL
1. Production/staging must use TLS Redis URL format:
`REDIS_URL=rediss://default:<token>@<host>:6379`
2. Do not use plain `redis://` for hosted Redis providers.
3. If a token is ever shared in chat/logs, rotate it immediately and update the environment secret.

### Required Backend Flags
1. `CONTROL_PLANE_USE_SUPABASE=true`
2. `COORDINATION_FAIL_CLOSED=true`
3. `ENFORCE_CAPABILITY_AUTH=true`
4. `RUNTIME_WORKER_ENABLED=true`
5. `REDIS_URL=<tls-redis-url>`

### JWT Claim Contract
Required claims:
1. `sub` (stable user identifier).
2. `aud` including `"authenticated"`.

Role/capability claim inputs accepted by backend:
1. Roles from: `role`, `roles`, `org_role`, `org_roles`, `app_metadata.role(s)`, `user_metadata.role(s)`.
2. Capabilities from: `capabilities`, `permissions`, `org_permissions`, `app_metadata.capabilities/permissions`, `user_metadata.capabilities/permissions`.

Recommended staging admin template:
```json
{
  "sub": "{{user.id}}",
  "aud": "authenticated",
  "role": "authenticated",
  "email": "{{user.primary_email_address}}",
  "roles": ["admin"],
  "capabilities": ["*"],
  "app_metadata": {
    "roles": ["admin"],
    "capabilities": ["*"]
  },
  "user_metadata": {}
}
```

Recommended staging operator template:
```json
{
  "sub": "{{user.id}}",
  "aud": "authenticated",
  "role": "authenticated",
  "email": "{{user.primary_email_address}}",
  "roles": ["operator"],
  "app_metadata": {
    "roles": ["operator"]
  },
  "user_metadata": {}
}
```

## Delivered Work vs Production Criteria

### Criterion 1: No in-memory source-of-truth for critical state
Status: Done in code (deployment config still required)
1. Build/program entities now persist to normalized Supabase tables with startup rehydration.
2. Snapshot/file persistence remains as compatibility fallback only.

### Criterion 2: No client-driven runtime orchestration loops
Status: Done (with guarded emergency fallback)
1. Browser tick loop removed from `ScanLive`.
2. Backend runtime worker owns ticking under distributed lease/heartbeat.
3. Client tick is now only a bounded safety fallback path when worker is disabled or heartbeat appears stalled.

### Criterion 3: Multi-instance-safe idempotency + replay protection
Status: Done in code (deployment config still required)
1. Redis-backed coordination now covers nonce replay, idempotency, and runtime build leases.
2. Fail-closed mode is implemented (`COORDINATION_FAIL_CLOSED=true`) and returns service-level errors when coordination is unavailable.

### Criterion 4: Stable non-week API contracts
Status: Done (with compatibility bridge)
1. Canonical `/v1/program/*` paths are implemented.
2. Week routes remain temporarily for backward compatibility.

### Criterion 5: SLO dashboards + alerting operational
Status: Partial
1. SLO summary API exists.
2. Full observability dashboards/alerts are not production-complete yet.

### Criterion 6: Rollback drill + launch readiness flow
Status: Partial
1. Checklist/drill/decision data model + APIs + UI exist.
2. Operational runbooks and staged launch gates still need completion.

## Remaining Work (Prioritized)

### P0 (Required before claiming production-ready)
1. Enable production flags in deployed environments:
`CONTROL_PLANE_USE_SUPABASE=true`, `COORDINATION_FAIL_CLOSED=true`, `ENFORCE_CAPABILITY_AUTH=true`, `REDIS_URL=...`.
2. Apply latest migrations in staging/prod and verify table-level RLS behavior for new entities.
3. Complete rollout runbooks: incident response, rollback command path, on-call playbook.
4. Roll out JWT claim templates in identity provider and verify capability enforcement with at least one `admin` token and one `operator` token.

### P1 (Required for robust platform behavior)
1. Implement planner policy layer for dynamic DAG selection and richer autonomous/deep-scan planning.
2. Add durable event log query API and timeline UI (not just stream consumption).
3. Expand release readiness UX from raw JSON/operator widgets to production-grade dashboards.
4. Add benchmark and variance tracking automation for open-source validation runs.

### P2 (Scale and ops maturity)
1. Add comprehensive metrics/alerts (runtime latency, failure modes, fallback rates, gate failures).
2. Add background job instrumentation and dead-letter strategy.
3. Remove week-prefixed compatibility routes after migration window closes.

## Change Control (How to Keep This SSOT Trustworthy)
For every merged PR affecting platform/runtime/orchestration:
1. Update this file in the same PR.
2. Update these sections only:
`Validation Snapshot`, `Delivered Work vs Production Criteria`, and `Remaining Work`.
3. If behavior changes, update `What Must Be Working Right Now`.

## Operational Commands
1. Backend tests:
`cd /Users/christopher/Documents/AntiGravity/clarity-check/backend && PYTHONPATH=. pytest -q`
2. Frontend tests:
`cd /Users/christopher/Documents/AntiGravity/clarity-check && npm run test`
3. Frontend build:
`cd /Users/christopher/Documents/AntiGravity/clarity-check && npm run build`

## Source References
1. Build store: `/Users/christopher/Documents/AntiGravity/clarity-check/backend/orchestration/store.py`
2. Runtime worker/tick: `/Users/christopher/Documents/AntiGravity/clarity-check/backend/orchestration/runtime_worker.py`, `/Users/christopher/Documents/AntiGravity/clarity-check/backend/orchestration/runtime_tick.py`
3. Program routes: `/Users/christopher/Documents/AntiGravity/clarity-check/backend/api/routes/program.py`
4. Auth/capabilities: `/Users/christopher/Documents/AntiGravity/clarity-check/backend/api/middleware/auth.py`, `/Users/christopher/Documents/AntiGravity/clarity-check/backend/api/middleware/authorization.py`
5. New scan + live UI: `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/NewScan.tsx`, `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/ScanLive.tsx`
6. Release readiness UI: `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/ReleaseReadiness.tsx`
7. Normalized persistence adapters: `/Users/christopher/Documents/AntiGravity/clarity-check/backend/services/control_plane_tables.py`
8. Migrations: `/Users/christopher/Documents/AntiGravity/clarity-check/supabase/migrations/20260221123000_control_plane_persistence.sql`, `/Users/christopher/Documents/AntiGravity/clarity-check/supabase/migrations/20260221170000_control_plane_entity_hardening.sql`
