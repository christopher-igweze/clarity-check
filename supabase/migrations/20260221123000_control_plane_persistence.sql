-- Control-plane persistence schema for orchestration/program hardening.

CREATE TABLE IF NOT EXISTS public.control_plane_state (
  state_key text PRIMARY KEY,
  state_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS update_control_plane_state_updated_at ON public.control_plane_state;
CREATE TRIGGER update_control_plane_state_updated_at
  BEFORE UPDATE ON public.control_plane_state
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TABLE IF NOT EXISTS public.build_runs (
  build_id uuid PRIMARY KEY,
  user_id text NOT NULL,
  repo_url text NOT NULL,
  objective text NOT NULL,
  status text NOT NULL,
  dag jsonb NOT NULL DEFAULT '[]'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.build_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  build_id uuid NOT NULL REFERENCES public.build_runs(build_id) ON DELETE CASCADE,
  user_id text NOT NULL,
  event_type text NOT NULL,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.build_tasks (
  task_run_id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES public.build_runs(build_id) ON DELETE CASCADE,
  user_id text NOT NULL,
  node_id text NOT NULL,
  attempt integer NOT NULL DEFAULT 1,
  status text NOT NULL,
  error text,
  started_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz
);

CREATE TABLE IF NOT EXISTS public.replan_decisions (
  decision_id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES public.build_runs(build_id) ON DELETE CASCADE,
  user_id text NOT NULL,
  action text NOT NULL,
  reason text NOT NULL,
  replacement_nodes jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.debt_items (
  debt_id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES public.build_runs(build_id) ON DELETE CASCADE,
  user_id text NOT NULL,
  node_id text NOT NULL,
  summary text NOT NULL,
  severity text NOT NULL DEFAULT 'medium',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.policy_violations (
  violation_id uuid PRIMARY KEY,
  build_id uuid NOT NULL REFERENCES public.build_runs(build_id) ON DELETE CASCADE,
  user_id text NOT NULL,
  code text NOT NULL,
  message text NOT NULL,
  source text NOT NULL,
  blocking boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.validation_campaigns (
  campaign_id uuid PRIMARY KEY,
  user_id text NOT NULL,
  name text NOT NULL,
  repos jsonb NOT NULL DEFAULT '[]'::jsonb,
  runs_per_repo integer NOT NULL DEFAULT 3,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.validation_campaign_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid NOT NULL REFERENCES public.validation_campaigns(campaign_id) ON DELETE CASCADE,
  user_id text NOT NULL,
  run_id text NOT NULL,
  repo text NOT NULL,
  language text NOT NULL,
  status text NOT NULL,
  duration_ms integer NOT NULL DEFAULT 0,
  findings_total integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(campaign_id, run_id)
);

CREATE TABLE IF NOT EXISTS public.release_checklists (
  release_id text PRIMARY KEY,
  user_id text NOT NULL,
  security_review boolean NOT NULL DEFAULT false,
  slo_dashboard boolean NOT NULL DEFAULT false,
  rollback_tested boolean NOT NULL DEFAULT false,
  docs_complete boolean NOT NULL DEFAULT false,
  runbooks_ready boolean NOT NULL DEFAULT false,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.rollback_drills (
  release_id text PRIMARY KEY,
  user_id text NOT NULL,
  passed boolean NOT NULL,
  duration_minutes integer NOT NULL,
  issues_found jsonb NOT NULL DEFAULT '[]'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.go_live_decisions (
  release_id text PRIMARY KEY,
  user_id text NOT NULL,
  status text NOT NULL,
  reasons jsonb NOT NULL DEFAULT '[]'::jsonb,
  decided_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_build_runs_user_status ON public.build_runs(user_id, status, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_build_events_build_created ON public.build_events(build_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_build_tasks_build_status ON public.build_tasks(build_id, status, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_validation_campaigns_user ON public.validation_campaigns(user_id, created_at DESC);

DROP TRIGGER IF EXISTS update_build_runs_updated_at ON public.build_runs;
CREATE TRIGGER update_build_runs_updated_at
  BEFORE UPDATE ON public.build_runs
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_validation_campaigns_updated_at ON public.validation_campaigns;
CREATE TRIGGER update_validation_campaigns_updated_at
  BEFORE UPDATE ON public.validation_campaigns
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

ALTER TABLE public.build_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.build_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.build_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.replan_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.debt_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.policy_violations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.validation_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.validation_campaign_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.release_checklists ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rollback_drills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.go_live_decisions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own build runs"
  ON public.build_runs FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own build runs"
  ON public.build_runs FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own build runs"
  ON public.build_runs FOR UPDATE USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own build events"
  ON public.build_events FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own build events"
  ON public.build_events FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own build tasks"
  ON public.build_tasks FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own build tasks"
  ON public.build_tasks FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own build tasks"
  ON public.build_tasks FOR UPDATE USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own replan decisions"
  ON public.replan_decisions FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own replan decisions"
  ON public.replan_decisions FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own debt items"
  ON public.debt_items FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own debt items"
  ON public.debt_items FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own policy violations"
  ON public.policy_violations FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own policy violations"
  ON public.policy_violations FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own validation campaigns"
  ON public.validation_campaigns FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own validation campaigns"
  ON public.validation_campaigns FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own validation campaigns"
  ON public.validation_campaigns FOR UPDATE USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own validation campaign runs"
  ON public.validation_campaign_runs FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own validation campaign runs"
  ON public.validation_campaign_runs FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own release checklists"
  ON public.release_checklists FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own release checklists"
  ON public.release_checklists FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own release checklists"
  ON public.release_checklists FOR UPDATE USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own rollback drills"
  ON public.rollback_drills FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own rollback drills"
  ON public.rollback_drills FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own rollback drills"
  ON public.rollback_drills FOR UPDATE USING (public.requesting_user_id() = user_id);

CREATE POLICY "Users can view their own go-live decisions"
  ON public.go_live_decisions FOR SELECT USING (public.requesting_user_id() = user_id);
CREATE POLICY "Users can insert their own go-live decisions"
  ON public.go_live_decisions FOR INSERT WITH CHECK (public.requesting_user_id() = user_id);
CREATE POLICY "Users can update their own go-live decisions"
  ON public.go_live_decisions FOR UPDATE USING (public.requesting_user_id() = user_id);
