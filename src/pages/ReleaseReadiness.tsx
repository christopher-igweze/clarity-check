import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Gauge, ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  createBuildRun,
  createValidationCampaign,
  decideGoLive,
  getCampaignReport,
  getProgramSloSummary,
  ingestCampaignRun,
  upsertReleaseChecklist,
  upsertRollbackDrill,
  type ProgramCampaignReport,
} from "@/lib/api";

function splitList(raw: string): string[] {
  return raw
    .split(/\n|,/)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

const ReleaseReadiness = () => {
  const navigate = useNavigate();

  const [error, setError] = useState<string | null>(null);
  const [campaignName, setCampaignName] = useState("release-validation");
  const [campaignRepos, setCampaignRepos] = useState(
    "https://github.com/pallets/flask\nhttps://github.com/expressjs/express",
  );
  const [runsPerRepo, setRunsPerRepo] = useState("3");
  const [campaignId, setCampaignId] = useState("");
  const [campaignReport, setCampaignReport] = useState<ProgramCampaignReport | null>(null);

  const [runRepo, setRunRepo] = useState("https://github.com/pallets/flask");
  const [runLanguage, setRunLanguage] = useState("python");
  const [runId, setRunId] = useState("run-001");
  const [runStatus, setRunStatus] = useState<"completed" | "failed" | "aborted">("completed");
  const [runDurationMs, setRunDurationMs] = useState("1200");

  const [releaseId, setReleaseId] = useState("release-2026-06-14");
  const [securityReview, setSecurityReview] = useState(true);
  const [sloDashboard, setSloDashboard] = useState(true);
  const [rollbackTested, setRollbackTested] = useState(true);
  const [docsComplete, setDocsComplete] = useState(true);
  const [runbooksReady, setRunbooksReady] = useState(true);
  const [rollbackPassed, setRollbackPassed] = useState(true);
  const [rollbackDurationMinutes, setRollbackDurationMinutes] = useState("8");
  const [rollbackIssues, setRollbackIssues] = useState("");
  const [decision, setDecision] = useState<Record<string, unknown> | null>(null);

  const [sloSummary, setSloSummary] = useState<Record<string, unknown> | null>(null);
  const [sampleBuildRepo, setSampleBuildRepo] = useState("https://github.com/octocat/Hello-World");
  const [sampleBuildId, setSampleBuildId] = useState("");

  const releaseReady = useMemo(() => {
    if (!campaignReport) return false;
    return Boolean(campaignReport.rubric.release_ready);
  }, [campaignReport]);

  const withError = async (fn: () => Promise<void>) => {
    setError(null);
    try {
      await fn();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-pattern opacity-30 pointer-events-none" />

      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-6xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/dashboard")}>
          <ShieldCheck className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Release</span>
            <span className="text-foreground">Readiness</span>
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={() => navigate("/program-ops")}>
            Advanced Program Ops
          </Button>
          <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-4 h-4 mr-1" /> Dashboard
          </Button>
        </div>
      </nav>

      <main className="relative z-10 max-w-5xl mx-auto px-6 pb-20 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Release Readiness Console</h1>
          <Badge variant={releaseReady ? "default" : "outline"}>
            {releaseReady ? "Validation: Release Ready" : "Validation: Needs Hardening"}
          </Badge>
        </div>
        {error && <div className="text-sm text-destructive">{error}</div>}

        <Card className="glass">
          <CardHeader>
            <CardTitle>Validation Dashboard</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={campaignName} onChange={(e) => setCampaignName(e.target.value)} placeholder="Campaign name" />
            <Textarea
              value={campaignRepos}
              onChange={(e) => setCampaignRepos(e.target.value)}
              placeholder="One repository per line"
              className="min-h-20"
            />
            <Input value={runsPerRepo} onChange={(e) => setRunsPerRepo(e.target.value)} placeholder="Runs per repo" />
            <div className="flex flex-wrap gap-2">
              <Button
                onClick={() =>
                  withError(async () => {
                    const row = await createValidationCampaign({
                      name: campaignName,
                      repos: splitList(campaignRepos),
                      runsPerRepo: Math.max(1, Number(runsPerRepo) || 1),
                    });
                    setCampaignId(row.campaign_id);
                  })
                }
              >
                Create Campaign
              </Button>
              <Button
                variant="outline"
                disabled={!campaignId}
                onClick={() =>
                  withError(async () => {
                    const row = await getCampaignReport(campaignId);
                    setCampaignReport(row);
                  })
                }
              >
                Refresh Report
              </Button>
              {campaignId && <Badge variant="outline">Campaign: {campaignId}</Badge>}
            </div>

            <div className="grid md:grid-cols-5 gap-2">
              <Input value={runRepo} onChange={(e) => setRunRepo(e.target.value)} placeholder="repo" />
              <Input value={runLanguage} onChange={(e) => setRunLanguage(e.target.value)} placeholder="language" />
              <Input value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="run id" />
              <Input value={runStatus} onChange={(e) => setRunStatus((e.target.value as "completed" | "failed" | "aborted") || "completed")} placeholder="status" />
              <Input value={runDurationMs} onChange={(e) => setRunDurationMs(e.target.value)} placeholder="duration ms" />
            </div>
            <Button
              variant="outline"
              disabled={!campaignId}
              onClick={() =>
                withError(async () => {
                  await ingestCampaignRun({
                    campaignId,
                    repo: runRepo,
                    language: runLanguage,
                    runId,
                    status: runStatus,
                    durationMs: Math.max(0, Number(runDurationMs) || 0),
                  });
                  setRunId((prev) => {
                    const suffix = Number(prev.split("-").pop() || "0") + 1;
                    return `run-${String(suffix).padStart(3, "0")}`;
                  });
                })
              }
            >
              Ingest Run
            </Button>

            {campaignReport && (
              <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">
                {JSON.stringify(campaignReport, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle>Release Gates + Go/No-Go</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={releaseId} onChange={(e) => setReleaseId(e.target.value)} placeholder="Release ID" />
            <div className="grid md:grid-cols-3 gap-2 text-sm">
              <label className="flex items-center gap-2"><input type="checkbox" checked={securityReview} onChange={(e) => setSecurityReview(e.target.checked)} /> Security review</label>
              <label className="flex items-center gap-2"><input type="checkbox" checked={sloDashboard} onChange={(e) => setSloDashboard(e.target.checked)} /> SLO dashboard</label>
              <label className="flex items-center gap-2"><input type="checkbox" checked={rollbackTested} onChange={(e) => setRollbackTested(e.target.checked)} /> Rollback tested</label>
              <label className="flex items-center gap-2"><input type="checkbox" checked={docsComplete} onChange={(e) => setDocsComplete(e.target.checked)} /> Docs complete</label>
              <label className="flex items-center gap-2"><input type="checkbox" checked={runbooksReady} onChange={(e) => setRunbooksReady(e.target.checked)} /> Runbooks ready</label>
              <label className="flex items-center gap-2"><input type="checkbox" checked={rollbackPassed} onChange={(e) => setRollbackPassed(e.target.checked)} /> Rollback drill passed</label>
            </div>
            <Input value={rollbackDurationMinutes} onChange={(e) => setRollbackDurationMinutes(e.target.value)} placeholder="Rollback duration (minutes)" />
            <Textarea
              value={rollbackIssues}
              onChange={(e) => setRollbackIssues(e.target.value)}
              placeholder="Rollback issues (comma or newline separated)"
              className="min-h-16"
            />
            <Button
              onClick={() =>
                withError(async () => {
                  await upsertReleaseChecklist({
                    releaseId,
                    securityReview,
                    sloDashboard,
                    rollbackTested,
                    docsComplete,
                    runbooksReady,
                  });
                  await upsertRollbackDrill({
                    releaseId,
                    passed: rollbackPassed,
                    durationMinutes: Math.max(1, Number(rollbackDurationMinutes) || 1),
                    issuesFound: splitList(rollbackIssues),
                  });
                  const row = await decideGoLive({
                    releaseId,
                    validationReleaseReady: releaseReady,
                  });
                  setDecision(row as unknown as Record<string, unknown>);
                })
              }
            >
              Evaluate Go/No-Go
            </Button>
            {decision && (
              <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(decision, null, 2)}</pre>
            )}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gauge className="w-4 h-4" /> Live Platform Signals
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex flex-wrap gap-2">
              <Input value={sampleBuildRepo} onChange={(e) => setSampleBuildRepo(e.target.value)} placeholder="Build repo URL" />
              <Button
                variant="outline"
                onClick={() =>
                  withError(async () => {
                    const row = await createBuildRun({
                      repoUrl: sampleBuildRepo,
                      objective: "release-readiness sample build",
                      metadata: { scan_mode: "autonomous" },
                    });
                    setSampleBuildId(row.buildId);
                  })
                }
              >
                Create Sample Build
              </Button>
              {sampleBuildId && <Badge variant="outline">Build: {sampleBuildId}</Badge>}
            </div>
            <Button
              variant="outline"
              onClick={() =>
                withError(async () => {
                  const row = await getProgramSloSummary();
                  setSloSummary(row as unknown as Record<string, unknown>);
                })
              }
            >
              Refresh SLO Summary
            </Button>
            {sloSummary && (
              <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(sloSummary, null, 2)}</pre>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default ReleaseReadiness;
