import { useEffect, useState } from "react";
import { listModels, API } from "../lib/api";
import { Download, FolderOpen, RefreshCw } from "lucide-react";

interface ModelInfo { checkpoints: string[]; loras: string[]; vaes: string[]; upscalers: string[]; }

const RECOMMENDED = [
  { id: "sdxl_base", name: "Stable Diffusion XL 1.0", size: "6.9 GB", tag: "Image", purpose: "Default general-purpose model" },
  { id: "realvis_xl", name: "RealVisXL V4.0", size: "6.5 GB", tag: "Image", purpose: "Photorealistic portraits & scenes" },
  { id: "anime_xl", name: "Animagine XL 3.1", size: "6.9 GB", tag: "Image", purpose: "Anime / manga style" },
  { id: "flux_schnell", name: "Flux.1 Schnell", size: "12.5 GB", tag: "Image", purpose: "Highest prompt fidelity, 4-step" },
  { id: "esrgan", name: "Real-ESRGAN 4x", size: "63 MB", tag: "Tool", purpose: "Image upscaler" },
  { id: "animatediff", name: "AnimateDiff v3", size: "1.7 GB", tag: "Video", purpose: "Bundled video on DirectML" },
];

export default function Models() {
  const [m, setM] = useState<ModelInfo>({ checkpoints: [], loras: [], vaes: [], upscalers: [] });
  const refresh = () => listModels().then(setM).catch(() => {});
  useEffect(() => { refresh(); }, []);

  const download = async (id: string) => {
    await fetch(`${API}/api/models/download`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    refresh();
  };

  return (
    <div className="p-8 space-y-6 fade-up max-w-[1400px] mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Models</h1>
          <p className="text-sm text-ink-400 mt-1">Manage your local model library.</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-ghost" onClick={() => fetch(`${API}/api/models/open_folder`)}>
            <FolderOpen size={16}/> Open folder
          </button>
          <button className="btn-ghost" onClick={refresh}><RefreshCw size={16}/> Refresh</button>
        </div>
      </div>

      <section>
        <h2 className="text-sm text-ink-400 mb-3">Recommended downloads</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
          {RECOMMENDED.map((r) => (
            <div key={r.id} className="card card-hover p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="font-medium">{r.name}</div>
                  <div className="text-[11px] text-ink-400 mt-0.5">{r.purpose}</div>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded-md bg-white/[0.06] text-ink-200">{r.tag}</span>
              </div>
              <div className="flex items-center justify-between mt-3">
                <div className="text-xs text-ink-400">{r.size}</div>
                <button className="btn-primary !py-1.5 !px-3 !text-xs" onClick={() => download(r.id)}>
                  <Download size={13}/> Get
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="card p-6">
        <h2 className="font-medium mb-3">Installed</h2>
        {(["checkpoints","loras","vaes","upscalers"] as const).map((k) => (
          <div key={k} className="mb-3 last:mb-0">
            <div className="text-xs text-ink-400 mb-1.5 capitalize">{k}</div>
            <div className="flex flex-wrap gap-1.5">
              {m[k].length === 0 && <div className="text-xs text-ink-600">None installed</div>}
              {m[k].map((x) => <span key={x} className="kbd">{x}</span>)}
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
