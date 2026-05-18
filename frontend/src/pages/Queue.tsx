import QueuePanel from "../components/QueuePanel";

export default function Queue() {
  return (
    <div className="p-8 max-w-3xl mx-auto fade-up">
      <div className="mb-5">
        <h1 className="text-2xl font-semibold tracking-tight">Queue</h1>
        <p className="text-sm text-ink-400 mt-1">Live job queue across both backends.</p>
      </div>
      <QueuePanel />
    </div>
  );
}
