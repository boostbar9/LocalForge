export interface PresetMeta {
  id: string;
  name: string;
  description: string;
  preview: string;
  family: "sdxl" | "flux";
}

export const STYLE_PRESETS: PresetMeta[] = [
  {
    id: "photorealistic",
    name: "Photorealistic",
    description: "Lifelike portraits and scenes with natural lighting",
    preview: "📷",
    family: "sdxl",
  },
  {
    id: "cinematic",
    name: "Cinematic",
    description: "Film-grade color, dramatic lighting, anamorphic feel",
    preview: "🎬",
    family: "sdxl",
  },
  {
    id: "anime",
    name: "Anime",
    description: "Clean linework, vibrant colors, manga/anime aesthetic",
    preview: "🌸",
    family: "sdxl",
  },
  {
    id: "flux_default",
    name: "Flux (high fidelity)",
    description: "Use Flux.1 for the highest prompt-following accuracy",
    preview: "✨",
    family: "flux",
  },
];

export const QUALITY_TIERS = [
  { id: "fast", name: "Fast", steps: 20, hint: "~6s on RX 7900 XT" },
  { id: "balanced", name: "Balanced", steps: 30, hint: "~10s — recommended" },
  { id: "max", name: "Max", steps: 50, hint: "~18s, highest detail" },
] as const;

export const SIZE_PRESETS = [
  { label: "Square 1024", w: 1024, h: 1024 },
  { label: "Portrait 832×1216", w: 832, h: 1216 },
  { label: "Landscape 1216×832", w: 1216, h: 832 },
  { label: "Cinema 1536×640", w: 1536, h: 640 },
];
