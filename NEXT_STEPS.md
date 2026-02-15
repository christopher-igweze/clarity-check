# Next Steps — Implementation Plan Execution

_Last reviewed: 2026-02-15_

## What is already true in the codebase

1. The FastAPI backend is ready to drive audits end-to-end:
   - `POST /api/audit` creates a project + scan row, then starts the orchestrator in the background.
   - `GET /api/status/{scan_id}` streams typed SSE events until `scan_complete` / `scan_error`.
2. The frontend scan path is still using legacy Supabase Edge Functions (`surface-scan`, `security-review`, `deep-probe`) and manually persists scan artifacts from the browser.
3. The implementation plan correctly identifies **Phase 2 (frontend integration)** as the critical path.

## What to do next (priority order)

### P0 — Rewire frontend to Python backend

1. **Replace legacy API helpers in `src/lib/api.ts`:**
   - Add `startAudit({ repoUrl, scanTier, vibePrompt, projectCharter })` for `POST /api/audit`.
   - Add `streamScanStatus(scanId, onEvent)` for `GET /api/status/{scan_id}`.
   - Inject Supabase session JWT into `Authorization: Bearer <token>`.
   - Keep `streamVisionIntake` unchanged for now.

2. **Refactor `src/pages/ScanLive.tsx`:**
   - Remove local pipeline chain (`fetchRepoContents → streamSurfaceScan → callSecurityReview → streamDeepProbe`).
   - Start a single backend run with `startAudit`.
   - Subscribe to SSE with `streamScanStatus` and render agent logs from backend `event_type` payloads.
   - On `scan_complete`, route to report page by returned `scan_id`.

3. **Adjust scan launch flow in `src/pages/NewScan.tsx`:**
   - Pass scan config only (repo URL/tier/prompt), not large repo content.
   - Navigate using `scan_id` once created.

### P1 — Make report page consume backend-native artifacts

4. **Update `src/pages/Report.tsx`:**
   - Read security verdicts and probe output from `scan_reports.report_data` + `scan_reports.security_review`.
   - Keep education cards sourced from `action_items.why_it_matters` and `action_items.cto_perspective`.

5. **Dashboard polish in `src/pages/Dashboard.tsx`:**
   - Confirm `latest_health_score` and scan counts are populated from backend writes only.

### P2 — Cleanup + hardening after migration

6. Remove unused frontend calls/imports (`surface-scan`, `security-review`, `deep-probe`, `fetchRepoContents` from scan flow).
7. Mark `supabase/functions/*` as legacy/deprecated (or delete after full cutover).
8. Add a small contract test for SSE event parsing in frontend utilities.

## Suggested execution slices

- **Slice A (1 PR):** `api.ts` + `ScanLive.tsx` migration, minimal UI parity.
- **Slice B (1 PR):** `NewScan` and navigation/state cleanup.
- **Slice C (1 PR):** `Report` + `Dashboard` backend artifact alignment.
- **Slice D (1 PR):** dead-code cleanup + docs + tests.

## Definition of done for Phase 2

- Starting a scan from UI triggers `POST /api/audit` and returns a real `scan_id`.
- Live scan screen consumes only backend SSE events.
- No legacy edge function calls are required for normal scan/report flow.
- Report and dashboard render data produced by backend orchestrator persistence.
