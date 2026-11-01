"""SEBI intermediary lists: investment advisers (INA), research analysts (INH), brokers (INZ).
Live search uses the same request SEBI's own GO button sends (captured in browser DevTools).
Records come back as label/value pairs ("Name" -> value, "Registration No." -> value)."""
import csv
import re
import time

import requests
from bs4 import BeautifulSoup

from connectors.base import HEADERS, http_post, result, safe
from connectors.local_list import search_list
from connectors.matching import best_matches, find_by_id

SOURCES = {
    "adviser": {"label": "SEBI investment adviser register", "prefix": "INA"},
    "analyst": {"label": "SEBI research analyst register",   "prefix": "INH"},
    "broker":  {"label": "SEBI stock broker register",       "prefix": "INZ"},
}
AJAX_URL = "https://www.sebi.gov.in/sebiweb/ajax/other/getintmfpiinfo.jsp"
# intmId of each register. 13 = investment advisers (captured). For the other two, repeat the
# DevTools capture on their SEBI pages and read intmId from the Payload tab.
INTM_IDS = {"adviser": 13, "analyst": None, "broker": None}


def page_url(kind):
    i = INTM_IDS[kind]
    return f"https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId={i}" if i else ""


# Words too common in firm names to be useful as a search term on their own.
GENERIC_WORDS = {"investment", "investments", "adviser", "advisers", "advisor", "advisors",
                 "advisory", "private", "pvt", "limited", "ltd", "llp", "services", "research",
                 "analyst", "analysts", "securities", "financial", "india", "and", "the", "capital"}


def valid_reg_format(reg_id: str, kind="adviser") -> bool:
    return bool(re.fullmatch(SOURCES[kind]["prefix"] + r"\d{9}", reg_id.strip().upper()))


def parse_records(html: str, kind="adviser"):
    """Return [{'name','id'}] from a live response or a page saved from the browser."""
    pat = re.compile(SOURCES[kind]["prefix"] + r"\d{9}", re.I)
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    tokens = [t.strip() for t in text.split("\n") if t.strip()]
    out, seen, name = [], set(), None
    for i, t in enumerate(tokens[:-1]):
        label = t.rstrip(" :").lower()
        nxt = tokens[i + 1]
        if label == "name":
            name = nxt
        elif label in ("registration no.", "registration no", "registration number"):
            m = pat.fullmatch(nxt.strip())
            if m and m.group(0).upper() not in seen:
                seen.add(m.group(0).upper())
                out.append({"name": name or "", "id": m.group(0).upper()})
            name = None
    return out


# ---------- live search (same request as SEBI's GO button) ----------
_session = None


def _form(intm_id, name="", reg_no=""):
    d = {k: "" for k in ["contPer", "email", "location", "exchange", "affiliate",
                         "alp", "model", "esgCategory", "intmIds"]}
    d.update({"nextValue": "1", "next": "s", "intmId": str(intm_id),
              "name": name, "regNo": reg_no, "language": "2", "doDirect": "-1"})
    return d


def live_query(kind, name="", reg_no=""):
    """One call to SEBI's search. Returns up to 25 records (SEBI's page size)."""
    global _session
    if INTM_IDS[kind] is None:
        raise RuntimeError(f"intmId for '{kind}' not captured yet (see INTM_IDS)")
    if _session is None:
        _session = requests.Session()
        try:  # visiting the page first gives us a session cookie, like a browser
            _session.get(page_url(kind), timeout=6, headers=HEADERS)
        except requests.RequestException:
            pass
    r = http_post(AJAX_URL, _form(INTM_IDS[kind], name, reg_no), session=_session,
                  headers={"Referer": page_url(kind), "Origin": "https://www.sebi.gov.in",
                           "X-Requested-With": "XMLHttpRequest"})
    return parse_records(r.text, kind)


def live_search(query, kind="adviser"):
    q = query.strip()
    if valid_reg_format(q, kind):
        recs = live_query(kind, reg_no=q.upper())
        return find_by_id(q, recs)
    # SEBI matches substrings, so a misspelt full name finds nothing. Try the whole query first,
    # then each word (longest first), and fuzzy-rank whatever comes back ourselves.
    recs = live_query(kind, name=q)
    if not recs:
        words = [w for w in q.split() if len(w) >= 3]
        distinctive = [w for w in words if w.lower() not in GENERIC_WORDS]
        pool, seen = [], set()
        for w in (distinctive or words)[:4]:  # cap calls; skip generic words like "investment"
            time.sleep(1)
            for r in live_query(kind, name=w):
                if r["id"] not in seen:
                    seen.add(r["id"])
                    pool.append(r)
        recs = pool
    return best_matches(q, recs)


# ---------- saved-page backup ----------
def html_to_csv(html_path, csv_path, kind="adviser"):
    html = open(html_path, encoding="utf-8", errors="ignore").read()
    rows = parse_records(html, kind)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["name", "id"])
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def search(query, kind="adviser", csv_path=None, downloaded_on=None):
    """Live by default. Pass csv_path to search a saved list instead (offline backup)."""
    src, url = SOURCES[kind]["label"], page_url(kind)

    def run():
        if csv_path:
            return search_list(src, query, csv_path, url, downloaded_on)
        matches = live_search(query, kind)
        return result(src, query, "found" if matches else "not_found", matches, source_url=url)

    return safe(src, query, url, run)


if __name__ == "__main__":
    import json, sys
    # python -m connectors.sebi "29K Investment Advisers"        -> live search
    # python -m connectors.sebi "query" advisers.csv             -> offline backup
    # python -m connectors.sebi build saved.html advisers.csv    -> make the backup CSV
    if sys.argv[1] == "build":
        print(html_to_csv(sys.argv[2], sys.argv[3]), "records saved")
    else:
        csv_arg = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(search(sys.argv[1], csv_path=csv_arg), indent=2, ensure_ascii=False))
