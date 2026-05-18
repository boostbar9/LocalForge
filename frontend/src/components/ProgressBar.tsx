export default function ProgressBar({ value }: { value: number }) {
  return (
    <div className="w-full h-1.5 bg-bg-700 rounded-full overflow-hidden">
      <div
        className="h-full bg-gradient-to-r from-accent to-accent-glow transition-all duration-300"
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  );
}
