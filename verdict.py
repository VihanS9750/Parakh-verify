"""Plain rules that turn connector results into verdicts. No AI decides a verdict.

Owner: Vihan. Everything a judge sees as "the answer" comes from this file, so it can be read and
explained line by line. We never call a named firm a "fraud"; we say what the official record shows.
"""
import re
from datetime import date

STRONG = 95      # a register match this good, with no close rival, counts as "matched"
RIVAL_GAP = 3    # another match within 3 points of the best one makes the result ambiguous

# key: (English label, Hindi label, colour)
VERDICTS = {
    "MATCHED": ("Matches the official record", "आधिकारिक रिकॉर्ड से मेल खाता है", "green"),
    "ON_WARNING_LIST": ("On an official warning list", "आधिकारिक चेतावनी सूची में दर्ज है", "red"),
    "INVALID": ("Fails an authenticity check", "प्रामाणिकता जाँच में विफल", "red"),
    "NOT_FOUND": ("Not found in the checked register", "जाँचे गए रजिस्टर में नहीं मिला", "orange"),
    "NEEDS_CLARIFICATION": ("Needs clarification", "स्पष्टता ज़रूरी है", "orange"),
    "NOT_LISTED": ("Not on the official warning list", "आधिकारिक चेतावनी सूची में नहीं है", "blue"),
    "CONFIRM_OFFICIALLY": ("Format OK: confirm on the official page", "फ़ॉर्मेट सही है: आधिकारिक पेज पर पुष्टि करें", "blue"),
    "COULDNT_VERIFY": ("Couldn't verify right now", "अभी पुष्टि नहीं हो सकी", "gray"),
}


def _same_id(a, b):
    return re.sub(r"[^A-Z0-9]", "", (a or "").upper()).lstrip("0") in re.sub(r"[^A-Z0-9]", "", (b or "").upper())


def decide(r, claimed_id=""):
    """One connector result -> (verdict key, reason in plain English)."""
    status, kind = r["status"], r["list_type"]
    if status == "unavailable":
        return "COULDNT_VERIFY", "The official source didn't respond. Open the link to check it yourself."
    if status == "invalid":
        return "INVALID", r["detail"]
    if status == "needs_user":
        return "CONFIRM_OFFICIALLY", r["detail"]

    top = r["matches"][0] if r["matches"] else None
    if kind == "warning_list":
        if status == "found" and top["score"] >= STRONG:
            return "ON_WARNING_LIST", f"'{top['name']}' appears on the {r['source']}. {r['detail']}"
        if status == "found":
            return "NEEDS_CLARIFICATION", (f"A similar name is on the {r['source']}: '{top['name']}' "
                                           f"({top['score']}% match).")
        return "NOT_LISTED", f"Not on the {r['source']}. That alone doesn't prove it's genuine."

    # A register: being found is good, but only if the match is clear.
    if status == "not_found":
        hint = f" Closest name: '{top['name']}' ({top['score']}% match)." if top else ""
        return "NOT_FOUND", f"No record matching '{r['query']}' in the {r['source']}.{hint}"
    rivals = [m for m in r["matches"][1:] if m["score"] >= top["score"] - RIVAL_GAP]
    if top["score"] < STRONG or rivals:
        others = f" and {len(rivals)} other similar name(s)" if rivals else ""
        return "NEEDS_CLARIFICATION", (f"Closest record is '{top['name']}' {top.get('id', '')} "
                                       f"({top['score']}% match){others}. Check the exact name and number.")
    if claimed_id and top.get("id") and not _same_id(claimed_id, top["id"]):
        return "NEEDS_CLARIFICATION", (f"The name matches '{top['name']}', but the official number is "
                                       f"{top['id']}, not {claimed_id} as the message says.")
    if top.get("valid_till") and top["valid_till"] < date.today().isoformat():
        return "NEEDS_CLARIFICATION", f"'{top['name']}' is registered, but the registration expired on {top['valid_till']}."
    return "MATCHED", f"Found '{top['name']}' {top.get('id', '')} in the {r['source']}."


# Warning signs in the wording of the message itself. (code, pattern, plain-English reason)
RED_FLAGS = [
    ("guaranteed_returns",
     r"guarantee[ds]?\s+(?:\w+\s+)?(?:returns?|profits?|income)|(?:profit|returns?)\s+guaranteed|assured\s+(?:returns?|profits?)|"
     r"double your money|risk[- ]free|sure[- ]?shot|highly safe|\d+\s?%\s*(?:to\s*\d+\s?%\s*)?(?:returns?|profit)|"
     r"\d+(?:\.\d+)?\s?%\s*(?:per\s+|a\s+|every\s+)?(?:day|daily|week|weekly|month|monthly)|daily\s+\d+k",
     "Promises fixed, guaranteed or 'sure shot' returns. No SEBI-registered adviser is allowed to guarantee returns."),
    ("sebi_claim_no_number",
     r"^(?!.*\bIN[AHZPM]\d{9}\b)(?=.*SEBI\s*(?:regd|reg\.|registered)).*",
     "Claims to be SEBI-registered but gives no registration number. Since May 2026 SEBI requires registered "
     "entities to show their number on social media."),
    ("admits_unregistered",
     r"not\s+SEBI\s+regist|not\s+registered\s+with\s+SEBI|for\s+(?:stock market\s+)?(?:study|learning|educational)\s+"
     r"(?:and\s+\w+\s+)?purposes?\s+only",
     "Sells tips while saying it is not SEBI-registered or 'for learning only'. Only registered advisers may charge for advice."),
    ("tip_group",
     r"previous group has been banned|(?:join|new)\s+(?:the\s+|our\s+)?(?:vip\s+|premium\s+)?group|vip group|"
     r"premium (?:service|group|membership)|t\.me/|telegram channel",
     "Invites you into a paid tip group or channel. SEBI warns these are usually run by unregistered people."),
    ("unexpected_money",
     r"refund of rs|tax refund|amount eligible|financial assistance (?:of|ranging)|free laptops?|you have won|lottery|"
     r"cash ?back of|to every citizen|monetary reward",
     "Offers money, a refund or a free benefit out of the blue. Refunds and government schemes don't arrive by forwarded message."),
    ("official_via_link",
     r"(?=.*(?:income tax|assessment order|\bGST\b|customs|SEBI|RBI|TRAI|police|court|enforcement|e-?challan|"
     r"\bRTO\b|government|ministry))(?=.*(?:click|link|https?://|www\.|\.apk|download|"
     r"\.(?:com|net|org|xyz|icu|top|site|online|info|link)\b))",
     "Claims to come from a government body but asks you to act through a link or app. Check notices on the official portal yourself."),
    ("task_job",
     r"part[- ]time job|work from home|earn (?:rs\.?|₹)\s?\d+\s+(?:for each|per)\s+(?:like|task|review)|like (?:youtube )?videos",
     "Offers easy money for simple online tasks. Real employers never charge you to start work."),
    ("urgency",
     r"within\s+\d+\s*(?:hours?|hrs|minutes?|mins)|immediately|urgent|today only|for today|last chance|"
     r"limited (?:slots|seats)|act now|(?:block(?:ed)?|suspended|expire[sd]?)\s+(?:today|tonight)",
     "Pushes you to act fast. Pressure to decide quickly is a classic scam sign."),
    ("threat",
     r"arrest|warrant|money laundering|narcotics|drugs? (?:parcel|package)|legal action|jail|freeze order|"
     r"(?-i:\bCBI\b|\bED\b|\bFIR\b)",
     "Threatens arrest or legal action. Police and agencies don't 'arrest' people over video calls or settle cases for money."),
    ("pay_to_resolve",
     r"processing fee|registration fee|refundable deposit|security deposit|settlement amount|"
     r"(?:pay|transfer|deposit)\b.{0,40}\b(?:fee|charges|fine|penalty|verification)|transfer (?:your )?funds",
     "Asks you to pay or move money first: to unlock a loan, job or refund, or to 'verify' funds."),
    ("kyc_block",
     r"\bKYC\b.{0,60}(?:block|suspend|expire|update)|(?:block|suspend)\w*.{0,80}\bKYC\b|"
     r"account\b.{0,30}(?:will be|has been) (?:block|suspend|frozen|deactivat)",
     "Says your account or SIM will be blocked unless you act. Banks and telecom companies don't do this over SMS or WhatsApp."),
    ("secrecy",
     r"don'?t tell|do not (?:tell|inform|share this)|keep (?:this|it) (?:secret|confidential)|"
     r"stay on (?:the )?(?:video )?call|skype|video call",
     "Asks you to stay on a video call or keep it secret. Scammers isolate their targets."),
    ("otp_or_remote",
     r"\bOTP\b|one[- ]time password|anydesk|teamviewer|screen ?share|remote access",
     "Asks for an OTP or remote access to your phone. Never share these with anyone."),
    ("app_outside_store",
     r"\.apk\b|download (?:our|the) app (?:from|via|using) (?:this |the )?link",
     "Asks you to install an app from a link instead of the Play Store."),
]


def warning_signs(text):
    """Red flags in the wording, found by fixed patterns."""
    return [{"code": code, "reason": reason, "by": "rules"}
            for code, rx, reason in RED_FLAGS if re.search(rx, text, re.I | re.S)]


HEADLINES = {
    "HIGH_RISK": ("High risk: don't pay or share anything", "ज़्यादा जोखिम: पैसे न भेजें, कोई जानकारी न दें", "red"),
    "CAUTION": ("Be careful: some things couldn't be confirmed", "सावधान: कुछ बातें पुष्ट नहीं हो सकीं", "orange"),
    "CONSISTENT": ("Consistent with official records", "आधिकारिक रिकॉर्ड से मेल खाता है", "green"),
}

NEXT_STEPS = {
    "HIGH_RISK": {
        "en": ["Don't pay, don't click the links, and never share an OTP, Aadhaar or PAN.",
               "If you've already paid, call 1930 right away or report at cybercrime.gov.in. The first hour matters most.",
               "Report the number or message on Sanchar Saathi (Chakshu): sancharsaathi.gov.in"],
        "hi": ["पैसे न भेजें, लिंक पर क्लिक न करें, और OTP, आधार या PAN कभी साझा न करें।",
               "अगर पैसे भेज चुके हैं, तो तुरंत 1930 पर कॉल करें या cybercrime.gov.in पर शिकायत करें। पहला घंटा सबसे ज़रूरी है।",
               "नंबर या संदेश की शिकायत संचार साथी (चक्षु) पर करें: sancharsaathi.gov.in"],
    },
    "CAUTION": {
        "en": ["Don't pay yet. Open the official links below and confirm the name and number yourself.",
               "Ask the sender for their registration number and check it on the regulator's own website.",
               "If anyone rushes or threatens you, stop and call 1930."],
        "hi": ["अभी पैसे न भेजें। नीचे दिए आधिकारिक लिंक खोलकर नाम और नंबर खुद जाँचें।",
               "भेजने वाले से उनका पंजीकरण नंबर माँगें और नियामक की अपनी वेबसाइट पर जाँचें।",
               "अगर कोई जल्दबाज़ी करवाए या धमकाए, तो रुकें और 1930 पर कॉल करें।"],
    },
    "CONSISTENT": {
        "en": ["The names and numbers match official records as of the times shown.",
               "A match doesn't prove the sender is who they claim to be. Pay only through official channels.",
               "Still unsure? Call the organisation on the number listed on its official website."],
        "hi": ["दिखाए गए समय तक नाम और नंबर आधिकारिक रिकॉर्ड से मेल खाते हैं।",
               "मेल खाने का मतलब यह नहीं कि भेजने वाला वही है जो वह होने का दावा करता है। भुगतान केवल आधिकारिक माध्यम से करें।",
               "फिर भी संदेह है? संस्था की आधिकारिक वेबसाइट पर दिए नंबर पर कॉल करें।"],
    },
}


# When one item has several checks, the most telling verdict wins: any red or doubtful finding first,
# then a register match (which beats a mere "format OK"), then the neutral ones.
RANK = ["ON_WARNING_LIST", "INVALID", "NOT_FOUND", "NEEDS_CLARIFICATION", "MATCHED", "COULDNT_VERIFY",
        "NOT_LISTED", "CONFIRM_OFFICIALLY"]


def item_verdict(keys):
    return min(keys, key=RANK.index)


def headline(item_keys, flags):
    """Overall verdict for the whole forward, from one verdict per item plus the wording's warning signs."""
    keys = set(item_keys)
    doubtful = keys & {"NOT_FOUND", "NEEDS_CLARIFICATION"}
    if keys & {"ON_WARNING_LIST", "INVALID"} or (flags and doubtful) or len(flags) >= 2:
        return "HIGH_RISK"
    if keys and keys == {"MATCHED"} and not flags:
        return "CONSISTENT"
    return "CAUTION"


if __name__ == "__main__":
    reg = {"status": "found", "list_type": "register", "source": "test register", "query": "x", "detail": ""}
    assert decide({**reg, "matches": [{"name": "A Ltd", "id": "INA1", "score": 100}]})[0] == "MATCHED"
    assert decide({**reg, "matches": [{"name": "A", "id": "1", "score": 99}, {"name": "B", "id": "2", "score": 97}]})[0] \
        == "NEEDS_CLARIFICATION"
    assert decide({**reg, "matches": [{"name": "A", "id": "INA000017523", "score": 100}]}, "INA000099999")[0] \
        == "NEEDS_CLARIFICATION"
    assert decide({**reg, "status": "not_found", "matches": []})[0] == "NOT_FOUND"
    warn = {**reg, "list_type": "warning_list", "matches": [{"name": "Fake U", "score": 100}]}
    assert decide(warn)[0] == "ON_WARNING_LIST"
    flags = warning_signs("Our SEBI registered adviser guarantees 4% monthly returns. Join within 24 hours!")
    assert {f["code"] for f in flags} == {"guaranteed_returns", "sebi_claim_no_number", "urgency"}, flags
    assert not warning_signs("Hello, I am Sunil A Kamdar, an AMFI-registered mutual fund distributor, ARN-108.")
    assert not warning_signs("Edward edited the fir tree report")  # 'ED'/'FIR' only as capitalised words
    assert headline(["MATCHED"], []) == "CONSISTENT"
    assert headline(["MATCHED"], flags) == "HIGH_RISK"
    assert headline(["COULDNT_VERIFY"], []) == "CAUTION"
    assert item_verdict(["CONFIRM_OFFICIALLY", "MATCHED"]) == "MATCHED"
    assert item_verdict(["MATCHED", "NOT_FOUND"]) == "NOT_FOUND"
    assert decide({**warn, "status": "not_found", "matches": []})[0] == "NOT_LISTED"
    print("verdict.py checks passed")
