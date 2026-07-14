import sqlite3
from datetime import datetime, timezone

DB_PATH = "/app/data/history.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            device_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            summary TEXT NOT NULL
        )
    """)
    return conn


def build_summary_line(model_output: dict, user_context: str | None) -> str:
    style = model_output.get("style", "bilinmiyor")
    palette_type = model_output.get("palette_type", "bilinmiyor")
    score = model_output.get("harmony_score", "-")
    purpose = user_context or "belirtilmedi"
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"{date}: {style}/{palette_type}, skor {score}, amaç: {purpose}"


def add_history_entry(device_id: str, summary: str) -> None:
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO history (device_id, created_at, summary) VALUES (?, ?, ?)",
            (device_id, datetime.now(timezone.utc).isoformat(), summary),
        )


def get_history_summary(device_id: str, limit: int = 5) -> str:
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT summary FROM history WHERE device_id = ? ORDER BY created_at DESC LIMIT ?",
            (device_id, limit),
        ).fetchall()
    if not rows:
        return ""
    lines = [row[0] for row in reversed(rows)]
    return "\n".join(lines)