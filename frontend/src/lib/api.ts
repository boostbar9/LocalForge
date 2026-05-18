import { useEffect, useState } from "react";

export const API = "http://127.0.0.1:8765";

export interface GenerateParams {
  mode: "txt2img" | "img2img" | "inpaint" | "upscale" | "txt2vid";
  prompt: string;
  negative_prompt?: string;
  preset: string;          // photoreal | cinematic | anime
  quality: "fast" | "balanced" | "max";
  width: number;
  height: number;
  steps?: number;
  cfg?: number;
  seed?: number;
  model?: string;
  lora?: { name: string; weight: number }[];
  init_image?: string;     // base64 or path
  mask?: string;           // base64 or path
  count?: number;
}

export interface Job {
  id: string;
  status: "queued" | "running" | "done" | "error" | "cancelled";
  progress: number;
  preview?: string;
  result?: string[];
  error?: string;
  params: GenerateParams;
  created_at: number;
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

export const enqueue = (p: GenerateParams) =>
  api<{ id: string }>("/api/generate", { method: "POST", body: JSON.stringify(p) });

export const listJobs = () => api<Job[]>("/api/jobs");
export const cancelJob = (id: string) =>
  api(`/api/jobs/${id}/cancel`, { method: "POST" });

export const listGallery = (limit = 100, offset = 0) =>
  api<{ items: any[]; total: number }>(`/api/gallery?limit=${limit}&offset=${offset}`);

export const listModels = () =>
  api<{ checkpoints: string[]; loras: string[]; vaes: string[]; upscalers: string[] }>("/api/models");

export const getSettings = () => api<any>("/api/settings");
export const updateSettings = (s: any) =>
  api("/api/settings", { method: "POST", body: JSON.stringify(s) });

export const getGpuInfo = () => api<any>("/api/gpu");

export function useBackend() {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    let attempts = 0;
    const tick = async () => {
      try {
        await api("/api/health");
        if (!cancelled) setReady(true);
      } catch {
        attempts++;
        if (attempts > 60) setError("Backend failed to start. Check logs.");
        else setTimeout(tick, 500);
      }
    };
    tick();
    return () => { cancelled = true; };
  }, []);
  return { ready, error };
}
