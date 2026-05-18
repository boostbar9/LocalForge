import clsx from "clsx";
import { STYLE_PRESETS, QUALITY_TIERS } from "../lib/presets";

interface Props {
  preset: string; setPreset: (v: string) => void;
  quality: "fast" | "balanced" | "max"; setQuality: (v: "fast" | "balanced" | "max") => void;
}

export default function PresetSelector({ preset, setPreset, quality, setQuality }: Props) {
  return (
    <div className="space-y-5">
      <div>
        <div className="text-sm text-ink-400 mb-2.5">Style</div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5">
          {STYLE_PRESETS.map((p) => (
            <button key={p.id} onClick={() => setPreset(p.id)}
                    className={clsx(
                      "card p-3.5 text-left card-hover",
                      preset === p.id && "card-selected"
                    )}>
              <div className="text-xl">{p.preview}</div>
              <div className="font-medium text-sm mt-1.5">{p.name}</div>
              <div className="text-[11px] text-ink-400 mt-0.5 leading-snug">{p.description}</div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className="text-sm text-ink-400 mb-2.5">Quality</div>
        <div className="flex gap-2">
          {QUALITY_TIERS.map((q) => (
            <button key={q.id} onClick={() => setQuality(q.id as any)}
                    className={clsx("card flex-1 p-3 text-center card-hover",
                                    quality === q.id && "card-selected")}>
              <div className="font-medium text-sm">{q.name}</div>
              <div className="text-[10px] text-ink-400 mt-0.5">{q.hint}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
