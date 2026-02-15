

# Vibe-to-Production: The Anti-Rewrite Engine MVP
## Full Agent Swarm — 6 Agents, Phases & OpenRouter Integration

---

## Architecture

- **Frontend:** React/Vite (Lovable) — Dark Mission Control UI
- **Auth:** GitHub OAuth via Supabase
- **Database:** Supabase (PostgreSQL)
- **Orchestration:** Supabase Edge Functions (TypeScript) — routes requests to the Python microservice
- **Execution Engine:** Python/FastAPI microservice (deployed to Railway/Render) using OpenHands SDK + Daytona SDK
- **Model Access:** All LLM calls routed through **OpenRouter** using your API key — enabling dynamic model switching per agent

---

## The Agent Swarm (6 Agents)

| Agent | Role | Model (via OpenRouter) | OpenRouter Model ID | Key Feature | When Used |
|---|---|---|---|---|---|
| **Agent_Visionary** | Product Manager | Gemini 3 Pro | `google/gemini-2.5-pro` | 10M token context | Phase 0 — Intake. Ingests repo + user's "vibe prompt" to generate `project_charter.md` so agents understand intent before auditing |
| **Agent_Auditor** | The Strategist | Claude 4.5 Opus | `anthropic/claude-opus-4` | 80.9% SWE-bench | Phase 1 — Deep Scan. Reads entire repo, hunts spaghetti code, circular deps, architectural risks. Diagnoses but doesn't fix |
| **Agent_Architect** | The Planner | GPT-5.2 (xhigh/Codex) | `openai/gpt-5.2` | 100% AIME reasoning | Phase 2 — Action Plan. Takes Auditor's report and designs modular refactoring blueprints. Decides exactly which files change |
| **Agent_SRE** | Site Reliability Engineer | DeepSeek V3.2 | `deepseek/deepseek-chat` | $0.28/1M tokens | Phase 3 — Auto-Fix. Executes Architect's plan in Daytona sandbox via OpenHands SDK. Writes code, runs tests, self-corrects in loops |
| **Agent_Security** | The Gatekeeper | DeepSeek V3.2 (Reasoner) | `deepseek/deepseek-reasoner` | Logic/cost ratio | All Phases — Reviews every line the SRE writes. Checks hardcoded secrets, SQL injection, SOC 2 compliance. Has VETO power |
| **Agent_Educator** | The Teacher | Claude 4.5 Sonnet | `anthropic/claude-sonnet-4` | Human-like writing | All Phases — Translates technical findings into "Why This Matters" and "The CTO's Perspective" cards |

---

## Phases (From PRDs)

### Phase 0: The Vision Intake (Onboarding Agent)
- User pastes GitHub repo URL + optional "Vibe Prompt" (the original prompt they used to build the app)
- **Agent_Visionary** (Gemini 3 Pro) asks 3 clarifying questions via chat interface to understand the app's intent
- Generates `project_charter.md` — ensures no agent accidentally deletes core features during refactoring
- UI: Chat interface that feels like talking to a Senior PM

### Phase 1: The Deep Scan (Lead Magnet)
**Two Tiers:**

**Tier 1 — Surface Scan (Static Analysis)**
- **Agent_Auditor** (Claude 4.5 Opus) ingests the full file tree + critical files
- Runs heuristic checks: hardcoded secrets, `.env` in git, missing test folders, circular dependencies, `sk_live` keys
- **Agent_Security** (DeepSeek V3.2 Reasoner) validates findings for false positives
- Cost: ~$0.10-0.20 | Speed: ~15 seconds
- No Daytona needed

**Tier 2 — Deep Probe (Dynamic Analysis via Daytona)**
- Spins up a Daytona sandbox and actually runs the code:
  - **The Crash Test:** Runs `npm install` / `pip install` — flags if build fails
  - **The Smoke Test:** Runs entry point (`node index.js`) — flags if app crashes on startup
  - **The Test Suite Execution:** Runs `npm test` — captures actual pass/fail counts
  - **Static tools:** Runs `semgrep` / `npm audit` in the sandbox
- Output: Objective proof — "I tried to run your app and it crashed" vs "your code looks complex"

**Output:** Production Health Score (0-100) across Security, Scalability, Reliability

### Phase 2: The Action Plan (Architecture)
- **Agent_Architect** (GPT-5.2 xhigh/Codex) reviews all Phase 1 findings
- Generates a prioritized mission list:
  - 🔴 Critical: "Move Stripe Secret Key to Env Var"
  - 🟠 High: "Implement Connection Pooling for Supabase"
  - 🟡 Medium: "Add Rate Limiting to API Routes"
- Each mission includes the specific files, the risk, and the recommended approach
- **Agent_Security** reviews the plan for security implications
- **Agent_Educator** (Claude 4.5 Sonnet) generates a "Why This Matters" and "The CTO's Perspective" card for every item

### Phase 3: The Auto-Fix (Revenue Feature)
- User clicks "Fix This" on any action item
- **Agent_SRE** (DeepSeek V3.2) enters a Daytona sandbox via OpenHands SDK:
  1. Clones the repo into the sandbox
  2. Edits code, installs libraries (e.g., `npm install express-rate-limit`)
  3. Writes a unit test for the fix
  4. Runs the test — if it fails, self-corrects (loop)
- **Agent_Security** (DeepSeek V3.2 Reasoner) reviews every code change before PR:
  - Checks for introduced vulnerabilities, hardcoded secrets, SQL injection
  - Has VETO power — can reject and send back to SRE for correction
  5. On success + security approval: creates a PR on the user's GitHub with a detailed description
- Diff preview shown in a code comparison view before committing
- **Token Efficiency:** Uses "Variable Passing" — when Auditor finds a file, it saves it as `$file_context` and passes to subsequent agents instead of re-reading

---

## Pages & UI

### 1. Landing Page
- Hero: "Is your AI app ready for real users?"
- 3-step visual: Connect → Scan → Fix
- Dark glass-morphism aesthetic, neon accents
- CTA: "Scan Your Repo Free" → GitHub OAuth

### 2. Vision Intake (Chat)
- Chat interface with Agent_Visionary
- 3 clarifying questions about the app's purpose
- Generates project charter before scanning begins

### 3. Scan Configuration
- Repo URL input + Vibe Prompt textarea
- Tier selection: ⚡ Surface Scan vs 🔬 Deep Probe
- "Start Scan" button

### 4. Live Scanning View ("The Thinking Stream")
- Terminal-style log window showing raw agent activity
- Real-time streaming: `> Agent_Auditor: Analyzing package.json...`, `> Agent_SRE: Running 'npm test'... Failed. Retrying...`
- Agent_Security logs shown with 🛡️ prefix
- Progress stages with time estimates
- Builds trust by visualizing the work

### 5. Production Health Report Dashboard
- **Health Score Gauge** — circular 0-100 (red/yellow/green)
- **Scan Tier Badge** — Surface vs Deep Probe
- **Three Category Sections:** Security 🔴, Reliability 🟡, Scalability 🔵
- **Security Officer Verdict** — separate section showing Agent_Security's review
- **Deep Probe Exclusive Findings** highlighted separately (build failures, crash logs, test results)
- **Action Items** — each card shows:
  - File path + line reference
  - Severity badge (Critical / High / Medium / Low)
  - Source badge: "Static" or "Dynamic"
  - Security review status (✅ Approved / ⚠️ Flagged by Security Officer)
  - "Why This Matters" educational card (Agent_Educator)
  - "The CTO's Perspective" business risk explanation
  - **"Fix This" button**

### 6. Auto-Fixer Modal
- Diff preview of proposed fix
- **Security Review Gate** — Agent_Security must approve before PR creation
- Confirm → live terminal showing Agent_SRE executing in Daytona sandbox
- Verification results (tests pass/fail)
- Security scan results (pass/veto)
- "Create PR" button on success + security approval

### 7. My Projects Dashboard
- Previously scanned repos with health scores
- Scan tier indicators
- Re-scan capability with score trends
- Fix history per project

---

## Backend

### Supabase Database
- **profiles** — GitHub user info, avatar, access token
- **projects** — repo URL, project charter, latest health score, scan tier
- **scan_reports** — full structured JSON report, tier, timestamps
- **action_items** — issues with severity, category, file path, source (static/dynamic), fix status, security_status
- **fix_attempts** — execution log with sandbox ID, status, PR URL, agent logs, security_review
- **trajectories** — successful fix trajectories (prompt → code → test pass) for future fine-tuning

### Supabase Edge Functions
- **vision-intake** — Calls OpenRouter (Gemini 3 Pro / `google/gemini-2.5-pro`) to run the Visionary agent chat
- **surface-scan** — Calls OpenRouter (Claude 4.5 Opus / `anthropic/claude-opus-4`) for static analysis, streams results
- **security-review** — Calls OpenRouter (DeepSeek V3.2 Reasoner / `deepseek/deepseek-reasoner`) for security validation
- **generate-plan** — Calls OpenRouter (GPT-5.2 / `openai/gpt-5.2`) for action plan generation
- **generate-education** — Calls OpenRouter (Claude 4.5 Sonnet / `anthropic/claude-sonnet-4`) for educational cards
- **deep-probe** — Proxies to Python microservice for Daytona dynamic analysis
- **execute-fix** — Proxies to Python microservice for OpenHands agent fix execution (DeepSeek V3.2)
- **create-pr** — GitHub API to create branch + PR

### Python Microservice (FastAPI — deployed to Railway/Render)
- Endpoints: `/deep-scan`, `/generate-fix`, `/execute-fix`
- Uses `openhands-sdk` (Agent, Conversation, TerminalTool, FileEditorTool)
- Uses `daytona-sdk` for sandbox lifecycle
- All LLM calls go through OpenRouter
- Streams output via SSE

### Required Secrets
- `OPENROUTER_API_KEY` — your key for all model access (Gemini, Claude, GPT, DeepSeek)
- `DAYTONA_API_KEY` — for sandbox creation
- `PYTHON_SERVICE_URL` — URL of your deployed FastAPI service
- GitHub OAuth token — from user's auth session

---

## Implementation Order

1. ✅ Landing Page — Dark Mission Control hero + CTA
2. ✅ GitHub OAuth — Supabase Auth with GitHub provider
3. ✅ Database Schema — All tables
4. ✅ Edge Functions — surface-scan, vision-intake, generate-plan, generate-education
5. ✅ Scan Flow — NewScan → ScanLive with Thinking Stream
6. Security Review — Agent_Security edge function with VETO power
7. Vision Intake — Chat interface + Gemini 3 Pro via OpenRouter
8. Health Report Dashboard — Score gauge, categories, action items, security verdict
9. Action Plan Generation — GPT-5.2 via OpenRouter
10. Education Layer — Claude 4.5 Sonnet via OpenRouter for "Why This Matters" cards
11. Python Microservice — FastAPI + OpenHands SDK + Daytona (generated code for external deploy)
12. Deep Probe (Tier 2) — Dynamic analysis via Python service
13. Auto-Fixer — Fix generation (DeepSeek V3.2) + security review + execution + verification + PR creation
14. My Projects Dashboard — History, re-scan, trends, trajectory storage
