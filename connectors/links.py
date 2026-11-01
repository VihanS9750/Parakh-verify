"""Link evidence without opening the scam page: where a short link leads, and how old the website is.

Owner: Vihan. Two public lookups:
  1. Short links (bit.ly etc.): we ask the shortener where it redirects (one request, not followed).
  2. Website age: the public RDAP registry (rdap.org), the official successor to WHOIS.
A website registered in the last NEW_DAYS days becomes a warning sign; scam sites are usually days or weeks old.
"""
from datetime import date, datetime
from urllib.parse import urlparse

import requests

from connectors import ids, net

NEW_DAYS = 90
TWO_PART = ("co.in", "org.in", "net.in", "gov.in", "ac.in", "nic.in", "firm.in", "gen.in", "ind.in", "co.uk")


def host_of(url):
    return urlparse(url if "://" in url else "http://" + url).netloc.lower().removeprefix("www.")


def registered_domain(host):
    """api.teledema.scoding.com -> scoding.com; abc.co.in -> abc.co.in"""
    parts = host.split(".")
    return ".".join(parts[-3:] if ".".join(parts[-2:]) in TWO_PART else parts[-2:])


def expand(url):
    """Where a short link leads, from the shortener's own redirect header. The destination is never opened."""
    r = requests.head(url if "://" in url else "https://" + url, headers=net.HEADERS, timeout=net.TIMEOUT,
                      allow_redirects=False)
    return r.headers.get("Location", "")


def registered_on(domain):
    """The date the domain was registered, from RDAP ("" if the registry doesn't say)."""
    try:
        events = net.get(f"https://rdap.org/domain/{domain}").json().get("events", [])
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None  # no record: taken down, or never registered
        raise
    return next((e["eventDate"][:10] for e in events if e.get("eventAction") == "registration"), "")


def inspect(url, claimed_body=""):
    """One result in the team contract. A website younger than NEW_DAYS adds a "flag" (a warning sign)."""
    details, flag, status = [], None, "needs_user"
    try:
        if host_of(url) in ids.SHORTENERS:
            target = expand(url)
            if target and host_of(target) not in ids.SHORTENERS:
                details.append(f"This short link leads to {target}.")
                hidden = ids.check_link(target, claimed_body)
                if hidden["status"] == "invalid":
                    status = "invalid"
                    details.append(hidden["detail"])
                url = target
        host = host_of(url)
        if host.endswith((".gov.in", ".nic.in")) or host in ids.OFFICIAL_NON_GOV:
            return net.result("Website age and redirect check", "RDAP domain registry", url, status, source_url="",
                              list_type="format", detail=" ".join(details + [f"{host} is a government site."]))
        domain = registered_domain(host)
        born = registered_on(domain)
        if born:
            days = (date.today() - datetime.fromisoformat(born).date()).days
            details.append(f"{domain} was registered on {born} ({days} days ago).")
            if days < NEW_DAYS:
                flag = {"code": "new_website", "by": "rules",
                        "reason": f"The website {domain} was registered only {days} days ago. Scam sites are usually "
                                  "days or weeks old; real banks, regulators and companies have had theirs for years."}
        elif born is None:
            details.append(f"No public registry record for {domain}: it may have been taken down, or its registry "
                           "doesn't publish records (common for .edu and some country domains).")
        else:
            details.append(f"The registry doesn't publish when {domain} was registered.")
    except (requests.RequestException, ValueError) as e:
        return net.result("Website age and redirect check", "RDAP domain registry", url, "unavailable",
                          list_type="format", detail=f"Couldn't look this up ({type(e).__name__}).")
    r = net.result("Website age and redirect check", "RDAP domain registry", url, status,
                   source_url=f"https://lookup.icann.org/en/lookup?name={registered_domain(host_of(url))}",
                   list_type="format", detail=" ".join(details),
                   limitations="Looks up the registry record only; it never opens the website itself.")
    r["flag"] = flag
    return r


if __name__ == "__main__":
    # Live lookups.
    assert registered_domain("api.teledema.scoding.com") == "scoding.com"
    assert registered_domain("www.abc.co.in") == "abc.co.in"
    old = inspect("https://www.google.com")
    assert old["status"] == "needs_user" and old["flag"] is None and "1997" in old["detail"], old
    print("google.com:", old["detail"])
    print("wwtax.icu:", inspect("https://wwtax.icu")["detail"])
    print("links.py live checks passed")
