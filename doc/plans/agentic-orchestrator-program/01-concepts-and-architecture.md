# Platform + Orchestration Program: Concepts and Architecture

## 1. Project Context and Objective

AntiGravity is not only building an orchestration engine. It is building a product platform with three connected outcomes:
1. Deterministic, low-cost baseline scans for broad onboarding.
2. Deep autonomous scans for production-grade diagnosis.
3. Guided implementation and auto-fix workflows that move users from findings to shipped improvements.

This program combines:
- platform implementation (frontend + backend integration),
- scan-tier architecture (deterministic and deep scan),
- autonomous orchestration foundation (OpenHands + Daytona + external control plane).

## 2. System Definitions

### 2.1 OpenHands

OpenHands is the agent execution runtime. It provides:
- agent loop and tool execution,
- conversation/event model,
- security confirmation policies,
- local/remote execution abstractions.

In this architecture, OpenHands executes work units; the control plane orchestrates multi-unit programs.

### 2.2 AgentField

AgentField represents a control-plane-oriented pattern:
- async execution lifecycle,
- webhook/event completion semantics,
- long-running orchestration concerns.

It is a reference for control-plane behavior, not a direct platform replacement.

### 2.3 SWE-AF

SWE-AF demonstrates autonomous engineering orchestration:
- DAG planning and level-parallel task execution,
- merge/test gates,
- debt/split/replan loops,
- checkpoint/resume behavior.

It is a reference for orchestration patterns and failure adaptation.

### 2.4 Daytona

Daytona is the sandbox/workspace isolation layer:
- ephemeral environment provisioning,
- command execution isolation,
- workspace lifecycle control.

In this architecture, Daytona underpins task isolation for both deterministic and deep scans.

### 2.5 Deterministic Scan (Tier 1)

A bounded-cost, deterministic pipeline:
- index/tree + AST + best-effort tool signals,
- no scanner LLM required,
- assistant report from normalized findings,
- quota and TTL controls for free-tier economics.

### 2.6 Deep Autonomous Scan (Tier 2+)

A multi-agent dynamic audit pipeline:
- deep repo analysis + runtime probing,
- security validation and prioritization,
- adaptive orchestration with retries and replanning,
- richer output for high-trust production migration guidance.

## 3. Comparative Model

| System | Strong At | Missing for Full Product Delivery |
| --- | --- | --- |
| OpenHands | Agent runtime, tool invocation, event/conversation lifecycle | Cross-agent DAG orchestration and platform-level release economics |
| AgentField | Async control-plane thinking, webhooks, lifecycle management | Complete product integration, hardened secret/governance defaults |
| SWE-AF | Practical autonomous orchestration and adaptation gates | Production hardening consistency and platform UX integration |
| Daytona | Isolation and workspace lifecycle | Product logic, orchestration semantics, and scan-tier policy |
| Current AntiGravity stack | Existing backend agents, API routes, Supabase schema, frontend surfaces | Complete platform wiring + deterministic/deep tier progression + hardened orchestration control plane |

## 4. Proposed Target Architecture

### 4.1 Layered Model

1. Experience Layer (platform UI)
- Onboarding, scan launch, live run stream, report, dashboard, fix workflow.

2. Product API Layer
- `/api/audit`, `/api/status/{scan_id}`, `/api/fix`, usage/limits/report artifacts.

3. Orchestration Control Layer
- DAG scheduler, gate state machine, policy enforcement, checkpoint/resume.

4. Execution Layer
- OpenHands agents running in Daytona isolated workspaces.

5. Data and Evidence Layer
- Supabase tables for projects, scan reports, action items, fix attempts, trajectories.
- Artifact/log storage and replayable event streams.

### 4.2 Scan-Tier Architecture

1. Tier 1 (Deterministic)
- Assistant onboarding -> deterministic scanner -> assistant report.
- Quota-aware and cost-bounded.

2. Tier 2 (Deep Scan)
- Multi-agent deep analysis and dynamic probing.
- Security/planner synthesis and stronger remediation quality.

3. Tier 3 (Auto-Fix)
- Apply fixes, verify, security-gate, generate PRs.

### 4.3 Prompt-Contract Layer

Prompt contracts are first-class interfaces, not ad hoc text:
- deterministic report synthesis prompt contract,
- deep-scan handoff contracts across scanner/builder/security/planner/educator,
- implementation-plan prompt contract for fix execution and acceptance checks.

Each contract must define input schema, required evidence, output schema, and failure behavior.

## 5. Execution Flow: Request to Deployment

### 5.1 Tier 1 Deterministic Flow

1. User submits repo and scan request.
2. Quota and project limits validated.
3. Index/cache refreshed.
4. Deterministic checks run.
5. Assistant report generated from normalized findings.
6. Results saved and streamed to live UI.

### 5.2 Tier 2 Deep Scan Flow

1. Orchestrator builds a task DAG from scan goal.
2. OpenHands tasks execute in Daytona workspaces.
3. Merge/test/review gates evaluate outputs.
4. Debt/split/replan handles complex failure paths.
5. Checkpoints persist at level barriers.
6. Final report and implementation plan are assembled.

### 5.3 Tier 3 Auto-Fix Flow

1. User selects fix action.
2. Builder agent applies patch in isolated workspace.
3. Test and security gates validate change.
4. Diff and PR metadata are generated.
5. Fix trajectory and evidence are persisted.

## 6. Safety Model

### 6.1 Mandatory Rules

1. No destructive repo operations on user-owned directories.
2. No approval/sandbox bypass flags in agent adapters.
3. Fail-closed gate behavior on reviewer/QA/replanner uncertainty.
4. Secret encryption at rest and masked logs.
5. Signed webhook payloads with nonce/timestamp replay defense.
6. Network and command policy enforcement in sandbox execution.

### 6.2 Enforcement Points

- API preflight policy checks.
- Runtime adapter argument guards.
- Gate-level stop conditions.
- Post-run audit and compliance checks.

## 7. IP Opportunity Map

### 7.1 Outcome Memory Graph

Store and retrieve cross-run relationships between:
- finding signatures,
- attempted fixes,
- test outcomes,
- true remediation success.

### 7.2 Scan Progression Intelligence

Predict when users should graduate from deterministic scan to deep autonomous scan based on:
- repo complexity,
- recurring failure patterns,
- risk profile and confidence intervals.

### 7.3 Risk-Aware Orchestration

Prioritize tasks by expected value under risk and cost constraints, not static order alone.

### 7.4 Policy and Governance Packs

Reusable policy bundles for enterprise constraints (security, compliance, branch controls, deployment gates).

## 8. Core Tradeoffs

| Tradeoff Axis | Option A | Option B | Program Position |
| --- | --- | --- | --- |
| Cost vs depth | Deterministic scan only | Deep autonomous scan | Two-tier strategy with progression gates |
| Speed vs safety | Aggressive autonomous execution | Fail-closed governance | Fail-closed by default |
| Simplicity vs power | Single-path pipeline | Multi-path scan + fix platform | Multi-path platform |
| Determinism vs adaptability | Strict deterministic flow | Adaptive replanning | Deterministic core + bounded adaptation |

## 9. KPIs and Expected Outcomes

### 9.1 Platform KPIs

1. End-to-end scan completion rate.
2. Median time to first usable report.
3. UI-to-backend integration reliability (SSE completion without manual retries).
4. Deterministic scan cost per run and p95 runtime.

### 9.2 Deep Scan KPIs

1. Deep scan success rate and recovery-after-failure rate.
2. Merge/test gate pass quality.
3. Replan efficacy (successful continuation after adaptation).

### 9.3 Auto-Fix KPIs

1. Fix attempt success rate.
2. Security-gate pass rate after fix.
3. PR acceptance or merge proxy metrics.

### 9.4 Expected Program Outcomes

- Platform can run deterministic scans at predictable cost.
- Deep autonomous scans deliver higher-confidence remediation plans.
- Auto-fix workflow reaches production deployment readiness.

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Platform/orchestration plans diverge | High | Single integrated roadmap with shared milestones |
| Deterministic scan quality too shallow | Medium | Tiered progression to deep scan and periodic check-set upgrades |
| Deep scan costs exceed budget | High | Strict budget envelopes, model routing, checkpoint reuse |
| Prompt contracts drift between agents | Medium | Versioned prompt contracts with schema tests |
| Security hardening delayed | High | Shift-left security tasks into MVP and beta gates |
| Team context gaps | Medium | Pairing rotations and weekly learning demos |

## 11. Glossary

- **Tier 1**: Deterministic-first free-tier scan.
- **Tier 2**: Deep autonomous scan with multi-agent execution.
- **Tier 3**: Auto-fix implementation loop.
- **Prompt Contract**: Versioned schema-bound prompt interface for agent handoffs.
- **BuildRun**: Top-level orchestration instance.
- **TaskRun**: Execution attempt for a task in isolated workspace.
- **Gate**: Deterministic quality/safety control point.
- **Fail-Closed**: Errors or uncertainty block progression by default.

## 12. References (Reviewed Repositories and Internal Plans)

### 12.1 External Repositories

- [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)
- [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk)
- [Agent-Field/agentfield](https://github.com/Agent-Field/agentfield)
- [Agent-Field/SWE-AF](https://github.com/Agent-Field/SWE-AF)

### 12.2 External Key Files

- [`openhands-tools/openhands/tools/delegate/impl.py`](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-tools/openhands/tools/delegate/impl.py)
- [`openhands-tools/openhands/tools/preset/planning.py`](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-tools/openhands/tools/preset/planning.py)
- [`openhands-sdk/openhands/sdk/conversation/state.py`](https://github.com/OpenHands/software-agent-sdk/blob/main/openhands-sdk/openhands/sdk/conversation/state.py)
- [`openhands/app_server/app_conversation/app_conversation_router.py`](https://github.com/OpenHands/OpenHands/blob/main/openhands/app_server/app_conversation/app_conversation_router.py)
- [`openhands/app_server/event/event_service.py`](https://github.com/OpenHands/OpenHands/blob/main/openhands/app_server/event/event_service.py)
- [`swe_af/execution/dag_executor.py`](https://github.com/Agent-Field/SWE-AF/blob/main/swe_af/execution/dag_executor.py)
- [`swe_af/execution/coding_loop.py`](https://github.com/Agent-Field/SWE-AF/blob/main/swe_af/execution/coding_loop.py)
- [`swe_af/app.py`](https://github.com/Agent-Field/SWE-AF/blob/main/swe_af/app.py)
- [`control-plane/internal/storage/execution_webhooks.go`](https://github.com/Agent-Field/agentfield/blob/main/control-plane/internal/storage/execution_webhooks.go)
- [`control-plane/internal/storage/observability_webhook.go`](https://github.com/Agent-Field/agentfield/blob/main/control-plane/internal/storage/observability_webhook.go)
- [Issue #65: inbound webhook secret/replay concern](https://github.com/Agent-Field/agentfield/issues/65)

### 12.3 Internal Source-of-Truth Docs

- `/Users/christopher/Documents/AntiGravity/clarity-check/PRD.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/IMPLEMENTATION_PLAN.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/NEXT_STEPS.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-implementation-execution-plan.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-orchestration-plan.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-1-deterministic-checks.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/tier-2-planning-track.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/plans/agent-org-chart-and-flow.md`
- `/Users/christopher/Documents/AntiGravity/clarity-check/doc/daytona-llms-full.txt`
