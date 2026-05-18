import { useJobStream } from "../lib/ws";
import ProgressBar from "./ProgressBar";
import { cancelJob } from "../lib/api";
import { X, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import clsx from "clsx";

export default function QueuePanel({ compact = false }: { compact?: boolean }) {
  const jobs = useJobStream();
  const list = Object.values(jobs).sort((a, b) => b.created_at - a.created_at);
  const active = list.filter((j) => j.status === "running" || j.status === "queued");
  if (compact && !active.length) {
    return <div className="text-xs text-ink-400 py-4 text-center">No jobs running</div>;
  }
  const shown = compact ? active.slice(0, 5) : list;

  return (
    <div className="space-y-2">
      {shown.map((j) => (
        <div key={j.id} className="bg-bg-700/40 rounded-xl p-3 border border-white/[0.04]">
          <div className="flex items-center justify-between gap-2">
            <div className="text-sm truncate flex items-center gap-2">
              <StatusIcon status={j.status} />
              <span className="truncate">{j.params.prompt || "(no prompt)"}</span>
            </div>
            {(j.status === "queued" || j.status === "running") && (
              <button onClick={() => cancelJob(j.id)}
                      className="text-ink-400 hover:text-red-400 transition-colors">
                <X size={14} />
              </button>
            )}
          </div>
          {j.status === "running" && (
            <div className="mt-2.5"><ProgressBar value={j.progress * 100} /></div>
          )}
          {j.status === "error" && (
            <div className="text-[11px] text-red-400 mt-1.5 truncate">{j.error}</div>
          )}
        </div>
      ))}
    </div>
  );
}

function StatusIcon({ status }: { status: string }) {
  const map: any = {
    queued:    <div className="w-2 h-2 rounded-full bg-ink-400" />,
    running:   <Loader2 size={12} className="animate-spin text-accent-glow" />,
    done:      <CheckCircle2 size={12} className="text-success" />,
    error:     <AlertCircle size={12} className="text-danger" />,
    cancelled: <X size={12} className="text-ink-400" />,
  };
  return map[status] ?? null;
}
