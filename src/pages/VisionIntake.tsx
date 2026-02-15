import { useState, useRef, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Shield, Send, ArrowRight, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { streamVisionIntake } from "@/lib/api";

interface Message {
  role: "assistant" | "user";
  content: string;
}

const VisionIntake = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { repoUrl: string; vibePrompt?: string } | null;

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [questionCount, setQuestionCount] = useState(0);
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages]);

  // Start conversation on mount
  useEffect(() => {
    if (!state?.repoUrl) return;
    sendToAgent([{
      role: "user",
      content: `I'm submitting my repository for a production readiness audit. Here's my repo: ${state.repoUrl}${state.vibePrompt ? `\n\nMy original vibe prompt was: "${state.vibePrompt}"` : ""}\n\nPlease interview me to understand my project's intent before the scan begins.`,
    }]);
  }, []);

  const sendToAgent = async (history: { role: string; content: string }[]) => {
    setStreaming(true);
    let accumulated = "";

    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    await streamVisionIntake({
      messages: history,
      repoUrl: state?.repoUrl || "",
      vibePrompt: state?.vibePrompt,
      onDelta: (chunk) => {
        accumulated += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "assistant", content: accumulated };
          return updated;
        });
      },
      onDone: () => {
        setStreaming(false);
        setQuestionCount((q) => q + 1);
      },
    });
  };

  const handleSend = () => {
    if (!input.trim() || streaming) return;
    const userMsg: Message = { role: "user", content: input.trim() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    sendToAgent(newMessages.map((m) => ({ role: m.role, content: m.content })));
  };

  const handleProceedToScan = () => {
    // Extract charter from conversation
    const charter = messages.map((m) => `${m.role}: ${m.content}`).join("\n");
    navigate("/scan/new", {
      state: {
        repoUrl: state?.repoUrl,
        vibePrompt: state?.vibePrompt,
        projectCharter: charter,
      },
    });
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden flex flex-col">
      <div className="fixed inset-0 grid-pattern opacity-40 pointer-events-none" />

      <nav className="relative z-10 flex items-center justify-between px-6 py-5 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("/dashboard")}>
          <Shield className="w-7 h-7 text-primary" />
          <span className="text-lg font-bold tracking-tight">
            <span className="text-gradient-neon">Vibe</span>
            <span className="text-foreground">2Prod</span>
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Bot className="w-4 h-4 text-neon-cyan" />
          <span>Agent_Visionary • Gemini 3 Pro</span>
        </div>
      </nav>

      <main className="relative z-10 flex-1 flex flex-col max-w-3xl mx-auto w-full px-6 pb-6">
        <div className="mb-4">
          <h1 className="text-2xl font-bold">Vision Intake</h1>
          <p className="text-sm text-muted-foreground">
            Agent_Visionary is interviewing you to understand your project's intent before scanning.
          </p>
        </div>

        {/* Chat Area */}
        <div ref={chatRef} className="flex-1 overflow-y-auto space-y-4 mb-4 min-h-[400px] max-h-[60vh]">
          {messages.filter((m, i) => !(i === 0 && m.role === "user")).map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-4 h-4 text-neon-cyan" />
                </div>
              )}
              <div className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "glass"
              }`}>
                {msg.content || (
                  <span className="text-muted-foreground animate-pulse-neon">Thinking...</span>
                )}
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0 mt-1">
                  <User className="w-4 h-4 text-primary" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="glass-strong rounded-xl p-4">
          {questionCount >= 3 && !streaming && (
            <div className="mb-3 flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                ✓ Vision intake complete. Ready to proceed.
              </span>
              <Button size="sm" className="neon-glow-green" onClick={handleProceedToScan}>
                Proceed to Scan <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          )}
          <div className="flex gap-3">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Answer Agent_Visionary's questions..."
              className="min-h-[44px] max-h-[120px] resize-none bg-secondary border-border"
              disabled={streaming}
            />
            <Button
              size="icon"
              onClick={handleSend}
              disabled={!input.trim() || streaming}
              className="shrink-0 h-[44px] w-[44px]"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default VisionIntake;
