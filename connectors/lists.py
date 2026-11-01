"""Official lists we can read live: UGC fake universities, IRDAI insurers and brokers, AMFI distributors.

Owner: Atharva. All three were tested from an Indian connection on 1 Nov 2026 and accept our honest
user agent. Lists are cached for 24 hours in store.py; AMFI is searched live every time.
"""
import re

import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz, process

from connectors.net import get, result
from store import cached_list

STOP = {"pvt", "private", "ltd", "limited", "co", "company", "the", "llp", "inc", "of"}


def normalise(name):
    """'Axis Max Life Insurance Ltd.' -> 'axis max life insurance'. Drops Hindi script and legal suffixes."""
    name = re.sub(r"[ऀ-ॿ]+", " ", name or "")
    words = re.sub(r"[^a-z0-9 ]", " ", name.lower()).split()
    return " ".join(w for w in words if w not in STOP)


def english(text):
    """IRDAI pages print 'Hindi English' in one cell. Keep the English part."""
    return re.sub(r"\s+", " ", re.sub(r"[ऀ-ॿ]+", " ", text)).strip(" /-")


FOUND_AT = 90  # a match scoring this or more counts as "found"; verdict.py decides matched vs needs-clarification


def best_matches(query, rows, key="name", limit=3, cutoff=70):
    """Fuzzy-match a name against rows; returns rows with a 0-100 'score' (the match confidence we show).

    WRatio copes with short names ("Star Health") and extra words ("Pvt Ltd") better than plain ratios.
    """
    names = [normalise(r[key]) for r in rows]
    found = process.extract(normalise(query), names, scorer=fuzz.WRatio, limit=limit, score_cutoff=cutoff)
    return [{**rows[i], "score": round(score)} for _, score, i in found]


def status_of(matches):
    return "found" if matches and matches[0]["score"] >= FOUND_AT else "not_found"


# ---------- UGC fake universities (a warning list: being on it is bad) ----------

UGC_URL = "https://www.ugc.gov.in/universitydetails/Fakeuniversity"


def _fetch_ugc():
    html = get(UGC_URL).text
    as_on = re.search(r"as on\s+([A-Za-z]+,?\s*\d{4})", html)
    rows = []
    for tr in BeautifulSoup(html, "html.parser").select("table tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(cells) >= 3 and cells[0].isdigit():
            full = cells[2]
            rows.append({"name": full.split(",")[0].strip(), "id": f"UGC fake list #{cells[0]}",
                         "state": cells[1], "address": full})
    if not rows:
        raise ValueError("UGC page layout changed: no rows found")
    return rows, as_on.group(1) if as_on else ""


def search_ugc_fake(name):
    limits = ("UGC's list of fake universities only. Not being on it does not prove a university is "
              "recognised; check UGC's list of recognised universities too.")
    try:
        rows, fetched_at, as_on, stale = cached_list("ugc_fake_universities", _fetch_ugc)
    except Exception as e:
        return result("UGC list of fake universities", "UGC", name, "unavailable", source_url=UGC_URL,
                      limitations=limits, list_type="warning_list", detail=str(e)[:200])
    matches = best_matches(name, rows)
    detail = f"List dated {as_on}." + (" Site unreachable; using our last copy." if stale else "")
    return result("UGC list of fake universities", "UGC", name, status_of(matches),
                  matches, UGC_URL, limits, "warning_list", detail, checked_at=fetched_at)


# ---------- IRDAI insurers and brokers (registers: being on them is good) ----------

IRDAI_PAGES = {
    "life insurer": "https://irdai.gov.in/list-of-life-insurers1",
    "general insurer": "https://irdai.gov.in/list-of-general-insurers",
    "health insurer": "https://irdai.gov.in/list-of-health-insurers",
    "insurance broker": "https://irdai.gov.in/list-of-brokers",
}


def _fetch_irdai(kind, url):
    def fetch():
        table = BeautifulSoup(get(url).text, "html.parser").find("table")
        trs = table.find_all("tr")
        head = [c.get_text(" ", strip=True).lower() for c in trs[0].find_all(["td", "th"])]
        name_col = next(i for i, h in enumerate(head) if "name" in h or "insurer" in h)
        id_col = next((i for i, h in enumerate(head) if re.match(r"(regn|cor\.? ?no)", h)), None)
        rows = []
        for tr in trs[1:]:
            cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
            if len(cells) > name_col and english(cells[name_col]):
                rows.append({"name": english(cells[name_col]), "kind": kind,
                             "id": f"IRDAI {cells[id_col]}" if id_col is not None and cells[id_col] else ""})
        return rows, ""
    return fetch


def search_irdai(name):
    limits = ("IRDAI lists of life, general and health insurers and insurance brokers. Individual agents and "
              "corporate agents are not covered here.")
    rows, fetched, failed = [], [], []
    for kind, url in IRDAI_PAGES.items():
        try:
            part, fetched_at, _, stale = cached_list(f"irdai_{kind.replace(' ', '_')}", _fetch_irdai(kind, url))
            rows += part
            fetched.append(fetched_at)
        except Exception:
            failed.append(kind)
    if not rows:
        return result("IRDAI registered insurers and brokers", "IRDAI", name, "unavailable",
                      source_url=IRDAI_PAGES["life insurer"], limitations=limits)
    matches = best_matches(name, rows)
    detail = f"Could not load: {', '.join(failed)}." if failed else ""
    return result("IRDAI registered insurers and brokers", "IRDAI", name, status_of(matches),
                  matches, "https://irdai.gov.in/list-of-licensed-insurance-entities", limits, "register",
                  detail, checked_at=min(fetched))


# ---------- AMFI mutual fund distributors (register, searched live) ----------

AMFI_API = "https://www.amfiindia.com/api/distributor-agent"
AMFI_PAGE = "https://www.amfiindia.com/locate-distributor"


def _amfi_rows(data):
    return [{"name": d.get("ARNHolderName", "").strip(), "id": f"ARN-{d.get('ARN')}", "city": d.get("City"),
             "valid_till": (d.get("ARNValidTill") or "")[:10]} for d in data]


def search_amfi(name_or_arn):
    limits = ("AMFI's register of mutual fund distributors (ARN holders). Distributors are not SEBI-registered "
              "investment advisers and may not charge advisory fees.")
    arn = re.fullmatch(r"(?:ARN[-\s]?)?(\d{1,7})", name_or_arn.strip(), re.I)

    def lookup(term):
        return get(AMFI_API, strOpt="ALL", search=term, page=1, pageSize=25).json().get("data") or []

    try:
        data = lookup(arn.group(1) if arn else name_or_arn)
        if not arn and not any(m["score"] >= FOUND_AT for m in best_matches(name_or_arn, _amfi_rows(data))):
            # AMFI only finds exact substrings, so "Sunil Kamdar" misses "Sunil A Kamdar".
            # Retry on the first and the longest word of the name, and pool the results.
            words = normalise(name_or_arn).split()
            for word in dict.fromkeys([words[0], max(words, key=len)] if words else []):
                data += lookup(word)
    except (requests.RequestException, ValueError) as e:
        return result("AMFI mutual fund distributor register", "AMFI", name_or_arn, "unavailable",
                      source_url=AMFI_PAGE, limitations=limits, detail=str(e)[:200])
    rows = _amfi_rows(data)
    if arn:
        matches = [{**r, "score": 100} for r in rows if r["id"] == f"ARN-{arn.group(1).lstrip('0')}"
                   or r["id"] == f"ARN-{arn.group(1)}"]
    else:
        matches = best_matches(name_or_arn, rows)
    return result("AMFI mutual fund distributor register", "AMFI", name_or_arn,
                  status_of(matches), matches, AMFI_PAGE, limits)


if __name__ == "__main__":
    # Live self-check. Run from the project folder:  python -m connectors.lists
    # These entries were on the official pages on 1 Nov 2026.
    r = search_ugc_fake("Commercial University Ltd")
    assert r["status"] == "found" and r["matches"][0]["score"] >= 90, r
    r = search_irdai("Life Insurance Corporation of India")
    assert r["status"] == "found" and r["matches"][0]["score"] >= 90, r
    r = search_amfi("ARN-108")
    assert r["status"] == "found" and r["matches"][0]["name"], r
    r = search_amfi("Zzqx Imaginary Wealth Gurus")
    assert r["status"] in ("not_found", "found"), r
    print("lists.py live checks passed")
