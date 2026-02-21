# Agentic Orchestrator Program — Single Source of Truth (SSOT)

Last updated: February 21, 2026  
Repository: `/Users/christopher/Documents/AntiGravity/clarity-check`  
Primary branch in progress: `codex/prod-hardening-phase1`  
Active PR: https://github.com/christopher-igweze/clarity-check/pull/4

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
`BuildStore` + `ProgramStore` with durable snapshot adapters.
3. Durability:
Supabase snapshot adapter (`control_plane_state` table) + optional local file fallback.
4. Ephemeral coordination:
Redis optional for nonce/idempotency; in-process fallback when Redis not configured.
5. Runtime execution authority:
Backend `RuntimeWorker` drives runtime ticks; frontend observes events and sends control actions only.
6. API shape:
Canonical program APIs under `/v1/program/*` with week endpoints retained for compatibility.
7. UI surfaces:
`Dashboard`, `NewScan`, `ScanLive`, `ReleaseReadiness`, and `ProgramOps` (advanced).

## What Must Be Working Right Now

### A) Build Flow (Autonomous Default)
1. `NewScan` creates a `BuildRun` via `/v1/builds` when `VITE_BUILD_CONTROL_PLANE_ENABLED=true`.
2. `scan_mode` defaults to `autonomous` (explicitly passed in metadata from UI).
3. `ScanLive` streams build events and does not run client tick loops.
4. Backend runtime worker bootstraps/ticks builds to completion or fail state.

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
1. Backend tests: `85 passed` (`cd backend && PYTHONPATH=. pytest -q`).
2. Frontend unit tests: `10 passed` (`npm run test`).
3. Frontend production build: success (`npm run build`).

## Delivered Work vs Production Criteria

### Criterion 1: No in-memory source-of-truth for critical state
Status: Partial
1. Durable snapshots now exist (Supabase + optional file fallback).
2. Still not full normalized DB read/write for every build/program entity.

### Criterion 2: No client-driven runtime orchestration loops
Status: Done
1. Browser tick loop removed from `ScanLive`.
2. Backend runtime worker owns ticking.

### Criterion 3: Multi-instance-safe idempotency + replay protection
Status: Partial
1. Redis-backed coordination implemented (optional).
2. Production readiness depends on actually deploying Redis and enforcing it.

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
1. Replace snapshot-centric persistence with normalized DB repositories for build/program entities.
2. Add distributed lease/heartbeat lock for runtime worker ownership per build.
3. Enable and enforce capability auth in deployed envs with real claims mapping from auth provider.
4. Define and enforce fail-closed behavior when Redis is unavailable in production.
5. Complete rollout runbooks: incident response, rollback command path, on-call playbook.

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
7. Migration: `/Users/christopher/Documents/AntiGravity/clarity-check/supabase/migrations/20260221123000_control_plane_persistence.sql`
