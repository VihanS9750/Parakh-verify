"""Offline checks for ID numbers and links found in a forward, plus the official page to confirm each.

Owner: Atharva. No network needed, so these never fail on stage. A valid format does NOT prove an ID is
real (anyone can copy one); it only proves an invalid one is fake. That is why a valid ID returns
"needs_user" with the official link, and an invalid one returns "invalid".
"""
import re
from urllib.parse import urlparse

from connectors.net import result

B36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gstin_check_digit(first14):
    """GSTIN check digit: base-36 values, weights 1,2,1,2..., add quotient and remainder of each product."""
    total = 0
    for i, ch in enumerate(first14):
        product = B36.index(ch) * (1 if i % 2 == 0 else 2)
        total += product // 36 + product % 36
    return B36[(36 - total % 36) % 36]


# Verhoeff tables: Aadhaar numbers end in a Verhoeff check digit. We only use this to spot and mask them.
_D = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
      [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
      [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
      [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
_P = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
      [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
      [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]


def verhoeff_ok(digits):
    c = 0
    for i, d in enumerate(reversed(digits)):
        c = _D[c][_P[i % 8][int(d)]]
    return c == 0


# Each ID type: regex that finds it in text, a validity test, a plain name, and where a citizen confirms it.
PATTERNS = {
    "gstin": (r"\b\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b", "GST number (GSTIN)",
              "https://services.gst.gov.in/services/searchtp"),
    "pan": (r"\b[A-Z]{3}[ABCFGHJLPT][A-Z]\d{4}[A-Z]\b", "PAN",
            "https://eportal.incometax.gov.in/iec/foservices/#/pre-login/verifyYourPAN"),
    "aadhaar": (r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b", "Aadhaar number", "https://myaadhaar.uidai.gov.in/"),
    "cin": (r"\b[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}\b", "Company ID (CIN)",
            "https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html"),
    "cnr": (r"\b[A-Z]{4}\d{12}\b", "eCourts case number (CNR)", "https://services.ecourts.gov.in/ecourtindia_v6/"),
    "itd_din": (r"\bITBA/[A-Z]{2,6}/[A-Z]/[\w().-]+/\d{4}-\d{2}/\d{10}(?:\(\d\))?", "Income Tax document ID (DIN)",
                "https://www.incometax.gov.in/iec/foportal/"),
    "cbic_din": (r"\bCBIC-\d{4}\s?\d{2}\s?[A-Z0-9]{3,5}\s?\d{6}\b", "CBIC document ID (DIN)",
                 "https://esanchar.cbic.gov.in/DIN/DINSearch"),
    "sebi_reg": (r"\bIN[AHZPMBFE]\d{9}\b", "SEBI registration number",
                 "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13"),
    "arn": (r"\bARN[-\s]?\d{1,7}\b", "AMFI distributor code (ARN)", "https://www.amfiindia.com/locate-distributor"),
    "upi": (r"\b[\w.-]{2,64}@[A-Za-z]{2,64}\b(?!\.\w)", "UPI ID", "https://siportal.sebi.gov.in/intermediary/sebi-check"),
    "phone": (r"(?:\+91[\s-]?)?\b[6-9]\d{9}\b", "Mobile number", "https://sancharsaathi.gov.in/sfc/"),
    "url": (r"\b(?:https?://|www\.)[^\s<>\"']+|(?<![@\w.-])[a-z0-9-]+(?:\.[a-z0-9-]+)*"
            r"\.(?:apk|in|com|net|org|xyz|top|online|site|info|ly|gd|at|cc|io|app|link)(?:/[^\s<>\"']*)?",
            "Link", ""),
}

SEBI_PREFIX = {"INA": "investment adviser", "INH": "research analyst", "INZ": "stock broker",
               "INP": "portfolio manager", "INM": "merchant banker", "INB": "stock broker (exchange segment)",
               "INF": "stock broker (exchange segment)", "INE": "stock broker (exchange segment)"}
# SEBI circular of 11 Jun 2025, Annexure B: registered intermediaries collect through <name>.<category>@valid<bank>
VALID_UPI_CATEGORY = {"brk": "stock broker", "bti": "banker to an issue", "dp": "depository participant",
                      "ra": "research analyst", "ia": "investment adviser", "invit": "InvIT", "mf": "mutual fund",
                      "pms": "portfolio manager", "sreit": "small and medium REIT", "reit": "REIT"}
PAN_HOLDER = {"P": "individual", "C": "company", "H": "Hindu undivided family", "F": "firm",
              "A": "association of persons", "T": "trust", "B": "body of individuals", "L": "local authority",
              "J": "artificial juridical person", "G": "government"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.ly", "cutt.ly", "rb.gy", "is.gd", "shorturl.at", "goo.gl", "tiny.cc"}
GOV_WORDS = ("incometax", "gst", "cbic", "sebi", "rbi", "uidai", "aadhaar", "epfo", "pmkisan", "npci", "court",
             "police", "cybercrime", "customs", "india-post", "indiapost")


def find_ids(text):
    """Every ID-like string in the text, as (kind, value). Used by agent.investigate and for masking."""
    found, seen = [], set()
    for kind, (rx, _, _) in PATTERNS.items():
        for m in re.finditer(rx, text, re.I if kind in ("url", "upi") else 0):
            value = m.group(0).rstrip(".,;")
            if value.endswith(")") and value.count(")") > value.count("("):
                value = value[:-1]
            if kind == "upi" and ("." in value.split("@")[1] or value.lower().startswith(("http", "www"))):
                continue  # that's an email address or part of a link, not a UPI ID
            if kind == "aadhaar" and not verhoeff_ok(value.replace(" ", "")):
                continue
            if value not in seen:
                seen.add(value)
                found.append((kind, value))
    return found


def mask(text):
    """Hide Aadhaar and PAN numbers before text leaves this computer. Keeps the last 4 characters."""
    for kind, value in find_ids(text):
        if kind in ("aadhaar", "pan"):
            text = text.replace(value, "X" * (len(value) - 4) + value[-4:])
    return text


def check(value, kind=None):
    """Validate one ID or link. kind is detected when not given."""
    value = value.strip()
    if not kind:
        kind = next((k for k, v in find_ids(value)), "unknown")
    if kind == "unknown":
        return result("ID format check", "Parakh offline rules", value, "invalid", list_type="format",
                      detail="Not a recognised Indian ID number or link format.")
    _, label, link = PATTERNS[kind]
    ok, detail = True, ""
    v = value.upper().replace(" ", "")

    if kind == "gstin":
        ok = gstin_check_digit(v[:14]) == v[14]
        detail = (f"State code {v[:2]}; contains PAN {v[2:12]}. Check digit is valid." if ok else
                  f"The last character should be {gstin_check_digit(v[:14])} for this number. "
                  "A real GSTIN always passes this check.")
    elif kind == "pan":
        detail = f"Format valid; the 4th letter means the holder is a {PAN_HOLDER.get(v[3], 'unknown type')}."
    elif kind == "aadhaar":
        detail = "Looks like an Aadhaar number. Never share it with strangers; Parakh does not store it."
    elif kind == "cin":
        detail = f"{'Listed' if v[0] == 'L' else 'Unlisted'} company, state {v[6:8]}, registered {v[8:12]}."
    elif kind == "sebi_reg":
        detail = f"Format of a SEBI-registered {SEBI_PREFIX.get(v[:3], 'intermediary')}. Check it in the SEBI register."
    elif kind == "itd_din":
        detail = ("Looks like an Income Tax document ID. Every genuine notice since Oct 2019 carries one; confirm it with "
                  "'Authenticate notice/order' on the e-filing portal (no login, OTP to your mobile).")
    elif kind == "cbic_din":
        detail = "Looks like a CBIC document ID. Confirm it on CBIC's DIN search page (it asks for a captcha)."
    elif kind == "arn":
        detail = "Format of an AMFI distributor code. Check it in AMFI's register."
    elif kind == "upi":
        name, handle = value.lower().split("@")
        category = VALID_UPI_CATEGORY.get(name.rsplit(".", 1)[-1]) if "." in name else None
        if handle.startswith("valid"):
            detail = (f"Uses SEBI's '@valid' format{f' for a {category}' if category else ''}. "
                      "Confirm the name behind it on SEBI Check.")
        else:
            detail = ("Ordinary UPI handle. Since Oct 2025, SEBI-registered advisers and brokers collect money "
                      "through handles like name.ia@validhdfc. If this person claims to be SEBI-registered, that's a red flag.")
    elif kind == "url":
        return check_link(value)
    elif kind == "phone":
        detail = "An ordinary mobile number. Government departments don't threaten or demand money over WhatsApp calls."

    if not ok:
        return result(f"{label} format check", "Parakh offline rules", value, "invalid", source_url=link,
                      list_type="format", detail=detail,
                      limitations="Checks the format and check digit only.")
    return result(f"{label} format check", "Parakh offline rules", value, "needs_user", source_url=link,
                  list_type="format", detail=detail,
                  limitations="A valid format doesn't prove the ID was really issued. Confirm it on the official page.")


OFFICIAL_NON_GOV = {"rbi.org.in", "npci.org.in"}  # official bodies whose sites aren't on .gov.in


def check_link(url, claimed_body=""):
    """Flag links that pretend to be government sites, shorteners that hide the destination, and app files.
    claimed_body: the government body the message says it comes from (e.g. "Income Tax Department"), if any."""
    host = urlparse(url if "://" in url else "http://" + url).netloc.lower().removeprefix("www.")
    path = url.lower()
    problems = []
    if host.endswith((".gov.in", ".nic.in")) or host in OFFICIAL_NON_GOV:
        detail = f"{host} is on an official Indian government domain."
    else:
        if claimed_body:
            problems.append(f"The message says it is from {claimed_body}, but {host} is not a government site "
                            "(.gov.in or .nic.in).")
        if any(w in host for w in GOV_WORDS):
            problems.append(f"{host} uses a government-sounding name but is not on .gov.in or .nic.in.")
        if host in SHORTENERS:
            problems.append(f"{host} is a link shortener that hides where the link really goes.")
        if path.endswith(".apk") or ".apk?" in path:
            problems.append("It downloads an Android app file (.apk) from outside the Play Store.")
        detail = " ".join(problems) or f"{host} is not a government domain; that alone isn't proof of anything."
    return result("Link check", "Parakh offline rules", url, "invalid" if problems else "needs_user",
                  source_url="", list_type="format", detail=detail,
                  limitations="Looks only at the address; it does not open the link.")


if __name__ == "__main__":
    # GSTIN check digit: flipping the last character must fail, and our own computed digit must pass.
    good = "27AAPFU0939F1Z" + gstin_check_digit("27AAPFU0939F1Z")
    assert check(good)["status"] == "needs_user"
    bad = good[:14] + ("A" if good[14] != "A" else "B")
    assert check(bad)["status"] == "invalid"
    assert check("https://incometax-refund.in/claim")["status"] == "invalid"
    assert check("https://www.incometax.gov.in/iec/foportal/")["status"] == "needs_user"
    assert check("bit.ly/abc123")["status"] == "invalid"
    assert find_ids("Click: https://wwtax.icu") == [("url", "https://wwtax.icu")]  # any https link, any ending
    assert check_link("https://wwtax.icu", "Income Tax Department")["status"] == "invalid"
    assert check_link("https://www.incometax.gov.in/iec/", "Income Tax Department")["status"] == "needs_user"
    assert check("ravi.sharma@ybl")["detail"].startswith("Ordinary UPI")
    assert "stock broker" in check("abc.brk@validhdfc")["detail"]
    assert [k for k, _ in find_ids("Ref ITBA/AST/F/17/2025-26/1035917840 and CBIC-2024 11 DL00 123456")] == \
        ["itd_din", "cbic_din"]
    assert check("INA000017523")["status"] == "needs_user"
    kinds = [k for k, _ in find_ids("Pay to 9876543210 or ravi@ybl, SEBI reg INA000017523, see bit.ly/x1")]
    assert kinds == ["sebi_reg", "upi", "phone", "url"], kinds
    assert "ABCPE1234F" not in mask("PAN ABCPE1234F")
    print("ids.py checks passed")
