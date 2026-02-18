# ADR 0001: Onboarding and Agent Architecture Baseline

- Date: 2026-02-16
- Status: Accepted

## Context

The product direction is "CTO in a box" with high-quality deep audits and clear remediation guidance. The onboarding flow must stay short while still collecting enough context to personalize output style and audit priorities.

## Decision

1. Use a personal-org MVP model (1 user = 1 org) and store org data in `profiles`.
2. Enforce required org onboarding with 4 screens:
   - Q1: technical level (`Founder`, `Vibe coder`, `Engineer`)
   - Q2: explanation style (`Teach me`, `Just steps`, `CTO brief`)
   - Q3: shipping posture (`Ship fast`, `Balanced`, `Production-first`; default `Balanced`)
   - Q4: combined screen for tool tags + required acquisition source
3. Enforce required project onboarding with 5 questions via wizard UI.
4. Freeze specialist architecture centered on Hermes with dedicated agents:
   - Primer, Scanner, Evolution, Builder, Security, Planner, Educator
   - Implementer + Verifier as paid workflow

## Rationale

- Keeps user friction low while collecting actionable personalization signals.
- Preserves product differentiation: deep audit quality, business-context prioritization, and adaptive communication.
- Clear agent boundaries reduce prompt coupling and simplify later tuning.

## Consequences

- Additional schema fields are required on `profiles` for onboarding completion and preferences.
- Frontend route gating must block core workflows until onboarding is complete.
- Report generation will need stable contracts across specialist agents.
- Future multi-user teams can be added by promoting profile-level defaults to an org table.
