"""UPI QR check: read what a payment QR will do, and compare it with what the message says.

Owner: Vihan. A UPI QR is just text: a payee handle, a payee NAME THE QR'S MAKER TYPED, an amount and a note.
Nothing in it proves who owns the account, so we never say "verified". We state the facts that are real
(it sends money, how much, which handle it pays) and check them against the forward's story.
Decoding is offline (OpenCV); the picture is never sent anywhere, like every screenshot in Parakh.
"""
import re
from urllib.parse import parse_qs, unquote, urlparse

import store
from connectors.net import result

SEBI_CHECK = "https://siportal.sebi.gov.in/intermediary/sebi-check"

# What the message promises, in words. Narrow on purpose: a normal bill must not trip these.
CLAIMS = [
    ("refund_or_prize", r"(?:refund|cash ?back|prize|lottery|reward|you(?:'ve| have)? won)\b.{0,80}\b(?:scan|qr)\b|"
                        r"\b(?:scan|qr)\b[^.]{0,40}\b(?:to|and)\s+(?:receive|claim|collect|get your)"),
    ("government", r"income ?tax|\bGST\b|customs|police|court|e-?challan|\bRTO\b|\bTRAI\b|\bEPFO\b|\bUIDAI\b|"
                   r"ministry|government of india|\bCBI\b|enforcement directorate|penalty|fine of"),
    ("bank", r"\bKYC\b|account\b.{0,30}(?:block|suspend|freez|deactivat)|bank (?:account )?(?:verification|update)"),
    ("investment", r"\bSEBI\b|invest|stock|trading|advis|tips?\b|returns?\b|demat"),
]
MONEY_IN = re.compile(CLAIMS[0][1], re.I | re.S)
NOT_BY_QR = {  # claims for which a forwarded QR is never how the money is really collected or sent
    "government": "Government dues are not collected through a QR sent in a message.",
    "bank": "A bank never asks you to scan a QR to fix your account or KYC.",
}


def decode(data):
    """The text inside the first QR code in an image (bytes), or "" if there is none or it can't be read."""
    try:
        import cv2
        import numpy as np
    except ImportError:  # OpenCV not installed: no QR reading, but the rest of Parakh must keep working
        return ""
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return ""
    detector = cv2.QRCodeDetector()
    # Screenshots are often small or soft, so try the picture as it is, then enlarged, then in grey with sharp edges.
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    for attempt in (img, cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC),
                    cv2.threshold(grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]):
        text, _, _ = detector.detectAndDecode(attempt)
        if text:
            return text
    return ""


def parse(payload):
    """upi://pay?pa=...&pn=...&am=...&tn=... -> {handle, name, amount, note}, or None if it isn't a UPI payment."""
    p = urlparse(payload.strip())
    if p.scheme.lower() != "upi":
        return None
    q = {k: unquote(v[0]) for k, v in parse_qs(p.query).items()}
    if "@" not in q.get("pa", ""):
        return None
    return {"handle": q["pa"].strip(), "name": q.get("pn", "").strip(), "amount": q.get("am", "").strip(),
            "note": q.get("tn", "").strip(), "action": p.netloc.lower()}  # action is "pay" for payments


def claim_kind(text):
    """Which story the message tells, as one label (the first that fits), or "other"."""
    return next((k for k, rx in CLAIMS if re.search(rx, text, re.I)), "other")


def check(payload, message=""):
    """One UPI QR -> the connector result. `message` is the text that came with the QR (typed text and OCR)."""
    upi = parse(payload)
    if not upi:
        return result("UPI QR check", "Parakh offline rules", payload[:80], "invalid", list_type="format",
                      detail="The QR holds text that isn't a UPI payment request.",
                      limitations="Reads the QR's text only.")
    handle, suffix = upi["handle"], upi["handle"].lower().split("@")[1]
    # We name no app or bank behind a suffix: NPCI publishes no handle-to-bank list we could cite.
    # The one documented format is SEBI's '@valid' (circular of 11 Jun 2025, Annexure B).
    provider = "a SEBI-style '@valid' handle" if suffix.startswith("valid") else f"handle ending @{suffix}"
    amount = f"₹{upi['amount']}" if upi["amount"] else "an amount you type yourself"
    facts = (f"This QR sends {amount} from you to {handle} ("
             + provider
             + (f"). The name on it, '{upi['name']}', was typed by whoever made the QR" if upi["name"] else ")")
             + ". Recipient unverified: no one can confirm who owns the account from the QR.")

    problems = []
    message = f"{message} {upi['note']}"  # the QR's own note is part of the story it tells
    kind = claim_kind(message)
    if upi["action"] == "mandate":
        problems.append("This sets up a recurring automatic debit, not a one-time payment.")
    elif upi["action"] != "pay":
        problems.append("This is a payment request, not a receipt.")
    if MONEY_IN.search(message):
        problems.append("The message says you will receive money, but scanning a QR only ever sends money.")
    for k, why in NOT_BY_QR.items():
        if re.search(dict(CLAIMS)[k], message, re.I):
            problems.append(why)
    if re.fullmatch(r"\d{10}", handle.split("@")[0]) and kind in ("government", "bank", "investment"):
        problems.append("The payee is a personal mobile-number handle, not an organisation's account.")

    seen = store.remember_handle(handle, kind, payload + message)  # claims this handle was used for in other forwards
    others = sorted(seen - {kind, "other"}) if kind != "other" else []  # two specific, different stories
    if others:
        problems.append(f"This same account appeared in other forwards with different stories "
                        f"({', '.join(o.replace('_', ' ') for o in others)}).")

    detail = " ".join(problems + [facts])
    if suffix.startswith("valid"):
        detail += " Check the registration yourself on SEBI Check (link below)."
    r = result("UPI QR check", "Parakh offline rules", handle, "invalid" if problems else "needs_user",
               source_url=SEBI_CHECK if suffix.startswith("valid") else "", list_type="format", detail=detail,
               limitations="Reads the QR and compares it with the message. Before paying, make sure the name your own "
                           "UPI app shows matches who the message claims to be.")
    if problems:
        r["flag"] = {"code": "qr_mismatch", "by": "rules", "reason": problems[0]}
    return r


if __name__ == "__main__":
    import tempfile
    from io import BytesIO
    from pathlib import Path

    import qrcode

    store.DB = Path(tempfile.mkdtemp()) / "test.db"  # the test must not write to the real handle memory

    def png(text):
        buf = BytesIO()
        qrcode.make(text).save(buf, "PNG")
        return buf.getvalue()

    payload = "upi://pay?pa=refund.desk@ybl&pn=SBI%20Refund&am=4999&cu=INR&tn=refund"
    assert decode(png(payload)) == payload
    assert parse(payload) == {"handle": "refund.desk@ybl", "name": "SBI Refund", "amount": "4999",
                              "note": "refund", "action": "pay"}
    assert decode(b"not an image") == ""
    r = check(payload, "SBI: your Rs 4999 refund is pending. Scan to receive it.")
    assert r["status"] == "invalid" and "only ever sends money" in r["detail"] and "unverified" in r["detail"], r
    ok = check("upi://pay?pa=sharmakirana@oksbi&pn=Sharma%20Kirana&am=350", "Hi, shop QR for the 350 bill")
    assert ok["status"] == "needs_user" and "handle ending @oksbi" in ok["detail"], ok
    assert check("upi://pay?pa=alphawealth@validhdfc&pn=Alpha", "")["source_url"] == SEBI_CHECK
    assert parse("https://example.com") is None
    a = check("upi://pay?pa=x1@ybl&am=1", "Income Tax Department penalty, pay now")
    b = check("upi://pay?pa=x1@ybl&am=1", "You won a lottery prize. Scan this QR to claim it.")
    assert "other forwards" in b["detail"], b["detail"]
    print("upi_qr.py checks passed")
