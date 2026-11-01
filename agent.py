"""The agent: reads the forward, picks which official checks to run, and builds the report.

Owner: Vihan. Everything runs on this computer with no external AI service. One check = three steps:
  1. Find every checkable item: ID numbers, UPI IDs and links (connectors/ids.py) and organisation names.
  2. Pick the right official source for each item from what the message says, and run the checks.
  3. verdict.py decides every verdict with fixed rules; a template writes the explanation.
Aadhaar and PAN numbers are never looked up or sent anywhere.
"""
import io
import re
import time

import pdfplumber

import store
import verdict
from connectors import ids, lists, net

try:  # Rahul's connectors
    from connectors import sebi
except ImportError:
    sebi = None
try:
    from connectors import rbi
except ImportError:
    rbi = None


def _sebi(query):
    """Rahul's SEBI search, reshaped to our connector contract (net.result)."""
    r = sebi.search(query, "adviser")
    status = r["status"] if r["status"] == "unavailable" else lists.status_of(r["matches"])  # found = 90+, like our lists
    return {**r, "status": status, "organisation": "SEBI", "list_type": "register", "detail": r["note"],
            "limitations": "Live search of SEBI's investment adviser register only. Research analyst and broker "
                           "registers are not connected yet, so a broker will show as not found here."}


# The checks we can run: name -> function taking one string and returning the connector contract.
TOOLS = {
    "ID and link check": ids.check,
    "UGC fake university list": lists.search_ugc_fake,
    "IRDAI insurer register": lists.search_irdai,
    "AMFI distributor register": lists.search_amfi,
}
if sebi:
    TOOLS["SEBI adviser register"] = _sebi
if rbi:
    TOOLS["RBI lists"] = rbi.search_rbi


def _run(tool, value):
    try:
        return TOOLS[tool](value)
    except Exception as e:  # a connector bug must never crash a check
        return net.result(tool, "", value, "unavailable", detail=f"{type(e).__name__}: {e}"[:200])


# A run of capitalised words (allowing "of", "for", "&") that contains an organisation keyword.
PHRASE = re.compile(r"(?:[A-Z][\w&'-]*|\([A-Z]{2,}\))(?:\s+(?:[A-Z][\w&'-]*|\([A-Z]{2,}\)|of|for|and|&))*")
ORG_WORDS = re.compile(r"\b(?:Pvt|Private|Limited|Ltd|Investments?|Advis[eo]rs?|Advisory|Capital|Securities|"
                       r"Finance|Finserv|Fintech|Insurance|Assurance|Universit(?:y|ies)|Vishwavidyalaya|Wealth|"
                       r"Research|Loans?|Asset Management|Broking)\b")


def org_names(text):
    names = []
    text = re.sub(r"\b(Pvt|Ltd|Co|Inc|No|Regn)\.", r"\1", text)  # so a full stop can end a phrase
    for m in PHRASE.finditer(text):
        name = re.sub(r"\s+(?:of|for|and|&)$", "", m.group(0).strip(" .,"))
        if len(name.split()) >= 2 and ORG_WORDS.search(name) and name not in names:
            names.append(name)
    return names


def investigate(text, on_step):
    """Regexes find IDs and organisation names; keywords in the message pick the register for each."""
    checks = []

    def add(item, tool, value):
        on_step(f"Checking “{item}” with the {tool}")
        checks.append({"item": item, "tool": tool, "result": _run(tool, value)})

    for kind, value in ids.find_ids(text):
        if kind in ("aadhaar", "pan"):
            continue  # never sent anywhere; nothing to look up
        add(value, "ID and link check", value)
        if kind == "arn":
            add(value, "AMFI distributor register", value)
        if kind == "sebi_reg" and value.upper().startswith("INA") and sebi:
            add(value, "SEBI adviser register", value)
    mentions_mf = re.search(r"mutual fund|\bAMFI\b|\bARN\b|distributor", text, re.I)
    for name in org_names(text):
        low = name.lower()
        if "universit" in low or "vishwavidyalaya" in low:
            add(name, "UGC fake university list", name)
        elif "insurance" in low or "assurance" in low:
            add(name, "IRDAI insurer register", name)
        elif re.search(r"financ|finserv|fintech|loan", low) and rbi:
            add(name, "RBI lists", name)
        elif mentions_mf:
            add(name, "AMFI distributor register", name)
        elif sebi:
            add(name, "SEBI adviser register", name)
    return checks


def _template_explanation(report):
    lines = [verdict.HEADLINES[report["headline"]][0] + "."]
    lines += [f"{c['item']}: {c['reason']}" for c in report["checks"] if c["verdict"] != "MATCHED"][:3]
    lines += [f["reason"] for f in report["flags"]][:2]
    return " ".join(lines)


def run_check(text, files=(), language="en", on_step=print):
    """The whole pipeline. files = [(filename, bytes, mime type)]; PDFs are read for their text."""
    start = time.time()
    for name, data, mime in files:
        if mime == "application/pdf":
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text += "\n" + "\n".join(p.extract_text() or "" for p in pdf.pages)
    checks = investigate(text, on_step)
    flags = verdict.warning_signs(text)
    for c in checks:
        c["verdict"], c["reason"] = verdict.decide(c["result"])

    items = {}
    for c in checks:
        items.setdefault(c["item"], []).append(c["verdict"])
    items = {item: verdict.item_verdict(keys) for item, keys in items.items()}
    headline = verdict.headline(items.values(), flags)
    report = {"headline": headline, "checks": checks, "items": items, "flags": flags, "language": language,
              "mode": "rules", "next_steps": verdict.NEXT_STEPS[headline].get(language) or verdict.NEXT_STEPS[headline]["en"]}
    report["explanation"] = _template_explanation(report)
    report["duration_ms"] = int((time.time() - start) * 1000)
    store.log_check(text, headline, [c["verdict"] for c in checks], report["duration_ms"], report["mode"])
    return report


if __name__ == "__main__":
    # Smoke test against live sources.
    rep = run_check("Get a degree from Commercial University Ltd in 30 days! Pay registration fee of Rs 5000 "
                    "to ravi.k@okaxis within 24 hours. Details: bit.ly/fastdegree", on_step=lambda s: None)
    verdicts = {c["item"]: c["verdict"] for c in rep["checks"]}
    assert verdicts.get("Commercial University Ltd") == "ON_WARNING_LIST", verdicts
    assert verdicts.get("bit.ly/fastdegree") == "INVALID", verdicts
    assert rep["headline"] == "HIGH_RISK", rep["headline"]
    if sebi:
        r = _sebi("29K Investment Advisers")
        assert r["status"] in ("found", "unavailable"), r
        print("SEBI:", r["status"], r["matches"][:1])
    print("agent.py check passed:", verdicts)
