import { useEffect, useState } from "react";
import { listModels } from "../lib/api";

interface Props { value: string; onChange: (v: string) => void; }

export default function ModelPicker({ value, onChange }: Props) {
  const [models, setModels] = useState<string[]>([]);
  useEffect(() => { listModels().then((m) => setModels(m.checkpoints)).catch(() => {}); }, []);
  return (
    <div>
      <label className="text-sm text-ink-400 mb-1 block">Model checkpoint</label>
      <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="">Auto (use preset default)</option>
        {models.map((m) => <option key={m} value={m}>{m}</option>)}
      </select>
    </div>
  );
}
