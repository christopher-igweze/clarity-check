import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Shield, ArrowRight, Loader2 } from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import {
  BUILD_CONTROL_PLANE_ENABLED,
  createBuildRun,
  getLimits,
  runPrimer,
  startAudit,
  TIER1_ENABLED,
} from "@/lib/api";
import { toast } from "@/hooks/use-toast";
import { RepoSelector } from "@/components/RepoSelector";

const SENSITIVE_OPTIONS: Array<{ value: "payments" | "pii" | "health" | "auth_secrets" | "none" | "not_sure"; label: string }> = [
  { value: "payments", label: "Payments" },
  { value: "pii", label: "PII / personal data" },
  { value: "health", label: "Health data" },
  { value: "auth_secrets", label: "Auth/secrets" },
  { value: "none", label: "None" },
  { value: "not_sure", label: "Not sure" },
];

const DEPLOYMENT_OPTIONS = [
  "Not deployed yet",
  "Vercel",
  "Netlify",
  "Render",
  "AWS",
  "GCP",
  "Azure",
  "Railway",
  "Fly.io",
  "Self-hosted",
];

const SCALE_OPTIONS = [
  "MVP / low traffic",
  "Early growth",
  "Expected rapid growth",
  "Enterprise / high traffic",
  "Not sure",
];

const NewScan = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const navState = location.state as { repoUrl?: string; vibePrompt?: string } | null;

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [primerLoading, setPrimerLoading] = useState(false);

  const [repoUrl, setRepoUrl] = useState(navState?.repoUrl || "");
  const [vibePrompt, setVibePrompt] = useState(navState?.vibePrompt || "");

  const [projectOrigin, setProjectOrigin] = useState<"inspired" | "external">("inspired");
  const [productSummary, setProductSummary] = useState("");
  const [targetUsers, setTargetUsers] = useState("");
  const [sensitiveData, setSensitiveData] = useState<Array<"payments" | "pii" | "health" | "auth_secrets" | "none" | "not_sure">>([]);
  const [mustNotBreakFlows, setMustNotBreakFlows] = useState<string[]>([]);
  const [customFlow, setCustomFlow] = useState("");
  const [deploymentTarget, setDeploymentTarget] = useState("");
  const [scaleExpectation, setScaleExpectation] = useState("");

  const [primer, setPrimer] = useState<{
    primer_json: Record<string, unknown>;
    summary: string;
    repo_sha: string;
    confidence: number;
    failure_reason: string | null;
  } | null>(null);
  const [suggestedFlows, setSuggestedFlows] = useState<string[]>([]);
  const [limits, setLimits] = useState<{
    reports_remaining: number;
    reports_limit: number;
    project_count: number;
    project_limit: number;
    loc_cap: number;
  } | null>(null);

  useEffect(() => {
    if (!navState?.repoUrl) return;
    setRepoUrl(navState.repoUrl);
  }, [navState?.repoUrl]);

  useEffect(() => {
    if (!user) return;
    getLimits()
      .then((data) => {
        setLimits({
          reports_remaining: data.reports_remaining,
          reports_limit: data.reports_limit,
          project_count: data.project_count,
          project_limit: data.project_limit,
          loc_cap: data.loc_cap,
        });
      })
      .catch(() => {
        // Keep UI usable even if limits endpoint is temporarily unavailable.
      });
  }, [user]);

  const canNext = useMemo(() => {
    if (step === 1) return Boolean(repoUrl.trim());
    if (step === 2) return productSummary.trim().length >= 3 && targetUsers.trim().length >= 2;
    if (step === 3) return sensitiveData.length > 0;
    if (step === 4) return mustNotBreakFlows.length > 0;
    if (step === 5) return Boolean(deploymentTarget && scaleExpectation);
    return false;
  }, [step, repoUrl, productSummary, targetUsers, sensitiveData, mustNotBreakFlows, deploymentTarget, scaleExpectation]);

  const ensurePrimer = async () => {
    if (!repoUrl.trim() || primer || primerLoading) return;
    setPrimerLoading(true);
    try {
      const data = await runPrimer({ repoUrl: repoUrl.trim() });
      setPrimer(data.primer);
      setSuggestedFlows(data.suggested_flows || []);
      setMustNotBreakFlows((prev) => (prev.length > 0 ? prev : (data.suggested_flows || []).slice(0, 2)));
    } catch (error) {
      const message = error instanceof Error ? error.message : "Primer failed";
      setPrimer({
        primer_json: {},
        summary: "Primer fallback path activated. Intake still required.",
        repo_sha: "",
        confidence: 35,
        failure_reason: message,
      });
      setSuggestedFlows([]);
      toast({
        title: "Primer fallback",
        description: "Could not fully extract repo context. Continuing with manual intake.",
      });
    } finally {
      setPrimerLoading(false);
    }
  };

  const toggleSensitive = (value: (typeof SENSITIVE_OPTIONS)[number]["value"]) => {
    setSensitiveData((prev) => {
      if (value === "none") return prev.includes("none") ? [] : ["none"];
      if (value === "not_sure") return prev.includes("not_sure") ? [] : ["not_sure"];
      const cleaned = prev.filter((item) => item !== "none" && item !== "not_sure");
      return cleaned.includes(value) ? cleaned.filter((item) => item !== value) : [...cleaned, value];
    });
  };

  const toggleFlow = (flow: string) => {
    setMustNotBreakFlows((prev) => (prev.includes(flow) ? prev.filter((f) => f !== flow) : [...prev, flow]));
  };

  const addCustomFlow = () => {
    const value = customFlow.trim();
    if (!value) return;
    if (!mustNotBreakFlows.includes(value)) {
      setMustNotBreakFlows((prev) => [...prev, value]);
    }
    setCustomFlow("");
  };

  const goNext = async () => {
    if (!canNext) return;
    if (step === 1) {
      await ensurePrimer();
    }
    setStep((s) => Math.min(5, s + 1));
  };

  const handleStartScan = async () => {
    if (!repoUrl.trim() || !user || !canNext) return;
    setLoading(true);

    try {
      if (BUILD_CONTROL_PLANE_ENABLED) {
        try {
          const objective = `Audit ${repoUrl.trim()} for product risk and reliability`;
          const build = await createBuildRun({
            repoUrl: repoUrl.trim(),
            objective,
            metadata: {
              scan_mode: "autonomous",
              fallback_scan_mode: "deterministic",
              project_intake: {
                project_origin: projectOrigin,
                product_summary: productSummary.trim(),
                target_users: targetUsers.trim(),
                sensitive_data: sensitiveData,
                must_not_break_flows: mustNotBreakFlows,
                deployment_target: deploymentTarget,
                scale_expectation: scaleExpectation,
              },
              primer_summary: primer?.summary || null,
              primer_confidence: primer?.confidence ?? null,
            },
          });
          navigate("/scan/live", {
            state: {
              buildId: build.buildId,
              repoUrl: repoUrl.trim(),
            },
          });
          return;
        } catch {
          // Keep deterministic scan fallback available for resilience.
        }
      }

      const { scanId, quotaRemaining } = await startAudit({
        repoUrl: repoUrl.trim(),
        vibePrompt: vibePrompt || undefined,
        primer: primer || undefined,
        projectIntake: {
          project_origin: projectOrigin,
          product_summary: productSummary.trim(),
          target_users: targetUsers.trim(),
          sensitive_data: sensitiveData,
          must_not_break_flows: mustNotBreakFlows,
          deployment_target: deploymentTarget,
          scale_expectation: scaleExpectation,
        },
      });

      navigate("/scan/live", {
        state: {
          scanId,
          repoUrl: repoUrl.trim(),
          quotaRemaining,
        },
      });
    } catch (err) {
      const code = (err as { code?: string })?.code;
      if (code === "onboarding_required") {
        toast({
          title: "Onboarding required",
          description: "Complete onboarding before starting a scan.",
          variant: "destructive",
        });
        navigate("/onboarding/org");
        return;
      }
      if (code === "limit_reports_exceeded") {
        toast({
          title: "Monthly scan limit reached",
          description: "You have used all free reports this month. Your quota resets next UTC month.",
          variant: "destructive",
        });
        return;
      }
      if (code === "limit_projects_exceeded") {
        toast({
          title: "Project cap reached",
          description: "Free tier supports up to 3 projects. Reuse an existing project or wait to upgrade.",
          variant: "destructive",
        });
        return;
      }
      if (code === "limit_loc_exceeded") {
        toast({
          title: "Repository too large for free tier",
          description: "This repository exceeds the 50k LOC free-tier cap.",
          variant: "destructive",
        });
        return;
      }
      toast({
        title: "Error",
        description: err instanceof Error ? err.message : "Failed to start audit. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-pattern opacity-40 pointer-events-none" />

      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-5xl mx-auto">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/dashboard")}>
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Vibe</span>
            <span className="text-foreground">2Prod</span>
          </span>
        </div>
        <div className="text-right">
          <span className="text-xs text-muted-foreground block">Project intake step {step}/5</span>
          {limits && (
            <span className="text-[11px] text-muted-foreground">
              Free reports left: {limits.reports_remaining}/{limits.reports_limit}
            </span>
          )}
        </div>
      </nav>

      <main className="relative z-10 max-w-3xl mx-auto px-6 pt-10 pb-20">
        <h1 className="text-3xl font-bold mb-2">New Audit</h1>
        <p className="text-muted-foreground mb-8">
          {TIER1_ENABLED
            ? "Tier 1 runs a deterministic scan and assistant report. Complete this 5-step intake so findings are prioritized for your product goals."
            : "Complete this 5-step intake so Hermes can audit against your real product goals."}
        </p>
        {TIER1_ENABLED && limits && (
          <div className="mb-6 rounded-lg border border-border bg-secondary/40 px-4 py-3 text-xs text-muted-foreground">
            Free tier limits: {limits.reports_remaining} reports remaining this month, {limits.project_count}/{limits.project_limit} projects used, LOC cap {limits.loc_cap.toLocaleString()}.
          </div>
        )}

        <div className="space-y-6">
          {step === 1 && (
            <div className="space-y-5">
              <RepoSelector value={repoUrl} onChange={setRepoUrl} />
              <div>
                <label className="text-sm font-medium mb-2 block">Project origin</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button
                    onClick={() => setProjectOrigin("inspired")}
                    className={`rounded-xl p-4 border text-left ${projectOrigin === "inspired" ? "border-primary bg-primary/10" : "border-border"}`}
                  >
                    Inspired by me
                  </button>
                  <button
                    onClick={() => setProjectOrigin("external")}
                    className={`rounded-xl p-4 border text-left ${projectOrigin === "external" ? "border-primary bg-primary/10" : "border-border"}`}
                  >
                    External project
                  </button>
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">
                  Vibe prompt <span className="text-muted-foreground">(optional)</span>
                </label>
                <Textarea
                  value={vibePrompt}
                  onChange={(e) => setVibePrompt(e.target.value)}
                  placeholder="Original prompt or quick context"
                  className="bg-secondary border-border min-h-[90px]"
                />
              </div>

              {primer && (
                <div className="glass rounded-xl p-4">
                  <p className="text-xs text-muted-foreground mb-1">Primer summary</p>
                  <p className="text-sm">{primer.summary}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    Confidence: {primer.confidence}/100
                    {primer.failure_reason ? ` • fallback: ${primer.failure_reason}` : ""}
                  </p>
                </div>
              )}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <div>
                <label className="text-sm font-medium mb-2 block">What does the product do?</label>
                <Textarea
                  value={productSummary}
                  onChange={(e) => setProductSummary(e.target.value)}
                  placeholder="Short summary of the core product"
                  className="bg-secondary border-border min-h-[110px]"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Who is it for?</label>
                <Input
                  value={targetUsers}
                  onChange={(e) => setTargetUsers(e.target.value)}
                  placeholder="Target users (founders, recruiters, SMB teams, etc.)"
                  className="bg-secondary border-border"
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-3">
              <label className="text-sm font-medium block">Sensitive data in this project</label>
              <div className="flex flex-wrap gap-2">
                {SENSITIVE_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => toggleSensitive(opt.value)}
                    className={`rounded-full px-3 py-1 text-xs border ${
                      sensitiveData.includes(opt.value) ? "border-primary bg-primary/10" : "border-border"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-4">
              <label className="text-sm font-medium block">Top 3 must-not-break user flows</label>
              {suggestedFlows.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs text-muted-foreground">Primer suggestions</p>
                  <div className="flex flex-wrap gap-2">
                    {suggestedFlows.map((flow) => (
                      <button
                        key={flow}
                        onClick={() => toggleFlow(flow)}
                        className={`rounded-full px-3 py-1 text-xs border ${
                          mustNotBreakFlows.includes(flow) ? "border-primary bg-primary/10" : "border-border"
                        }`}
                      >
                        {flow}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <Input
                  value={customFlow}
                  onChange={(e) => setCustomFlow(e.target.value)}
                  placeholder="Add custom flow"
                  className="bg-secondary border-border"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addCustomFlow();
                    }
                  }}
                />
                <Button variant="outline" onClick={addCustomFlow}>Add</Button>
              </div>
              <div className="flex flex-wrap gap-2">
                {mustNotBreakFlows.map((flow) => (
                  <span key={flow} className="rounded-full px-3 py-1 text-xs bg-primary/10 border border-primary/30">
                    {flow}
                  </span>
                ))}
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-5">
              <div>
                <label className="text-sm font-medium mb-2 block">Deployment target</label>
                <select
                  value={deploymentTarget}
                  onChange={(e) => setDeploymentTarget(e.target.value)}
                  className="w-full bg-secondary border border-border rounded-md px-3 py-2 text-sm"
                >
                  <option value="">Select deployment target</option>
                  {DEPLOYMENT_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Scale expectation</label>
                <select
                  value={scaleExpectation}
                  onChange={(e) => setScaleExpectation(e.target.value)}
                  className="w-full bg-secondary border border-border rounded-md px-3 py-2 text-sm"
                >
                  <option value="">Select scale expectation</option>
                  {SCALE_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              </div>
            </div>
          )}

          <div className="flex justify-between pt-3">
            <Button variant="outline" onClick={() => setStep((s) => Math.max(1, s - 1))} disabled={step === 1 || loading || primerLoading}>
              Back
            </Button>

            {step < 5 ? (
              <Button onClick={goNext} disabled={!canNext || loading || primerLoading}>
                {primerLoading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Running primer...</> : "Next"}
              </Button>
            ) : (
              <Button
                onClick={handleStartScan}
                disabled={!canNext || loading || primerLoading}
                className="neon-glow-green text-base font-semibold"
              >
                {loading ? "Creating audit..." : (TIER1_ENABLED ? "Start Tier 1 scan" : "Start deep audit")}
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default NewScan;
