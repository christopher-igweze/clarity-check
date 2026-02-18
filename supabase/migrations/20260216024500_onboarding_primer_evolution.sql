-- Onboarding profile fields
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS onboarding_complete boolean NOT NULL DEFAULT false,
ADD COLUMN IF NOT EXISTS technical_level text,
ADD COLUMN IF NOT EXISTS explanation_style text,
ADD COLUMN IF NOT EXISTS shipping_posture text NOT NULL DEFAULT 'balanced',
ADD COLUMN IF NOT EXISTS tool_tags jsonb NOT NULL DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS acquisition_source text,
ADD COLUMN IF NOT EXISTS acquisition_other text;

-- Scan report metadata for intake / primer / evolution
ALTER TABLE public.scan_reports
ADD COLUMN IF NOT EXISTS project_intake jsonb,
ADD COLUMN IF NOT EXISTS primer_summary text,
ADD COLUMN IF NOT EXISTS audit_confidence integer,
ADD COLUMN IF NOT EXISTS evolution_report jsonb;

ALTER TABLE public.scan_reports
DROP CONSTRAINT IF EXISTS scan_reports_scan_tier_check;

ALTER TABLE public.scan_reports
ALTER COLUMN scan_tier SET DEFAULT 'deep';

UPDATE public.scan_reports
SET scan_tier = 'deep'
WHERE scan_tier IS DISTINCT FROM 'deep';

ALTER TABLE public.scan_reports
ALTER COLUMN scan_tier SET NOT NULL;

ALTER TABLE public.scan_reports
ADD CONSTRAINT scan_reports_scan_tier_check
CHECK (scan_tier = 'deep');

ALTER TABLE public.projects
DROP CONSTRAINT IF EXISTS projects_latest_scan_tier_check;

ALTER TABLE public.projects
ALTER COLUMN latest_scan_tier SET DEFAULT 'deep';

UPDATE public.projects
SET latest_scan_tier = 'deep'
WHERE latest_scan_tier IS NOT NULL
  AND latest_scan_tier IS DISTINCT FROM 'deep';

ALTER TABLE public.projects
ADD CONSTRAINT projects_latest_scan_tier_check
CHECK (latest_scan_tier IS NULL OR latest_scan_tier = 'deep');

-- Commit-aware primer cache
CREATE TABLE IF NOT EXISTS public.project_primers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id text NOT NULL,
  repo_sha text NOT NULL,
  primer_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  summary text NOT NULL DEFAULT '',
  confidence integer NOT NULL DEFAULT 0 CHECK (confidence >= 0 AND confidence <= 100),
  failure_reason text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(project_id, repo_sha)
);

ALTER TABLE public.project_primers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own primers"
  ON public.project_primers FOR SELECT
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can insert their own primers"
  ON public.project_primers FOR INSERT
  WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can update their own primers"
  ON public.project_primers FOR UPDATE
  USING (public.requesting_user_id() = user_id);

DROP TRIGGER IF EXISTS update_project_primers_updated_at ON public.project_primers;
CREATE TRIGGER update_project_primers_updated_at
  BEFORE UPDATE ON public.project_primers
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE INDEX IF NOT EXISTS idx_project_primers_project_id
  ON public.project_primers(project_id);

CREATE INDEX IF NOT EXISTS idx_project_primers_repo_sha
  ON public.project_primers(repo_sha);
