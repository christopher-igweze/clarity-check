-- Additional normalized control-plane entities for production hardening.

CREATE TABLE IF NOT EXISTS public.build_checkpoints (
  checkpoint_id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES public.build_runs(build_id) ON DELETE CASCADE,
  user_id text NOT NULL,
  status text NOT NULL,
  reason text NOT NULL,
  event_cursor integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_build_checkpoints_build_created
  ON public.build_checkpoints(build_id, created_at DESC);

ALTER TABLE public.build_checkpoints ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own build checkpoints" ON public.build_checkpoints;
CREATE POLICY "Users can view their own build checkpoints"
  ON public.build_checkpoints FOR SELECT USING (public.requesting_user_id() = user_id);

DROP POLICY IF EXISTS "Users can insert their own build checkpoints" ON public.build_checkpoints;
CREATE POLICY "Users can insert their own build checkpoints"
  ON public.build_checkpoints FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

CREATE TABLE IF NOT EXISTS public.program_policy_profiles (
  profile_id uuid PRIMARY KEY,
  user_id text NOT NULL,
  name text NOT NULL,
  blocked_commands jsonb NOT NULL DEFAULT '[]'::jsonb,
  restricted_paths jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS update_program_policy_profiles_updated_at ON public.program_policy_profiles;
CREATE TRIGGER update_program_policy_profiles_updated_at
  BEFORE UPDATE ON public.program_policy_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE public.program_policy_profiles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own program policy profiles" ON public.program_policy_profiles;
CREATE POLICY "Users can view their own program policy profiles"
  ON public.program_policy_profiles FOR SELECT USING (public.requesting_user_id() = user_id);

DROP POLICY IF EXISTS "Users can insert their own program policy profiles" ON public.program_policy_profiles;
CREATE POLICY "Users can insert their own program policy profiles"
  ON public.program_policy_profiles FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

DROP POLICY IF EXISTS "Users can update their own program policy profiles" ON public.program_policy_profiles;
CREATE POLICY "Users can update their own program policy profiles"
  ON public.program_policy_profiles FOR UPDATE USING (public.requesting_user_id() = user_id);

CREATE TABLE IF NOT EXISTS public.program_secrets (
  secret_id uuid PRIMARY KEY,
  user_id text NOT NULL,
  name text NOT NULL,
  encrypted_value text NOT NULL,
  cipher_digest text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(user_id, name)
);

DROP TRIGGER IF EXISTS update_program_secrets_updated_at ON public.program_secrets;
CREATE TRIGGER update_program_secrets_updated_at
  BEFORE UPDATE ON public.program_secrets
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE public.program_secrets ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own program secrets" ON public.program_secrets;
CREATE POLICY "Users can view their own program secrets"
  ON public.program_secrets FOR SELECT USING (public.requesting_user_id() = user_id);

DROP POLICY IF EXISTS "Users can insert their own program secrets" ON public.program_secrets;
CREATE POLICY "Users can insert their own program secrets"
  ON public.program_secrets FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

DROP POLICY IF EXISTS "Users can update their own program secrets" ON public.program_secrets;
CREATE POLICY "Users can update their own program secrets"
  ON public.program_secrets FOR UPDATE USING (public.requesting_user_id() = user_id);

CREATE TABLE IF NOT EXISTS public.program_idempotent_checkpoints (
  build_id uuid NOT NULL REFERENCES public.build_runs(build_id) ON DELETE CASCADE,
  idempotency_key text NOT NULL,
  checkpoint_id uuid NOT NULL,
  status text NOT NULL,
  reason text NOT NULL,
  created_ts bigint NOT NULL,
  user_id text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (build_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS idx_program_idempotent_checkpoints_created
  ON public.program_idempotent_checkpoints(created_at DESC);

ALTER TABLE public.program_idempotent_checkpoints ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view their own idempotent checkpoints" ON public.program_idempotent_checkpoints;
CREATE POLICY "Users can view their own idempotent checkpoints"
  ON public.program_idempotent_checkpoints FOR SELECT USING (public.requesting_user_id() = user_id);

DROP POLICY IF EXISTS "Users can insert their own idempotent checkpoints" ON public.program_idempotent_checkpoints;
CREATE POLICY "Users can insert their own idempotent checkpoints"
  ON public.program_idempotent_checkpoints FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

DROP POLICY IF EXISTS "Users can update their own idempotent checkpoints" ON public.program_idempotent_checkpoints;
CREATE POLICY "Users can update their own idempotent checkpoints"
  ON public.program_idempotent_checkpoints FOR UPDATE USING (public.requesting_user_id() = user_id);
