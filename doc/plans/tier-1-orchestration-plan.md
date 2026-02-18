# Tier 1 Orchestration Plan

Date: 2026-02-16
Status: Drafted for review before implementation

## Scope

Tier 1 flow only:
- `assistant onboarding -> deterministic scan (includes index + 30d cache) -> assistant report`

Constraints:
- `10 scans/reports per month` (count on successful report generation)
- `<= 50k LOC` per project snapshot
- `<= 3 projects` per free user
- report download TTL: `7 days`
- reset window: `calendar month (UTC)`

---

## 1) Agent Communication Plan

### 1.1 Runtime Roles (Tier 1)

- `Assistant_Onboarding` (collects minimal context and validates inputs)
- `Scanner_Deterministic` (balanced ~15 checks)
- `Assistant_Report` (cheap model summarization)

### 1.2 Message Contract (Internal)

Use one simple synchronous envelope between steps:

```json
{
  "scan_id": "uuid",
  "user_id": "string",
  "project_id": "uuid",
  "stage": "onboarding|scan|report",
  "status": "started|completed|failed",
  "payload": {},
  "metrics": {
    "duration_ms": 0,
    "files_seen": 0,
    "loc_estimate": 0
  },
  "error": null
}
```

### 1.3 Data Contract Between Components

`Assistant_Onboarding -> Scanner_Deterministic`
- validated repo/project inputs
- basic context summary
- tier guardrail context (quota/project/loc caps)

`Scanner_Deterministic -> Assistant_Report`
- normalized findings JSON
- grouped counts by severity/category
- deterministic evidence snippets

`Assistant_Report -> Report Generator`
- executive summary (short)
- issue explanation blocks
- prioritized next steps

### 1.4 Failure Communication

- Pre-flight or indexing failure: return actionable failure reason; no quota consumed.
- Scanner failure: return deterministic failure reason; no quota consumed.
- Summary failure: return fallback deterministic report template; still counts if report is generated.

---

## 2) Tooling Plan

### 2.1 Deterministic Scanner (Balanced 15 Checks)

Canonical check catalog is defined in:
- `doc/plans/tier-1-deterministic-checks.md`

Scanner engine stack is fixed to:
- Repo tree/index engine (`git ls-files`, LOC/hash/language metadata)
- AST engine (`tree-sitter` for supported languages, regex fallback)
- Linter/audit engine (best effort with strict timeout, no install step)

Each check must emit:
- `check_id`
- `pass/fail/warn`
- `evidence`
- `severity`
- `category`
- `suggested_fix_stub`

### 2.1.1 Indexing Contract

- index key: `project_id + repo_sha`
- cache TTL: `30 days`
- manifest fields: `path`, `language`, `loc`, `sha256`, `path_role`
- AST fact fields: route markers, auth/rate-limit markers, risky calls, query construction hints
- reuse rule:
  - same `repo_sha`: reuse cached index
  - changed `repo_sha`: rebuild changed files and refresh aggregate facts

### 2.2 Assistant Report (Cheap Model) Tooling

- Single prompt template fed with deterministic findings only
- token cap + truncation strategy
- strict JSON output format for report sections
- fallback non-LLM template if model call fails

### 2.3 Storage/TTL Tooling

- index cache store with `expires_at` (30 days)
- report artifact store with `expires_at` (7 days)
- daily cleanup job for expired free-tier artifacts

### 2.4 Metering/Gating Tooling

- monthly counter table for free scans/reports
- project-count tracker per user
- LOC cap checker at index stage
- UTC month rollover logic

---

## 3) Activity Plan (Execution Sequence)

### 3.1 Pre-flight

1. Validate user tier (`free`).
2. Validate monthly quota (`reports_generated < 10`).
3. Validate project cap (`projects_count < 3` or existing project).

### 3.2 Onboarding Activity

4. Run assistant onboarding prompts and validate required context.

### 3.3 Scan Activity

5. Build or refresh deterministic index for the project snapshot.
6. Persist index cache with `expires_at = now + 30 days` keyed by `project_id + repo_sha`.
7. Run deterministic scanner with balanced checks using `index + AST + best-effort linter/audit` signals.
8. Persist normalized findings (temporary for free flow only).

### 3.4 Report Activity

9. Call Assistant_Report with deterministic findings payload.
10. Generate report artifact (downloadable).
11. Persist report metadata with `expires_at = now + 7 days`.

### 3.5 Metering Activity

12. Increment free monthly report count only after report artifact is successfully generated.
13. Emit quota remaining in response.

### 3.6 Cleanup Activity

14. Scheduled cleanup removes expired report artifacts and expired index caches.

---

## 4) Open Items For Next Planning Pass

1. Report artifact format for Tier 1 (`markdown` first vs `pdf` first).
2. Exact DB schema for metering and TTL artifacts.
