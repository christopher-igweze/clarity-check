# Implementation Plan — Clarity Check

**Last updated:** 2026-02-20
**Source of truth:** `PRD.md` (Technical PRD v2.1)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| [x] | Done — code exists and is functional |
| [~] | Partial — scaffolded or has known issues |
| [ ] | Not started |

---

## Phase 1: Python Backend + OpenHands Orchestration (FOUNDATION)

### 1.1 Project structure & infrastructure

- [x] FastAPI project skeleton (`backend/main.py`, CORS, middleware, health check)
- [x] Pydantic settings / config (`backend/config.py`)
- [x] Dockerfile (Python 3.12 slim, non-root, health check)
- [x] `docker-compose.yml` (single `api` service, port 8000, live-reload)
- [x] `requirements.txt` (FastAPI, OpenHands SDK, Daytona, Supabase, PyJWT, etc.)

### 1.2 Database schema (Supabase / PostgreSQL)

- [x] Core migration — 7 tables: `profiles`, `projects`, `scan_reports`, `action_items`, `fix_attempts`, `trajectories` + RLS policies + indexes
- [x] `security_review` JSONB column on `scan_reports`
- [x] `github_access_token` on `profiles`

### 1.3 API routes

- [x] `POST /api/audit` — create project, create scan_report, kick off background pipeline (`backend/api/routes/audit.py`)
- [x] `GET /api/status/{scan_id}` — SSE stream via in-memory event bus (`backend/api/routes/status.py`)
- [~] `POST /api/fix` — stub only; returns "queued" message (`backend/api/routes/fix.py`) — **full loop is Phase 3**
- [ ] `POST /api/webhook` — GitHub webhook handlers (PRD §5 mentions `webhook.py` but file does not exist)

### 1.4 Middleware

- [x] JWT auth — Supabase token verification, skips health/docs (`backend/api/middleware/auth.py`)
- [x] Rate limiting — SlowAPI, 10 req/min default (`backend/api/middleware/rate_limit.py`)

### 1.5 Services

- [x] Supabase client — `get_or_create_project`, `create_scan_report`, `update_scan_status`, `save_report`, `save_findings`, `save_action_items`, `save_education` (`backend/services/supabase_client.py`)
- [x] GitHub service — repo URL parsing, repo info fetching (`backend/services/github.py`)
- [x] OpenRouter service — LLM routing per agent (`backend/services/openrouter.py`)
- [x] Context store — thread-safe key/value store scoped to scan session (`backend/services/context_store.py`)

### 1.6 Sandbox management

- [x] Sandbox manager — Daytona lifecycle: provision, execute, destroy, resource limits (`backend/sandbox/manager.py`)
- [ ] Sandbox executor — dedicated command execution module (`sandbox/executor.py` — PRD lists it but file does not exist; execution currently inlined in `manager.py`)
- [ ] Network policy — whitelist npm/pip/GitHub, block everything else (`sandbox/network_policy.py` — PRD lists it but file does not exist)

### 1.7 Agent implementations

- [x] Base agent — abstract OpenHands SDK wrapper (`backend/agents/base_agent.py`)
- [x] Orchestrator — master pipeline: provision → Scanner → Builder → Security → Planner → Educator → assemble → save → teardown (`backend/agents/orchestrator.py`)
- [x] Agent_Scanner (Gemini 3 Pro) — full repo ingestion, static analysis, semgrep, npm audit, architecture mapping (`backend/agents/scanner.py`)
- [x] Agent_Builder (DeepSeek V3.2) — dynamic probing: install, build, test, startup, endpoint checks (`backend/agents/builder.py`)
- [x] Agent_Security (DeepSeek V3.2) — finding validation, OWASP analysis, secrets detection, CVE review (`backend/agents/security.py`)
- [x] Agent_Planner (Claude Opus) — prioritisation, step-by-step remediation, effort estimates (`backend/agents/planner.py`)
- [x] Agent_Educator (Claude Sonnet) — "Why This Matters" + "CTO Perspective" cards (`backend/agents/educator.py`)

### 1.8 Data persistence (recent bug fixes — completed)

- [x] **Bug fix:** `scan_reports.project_id` FK violation — `start_audit` now calls `get_or_create_project()` before inserting
- [x] **Bug fix:** scan_report ID consistency — `create_scan_report` now accepts caller-supplied `scan_id` as the row `id`
- [x] **Bug fix:** education card overwrite — `save_education` now targets specific `action_item_id` instead of blanket-updating by `scan_report_id`

### 1.9 Scoring algorithm

- [x] Category score: start at 100, deduct by severity (critical -25, high -15, medium -8, low -3)
- [x] Probe factor adjusts reliability score
- [x] Health score: `(security * 0.40) + (reliability * 0.35) + (scalability * 0.25)`

### 1.10 SSE streaming

- [x] In-memory event bus (`_sse.py`)
- [x] Background task emits `AgentLogEntry` events as agents work
- [x] SSE endpoint yields events with proper `event:` / `data:` framing
- [x] Timeout after 10 minutes of idle

---

## Phase 2: Frontend Integration

The React frontend is fully built (pages, components, auth, routing) but currently wired to **legacy Supabase Edge Functions**. It needs to be re-pointed at the Python backend.

### 2.1 API client (`src/lib/api.ts`)

- [x] Replace `streamSurfaceScan()` (calls Edge Function `surface-scan`) with a call to `POST /api/audit` + `GET /api/status/{scan_id}` SSE
- [ ] Replace `callSecurityReview()` (calls Edge Function `security-review`) — no longer needed; security agent is part of the pipeline
- [ ] Replace `streamDeepProbe()` (calls Edge Function `deep-probe`) — no longer needed; builder agent is part of the pipeline
- [x] Keep or refactor `streamVisionIntake()` — moved to Python backend `/api/vision-intake`
- [x] Add `startAudit(repoUrl, vibePrompt?, projectCharter?)` — POST to `/api/audit`, return `scan_id`
- [x] Add `streamScanStatus(scanId, onEvent)` — EventSource to `/api/status/{scan_id}`
- [ ] Add proper auth header injection (Supabase JWT)

### 2.2 ScanLive page (`src/pages/ScanLive.tsx`)

- [x] Remove call chain: `fetchRepoContents` → `streamSurfaceScan` → `callSecurityReview` → `streamDeepProbe`
- [x] Replace with: `startAudit()` → `streamScanStatus()` — single SSE stream for the entire pipeline
- [ ] Update `LogEntry` type to match `AgentLogEntry` model from backend (`event_type`, `agent`, `message`, `level`, `data`)
- [ ] Update `agentColors` map to match backend agent names (`scanner`, `builder`, `security`, `planner`, `educator`, `orchestrator`)
- [x] Wire health score and findings from `scan_complete` event to navigate to Report page

### 2.3 Report page (`src/pages/Report.tsx`)

- [ ] Verify Supabase queries match the updated schema (action_items has `action_item_id`-keyed education fields now)
- [ ] Display `why_it_matters` and `cto_perspective` from action_items (already queries them, should work as-is)
- [ ] Add dynamic proof section (probe_results from `report_data` JSONB)
- [ ] Add security verdict badges (confirmed/rejected per finding)

### 2.4 Dashboard page (`src/pages/Dashboard.tsx`)

- [ ] Ensure project list queries `projects` table (should already work via Supabase RLS)
- [ ] Show `latest_health_score` from project row (updated after each scan)

### 2.5 NewScan page (`src/pages/NewScan.tsx`)

- [x] Wire form submit to new `startAudit()` API client function
- [x] Navigate to ScanLive with `scan_id` from response (instead of passing repoUrl/content in route state)

### 2.6 Cleanup

- [x] Remove legacy Supabase Edge Function references from frontend
- [ ] Delete `supabase/functions/` directory if it still exists (Edge Functions are replaced by Python backend)
- [ ] Update `.env` / `VITE_*` variables if the backend URL differs from Supabase Functions URL

---

## Phase 3: Auto-Fix (Revenue)

### 3.1 Fix execution loop

- [ ] Implement full `POST /api/fix` handler — look up action item + fix_steps, provision sandbox, run Agent_Builder with fix instructions
- [ ] Agent_Builder fix mode — read Planner's fix plan, edit code, run tests, self-correct (up to 3 retries)
- [ ] Agent_Security review gate — validate diff doesn't introduce new vulnerabilities
- [ ] Diff preview — generate before/after comparison, store in `fix_attempts.diff_preview`
- [ ] GitHub PR creation — push branch, open PR with description, store `fix_attempts.pr_url`

### 3.2 Database persistence

- [ ] Write `fix_attempts` rows (status, sandbox_id, diff_preview, pr_url, agent_logs, timing)
- [ ] Write `trajectories` rows (prompt, code_changes, test_results, success boolean)

### 3.3 Payment

- [ ] Stripe integration — charge $149 before running auto-fix
- [ ] Payment verification middleware
- [ ] Receipt/invoice generation

### 3.4 Frontend — fix UI

- [ ] "Fix This" button on each action item in Report page
- [ ] Fix progress SSE stream (reuse `/api/status/` or add `/api/fix-status/`)
- [ ] Diff viewer component (before/after code comparison)
- [ ] PR link display after successful fix

---

## Phase 4: Production Hardening

### 4.1 Error handling & resilience

- [ ] Agent retry logic — retry up to 3x with exponential backoff on failure
- [ ] Sandbox failure recovery — provision new container and resume
- [ ] Model fallback — e.g. Claude Opus → GPT-5.2 on API failure
- [ ] Graceful degradation — partial reports when one agent fails (currently the whole pipeline fails)

### 4.2 Observability

- [ ] Structured logging (JSON format) for all agents and API routes
- [ ] Monitoring — health metrics, agent success rates, latency percentiles
- [ ] Alerting — failed scans, sandbox timeouts, model API errors
- [ ] Save `agent_logs` JSONB to `scan_reports` for post-mortem debugging

### 4.3 Security & abuse prevention

- [~] Network policy enforcement in sandbox (`sandbox/network_policy.py`)
- [ ] Rate limiting tuning — per-user, per-IP, burst caps
- [ ] Input validation — repo URL sanitisation, size limits
- [ ] Secrets management audit — ensure no keys in code/images

### 4.4 Performance

- [ ] Connection pooling for Supabase client (currently creates a new client per call)
- [ ] Prompt caching where supported (reduce input token costs ~90%)
- [ ] Concurrent agent execution where possible (Scanner + Builder could run in parallel)
- [ ] Event bus — consider Redis/pub-sub instead of in-memory list for multi-process deployments

### 4.5 Missing backend files from PRD

- [x] `sandbox/executor.py` — dedicated command execution abstraction
- [x] `sandbox/network_policy.py` — whitelist/blacklist rules for sandbox networking
- [x] `api/routes/webhook.py` — GitHub webhook handlers (PR status, push events)
- [ ] MCP tool integration — `search_codebase`, `read_file`, `run_command`, `screenshot` (PRD §5.3)

---

## Current Status Summary

| Phase | Status | Notes |
|-------|--------|-------|
| **Phase 1** — Backend foundation | **~98% complete** | Agents, orchestrator, API routes, DB schema, and core services are in place. Sandbox executor/network policy and webhook route now exist; remaining work is deeper reliability hardening. |
| **Phase 2** — Frontend integration | **~90% complete** | Core scan path and vision intake are wired to Python backend (`/api/audit`, `/api/status`, `/api/vision-intake`, limits/artifacts). Remaining work is mainly type cleanup and final UX polish. |
| **Phase 3** — Auto-fix (paid) | **Stub only** | `POST /api/fix` returns a placeholder response. Full fix loop, payment, PR creation not implemented. |
| **Phase 4** — Production hardening | **In progress** | Added webhook signature + replay checks and sandbox command/network policy enforcement scaffold. Retry logic/monitoring/perf work still pending. |

### Recommended next step

**Phase 3 (Auto-fix revenue loop) + Phase 4 hardening** are now the critical path.

1. Implement full `POST /api/fix` execution loop (sandbox edit/test/verify/PR)
2. Add robust retry/recovery and model fallback behavior
3. Complete observability and incident alerting baselines
4. Tighten policy enforcement and security controls for production rollout
