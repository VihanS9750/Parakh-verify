"""Is this link on URLhaus (abuse.ch), a public list of URLs reported for spreading malware?

Owner: Vihan. Used for QR codes that hold a link instead of a UPI payment. Needs a free Auth-Key from
https://auth.abuse.ch/ in the URLHAUS_AUTH_KEY environment variable; without one the check says "unavailable".
We download abuse.ch's own "recent URLs" export (last 30 days) and keep it for an hour (their rule: no more than
once every 5 minutes), then look the link up in it. Not being listed proves nothing: most scam links never get reported.
"""
import csv
import io
import os

import requests

import store
from connectors import net

EXPORT = "https://urlhaus-api.abuse.ch/v2/files/exports/{key}/recent.csv"
PAGE = "https://urlhaus.abuse.ch/"


def _fetch():
    r = requests.get(EXPORT.format(key=os.environ["URLHAUS_AUTH_KEY"]), headers=net.HEADERS, timeout=30)
    r.raise_for_status()
    lines = [l for l in r.text.splitlines() if l.strip()]
    header = next(l for l in lines if l.startswith("#") and "url" in l.lower() and "," in l).lstrip("# ")
    rows = list(csv.DictReader(io.StringIO("\n".join([header] + [l for l in lines if not l.startswith("#")]))))
    return [{"url": r["url"], "threat": r.get("threat", ""), "added": r.get("dateadded", "")} for r in rows], \
        "last 30 days"


def check(url):
    name = "URLhaus (abuse.ch) malware URL list"
    if not os.environ.get("URLHAUS_AUTH_KEY"):
        return net.result(name, "abuse.ch", url, "unavailable", source_url=PAGE, list_type="warning_list",
                          detail="No URLHAUS_AUTH_KEY set, so this list was not checked.")
    try:
        rows, fetched_at, as_on, stale = store.cached_list("urlhaus_recent", _fetch, max_age_hours=1)
    except Exception as e:
        return net.result(name, "abuse.ch", url, "unavailable", source_url=PAGE, list_type="warning_list",
                          detail=f"Could not download the list ({type(e).__name__}).")
    want = url.strip().lower().rstrip("/")
    hit = next((r for r in rows if r["url"].lower().rstrip("/") == want), None)
    return net.result(name, "abuse.ch", url, "found" if hit else "not_found", source_url=PAGE,
                      matches=[{"name": hit["url"], "id": hit["added"], "score": 100}] if hit else [],
                      list_type="warning_list", checked_at=fetched_at,
                      detail=(f"Listed as '{hit['threat']}' on {hit['added']}." if hit else
                              f"Not in abuse.ch's last-30-days list (copy fetched {fetched_at})."),
                      limitations="Only URLs reported in the last 30 days; most scam links are never reported.")
