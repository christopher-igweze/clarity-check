# ADR 0003: Pricing and Metering Model

- Date: 2026-02-16
- Status: Accepted

## Context

The platform has three intended tiers and potentially expensive cost drivers:
- Daytona runtime
- LLM token usage
- test/build execution time
- implementation loops and monitoring jobs

A simple LOC-only pricing model is easy to explain but does not track true compute cost. We need a model that is understandable to users and sustainable for margins.

## Decision

1. Use LOC as a guardrail for eligibility/abuse control, not as the primary billing meter.
2. Meter actual usage through compute credits tied to expensive actions:
   - audit runs
   - implementation runs
   - monitoring jobs
3. For rescans, compute usage must be incremental:
   - meter based on changed LOC + impacted files
   - avoid full-repo re-indexing and full-context re-analysis by default
4. Enforce plan ceilings by dual limits:
   - LOC cap
   - project-count cap
   - whichever limit is reached first blocks additional usage
5. Tier framing:
   - Tier 1 (Free): 10 scans/month, deterministic-first analysis, cheap summary model, stateless reports
   - Tier 2: full audit pipeline + persistence/tracking, excludes implementation and realtime monitoring
   - Tier 3: everything in Tier 2 plus implementation and realtime monitoring/suggestions
6. Tier 2 should launch with bundled credits + overage instead of true unlimited until usage telemetry validates sustainable margins.

## Rationale

- Aligns pricing with actual compute cost and margin risk.
- Keeps onboarding and packaging simple for users (clear tier labels + predictable limits).
- Supports efficient rescans by rewarding incremental analysis design.
- Prevents heavy users from forcing negative unit economics under flat unlimited pricing.

## Consequences

- Requires usage metering tables and counters for compute credits.
- Requires project indexing and diff-aware analysis pipeline.
- Requires tier gating logic in API and UI.
- Requires monthly reset logic for free-tier scan allowances.
