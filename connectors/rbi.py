"""RBI lists for the agent: one call, one result in the team's contract (connectors/net.result).

Owner: Rahul. agent.py calls search_rbi(name) for names that look like finance companies.
It checks Rahul's three hand-downloaded RBI lists in this order and returns the most telling one:
  1. Alert List (unauthorised forex platforms)  -> warning_list: being found is bad
  2. Registered NBFCs, if the match is strong      -> register: being found is good
  3. Cancelled NBFC registrations                  -> warning_list
  4. Otherwise the registered-list answer (not found, or a near miss to clarify)
Step 2 comes before 3 so a registered firm ("Bajaj Finance") isn't shown next to a different,
cancelled firm with a similar name ("Bajaj Finserv").
"""
from connectors import rbi_alert_list, rbi_nbfc
from connectors.lists import status_of
from connectors.net import result

STRONG = 95  # same bar verdict.py uses for "matched"


def _convert(r, list_type, limitations):
    """Rahul's result shape (base.result) -> team contract. Found = 90+, like the other lists."""
    status = r["status"] if r["status"] == "unavailable" else status_of(r["matches"])
    return result(r["source"], "RBI", r["query"], status, r["matches"], r["source_url"],
                  limitations=limitations, list_type=list_type, detail=r["note"], checked_at=r["checked_at"])


def search_rbi(name):
    alert = _convert(rbi_alert_list.search(name), "warning_list",
                     "RBI's Alert List is not exhaustive: not being on it doesn't mean a platform is authorised.")
    if alert["status"] == "found":
        return alert

    registered = _convert(rbi_nbfc.search(name), "register",
                          "Registered NBFCs and ARCs only. A registered NBFC doesn't make an app or agent "
                          "claiming to work with it genuine.")
    if registered["status"] == "found" and registered["matches"][0]["score"] >= STRONG:
        return registered

    cancelled = _convert(rbi_nbfc.search_cancelled(name), "warning_list",
                         "This list has names only (no company ID), so a different company may share the name.")
    if cancelled["status"] == "found":
        return cancelled
    return registered


if __name__ == "__main__":
    # Lookups against the RBI files in data/ (downloaded by hand from rbi.org.in on 1 Nov 2026).
    checks = {"Exness": ("RBI Alert List (unauthorised forex platforms)", "found"),
              "Bajaj Finance Limited": ("RBI list of registered NBFCs and ARCs", "found"),
              "Agroha Savings Limited": ("RBI list of NBFCs whose registration was cancelled", "found"),
              "Totally Fake Loans Pvt Ltd": ("RBI list of registered NBFCs and ARCs", "not_found")}
    for q, (source, status) in checks.items():
        r = search_rbi(q)
        print(f"{q!r}: {r['source']} | {r['list_type']} | {r['status']} | {r['matches'][:1]}")
        assert (r["source"], r["status"]) == (source, status), r
    print("rbi.py check passed")
