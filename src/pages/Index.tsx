import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Shield, Zap, GitPullRequest, ArrowRight, Terminal, Bug, Lock, TrendingUp } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const steps = [
  {
    icon: GitPullRequest,
    title: "Connect",
    description: "Paste your GitHub repo URL. Our AI reads every file in one pass.",
    color: "text-neon-green",
  },
  {
    icon: Terminal,
    title: "Scan",
    description: "5-agent swarm audits security, reliability & scalability. Deep Probe actually runs your code.",
    color: "text-neon-cyan",
  },
  {
    icon: Zap,
    title: "Fix",
    description: "One-click fixes with verified tests. Auto-PR to your repo. No rewrites.",
    color: "text-neon-purple",
  },
];

const stats = [
  { label: "Security Issues", icon: Lock, value: "Hardcoded keys, exposed secrets" },
  { label: "Reliability", icon: Bug, value: "Crash-on-startup, failing tests" },
  { label: "Scalability", icon: TrendingUp, value: "Architecture debt, missing patterns" },
];

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.15, duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] as [number, number, number, number] },
  }),
};

const Index = () => {
  const { user, signInWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleCTA = () => {
    if (user) {
      navigate("/dashboard");
    } else {
      signInWithGoogle();
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Grid pattern background */}
      <div className="fixed inset-0 grid-pattern opacity-40 pointer-events-none" />

      {/* Radial gradient overlay */}
      <div className="fixed inset-0 pointer-events-none" style={{
        background: "radial-gradient(ellipse 80% 50% at 50% -20%, hsl(160 100% 50% / 0.08), transparent)"
      }} />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Vibe</span>
            <span className="text-foreground">2Prod</span>
          </span>
        </div>
        {user ? (
          <Button variant="outline" className="border-primary/30 text-primary hover:bg-primary/10" onClick={() => navigate("/dashboard")}>
            Dashboard
          </Button>
        ) : (
          <Button variant="outline" className="border-primary/30 text-primary hover:bg-primary/10" onClick={signInWithGoogle}>
            Sign in with Google
          </Button>
        )}
      </nav>

      {/* Hero */}
      <main className="relative z-10 max-w-5xl mx-auto px-6 pt-20 pb-32">
        <motion.div
          className="text-center"
          initial="hidden"
          animate="visible"
          variants={fadeUp}
          custom={0}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-sm text-muted-foreground mb-8">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse-neon" />
            5-Agent AI Swarm • OpenRouter Powered
          </div>

          <h1 className="text-5xl sm:text-7xl font-bold leading-[1.05] tracking-tight mb-6">
            Is your AI app ready
            <br />
            <span className="text-gradient-neon">for real users?</span>
          </h1>

          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
            We don't just read your code — we <strong className="text-foreground">run it</strong>.
            Surface hardcoded secrets, crashing builds, and failing tests.
            Then fix them with verified PRs.
          </p>

          <motion.div variants={fadeUp} custom={1} className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button size="lg" className="text-base px-8 py-6 font-semibold neon-glow-green" onClick={handleCTA}>
              Scan Your Repo Free
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
            <Button variant="ghost" size="lg" className="text-base text-muted-foreground hover:text-foreground">
              See how it works
            </Button>
          </motion.div>
        </motion.div>

        {/* 3-Step Flow */}
        <motion.section
          className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-6"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              variants={fadeUp}
              custom={i}
              className="glass rounded-xl p-8 relative group hover:border-primary/30 transition-colors"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                  <step.icon className={`w-5 h-5 ${step.color}`} />
                </div>
                <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
                  Step {i + 1}
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{step.description}</p>
            </motion.div>
          ))}
        </motion.section>

        {/* What We Catch */}
        <motion.section
          className="mt-32 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
        >
          <motion.div variants={fadeUp} custom={0}>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Static analysis <span className="text-muted-foreground line-through">guesses</span>.
              <br />
              Deep Probe <span className="text-gradient-neon">proves</span>.
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto mb-12">
              Our Tier 2 scan spins up a sandbox and actually runs your app.
              If it crashes, we show you the stack trace — not a suggestion.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                variants={fadeUp}
                custom={i + 1}
                className="glass rounded-xl p-6 text-left"
              >
                <stat.icon className="w-8 h-8 text-neon-orange mb-4" />
                <h4 className="font-semibold text-lg mb-1">{stat.label}</h4>
                <p className="text-sm text-muted-foreground">{stat.value}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Terminal Preview */}
        <motion.section
          className="mt-32"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={fadeUp}
          custom={0}
        >
          <div className="glass-strong rounded-xl overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-border">
              <div className="w-3 h-3 rounded-full bg-neon-red/80" />
              <div className="w-3 h-3 rounded-full bg-neon-orange/80" />
              <div className="w-3 h-3 rounded-full bg-neon-green/80" />
              <span className="ml-3 text-xs font-mono text-muted-foreground">the-thinking-stream</span>
            </div>
            <div className="p-6 font-mono text-sm space-y-2">
              <p><span className="text-neon-cyan">▸ Agent_Visionary:</span> <span className="text-muted-foreground">Generating project charter from vibe prompt...</span></p>
              <p><span className="text-neon-green">▸ Agent_Auditor:</span> <span className="text-muted-foreground">Ingesting 247 files via Claude 4.5 Opus...</span></p>
              <p><span className="text-neon-green">▸ Agent_Auditor:</span> <span className="text-muted-foreground">Found hardcoded Stripe key in src/config.ts:42</span> <span className="text-neon-red">⚠ CRITICAL</span></p>
              <p><span className="text-neon-red">▸ Agent_Security:</span> <span className="text-muted-foreground">🛡️ Confirmed: sk_live key exposed. SOC 2 violation.</span></p>
              <p><span className="text-neon-purple">▸ Agent_Architect:</span> <span className="text-muted-foreground">Designing refactoring plan via GPT-5.2...</span></p>
              <p><span className="text-neon-orange">▸ Agent_SRE:</span> <span className="text-muted-foreground">Entering Daytona sandbox... running npm test...</span></p>
              <p><span className="text-neon-orange">▸ Agent_SRE:</span> <span className="text-muted-foreground">12 of 20 tests failing.</span> <span className="text-neon-red">⚠ HIGH</span></p>
              <p><span className="text-primary">▸ Agent_Educator:</span> <span className="text-muted-foreground">Generating "Why This Matters" cards...</span></p>
              <p className="text-primary animate-pulse-neon">█</p>
            </div>
          </div>
        </motion.section>

        {/* Bottom CTA */}
        <motion.section
          className="mt-32 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          variants={fadeUp}
          custom={0}
        >
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Stop shipping <span className="text-gradient-purple">hallucinated code</span>.
          </h2>
          <p className="text-muted-foreground max-w-lg mx-auto mb-8">
            Connect your repo. Get a Production Health Score. Fix issues with verified PRs.
          </p>
          <Button size="lg" className="text-base px-8 py-6 font-semibold neon-glow-green" onClick={handleCTA}>
            Scan Your Repo Free
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </motion.section>

        {/* Footer */}
        <footer className="mt-32 pt-8 border-t border-border text-center">
          <p className="text-xs text-muted-foreground">
            Powered by OpenRouter • Gemini 3 Pro • Claude 4.5 Opus • GPT-5.2 • DeepSeek V3.2 • OpenHands SDK • Daytona
          </p>
        </footer>
      </main>
    </div>
  );
};

export default Index;
