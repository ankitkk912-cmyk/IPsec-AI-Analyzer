import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent / "ipsec_analyzer.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                score INTEGER NOT NULL,
                risk TEXT NOT NULL,
                summary TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def save_analysis(filename, result):
    with connect() as conn:
        cur = conn.execute("""
            INSERT INTO analyses(filename, score, risk, summary, result_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            filename,
            result["score"],
            result["risk"],
            result["summary"],
            json.dumps(result),
            datetime.now(timezone.utc).isoformat()
        ))
        return cur.lastrowid

def list_analyses():
    with connect() as conn:
        rows = conn.execute("""
            SELECT id, filename, score, risk, summary, created_at
            FROM analyses ORDER BY id DESC LIMIT 20
        """).fetchall()
        return [dict(r) for r in rows]

def get_analysis(analysis_id):
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        data["result"] = json.loads(data.pop("result_json"))
        return data
