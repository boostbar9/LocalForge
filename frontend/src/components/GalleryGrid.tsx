import { useEffect, useState } from "react";
import { API, listGallery } from "../lib/api";
import ImageViewer from "./ImageViewer";
import { Play } from "lucide-react";

interface Item { id: string; filename: string; prompt: string; created_at: number; }

const VIDEO_EXT = [".mp4", ".webm", ".mov", ".gif"];

export default function GalleryGrid() {
  const [items, setItems] = useState<Item[]>([]);
  const [open, setOpen] = useState<string | null>(null);

  useEffect(() => {
    listGallery().then((r) => setItems(r.items)).catch(() => {});
    const id = setInterval(() => listGallery().then((r) => setItems(r.items)).catch(() => {}), 4000);
    return () => clearInterval(id);
  }, []);

  if (!items.length) {
    return (
      <div className="card p-12 text-center text-ink-400">
        <div className="text-base mb-1">No creations yet</div>
        <div className="text-sm">Generate an image or video to get started.</div>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-3">
        {items.map((it) => {
          const isVideo = VIDEO_EXT.some((e) => it.filename.toLowerCase().endsWith(e));
          return (
            <button key={it.id} onClick={() => setOpen(it.filename)}
                    className="group relative aspect-square overflow-hidden rounded-xl bg-bg-700 fade-up
                               ring-1 ring-white/[0.04] hover:ring-accent/40 transition-all">
              {isVideo ? (
                <video src={`${API}/api/image/${it.filename}`}
                       className="w-full h-full object-cover" muted loop
                       onMouseEnter={(e) => e.currentTarget.play()}
                       onMouseLeave={(e) => { e.currentTarget.pause(); e.currentTarget.currentTime = 0; }} />
              ) : (
                <img src={`${API}/api/image/${it.filename}`}
                     className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
              )}
              {isVideo && (
                <div className="absolute top-2 left-2 bg-black/60 backdrop-blur px-1.5 py-0.5 rounded-md flex items-center gap-1 text-[10px]">
                  <Play size={10} /> VIDEO
                </div>
              )}
              <div className="absolute inset-x-0 bottom-0 p-2 text-xs bg-gradient-to-t from-black/85 to-transparent
                              opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="line-clamp-2">{it.prompt}</div>
              </div>
            </button>
          );
        })}
      </div>
      <ImageViewer url={open ? `${API}/api/image/${open}` : null} filename={open ?? undefined}
                   onClose={() => setOpen(null)} />
    </>
  );
}
