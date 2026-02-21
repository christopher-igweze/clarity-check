import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  createBuildRun,
  createIdempotentCheckpoint,
  createPolicyProfile,
  createProgramSecret,
  createValidationCampaign,
  decideGoLive,
  evaluatePolicyCheck,
  getCampaignReport,
  getProgramSloSummary,
  ingestCampaignRun,
  listProgramSecrets,
  upsertReleaseChecklist,
  upsertRollbackDrill,
  type ProgramCampaignReport,
  type ProgramPolicyResult,
  type ProgramSecretRef,
} from "@/lib/api";

function splitList(raw: string): string[] {
  return raw
    .split(/\n|,/)
    .map((item) => item.trim())
    .filter(Boolean);
}

const ProgramOps = () => {
  const navigate = useNavigate();

  const [error, setError] = useState<string | null>(null);

  const [campaignName, setCampaignName] = useState("open-source-validation");
  const [campaignRepos, setCampaignRepos] = useState("https://github.com/pallets/flask\nhttps://github.com/expressjs/express");
  const [campaignRunsPerRepo, setCampaignRunsPerRepo] = useState("3");
  const [campaignId, setCampaignId] = useState<string>("");
  const [campaignReport, setCampaignReport] = useState<ProgramCampaignReport | null>(null);

  const [runRepo, setRunRepo] = useState("https://github.com/pallets/flask");
  const [runLanguage, setRunLanguage] = useState("python");
  const [runId, setRunId] = useState("run-001");
  const [runStatus, setRunStatus] = useState<"completed" | "failed" | "aborted">("completed");
  const [runDurationMs, setRunDurationMs] = useState("1200");

  const [policyName, setPolicyName] = useState("strict-commands");
  const [blockedCommands, setBlockedCommands] = useState("rm -rf\ncurl | sh");
  const [restrictedPaths, setRestrictedPaths] = useState("/.git\n/etc");
  const [policyProfileId, setPolicyProfileId] = useState<string>("");
  const [policyCommand, setPolicyCommand] = useState("rm -rf /tmp/work");
  const [policyPath, setPolicyPath] = useState("/tmp/work");
  const [policyBuildId, setPolicyBuildId] = useState("");
  const [policyResult, setPolicyResult] = useState<ProgramPolicyResult | null>(null);

  const [secretName, setSecretName] = useState("github_pat");
  const [secretValue, setSecretValue] = useState("");
  const [secrets, setSecrets] = useState<ProgramSecretRef[]>([]);

  const [buildRepoUrl, setBuildRepoUrl] = useState("https://github.com/octocat/Hello-World");
  const [buildObjective, setBuildObjective] = useState("program-ops build checkpoint flow");
  const [buildId, setBuildId] = useState("");
  const [idempotencyKey, setIdempotencyKey] = useState("checkpoint-key-1");
  const [checkpointReason, setCheckpointReason] = useState("manual_program_checkpoint");
  const [checkpointResult, setCheckpointResult] = useState<Record<string, unknown> | null>(null);
  const [sloSummary, setSloSummary] = useState<Record<string, unknown> | null>(null);

  const [releaseId, setReleaseId] = useState("release-2026-06-14");
  const [securityReview, setSecurityReview] = useState(true);
  const [sloDashboard, setSloDashboard] = useState(true);
  const [rollbackTested, setRollbackTested] = useState(true);
  const [docsComplete, setDocsComplete] = useState(true);
  const [runbooksReady, setRunbooksReady] = useState(true);
  const [rollbackPassed, setRollbackPassed] = useState(true);
  const [rollbackDuration, setRollbackDuration] = useState("10");
  const [rollbackIssues, setRollbackIssues] = useState("");
  const [decisionResult, setDecisionResult] = useState<Record<string, unknown> | null>(null);

  const validationBadge = useMemo(() => {
    if (!campaignReport) return null;
    if (campaignReport.rubric.release_ready) return <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/40">Release Ready</Badge>;
    return <Badge variant="outline">Needs Hardening</Badge>;
  }, [campaignReport]);

  const withError = async (fn: () => Promise<void>) => {
    setError(null);
    try {
      await fn();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    }
  };

  const handleCreateCampaign = () =>
    withError(async () => {
      const campaign = await createValidationCampaign({
        name: campaignName,
        repos: splitList(campaignRepos),
        runsPerRepo: Math.max(1, Number(campaignRunsPerRepo) || 1),
      });
      setCampaignId(campaign.campaign_id);
    });

  const handleIngestRun = () =>
    withError(async () => {
      if (!campaignId) throw new Error("Create a campaign first.");
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
    });

  const handleFetchReport = () =>
    withError(async () => {
      if (!campaignId) throw new Error("Create a campaign first.");
      const report = await getCampaignReport(campaignId);
      setCampaignReport(report);
    });

  const handleCreatePolicy = () =>
    withError(async () => {
      const profile = await createPolicyProfile({
        name: policyName,
        blockedCommands: splitList(blockedCommands),
        restrictedPaths: splitList(restrictedPaths),
      });
      setPolicyProfileId(profile.profile_id);
    });

  const handlePolicyCheck = () =>
    withError(async () => {
      if (!policyProfileId) throw new Error("Create a policy profile first.");
      const result = await evaluatePolicyCheck({
        profileId: policyProfileId,
        command: policyCommand,
        path: policyPath || undefined,
        buildId: policyBuildId || undefined,
      });
      setPolicyResult(result);
    });

  const handleStoreSecret = () =>
    withError(async () => {
      if (!secretValue.trim()) throw new Error("Secret value is required.");
      await createProgramSecret({ name: secretName, value: secretValue });
      setSecretValue("");
      const rows = await listProgramSecrets();
      setSecrets(rows);
    });

  const handleCreateBuild = () =>
    withError(async () => {
      const result = await createBuildRun({
        repoUrl: buildRepoUrl,
        objective: buildObjective,
      });
      setBuildId(result.buildId);
      setPolicyBuildId(result.buildId);
    });

  const handleIdempotentCheckpoint = () =>
    withError(async () => {
      if (!buildId) throw new Error("Create a build first.");
      const result = await createIdempotentCheckpoint({
        buildId,
        idempotencyKey,
        reason: checkpointReason,
      });
      setCheckpointResult(result as unknown as Record<string, unknown>);
    });

  const handleSloSummary = () =>
    withError(async () => {
      const summary = await getProgramSloSummary();
      setSloSummary(summary as unknown as Record<string, unknown>);
    });

  const handleChecklistAndDecision = () =>
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
        durationMinutes: Math.max(1, Number(rollbackDuration) || 1),
        issuesFound: splitList(rollbackIssues),
      });
      const decision = await decideGoLive({
        releaseId,
        validationReleaseReady: campaignReport?.rubric.release_ready ?? false,
      });
      setDecisionResult(decision as unknown as Record<string, unknown>);
    });

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-pattern opacity-30 pointer-events-none" />
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/dashboard")}>
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Vibe</span>
            <span className="text-foreground">2Prod</span>
          </span>
        </div>
        <Button variant="ghost" size="sm" onClick={() => navigate("/dashboard")}>
          <ArrowLeft className="w-4 h-4 mr-1" /> Dashboard
        </Button>
      </nav>

      <main className="relative z-10 max-w-5xl mx-auto px-6 pb-20 space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Advanced Program Ops</h1>
          {validationBadge}
        </div>
        {error && <div className="text-sm text-destructive">{error}</div>}

        <Card className="glass">
          <CardHeader>
            <CardTitle>Week 7-8: Validation Campaign + Report</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={campaignName} onChange={(e) => setCampaignName(e.target.value)} placeholder="Campaign name" />
            <Textarea value={campaignRepos} onChange={(e) => setCampaignRepos(e.target.value)} placeholder="One repo per line" className="min-h-20" />
            <Input value={campaignRunsPerRepo} onChange={(e) => setCampaignRunsPerRepo(e.target.value)} placeholder="Runs per repo" />
            <div className="flex flex-wrap gap-2">
              <Button onClick={handleCreateCampaign}>Create Campaign</Button>
              <Button variant="outline" onClick={handleFetchReport} disabled={!campaignId}>Fetch Report</Button>
              {campaignId && <Badge variant="outline">Campaign: {campaignId}</Badge>}
            </div>

            <div className="grid md:grid-cols-5 gap-2">
              <Input value={runRepo} onChange={(e) => setRunRepo(e.target.value)} placeholder="repo" />
              <Input value={runLanguage} onChange={(e) => setRunLanguage(e.target.value)} placeholder="language" />
              <Input value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="run id" />
              <Input value={runStatus} onChange={(e) => setRunStatus((e.target.value as "completed" | "failed" | "aborted") || "completed")} placeholder="status" />
              <Input value={runDurationMs} onChange={(e) => setRunDurationMs(e.target.value)} placeholder="duration ms" />
            </div>
            <Button variant="outline" onClick={handleIngestRun} disabled={!campaignId}>Ingest Run</Button>

            {campaignReport && (
              <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(campaignReport, null, 2)}</pre>
            )}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle>Week 9: Policy Profile + Check</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={policyName} onChange={(e) => setPolicyName(e.target.value)} placeholder="Policy profile name" />
            <Textarea value={blockedCommands} onChange={(e) => setBlockedCommands(e.target.value)} placeholder="Blocked commands" className="min-h-16" />
            <Textarea value={restrictedPaths} onChange={(e) => setRestrictedPaths(e.target.value)} placeholder="Restricted paths" className="min-h-16" />
            <div className="flex gap-2 flex-wrap">
              <Button onClick={handleCreatePolicy}>Create Policy Profile</Button>
              {policyProfileId && <Badge variant="outline">Profile: {policyProfileId}</Badge>}
            </div>
            <Input value={policyCommand} onChange={(e) => setPolicyCommand(e.target.value)} placeholder="Command to evaluate" />
            <Input value={policyPath} onChange={(e) => setPolicyPath(e.target.value)} placeholder="Path (optional)" />
            <Input value={policyBuildId} onChange={(e) => setPolicyBuildId(e.target.value)} placeholder="Build ID for fail-closed write-back (optional)" />
            <Button variant="outline" onClick={handlePolicyCheck} disabled={!policyProfileId}>Evaluate Policy</Button>
            {policyResult && <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(policyResult, null, 2)}</pre>}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle>Week 10: Secret Storage</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={secretName} onChange={(e) => setSecretName(e.target.value)} placeholder="Secret name" />
            <Input value={secretValue} onChange={(e) => setSecretValue(e.target.value)} placeholder="Secret value" />
            <div className="flex gap-2">
              <Button onClick={handleStoreSecret}>Store Secret</Button>
              <Button variant="outline" onClick={() => withError(async () => setSecrets(await listProgramSecrets()))}>Refresh Secrets</Button>
            </div>
            {secrets.length > 0 && (
              <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(secrets, null, 2)}</pre>
            )}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle>Week 12-13: Idempotent Checkpoints + SLO</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input value={buildRepoUrl} onChange={(e) => setBuildRepoUrl(e.target.value)} placeholder="Build repo URL" />
            <Input value={buildObjective} onChange={(e) => setBuildObjective(e.target.value)} placeholder="Build objective" />
            <div className="flex gap-2 flex-wrap">
              <Button onClick={handleCreateBuild}>Create Build</Button>
              {buildId && <Badge variant="outline">Build: {buildId}</Badge>}
            </div>
            <Input value={idempotencyKey} onChange={(e) => setIdempotencyKey(e.target.value)} placeholder="Idempotency key" />
            <Input value={checkpointReason} onChange={(e) => setCheckpointReason(e.target.value)} placeholder="Checkpoint reason" />
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleIdempotentCheckpoint} disabled={!buildId}>Create Idempotent Checkpoint</Button>
              <Button variant="outline" onClick={handleSloSummary}>Fetch SLO Summary</Button>
            </div>
            {checkpointResult && <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(checkpointResult, null, 2)}</pre>}
            {sloSummary && <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(sloSummary, null, 2)}</pre>}
          </CardContent>
        </Card>

        <Card className="glass">
          <CardHeader>
            <CardTitle>Week 14-16: Release Checklist, Rollback Drill, Go/No-Go</CardTitle>
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
            <Input value={rollbackDuration} onChange={(e) => setRollbackDuration(e.target.value)} placeholder="Rollback duration minutes" />
            <Textarea value={rollbackIssues} onChange={(e) => setRollbackIssues(e.target.value)} placeholder="Rollback issues (comma or newline separated)" className="min-h-16" />
            <Button onClick={handleChecklistAndDecision}>Apply Checklist + Rollback + Decide Go/No-Go</Button>
            {decisionResult && <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">{JSON.stringify(decisionResult, null, 2)}</pre>}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default ProgramOps;
