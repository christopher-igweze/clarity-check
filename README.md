# Clarity Check (Clerk + Supabase)

This app now uses:
- **Clerk** for frontend authentication
- **Supabase** for database + edge functions
- Optional FastAPI backend at `VITE_API_BASE_URL` for audit orchestration

## 1) Create Your Own Supabase Project

1. Create a new project in Supabase.
2. Copy:
   - Project URL
   - Anon/Public key
3. Set env values in `.env.local` (copy from `.env.example`):

```bash
VITE_SUPABASE_URL="https://YOUR_PROJECT_REF.supabase.co"
VITE_SUPABASE_PUBLISHABLE_KEY="YOUR_SUPABASE_ANON_KEY"
```

4. Set your project ref in `supabase/config.toml`:

```toml
project_id = "YOUR_PROJECT_REF"
```

5. Apply schema migrations:

```bash
supabase link --project-ref YOUR_PROJECT_REF
supabase db push
```

## 2) Create Your Own Clerk App

1. Create a Clerk application.
2. Enable the auth providers you want (Google, etc).
3. Set frontend env:

```bash
VITE_CLERK_PUBLISHABLE_KEY="pk_test_xxx"
```

## 3) Connect Clerk Tokens to Supabase RLS

This repo is configured for Clerk-compatible RLS using JWT `sub`.

- SQL policies use `auth.jwt()->>'sub'` through `public.requesting_user_id()`.
- `user_id` columns are stored as `TEXT` to match Clerk user IDs.

### Supabase auth configuration

In your **Supabase project dashboard**, configure JWT verification for Clerk (follow Clerk's Supabase guide). The database policies in this repo assume the incoming JWT has a `sub` claim equal to the Clerk user id.

### Optional fallback template

If you use a Clerk JWT template instead of native third-party auth wiring, set:

```bash
VITE_CLERK_SUPABASE_TEMPLATE="your_template_name"
```

Otherwise keep it empty.

## 4) Run Locally

```bash
npm install
npm run dev
```

Open:
- http://localhost:5173

Protected routes redirect to `/sign-in` (Clerk-hosted UI component).

## 5) Notes

- `AuthContext` now bootstraps a `profiles` row automatically after Clerk login.
- Supabase requests include Clerk bearer tokens via `createClient(..., { accessToken })`.
- If API calls still fail auth locally, set `VITE_LOCAL_DEV_BEARER_TOKEN` temporarily.

## Backend

If you want to run the FastAPI backend included in this repo, see `backend/README.md`.
