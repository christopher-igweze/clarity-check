# One-Shot Implementation Framework (OpenAI, Anthropic, Gemini)

This framework is the canonical contract for generating implementation prompts that should succeed in one pass for coding tasks.

## Cross-Provider Invariants
- Declare one concrete objective with explicit success criteria.
- Include hard constraints (scope, safety, no disabling tests/CI, no TODO-only fixes).
- Provide required validation commands and expected evidence.
- Force strict output contract (JSON schema with exact keys).
- Instruct: no follow-up questions; make safe assumptions and proceed.
- Require branching, implementation note doc, and user-facing summary.

## OpenAI Overlay
- Keep instructions explicit and deterministic.
- Put output schema and forbidden behavior in the prompt body.
- Emphasize strict format fidelity and command-backed evidence.
- Prefer concise action-first language over narrative.

## Anthropic Overlay
- Be clear and direct.
- Use structured, explicit task sections and acceptance criteria.
- Require assumptions to be listed briefly if context is missing.
- Keep final answer schema-only and avoid extra prose.

## Gemini Overlay
- Treat the prompt as a system-style execution contract.
- Use deterministic ordered steps and explicit command requirements.
- Reinforce schema-first output and assumption logging.
- Keep policy and safety constraints concrete and testable.

## Common Anti-Patterns
- Ambiguous objective or missing acceptance criteria.
- Missing test/scan commands or no evidence requirements.
- Asking for "best effort" without strict output schema.
- Allowing follow-up question loops during one-shot runs.
- Mixing strategy brainstorming with execution instructions.

## Copy/Paste One-Shot Template
```text
You are a senior software engineer executing a one-shot remediation task in a real repository.

Objective:
- [exact change to implement]

Success Criteria:
- [criterion 1]
- [criterion 2]
- [criterion 3]

Hard Constraints:
- Keep changes minimal and scoped.
- Do not disable tests, CI, or safety checks.
- Do not ask follow-up questions; make safe assumptions, record them, and proceed.
- Create branch `codex/[repo]-[task]-[runid]`.
- Create/update `docs/agent-implementation-note.md` with: changes made, rationale, validation evidence.

Required Commands:
- git status --short
- git diff --stat
- [project test command]
- [post-fix scan command]

Final Output:
Return STRICT JSON only:
{
  "status": "done" | "blocked",
  "summary": "technical summary",
  "user_summary": "plain-English summary",
  "assumptions": ["..."],
  "asked_follow_up_questions": false,
  "branch_name": "...",
  "implementation_doc": "docs/agent-implementation-note.md",
  "files_changed": ["..."],
  "tests": {"command": "...", "passed": true, "notes": "..."},
  "scan": {"actionable_before": 0, "actionable_after": 0, "top_remaining": ["..."]},
  "risks": ["..."],
  "follow_up_prs": ["..."]
}
```
