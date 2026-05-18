import { useEffect, useRef, useState } from "react";
import { Job } from "./api";

export function useJobStream() {
  const [jobs, setJobs] = useState<Record<string, Job>>({});
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8765/api/ws");
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "job") {
          setJobs((j) => ({ ...j, [msg.job.id]: msg.job }));
        }
      } catch {}
    };
    ws.onclose = () => { wsRef.current = null; };
    return () => ws.close();
  }, []);

  return jobs;
}
