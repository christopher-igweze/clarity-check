-- Required coding-agent preferences captured during onboarding.
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS coding_agent_provider text,
ADD COLUMN IF NOT EXISTS coding_agent_model text;

UPDATE public.profiles
SET
  coding_agent_provider = COALESCE(NULLIF(coding_agent_provider, ''), 'openai'),
  coding_agent_model = COALESCE(NULLIF(coding_agent_model, ''), 'openai/gpt-5.2-codex')
WHERE coding_agent_provider IS NULL
   OR coding_agent_provider = ''
   OR coding_agent_model IS NULL
   OR coding_agent_model = '';

ALTER TABLE public.profiles
ALTER COLUMN coding_agent_provider SET NOT NULL,
ALTER COLUMN coding_agent_model SET NOT NULL;

ALTER TABLE public.profiles
DROP CONSTRAINT IF EXISTS profiles_coding_agent_provider_check;

ALTER TABLE public.profiles
ADD CONSTRAINT profiles_coding_agent_provider_check
CHECK (coding_agent_provider IN ('openai', 'anthropic', 'google'));
