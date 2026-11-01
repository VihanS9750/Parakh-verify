"""SQLite store: dated copies of official lists, and a log of every check.

Owner: Atharva.
- snapshots: the latest copy of each official list, with the time we fetched it.
- checks:    one row per check. We keep a hash of the forward, never the forward itself.
"""
import hashlib
import json
import sqlite3
import time
from pathlib import Path

from connectors.net import now

DB = Path(__file__).with_name("parakh.db")


def _db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS snapshots (
        source TEXT PRIMARY KEY, rows TEXT, fetched_at TEXT, saved_ts REAL, as_on TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS checks (
        id INTEGER PRIMARY KEY, created_at TEXT, input_hash TEXT, headline TEXT,
        n_items INTEGER, verdicts TEXT, duration_ms INTEGER, mode TEXT)""")
    return con


def cached_list(source, fetch, max_age_hours=24):
    """Return (rows, fetched_at, as_on, stale) for an official list.

    Uses our copy if it is younger than max_age_hours. Otherwise downloads a fresh one with fetch(),
    which must return (rows, as_on). If the site is down we fall back to the last copy and mark it stale;
    with no copy at all, the error goes up to the connector, which reports "unavailable".
    """
    con = _db()
    row = con.execute("SELECT rows, fetched_at, saved_ts, as_on FROM snapshots WHERE source=?",
                      (source,)).fetchone()
    if row and time.time() - row[2] < max_age_hours * 3600:
        return json.loads(row[0]), row[1], row[3], False
    try:
        rows, as_on = fetch()
    except Exception:
        if row:
            return json.loads(row[0]), row[1], row[3], True
        raise
    fetched_at = now()
    con.execute("REPLACE INTO snapshots VALUES (?,?,?,?,?)",
                (source, json.dumps(rows, ensure_ascii=False), fetched_at, time.time(), as_on))
    con.commit()
    return rows, fetched_at, as_on, False


def snapshots():
    """What official lists we hold and when we fetched them (for the Sources tab)."""
    return _db().execute("SELECT source, fetched_at, as_on, length(rows) FROM snapshots ORDER BY source").fetchall()


def clear_snapshots():
    con = _db()
    con.execute("DELETE FROM snapshots")
    con.commit()


def log_check(forward_text, headline, verdicts, duration_ms, mode):
    digest = hashlib.sha256(forward_text.encode()).hexdigest()[:16]
    con = _db()
    con.execute("INSERT INTO checks (created_at, input_hash, headline, n_items, verdicts, duration_ms, mode) "
                "VALUES (?,?,?,?,?,?,?)",
                (now(), digest, headline, len(verdicts), json.dumps(verdicts), duration_ms, mode))
    con.commit()


def recent_checks(limit=50):
    return _db().execute("SELECT created_at, headline, n_items, verdicts, duration_ms, mode, input_hash "
                         "FROM checks ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
