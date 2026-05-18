interface Props {
  prompt: string;
  setPrompt: (v: string) => void;
  negative: string;
  setNegative: (v: string) => void;
}

export default function PromptBox({ prompt, setPrompt, negative, setNegative }: Props) {
  return (
    <div className="space-y-3">
      <div>
        <label className="text-sm text-ink-400 mb-1 block">Prompt</label>
        <textarea
          className="input min-h-[110px] resize-none"
          placeholder="A serene mountain lake at golden hour, ultra-detailed, 8k"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
      </div>
      <details className="text-sm">
        <summary className="cursor-pointer text-ink-400 select-none">Negative prompt (optional)</summary>
        <textarea
          className="input mt-2 min-h-[70px] resize-none"
          placeholder="blurry, low quality, watermark"
          value={negative}
          onChange={(e) => setNegative(e.target.value)}
        />
      </details>
    </div>
  );
}
