"""Maintains the gallery index — every generated image gets a sidecar with full params."""
from __future__ import annotations
import json, sqlite3, time
from pathlib import Path
from config import DB_PATH, OUTPUT_DIR, SETTINGS


def _init() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS gallery(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE, prompt TEXT, params TEXT, created_at REAL)""")
    conn.commit(); conn.close()


_init()


def register_output(path: Path, params: dict) -> None:
    """Record a finished image and write its sidecar JSON."""
    if SETTINGS.save_sidecar:
        sidecar = path.with_suffix(path.suffix + ".json")
        sidecar.write_text(json.dumps(params, indent=2, default=str))

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO gallery(filename, prompt, params, created_at) VALUES (?,?,?,?)",
        (path.name, params.get("prompt", ""), json.dumps(params), time.time()),
    )
    conn.commit(); conn.close()


def list_items(limit: int = 100, offset: int = 0) -> dict:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, filename, prompt, created_at FROM gallery ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM gallery").fetchone()[0]
    conn.close()
    return {
        "items": [{"id": r[0], "filename": r[1], "prompt": r[2], "created_at": r[3]} for r in rows],
        "total": total,
    }
