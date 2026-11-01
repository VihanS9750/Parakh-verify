"""The agent: reads the forward, picks which official checks to run, and builds the report.

Owner: Vihan. One check = four steps:
  1. Get the text: pasted text, PDF text (pdfplumber) and screenshot text (Tesseract OCR, offline).
  2. Investigate. The AI brain (brain.py) calls our checks as tools; with no key, or if the AI fails,
     plain rules here find the items and pick the checks instead.
  3. verdict.py decides every verdict with fixed rules. The AI never decides a verdict.
  4. The AI explains the result in English or Hindi (a template does it when AI is off).
Aadhaar, PAN and mobile numbers are masked before any text is sent to the AI, and never looked up.
Screenshots are read here (OCR) and never sent to the AI: an image can't be masked.
"""
import io
import os
import re
import shutil
import time
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image

import brain
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


# Tesseract: the installer's default place on Windows, or wherever it is on the PATH.
TESSERACT = shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = Path(__file__).with_name("tessdata")  # eng + hin language files (see README)


def read_image(data):
    """Offline OCR of a screenshot in English and Hindi. Returns "" if Tesseract isn't installed."""
    if not Path(TESSERACT).exists():
        return ""
    pytesseract.pytesseract.tesseract_cmd = TESSERACT
    langs = "eng"
    if (TESSDATA / "hin.traineddata").exists():
        os.environ["TESSDATA_PREFIX"] = str(TESSDATA)  # tells Tesseract where our language files are
        langs = "eng+hin"
    return pytesseract.image_to_string(Image.open(io.BytesIO(data)), lang=langs)


def _facts(report):
    """What the AI may use to explain the result: verdicts and reasons, nothing else."""
    return {"overall": verdict.HEADLINES[report["headline"]][0],
            "checks": [{"item": c["item"], "verdict": verdict.VERDICTS[c["verdict"]][0], "reason": c["reason"],
                        "source": c["result"]["source"], "checked_at": c["result"]["checked_at"]}
                       for c in report["checks"]],
            "warning_signs": [f["reason"] for f in report["flags"]]}


def run_check(text, files=(), language="en", on_step=print):
    """The whole pipeline. files = [(filename, bytes, mime type)]: PDFs and screenshots."""
    start = time.time()
    for name, data, mime in files:
        if mime == "application/pdf":
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text += "\n" + "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif mime.startswith("image/"):
            on_step(f"Reading the text in {name}")
            image_text = read_image(data)
            if not image_text.strip():
                on_step(f"Couldn't read any text in {name} (is Tesseract installed? see README). "
                        "Screenshots are never sent to the AI, so paste the text instead.")
            text += "\n" + image_text

    ai = None
    if brain.available():
        # Only masked text leaves this computer: no images, no Aadhaar/PAN/mobile numbers.
        found = brain.investigate(ids.mask(text), [], list(TOOLS), _run, on_step)
        if found:
            checks, extra, ai = found
        else:
            on_step("AI unavailable; switching to rules-only checks.")
    if not ai:
        checks, extra = investigate(text, on_step), {}

    flags = verdict.warning_signs(text + "\n" + extra.get("text_in_images", ""))
    seen = {f["code"] for f in flags}
    for c in extra.get("claims", []):  # warning signs the AI spotted that our patterns missed
        if c.get("type") not in seen:
            seen.add(c.get("type"))
            flags.append({"code": c.get("type", "other"), "reason": c.get("text", ""), "by": "AI"})
    for c in checks:
        c["verdict"], c["reason"] = verdict.decide(c["result"], c.get("claimed_id", ""))

    items = {}
    for c in checks:
        items.setdefault(c["item"], []).append(c["verdict"])
    items = {item: verdict.item_verdict(keys) for item, keys in items.items()}
    headline = verdict.headline(items.values(), flags)
    report = {"headline": headline, "checks": checks, "items": items, "flags": flags, "language": language,
              "summary": extra.get("summary", ""), "mode": f"AI: {ai[2]}" if ai else "rules only",
              "next_steps": verdict.NEXT_STEPS[headline].get(language) or verdict.NEXT_STEPS[headline]["en"]}
    report["explanation"] = _template_explanation(report)
    if ai:
        try:
            report["explanation"] = brain.explain(ai, _facts(report), language)
        except brain.openai.OpenAIError:
            pass  # keep the template explanation
    report["duration_ms"] = int((time.time() - start) * 1000)
    store.log_check(text, headline, [c["verdict"] for c in checks], report["duration_ms"], report["mode"])
    return report


if __name__ == "__main__":
    # Rules-only smoke test against live sources (keys hidden so the AI isn't used).
    brain.PROVIDERS = []
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
