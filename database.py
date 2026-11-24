"""database.py - tiny SQLite layer. Every profile check is saved so you can see a history."""
import json
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "profiles.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created TEXT NOT NULL,
                platform TEXT NOT NULL,
                username TEXT NOT NULL,
                display_name TEXT,
                score INTEGER NOT NULL,
                verdict TEXT NOT NULL,
                level TEXT NOT NULL,
                result_json TEXT NOT NULL
            )"""
        )


def save_check(form, result):
    with _connect() as conn:
        cur = conn.execute(
            """INSERT INTO checks (created, platform, username, display_name, score, verdict, level, result_json)
               VALUES (?,?,?,?,?,?,?,?)""",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), form["platform"], form["username"],
             form.get("display_name", ""), result["score"], result["verdict"], result["level"],
             json.dumps(result)),
        )
        return cur.lastrowid


def get_check(check_id):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM checks WHERE id = ?", (check_id,)).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["result"] = json.loads(data.pop("result_json"))
    return data


def list_checks(limit=100):
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, created, platform, username, display_name, score, verdict, level "
            "FROM checks ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def delete_check(check_id):
    with _connect() as conn:
        conn.execute("DELETE FROM checks WHERE id = ?", (check_id,))


def stats():
    with _connect() as conn:
        rows = conn.execute("SELECT level, COUNT(*) AS n FROM checks GROUP BY level").fetchall()
    counts = {"real": 0, "suspicious": 0, "fake": 0}
    for r in rows:
        counts[r["level"]] = r["n"]
    counts["total"] = sum(counts.values())
    return counts
