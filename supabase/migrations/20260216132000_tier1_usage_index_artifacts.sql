-- Tier 1 free usage, commit-aware index cache, and report artifacts.

-- Allow free/deep scan tier coexistence.
ALTER TABLE public.scan_reports
DROP CONSTRAINT IF EXISTS scan_reports_scan_tier_check;

ALTER TABLE public.scan_reports
ADD CONSTRAINT scan_reports_scan_tier_check
CHECK (scan_tier IN ('deep', 'free'));

ALTER TABLE public.projects
DROP CONSTRAINT IF EXISTS projects_latest_scan_tier_check;

ALTER TABLE public.projects
ADD CONSTRAINT projects_latest_scan_tier_check
CHECK (latest_scan_tier IS NULL OR latest_scan_tier IN ('deep', 'free'));

CREATE TABLE IF NOT EXISTS public.free_usage_monthly (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  month_key date NOT NULL,
  reports_generated integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(user_id, month_key)
);

CREATE TABLE IF NOT EXISTS public.project_indexes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id text NOT NULL,
  repo_sha text NOT NULL,
  loc_total integer NOT NULL DEFAULT 0,
  file_count integer NOT NULL DEFAULT 0,
  index_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  expires_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(project_id, repo_sha)
);

CREATE TABLE IF NOT EXISTS public.report_artifacts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_report_id uuid NOT NULL REFERENCES public.scan_reports(id) ON DELETE CASCADE,
  project_id uuid NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id text NOT NULL,
  artifact_type text NOT NULL DEFAULT 'markdown',
  content text NOT NULL,
  expires_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(scan_report_id, artifact_type)
);

CREATE INDEX IF NOT EXISTS idx_free_usage_monthly_user_month
  ON public.free_usage_monthly(user_id, month_key);

CREATE INDEX IF NOT EXISTS idx_project_indexes_project_sha
  ON public.project_indexes(project_id, repo_sha);

CREATE INDEX IF NOT EXISTS idx_project_indexes_expires_at
  ON public.project_indexes(expires_at);

CREATE INDEX IF NOT EXISTS idx_report_artifacts_scan_user
  ON public.report_artifacts(scan_report_id, user_id);

CREATE INDEX IF NOT EXISTS idx_report_artifacts_expires_at
  ON public.report_artifacts(expires_at);

ALTER TABLE public.free_usage_monthly ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_indexes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_artifacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own free usage"
  ON public.free_usage_monthly FOR SELECT
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can insert their own free usage"
  ON public.free_usage_monthly FOR INSERT
  WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can update their own free usage"
  ON public.free_usage_monthly FOR UPDATE
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own project indexes"
  ON public.project_indexes FOR SELECT
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can insert their own project indexes"
  ON public.project_indexes FOR INSERT
  WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can update their own project indexes"
  ON public.project_indexes FOR UPDATE
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can delete their own project indexes"
  ON public.project_indexes FOR DELETE
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own report artifacts"
  ON public.report_artifacts FOR SELECT
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can insert their own report artifacts"
  ON public.report_artifacts FOR INSERT
  WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can update their own report artifacts"
  ON public.report_artifacts FOR UPDATE
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can delete their own report artifacts"
  ON public.report_artifacts FOR DELETE
  USING (public.requesting_user_id() = user_id);

DROP TRIGGER IF EXISTS update_free_usage_monthly_updated_at ON public.free_usage_monthly;
CREATE TRIGGER update_free_usage_monthly_updated_at
  BEFORE UPDATE ON public.free_usage_monthly
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_project_indexes_updated_at ON public.project_indexes;
CREATE TRIGGER update_project_indexes_updated_at
  BEFORE UPDATE ON public.project_indexes
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();
