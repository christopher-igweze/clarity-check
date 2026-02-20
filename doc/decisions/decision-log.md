# Decision Log

Date: 2026-02-16

## Confirmed Decisions

1. Org model is personal org for MVP (1 user = 1 org).
2. Org-level data stays in `profiles` for MVP; no standalone org table yet.
3. Org onboarding is required.
4. Org onboarding uses 4 screens total.
5. Org Q1 options are `Founder`, `Vibe coder`, `Engineer`.
6. Org Q2 explanation style options are `Teach me`, `Just steps`, `CTO brief`.
7. Org Q3 shipping posture options are `Ship fast`, `Balanced`, `Production-first` with default `Balanced`.
8. Org Q4 combines tool tags and marketing acquisition source in one screen.
9. Marketing acquisition source is required.
10. Acquisition options use a full list and include `Founder begged me to try it`.
11. Project onboarding is required for all audits.
12. Project onboarding is max 5 questions.
13. Project onboarding UI is a wizard form.
14. There is no surface/deep split going forward; all scans are deep audits.
15. Paid feature is implementation/fix workflow, not scan depth.
16. Primer runs before project questions.
17. Primer is a dedicated agent (`Agent_Primer`), not an internal hidden step only.
18. Primer execution plane is Daytona.
19. Primer target runtime is ~60 seconds.
20. Primer method is hybrid (deterministic extraction + constrained LLM summary).
21. Primer command depth is static + light commands only (no install/build/test).
22. Primer failure policy is fallback onboarding without primer suggestions, with lower confidence.
23. Primer persistence is a new table with commit-aware reuse.
24. Primer reuse policy is by commit SHA.
25. Specialist agent topology was selected.
26. CodeScene-style behavioral analysis is explicitly included via a dedicated `Agent_Evolution`.

## Baseline Agent Topology

- Hermes (CTO orchestrator)
- Agent_Primer
- Agent_Scanner
- Agent_Evolution
- Agent_Builder
- Agent_Security
- Agent_Planner
- Agent_Educator
- Agent_Implementer (paid)
- Agent_Verifier (paid)

## Pricing and Metering Decisions (2026-02-16)

27. Use LOC as an eligibility/abuse guardrail, not as the primary billing unit.
28. Meter paid usage by compute credits tied to real cost drivers (audit runs, implementation runs, monitoring jobs).
29. Rescan metering must be incremental: changed LOC + impacted files, not full-repo LOC every run.
30. Plan enforcement uses dual caps: LOC cap OR project-count cap, whichever is hit first.
31. Tier 1 (Free) includes 10 scans/month, deterministic-first analysis, cheap Hermes summary, and stateless report handling.
32. Tier 1 report behavior is download-oriented with no long-term persistence or cross-scan memory.
33. Tier 2 is the full audit pipeline + history/tracking, excluding implementation and realtime monitoring.
34. Tier 2 should not launch as true unlimited initially; use bundled credits + overage until telemetry validates margins.
35. Tier 3 includes everything in Tier 2 plus implementation workflow, realtime monitoring, and self-improvement suggestions.
36. Tier 1 baseline flow is: new project → index → store index with TTL (target 30 days) → deterministic scanner → Hermes-assistant report generation.
37. Tier 1 deterministic scanner check-set is `Balanced` (approximately 15 checks, signal/cost middle ground).
38. Tier 1 repo-size guardrail is max `50k LOC` per project snapshot.
39. Free-tier monthly cap is `10 scans = 10 reports`; quota consumption is tied to successful report generation.
40. Free-tier project-count cap default is `3 projects`, enforced alongside LOC cap (whichever limit is hit first).
41. Free-tier report artifact download TTL default is `7 days`; index TTL remains `30 days`.
42. Free-tier monthly quota reset policy default is `calendar month (UTC)`.
43. Tier 1 orchestration is explicitly simplified to three steps:
    - assistant onboarding
    - deterministic scanning
    - assistant report
44. Tier 1 communication transport is in-process synchronous handoff (no queue/event-bus complexity for v1).
45. Tier 1 `Balanced` deterministic scanner is locked to 15 checks, specified in `doc/plans/tier-1-deterministic-checks.md`.
46. Tier 1 scanner engine stack is locked to deterministic `repo tree/index + AST + linter/audit` (no LLM in scanner).
47. AST engine baseline is `tree-sitter` for supported languages with deterministic regex fallback when parsing is unavailable.
48. Linter/audit signals are best-effort and runtime-available only (no install/build/test step added to Tier 1 scan path).
49. Every deterministic check must declare a primary engine and optional fallback engine.
50. Index cache contract is commit-aware and diff-friendly: keyed by `project_id + repo_sha`, TTL `30 days`, reused on same SHA, rebuilt on SHA change.
