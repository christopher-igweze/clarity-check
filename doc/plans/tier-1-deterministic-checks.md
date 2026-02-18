# Tier 1 Deterministic Scanner: Balanced 15 Checks

Date: 2026-02-16  
Status: Locked baseline for Tier 1 implementation

## Output Contract (per check result)

```json
{
  "check_id": "SEC_001",
  "status": "pass|warn|fail",
  "category": "security|reliability|scalability",
  "severity": "critical|high|medium|low",
  "engine": "index|ast|linter|regex|hybrid",
  "confidence": 0.0,
  "title": "string",
  "description": "string",
  "evidence": [
    {
      "file_path": "string",
      "line_number": 0,
      "snippet": "string",
      "match": "string"
    }
  ],
  "suggested_fix_stub": "string"
}
```

## Deterministic Engine Stack (Locked)

1. Repo Tree/Index engine  
Uses `git ls-files` + ignore filters to create the file set and metadata index (`language`, `loc`, `sha256`, path class, framework hints).

2. AST engine  
Uses `tree-sitter` for supported languages (JS/TS/Python first) to detect structural patterns (routes, guards, risky calls). Falls back to deterministic regex when parsing fails.

3. Linter/Audit engine (best effort)  
Consumes deterministic tool signals if available in runtime image (example: `eslint`, `ruff`/`pylint`, `bandit`, `semgrep`) under strict timeout. Tier 1 does not install dependencies just to run a tool.

## Indexing Flow (How Indexing Happens)

1. Resolve snapshot identity (`repo_sha`) from git HEAD.
2. Build file manifest from tracked source files only.
3. Compute per-file metadata (`sha256`, `loc`, extension/language, path role).
4. Parse supported files into AST facts (imports, route markers, sink calls, auth/rate-limit hints).
5. Store index as a reusable cache keyed by `project_id + repo_sha` with `expires_at = now + 30 days`.
6. On next run:
   - same `repo_sha`: reuse index directly
   - new `repo_sha`: rebuild only changed files and refresh aggregate facts
7. Scanner runs checks over index facts + AST facts + best-effort linter findings.

## Design Rules

- All checks are deterministic; no LLM in scanner.
- No install/build/test in Tier 1 scanner path.
- Each check declares primary engine and fallback engine.
- False-positive prone checks emit `warn` unless high-confidence evidence exists.
- Findings must include file-level evidence where possible.

## 15-Check Engine Map

| Check | Title | Primary Engine | Fallback Engine | Category | Default Severity |
|---|---|---|---|---|---|
| `SEC_001` | Hardcoded API keys/secrets | `regex` | `linter` | security | critical |
| `SEC_002` | Private key material committed | `regex` | `index` | security | critical |
| `SEC_003` | Secret-bearing env files committed | `index` | `regex` | security | high |
| `SEC_004` | Insecure CORS configuration | `ast` | `regex` | security | high |
| `SEC_005` | Dangerous dynamic execution patterns | `ast` | `regex` | security | high |
| `SEC_006` | SQL injection-risk query construction | `ast` | `regex` | security | high |
| `SEC_007` | Missing auth guard hints on API routes | `ast` | `index` | security | medium |
| `REL_001` | Missing automated tests | `index` | `regex` | reliability | high |
| `REL_002` | Missing CI workflow | `index` | none | reliability | medium |
| `REL_003` | Missing lockfile for dependency reproducibility | `index` | none | reliability | medium |
| `REL_004` | Env vars used but no `.env.example` | `hybrid` (`ast+index`) | `regex` | reliability | medium |
| `REL_005` | Weak error/logging hygiene in backend paths | `hybrid` (`ast+linter`) | `regex` | reliability | low |
| `SCL_001` | God file size threshold exceeded | `index` | none | scalability | medium/high |
| `SCL_002` | Blocking sync operations in request paths | `ast` | `regex` | scalability | medium |
| `SCL_003` | Missing rate limiting hints on exposed APIs | `ast` | `index` | scalability | medium |

## Check Details

1. `SEC_001` Hardcoded API keys/secrets  
Detection: known token regexes (`sk_live_`, `AKIA`, `xoxb-`, `ghp_`) and assignment patterns in source/config.  
Engine: `regex` primary, `linter` secondary.

2. `SEC_002` Private key material committed  
Detection: PEM markers (`BEGIN PRIVATE KEY`, `BEGIN RSA PRIVATE KEY`).  
Engine: `regex` primary, `index` secondary.

3. `SEC_003` Secret-bearing env files committed  
Detection: tracked `.env*` files excluding template files (for example `.env.example`).  
Engine: `index` primary, `regex` secondary.

4. `SEC_004` Insecure CORS configuration  
Detection: wildcard origin + credentials enabled in same config path.  
Engine: `ast` primary, `regex` secondary.

5. `SEC_005` Dangerous dynamic execution patterns  
Detection: calls like `eval`, `new Function`, `child_process.exec`, `pickle.loads` on untrusted paths.  
Engine: `ast` primary, `regex` secondary.

6. `SEC_006` SQL injection-risk query construction  
Detection: SQL statements constructed via string concat/interpolation near query APIs.  
Engine: `ast` primary, `regex` secondary.

7. `SEC_007` Missing auth guard hints on API routes  
Detection: route handlers present without auth middleware/guard markers in chain/module.  
Engine: `ast` primary, `index` secondary.

8. `REL_001` Missing automated tests  
Detection: no test folders/files/patterns (`test`, `spec`, `__tests__`, `pytest`).  
Engine: `index` primary, `regex` secondary.

9. `REL_002` Missing CI workflow  
Detection: no CI config (for example `.github/workflows/*`).  
Engine: `index` only.

10. `REL_003` Missing lockfile for dependency reproducibility  
Detection: manifest exists without lockfile (`package.json` without lockfile, etc.).  
Engine: `index` only.

11. `REL_004` Env vars used but no `.env.example`  
Detection: env access API patterns + missing template env file.  
Engine: `hybrid` (`ast+index`) primary, `regex` secondary.

12. `REL_005` Weak error/logging hygiene in backend paths  
Detection: excessive ad-hoc logging patterns and weak exception handling in server modules.  
Engine: `hybrid` (`ast+linter`) primary, `regex` secondary.

13. `SCL_001` God file size threshold exceeded  
Detection: file LOC > 500 (`warn`), > 800 (`fail/high`).  
Engine: `index` only.

14. `SCL_002` Blocking sync operations in request paths  
Detection: blocking/sync APIs in request handlers (`fs.*Sync`, blocking subprocess usage).  
Engine: `ast` primary, `regex` secondary.

15. `SCL_003` Missing rate limiting hints on exposed APIs  
Detection: API routes exist but no rate-limit middleware markers.  
Engine: `ast` primary, `index` secondary.

## Severity Escalation Rules

- Escalate one level when:
  - evidence appears in production config/runtime paths
  - the same check triggers in 3+ distinct files
  - security check intersects with sensitive data flag from onboarding

## Implementation Notes

- Keep each check as an isolated module: `check_id`, detector, formatter.
- Each check returns deterministic evidence and a short fix stub.
- Hermes Assistant consumes only this normalized output in Tier 1.
