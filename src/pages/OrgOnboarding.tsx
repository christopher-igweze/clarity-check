import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { getClerkToken } from "@/integrations/clerk/tokenStore";
import { toast } from "@/hooks/use-toast";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const API_URL = `${API_BASE_URL}/api`;

const TOOL_TAG_SUGGESTIONS = [
  "React",
  "Next.js",
  "TypeScript",
  "Node.js",
  "FastAPI",
  "Python",
  "Supabase",
  "Clerk",
  "Firebase",
  "PostgreSQL",
  "Prisma",
  "Stripe",
  "Vercel",
  "AWS",
  "Docker",
  "Tailwind",
  "Cursor",
  "v0",
  "Bolt",
  "Lovable",
];

const ACQUISITION_OPTIONS = [
  { value: "x_twitter", label: "X / Twitter" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "tiktok", label: "TikTok" },
  { value: "youtube", label: "YouTube" },
  { value: "reddit", label: "Reddit" },
  { value: "discord", label: "Discord" },
  { value: "product_hunt", label: "Product Hunt" },
  { value: "indie_hackers", label: "Indie Hackers" },
  { value: "hacker_news", label: "Hacker News" },
  { value: "google_search", label: "Google / Search" },
  { value: "newsletter_email", label: "Newsletter / Email" },
  { value: "referral", label: "Friend / Referral" },
  { value: "founder_begged_me", label: "Founder begged me to try it" },
  { value: "other", label: "Other" },
];

const CODING_AGENT_PROVIDER_OPTIONS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google" },
] as const;

const CODING_AGENT_MODEL_OPTIONS: Record<string, string[]> = {
  openai: ["openai/gpt-5.2-codex", "openai/gpt-5.2-chat"],
  anthropic: ["anthropic/claude-sonnet-4.5", "anthropic/claude-opus-4.1"],
  google: ["google/gemini-2.5-pro", "google/gemini-2.5-flash"],
};

export default function OrgOnboarding() {
  const navigate = useNavigate();
  const { user, refreshProfile } = useAuth();

  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);
  const [customTag, setCustomTag] = useState("");

  const [technicalLevel, setTechnicalLevel] = useState<"founder" | "vibe_coder" | "engineer" | "">("");
  const [explanationStyle, setExplanationStyle] = useState<"teach_me" | "just_steps" | "cto_brief" | "">("");
  const [shippingPosture, setShippingPosture] = useState<"ship_fast" | "balanced" | "production_first">("balanced");
  const [toolTags, setToolTags] = useState<string[]>([]);
  const [acquisitionSource, setAcquisitionSource] = useState("");
  const [acquisitionOther, setAcquisitionOther] = useState("");
  const [codingAgentProvider, setCodingAgentProvider] = useState<"openai" | "anthropic" | "google" | "">("");
  const [codingAgentModel, setCodingAgentModel] = useState("");

  useEffect(() => {
    if (!codingAgentProvider) {
      setCodingAgentModel("");
      return;
    }
    const options = CODING_AGENT_MODEL_OPTIONS[codingAgentProvider] || [];
    if (!options.includes(codingAgentModel)) {
      setCodingAgentModel(options[0] || "");
    }
  }, [codingAgentProvider, codingAgentModel]);

  const canGoNext = useMemo(() => {
    if (step === 1) return Boolean(technicalLevel);
    if (step === 2) return Boolean(explanationStyle);
    if (step === 3) return Boolean(shippingPosture);
    if (step === 4) {
      return Boolean(acquisitionSource) && Boolean(codingAgentProvider) && Boolean(codingAgentModel.trim());
    }
    return false;
  }, [step, technicalLevel, explanationStyle, shippingPosture, acquisitionSource, codingAgentProvider, codingAgentModel]);

  const toggleTag = (tag: string) => {
    setToolTags((prev) => (prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]));
  };

  const addCustomTag = () => {
    const value = customTag.trim();
    if (!value) return;
    if (!toolTags.includes(value)) {
      setToolTags((prev) => [...prev, value]);
    }
    setCustomTag("");
  };

  const submit = async () => {
    if (!user || !acquisitionSource) return;
    setSaving(true);
    try {
      const token = await getClerkToken();
      if (!token) throw new Error("Missing auth token.");

      const resp = await fetch(`${API_URL}/onboarding/org`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          technical_level: technicalLevel,
          explanation_style: explanationStyle,
          shipping_posture: shippingPosture,
          tool_tags: toolTags,
          acquisition_source: acquisitionSource,
          acquisition_other: acquisitionSource === "other" ? acquisitionOther : null,
          coding_agent_provider: codingAgentProvider,
          coding_agent_model: codingAgentModel,
        }),
      });

      if (!resp.ok) {
        const errorBody = await resp.text();
        throw new Error(errorBody || "Failed to save onboarding");
      }

      await refreshProfile();
      toast({ title: "Onboarding complete", description: "Hermes now has your defaults." });
      navigate("/dashboard");
    } catch (error) {
      toast({
        title: "Could not save onboarding",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 grid-pattern opacity-40 pointer-events-none" />

      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-4xl mx-auto">
        <div className="flex items-center gap-2">
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Vibe</span>
            <span className="text-foreground">2Prod</span>
          </span>
        </div>
        <span className="text-xs text-muted-foreground">Step {step} of 4</span>
      </nav>

      <main className="relative z-10 max-w-2xl mx-auto px-6 pt-8 pb-20">
        <Card className="glass-strong">
          <CardHeader>
            <CardTitle>Set Your Org Defaults</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {step === 1 && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">1. What best describes your technical level?</p>
                <div className="grid gap-2">
                  {[
                    { value: "founder", label: "Founder" },
                    { value: "vibe_coder", label: "Vibe coder" },
                    { value: "engineer", label: "Engineer" },
                  ].map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setTechnicalLevel(opt.value as typeof technicalLevel)}
                      className={`text-left rounded-lg px-4 py-3 border transition-colors ${
                        technicalLevel === opt.value ? "border-primary bg-primary/10" : "border-border hover:border-primary/40"
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">2. How should Hermes explain issues and fixes?</p>
                <div className="grid gap-2">
                  {[
                    { value: "teach_me", label: "Teach me (why + how)" },
                    { value: "just_steps", label: "Just steps (do this now)" },
                    { value: "cto_brief", label: "CTO brief (business risk first)" },
                  ].map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setExplanationStyle(opt.value as typeof explanationStyle)}
                      className={`text-left rounded-lg px-4 py-3 border transition-colors ${
                        explanationStyle === opt.value ? "border-primary bg-primary/10" : "border-border hover:border-primary/40"
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">3. What is your default shipping posture?</p>
                <div className="grid gap-2">
                  {[
                    { value: "ship_fast", label: "Ship fast" },
                    { value: "balanced", label: "Balanced" },
                    { value: "production_first", label: "Production-first" },
                  ].map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setShippingPosture(opt.value as typeof shippingPosture)}
                      className={`text-left rounded-lg px-4 py-3 border transition-colors ${
                        shippingPosture === opt.value ? "border-primary bg-primary/10" : "border-border hover:border-primary/40"
                      }`}
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-5">
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">4A. Tools you commonly use (optional but useful)</p>
                  <div className="flex flex-wrap gap-2">
                    {TOOL_TAG_SUGGESTIONS.map((tag) => (
                      <button
                        key={tag}
                        onClick={() => toggleTag(tag)}
                        className={`text-xs rounded-full px-3 py-1 border ${
                          toolTags.includes(tag) ? "border-primary bg-primary/10" : "border-border hover:border-primary/40"
                        }`}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Input
                      value={customTag}
                      onChange={(e) => setCustomTag(e.target.value)}
                      placeholder="Add custom tag"
                      className="bg-secondary border-border"
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          addCustomTag();
                        }
                      }}
                    />
                    <Button variant="outline" onClick={addCustomTag}>Add</Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">4B. How did you hear about us? (required)</p>
                  <select
                    value={acquisitionSource}
                    onChange={(e) => setAcquisitionSource(e.target.value)}
                    className="w-full bg-secondary border border-border rounded-md px-3 py-2 text-sm"
                  >
                    <option value="">Select one</option>
                    {ACQUISITION_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                  {acquisitionSource === "other" && (
                    <Input
                      value={acquisitionOther}
                      onChange={(e) => setAcquisitionOther(e.target.value)}
                      placeholder="Tell us where"
                      className="bg-secondary border-border"
                    />
                  )}
                </div>

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">4C. Which coding agent do you use? (required)</p>
                  <select
                    value={codingAgentProvider}
                    onChange={(e) => setCodingAgentProvider(e.target.value as typeof codingAgentProvider)}
                    className="w-full bg-secondary border border-border rounded-md px-3 py-2 text-sm"
                  >
                    <option value="">Select provider</option>
                    {CODING_AGENT_PROVIDER_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>

                  <select
                    value={codingAgentModel}
                    onChange={(e) => setCodingAgentModel(e.target.value)}
                    className="w-full bg-secondary border border-border rounded-md px-3 py-2 text-sm disabled:opacity-50"
                    disabled={!codingAgentProvider}
                  >
                    {!codingAgentProvider ? (
                      <option value="">Select provider first</option>
                    ) : (
                      (CODING_AGENT_MODEL_OPTIONS[codingAgentProvider] || []).map((model) => (
                        <option key={model} value={model}>{model}</option>
                      ))
                    )}
                  </select>
                </div>
              </div>
            )}

            <div className="flex justify-between pt-2">
              <Button
                variant="outline"
                onClick={() => setStep((s) => Math.max(1, s - 1))}
                disabled={step === 1 || saving}
              >
                Back
              </Button>

              {step < 4 ? (
                <Button onClick={() => setStep((s) => s + 1)} disabled={!canGoNext || saving}>
                  Next
                </Button>
              ) : (
                <Button onClick={submit} disabled={!canGoNext || saving}>
                  {saving ? "Saving..." : "Complete onboarding"}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
