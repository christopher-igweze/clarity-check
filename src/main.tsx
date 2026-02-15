import { createRoot } from "react-dom/client";
import { ClerkProvider } from "@clerk/clerk-react";
import App from "./App.tsx";
import "./index.css";

const clerkPublishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!clerkPublishableKey) {
  createRoot(document.getElementById("root")!).render(
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-6">
      <div className="max-w-lg glass rounded-xl p-8">
        <h1 className="text-xl font-semibold mb-2">Missing Clerk config</h1>
        <p className="text-sm text-muted-foreground">
          Set <code className="font-mono">VITE_CLERK_PUBLISHABLE_KEY</code> in <code className="font-mono">.env</code> and restart.
        </p>
      </div>
    </div>,
  );
} else {
  createRoot(document.getElementById("root")!).render(
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <App />
    </ClerkProvider>,
  );
}
