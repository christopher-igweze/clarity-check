# Technical PRD: The "Vibe-to-Production" Engine

**Version:** 2.1 (OpenHands-First Architecture)
**Date:** February 2026
**Strategic Goal:** Build the "Anti-Rewrite Engine" — a platform that takes fragile AI-generated MVPs (from Lovable/Bolt) and automates their transition to production-grade reliability using a swarm of specialized AI agents orchestrated by OpenHands.

---

## 1. Executive Summary & Core Philosophy

### The Problem
"Vibe coding" tools (Lovable, Bolt, v0) create functional but fragile prototypes — spaghetti code, hardcoded secrets, no tests, no observability. Founders hit a "Technical Ceiling" where they must rewrite from scratch to scale. Unchecked AI code contains 1.57x more security vulnerabilities than human-written code.

### The Solution
An **OpenHands-orchestrated multi-agent system** that deeply audits, diagnoses, and fortifies existing codebases. Agents don't just read code — they **run it, test it, break it, and understand it** inside real sandboxed environments. This is the "fractional SRE" for the millions of non-technical founders building with AI.

### The "Vibe"
"Mission Control for your Code." Dark mode, high-fidelity data visualization, real-time terminal logs (Matrix-style but readable), and "medical-grade" diagnostic dashboards. The user should feel like they're watching a team of senior engineers inspect their app in real-time.

### Monetization Split
| Tier | What the User Gets | Cost |
|------|-------------------|------|
| **Free (Lead Magnet)** | Full deep audit + diagnosis + step-by-step remediation plan with detailed solutions | Free |
| **Paid (Revenue)** | Auto-Fix — agents actually implement the solutions, run verification tests, and push PRs | $149/refactor |

---

## 2. Core Architectural Principle: OpenHands-First

> **CRITICAL**: Every agent interaction runs through OpenHands. This is NOT an "LLM-as-a-service" platform where we stuff code into prompts and call model APIs. This is an **agentic system** where AI agents have real terminal access, can execute commands, inspect running processes, and operate inside isolated environments.

### What This Means Concretely
- Agents **clone repos** and navigate the filesystem
- Agents **run code** — `npm install`, `npm run build`, `npm test`, `npm audit`
- Agents **inspect outputs** — read error logs, check exit codes, analyze stack traces
- Agents **test features** — spin up dev servers, hit endpoints, verify functionality
- Agents **understand visuals** — screenshot UIs, check for broken layouts, verify responsive design
- Agents **self-correct** — when a test fails, they read the error, adjust, and retry

### What This Replaces
The current Supabase Edge Functions that make OpenRouter API calls with repo content in prompts are **throwaway code**. They will be entirely replaced by the Python/FastAPI backend described below.

---

## 3. Technical Stack

### Frontend (Existing — Keep)
- **Framework:** Next.js 15 (App Router) / React 18 + Vite (current Lovable build)
- **Styling:** Tailwind CSS + Shadcn/UI
- **Icons:** Lucide React
- **Charts:** Recharts
- **Animations:** Framer Motion
- **State:** React Query (TanStack)

### Backend (NEW — Must Be Built)
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Agent Runtime:** OpenHands SDK (`openhands-ai`)
- **Sandbox:** Docker containers managed via Daytona SDK + Docker SDK for Python
- **Model Routing:** OpenRouter API (dynamic model switching per agent role)

### Database (Existing — Keep & Extend)
- **Provider:** Supabase (PostgreSQL)
- **Extensions:** pgvector (for semantic code search, future)
- **Schema:** Existing tables (profiles, projects, scan_reports, action_items, fix_attempts, trajectories) remain valid

### Infrastructure
- **Agent Containers:** Ephemeral Docker containers via Daytona
- **Networking:** Whitelisted outbound (npm registry, pip, GitHub) — block unknown IPs
- **Secrets:** Environment variables only — never in code or container images

---

## 4. The Agent "Swarm" Architecture

### Hybrid Model Strategy
Based on 2026 benchmarks (OpenHands Index & SWE-bench Verified), each agent uses the optimal model for its specific task.

| Role | Agent Name | Model | Rationale |
|------|-----------|-------|-----------|
| **The Auditor** | `Agent_Scanner` | Gemini 3 Pro | 2M+ token context window — can ingest an entire repo at once to find circular dependencies, architectural flaws, and systemic issues |
| **The Architect** | `Agent_Planner` | Claude 4.5 Opus | 80.9% on SWE-bench Verified — the "careful brain" needed to plan safe refactors without breaking business logic |
| **The SRE** | `Agent_Builder` | DeepSeek V3.2 | Highly capable at coding/terminal tasks, 10x cheaper ($0.28/1M tokens) — handles heavy lifting: running tests, executing builds, inspecting infrastructure |
| **The Gatekeeper** | `Agent_Security` | DeepSeek V3.2 | Cost-efficient reasoning for OWASP/SOC 2 scanning, vulnerability validation, false positive elimination |
| **The Teacher** | `Agent_Educator` | Claude 4.5 Sonnet | Best at producing human-readable, empathetic documentation to explain technical concepts to non-technical founders |

### How Agents Collaborate (Orchestration Flow)

All agents run as OpenHands agent instances inside Docker containers. They share context through a structured data pipeline — NOT by passing raw file content back and forth in chat history.

```
User submits GitHub URL
        │
        ▼
┌─────────────────────────────────────────────────┐
│  ORCHESTRATOR (Python/FastAPI)                   │
│  Manages agent lifecycle, context passing,       │
│  sandbox provisioning, result aggregation        │
└──────────┬──────────────────────────────────────┘
           │
           ▼
┌──────────────────────┐
│  1. SANDBOX SETUP    │  Daytona spins up Docker container
│     Clone repo       │  git clone <url> /workspace/repo
│     Install deps     │  npm install / pip install
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  2. Agent_Scanner     │  THE AUDITOR (Gemini 3 Pro)
│  (Deep Scan)         │
│  - Reads entire repo │  Ingests full file tree + content
│  - Runs static tools │  semgrep, npm audit, eslint
│  - Maps architecture │  Dependency graph, circular refs
│  - Identifies issues │  Secrets, missing tests, dead code
│  OUTPUT: findings[]  │  Structured JSON → saved to DB
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  3. Agent_Builder     │  THE SRE (DeepSeek V3.2)
│  (Dynamic Probe)     │
│  - Runs the app      │  npm run dev / npm start
│  - Executes tests    │  npm test (captures pass/fail)
│  - Attempts build    │  npm run build (captures errors)
│  - Stress tests      │  Hit endpoints, check responses
│  - Screenshots UI    │  Headless browser → visual check
│  OUTPUT: probe_results[] │  Build status, test results, screenshots
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  4. Agent_Security    │  THE GATEKEEPER (DeepSeek V3.2)
│  (Security Audit)    │
│  - Validates Scanner │  Confirms/rejects Scanner findings
│     findings         │  Eliminates false positives
│  - Deep sec analysis │  OWASP Top 10, auth bypass, XSS, CSRF
│  - Checks deps      │  Known CVEs, outdated packages
│  OUTPUT: security_review │  Validated findings + confidence scores
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  5. Agent_Planner     │  THE ARCHITECT (Claude 4.5 Opus)
│  (Action Plan)       │
│  - Reviews all       │  Scanner + SRE + Security findings
│     findings         │
│  - Prioritizes       │  Critical → High → Medium → Low
│  - Plans remediation │  Step-by-step fix instructions
│  - Estimates effort  │  Quick / Moderate / Significant
│  OUTPUT: action_plan[] │  Prioritized missions with solutions
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  6. Agent_Educator    │  THE TEACHER (Claude 4.5 Sonnet)
│  (Education Layer)   │
│  - "Why This Matters"│  Developer-focused explanation
│  - "CTO Perspective" │  Business risk / revenue impact
│  OUTPUT: education[] │  Human-readable cards per finding
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  REPORT ASSEMBLED    │  Health Score (0-100)
│  Sent to Frontend    │  Category scores + findings + education
└──────────────────────┘
```

### Phase 2 (Paid): The Auto-Fix Loop
```
User clicks "Fix This" on an action item
        │
        ▼
┌──────────────────────┐
│  Agent_Builder (SRE)  │  DeepSeek V3.2 in sandbox
│  1. Read fix plan    │  From Agent_Planner output
│  2. Edit code        │  Apply the fix
│  3. Run tests        │  npm test
│  4. If fail → retry  │  Self-correct loop (max 3 attempts)
│  5. If pass → diff   │  Generate PR description
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Agent_Security       │  Validates the fix didn't
│  (Review Gate)       │  introduce new vulnerabilities
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Push PR to GitHub   │  With detailed description
│  Save trajectory     │  For future fine-tuning
└──────────────────────┘
```

---

## 5. Python Backend Architecture (FastAPI)

### Directory Structure
```
backend/
├── main.py                     # FastAPI app entry point
├── config.py                   # Environment variables, model configs
├── requirements.txt
├── Dockerfile
│
├── api/
│   ├── routes/
│   │   ├── audit.py            # POST /api/audit — start full audit
│   │   ├── fix.py              # POST /api/fix — trigger auto-fix (paid)
│   │   ├── status.py           # GET /api/status/{scan_id} — SSE stream
│   │   └── webhook.py          # GitHub webhook handlers
│   └── middleware/
│       ├── auth.py             # Supabase JWT verification
│       └── rate_limit.py       # Request throttling
│
├── agents/
│   ├── orchestrator.py         # Master orchestrator — manages agent lifecycle
│   ├── base_agent.py           # Base OpenHands agent wrapper
│   ├── scanner.py              # Agent_Scanner (Gemini 3 Pro)
│   ├── builder.py              # Agent_Builder / SRE (DeepSeek V3.2)
│   ├── security.py             # Agent_Security (DeepSeek V3.2)
│   ├── planner.py              # Agent_Planner (Claude 4.5 Opus)
│   └── educator.py             # Agent_Educator (Claude 4.5 Sonnet)
│
├── sandbox/
│   ├── manager.py              # Daytona/Docker container lifecycle
│   ├── executor.py             # Command execution in sandbox
│   └── network_policy.py       # Whitelist/blacklist rules
│
├── models/
│   ├── scan.py                 # Pydantic models for scan data
│   ├── findings.py             # Finding, ActionItem, etc.
│   └── agent_log.py            # Agent log entry models
│
└── services/
    ├── github.py               # GitHub API client (clone, PR, etc.)
    ├── openrouter.py           # OpenRouter model routing
    ├── supabase.py             # Supabase DB client
    └── context_store.py        # Shared context between agents (variable passing)
```

### Key Design Decisions

#### 5.1 Token Efficiency: "Variable Passing"
**Problem:** Agents waste tokens re-reading the same file content.
**Solution:** Implement a shared context store.

```python
# context_store.py — agents read/write shared variables
class ContextStore:
    """
    When Agent_Scanner reads a file, it saves it as a variable.
    Agent_Planner receives the variable reference, NOT the full text
    re-streamed through chat history.
    """
    def set(self, key: str, value: Any) -> None: ...
    def get(self, key: str) -> Any: ...

    # Example usage in orchestrator:
    # scanner finds auth.js has issues
    # store.set("file:auth.js", file_content)
    # store.set("findings:security", scanner_findings)
    # planner receives: store.get("findings:security") — NOT raw file text
```

#### 5.2 Sandbox Management
Every audit session gets its own isolated Docker container:

- **Provisioning:** Daytona SDK creates container with Node.js/Python runtimes
- **Repo Clone:** `git clone` into `/workspace/repo`
- **Network Policy:** Whitelist npm registry, PyPI, GitHub — block everything else
- **Lifecycle:** Container destroyed after audit completes (or 30-min timeout)
- **Resource Limits:** CPU/memory caps to prevent abuse

#### 5.3 MCP (Model Context Protocol) Integration
Agents use MCP to interact with tools instead of raw command strings:

- `search_codebase(query)` — semantic search across repo files
- `read_file(path)` — read a specific file
- `run_command(cmd)` — execute a shell command in sandbox
- `screenshot(url)` — capture UI screenshot via headless browser
- `list_dependencies()` — parse package.json/requirements.txt

This reduces hallucination — the LLM calls a well-defined tool instead of guessing `grep` syntax.

#### 5.4 Streaming Architecture
The frontend receives real-time updates via Server-Sent Events (SSE):

```
GET /api/status/{scan_id}

Event types:
- agent_start    { agent: "Scanner", model: "gemini-3-pro", status: "running" }
- agent_log      { agent: "SRE", message: "Running npm test...", level: "info" }
- finding        { category: "security", severity: "critical", title: "..." }
- probe_result   { test: "build", passed: true, duration_ms: 4500 }
- agent_complete { agent: "Scanner", findings_count: 12 }
- scan_complete  { health_score: 42, report_id: "uuid" }
```

---

## 6. The Deep Audit Process (What Each Agent Actually Does)

### Agent_Scanner (The Auditor) — Gemini 3 Pro

This is not a superficial scan. The agent:

1. **Ingests the entire repository** using Gemini 3 Pro's 2M+ token context window
2. **Maps the architecture** — identifies entry points, routing, database calls, auth flows
3. **Runs static analysis tools** inside the sandbox:
   - `semgrep` — pattern-based vulnerability detection
   - `npm audit` / `pip audit` — dependency vulnerabilities
   - `eslint` with security plugins — code quality issues
4. **Detects structural problems:**
   - Circular dependencies
   - God files (>500 lines doing too much)
   - Missing error boundaries
   - Hardcoded configuration values
   - Missing environment variable usage
   - No logging/observability
   - No test files at all
5. **Outputs:** Structured findings with file paths, line numbers, severity, and category

### Agent_Builder (The SRE) — DeepSeek V3.2

This agent **runs the application** to verify what actually works:

1. **Install dependencies** — `npm install` — does it even install cleanly?
2. **Build the project** — `npm run build` — does it compile without errors?
3. **Run existing tests** — `npm test` — what's the pass rate?
4. **Start the dev server** — `npm run dev` — does it boot?
5. **Hit endpoints** — curl API routes, check response codes
6. **Screenshot the UI** — headless browser captures for visual inspection
7. **Check for runtime errors** — monitor console output during startup
8. **Audit dependencies** — `npm audit --json` — known CVEs in dependency tree
9. **Outputs:** Objective proof — build status, test results, screenshots, error logs

### Agent_Security (The Gatekeeper) — DeepSeek V3.2

Validates and deepens the Scanner's findings:

1. **Confirm or reject** each Scanner finding (eliminate false positives)
2. **OWASP Top 10 analysis** — SQL injection, XSS, CSRF, auth bypass, SSRF
3. **Secrets detection** — hardcoded API keys, `sk_live_`, database credentials
4. **Auth flow review** — are routes properly protected? Is JWT validation correct?
5. **Dependency risk** — are any deps abandoned, compromised, or have known exploits?
6. **Outputs:** Validated findings with confidence scores (0-100)

### Agent_Planner (The Architect) — Claude 4.5 Opus

The strategic brain that turns findings into an actionable plan:

1. **Reviews all findings** from Scanner + SRE + Security
2. **Prioritizes by business impact:**
   - **Critical:** "Your Stripe key is hardcoded — you'll lose money"
   - **High:** "No connection pooling — app will crash at 50 concurrent users"
   - **Medium:** "No rate limiting — vulnerable to abuse"
   - **Low:** "Console.log statements in production code"
3. **Generates step-by-step remediation plans** for each issue:
   - What to change
   - Which files to modify
   - What the fix looks like (code snippets)
   - How to verify the fix works
4. **Estimates effort:** Quick (< 5 min) / Moderate (15-30 min) / Significant (1+ hour)
5. **Identifies dependencies** between fixes (e.g., "fix auth before adding rate limiting")

### Agent_Educator (The Teacher) — Claude 4.5 Sonnet

Makes the technical findings accessible to non-technical founders:

1. **"Why This Matters"** — 2-3 sentence developer explanation for each finding
2. **"The CTO's Perspective"** — Business risk framing:
   - Revenue impact ("This could cost you $50K in fines")
   - User trust ("Users will leave if their data leaks")
   - Velocity impact ("This tech debt will slow you down 3x")
3. **Tone:** Empathetic, not condescending. Explains *why*, not just *what*.

---

## 7. Key Functional Features

### Phase 1: The Deep Audit (Free — Lead Magnet)

**Input:**
- GitHub Repo URL (public or private via OAuth)
- Optional "Vibe Prompt" — the original prompt used to generate the code
- Optional Vision Intake — 3-question interview to understand the founder's intent

**Process (3-5 minutes):**
1. Sandbox provisioned (Daytona Docker container)
2. Repo cloned into sandbox
3. Agent_Scanner performs deep static analysis
4. Agent_Builder performs dynamic analysis (build, test, run)
5. Agent_Security validates and deepens findings
6. Agent_Planner creates prioritized remediation plan
7. Agent_Educator generates human-readable explanations
8. All results aggregated into report

**Output: "Production Health Report"**
- **Health Score:** 0-100 (composite of Security + Reliability + Scalability)
- **Category Scores:** Individual scores for each dimension
- **Findings:** Categorized, prioritized issues with:
  - Severity (Critical / High / Medium / Low)
  - Source (Static analysis / Dynamic proof)
  - File path + line number
  - Step-by-step fix instructions
  - "Why This Matters" education card
  - "CTO's Perspective" business risk card
- **Dynamic Proof:** Build status, test results, screenshots, runtime errors

### Phase 2: The Auto-Fix (Paid — Revenue Feature)

**Input:** User clicks "Fix This" on any action item from the report.

**Process:**
1. Agent_Builder (SRE) enters the sandbox
2. Reads the Planner's step-by-step fix instructions
3. Edits the code to implement the fix
4. Runs tests to verify the fix works
5. If tests fail → self-corrects (up to 3 retries)
6. Agent_Security reviews the diff for new vulnerabilities
7. If approved → generates PR with detailed description
8. Pushes PR to user's GitHub

**Output:**
- Code diff (before/after comparison view in UI)
- PR on user's GitHub repo
- Test verification results
- Trajectory saved for future fine-tuning

---

## 8. UI/UX Guidelines

### The "Mission Control" Aesthetic
- Dark mode, glass-morphism surfaces
- Neon accent colors: green (pass), red (critical), amber (warning), cyan (info)
- Terminal-style monospace fonts for agent logs
- Medical-grade diagnostic feel — gauges, vitals, status indicators

### Live "Thinking" Stream
**No spinners.** Show the raw logs of what each agent is doing in real-time:

```
> Agent_Scanner: Cloning repository...
> Agent_Scanner: Analyzing 147 files across 23 directories...
> Agent_Scanner: FOUND — Hardcoded API key in src/lib/api.ts:42
> Agent_SRE: Running 'npm install'... completed (14.2s)
> Agent_SRE: Running 'npm run build'... FAILED (exit code 1)
> Agent_SRE: Build error: Cannot find module '@/lib/auth'
> Agent_Security: Validating 12 findings... 2 false positives removed
> Agent_Planner: Generating remediation plan for 10 confirmed issues...
> Agent_Educator: Creating education cards...
```

This visualizes the work and builds trust. Users see a team of agents working, not a loading bar.

### Educational Cards
Every finding has an expandable "Why?" card:
- **Developer view:** Technical explanation of the issue
- **CTO view:** Business impact framing (revenue, compliance, velocity)
- Generated by Agent_Educator (Claude 4.5 Sonnet)

### The Report Dashboard
- **Left:** Navigation sidebar
- **Center:** Health Score gauge (circular progress, 0-100)
- **Below:** Action Items grouped by Security / Reliability / Scalability
- **Click item:** Slide-out panel with file path, code context, fix plan, education card
- **Right panel (during scan):** Live terminal showing agent activity

---

## 9. Critical Technical Constraints

### 9.1 Token Efficiency ("Variable Passing")
- When Agent_Scanner reads a file, save it as `$file_context` in the shared context store
- Pass `$file_context` reference to downstream agents — do NOT re-stream raw file content through chat history
- Use Prompt Caching where supported to reduce input token costs by ~90%

### 9.2 Sandbox Safety
- Every audit session gets an isolated Docker container
- Network whitelisting: allow npm, pip, GitHub — block everything else
- Resource limits: CPU/memory caps per container
- Auto-destroy after completion or 30-minute timeout
- No persistent storage between sessions

### 9.3 MCP Tool Integration
- Expose standardized MCP tools (`search_codebase`, `read_file`, `run_command`, `screenshot`)
- Agents call tools via MCP protocol instead of generating raw shell commands
- Reduces hallucination and increases reliability

### 9.4 Error Handling & Retries
- Agent failures: retry up to 3 times with exponential backoff
- Sandbox failures: provision new container and resume
- Model API failures: fall back to alternative model (e.g., Claude Opus → GPT-5.2)
- All errors logged to `agent_logs` for debugging

---

## 10. Success Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Audit completion rate | > 95% | Agents must reliably produce reports |
| Time to report | < 5 minutes | Users won't wait longer |
| Finding accuracy | > 85% (validated by Security agent) | False positives erode trust |
| "Fix All" click rate | > 30% of free users | Conversion to paid |
| Time on education cards | > 45 seconds avg | Proves the "Teacher" agent adds value |
| Auto-fix success rate | > 70% first attempt | Must work reliably to charge for it |

---

## 11. Unit Economics

| Item | Cost |
|------|------|
| Cost per deep audit | ~$1.25 (DeepSeek/Gemini for heavy lifting, Opus only for planning) |
| Revenue per auto-fix | $149 |
| Gross margin | ~95% |
| Model: Free audit (lead gen) → Paid fix (revenue) | |

---

## 12. Self-Improvement Loop (Future)

### Trajectory Storage
Every successful Auto-Fix saves:
- The original finding (prompt)
- The code changes (diff)
- The test results (pass/fail)
- Into the `trajectories` table

### Fine-Tuning Pipeline
Use accumulated trajectory data to fine-tune smaller models (Llama 3 / Mistral) to handle common fix patterns, reducing reliance on expensive Claude Opus calls over time.

---

## 13. Implementation Priority

### Phase 1: Python Backend + OpenHands Orchestration (FOUNDATION)
1. Set up FastAPI project structure
2. Implement OpenHands SDK integration for agent management
3. Build Daytona sandbox manager (provision, execute, destroy)
4. Create shared context store (variable passing between agents)
5. Implement Agent_Scanner (Gemini 3 Pro) with real terminal access
6. Implement Agent_Builder (DeepSeek V3.2) for dynamic probing
7. Implement Agent_Security (DeepSeek V3.2) for validation
8. Implement Agent_Planner (Claude 4.5 Opus) for remediation planning
9. Implement Agent_Educator (Claude 4.5 Sonnet) for education generation
10. Wire up SSE streaming from backend to frontend

### Phase 2: Frontend Integration
11. Replace current Supabase Edge Function calls with Python backend API calls
12. Update ScanLive page to consume new SSE event format
13. Update Report page to display richer findings (dynamic proof, screenshots)

### Phase 3: Auto-Fix (Revenue)
14. Implement fix execution loop in Agent_Builder
15. Add security review gate before PR
16. GitHub PR creation flow
17. Stripe integration for payment
18. Trajectory storage for fine-tuning

### Phase 4: Production Hardening
19. Rate limiting and abuse prevention
20. Monitoring and alerting
21. Error recovery and graceful degradation
22. Performance optimization (caching, connection pooling)

---

## Appendix A: Current Codebase Status

### What Exists (Frontend — Keep)
- React/TypeScript frontend with full UI: landing page, dashboard, scan pages, report view
- Supabase auth (Google OAuth + GitHub OAuth)
- Database schema with 6 tables and RLS policies
- UI components: terminal log viewer, health gauge, scan sequence animation

### What Exists (Backend — Replace)
- 7 Supabase Edge Functions (Deno/TypeScript) making direct LLM API calls
- These are **throwaway** — they will be replaced by the Python/FastAPI backend
- They serve as a working prototype but do not match the architectural vision

### What Must Be Built
- The entire Python/FastAPI backend
- OpenHands SDK integration
- Daytona sandbox orchestration
- Agent implementations with real terminal access
- Context store for token efficiency
- MCP tool integration
- SSE streaming from Python backend to React frontend
