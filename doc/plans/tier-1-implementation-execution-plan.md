# Tier 1 Implementation Execution Plan (Handoff)

Date: 2026-02-16  
Status: Ready for execution by a separate agent  
Scope: Implement Tier 1 only while Tier 2 planning continues in parallel

## 1) Read This First (Source of Truth)

The implementing agent must read these docs before writing code:

- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/decision-log.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/adrs/0001-onboarding-and-agent-architecture.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/adrs/0002-primer-and-intake-contract.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/adrs/0003-pricing-and-metering-model.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-offering-baseline.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-orchestration-plan.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-deterministic-checks.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/hypothesis-tier1-scan-cost-and-time.md`

If any implementation choice conflicts with these docs, stop and update decisions first.

## 2) Locked Constraints (Do Not Reinterpret)

1. Tier 1 flow is exactly:
   - `assistant onboarding -> deterministic scan -> assistant report`
2. Free-tier limits:
   - `10 scans/reports per month`
   - `<= 50k LOC`
   - `<= 3 projects`
   - limit hit rule: `whichever cap is hit first`
3. Index cache:
   - key: `project_id + repo_sha`
   - TTL: `30 days`
4. Report artifact:
   - TTL: `7 days`
5. Scanner engine stack:
   - deterministic `repo tree/index + AST + best-effort linter/audit`
   - no scanner LLM
6. Monthly reset:
   - calendar month in UTC
7. Quota consumption rule:
   - count only when report artifact is successfully generated

## 3) Current Code Snapshot (Why This Work Is Needed)

- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/api/routes/audit.py` currently calls full multi-agent orchestrator.
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/agents/orchestrator.py` runs Scanner/Evolution/Builder/Security/Planner/Educator (Tier 2/3 behavior).
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/services/supabase_client.py` does not yet implement free-tier usage counters, index cache tables, or report TTL artifact handling.
- `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/NewScan.tsx` currently triggers primer and full audit intake flow.

Tier 1 requires a separate low-cost execution path without removing the existing full pipeline code.

## 4) Implementation Strategy

Use a separate Tier 1 pipeline and keep the current full pipeline intact behind feature flags.

### 4.1 Feature flags (required)

Add to `/Users/christopher/Documents/AntiGravity/clarity-check/backend/config.py`:

- `tier1_enabled: bool = True`
- `tier1_assistant_model: str = "google/gemini-2.5-flash-lite"`
- `tier1_loc_cap: int = 50000`
- `tier1_monthly_report_cap: int = 10`
- `tier1_project_cap: int = 3`
- `tier1_index_ttl_days: int = 30`
- `tier1_report_ttl_days: int = 7`

Add frontend flag in `.env` usage (read-only in code, no secret):
- `VITE_TIER1_ENABLED=true`

## 5) Work Packages (Execution Order)

## WP0: Scaffolding and Contracts

Create backend package:
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/__init__.py`
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/contracts.py`
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/orchestrator.py`
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/quota.py`
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/indexer.py`
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/scanner.py`
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/reporter.py`

`contracts.py` must define:
- `Tier1Finding`
- `Tier1ScanResult`
- `Tier1ReportArtifact`
- `Tier1QuotaStatus`

DoD:
- code compiles and imports cleanly from `backend/api/routes/audit.py`

## WP1: Supabase Schema and Persistence

Create migration:
- `/Users/christopher/Documents/AntiGravity/clarity-check/supabase/migrations/<timestamp>_tier1_usage_index_artifacts.sql`

Required tables:

1. `free_usage_monthly`
- `id uuid pk default gen_random_uuid()`
- `user_id text not null`
- `month_key date not null` (first day of month in UTC)
- `reports_generated integer not null default 0`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `unique(user_id, month_key)`

2. `project_indexes`
- `id uuid pk default gen_random_uuid()`
- `project_id uuid not null references projects(id) on delete cascade`
- `user_id text not null`
- `repo_sha text not null`
- `loc_total integer not null default 0`
- `file_count integer not null default 0`
- `index_json jsonb not null default '{}'::jsonb`
- `expires_at timestamptz not null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `unique(project_id, repo_sha)`

3. `report_artifacts`
- `id uuid pk default gen_random_uuid()`
- `scan_report_id uuid not null references scan_reports(id) on delete cascade`
- `project_id uuid not null references projects(id) on delete cascade`
- `user_id text not null`
- `artifact_type text not null default 'markdown'`
- `content text not null`
- `expires_at timestamptz not null`
- `created_at timestamptz not null default now()`
- `unique(scan_report_id, artifact_type)`

Required indexes:
- `free_usage_monthly(user_id, month_key)`
- `project_indexes(project_id, repo_sha)`
- `project_indexes(expires_at)`
- `report_artifacts(scan_report_id, user_id)`
- `report_artifacts(expires_at)`

RLS:
- same pattern as existing user-scoped tables using `public.requesting_user_id()`.

Add/update helper functions in:
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/services/supabase_client.py`

Required methods:
- `get_or_create_free_usage_month(user_id, month_key)`
- `increment_free_reports_generated(user_id, month_key)`
- `get_active_project_count(user_id)`
- `get_project_index(project_id, repo_sha)`
- `upsert_project_index(...)`
- `save_report_artifact(...)`
- `get_report_artifact(scan_report_id, user_id)`
- `delete_expired_report_artifacts()`
- `delete_expired_project_indexes()`

DoD:
- migration applies with `supabase db push`
- helper methods tested with one read/write cycle each

## WP2: Tier 1 Preflight and Gating

In `/Users/christopher/Documents/AntiGravity/clarity-check/backend/api/routes/audit.py`:

Before creating background task:
1. Validate org onboarding complete from `profiles.onboarding_complete`.
2. Resolve/create project.
3. Enforce project cap (`<= 3`) for new projects.
4. Resolve repo SHA and run index preflight to estimate LOC.
5. Enforce LOC cap (`<= 50k`).
6. Load month usage row and enforce report cap (`< 10`).

Error responses must be explicit:
- `402/403` style for limit exceeded (pick one and keep consistent).
- include machine-readable code:
  - `limit_reports_exceeded`
  - `limit_projects_exceeded`
  - `limit_loc_exceeded`
  - `onboarding_required`

DoD:
- route blocks correctly on each cap
- no quota consumed when request is blocked

## WP3: Deterministic Indexer

Implement in `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/indexer.py`:

Pipeline:
1. clone/open repo workspace
2. get `repo_sha`
3. file manifest via `git ls-files`
4. compute:
   - `loc_total`
   - `file_count`
   - per-file metadata (`path`, `ext`, `loc`, `sha256`)
5. AST extraction using `tree-sitter` where supported
6. best-effort linter/audit probe with strict timeout
7. write cache row in `project_indexes` with TTL 30 days

Reuse logic:
- if `(project_id, repo_sha)` exists and `expires_at > now()`, reuse cached index
- otherwise rebuild and overwrite

DoD:
- same SHA run uses cache
- changed SHA run rebuilds
- emits metrics: files seen, loc total, cache hit bool

## WP4: Deterministic Scanner (15 Checks)

Implement scanner in:
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/scanner.py`
- optional check modules under `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/checks/`

Scanner must implement exactly the 15 checks defined in:
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-deterministic-checks.md`

Output must match the contract in that doc, including:
- `check_id`
- `status`
- `category`
- `severity`
- `engine`
- `confidence`
- `evidence[]`
- `suggested_fix_stub`

DoD:
- deterministic output (no model calls)
- at least one unit test fixture per category

## WP5: Assistant Report Generator

Implement in `/Users/christopher/Documents/AntiGravity/clarity-check/backend/tier1/reporter.py`:

Input:
- normalized deterministic findings
- grouped severity/category counts
- intake context

Output:
- report markdown
- machine summary JSON (scores/counts/next steps)

Model:
- `settings.tier1_assistant_model` default `google/gemini-2.5-flash-lite`

Fallback:
- if model call fails, generate deterministic template report

Persist:
- save markdown to `report_artifacts` with `expires_at = now + 7 days`

Quota:
- increment monthly report count only after artifact save succeeds

DoD:
- successful scan always yields downloadable report content
- model outage still yields fallback report

## WP6: Tier 1 Orchestration Route

In `/Users/christopher/Documents/AntiGravity/clarity-check/backend/api/routes/audit.py`:

Add a Tier 1 background runner (new function) that emits SSE events in this order:
1. `agent_start` (`Orchestrator`) preflight passed
2. `agent_start` (`Agent_Scanner`) indexing/scanning start
3. `agent_complete` (`Agent_Scanner`) scan done
4. `agent_start` (`Agent_Educator` or `Orchestrator`) report synthesis start
5. `scan_complete` final payload with:
   - `health_score`
   - category scores
   - `findings_count`
   - `quota_remaining`
   - `report_artifact_available=true`

Error path:
- emit `scan_error`
- set scan status failed
- do not increment monthly usage

DoD:
- `/api/status/{scan_id}` reflects Tier 1 lifecycle cleanly

## WP7: Frontend Wiring for Tier 1

Update:
- `/Users/christopher/Documents/AntiGravity/clarity-check/src/lib/api.ts`
- `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/NewScan.tsx`
- `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/ScanLive.tsx`
- `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/Report.tsx`
- `/Users/christopher/Documents/AntiGravity/clarity-check/src/pages/Dashboard.tsx`

Required UI behavior:
1. Keep existing onboarding gate.
2. Keep project intake wizard (5-step).
3. Show free-tier remaining quota (reports left this month).
4. On completion, show “Download report” action.
5. If report expired, show clear message and next action (run new scan).

DoD:
- user can complete end-to-end Tier 1 run without touching Tier 2 UI

## WP8: TTL Cleanup

Implement cleanup logic in backend:
- `/Users/christopher/Documents/AntiGravity/clarity-check/backend/services/supabase_client.py`
- optional script `/Users/christopher/Documents/AntiGravity/clarity-check/backend/scripts/cleanup_tier1_artifacts.py`

Behavior:
- delete expired rows from `report_artifacts`
- delete expired rows from `project_indexes`

Invocation (MVP):
- run once at API startup and once every N scan starts (cheap opportunistic cleanup)

DoD:
- expired artifacts are not returned by download API

## 6) API Contracts to Implement

## 6.1 Start Audit (existing route)

`POST /api/audit` remains the entrypoint.

Add response fields (non-breaking extension):
- `quota_remaining: number | null`
- `tier: "free"`

## 6.2 New Limits Endpoint

Add:
- `GET /api/limits`

Response:

```json
{
  "tier": "free",
  "month_key": "2026-02-01",
  "reports_generated": 3,
  "reports_limit": 10,
  "reports_remaining": 7,
  "project_count": 2,
  "project_limit": 3,
  "loc_cap": 50000
}
```

## 6.3 Report Download Endpoint

Add:
- `GET /api/report-artifacts/{scan_id}`

Rules:
- only owner can access
- return 404 if expired or missing
- return markdown payload

## 7) Test Matrix (Minimum Required)

Backend tests to add (new `backend/tests` folder):

1. onboarding incomplete blocks audit.
2. new project beyond cap blocks audit.
3. LOC > 50k blocks audit.
4. reports_generated >= 10 blocks audit.
5. successful report increments usage by exactly 1.
6. scanner failure does not increment usage.
7. same SHA reuses index cache.
8. changed SHA rebuilds index cache.
9. report artifact expires after TTL.
10. limits endpoint returns correct month counters.

Frontend tests (or manual QA checklist if no test harness available):

1. quota shown on scan screen.
2. limit errors shown with actionable copy.
3. scan live stream completes and routes to report.
4. report download works when not expired.

## 8) Rollout Plan

1. Merge with `tier1_enabled=false` default.
2. Run migration in staging.
3. Enable `tier1_enabled=true` in staging.
4. Execute full QA matrix.
5. Enable in production for internal users only.
6. Observe for 48 hours:
   - avg scan time
   - cost/scan
   - failure rate
7. open to all free users.

## 9) Deliverables Checklist

- [ ] migration merged and applied
- [ ] backend Tier 1 modules merged
- [ ] `/api/audit` Tier 1 path working
- [ ] `/api/limits` and `/api/report-artifacts/{scan_id}` working
- [ ] frontend end-to-end Tier 1 flow working
- [ ] tests added and passing
- [ ] docs updated with final API payload examples

## 10) Explicit Non-Goals for This Execution

- No Tier 2 pricing/credit pack implementation.
- No Tier 3 implementation/fix automation.
- No redesign of specialist multi-agent pipeline.
- No “unlimited” plan mechanics.

This plan is intentionally narrow: ship Tier 1 with predictable cost and deterministic behavior.
