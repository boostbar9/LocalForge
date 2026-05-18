import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Generate from "./pages/Generate";
import VideoPro from "./pages/VideoPro";
import Gallery from "./pages/Gallery";
import Models from "./pages/Models";
import Queue from "./pages/Queue";
import Settings from "./pages/Settings";
import Welcome from "./pages/Welcome";
import { useBackend } from "./lib/api";
import { Sparkles } from "lucide-react";

export default function App() {
  const { ready, error } = useBackend();

  if (!ready) {
    return (
      <div className="h-full grid place-items-center">
        <div className="card p-10 text-center max-w-md fade-up">
          <div className="relative inline-block mb-4">
            <Sparkles className="text-accent-glow" size={36} />
            <div className="absolute -inset-3 bg-accent/20 rounded-full blur-xl -z-10 animate-pulse" />
          </div>
          <div className="text-2xl font-semibold mb-2">Starting LocalForge</div>
          <div className="text-ink-400 text-sm">
            {error ? <span className="text-red-400">{error}</span> : "Booting local AI engine…"}
          </div>
          {!error && (
            <div className="mt-5 h-1 bg-bg-700 rounded-full overflow-hidden">
              <div className="h-full shimmer" />
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/generate" replace />} />
          <Route path="/welcome" element={<Welcome />} />
          <Route path="/generate" element={<Generate />} />
          <Route path="/video" element={<VideoPro />} />
          <Route path="/gallery" element={<Gallery />} />
          <Route path="/models" element={<Models />} />
          <Route path="/queue" element={<Queue />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}
