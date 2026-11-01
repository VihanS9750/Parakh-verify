"""Bank impersonation check: the message names a bank, but does its link go to that bank's own website?

Owner: Vihan. The official domains below were read from each bank's live website on 1 Nov 2026: the old
domain redirects to the bank's .bank.in domain, which RBI required banks to move to by 31 Oct 2025
(RBI circular RBI/2025-26/28). A link that is not on a listed domain is not proof of fraud, and the bank
has not said anything about the message: we only report that the link does not match the bank named.
Related companies (SBI Card, HDFC Life, ICICI Prudential...) have their own sites and are not matched.

Not covered (their sites didn't confirm to us on 1 Nov 2026, so we list nothing rather than guess):
Bank of India, Punjab & Sind Bank, South Indian Bank, Paytm Payments Bank, India Post Payments Bank.
Punjab & Sind Bank's old psbindia.com redirected to an unrelated betting site that day, so it is NOT listed.
"""
import re
from urllib.parse import urlparse

from connectors import ids, net

LISTED_ON = "2026-11-01"
# key: (name in reports, verified official domains, regex for the name in text, home page, brand words that
#       show a domain imitating the bank, older domains of the bank that did not respond to us)
BANKS = {
    "SBI": ("State Bank of India", ("sbi.co.in", "sbi.bank.in", "onlinesbi.sbi", "onlinesbi.sbi.bank.in"),
            r"\bSBI\b(?!\s*(?:Card|Life|General|Mutual|MF|Caps|Securities))|State Bank of India|\bYONO\b",
            "https://sbi.bank.in", ("sbi", "onlinesbi", "sbibank", "sbionline"), ()),
    "HDFC Bank": ("HDFC Bank", ("hdfcbank.com", "hdfc.bank.in"),
                  r"\bHDFC\b(?!\s*(?:Life|ERGO|Securities|AMC|Mutual|Sec|Capital|Credila))",
                  "https://www.hdfc.bank.in", ("hdfc", "hdfcbank"), ()),
    "ICICI Bank": ("ICICI Bank", ("icicibank.com", "icici.bank.in"),
                   r"\bICICI\b(?!\s*(?:Prudential|Pru|Lombard|Securities|Direct|Venture|Home))",
                   "https://www.icici.bank.in", ("icici", "icicibank"), ()),
    "Axis Bank": ("Axis Bank", ("axisbank.com", "axis.bank.in"), r"\bAxis\s+Bank\b", "https://www.axis.bank.in",
                  ("axisbank",), ()),
    "PNB": ("Punjab National Bank", ("pnbindia.in", "pnb.bank.in"),
            r"\bPNB\b(?!\s*(?:Housing|MetLife))|Punjab\s+National\s+Bank", "https://pnb.bank.in",
            ("pnb", "pnbindia", "pnbonline"), ()),
    "Bank of Baroda": ("Bank of Baroda", ("bankofbaroda.bank.in", "bankofbaroda.in"), r"Bank\s+of\s+Baroda",
                       "https://bankofbaroda.bank.in", ("baroda", "bankofbaroda"), ()),
    "Canara Bank": ("Canara Bank", ("canarabank.bank.in", "canarabank.com"), r"\bCanara\s+Bank\b",
                    "https://www.canarabank.bank.in", ("canara", "canarabank"), ()),
    "Union Bank": ("Union Bank of India", ("unionbankofindia.bank.in",), r"\bUnion\s+Bank(?:\s+of\s+India)?\b",
                   "https://www.unionbankofindia.bank.in", ("unionbank", "unionbankofindia"),
                   ("unionbankofindia.co.in",)),
    "Indian Bank": ("Indian Bank", ("indianbank.bank.in", "indianbank.in"), r"\bIndian\s+Bank\b",
                    "https://indianbank.bank.in", ("indianbank",), ()),
    "Central Bank": ("Central Bank of India", ("centralbank.bank.in",), r"Central\s+Bank\s+of\s+India",
                     "https://centralbank.bank.in", ("centralbank", "centralbankofindia"),
                     ("centralbankofindia.co.in",)),
    "Indian Overseas Bank": ("Indian Overseas Bank", ("iob.bank.in", "iob.in"), r"Indian\s+Overseas\s+Bank|\bIOB\b",
                             "https://www.iob.bank.in", ("iob", "indianoverseas"), ()),
    "UCO Bank": ("UCO Bank", ("uco.bank.in",), r"\bUCO\s+Bank\b", "https://uco.bank.in", ("uco", "ucobank"),
                 ("ucobank.com",)),
    "Bank of Maharashtra": ("Bank of Maharashtra", ("bankofmaharashtra.bank.in",), r"Bank\s+of\s+Maharashtra",
                            "https://bankofmaharashtra.bank.in", ("bankofmaharashtra",), ("bankofmaharashtra.in",)),
    "Kotak Bank": ("Kotak Mahindra Bank", ("kotak.bank.in", "kotak.com"),
                   r"\bKotak\b(?!\s*(?:Securities|Life|General|AMC|Mutual|Mahindra\s+(?:Life|General|Prime|AMC|"
                   r"Securities|Asset)))", "https://www.kotak.bank.in", ("kotak",), ()),
    "IndusInd Bank": ("IndusInd Bank", ("indusind.bank.in", "indusind.com"), r"\bIndusInd\b",
                      "https://www.indusind.bank.in", ("indusind",), ()),
    "Yes Bank": ("Yes Bank", ("yes.bank.in", "yesbank.in"), r"\bYes\s+Bank\b", "https://www.yes.bank.in",
                 ("yesbank",), ()),
    "IDBI Bank": ("IDBI Bank", ("idbi.bank.in", "idbibank.in"),
                  r"\bIDBI\b(?!\s*(?:Federal|Capital|Intech|Mutual|MF))", "https://www.idbi.bank.in",
                  ("idbi", "idbibank"), ()),
    "IDFC FIRST Bank": ("IDFC FIRST Bank", ("idfcfirst.bank.in", "idfcfirstbank.com"),
                        r"\bIDFC\b(?!\s*(?:Mutual|AMC|Infra))", "https://www.idfcfirst.bank.in",
                        ("idfc", "idfcfirst", "idfcfirstbank"), ()),
    "Federal Bank": ("Federal Bank", ("federal.bank.in", "federalbank.co.in"), r"\bFederal\s+Bank\b",
                     "https://federal.bank.in", ("federalbank",), ()),
    "RBL Bank": ("RBL Bank", ("rbl.bank.in", "rblbank.com"), r"\bRBL\b", "https://www.rbl.bank.in",
                 ("rbl", "rblbank"), ()),
    "Bandhan Bank": ("Bandhan Bank", ("bandhan.bank.in", "bandhanbank.com"), r"\bBandhan\s+Bank\b",
                     "https://bandhan.bank.in", ("bandhanbank",), ()),
    "AU Small Finance Bank": ("AU Small Finance Bank", ("au.bank.in", "aubank.in"),
                              r"\bAU\s+(?:Small\s+Finance\s+)?Bank\b", "https://www.au.bank.in", ("aubank",), ()),
    "Karnataka Bank": ("Karnataka Bank", ("karnatakabank.bank.in", "karnatakabank.com"), r"\bKarnataka\s+Bank\b",
                       "https://www.karnatakabank.bank.in", ("karnatakabank",), ()),
    "J&K Bank": ("Jammu & Kashmir Bank", ("jkb.bank.in", "jkbank.com"),
                 r"\bJ\s*&\s*K\s+Bank\b|Jammu\s+(?:and|&)\s+Kashmir\s+Bank", "https://jkb.bank.in",
                 ("jkbank",), ()),
    "City Union Bank": ("City Union Bank", ("cityunionbank.bank.in", "cityunionbank.com"),
                        r"\bCity\s+Union\s+Bank\b", "https://cityunionbank.bank.in", ("cityunion",), ()),
}
TOOL = "Bank identity check"


def host_of(url):
    return (urlparse(url if "://" in url else "http://" + url).hostname or "").lower().removeprefix("www.")


def on_domain(host, domains):
    """True for the domain itself or a real subdomain: evil-sbi.co.in and sbi.co.in.evil.com do not match."""
    return any(host == d or host.endswith("." + d) for d in domains)


def imitates(host, brands):
    """The domain's own name carries the bank's name: long brand words anywhere, short ones as a whole word."""
    return any(b in host if len(b) >= 6 else re.search(rf"(?<![a-z0-9]){b}(?![a-z0-9])", host) for b in brands)


def banks_named(text, hosts=()):
    """Banks named in the message text, or imitated by a link's own name."""
    return [key for key, (_, _, rx, _, brands, _) in BANKS.items()
            if re.search(rx, text, re.I) or any(imitates(h, brands) for h in hosts)]


def check_text(text):
    """One check per (bank named, link in the message). Returns [{item, tool, result}] in the team contract."""
    urls = [(u, host_of(u)) for k, u in ids.find_ids(text) if k == "url"]
    urls = [(u, h) for u, h in urls if h and h not in ids.SHORTENERS]  # a short link's destination: links.inspect
    named = banks_named(text, [h for _, h in urls])
    checks = []
    for url, host in urls:
        for key in named:
            name, domains, _, home, brands, legacy = BANKS[key]
            if on_domain(host, domains):
                status = "needs_user"
                detail = (f"{host} is an official {name} domain (listed {LISTED_ON}). That doesn't prove the "
                          "message itself came from the bank.")
            elif on_domain(host, legacy):
                status = "needs_user"
                detail = (f"{host} is an older {name} address that did not respond to us on {LISTED_ON}; the bank "
                          f"has moved to {domains[0]}. Open the bank's own site to confirm.")
            else:
                status = "invalid"
                detail = (f"The message mentions {name}, but {host} is not one of its official domains "
                          f"({', '.join(domains[:2])}).")
                if imitates(host, brands):
                    detail += " The address imitates the bank's name."
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
    S = lambda t: [c["result"]["status"] for c in check_text(t)]
    assert on_domain("sbi.co.in", BANKS["SBI"][1]) and on_domain("retail.onlinesbi.sbi", BANKS["SBI"][1])
    assert not on_domain("sbi.co.in.evil.com", BANKS["SBI"][1]) and not on_domain("evil-sbi.co.in", BANKS["SBI"][1])
    assert banks_named("Dear SBI customer") == ["SBI"] and banks_named("SBI Card offer") == []
    assert banks_named("HDFC Life policy") == [] and banks_named("Your Axis Bank account") == ["Axis Bank"]
    assert banks_named("Reserve Bank of India circular, State Bank of India") == ["SBI"]  # no mix-ups
    assert banks_named("Indian Overseas Bank alert") == ["Indian Overseas Bank"] and banks_named("Kotak Securities") == []
    assert S("Dear SBI Customer, your account will be blocked today. Update your Aadhaar through sbi-kyc-update.in") \
        == ["invalid"]
    assert "imitates" in check_text("Dear SBI Customer, update at sbi-kyc-update.in")[0]["result"]["detail"]
    assert S("SBI: update your KYC at https://sbi.bank.in/kyc or visit onlinesbi.sbi") == ["needs_user", "needs_user"]
    assert S("Pay at bit.ly/x1 to SBI") == []  # a short link's destination is unknown
    assert S("fill the form at sbi-kyc-update.in") == ["invalid"]  # the domain imitates the name
    assert S("see sbicard.com and hdfcsec.com and icicidirect.com") == []  # sibling companies, own sites
    assert sorted(S("HDFC Bank and ICICI Bank: see https://www.hdfcbank.com/offers")) == ["invalid", "needs_user"]
    # the new banks
    assert S("Canara Bank KYC: https://www.canarabank.bank.in/kyc") == ["needs_user"]
    assert S("Canara Bank KYC: canara-kyc-update.club") == ["invalid"]
    assert S("Your Kotak account is blocked, login at kotak-secure.live") == ["invalid"]
    assert S("Bank of Baroda: bobworld-rewards.xyz now") == ["invalid"]  # named in text, link not Baroda's
    assert S("Union Bank: see https://www.unionbankofindia.bank.in/en/home") == ["needs_user"]
    assert S("Union Bank: see unionbankofindia.co.in") == ["needs_user"]  # older address: neutral, not an accusation
    assert S("Yes Bank KYC at yesbank-verify.cc") == ["invalid"] and S("IDFC FIRST Bank: idfcfirstbank.com") == ["needs_user"]
    assert S("a biobank.com study") == [] and S("RBL notice") == []  # no link, no check
    print(f"banks.py checks passed ({len(BANKS)} banks)")
