# 16-Week Platform Delivery Roadmap and Team Breakdown

## 1. Program Overview

- Program: AntiGravity Platform + Autonomous Orchestration
- Start date: Monday, February 23, 2026
- End date: Sunday, June 14, 2026
- Team: Ifeanyi, Tolu, Justin (peer model)
- Scope: platform implementation, deterministic scan foundation, deep autonomous scan evolution, and deployment readiness

## 2. Executive Timeline and Milestones

| Milestone                       | Date                           | Definition of Done                                                             |
| ------------------------------- | ------------------------------ | ------------------------------------------------------------------------------ |
| Program kickoff                 | February 23, 2026              | Team operating model active; roadmap baselined                                 |
| Architecture + contracts freeze | March 8, 2026                  | API, event, prompt contracts versioned and approved by team consensus          |
| Platform integration baseline   | March 29, 2026                 | Frontend wired to Python backend audit/status path in staging                  |
| Internal MVP release            | April 12, 2026                 | Tier 1 deterministic scan + initial deep-scan orchestration running end-to-end |
| Open-source validation window   | April 13, 2026 to May 10, 2026 | Repeatable matrix runs, reliability and variance reports published             |
| External beta release           | May 17, 2026                   | Beta hardening complete with safety and observability gates                    |
| GA production deployment        | June 14, 2026                  | Deployment checklist complete, rollback tested, hypercare active               |

## 3. Workstream Breakdown and Ownership

### 3.1 Collaboration Model (Peer Team)

1. All three contributors are equals for technical decision-making.
2. Decisions use consensus-first process.
3. A rotating "driver of the week" breaks deadlocks only when needed.
4. Ifeanyi is project initiator/context anchor, not default sole approver.

### 3.2 Focus Areas by Person

#### Ifeanyi (Core Systems + Product Coherence)

- Co-own orchestration core (scheduler, gates, replanner) with hands-on implementation.
- Co-own platform architecture coherence across Tier 1 and deep scan.
- Co-own prompt-contract design and versioning.

#### Tolu (API + Platform Integration)

- Co-own API surface, persistence, and lifecycle endpoint behavior.
- Co-own frontend/backend integration and scan flow migration.
- Co-own checkpoint persistence and run-state integrity.

#### Justin (Runtime + Validation + Reliability)

- Co-own OpenHands runner gateway and Daytona workspace lifecycle.
- Co-own CI/eval pipelines, metrics, and reliability instrumentation.
- Co-own benchmark matrix and open-source validation reporting.

## 4. Workstreams (Integrated)

1. Platform Integration Track

- Move frontend from legacy edge functions to Python backend APIs.
- Complete scan launch, live stream, and report wiring.

2. Tier 1 Deterministic Scan Track

- Deterministic scanner, quota/limits, artifact TTL, report synthesis path.

3. Deep Autonomous Scan Track

- DAG scheduler, merge/test gates, debt/split/replan, checkpoint/resume.

4. Prompt-Contract and Implementation Plan Track

- Versioned prompt contracts for onboarding, deterministic reporting, deep-scan handoffs, and fix execution plans.

5. Reliability/Security/Deployment Track

- Policy enforcement, secret/replay hardening, observability, rollout and rollback readiness.

## 5. Weekly Task Plan (16 Weeks)

| Week | Date Range       | Ifeanyi                                                                        | Tolu                                                                                                  | Justin                                                                      | Weekly Exit Output                                 |
| ---- | ---------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------- |
| 1    | Feb 23 to Mar 1  | Implement orchestration engine skeleton; draft prompt-contract registry format | Scaffold API route adapters for `/api/audit` and `/api/status`; begin frontend API client rewrite | Scaffold runner gateway + Daytona workspace bootstrap; baseline CI pipeline | Shared architecture repo skeleton + contract draft |
| 2    | Mar 2 to Mar 8   | Implement state-machine core types and gate contracts                          | Implement `BuildRun`/`TaskRun` persistence and status retrieval paths                             | Implement telemetry and structured run logging baseline                     | Contracts frozen by team consensus                 |
| 3    | Mar 9 to Mar 15  | Implement DAG parse/level scheduler and deterministic gate transitions         | Integrate scheduler with API workers; migrate `src/lib/api.ts` to backend endpoints                 | Implement OpenHands task-launch bridge in Daytona and event normalization   | Single-level deep-scan execution in staging        |
| 4    | Mar 16 to Mar 22 | Implement checkpoint/recovery algorithm and replay guards                      | Rewire `ScanLive.tsx` to backend SSE schema; update event mapping and logs                          | Implement artifact persistence and stream observability hooks               | Crash/resume and live stream validated             |
| 5    | Mar 23 to Mar 29 | Implement policy-engine v0 (no-destructive and no-bypass guards)               | Rewire `NewScan.tsx`, dashboard/report backend data paths; remove legacy edge-function flow         | Implement index/cache instrumentation for deterministic scans               | Platform integration baseline complete             |
| 6    | Mar 30 to Apr 5  | Implement merge/test gates and minimal replanner loop                          | Implement Tier 1 deterministic scanner orchestration and quota endpoint integration                   | Implement deterministic scan runtime checks and report artifact storage     | Tier 1 + deep-scan core paths both runnable        |
| 7    | Apr 6 to Apr 12  | Implement deep-scan debt/split handling and bounded retries                    | Complete frontend routing on `scan_complete` + report rendering contract                            | Harden CI checks and runtime dashboard for MVP operations                   | Internal MVP released (Apr 12)                     |
| 8    | Apr 13 to Apr 19 | Triage failures and patch scheduler/replanner logic from validation wave 1     | Improve API/backpressure behavior under concurrent runs                                               | Execute open-source benchmark wave 1 and publish findings                   | Validation wave 1 report                           |
| 9    | Apr 20 to Apr 26 | Implement prompt-contract v2 for deep handoffs and fix planning                | Implement timeout/stuck-run controls and SSE resilience improvements                                  | Execute benchmark wave 2 + regression deltas                                | Validation wave 2 report                           |
| 10   | Apr 27 to May 3  | Implement orchestration hot-path optimizations and failure taxonomy updates    | Implement deterministic/deep mode switch controls in API contracts                                    | Execute benchmark wave 3 and variance analysis                              | Validation wave 3 report                           |
| 11   | May 4 to May 10  | Implement top reliability fixes from validation matrix                         | Close API consistency bugs for resume/abort/idempotency                                               | Publish final open-source validation summary + threshold results            | Validation exit criteria met                       |
| 12   | May 11 to May 17 | Implement fail-closed enforcement for reviewer/QA/replanner and policy gates   | Implement idempotency keys and lock handling across lifecycle endpoints                               | Implement secret encryption and webhook replay protection                   | External beta release (May 17)                     |
| 13   | May 18 to May 24 | Implement orchestration hardening refactors from beta telemetry                | Implement auto-fix API alpha flow and fix-attempt persistence wiring                                  | Implement SLO dashboard + incident alerting + chaos test harness            | Beta reliability uplift checkpoint                 |
| 14   | May 25 to May 31 | Implement launch-gating controls and production safeguards                     | Implement final report/fix UX integration gaps                                                        | Run resilience drills and tune operational thresholds                       | Launch-readiness package complete                  |
| 15   | Jun 1 to Jun 7   | Implement cutover safeguards and rollback automation checks                    | Final bugfix sweep across platform integration and API contracts                                      | Final deployment automation and backup/restore validation                   | GA preflight checklist complete                    |
| 16   | Jun 8 to Jun 14  | Co-lead production cutover and hypercare fixes                                 | Co-lead production cutover and post-launch triage                                                     | Co-lead production cutover and telemetry watch                              | GA deployed by Jun 14                              |

## 6. MVP Scope and Release Gate

### 6.1 MVP Scope (Internal Release by April 12, 2026)

1. Frontend integrated with backend `audit/status` flow (no legacy edge-function dependency for core scan path).
2. Tier 1 deterministic scan path operational (index + deterministic checks + report).
3. Initial deep autonomous scan path operational (DAG + checkpoint/resume + merge/test gates).
4. Basic prompt-contract versioning for deterministic report and deep-scan handoffs.
5. Baseline observability and failure diagnostics.

### 6.2 MVP Release Gate

All must pass:

1. End-to-end scan flow succeeds on at least 3 representative repos.
2. Forced crash recovery resumes without duplicate execution.
3. Deterministic scan budget envelope stays within agreed threshold.
4. No critical policy bypass or destructive execution path detected.

## 7. Open-Source Validation Plan and Acceptance Criteria

### 7.1 Validation Window

- Start: April 13, 2026
- End: May 10, 2026

### 7.2 Validation Scope

1. At least 10 open-source repositories across Python and Node.
2. At least 3 repeated runs per repository.
3. Both deterministic and deep-scan modes tested where applicable.

### 7.3 Acceptance Criteria

1. Reliability and regression metrics meet beta thresholds.
2. Run-to-run variance documented and bounded.
3. Failure categories mapped to concrete remediation tickets.
4. Validation report includes method, dataset, run config, and aggregate outcomes.

## 8. Beta Hardening Plan (May 11, 2026 to June 1, 2026)

1. Enforce fail-closed behavior across review and replanning gates.
2. Add lifecycle idempotency and concurrency lock guarantees.
3. Complete secret-at-rest encryption and replay-safe webhook handling.
4. Finalize operational runbooks and incident routing.
5. Stabilize SLOs, dashboards, and alerts.
6. Validate auto-fix alpha plumbing with safety gates.

## 9. Final Production Deployment Checklist

### 9.1 Pre-Deployment

1. Migration scripts validated in staging.
2. Rollback scripts tested with timing evidence.
3. Prompt-contract versions pinned and release-tagged.
4. Incident runbooks and on-call rota confirmed.
5. Canary policy and safety checks defined.

### 9.2 Deployment Day

1. Execute deployment automation.
2. Verify health checks and readiness endpoints.
3. Verify scan launch, SSE stream, report rendering, and policy enforcement.
4. Verify deterministic and deep-scan mode routing.
5. Verify metrics/log/trace ingestion.

### 9.3 Post-Deployment (Hypercare Week 1)

1. Twice-daily reliability review.
2. Critical incident response within agreed SLA.
3. KPI and cost tracking versus launch baseline.
4. Priority hotfix process active.

## 10. RACI Matrix (Peer-Team Version)

| Area                                                       | Responsible           | Accountable      | Consulted                 | Informed             |
| ---------------------------------------------------------- | --------------------- | ---------------- | ------------------------- | -------------------- |
| Architecture and interface contracts                       | Ifeanyi, Tolu, Justin | Team (consensus) | Product stakeholders      | Team                 |
| Orchestration core (scheduler, gates, replanner)           | Ifeanyi, Tolu         | Team (consensus) | Justin                    | Team                 |
| Platform API and persistence                               | Tolu, Ifeanyi         | Team (consensus) | Justin                    | Team                 |
| OpenHands + Daytona runtime integration                    | Justin, Ifeanyi       | Team (consensus) | Tolu                      | Team                 |
| Frontend/backend scan flow integration                     | Tolu, Justin          | Team (consensus) | Ifeanyi                   | Team                 |
| Prompt-contract versioning and implementation-plan prompts | Ifeanyi, Tolu, Justin | Team (consensus) | Product stakeholders      | Team                 |
| CI, evaluation, validation reporting                       | Justin, Tolu          | Team (consensus) | Ifeanyi                   | Product stakeholders |
| Security hardening and deployment readiness                | Ifeanyi, Tolu, Justin | Team (consensus) | Security/Ops stakeholders | Team                 |

## 11. Operating Cadence

1. Weekly planning (Monday): commit to scoped weekly outcomes and pairing rotations.
2. Mid-week sync (Wednesday): blockers, architecture drift checks, and priority corrections.
3. Friday demo + retro: shipped artifacts, failures, learnings, and next-week adjustments.
4. Driver-of-week rotation: changes weekly among Ifeanyi, Tolu, Justin.

## 12. Phase Exit Criteria

### Phase 0 Exit (Mar 8, 2026)

1. Architecture, API, event, and prompt contracts frozen.
2. Mock end-to-end trace run is successful.

### Phase 1 Exit (Mar 29, 2026)

1. Frontend and backend core scan path integrated in staging.
2. Deep-scan scheduler baseline executes single-level plans.

### Phase 2 Exit (Apr 12, 2026)

1. Internal MVP gate checklist passes.
2. Deterministic and deep baseline paths are both operational.

### Phase 3 Exit (May 10, 2026)

1. Open-source validation report complete.
2. Reliability thresholds approved for beta expansion.

### Phase 4 Exit (Jun 1, 2026)

1. Critical security and reliability issues closed.
2. SLO dashboards and alerts operational.

### Phase 5 Exit (Jun 14, 2026)

1. GA deployment completed.
2. Rollback drill passed.
3. Hypercare plan active and staffed.

## 13. Public APIs, Interfaces, Types, and Events

### 13.1 Endpoints

1. `POST /v1/builds`
2. `GET /v1/builds/{build_id}`
3. `POST /v1/builds/{build_id}/resume`
4. `POST /v1/builds/{build_id}/abort`
5. `GET /v1/builds/{build_id}/events` (SSE)
6. `POST /api/audit`
7. `GET /api/status/{scan_id}`
8. `POST /api/fix`
9. `GET /api/limits`
10. `GET /api/report-artifacts/{scan_id}`

### 13.2 Core Types

1. `BuildRun`
2. `DagNode`
3. `TaskRun`
4. `ReplanDecision`
5. `DebtItem`
6. `PolicyViolation`
7. `ScanReport`
8. `ActionItem`
9. `FixAttempt`
10. `Trajectory`

### 13.3 Event Schema

1. `BUILD_STARTED`
2. `LEVEL_STARTED`
3. `TASK_STARTED`
4. `TASK_COMPLETED`
5. `TASK_FAILED`
6. `MERGE_GATE`
7. `TEST_GATE`
8. `REPLAN_DECISION`
9. `BUILD_FINISHED`
10. `agent_start`
11. `agent_log`
12. `agent_complete`
13. `scan_complete`
14. `scan_error`

## 14. Test Cases and Validation Scenarios

1. Checkpoint/resume recovery after crashes at every lifecycle stage.
2. Concurrency correctness with parallel DAG levels.
3. Merge conflict and integration-test gate behavior.
4. Replanner action correctness: `CONTINUE`, `MODIFY_DAG`, `REDUCE_SCOPE`, `ABORT`.
5. Fail-closed behavior when reviewer/QA/replanner subsystems fail.
6. Policy enforcement tests for blocked commands/restricted actions.
7. Secret handling tests for encryption, masking, and non-leak guarantees.
8. Webhook replay attack simulation with nonce/timestamp/HMAC checks.
9. Open-source benchmark repeatability and variance thresholds.
10. Deployment rollback drill in staging before GA.
11. Frontend integration test: scan launch -> live stream -> report route.
12. Deterministic-scan budget envelope tests (cost and latency bounds).
13. Prompt-contract schema tests for each handoff prompt.
14. Auto-fix alpha safety tests (no unsafe patch merge path).

## 15. Assumptions and Defaults

1. Deliverables are Markdown-based.
2. Folder path remains under `doc/plans/agentic-orchestrator-program/`.
3. Team members are near full-time on this program.
4. Week 1 starts February 23, 2026.
5. Internal MVP includes both deterministic and deep baseline paths.
6. Open-source validation is mandatory before beta expansion.
7. Production go/no-go is a joint team decision (consensus with rotating driver tie-break only if needed).
8. Existing source-of-truth docs (`PRD.md`, `IMPLEMENTATION_PLAN.md`, tier-1/tier-2 plans) remain authoritative inputs.
