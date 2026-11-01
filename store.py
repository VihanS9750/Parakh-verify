"""SQLite store: dated copies of official lists, and a log of every check.

Owner: Atharva.
- snapshots: the latest copy of each official list, with the time we fetched it.
- checks:    one row per check. We keep a hash of the forward, never the forward itself.
"""
import hashlib
import hmac
import os
import secrets
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
    con.execute("""CREATE TABLE IF NOT EXISTS handle_sightings (
        handle_hash TEXT, input_hash TEXT, claim TEXT, seen_at TEXT, PRIMARY KEY (handle_hash, input_hash))""")
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


KEY_FILE = Path(__file__).with_name(".parakh_log_key")  # made on first use, kept on this computer, never committed


def fingerprint(text):
    """A keyed hash (HMAC) of a forward. Plain SHA-256 can be guessed for a known message; without the key it can't."""
    key = os.environ.get("PARAKH_LOG_KEY") or (KEY_FILE.read_text() if KEY_FILE.exists() else "")
    if not key:
        key = secrets.token_hex(16)
        KEY_FILE.write_text(key)
    return hmac.new(key.encode(), text.encode(), hashlib.sha256).hexdigest()[:16]


def log_check(forward_text, headline, verdicts, duration_ms, mode):
    digest = fingerprint(forward_text)
    con = _db()
    con.execute("INSERT INTO checks (created_at, input_hash, headline, n_items, verdicts, duration_ms, mode) "
                "VALUES (?,?,?,?,?,?,?)",
                (now(), digest, headline, len(verdicts), json.dumps(verdicts), duration_ms, mode))
    con.commit()


def recent_checks(limit=50):
    return _db().execute("SELECT created_at, headline, n_items, verdicts, duration_ms, mode, input_hash "
                         "FROM checks ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


def remember_handle(handle, claim, forward_text):
    """Note that a UPI handle was in this forward, told as story `claim`. Returns every claim that handle has been
    seen with in OTHER forwards. Only hashes are kept (of the handle and of the forward), never the handle itself."""
    h = hashlib.sha256(handle.lower().encode()).hexdigest()[:16]
    digest = hashlib.sha256(forward_text.encode()).hexdigest()[:16]
    con = _db()
    before = {r[0] for r in con.execute("SELECT claim FROM handle_sightings WHERE handle_hash=? AND input_hash!=?",
                                        (h, digest))}
    con.execute("INSERT OR IGNORE INTO handle_sightings VALUES (?,?,?,?)", (h, digest, claim, now()))
    con.commit()
    return before
