import { api, API } from "./api";

export interface VideoStatus {
  installed: boolean;
  running: boolean;
  error?: string | null;
}

export const getVideoStatus = () => api<VideoStatus>("/api/video/status");
export const installVideoPro = () => fetch(`${API}/api/video/install`, { method: "POST" }).then((r) => r.json());
export const getInstallLog = () => api<{ lines: string[]; done: boolean }>("/api/video/install/log");
export const listVideoModels = () => api<Record<string, any>>("/api/video/models");

export const VIDEO_MODELS = [
  {
    id: "ltx",
    name: "LTX-Video",
    tagline: "Fastest realistic video",
    description: "5-second clips at 768×512 in ~60-90 seconds. Best balance of speed and quality.",
    time: "~90s",
    quality: 3,
    vram: "12 GB",
    recommended: true,
  },
  {
    id: "wan21",
    name: "Wan 2.1 T2V",
    tagline: "Higher quality, longer wait",
    description: "5-second clips at 832×480 in ~3-5 minutes. Sharper motion, better prompt following.",
    time: "~4 min",
    quality: 4,
    vram: "16 GB",
    recommended: false,
  },
  {
    id: "hunyuan",
    name: "HunyuanVideo 720p",
    tagline: "Near-Sora quality",
    description: "5-second clips at 1280×720 in ~12-15 minutes. The best open model, requires patience.",
    time: "~14 min",
    quality: 5,
    vram: "20 GB",
    recommended: false,
  },
];

export const VIDEO_PRESETS = [
  { id: "photorealistic", name: "Photorealistic", icon: "📷",
    description: "Lifelike footage, natural lighting" },
  { id: "cinematic", name: "Cinematic", icon: "🎬",
    description: "Film grain, dramatic color grading" },
  { id: "anime", name: "Anime", icon: "🌸",
    description: "2D animation style" },
];
