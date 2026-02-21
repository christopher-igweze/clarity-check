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

### Clerk Setup (Current Project Path)

This repo currently uses Clerk tokens from the frontend (`getToken`) and backend verifies HS256 with `SUPABASE_JWT_SECRET`.

1. In Clerk Dashboard, create/update a JWT template (for example `supabase`).
2. Put the template name in frontend env:
`VITE_CLERK_SUPABASE_TEMPLATE="supabase"`.
3. Set backend `SUPABASE_JWT_SECRET` to the signing key for that Clerk JWT template.
4. Ensure the token includes:
`sub`, `aud="authenticated"`, and role/capability claims when `ENFORCE_CAPABILITY_AUTH=true`.

Recommended staging admin claims payload:

```json
{
  "sub": "{{user.id}}",
  "aud": "authenticated",
  "role": "authenticated",
  "email": "{{user.primary_email_address}}",
  "roles": ["admin"],
  "capabilities": ["*"],
  "app_metadata": {
    "roles": ["admin"],
    "capabilities": ["*"]
  },
  "user_metadata": {}
}
```
