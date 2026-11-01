"""The agent: reads the forward, picks which official checks to run, and builds the report.

Owner: Vihan. One check = four steps:
  1. Get the text: pasted text, PDF text (pdfplumber) and screenshot text (Tesseract OCR, offline).
  2. Investigate. The AI brain (brain.py) calls our checks as tools; with no key, or if the AI fails,
     plain rules here find the items and pick the checks instead.
  3. verdict.py decides every verdict with fixed rules. The AI never decides a verdict.
  4. The AI explains the result in English or Hindi (a template does it when AI is off).
The AI only ever gets masked text: Aadhaar, PAN and mobile numbers keep just their last 4 characters
(ids.mask, applied inside brain.py). Screenshots are read here (OCR) and never sent to the AI: an image
can't be masked. Aadhaar and PAN are never looked up.
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
from connectors import banks, ids, links, lists, net, sebi_orders, upi_qr, urlhaus

try:  # Rahul's connectors
    from connectors import sebi
except ImportError:
    sebi = None
try:
    from connectors import rbi, rbi_alert_list
except ImportError:
    rbi = None


SEBI_PREFIX = {"INA": "adviser", "INH": "analyst", "INZ": "broker"}


def _sebi_one(query, kind):
    """Rahul's SEBI search of one register, reshaped to our connector contract (net.result)."""
    r = sebi.search(query, kind)
    status = r["status"] if r["status"] == "unavailable" else lists.status_of(r["matches"])  # found = 90+, like our lists
    return {**r, "status": status, "organisation": "SEBI", "list_type": "register", "detail": r["note"],
            "limitations": "Live search of SEBI's register. Equity-segment brokers only; SEBI returns at most 25 "
                           "records per search, and lists hold legal company names, not app or brand names."}


def _sebi(query):
    """A SEBI number goes to its own register. A name could be an adviser, research analyst or broker, so it is
    searched in all three, one after another (SEBI asks for 1 request a second), stopping at a strong match."""
    q = query.strip().upper()
    if q[:3] in SEBI_PREFIX and q[3:].isdigit():
        return _sebi_one(q, SEBI_PREFIX[q[:3]])
    kinds = ["broker", "adviser", "analyst"] if re.search(r"brok|securities|stock", query, re.I) else \
            ["adviser", "analyst", "broker"]
    results = []
    for kind in kinds:
        results.append(_sebi_one(query, kind))
        if results[-1]["matches"] and results[-1]["matches"][0]["score"] >= verdict.STRONG:
            return results[-1]
    found = [r for r in results if r["status"] == "found"]
    down = [r for r in results if r["status"] == "unavailable"]
    if found or not down:  # the closest name across the three registers
        best = max(found or results, key=lambda r: r["matches"][0]["score"] if r["matches"] else 0)
        return best if found else {**best, "source": "SEBI registers (advisers, research analysts, brokers)"}
    return down[0]  # a register didn't answer, so we can't say "not found"


_answers = {}  # ponytail: in memory, kept while the app runs; a dated SQLite copy if restarts become common


def _remembered(fn):
    """Keep a slow live search's answer, so the same name checked again (e.g. in a demo) is instant.
    The answer keeps its original checked_at time. A failed lookup is never kept."""
    def run(query):
        key = (fn.__name__, " ".join(query.lower().split()))
        if key not in _answers:
            r = fn(query)
            if r["status"] == "unavailable":
                return r
            _answers[key] = r
        return _answers[key]
    return run


# The checks we can run: name -> function taking one string and returning the connector contract.
TOOLS = {
    "ID and link check": ids.check,
    "UGC fake university list": lists.search_ugc_fake,
    "IRDAI insurer register": lists.search_irdai,
    "AMFI distributor register": lists.search_amfi,
    "SEBI enforcement orders": _remembered(sebi_orders.search_orders),
}
if sebi:
    TOOLS["SEBI registers"] = _remembered(_sebi)  # up to 3 live searches at 1 a second: the slowest check
if rbi:
    TOOLS["RBI lists"] = rbi.search_rbi  # company names: Alert List, registered and cancelled NBFCs
    TOOLS["RBI forex Alert List"] = lambda q: rbi._convert(  # a platform's name or website
        rbi_alert_list.search(q), "warning_list",
        "RBI's Alert List is not exhaustive: not being on it doesn't mean a platform is authorised.")


def _run(tool, value):
    try:
        return TOOLS[tool](value)
    except Exception as e:  # a connector bug must never crash a check
        return net.result(tool, "", value, "unavailable", detail=f"{type(e).__name__}: {e}"[:200])


# A run of capitalised words (allowing "of", "for", "&") that contains an organisation keyword.
PHRASE = re.compile(r"(?:[A-Z][\w&'-]*|\([A-Z]{2,}\))(?:\s+(?:[A-Z][\w&'-]*|\([A-Z]{2,}\)|of|for|and|&))*")
ORG_WORDS = re.compile(r"\b(?:Pvt|Private|Limited|Ltd|Investments?|Advis[eo]rs?|Advisory|Capital|Securities|"
                       r"Finance|Finserv|Fintech|Insurance|Assurance|Universit(?:y|ies)|Vishwavidyalaya|Wealth|"
                       r"Research|Loans?|Asset Management|Broking|Academy)\b")


def org_names(text):
    names = []
    text = re.sub(r"\b(Pvt|Ltd|Co|Inc|No|Regn)\.", r"\1", text)  # so a full stop can end a phrase
    for m in PHRASE.finditer(text):
        name = re.sub(r"\s+(?:of|for|and|&)$", "", " ".join(m.group(0).split()).strip(" .,"))  # one line, even across OCR line breaks
        if len(name.split()) >= 2 and ORG_WORDS.search(name) and name not in names:
            names.append(name)
    return names


# A message presenting itself as coming from a government body. SEBI and RBI are left out on purpose:
# genuine brokers and lenders write "SEBI registered" or "RBI registered NBFC" all the time.
GOV_CLAIM = re.compile(r"income ?tax department|assessment order|\bGST (?:department|council)|customs department|"
                       r"\bpolice\b|cyber ?cell|\bcourt\b|e-?challan|\bRTO\b|traffic police|\bTRAI\b|\bEPFO\b|"
                       r"\bUIDAI\b|ministry of|government of india|india post|\bCBI\b|enforcement directorate", re.I)


def investigate(text, on_step):
    """Regexes find IDs and organisation names; keywords in the message pick the register for each."""
    checks = []
    claim = GOV_CLAIM.search(text)

    def add(item, tool, value):
        on_step(f"Checking “{item}” with the {tool}")
        checks.append({"item": item, "tool": tool, "result": _run(tool, value)})

    for kind, value in ids.find_ids(text):
        if kind in ("aadhaar", "pan"):
            continue  # never sent anywhere; nothing to look up
        if kind == "url":  # a "government" message's link must be on a government site
            for tool, fn in (("ID and link check", ids.check_link), ("Website age and redirect check", links.inspect)):
                on_step(f"Checking “{value}” with the {tool}")
                checks.append({"item": value, "tool": tool, "result": fn(value, claim.group(0) if claim else "")})
        else:
            add(value, "ID and link check", value)
        if kind == "arn":
            add(value, "AMFI distributor register", value)
        if kind == "sebi_reg" and value.upper()[:3] in SEBI_PREFIX and sebi:
            add(value, "SEBI registers", value)
        if kind == "url" and rbi and re.search(r"forex|currency|trading|crypto|binary|dollar|\bfx\b", text, re.I):
            add(value, "RBI forex Alert List", value)
    for c in banks.check_text(text):  # a bank is named: does each link go to that bank's own domain?
        on_step(f"Checking “{c['item']}” against {c['result']['source']}")
        checks.append(c)
    mentions_mf = re.search(r"mutual fund|\bAMFI\b|\bARN\b|distributor", text, re.I)
    # Only search SEBI when the message is about investing: a shop or a hospital is never in SEBI's registers,
    # and "not found" there would sound like an accusation.
    about_investing = re.search(r"\bSEBI\b|invest|stock|share market|trading|demat|portfolio|returns?\b|profit|"
                                r"tips?\b|broker|advis", text, re.I)
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
        elif sebi and about_investing:
            add(name, "SEBI registers", name)  # run_check follows up with SEBI's enforcement orders
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
    """The whole pipeline. files = [(filename, bytes, mime type)]: PDFs, screenshots and voice notes."""
    start = time.time()
    qr_codes = []  # text of every QR code found in a screenshot (decoded offline, never sent anywhere)
    for name, data, mime in files:
        if mime == "application/pdf":
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text += "\n" + "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif mime.startswith("image/"):  # read here, never sent anywhere: an image can't be masked
            on_step(f"Reading the text in {name}")
            image_text = read_image(data)
            qr = upi_qr.decode(data)
            if qr:
                on_step(f"Found a QR code in {name}")
                qr_codes.append(qr)
            else:
                on_step(f"No readable QR code in {name} (if it has one, send a sharper picture)")
            if not image_text.strip():
                on_step(f"Couldn't read any text in {name}" +
                        ("" if Path(TESSERACT).exists() else " (Tesseract isn't installed, see README)") +
                        ". Screenshots are never sent to the AI, so paste the text instead.")
            text += "\n" + image_text
        elif mime.startswith("audio/"):  # parked: not reachable from the app yet (voice notes come after text + images)
            on_step(f"Listening to {name}")
            try:
                heard = brain.transcribe(data, name)
            except brain.openai.OpenAIError as e:
                heard = ""
                on_step(f"Couldn't transcribe it ({type(e).__name__}).")
            text += "\n" + heard
            on_step(f"Heard: “{heard[:160]}”" if heard else "No speech-to-text available (needs GROQ_API_KEY).")

    ai = None
    if brain.available() and text.strip():
        # Only masked text leaves this computer: brain.py runs ids.mask on everything it sends; no images.
        found = brain.investigate(text, list(TOOLS), _run, on_step)
        if found:
            checks, extra, ai = found
        else:
            on_step("AI unavailable; switching to rules-only checks.")
    if not ai:
        checks, extra = investigate(text, on_step), {}
    else:
        # Safety net: the rules' checks run too, so a name the AI shortened or skipped is still checked in full.
        # An AI check is dropped when the rules checked the same thing with the same source
        # (one item contains the other, e.g. "AIIPHS" in the full name, or "U651..." in "CIN: U651...").
        rule_checks = investigate(text, on_step)
        same = lambda a, b: a["tool"] == b["tool"] and (a["item"].lower() in b["item"].lower() or b["item"].lower() in a["item"].lower())
        checks = [c for c in checks if not any(same(c, r) for r in rule_checks)] + rule_checks

    # Follow-up step: every firm or person searched in SEBI's registers (by the AI or the rules) is also
    # searched in SEBI's enforcement orders, whether the registers knew it or not.
    done = {c["item"].lower() for c in checks if c["tool"] == "SEBI enforcement orders"}
    for c in list(checks):
        if c["tool"] == "SEBI registers" and c["item"].lower() not in done and not ids.find_ids(c["item"]):
            done.add(c["item"].lower())
            on_step(f"Following up: searching SEBI's enforcement orders for “{c['item']}”")
            checks.append({"item": c["item"], "tool": "SEBI enforcement orders",
                           "result": _run("SEBI enforcement orders", c["item"])})

    for qr in qr_codes:  # a QR is compared with the words that came with it
        if upi_qr.parse(qr):
            item = f"UPI QR to {upi_qr.parse(qr)['handle']}"
            on_step(f"Checking “{item}” against the message")
            checks.append({"item": item, "tool": "UPI QR check", "result": upi_qr.check(qr, text)})
        else:  # any other QR (a link, usually) goes through the link check
            on_step(f"Checking the QR's link “{qr[:60]}”")
            checks.append({"item": qr[:80], "tool": "ID and link check", "result": ids.check_link(qr)})
            checks.append({"item": qr[:80], "tool": "URLhaus malware URL list", "result": urlhaus.check(qr)})

    flags = verdict.warning_signs(text)
    seen = {f["code"] for f in flags}
    for c in checks:  # warning signs found by a check, e.g. a website registered last week
        flag = c["result"].get("flag")
        if flag and flag["code"] not in seen:
            seen.add(flag["code"])
            flags.append(flag)
    for c in extra.get("claims", []) if isinstance(extra.get("claims"), list) else []:
        # A warning sign the AI spotted is kept only if its type is one we know and the words it quotes are
        # really in the message (a claim with no support in the forward is dropped, never shown).
        kind, quote = (c.get("type"), c.get("text")) if isinstance(c, dict) else (None, None)
        grounded = isinstance(quote, str) and len(quote) >= 4 and " ".join(quote.lower().split()) in " ".join(text.lower().split())
        if kind in brain.CLAIM_TYPES and grounded and kind not in seen:
            seen.add(kind)
            flags.append({"code": kind, "reason": f"“{quote}”: wording that looks like a warning sign ({kind.replace('_', ' ')}).",
                          "by": "AI"})
    for c in checks:
        c["verdict"], c["reason"] = verdict.decide(c["result"], c.get("claimed_id", ""))

    items = {}
    for c in checks:
        items.setdefault(c["item"], []).append(c["verdict"])
    items = {item: verdict.item_verdict(keys) for item, keys in items.items()}
    headline = verdict.headline(items.values(), flags)
    report = {"headline": headline, "checks": checks, "items": items, "flags": flags, "language": language,
              "summary": extra.get("summary", ""), "evidence": verdict.evidence_strength(items.values(), flags), "mode": f"AI: {ai[2]}" if ai else "rules only",
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
    verdicts = rep["items"]  # one verdict per item: the most telling of its checks
    assert verdicts.get("Commercial University Ltd") == "ON_WARNING_LIST", verdicts
    assert verdicts.get("bit.ly/fastdegree") == "HIDDEN_DESTINATION", verdicts
    assert rep["headline"] == "HIGH_RISK", rep["headline"]
    if sebi:
        r = _sebi("29K Investment Advisers")
        assert r["status"] in ("found", "unavailable"), r
        print("SEBI:", r["status"], r["matches"][:1])
    print("agent.py check passed:", verdicts)
