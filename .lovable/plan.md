

# Vibe-to-Production: The Anti-Rewrite Engine MVP
## Full Agent Swarm — Phases, Models & OpenRouter Integration

---

## Architecture

- **Frontend:** React/Vite (Lovable) — Dark Mission Control UI
- **Auth:** GitHub OAuth via Supabase
- **Database:** Supabase (PostgreSQL)
- **Orchestration:** Supabase Edge Functions (TypeScript) — routes requests to the Python microservice
- **Execution Engine:** Python/FastAPI microservice (deployed to Railway/Render) using OpenHands SDK + Daytona SDK
- **Model Access:** All LLM calls routed through **OpenRouter** using your API key — enabling dynamic model switching per agent

---

## The Agent Swarm (Merged Roster — 5 Agents)

| Agent | Role | Model (via OpenRouter) | When Used |
|---|---|---|---|
| **Agent_Visionary** | Product Manager | Gemini 3 Pro (10M context) | Phase 0 — Intake. Ingests repo + user's "vibe prompt" to generate a `project_charter.md` so agents understand intent before auditing |
| **Agent_Scanner** | The Auditor | Gemini 3 Pro | Phase 1 — Deep Scan. Reads entire repo in one pass (2M+ context), runs static analysis, identifies security/architecture/reliability issues |
| **Agent_Planner** | The Architect | Claude 4.5 Opus | Phase 2 — Action Plan. Reviews scan findings, designs safe refactoring strategy, prioritizes missions without breaking business logic |
| **Agent_Builder** | The SRE | DeepSeek V3.2 | Phase 3 — Auto-Fix. Enters Daytona sandbox, writes code fixes, installs packages, writes tests, self-corrects in a loop. 10x cheaper for heavy lifting |
| **Agent_Educator** | The Teacher | Claude 4.5 Sonnet | All Phases — Education Layer. Generates plain-English "Why This Matters" and "The CTO's Perspective" cards for every finding |

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
- **Agent_Scanner** (Gemini 3 Pro) ingests the full file tree + critical files in one massive context pass
- Runs heuristic checks: hardcoded secrets, `.env` in git, missing test folders, circular dependencies, `sk_live` keys
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
- **Agent_Planner** (Claude 4.5 Opus) reviews all Phase 1 findings
- Generates a prioritized mission list:
  - 🔴 Critical: "Move Stripe Secret Key to Env Var"
  - 🟠 High: "Implement Connection Pooling for Supabase"
  - 🟡 Medium: "Add Rate Limiting to API Routes"
- Each mission includes the specific files, the risk, and the recommended approach
- **Agent_Educator** (Claude 4.5 Sonnet) generates a "Why This Matters" and "The CTO's Perspective" card for every item

### Phase 3: The Auto-Fix (Revenue Feature)
- User clicks "Fix This" on any action item
- **Agent_Builder** (DeepSeek V3.2) enters a Daytona sandbox via OpenHands SDK:
  1. Clones the repo into the sandbox
  2. Edits code, installs libraries (e.g., `npm install express-rate-limit`)
  3. Writes a unit test for the fix
  4. Runs the test — if it fails, self-corrects (loop)
  5. On success: creates a PR on the user's GitHub with a detailed description
- Diff preview shown in a code comparison view before committing
- **Token Efficiency:** Uses "Variable Passing" — when Scanner finds a file, it saves it as `$file_context` and passes to subsequent agents instead of re-reading

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
- Real-time streaming: `> Agent_Scanner: Analyzing package.json...`, `> SRE_Agent: Running 'npm test'... Failed. Retrying...`
- Progress stages with time estimates
- Builds trust by visualizing the work

### 5. Production Health Report Dashboard
- **Health Score Gauge** — circular 0-100 (red/yellow/green)
- **Scan Tier Badge** — Surface vs Deep Probe
- **Three Category Sections:** Security 🔴, Reliability 🟡, Scalability 🔵
- **Deep Probe Exclusive Findings** highlighted separately (build failures, crash logs, test results)
- **Action Items** — each card shows:
  - File path + line reference
  - Severity badge (Critical / High / Medium / Low)
  - Source badge: "Static" or "Dynamic"
  - "Why This Matters" educational card (Agent_Educator)
  - "The CTO's Perspective" business risk explanation
  - **"Fix This" button**

### 6. Auto-Fixer Modal
- Diff preview of proposed fix
- Confirm → live terminal showing Agent_Builder executing in Daytona sandbox
- Verification results (tests pass/fail)
- "Create PR" button on success

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
- **action_items** — issues with severity, category, file path, source (static/dynamic), fix status
- **fix_attempts** — execution log with sandbox ID, status, PR URL, agent logs
- **trajectories** — successful fix trajectories (prompt → code → test pass) for future fine-tuning

### Supabase Edge Functions
- **vision-intake** — Calls OpenRouter (Gemini 3 Pro) to run the Visionary agent chat
- **surface-scan** — Calls OpenRouter (Gemini 3 Pro) for static analysis, streams results
- **deep-probe** — Proxies to Python microservice for Daytona dynamic analysis
- **generate-plan** — Calls OpenRouter (Claude 4.5 Opus) for action plan generation
- **generate-education** — Calls OpenRouter (Claude 4.5 Sonnet) for educational cards
- **execute-fix** — Proxies to Python microservice for OpenHands agent fix execution
- **create-pr** — GitHub API to create branch + PR

### Python Microservice (FastAPI — deployed to Railway/Render)
- Endpoints: `/deep-scan`, `/generate-fix`, `/execute-fix`
- Uses `openhands-sdk` (Agent, Conversation, TerminalTool, FileEditorTool)
- Uses `daytona-sdk` for sandbox lifecycle
- All LLM calls go through OpenRouter
- Streams output via SSE

### Required Secrets
- `OPENROUTER_API_KEY` — your key for all model access (Gemini, Claude, DeepSeek)
- `DAYTONA_API_KEY` — for sandbox creation
- `PYTHON_SERVICE_URL` — URL of your deployed FastAPI service
- GitHub OAuth token — from user's auth session

---

## Implementation Order

1. Landing Page — Dark Mission Control hero + CTA
2. GitHub OAuth — Supabase Auth with GitHub provider
3. Database Schema — All tables
4. Vision Intake — Chat interface + Gemini 3 Pro via OpenRouter
5. Surface Scan (Tier 1) — Edge function + OpenRouter (Gemini) + streaming terminal
6. Health Report Dashboard — Score gauge, categories, action items, educational cards
7. Action Plan Generation — Claude 4.5 Opus via OpenRouter
8. Education Layer — Claude 4.5 Sonnet via OpenRouter for "Why This Matters" cards
9. Python Microservice — FastAPI + OpenHands SDK + Daytona (generated code for external deploy)
10. Deep Probe (Tier 2) — Dynamic analysis via Python service
11. Auto-Fixer — Fix generation (DeepSeek V3.2) + execution + verification + PR creation
12. My Projects Dashboard — History, re-scan, trends, trajectory storage

