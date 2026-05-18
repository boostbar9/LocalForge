import { useEffect, useState } from "react";
import {
  getVideoStatus, installVideoPro, getInstallLog,
  VIDEO_MODELS, VIDEO_PRESETS,
} from "../lib/video";
import { enqueue } from "../lib/api";
import { Film, Download, Play, Star, Clock, HardDrive, Shield, CheckCircle2 } from "lucide-react";
import clsx from "clsx";
import QueuePanel from "../components/QueuePanel";

export default function VideoPro() {
  const [status, setStatus] = useState<{ installed: boolean; running: boolean; error?: string | null } | null>(null);
  const [installing, setInstalling] = useState(false);
  const [log, setLog] = useState<string[]>([]);
  const [model, setModel] = useState("ltx");
  const [style, setStyle] = useState("photorealistic");
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);

  // Status poll
  useEffect(() => {
    const tick = () => getVideoStatus().then(setStatus).catch(() => {});
    tick();
    const id = setInterval(tick, 3000);
    return () => clearInterval(id);
  }, []);

  // Install log poll
  useEffect(() => {
    if (!installing) return;
    const id = setInterval(async () => {
      const r = await getInstallLog().catch(() => null);
      if (r) {
        setLog(r.lines);
        if (r.done) {
          setInstalling(false);
          getVideoStatus().then(setStatus);
        }
      }
    }, 1500);
    return () => clearInterval(id);
  }, [installing]);

  const startInstall = async () => {
    setInstalling(true);
    setLog([]);
    await installVideoPro();
  };

  const generate = async () => {
    if (!prompt.trim()) return;
    setBusy(true);
    await enqueue({
      mode: "txt2vid", prompt, preset: style, quality: "balanced",
      width: 768, height: 512,
      // @ts-ignore extra field
      video_model: model,
    } as any);
    setTimeout(() => setBusy(false), 500);
  };

  // ----- STATE 1: not installed -----
  if (status && !status.installed) {
    return (
      <div className="p-8 max-w-3xl mx-auto fade-up">
        <Header />

        {!installing ? (
          <div className="card card-glow p-8 mt-6">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-2xl bg-accent/20">
                <Film className="text-accent-glow" size={28} />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold">Install Video Pro</h2>
                <p className="text-ink-200 mt-1 text-sm">
                  Unlock real photorealistic video generation on your AMD RX 7900 XT using
                  ZLUDA + CUDA-built PyTorch. Adds LTX-Video, Wan 2.1, and HunyuanVideo support.
                </p>

                <div className="grid grid-cols-3 gap-3 mt-5">
                  <Stat icon={HardDrive} label="Download" value="~3.5 GB" />
                  <Stat icon={Clock} label="Install time" value="5-15 min" />
                  <Stat icon={Shield} label="Stays local" value="Always" />
                </div>

                <button onClick={startInstall} className="btn-primary mt-6">
                  <Download size={18} /> Install Video Pro
                </button>

                <p className="text-[11px] text-ink-400 mt-3">
                  Image generation will keep working normally on DirectML during installation.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <InstallProgress log={log} />
        )}
      </div>
    );
  }

  // ----- STATE 2: installed & ready -----
  return (
    <div className="p-8 grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6 fade-up max-w-[1600px] mx-auto">
      <div className="space-y-6">
        <Header status={status} />

        {/* Model picker */}
        <div>
          <div className="text-sm text-ink-400 mb-2.5">Video model</div>
          <div className="grid md:grid-cols-3 gap-3">
            {VIDEO_MODELS.map((m) => (
              <button key={m.id} onClick={() => setModel(m.id)}
                      className={clsx(
                        "card p-4 text-left card-hover relative",
                        model === m.id && "card-selected"
                      )}>
                {m.recommended && (
                  <div className="absolute top-3 right-3 pro-badge !bg-success !animate-none !bg-none" style={{background:"#22c55e"}}>BEST</div>
                )}
                <div className="font-semibold">{m.name}</div>
                <div className="text-xs text-ink-400 mt-0.5">{m.tagline}</div>
                <div className="flex gap-1 my-3">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} size={11}
                          className={i < m.quality ? "fill-accent-glow text-accent-glow" : "text-ink-600"} />
                  ))}
                </div>
                <p className="text-[11px] text-ink-400 leading-relaxed">{m.description}</p>
                <div className="flex gap-3 mt-3 text-[10px] text-ink-400">
                  <span className="flex items-center gap-1"><Clock size={10}/>{m.time}</span>
                  <span className="flex items-center gap-1"><HardDrive size={10}/>{m.vram}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Prompt */}
        <div className="card p-6 space-y-5">
          <div>
            <label className="text-sm text-ink-400 mb-1.5 block">Describe your video</label>
            <textarea className="input min-h-[120px] resize-none"
                      placeholder="A cinematic shot of a deer walking through misty pine forest at dawn, golden light filtering through trees, slow camera dolly forward"
                      value={prompt} onChange={(e) => setPrompt(e.target.value)} />
          </div>

          <div>
            <div className="text-sm text-ink-400 mb-2">Style</div>
            <div className="grid grid-cols-3 gap-2">
              {VIDEO_PRESETS.map((p) => (
                <button key={p.id} onClick={() => setStyle(p.id)}
                        className={clsx("card p-3 text-left card-hover",
                                        style === p.id && "card-selected")}>
                  <div className="text-xl mb-1">{p.icon}</div>
                  <div className="font-medium text-sm">{p.name}</div>
                  <div className="text-[11px] text-ink-400 mt-0.5">{p.description}</div>
                </button>
              ))}
            </div>
          </div>

          <button onClick={generate} disabled={busy || !prompt.trim()}
                  className={clsx("btn-primary w-full text-base py-3.5", busy && "pulse-glow")}>
            <Play size={18} /> {busy ? "Queuing video…" : "Generate video"}
          </button>
          <p className="text-[11px] text-ink-400 text-center">
            First generation downloads the model (one-time, ~5 GB).
          </p>
        </div>
      </div>

      <aside className="space-y-4">
        <div className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm font-medium">Queue</div>
            <div className="text-[11px] text-ink-400">live</div>
          </div>
          <QueuePanel compact />
        </div>
      </aside>
    </div>
  );
}

function Header({ status }: { status?: any } = {}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold tracking-tight">Video Pro</h1>
          <span className="pro-badge">PRO</span>
        </div>
        <p className="text-sm text-ink-400 mt-1">
          Photorealistic local video — ZLUDA accelerated on AMD.
        </p>
      </div>
      {status?.running && (
        <div className="flex items-center gap-2 text-xs text-success">
          <CheckCircle2 size={14} /> backend online
        </div>
      )}
    </div>
  );
}

function Stat({ icon: Icon, label, value }: any) {
  return (
    <div className="bg-bg-700/40 rounded-xl p-3 border border-white/[0.04]">
      <Icon size={14} className="text-accent-glow mb-1" />
      <div className="text-[10px] text-ink-400 uppercase tracking-wider">{label}</div>
      <div className="text-sm font-medium mt-0.5">{value}</div>
    </div>
  );
}

function InstallProgress({ log }: { log: string[] }) {
  return (
    <div className="card p-6 mt-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-3 h-3 rounded-full bg-accent animate-pulse" />
        <div className="font-medium">Installing Video Pro…</div>
      </div>
      <div className="bg-black/60 rounded-xl p-3 max-h-96 overflow-y-auto font-mono text-[11px] text-ink-200 space-y-0.5">
        {log.length === 0 && <div className="text-ink-600">Preparing installer…</div>}
        {log.map((l, i) => <div key={i}>{l}</div>)}
      </div>
      <p className="text-[11px] text-ink-400 mt-3">
        Safe to leave this page — installation continues in the background.
      </p>
    </div>
  );
}
