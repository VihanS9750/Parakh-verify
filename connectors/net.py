"""Shared helpers every connector uses: one polite way to fetch, one result shape.

Owner: Atharva. Rahul's connectors should use these too.
"""
import time
from datetime import datetime, timedelta, timezone

import requests

IST = timezone(timedelta(hours=5, minutes=30))
# We say who we are. We never pretend to be a browser to get past a block.
HEADERS = {"User-Agent": "ParakhVerifier/0.1 (Forge hackathon student project; low-rate)"}
TIMEOUT = 8          # seconds before we give up on a site
MIN_GAP = 1.0        # seconds between two requests to the same site
_last_hit = {}


def now():
    return datetime.now(IST).isoformat(timespec="seconds")


def get(url, **params):
    """GET a page politely: honest user agent, 1 request/second per site, 8 s timeout, one retry.

    Raises requests.RequestException if both tries fail; callers turn that into status "unavailable".
    """
    host = url.split("/")[2]
    for attempt in (1, 2):
        wait = MIN_GAP - (time.time() - _last_hit.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        _last_hit[host] = time.time()
        try:
            r = requests.get(url, params=params or None, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r
        except requests.RequestException:
            if attempt == 2:
                raise


def result(source, organisation, query, status, matches=(), source_url="", limitations="",
           list_type="register", detail="", checked_at=None):
    """The one shape every connector returns (see CLAUDE.md).

    status:    found | not_found | unavailable | needs_user | invalid
    list_type: "register" (being found is good) or "warning_list" (being found is bad) or "format" (ID checks)
    """
    return {
        "source": source,
        "organisation": organisation,
        "query": query,
        "status": status,
        "matches": list(matches),
        "source_url": source_url,
        "checked_at": checked_at or now(),
        "limitations": limitations,
        "list_type": list_type,
        "detail": detail,
    }
