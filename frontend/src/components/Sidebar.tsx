import { NavLink } from "react-router-dom";
import { Wand2, Images, Boxes, ListChecks, Settings2, Sparkles, Film, ShieldCheck } from "lucide-react";
import clsx from "clsx";
import { useEffect, useState } from "react";
import { api } from "../lib/api";

const items = [
  { to: "/generate", label: "Generate", icon: Wand2 },
  { to: "/video", label: "Video Pro", icon: Film, pro: true },
  { to: "/gallery", label: "Gallery", icon: Images },
  { to: "/models", label: "Models", icon: Boxes },
  { to: "/queue", label: "Queue", icon: ListChecks },
  { to: "/settings", label: "Settings", icon: Settings2 },
];

export default function Sidebar() {
  const [backends, setBackends] = useState<any[]>([]);
  useEffect(() => {
    const tick = () => api<any>("/api/health").then((r) => setBackends(r.backends || [])).catch(() => {});
    tick();
    const id = setInterval(tick, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <aside className="w-64 shrink-0 bg-bg-800/40 border-r border-white/[0.05] flex flex-col backdrop-blur-xl">
      <div className="px-5 py-5 flex items-center gap-3">
        <div className="relative">
          <Sparkles className="text-accent-glow" size={24} />
          <div className="absolute -inset-1 bg-accent/20 rounded-full blur-md -z-10" />
        </div>
        <div>
          <div className="font-semibold tracking-tight text-[15px]">LocalForge</div>
          <div className="text-[11px] text-ink-400 flex items-center gap-1">
            <ShieldCheck size={10} /> 100% local · no cloud
          </div>
        </div>
      </div>

      <nav className="px-3 flex flex-col gap-1 mt-2">
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all duration-150",
                isActive
                  ? "bg-accent/15 text-white shadow-[0_0_20px_-8px_rgba(124,92,255,0.5)]"
                  : "text-ink-200 hover:bg-white/[0.04]"
              )
            }
          >
            <it.icon size={17} />
            <span className="flex-1">{it.label}</span>
            {it.pro && <span className="pro-badge">PRO</span>}
          </NavLink>
        ))}
      </nav>

      {/* Backend status pills */}
      <div className="mt-auto px-4 py-4 space-y-2 border-t border-white/[0.05]">
        {backends.map((b) => (
          <div key={b.name} className="flex items-center justify-between text-[11px]">
            <span className="text-ink-400 truncate pr-2">{b.name}</span>
            <span className="flex items-center gap-1.5">
              <span className={clsx("w-1.5 h-1.5 rounded-full",
                b.running ? "bg-success" : b.available ? "bg-warn" : "bg-ink-600")} />
              <span className={clsx(b.running ? "text-success" : "text-ink-400")}>
                {b.running ? "online" : b.available ? "ready" : "off"}
              </span>
            </span>
          </div>
        ))}
        <div className="text-[10px] text-ink-600 pt-1">v1.1.0</div>
      </div>
    </aside>
  );
}
