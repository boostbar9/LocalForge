import { useState } from "react";
import PromptBox from "../components/PromptBox";
import PresetSelector from "../components/PresetSelector";
import DropZone from "../components/DropZone";
import QueuePanel from "../components/QueuePanel";
import ModelPicker from "../components/ModelPicker";
import { SIZE_PRESETS } from "../lib/presets";
import { enqueue, GenerateParams } from "../lib/api";
import { Play, Sparkles, ImageIcon, Wand, Maximize2 } from "lucide-react";
import clsx from "clsx";

type Mode = "txt2img" | "img2img" | "inpaint" | "upscale";

const MODES: { id: Mode; label: string; icon: any }[] = [
  { id: "txt2img", label: "Text → Image", icon: Sparkles },
  { id: "img2img", label: "Image → Image", icon: ImageIcon },
  { id: "inpaint", label: "Inpaint", icon: Wand },
  { id: "upscale", label: "Upscale / Restore", icon: Maximize2 },
];

export default function Generate() {
  const [mode, setMode] = useState<Mode>("txt2img");
  const [prompt, setPrompt] = useState("");
  const [negative, setNegative] = useState("");
  const [preset, setPreset] = useState("photorealistic");
  const [quality, setQuality] = useState<"fast" | "balanced" | "max">("balanced");
  const [size, setSize] = useState(0);
  const [initImage, setInitImage] = useState<string | null>(null);
  const [mask, setMask] = useState<string | null>(null);
  const [model, setModel] = useState("");
  const [busy, setBusy] = useState(false);

  const onGenerate = async () => {
    if (!prompt.trim() && mode !== "upscale") return;
    setBusy(true);
    const s = SIZE_PRESETS[size];
    const p: GenerateParams = {
      mode, prompt, negative_prompt: negative, preset, quality,
      width: s.w, height: s.h, model, count: 1,
      init_image: initImage ?? undefined, mask: mask ?? undefined,
    };
    try { await enqueue(p); } finally { setTimeout(() => setBusy(false), 400); }
  };

  return (
    <div className="p-8 grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6 fade-up max-w-[1600px] mx-auto">
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Create</h1>
          <p className="text-sm text-ink-400 mt-1">Choose a mode, write a prompt, pick a style. That's it.</p>
        </div>

        {/* Mode pills */}
        <div className="flex flex-wrap gap-2">
          {MODES.map((m) => (
            <button key={m.id} onClick={() => setMode(m.id)}
                    className={clsx("mode-pill flex items-center gap-2",
                                    mode === m.id ? "mode-pill-active" : "mode-pill-inactive")}>
              <m.icon size={15} />
              {m.label}
            </button>
          ))}
        </div>

        <div className="card p-6 space-y-6">
          <PromptBox prompt={prompt} setPrompt={setPrompt} negative={negative} setNegative={setNegative} />

          {(mode === "img2img" || mode === "inpaint" || mode === "upscale") && (
            <div className="grid grid-cols-2 gap-3">
              <DropZone image={initImage} setImage={setInitImage} label="Input image" />
              {mode === "inpaint" && <DropZone image={mask} setImage={setMask} label="Mask (white = edit)" />}
            </div>
          )}

          <PresetSelector preset={preset} setPreset={setPreset} quality={quality} setQuality={setQuality} />

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-sm text-ink-400 mb-1.5 block">Size</label>
              <select className="input" value={size} onChange={(e) => setSize(+e.target.value)}>
                {SIZE_PRESETS.map((s, i) => <option key={s.label} value={i}>{s.label}</option>)}
              </select>
            </div>
            <ModelPicker value={model} onChange={setModel} />
          </div>

          <button onClick={onGenerate} disabled={busy}
                  className={clsx("btn-primary w-full text-base py-3.5", busy && "pulse-glow")}>
            <Play size={18} />
            {busy ? "Queuing…" : "Generate"}
          </button>
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
