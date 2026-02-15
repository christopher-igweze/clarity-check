# Clarity Check

AI-powered code audit platform that takes fragile AI-generated MVPs and produces production-grade remediation reports. Five specialised agents (Scanner, Builder, Security, Planner, Educator) analyse a GitHub repository inside real sandboxed environments and deliver a prioritised action plan with real-time streaming.

## Tech Stack

### Frontend

| Layer | Technology |
|-------|-----------|
| Build | Vite 5 |
| UI | React 18 + TypeScript |
| Components | shadcn/ui (Radix primitives) |
| Styling | Tailwind CSS |
| Icons | Lucide React |
| Charts | Recharts |
| Animations | Framer Motion |
| State | TanStack React Query |
| Routing | React Router v6 |
| Auth | Supabase (Google + GitHub OAuth) |

### Backend

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Agent Runtime | OpenHands SDK |
| Sandbox | Daytona (ephemeral Docker containers) |
| Model Routing | OpenRouter (Gemini, DeepSeek, Claude) |
| Auth | Supabase JWT verification |
| Streaming | Server-Sent Events (SSE) |

### Database

| Layer | Technology |
|-------|-----------|
| Provider | Supabase (PostgreSQL) |
| Future | pgvector for semantic code search |

## Project Structure

```
clarity-check/
├── src/                        # React frontend (Vite)
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── lib/
│   └── ...
├── backend/                    # Python/FastAPI backend
│   ├── main.py                 # App entry point
│   ├── config.py               # Environment config
│   ├── agents/                 # OpenHands agent implementations
│   │   ├── orchestrator.py     # Agent lifecycle + report assembly
│   │   ├── scanner.py          # Static analysis (Gemini)
│   │   ├── builder.py          # Dynamic probing (DeepSeek)
│   │   ├── security.py         # Vulnerability validation (DeepSeek)
│   │   ├── planner.py          # Remediation planning (Claude Opus)
│   │   └── educator.py         # Education cards (Claude Sonnet)
│   ├── api/                    # Routes + middleware
│   ├── models/                 # Pydantic models
│   ├── sandbox/                # Daytona sandbox manager
│   └── services/               # GitHub, Supabase, OpenRouter clients
├── supabase/                   # Migrations + edge functions (legacy)
├── docker-compose.yml
└── PRD.md                      # Technical product requirements
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+ and pip
- Docker (for backend sandbox features)

### Frontend

```sh
git clone <YOUR_GIT_URL>
cd clarity-check
npm install
npm run dev            # http://localhost:5173
```

### Backend

```sh
cd backend
cp .env.example .env   # fill in API keys
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker (full stack)

```sh
docker compose up
```

## How It Works

1. User submits a GitHub repo URL
2. An ephemeral sandbox is provisioned (Daytona)
3. **Agent_Scanner** (Gemini) ingests the repo and runs static analysis
4. **Agent_Builder** (DeepSeek) runs the app — build, test, startup, endpoints
5. **Agent_Security** (DeepSeek) validates findings, eliminates false positives
6. **Agent_Planner** (Claude Opus) creates a prioritised remediation plan
7. **Agent_Educator** (Claude Sonnet) generates human-readable explanations
8. A **Production Health Report** (0-100 score) is streamed to the frontend via SSE

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Vite dev server |
| `npm run build` | Production build |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
| `npm run test` | Run Vitest |

## Environment Variables

See `backend/.env.example` for the full list. Key variables:

- `OPENROUTER_API_KEY` — model routing for all agents
- `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` — database + auth
- `DAYTONA_API_URL` / `DAYTONA_API_KEY` — sandbox provisioning
- `GITHUB_TOKEN` — repo access and PR creation

## License

Private.
