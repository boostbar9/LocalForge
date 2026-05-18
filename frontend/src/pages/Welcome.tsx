import { useNavigate } from "react-router-dom";
import { Sparkles, ShieldCheck, Cpu, Film } from "lucide-react";

export default function Welcome() {
  const nav = useNavigate();
  return (
    <div className="p-12 max-w-4xl mx-auto fade-up">
      <div className="flex items-center gap-3 mb-2">
        <div className="relative">
          <Sparkles className="text-accent-glow" size={28} />
          <div className="absolute -inset-2 bg-accent/20 rounded-full blur-md -z-10" />
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Welcome to LocalForge</h1>
      </div>
      <p className="text-ink-400 mb-10 text-lg">AI image and video generation — 100% on your machine, forever offline.</p>

      <div className="grid md:grid-cols-3 gap-4 mb-10">
        <Feature icon={ShieldCheck} title="Private by design" body="No accounts, no telemetry, no cloud." />
        <Feature icon={Cpu} title="Tuned for your GPU" body="DirectML + ZLUDA on AMD RX 7900 XT." />
        <Feature icon={Film} title="Photoreal video" body="LTX-Video, Wan 2.1, HunyuanVideo." />
      </div>

      <div className="flex gap-3">
        <button className="btn-primary text-base py-3 px-6" onClick={() => nav("/generate")}>
          Start creating
        </button>
        <button className="btn-ghost" onClick={() => nav("/models")}>
          Browse models
        </button>
      </div>
    </div>
  );
}

function Feature({ icon: Icon, title, body }: any) {
  return (
    <div className="card card-hover p-5">
      <div className="inline-flex p-2 rounded-xl bg-accent/15 mb-3">
        <Icon className="text-accent-glow" size={20} />
      </div>
      <div className="font-medium">{title}</div>
      <div className="text-sm text-ink-400 mt-1">{body}</div>
    </div>
  );
}
