# ADR 0002: Primer and Intake Contract

- Date: 2026-02-16
- Status: Accepted

## Context

Audit quality depends on understanding repository structure and intended product behavior before detailed scanning. The primer must be fast, reliable, and reusable across repeated scans of the same commit.

## Decision

1. Introduce `Agent_Primer` as an explicit pre-audit agent.
2. Run primer in Daytona for consistency with the deep-audit execution model.
3. Target ~60 seconds runtime.
4. Use hybrid approach:
   - deterministic extraction (repo metadata, scripts, file map, config signals)
   - constrained LLM summary for purpose/flows/risks abstraction
5. Primer uses static + light commands only (no install/build/test).
6. On primer failure, continue with fallback intake and set lower confidence.
7. Persist primer artifacts in `project_primers` and reuse by commit SHA.

## Primer Output Contract

```json
{
  "primer_json": {},
  "summary": "",
  "repo_sha": "",
  "confidence": 0,
  "failure_reason": null
}
```

## Consequences

- Adds primer API and DB persistence requirements.
- Intake UX can prefill suggested critical flows to reduce user typing.
- Confidence scoring is first-class in report interpretation.
- Commit-level caching reduces repeat latency/cost on unchanged repos.
