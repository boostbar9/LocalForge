"""SQLite-backed job queue with crash recovery."""
from __future__ import annotations
import asyncio, json, sqlite3, time, uuid
from dataclasses import dataclass, asdict, field
from typing import Optional
from config import DB_PATH


@dataclass
class Job:
    id: str
    status: str = "queued"     # queued | running | done | error | cancelled
    progress: float = 0.0
    preview: Optional[str] = None
    result: list = field(default_factory=list)
    error: Optional[str] = None
    params: dict = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: time.time())


class JobQueue:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._cond = asyncio.Condition(self._lock)
        self._jobs: dict[str, Job] = {}
        self._listeners: set[asyncio.Queue] = set()
        self._init_db()
        self._restore()

    # ----------------------- persistence -----------------------
    def _init_db(self) -> None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY, status TEXT, progress REAL,
            result TEXT, error TEXT, params TEXT, created_at REAL)""")
        conn.commit(); conn.close()

    def _restore(self) -> None:
        conn = sqlite3.connect(DB_PATH)
        for row in conn.execute("SELECT id,status,progress,result,error,params,created_at FROM jobs"):
            j = Job(id=row[0], status=row[1] if row[1] != "running" else "queued",
                    progress=row[2], result=json.loads(row[3] or "[]"),
                    error=row[4], params=json.loads(row[5] or "{}"), created_at=row[6])
            self._jobs[j.id] = j
        conn.close()

    def _persist(self, j: Job) -> None:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?)",
            (j.id, j.status, j.progress, json.dumps(j.result), j.error,
             json.dumps(j.params), j.created_at),
        )
        conn.commit(); conn.close()

    # ----------------------- API -----------------------
    async def enqueue(self, params: dict) -> Job:
        j = Job(id=uuid.uuid4().hex[:12], params=params)
        async with self._cond:
            self._jobs[j.id] = j
            self._persist(j)
            self._cond.notify()
        await self._broadcast(j)
        return j

    async def next_runnable(self) -> Job:
        async with self._cond:
            while True:
                pending = [j for j in self._jobs.values() if j.status == "queued"]
                if pending:
                    pending.sort(key=lambda x: x.created_at)
                    j = pending[0]
                    j.status = "running"
                    self._persist(j)
                    await self._broadcast(j)
                    return j
                await self._cond.wait()

    async def update(self, job_id: str, **fields) -> None:
        if job_id not in self._jobs: return
        j = self._jobs[job_id]
        for k, v in fields.items():
            setattr(j, k, v)
        self._persist(j)
        await self._broadcast(j)

    async def cancel(self, job_id: str) -> None:
        await self.update(job_id, status="cancelled")

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def list(self) -> list[Job]:
        return sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)

    # ----------------------- events -----------------------
    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._listeners.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._listeners.discard(q)

    async def _broadcast(self, job: Job) -> None:
        msg = {"type": "job", "job": asdict(job)}
        for q in list(self._listeners):
            try: q.put_nowait(msg)
            except Exception: pass


QUEUE = JobQueue()
