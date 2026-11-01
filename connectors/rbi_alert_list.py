"""RBI Alert List: forex platforms/websites that are NOT authorised by RBI.
Being FOUND here is the warning sign. Not being here proves nothing: RBI says the list
"is not exhaustive", so a missing name must never be reported as safe.
RBI blocks scripts, so the PDF is downloaded by hand and turned into a CSV (name, id=website)."""
import os
import re
from urllib.parse import urlparse

from connectors.base import result, safe
from connectors.local_list import load_csv, pdf_to_csv, search_list

SOURCE = "RBI Alert List (unauthorised forex platforms)"
SOURCE_URL = "https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=4235"
LIST_DATE = "2025-11-19"      # "Updated as on" date printed on the PDF
DOWNLOADED_ON = "2026-11-01"  # the day we saved the PDF
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
PDF_PATH = os.path.join(DATA, "rbi_alert_list_2025-11-19.pdf")
CSV_PATH = os.path.join(DATA, "rbi_alert_list.csv")
NOTE = (f"From RBI's Alert List updated {LIST_DATE}, downloaded {DOWNLOADED_ON}. "
        "The list is not exhaustive: not being on it does not mean authorised.")


def domain(text):
    """'https://www.Exness.com/in' -> 'exness.com'. Returns '' if text isn't a web address."""
    t = text.strip().lower()
    if not re.search(r"[a-z0-9-]+\.[a-z]{2,}", t) or " " in t:
        return ""
    host = urlparse(t if "//" in t else "//" + t).hostname or ""
    return host.removeprefix("www.")


def find_by_domain(query, records):
    """Exact website match, also catching sub-domains (in.exness.com -> exness.com)."""
    q = domain(query)
    out = []
    for r in records:
        d = domain(r["id"])
        if q and d and (q == d or q.endswith("." + d)):
            out.append({"name": r["name"], "id": r["id"], "score": 100})
    return out


def search(query):
    def run():
        if domain(query):
            matches = find_by_domain(query, load_csv(CSV_PATH))
            res = result(SOURCE, query, "found" if matches else "not_found", matches,
                         source_url=SOURCE_URL, data_as_of=DOWNLOADED_ON)
        else:
            res = search_list(SOURCE, query, CSV_PATH, SOURCE_URL, DOWNLOADED_ON)
        res["note"] = NOTE
        return res

    return safe(SOURCE, query, SOURCE_URL, run)


if __name__ == "__main__":
    import json, sys
    # python -m connectors.rbi_alert_list build        -> PDF to CSV (run once after downloading)
    # python -m connectors.rbi_alert_list "Exness"     -> search by name or website
    if sys.argv[1] == "build":
        print(pdf_to_csv(PDF_PATH, CSV_PATH, name_col=1, id_col=2), "entries saved")
    else:
        print(json.dumps(search(sys.argv[1]), indent=2, ensure_ascii=False))
