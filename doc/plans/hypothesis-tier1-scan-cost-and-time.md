# Hypothesis: Tier 1 Scan Cost and Runtime

Date: 2026-02-16  
Status: Working hypothesis (not a pricing commitment)

## Purpose

Estimate likely per-scan cost and runtime for Tier 1 (`assistant onboarding -> deterministic scan -> assistant report`) so we can price safely before full telemetry is available.

## Inputs and Assumptions

### A) Daytona compute rates (public pricing)

- vCPU: `$0.000014 / vCPU / sec`
- RAM: `$0.0000045 / GB / sec`
- Reference sandbox: `2 vCPU`, `4 GB RAM`

Estimated runtime burn for this sandbox:
- `((2 * 0.000014) + (4 * 0.0000045)) * 60 = ~$0.00276 / min`

Note:
- Storage/network transfer are excluded here (expected to be small at Tier 1 scale).

### B) Tier 1 model assumption (assistant summary only)

- Model assumption: `google/gemini-2.5-flash-lite`
- Pricing assumption:
  - input: `$0.10 / 1M tokens`
  - output: `$0.40 / 1M tokens`

### C) Operational assumptions

- Deterministic scanner only (no scanner LLM call).
- One assistant summary call per successful scan.
- Index cache exists; first run pays full indexing, rescan on same snapshot benefits from cache.

## Cost/Time Hypothesis by Repo Size

| Repo size (LOC) | Expected runtime | Daytona compute | Assistant LLM | Estimated total/scan |
|---|---:|---:|---:|---:|
| 5k LOC | 2-4 min | $0.006-$0.011 | $0.001-$0.002 | **$0.007-$0.013** |
| 20k LOC | 4-8 min | $0.011-$0.022 | $0.002-$0.004 | **$0.013-$0.026** |
| 50k LOC | 8-15 min | $0.022-$0.041 | $0.004-$0.007 | **$0.026-$0.048** |

## Interpretation

- Working range for Tier 1 per scan is approximately **$0.01-$0.05**.
- Compute (Daytona runtime) is the dominant cost driver in Tier 1; assistant summary cost is secondary.
- Cache hits should reduce average runtime on repeat scans of unchanged snapshots.

## Validation Plan (before pricing freeze)

1. Add per-stage timing instrumentation (`index`, `scan`, `summary`).
2. Log assistant token counts (`input_tokens`, `output_tokens`).
3. Record cold vs warm cache runs separately.
4. Refit the table after the first 200 production scans.
