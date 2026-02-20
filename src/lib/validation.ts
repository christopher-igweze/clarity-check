export type RepoValidationSummary = {
  repo: string;
  language: string;
  run_count: number;
  success_count: number;
  success_rate: number;
  mean_duration_ms: number;
  duration_stddev_ms: number;
  duration_cv: number;
};

export type ValidationSummary = {
  repo_count: number;
  run_count: number;
  avg_success_rate: number;
  max_duration_cv: number;
  repos: RepoValidationSummary[];
};

export type ValidationGateResult = {
  passed: boolean;
  reasons: string[];
};

export function evaluateValidationGate(
  summary: ValidationSummary,
  {
    minSuccessRate = 0.8,
    maxDurationCv = 0.35,
    minRunsPerRepo = 3,
  }: {
    minSuccessRate?: number;
    maxDurationCv?: number;
    minRunsPerRepo?: number;
  } = {}
): ValidationGateResult {
  const reasons: string[] = [];
  if (summary.repo_count <= 0) {
    reasons.push("no_repositories_evaluated");
  }

  for (const repo of summary.repos) {
    if (repo.run_count < minRunsPerRepo) {
      reasons.push(`insufficient_runs:${repo.repo}:${repo.run_count}`);
    }
    if (repo.success_rate < minSuccessRate) {
      reasons.push(`success_rate_below_threshold:${repo.repo}:${repo.success_rate.toFixed(3)}`);
    }
    if (repo.duration_cv > maxDurationCv) {
      reasons.push(`duration_variance_above_threshold:${repo.repo}:${repo.duration_cv.toFixed(3)}`);
    }
  }

  return {
    passed: reasons.length === 0,
    reasons,
  };
}

