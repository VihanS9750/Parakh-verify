"""SEBI enforcement orders: is this firm or person named in one? Live search of SEBI's own order listing.

Owner: Vihan. SEBI publishes every enforcement order (final orders, adjudication orders, settlements) with a
title like "Order in the matter of Mr Yash Garg Proprietor of Yash Trading Academy". We send the name to the
search box on SEBI's orders page (a public form, honest user agent, 1 request a second) and fuzzy-match the
titles. Being named in an order is not proof of fraud: some orders close a case. We show the title, date
and link so the person can read it.
"""
import re

from rapidfuzz import fuzz

from connectors import net

PAGE = "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=0"
SEARCH = "https://www.sebi.gov.in/sebiweb/ajax/home/getnewslistinfo.jsp"
FOUND_AT = 90
NOISE = re.compile(r"\b(?:pvt|private|ltd|limited|llp|the|and|&|of|mr|mrs|ms|india)\b\.?", re.I)


def _clean(text):
    return " ".join(NOISE.sub(" ", text.lower()).split())


def search_orders(name):
    """One result in the team contract, list_type "orders": found = named in at least one SEBI order title."""
    words = " ".join(w for w in name.split() if not NOISE.fullmatch(w))  # SEBI's box matches exact words only
    form = {"nextValue": "1", "next": "s", "search": words, "fromDate": "", "toDate": "", "fromYear": "",
            "toYear": "", "deptId": "", "sid": "2", "ssid": "9", "smid": "0", "ssidhidden": "9", "intmid": "-1",
            "sText": "Enforcement", "ssText": "Orders", "smText": "", "doDirect": "-1"}
    source = "SEBI enforcement orders"
    limits = ("Searches the titles of SEBI's published enforcement orders. Being named in an order isn't proof "
              "of wrongdoing (some orders close a case), and an order may name a different person with the same name.")
    if len(_clean(name).split()) < 2:  # one word ("Capital") would match hundreds of unrelated orders
        return net.result(source, "SEBI", name, "needs_user", source_url=PAGE, list_type="orders",
                          limitations=limits, detail="Name too short to search orders reliably.")
    try:
        html = net.post(SEARCH, form, headers={"Referer": PAGE}).text
    except Exception as e:  # site down: say so, never guess
        return net.result(source, "SEBI", name, "unavailable", source_url=PAGE, list_type="orders",
                          limitations=limits, detail=f"{type(e).__name__}")
    matches = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S)[1:]:
        date = re.search(r"<td[^>]*>(.*?)</td>", row, re.S)
        link = re.search(r"href=['\"]([^'\"]+)['\"][^>]*>(.*?)</a>", row, re.S)
        if date and link:
            title = " ".join(re.sub(r"<[^>]+>", "", link.group(2)).split())
            score = int(fuzz.partial_ratio(_clean(name), _clean(title)))
            matches.append({"name": title, "id": date.group(1).strip(), "score": score, "url": link.group(1)})
    matches.sort(key=lambda m: -m["score"])
    found = bool(matches) and matches[0]["score"] >= FOUND_AT
    return net.result(source, "SEBI", name, "found" if found else "not_found", matches[:3],
                      source_url=matches[0]["url"] if found else PAGE, list_type="orders", limitations=limits,
                      detail=f"{sum(m['score'] >= FOUND_AT for m in matches)} order(s) name it." if found else "")


if __name__ == "__main__":
    # Live lookups. Yash Trading Academy is from test forward INV-2 (a SEBI order of 27 Mar 2026 names it).
    r = search_orders("Yash Trading Academy")
    assert r["status"] == "found" and "Yash Trading Academy" in r["matches"][0]["name"], r
    print(r["matches"][0]["id"], "|", r["matches"][0]["name"])
    assert search_orders("Capital")["status"] == "needs_user"
    print("Zerodha Broking:", search_orders("Zerodha Broking Ltd")["status"])
    print("sebi_orders.py live checks passed")
