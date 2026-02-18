# Tier 2 Planning Track

Date: 2026-02-16  
Status: Active planning track (no new Tier 2 decisions locked in this file yet)

## 1) Purpose

Keep Tier 2 planning isolated from Tier 1 execution so another agent can ship Tier 1 while we make Tier 2 decisions deliberately.

## 2) Context References (Read Before Planning)

- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/decision-log.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/adrs/0001-onboarding-and-agent-architecture.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/adrs/0002-primer-and-intake-contract.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/adrs/0003-pricing-and-metering-model.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/agent-org-chart-and-flow.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-offering-baseline.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-orchestration-plan.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-implementation-execution-plan.md`

## 3) Tier 2 Locked Baseline From Existing Decisions

Already decided (imported from decision log):

1. Tier 2 is full audit pipeline + persistence/tracking.
2. Tier 2 excludes implementation workflow and realtime monitoring (those are Tier 3).
3. Billing direction is not true unlimited at launch; use bundled credits + overage first.
4. LOC remains guardrail; compute credits meter actual usage.
5. Rescans should be incremental (changed LOC + impacted files).

## 4) Tier 2 Target Outcome

Tier 2 user should get:

1. Deep multi-agent audit with specialist pipeline.
2. Historical memory and cross-scan tracking.
3. Commit-aware reuse and incremental rescans.
4. Higher-confidence recommendations than Tier 1.
5. Persistent report history, deltas, and trend views.

## 5) Proposed Tier 2 Scope Boundary

## In scope

- Full specialist audit path:
  - `Primer -> Scanner -> Evolution -> Builder -> Security -> Planner -> Educator`
- Persistent project history:
  - report timeline
  - findings delta between scans
  - trend indicators
- Credit accounting and limits for paid usage.
- Incremental re-scan logic over cached index/artifacts.

## Out of scope

- Auto-implementation (`Agent_Implementer`)
- Post-fix validation (`Agent_Verifier`)
- Realtime monitoring and continuous suggestions

## 6) Workstreams

## WS1: Product and Packaging

- Define Tier 2 included monthly credits.
- Define overage behavior and hard-stop vs soft-overage.
- Define who can buy add-on credits.

## WS2: Metering and Credits

- Translate each expensive action into credit units.
- Track per-scan credit breakdown (compute + model + tooling).
- Build predictable cost controls (timeouts, token caps, retries cap).

## WS3: Multi-Agent Runtime Contracts

- Define per-agent input/output contracts in stable schemas.
- Define failure policy per agent:
  - fail-fast
  - degrade with confidence penalty
  - retry policy
- Define orchestration sequence and optional parallel steps.

## WS4: Data Model and Persistence

- Historical scan summaries.
- Findings lineage/delta model:
  - new
  - recurring
  - resolved
- Per-project long-lived context and preference memory.

## WS5: User Experience and Reporting

- Tier 2 dashboard:
  - trends
  - hotspot movement
  - unresolved risk backlog
- Report shape and exports.
- Confidence/explainability blocks tied to evidence.

## WS6: Operational Controls

- Runtime budgets by repo size bands.
- Queueing/prioritization policy.
- Observability:
  - cost per scan
  - scan latency
  - failure causes

## 7) Tier 2 Open Decision Queue (Plan One-by-One)

Each decision should be settled explicitly and copied into:
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/decisions/decision-log.md`

### D2-01 Credits Package

Choose Tier 2 monthly included credits and initial overage rate model.

### D2-02 Project/LOC Limits in Tier 2

Set practical caps (or cap bands) to prevent abuse and protect margin.

### D2-03 Agent Runtime Budgets

Set default timeouts and retry policy per agent and per scan.

### D2-04 Failure Policy

Decide which agents are mandatory vs optional-degrade in final report.

### D2-05 Persistence Window

Choose retention for Tier 2 artifacts/history and what is user-visible.

### D2-06 Delta Algorithm

Define the canonical method for new/recurring/resolved findings between scans.

### D2-07 Confidence Scoring

Define how confidence is computed and displayed in Tier 2 reports.

### D2-08 Tier 2 Report Contract

Freeze sections and schema for API and UI rendering.

## 8) Suggested Planning Order

1. D2-01 Credits Package
2. D2-02 Project/LOC Limits
3. D2-03 Agent Runtime Budgets
4. D2-04 Failure Policy
5. D2-06 Delta Algorithm
6. D2-08 Report Contract
7. D2-05 Persistence Window
8. D2-07 Confidence Scoring

## 9) Risks To Watch During Planning

1. Margin risk from long scans if budgets are not strict.
2. User trust risk if confidence is unclear when partial failures happen.
3. Complexity risk if Tier 2 contracts are not stable before coding.
4. UX risk if report is detailed but not actionable.

## 10) Planning Log (append-only)

Use this section for short planning snapshots before formal decision log entries.

- 2026-02-16: Tier 2 planning track created. No new Tier 2 decisions locked yet.
