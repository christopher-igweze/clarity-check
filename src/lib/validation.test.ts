import { describe, expect, it } from "vitest";

import { evaluateValidationGate, type ValidationSummary } from "@/lib/validation";

const baseSummary: ValidationSummary = {
  repo_count: 2,
  run_count: 6,
  avg_success_rate: 0.91,
  max_duration_cv: 0.18,
  repos: [
    {
      repo: "repo-a",
      language: "python",
      run_count: 3,
      success_count: 3,
      success_rate: 1,
      mean_duration_ms: 1200,
      duration_stddev_ms: 90,
      duration_cv: 0.075,
    },
    {
      repo: "repo-b",
      language: "node",
      run_count: 3,
      success_count: 2,
      success_rate: 0.667,
      mean_duration_ms: 1500,
      duration_stddev_ms: 650,
      duration_cv: 0.433,
    },
  ],
};

describe("evaluateValidationGate", () => {
  it("passes when all repo thresholds are met", () => {
    const summary: ValidationSummary = {
      ...baseSummary,
      repos: baseSummary.repos.map((repo) => ({ ...repo, success_rate: 1, duration_cv: 0.1 })),
    };
    const result = evaluateValidationGate(summary);
    expect(result.passed).toBe(true);
    expect(result.reasons).toHaveLength(0);
  });

  it("returns reasons when repo thresholds fail", () => {
    const result = evaluateValidationGate(baseSummary);
    expect(result.passed).toBe(false);
    expect(result.reasons.some((reason) => reason.startsWith("success_rate_below_threshold:repo-b"))).toBe(true);
    expect(result.reasons.some((reason) => reason.startsWith("duration_variance_above_threshold:repo-b"))).toBe(true);
  });
});

