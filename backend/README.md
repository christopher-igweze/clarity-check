# Backend (FastAPI)

This folder contains a FastAPI backend intended to orchestrate audits and stream progress via SSE.

## Local Run

Prereqs:
- Python 3.12+

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Auth Notes

The frontend sends a `Bearer` token for API calls (Clerk token or dev token).

If you want strict verification in the backend, wire token verification to whatever JWT strategy you use with Supabase:
- Clerk JWT template (HS256 using Supabase JWT secret), or
- Clerk JWKS (RS256) if you configured Supabase to validate Clerk tokens directly.

At minimum, the backend should treat the user id as the JWT `sub` claim (Clerk user id string).
