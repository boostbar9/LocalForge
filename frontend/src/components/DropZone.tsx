import { useRef, useState } from "react";
import { Upload, X } from "lucide-react";

interface Props {
  image: string | null;
  setImage: (b64: string | null) => void;
  label?: string;
}

export default function DropZone({ image, setImage, label = "Drop an image" }: Props) {
  const ref = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = (file: File) => {
    const r = new FileReader();
    r.onload = () => setImage(r.result as string);
    r.readAsDataURL(file);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault(); setDragOver(false);
        const f = e.dataTransfer.files?.[0];
        if (f) handleFile(f);
      }}
      onClick={() => ref.current?.click()}
      className={`card aspect-square flex items-center justify-center cursor-pointer
        transition ${dragOver ? "border-accent/70 bg-accent/5" : ""}`}
    >
      {image ? (
        <div className="relative w-full h-full">
          <img src={image} className="w-full h-full object-cover rounded-2xl" />
          <button
            onClick={(e) => { e.stopPropagation(); setImage(null); }}
            className="absolute top-2 right-2 p-1 rounded-full bg-black/60 hover:bg-black/80"
          >
            <X size={14} />
          </button>
        </div>
      ) : (
        <div className="text-center text-ink-400">
          <Upload size={28} className="mx-auto mb-2 opacity-70" />
          <div className="text-sm">{label}</div>
          <div className="text-xs mt-1">or click to browse</div>
        </div>
      )}
      <input
        ref={ref}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
    </div>
  );
}
