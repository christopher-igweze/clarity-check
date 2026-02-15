-- Clerk-compatible auth model:
-- Store external identity in user_id (text), sourced from JWT sub claim.

CREATE OR REPLACE FUNCTION public.requesting_user_id()
RETURNS text
LANGUAGE sql
STABLE
AS $$
  SELECT NULLIF(auth.jwt() ->> 'sub', '');
$$;

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- Profiles table
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL UNIQUE,
  github_username TEXT,
  avatar_url TEXT,
  display_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
  ON public.profiles FOR SELECT
  USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can insert their own profile"
  ON public.profiles FOR INSERT
  WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can update their own profile"
  ON public.profiles FOR UPDATE
  USING (public.requesting_user_id() = user_id);

CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Projects table
CREATE TABLE public.projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  repo_url TEXT NOT NULL,
  repo_name TEXT,
  vibe_prompt TEXT,
  project_charter JSONB,
  latest_health_score INTEGER,
  latest_scan_tier TEXT CHECK (latest_scan_tier IN ('surface', 'deep')),
  scan_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own projects"
  ON public.projects FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own projects"
  ON public.projects FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own projects"
  ON public.projects FOR UPDATE USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can delete their own projects"
  ON public.projects FOR DELETE USING (public.requesting_user_id() = user_id);

CREATE TRIGGER update_projects_updated_at
  BEFORE UPDATE ON public.projects
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Scan reports table
CREATE TABLE public.scan_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  scan_tier TEXT NOT NULL CHECK (scan_tier IN ('surface', 'deep')),
  health_score INTEGER,
  security_score INTEGER,
  reliability_score INTEGER,
  scalability_score INTEGER,
  report_data JSONB,
  agent_logs JSONB,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'scanning', 'completed', 'failed')),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.scan_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own scan reports"
  ON public.scan_reports FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own scan reports"
  ON public.scan_reports FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own scan reports"
  ON public.scan_reports FOR UPDATE USING (public.requesting_user_id() = user_id);

-- Action items table
CREATE TABLE public.action_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_report_id UUID NOT NULL REFERENCES public.scan_reports(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL CHECK (category IN ('security', 'reliability', 'scalability')),
  severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
  source TEXT NOT NULL DEFAULT 'static' CHECK (source IN ('static', 'dynamic')),
  file_path TEXT,
  line_number INTEGER,
  why_it_matters TEXT,
  cto_perspective TEXT,
  fix_status TEXT NOT NULL DEFAULT 'open' CHECK (fix_status IN ('open', 'in_progress', 'fixed', 'wont_fix')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.action_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own action items"
  ON public.action_items FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own action items"
  ON public.action_items FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own action items"
  ON public.action_items FOR UPDATE USING (public.requesting_user_id() = user_id);

-- Fix attempts table
CREATE TABLE public.fix_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  action_item_id UUID NOT NULL REFERENCES public.action_items(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'failed')),
  sandbox_id TEXT,
  diff_preview TEXT,
  pr_url TEXT,
  agent_logs JSONB,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.fix_attempts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own fix attempts"
  ON public.fix_attempts FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own fix attempts"
  ON public.fix_attempts FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own fix attempts"
  ON public.fix_attempts FOR UPDATE USING (public.requesting_user_id() = user_id);

-- Trajectories table (for future fine-tuning)
CREATE TABLE public.trajectories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  fix_attempt_id UUID NOT NULL REFERENCES public.fix_attempts(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  prompt TEXT,
  code_changes JSONB,
  test_results JSONB,
  success BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.trajectories ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own trajectories"
  ON public.trajectories FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own trajectories"
  ON public.trajectories FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

-- Indexes for performance
CREATE INDEX idx_projects_user_id ON public.projects(user_id);
CREATE INDEX idx_scan_reports_project_id ON public.scan_reports(project_id);
CREATE INDEX idx_scan_reports_user_id ON public.scan_reports(user_id);
CREATE INDEX idx_action_items_scan_report_id ON public.action_items(scan_report_id);
CREATE INDEX idx_action_items_project_id ON public.action_items(project_id);
CREATE INDEX idx_fix_attempts_action_item_id ON public.fix_attempts(action_item_id);
CREATE INDEX idx_trajectories_fix_attempt_id ON public.trajectories(fix_attempt_id);
