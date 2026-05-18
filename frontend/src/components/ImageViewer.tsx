import { Download, Folder, X } from "lucide-react";
import { API } from "../lib/api";

const VIDEO_EXT = [".mp4", ".webm", ".mov", ".gif"];

interface Props { url: string | null; onClose: () => void; filename?: string; }

export default function ImageViewer({ url, onClose, filename }: Props) {
  if (!url) return null;
  const isVideo = filename && VIDEO_EXT.some((e) => filename.toLowerCase().endsWith(e));
  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-6 fade-up"
         onClick={onClose}>
      <div className="max-w-[92vw] max-h-[92vh] relative" onClick={(e) => e.stopPropagation()}>
        {isVideo ? (
          <video src={url} className="max-w-full max-h-[80vh] rounded-xl" controls autoPlay loop />
        ) : (
          <img src={url} className="max-w-full max-h-[80vh] object-contain rounded-xl shadow-2xl" />
        )}
        <div className="flex justify-center gap-2 mt-4">
          <a className="btn-ghost" href={url} download={filename}><Download size={16}/> Download</a>
          <button className="btn-ghost"
                  onClick={() => fetch(`${API}/api/reveal?file=${encodeURIComponent(filename ?? "")}`)}>
            <Folder size={16}/> Show in folder
          </button>
          <button className="btn-ghost" onClick={onClose}><X size={16}/> Close</button>
        </div>
      </div>
    </div>
  );
}
