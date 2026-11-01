"""Shared shape + safe fetching for every Parakh connector."""
import time
from datetime import datetime, timezone, timedelta

import requests

from connectors.net import HEADERS  # one honest user agent for every connector (team rule 6: never look like a browser)

IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> str:
    return datetime.now(IST).isoformat(timespec="seconds")


def result(source, query, status, matches=None, source_url="", note="", data_as_of=None):
    """status: found | not_found | unavailable | needs_user"""
    return {
        "source": source,
        "query": query,
        "status": status,
        "matches": matches or [],
        "source_url": source_url,
        "checked_at": now_ist(),
        "data_as_of": data_as_of,  # set for hand-downloaded lists
        "note": note,
    }


def http_get(url, timeout=6, retries=1, delay=2, **kw):
    """Short timeout, one retry, polite pause. Raises if it still fails."""
    last = None
    for _ in range(retries + 1):
        try:
            r = requests.get(url, timeout=timeout, headers=HEADERS, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            last = e
            time.sleep(delay)
    raise last


def safe(source, query, source_url, fn):
    """Run a connector; any failure becomes an 'unavailable' result, never a crash."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        return result(source, query, "unavailable", source_url=source_url,
                      note=f"{type(e).__name__}: {e}"[:200])


def http_post(url, data, session=None, timeout=6, retries=1, delay=2, headers=None):
    """POST with the same short timeout + one retry as http_get."""
    client = session or requests
    h = dict(HEADERS)
    h.update(headers or {})
    last = None
    for _ in range(retries + 1):
        try:
            r = client.post(url, data=data, timeout=timeout, headers=h)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            last = e
            time.sleep(delay)
    raise last
