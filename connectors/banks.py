"""Bank impersonation check: the message names a bank, but does its link go to that bank's own website?

Owner: Vihan. The official domains below were read from each bank's live website on 1 Nov 2026: the old
domain redirects to the bank's .bank.in domain, which RBI required banks to move to by 31 Oct 2025
(RBI circular RBI/2025-26/28). A link that is not on a listed domain is not proof of fraud, and the bank
has not said anything about the message: we only report that the link does not match the bank named.
Related companies (SBI Card, HDFC Life, ICICI Prudential...) have their own sites and are not matched.
"""
import re
from urllib.parse import urlparse

from connectors import ids, net

LISTED_ON = "2026-11-01"
BANKS = {
    "SBI": ("State Bank of India", ("sbi.co.in", "sbi.bank.in", "onlinesbi.sbi", "onlinesbi.sbi.bank.in"),
            r"\bSBI\b(?!\s*(?:Card|Life|General|Mutual|MF|Caps|Securities))|State Bank of India|\bYONO\b",
            "https://sbi.bank.in"),
    "HDFC Bank": ("HDFC Bank", ("hdfcbank.com", "hdfc.bank.in"),
                  r"\bHDFC\b(?!\s*(?:Life|ERGO|Securities|AMC|Mutual|Sec|Capital|Credila))",
                  "https://www.hdfc.bank.in"),
    "ICICI Bank": ("ICICI Bank", ("icicibank.com", "icici.bank.in"),
                   r"\bICICI\b(?!\s*(?:Prudential|Pru|Lombard|Securities|Direct|Venture|Home))",
                   "https://www.icici.bank.in"),
    "Axis Bank": ("Axis Bank", ("axisbank.com", "axis.bank.in"), r"\bAxis\s+Bank\b", "https://www.axis.bank.in"),
    "PNB": ("Punjab National Bank", ("pnbindia.in", "pnb.bank.in"),
            r"\bPNB\b(?!\s*(?:Housing|MetLife))|Punjab\s+National\s+Bank", "https://pnb.bank.in"),
}
TOOL = "Bank identity check"


def host_of(url):
    return (urlparse(url if "://" in url else "http://" + url).hostname or "").lower().removeprefix("www.")


def on_domain(host, domains):
    """True for the domain itself or a real subdomain: evil-sbi.co.in and sbi.co.in.evil.com do not match."""
    return any(host == d or host.endswith("." + d) for d in domains)


def banks_named(text):
    return [key for key, (_, _, rx, _) in BANKS.items() if re.search(rx, text, re.I)]


def check_text(text):
    """One check per (bank named, link in the message). Returns [{item, tool, result}] in the team contract."""
    named = banks_named(text)
    checks = []
    for kind, url in ids.find_ids(text):
        host = host_of(url) if kind == "url" else ""
        if not host or host in ids.SHORTENERS:  # a short link's destination is unknown: links.inspect handles it
            continue
        for key in named:
            name, domains, _, home = BANKS[key]
            if on_domain(host, domains):
                status = "needs_user"
                detail = (f"{host} is an official {name} domain (listed {LISTED_ON}). That doesn't prove the "
                          "message itself came from the bank.")
            else:
                status = "invalid"
                brand = key.split()[0].lower()
                detail = (f"The message mentions {name}, but {host} is not one of its official domains "
                          f"({', '.join(domains[:2])}).")
                if brand in host:
                    detail += f" The address imitates the name '{brand}'."
                if "xn--" in host:
                    detail += " It uses lookalike characters."
                detail += " This shows the link doesn't match the bank; it is not a statement by the bank."
            checks.append({"item": url, "tool": TOOL, "result": net.result(
                f"{name} official domains", "RBI .bank.in mandate, bank websites", url, status, source_url=home,
                list_type="format", detail=detail,
                limitations="Domain list read from each bank's own website on 1 Nov 2026. A link on another "
                            "domain is not proof of fraud; a link on the right domain doesn't authenticate the sender.")})
    return checks


if __name__ == "__main__":
    assert on_domain("sbi.co.in", BANKS["SBI"][1]) and on_domain("retail.onlinesbi.sbi", BANKS["SBI"][1])
    assert not on_domain("sbi.co.in.evil.com", BANKS["SBI"][1]) and not on_domain("evil-sbi.co.in", BANKS["SBI"][1])
    assert banks_named("Dear SBI customer") == ["SBI"] and banks_named("SBI Card offer") == []
    assert banks_named("HDFC Life policy") == [] and banks_named("Your Axis Bank account") == ["Axis Bank"]
    fake = check_text("Dear SBI Customer, your account will be blocked today. Update KYC at sbi-kyc-update.in")
    assert [c["result"]["status"] for c in fake] == ["invalid"] and "imitates" in fake[0]["result"]["detail"], fake
    real = check_text("SBI: update your KYC at https://sbi.bank.in/kyc or visit onlinesbi.sbi")
    assert [c["result"]["status"] for c in real] == ["needs_user", "needs_user"], real
    assert check_text("Pay at bit.ly/x1 to SBI") == []  # a short link's destination is unknown
    assert [c["result"]["status"] for c in check_text("fill the form at sbi-kyc-update.in")] == ["invalid"]  # the domain imitates the name
    assert check_text("see sbicard.com and hdfcsec.com and icicidirect.com") == []  # sibling companies, own sites
    two = check_text("HDFC Bank and ICICI Bank: see https://www.hdfcbank.com/offers")
    assert sorted(c["result"]["status"] for c in two) == ["invalid", "needs_user"], two
    print("banks.py checks passed")
