import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import Dashboard from "./pages/Dashboard";
import NewScan from "./pages/NewScan";
import ScanLive from "./pages/ScanLive";
import Report from "./pages/Report";
import VisionIntake from "./pages/VisionIntake";
import ProjectDetail from "./pages/ProjectDetail";
import Settings from "./pages/Settings";
import SignInPage from "./pages/SignInPage";
import SignUpPage from "./pages/SignUpPage";
import DevDiagnostics from "./pages/DevDiagnostics";
import NotFound from "./pages/NotFound";
import OrgOnboarding from "./pages/OrgOnboarding";
import ProgramOps from "./pages/ProgramOps";
import ReleaseReadiness from "./pages/ReleaseReadiness";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/sign-in/*" element={<SignInPage />} />
            <Route path="/sign-up/*" element={<SignUpPage />} />
            <Route path="/dev/diag" element={<ProtectedRoute><DevDiagnostics /></ProtectedRoute>} />
            <Route path="/onboarding/org" element={<ProtectedRoute><OrgOnboarding /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/scan/new" element={<ProtectedRoute><NewScan /></ProtectedRoute>} />
            <Route path="/scan/live" element={<ProtectedRoute><ScanLive /></ProtectedRoute>} />
            <Route path="/program-ops" element={<ProtectedRoute><ProgramOps /></ProtectedRoute>} />
            <Route path="/release-readiness" element={<ProtectedRoute><ReleaseReadiness /></ProtectedRoute>} />
            <Route path="/report/:id" element={<ProtectedRoute><Report /></ProtectedRoute>} />
            <Route path="/project/:id" element={<ProtectedRoute><ProjectDetail /></ProtectedRoute>} />
            <Route path="/vision-intake" element={<ProtectedRoute><VisionIntake /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
