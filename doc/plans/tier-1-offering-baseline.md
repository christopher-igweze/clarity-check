# Tier 1 (Free) Offering Baseline

Date: 2026-02-16

## Product Goal

Deliver a low-cost, high-signal first audit for new users while protecting platform margins.

## Tier 1 Definition (Locked)

- 10 scans per month
- deterministic-first analysis pipeline
- low-cost Hermes summary model for user-facing report
- stateless usage mode:
  - no long-term report persistence
  - no cross-scan memory/context
  - report download supported

## Core Constraints

- keep compute spend low and predictable
- avoid large-context full-repo LLM analysis in free tier
- avoid persistent storage costs for long-lived artifacts in free tier

## Tier 1 Architecture Direction

1. Assistant onboarding step captures minimal project context.
2. Deterministic scanner runs and produces normalized findings.
   - engine stack: `repo tree/index + AST + best-effort linter/audit` (no LLM in scanner)
3. Assistant generates the final user-facing report from deterministic findings.
4. Report is generated and offered as download.
5. Temporary free-tier artifacts are purged after TTL.

## Locked Tier 1 Decisions (Round 1)

- Deterministic scanner depth: `Balanced` (~15 checks).
- Deterministic scanner method: `tree/index + AST + linter/audit` with deterministic regex fallback.
- Flow clarification accepted:
  - `new project -> index -> store TTL (~30 days) -> deterministic scanner -> Hermes-assistant report`.
- Tier 1 orchestration simplification accepted:
  - `assistant onboarding -> deterministic scanning -> assistant report`.
- Repo-size guardrail: `<= 50k LOC`.
- Monthly free quota semantics: `10 scans = 10 reports` (counted on successful report generation).
- Free-tier project-count cap: `3 projects` (with LOC/project caps enforced by whichever limit is hit first).
- Free-tier report download TTL: `7 days`.
- Monthly quota reset policy: `calendar month (UTC)`.

## In Scope for Tier 1 Planning

- monthly scan limit enforcement (10/month)
- report generation/download flow
- deterministic scanner contract and finding schema
- cheap summarizer prompt contract
- stateless storage policy (TTL + cleanup strategy)
- usage metering for free scans consumed

## Out of Scope for Tier 1

- implementation/fix workflow
- realtime monitoring
- long-term project memory
- full specialist deep pipeline for every run

## Success Criteria

- user can complete an end-to-end audit in free tier without setup friction
- each scan consumes bounded compute budget
- monthly cap enforcement is reliable
- report quality is actionable for MVP users

## Planning Kickoff Questions

1. What exact deterministic checks are in v1 scanner (minimum must-have set)?
2. What max repository size/file count should Tier 1 allow?
3. What report format is canonical for v1 (PDF, Markdown, both)?
4. What TTL should be used for temporary free-tier report artifacts?
5. What should happen when user hits 10/10 scans (hard block vs waitlist/upgrade prompt)?
