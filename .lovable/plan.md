

# Deep Probe (Tier 2) — Daytona Sandbox Integration

## Overview

Enable the "Deep Probe" scan tier by creating a new edge function that uses the **Daytona REST API** to spin up a sandbox, clone the user's repo, and run real commands (`npm install`, `npm test`, `npm run build`, `semgrep`). This produces **objective, dynamic analysis** — proving whether the code actually builds, runs, and passes tests — rather than relying solely on static LLM analysis.

The auto-fix phase (OpenHands SDK) is deferred to a later iteration.

---

## What Changes

### 1. New Edge Function: `deep-probe`

A new backend function at `supabase/functions/deep-probe/index.ts` that:

1. **Creates a Daytona sandbox** via `POST https://app.daytona.io/api/sandbox`
2. **Clones the repo** into the sandbox via `POST https://proxy.app.daytona.io/toolbox/{sandboxId}/process/execute` running `git clone <repo_url> /workspace/repo`
3. **Runs a sequence of diagnostic commands**, streaming progress back via SSE:
   - **The Crash Test**: `npm install` (or `pip install -r requirements.txt`) — does the build even start?
   - **The Build Test**: `npm run build` — does it compile?
   - **The Smoke Test**: Run entry point — does the app start without crashing?
   - **The Test Suite**: `npm test` — capture pass/fail counts
   - **Static Tools**: `npx semgrep --config auto` and `npm audit --json` for vulnerability scanning
4. **Collects all stdout/stderr/exit codes** from each step
5. **Cleans up** the sandbox via `DELETE https://app.daytona.io/api/sandbox/{sandboxId}`
6. Returns structured results as SSE stream

Each command result streams as:
```text
data: {"type":"probe_step","step":"npm_install","status":"running","agent":"Agent_SRE"}
data: {"type":"probe_result","step":"npm_install","exit_code":0,"stdout":"...","stderr":"...","duration_ms":12340}
```

### 2. New Secret: `DAYTONA_API_KEY`

Required to authenticate with the Daytona API. You'll be prompted to add this.

### 3. Update `supabase/config.toml`

Add the `deep-probe` function with `verify_jwt = false`.

### 4. Update `src/lib/api.ts`

Add a new `streamDeepProbe()` function that calls the `deep-probe` edge function and parses the SSE stream, similar to the existing `streamSurfaceScan()`.

### 5. Update `src/pages/NewScan.tsx`

- Remove the "Coming soon" label from the Deep Probe tier option
- Enable selecting "deep" tier

### 6. Update `src/pages/ScanLive.tsx`

- When `tier === "deep"`, call `streamDeepProbe()` instead of (or in addition to) `streamSurfaceScan()`
- Show Agent_SRE logs with the orange color for sandbox activity
- Parse `probe_step` and `probe_result` events to show real-time sandbox output
- After the deep probe completes, still run the surface scan + security review to get the full health score
- Save deep probe results (build status, test results, audit findings) to the `scan_reports.report_data` JSON field

### 7. Update `src/pages/Report.tsx`

- Add a "Deep Probe Results" section that shows:
  - Build status (pass/fail with logs)
  - Test suite results (X passed, Y failed)
  - `npm audit` vulnerability count
  - `semgrep` findings
- These appear as a highlighted section separate from the static analysis findings, with a "Dynamic" source badge

---

## Technical Details

### Daytona REST API Flow

```text
1. POST https://app.daytona.io/api/sandbox
   Headers: Authorization: Bearer <DAYTONA_API_KEY>
   Body: { "language": "typescript" }
   Response: { "id": "sandbox-abc123", ... }

2. POST https://proxy.app.daytona.io/toolbox/sandbox-abc123/process/execute
   Headers: Authorization: Bearer <DAYTONA_API_KEY>
   Body: { "command": "git clone https://github.com/user/repo /workspace/repo && cd /workspace/repo && npm install", "timeout": 120 }
   Response: { "exitCode": 0, "result": "..." }

3. (repeat step 2 for each diagnostic command)

4. DELETE https://app.daytona.io/api/sandbox/sandbox-abc123
   Headers: Authorization: Bearer <DAYTONA_API_KEY>
```

### Edge Function SSE Stream Format

The deep-probe edge function streams events in the same SSE format as surface-scan, but with probe-specific event types so the frontend can distinguish between static and dynamic findings.

### GitHub Token Passthrough

For private repos, the edge function receives the user's GitHub token and passes it to the `git clone` command inside the sandbox using a token URL: `git clone https://x-access-token:<token>@github.com/user/repo`.

### Timeout and Cleanup

- Each command has a 120-second timeout
- The sandbox is always deleted in a `finally` block, even if errors occur
- Total deep probe timeout: ~5 minutes

### Implementation Order

1. Add `DAYTONA_API_KEY` secret
2. Create `deep-probe` edge function
3. Update config.toml
4. Add `streamDeepProbe()` to `src/lib/api.ts`
5. Update `NewScan.tsx` — remove "Coming soon"
6. Update `ScanLive.tsx` — handle deep probe flow
7. Update `Report.tsx` — display dynamic analysis results

