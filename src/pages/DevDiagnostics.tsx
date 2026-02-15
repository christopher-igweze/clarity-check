import { useEffect, useMemo, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { getClerkToken } from "@/integrations/clerk/tokenStore";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  const parts = token.split(".");
  if (parts.length < 2) return null;
  try {
    const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padded = payload + "===".slice((payload.length + 3) % 4);
    const json = atob(padded);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

const DevDiagnostics = () => {
  const { user } = useAuth();
  const [tokenPayload, setTokenPayload] = useState<Record<string, unknown> | null>(null);
  const [tokenErr, setTokenErr] = useState<string | null>(null);
  const [dbResult, setDbResult] = useState<unknown>(null);
  const [dbErr, setDbErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const expectedSub = user?.id || null;

  const fetchToken = async () => {
    setTokenErr(null);
    setTokenPayload(null);
    try {
      const token = await getClerkToken();
      if (!token) throw new Error("No token returned from Clerk.");
      const payload = decodeJwtPayload(token);
      if (!payload) throw new Error("Failed to decode JWT payload.");
      setTokenPayload(payload);
    } catch (e) {
      setTokenErr(e instanceof Error ? e.message : String(e));
    }
  };

  const runDbCheck = async () => {
    setDbErr(null);
    setDbResult(null);
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("user_id", expectedSub || "")
        .limit(1);

      if (error) throw error;
      setDbResult(data);
    } catch (e) {
      setDbErr(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  };

  const summary = useMemo(() => {
    const sub = (tokenPayload?.sub as string | undefined) || null;
    const role = (tokenPayload?.role as string | undefined) || null;
    const aud = tokenPayload?.aud ?? null;
    return { sub, role, aud };
  }, [tokenPayload]);

  useEffect(() => {
    // Auto-run on load for convenience.
    fetchToken().catch(() => {});
  }, []);

  if (!import.meta.env.DEV) return null;

  return (
    <div className="min-h-screen bg-background text-foreground px-6 py-10">
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold">Dev Diagnostics</h1>

        <div className="glass rounded-xl p-6 space-y-3">
          <div className="text-sm text-muted-foreground">App user</div>
          <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">
            {JSON.stringify({ id: user?.id, email: user?.email }, null, 2)}
          </pre>
        </div>

        <div className="glass rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-sm text-muted-foreground">Clerk JWT (decoded claims)</div>
              <div className="text-xs text-muted-foreground">
                Expect: <code className="font-mono">sub</code> equals your Clerk user id, and ideally <code className="font-mono">role</code> is <code className="font-mono">authenticated</code>.
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={fetchToken}>
              Refresh Token
            </Button>
          </div>

          {tokenErr ? (
            <div className="text-sm text-destructive">{tokenErr}</div>
          ) : (
            <>
              <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">
                {JSON.stringify(summary, null, 2)}
              </pre>
              <details className="text-xs">
                <summary className="cursor-pointer text-muted-foreground">Full claims</summary>
                <pre className="mt-2 bg-secondary/40 rounded-lg p-3 overflow-auto">
                  {JSON.stringify(tokenPayload, null, 2)}
                </pre>
              </details>
            </>
          )}
        </div>

        <div className="glass rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="text-sm text-muted-foreground">Supabase RLS check</div>
              <div className="text-xs text-muted-foreground">
                Runs: <code className="font-mono">select * from profiles where user_id = &lt;sub&gt;</code>
              </div>
            </div>
            <Button size="sm" onClick={runDbCheck} disabled={loading || !expectedSub}>
              {loading ? "Running..." : "Run DB Check"}
            </Button>
          </div>

          {dbErr ? (
            <div className="text-sm text-destructive">{dbErr}</div>
          ) : (
            <pre className="text-xs bg-secondary/40 rounded-lg p-3 overflow-auto">
              {JSON.stringify(dbResult, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
};

export default DevDiagnostics;

