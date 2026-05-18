import { useEffect, useState } from "react";
import { getSettings, updateSettings, getGpuInfo, api } from "../lib/api";
import { Cpu, ShieldCheck, Film, RefreshCw, Check } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Settings() {
  const nav = useNavigate();
  const [s, setS] = useState<any>({});
  const [gpu, setGpu] = useState<any>(null);
  const [backends, setBackends] = useState<any[]>([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    getSettings().then(setS).catch(() => {});
    getGpuInfo().then(setGpu).catch(() => {});
    api<any>("/api/health").then((r) => setBackends(r.backends || [])).catch(() => {});
  }, []);

  const save = async () => {
    await updateSettings(s);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6 fade-up">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-ink-400 mt-1">Tune LocalForge to your hardware.</p>
      </div>

      <Section icon={Cpu} title="Hardware">
        {gpu ? (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <KV k="GPU" v={gpu.name} />
            <KV k="VRAM" v={`${gpu.vram_gb} GB`} />
            <KV k="Image backend" v={gpu.backend} />
            <KV k="Detected" v={gpu.detected ? "yes" : "no"} />
          </div>
        ) : <div className="text-ink-400 text-sm">Detecting…</div>}
      </Section>

      <Section icon={Film} title="Video Pro (ZLUDA)">
        <div className="space-y-3">
          {backends.filter(b => b.name.includes("Video")).map(b => (
            <div key={b.name} className="flex items-center justify-between bg-bg-700/40 rounded-xl p-3 border border-white/[0.04]">
              <div>
                <div className="font-medium text-sm">{b.name}</div>
                <div className="text-[11px] text-ink-400 mt-0.5">
                  {b.available ? (b.running ? "Online" : "Installed but offline") : "Not installed"}
                </div>
              </div>
              {!b.available ? (
                <button className="btn-primary !py-1.5 !px-3 !text-xs" onClick={() => nav("/video")}>
                  Install
                </button>
              ) : (
                <span className="text-xs text-success flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-success" /> ready
                </span>
              )}
            </div>
          ))}
          <Toggle label="Route video jobs to Video Pro backend"
                  hint="Disable to keep using AnimateDiff on DirectML"
                  checked={!!s.video_pro_enabled}
                  onChange={(v) => setS({ ...s, video_pro_enabled: v })} />
        </div>
      </Section>

      <Section icon={RefreshCw} title="Generation">
        <Toggle label="Save metadata sidecar (.json)" checked={!!s.save_sidecar}
                onChange={(v) => setS({ ...s, save_sidecar: v })} />
        <Select label="Default image format" value={s.output_format ?? "png"}
                onChange={(v) => setS({ ...s, output_format: v })}
                options={[["png","PNG"],["jpg","JPG"],["webp","WebP"]]} />
        <Select label="VRAM optimization" value={s.vram_mode ?? "balanced"}
                onChange={(v) => setS({ ...s, vram_mode: v })}
                options={[
                  ["speed","Speed (use full 20GB)"],
                  ["balanced","Balanced (recommended)"],
                  ["lowvram","Low VRAM"],
                ]} />
      </Section>

      <Section icon={ShieldCheck} title="Privacy">
        <p className="text-xs text-ink-400">LocalForge never makes outbound calls beyond model downloads you initiate.</p>
        <Toggle label="Enable auto-update check" checked={!!s.auto_update}
                onChange={(v) => setS({ ...s, auto_update: v })} />
        <Toggle label="Air-gapped mode — block all outbound network"
                hint="Even model downloads are refused"
                checked={!!s.airgapped}
                onChange={(v) => setS({ ...s, airgapped: v })} />
      </Section>

      <div className="flex items-center gap-3">
        <button className="btn-primary" onClick={save}>Save settings</button>
        {saved && (
          <span className="text-sm text-success flex items-center gap-1.5 fade-up">
            <Check size={14} /> Saved
          </span>
        )}
      </div>
    </div>
  );
}

function Section({ icon: Icon, title, children }: any) {
  return (
    <section className="card p-5 space-y-4">
      <div className="flex items-center gap-2.5">
        <div className="p-1.5 rounded-lg bg-accent/15">
          <Icon size={14} className="text-accent-glow" />
        </div>
        <h2 className="font-medium">{title}</h2>
      </div>
      {children}
    </section>
  );
}
function KV({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <div className="text-[11px] text-ink-400 uppercase tracking-wider">{k}</div>
      <div className="text-sm mt-0.5">{v}</div>
    </div>
  );
}
function Toggle({ label, hint, checked, onChange }: any) {
  return (
    <label className="flex items-start justify-between gap-3 cursor-pointer">
      <div>
        <div className="text-sm">{label}</div>
        {hint && <div className="text-[11px] text-ink-400 mt-0.5">{hint}</div>}
      </div>
      <button onClick={() => onChange(!checked)}
              className={`w-10 h-6 rounded-full transition-colors relative shrink-0 mt-0.5
                          ${checked ? "bg-accent" : "bg-bg-700"}`}>
        <div className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform
                         ${checked ? "translate-x-4" : ""}`} />
      </button>
    </label>
  );
}
function Select({ label, value, onChange, options }: any) {
  return (
    <label className="flex items-center justify-between gap-3">
      <div className="text-sm">{label}</div>
      <select className="input max-w-[220px]" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map(([v,l]: any) => <option key={v} value={v}>{l}</option>)}
      </select>
    </label>
  );
}
