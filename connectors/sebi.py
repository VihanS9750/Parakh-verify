"""SEBI intermediary lists: investment advisers (INA), research analysts (INH), brokers (INZ).
The parser finds registration numbers by pattern, so it doesn't depend on column layout."""
import re

from bs4 import BeautifulSoup

from base import http_get, result, safe
from matching import best_matches, find_by_id

SOURCES = {
    "adviser":  {"label": "SEBI investment adviser register", "prefix": "INA"},
    "analyst":  {"label": "SEBI research analyst register",   "prefix": "INH"},
    "broker":   {"label": "SEBI stock broker register",       "prefix": "INZ"},
}
# TODO(Rahul): open the SEBI page in a browser, use DevTools > Network to find the
# request the search box sends, and fill these in. Keep the URL we show users separate.
LIST_URLS = {"adviser": "", "analyst": "", "broker": ""}


def valid_reg_format(reg_id: str, kind="adviser") -> bool:
    return bool(re.fullmatch(SOURCES[kind]["prefix"] + r"\d{9}", reg_id.strip().upper()))


def parse_records(html: str, kind="adviser"):
    """Rows -> [{'name','id'}]. Works on a live response or a page saved from the browser."""
    pat = re.compile(SOURCES[kind]["prefix"] + r"\d{9}", re.I)
    out = []
    for tr in BeautifulSoup(html, "html.parser").find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        reg = next((m.group(0).upper() for c in cells if (m := pat.search(c))), None)
        if reg:
            name = max((c for c in cells if not pat.search(c)), key=len, default="")
            out.append({"name": name, "id": reg})
    return out


def search(query, kind="adviser", saved_html_path=None):
    src, url = SOURCES[kind]["label"], LIST_URLS[kind]

    def run():
        if saved_html_path:
            html = open(saved_html_path, encoding="utf-8", errors="ignore").read()
        elif url:
            html = http_get(url).text
        else:
            raise RuntimeError("SEBI URL not configured yet (see LIST_URLS)")
        records = parse_records(html, kind)
        if not records:
            raise RuntimeError("page loaded but no records parsed; layout may have changed")
        matches = find_by_id(query, records) if valid_reg_format(query, kind) else best_matches(query, records)
        return result(src, query, "found" if matches else "not_found", matches, source_url=url or "")

    return safe(src, query, url, run)


if __name__ == "__main__":
    import json, sys
    print(json.dumps(search(sys.argv[1], saved_html_path=sys.argv[2] if len(sys.argv) > 2 else None),
                     indent=2, ensure_ascii=False))
