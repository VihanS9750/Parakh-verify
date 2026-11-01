"""Parakh web app. Run:  streamlit run app.py

Owner: Rahul (frontend); redesigned on 1 Nov night: left navigation, a loading screen that shows each step,
then a report page with the answer, what to do, where to complain and the records we matched.
The page only shows what agent.run_check returns; every verdict comes from verdict.py, never from this file.
"""
import html
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

import agent
import store
import verdict
from connectors import banks, ids, lists

ASSETS = Path(__file__).with_name("assets")
st.set_page_config(page_title="Parakh", page_icon=str(ASSETS / "logo-mark.png"), layout="wide")
st.logo(str(ASSETS / "logo.png"), size="large")  # top of the left navigation

LANGS = {"English": "en", "हिन्दी": "hi"}

# Every label on the page, in both languages. T("key") picks the one for the chosen language.
UI = {
    "nav_check": ("Check a forward", "संदेश जाँचें"),
    "nav_learn": ("How to use", "कैसे इस्तेमाल करें"),
    "nav_how": ("How it works", "यह कैसे काम करता है"),
    "nav_sources": ("Sources", "स्रोत"),
    "intro": ("Paste a forwarded message or add a screenshot. Parakh checks every name, number and link in it "
              "against official Indian records and tells you what it found.",
              "कोई फ़ॉर्वर्ड किया हुआ संदेश चिपकाएँ या स्क्रीनशॉट जोड़ें। Parakh उसमें हर नाम, नंबर और लिंक को "
              "आधिकारिक भारतीय रिकॉर्ड से जाँचता है और बताता है कि क्या मिला।"),
    "privacy": ("Aadhaar, PAN and mobile numbers are masked before any text goes to the AI, and never looked up. "
                "Screenshots are read on this computer and never sent to the AI. "
                "We don't keep your messages or screenshots.",
                "आधार, PAN और मोबाइल नंबर AI को भेजने से पहले छिपा दिए जाते हैं और कभी खोजे नहीं जाते। "
                "स्क्रीनशॉट इसी कंप्यूटर पर पढ़े जाते हैं, AI को नहीं भेजे जाते। "
                "हम आपके संदेश या स्क्रीनशॉट नहीं रखते।"),
    "paste": ("Paste the message here", "संदेश यहाँ चिपकाएँ"),
    "placeholder": ("e.g. Invest ₹50,000 with ABC Investments. Our SEBI-registered adviser guarantees 4% monthly returns…",
                    "जैसे: ABC Investments में ₹50,000 लगाएँ। हमारे SEBI-पंजीकृत सलाहकार हर महीने 4% की गारंटी देते हैं…"),
    "upload": ("…or upload a screenshot or PDF", "…या स्क्रीनशॉट या PDF अपलोड करें"),
    "check": ("Check it", "जाँचें"),
    "empty": ("Paste a message or add a file first.", "पहले संदेश चिपकाएँ या फ़ाइल जोड़ें।"),
    "reading": ("Reading the screenshot…", "स्क्रीनशॉट पढ़ा जा रहा है…"),
    "ocr_title": ("Text read from the screenshot", "स्क्रीनशॉट से पढ़ा गया पाठ"),
    "ocr_help": ("Fix any wrong letter or digit before checking: one wrong digit can change the result. "
                 "This text stays on this computer unless you press Check, and then only masked text reaches the AI.",
                 "जाँचने से पहले कोई भी ग़लत अक्षर या अंक सुधारें: एक ग़लत अंक से नतीजा बदल सकता है। "
                 "जाँच दबाने तक यह पाठ इसी कंप्यूटर पर रहता है, और तब भी AI को सिर्फ़ छिपाया हुआ पाठ जाता है।"),
    "ocr_empty": ("Couldn't read any text in this image (is Tesseract installed?). Type or paste the text above.",
                  "इस चित्र में कोई पाठ नहीं पढ़ा जा सका (क्या Tesseract लगा है?)। ऊपर पाठ लिखें या चिपकाएँ।"),
    # loading screen
    "loading_title": ("Investigating your message…", "आपके संदेश की जाँच हो रही है…"),
    "loading_sub": ("Each step appears below as it happens. This usually takes a few seconds.",
                    "हर कदम होते ही नीचे दिखता है। इसमें आमतौर पर कुछ सेकंड लगते हैं।"),
    "crashed": ("Something went wrong while checking. Nothing was decided. Please try again.",
                "जाँच के दौरान कुछ गड़बड़ हुई। कोई फ़ैसला नहीं लिया गया। कृपया फिर कोशिश करें।"),
    "retry": ("Try again", "फिर कोशिश करें"),
    # report
    "report_title": ("Report", "रिपोर्ट"),
    "another": ("Check another message", "दूसरा संदेश जाँचें"),
    "result": ("Result", "नतीजा"),
    "evidence_chip": ("Evidence", "सबूत"),
    "asks": ("What the message asks: ", "संदेश क्या कहता है: "),
    "todo_title": ("What to do now", "अब क्या करें"),
    "report_title2": ("Report this message", "इस संदेश की शिकायत करें"),
    "report_bad": ("If this looks dangerous, report it so others are protected. Reports go to the official portals.",
                   "अगर यह ख़तरनाक लगे, तो शिकायत करें ताकि दूसरे सुरक्षित रहें। शिकायतें आधिकारिक पोर्टल पर जाती हैं।"),
    "report_ok": ("If something still feels wrong, you can report it to the official portals.",
                  "अगर फिर भी कुछ ग़लत लगे, तो आप आधिकारिक पोर्टल पर शिकायत कर सकते हैं।"),
    "call1930": ("Already lost money? Call 1930 right away: the first hour matters most.",
                 "पैसे जा चुके हैं? तुरंत 1930 पर कॉल करें: पहला घंटा सबसे ज़रूरी है।"),
    "btn_cyber": ("File a complaint: cybercrime.gov.in", "शिकायत दर्ज करें: cybercrime.gov.in"),
    "btn_chakshu": ("Report to Sanchar Saathi (Chakshu)", "संचार साथी (चक्षु) पर रिपोर्ट करें"),
    "btn_sebi": ("Complain to SEBI (SCORES)", "SEBI में शिकायत करें (SCORES)"),
    "btn_rbi": ("RBI Sachet: report a suspicious scheme", "RBI सचेत: संदिग्ध योजना की रिपोर्ट करें"),
    "found_title": ("What we found", "हमें क्या मिला"),
    "col_item": ("Item", "आइटम"),
    "col_result": ("Result", "नतीजा"),
    "col_record": ("What the record shows", "रिकॉर्ड क्या दिखाता है"),
    "col_where": ("Where we checked", "कहाँ जाँचा"),
    "col_verify": ("Verify", "ख़ुद जाँचें"),
    "verify": ("Open ↗", "खोलें ↗"),
    "also": ("Also checked, nothing notable: ", "यह भी जाँचा, कुछ ख़ास नहीं मिला: "),
    "nothing": ("Nothing checkable was found: no names, ID numbers, UPI IDs or links.",
                "जाँचने लायक कुछ नहीं मिला: कोई नाम, ID नंबर, UPI ID या लिंक नहीं।"),
    "warn_title": ("Warning signs in the wording", "शब्दों में चेतावनी के संकेत"),
    "by_ai": ("spotted by AI", "AI ने पकड़ा"),
    "cant_verify": ("Couldn't verify this just now. That is not a clean result: open the official page and check it yourself.",
                    "यह अभी जाँचा नहीं जा सका। यह साफ़ नतीजा नहीं है: आधिकारिक पेज खोलकर खुद जाँचें।"),
    "no_record": ("No matching record", "कोई मेल खाता रिकॉर्ड नहीं"),
    # How to use
    "learn_intro": ("Three steps, then try it yourself with a real forward.",
                    "तीन कदम, फिर एक असली फ़ॉर्वर्ड के साथ ख़ुद आज़माएँ।"),
    "s1_t": ("Paste or upload", "चिपकाएँ या अपलोड करें"),
    "s1_d": ("Paste the message, or upload a screenshot or PDF of it. For a screenshot you can fix the text we read before checking.",
             "संदेश चिपकाएँ, या उसका स्क्रीनशॉट या PDF अपलोड करें। स्क्रीनशॉट में जाँच से पहले पढ़े गए पाठ को सुधार सकते हैं।"),
    "s2_t": ("Watch it work", "होते हुए देखें"),
    "s2_d": ("Press Check it. Parakh finds every name, number and link and checks each one against the official record. You see each step as it happens.",
             "जाँचें दबाएँ। Parakh हर नाम, नंबर और लिंक ढूँढकर आधिकारिक रिकॉर्ड से जाँचता है। हर कदम होते हुए दिखता है।"),
    "s3_t": ("Read the report", "रिपोर्ट पढ़ें"),
    "s3_d": ("You get the answer, what to do now, where to complain, and the records we matched, each with a link so you can verify it yourself.",
             "आपको जवाब, अब क्या करें, शिकायत कहाँ करें, और जो रिकॉर्ड मिले वे मिलते हैं, हर एक के लिंक के साथ ताकि आप ख़ुद जाँच सकें।"),
    "means_title": ("What the results mean", "नतीजों का मतलब"),
    "m_high": ("The records or the wording point to a scam. Don't pay and don't share anything.",
               "रिकॉर्ड या शब्द धोखाधड़ी की ओर इशारा करते हैं। पैसे न भेजें और कुछ साझा न करें।"),
    "m_care": ("Parakh could not confirm the message, or found something odd. This is not a clean result: check the official page yourself.",
               "Parakh संदेश की पुष्टि नहीं कर सका, या कुछ अजीब मिला। यह साफ़ नतीजा नहीं है: आधिकारिक पेज ख़ुद जाँचें।"),
    "m_ok": ("Nothing wrong turned up in the checks. This never proves who sent the message.",
             "जाँचों में कुछ ग़लत नहीं मिला। इससे यह साबित नहीं होता कि संदेश किसने भेजा।"),
    "try_title": ("Try it yourself", "ख़ुद आज़माएँ"),
    "try_intro": ("These are real forwards from official advisories. Pick one: Parakh checks it live, the same way it checks yours.",
                  "ये आधिकारिक चेतावनियों से लिए गए असली फ़ॉर्वर्ड हैं। एक चुनें: Parakh उसे लाइव जाँचेगा, ठीक आपके संदेश की तरह।"),
    # How it works (an overview only)
    "how_intro": ("The short version, for the curious: what happens between pressing the button and seeing the report.",
                  "छोटा रूप, जिज्ञासुओं के लिए: बटन दबाने से रिपोर्ट दिखने तक क्या होता है।"),
    "f_legend_dev": ("Runs on your device", "आपके डिवाइस पर चलता है"),
    "f_legend_net": ("Online: the AI or an official website", "ऑनलाइन: AI या आधिकारिक वेबसाइट"),
    "f_legend_rule": ("Fixed decision rules", "तय निर्णय नियम"),
    "tag_dev": ("on your device", "आपके डिवाइस पर"),
    "tag_net": ("online", "ऑनलाइन"),
    "f_in_t": ("Your forward", "आपका फ़ॉर्वर्ड"),
    "f_in_s": ("Text · screenshot · PDF", "पाठ · स्क्रीनशॉट · PDF"),
    "f_read_t": ("Read", "पढ़ना"),
    "f_read_s": ("Tesseract OCR (English + Hindi) · pdfplumber · OpenCV QR decoder",
                 "Tesseract OCR (अंग्रेज़ी + हिन्दी) · pdfplumber · OpenCV QR डिकोडर"),
    "f_prot_t": ("Protect", "सुरक्षित करना"),
    "f_prot_s": ("Aadhaar, PAN, phone, bank account, IFSC and email are masked",
                 "आधार, PAN, फ़ोन, बैंक खाता, IFSC और ईमेल छिपा दिए जाते हैं"),
    "f_a1": ("masked text only: images never leave your device", "सिर्फ़ छिपा हुआ पाठ: चित्र आपके डिवाइस से बाहर नहीं जाते"),
    "f_par": ("two investigators, in parallel", "दो जाँचकर्ता, साथ-साथ"),
    "f_ai_t": ("AI investigator", "AI जाँचकर्ता"),
    "f_ai_s": ("Gemini (free tier) as a tool-calling agent: plans the checks, retries and re-plans when a search fails",
               "Gemini (मुफ़्त स्तर) एक टूल-कॉलिंग एजेंट के रूप में: जाँच की योजना बनाता है, खोज विफल हो तो दोबारा कोशिश करता है"),
    "f_bi_t": ("Built-in checks", "अपनी जाँचें"),
    "f_bi_s": ("IDs, links, names, bank domains, payment QR. Always run, with or without the AI",
               "ID, लिंक, नाम, बैंक डोमेन, पेमेंट QR। AI हो या न हो, हमेशा चलती हैं"),
    "f_a2": ("every item is looked up", "हर बात की खोज होती है"),
    "f_src_t": ("Official sources", "आधिकारिक स्रोत"),
    "f_src_s": ("Live lookups and dated downloads. Each result keeps its source and the time it was checked",
                "लाइव खोज और तारीख़ वाले डाउनलोड। हर नतीजे के साथ उसका स्रोत और जाँच का समय रहता है"),
    "f_fu_t": ("Follow-up", "अगला कदम"),
    "f_fu_s": ("A firm found in a SEBI register is also searched in SEBI's enforcement orders",
               "SEBI रजिस्टर में मिली फ़र्म को SEBI के प्रवर्तन आदेशों में भी खोजा जाता है"),
    "f_a3": ("all findings", "सभी निष्कर्ष"),
    "f_rule_t": ("Decision rules", "निर्णय नियम"),
    "f_rule_s": ("Fixed, readable rules turn the findings into the result. The AI cannot change it",
                 "तय, पढ़े जा सकने वाले नियम निष्कर्षों को नतीजे में बदलते हैं। AI इसे बदल नहीं सकता"),
    "f_exp_t": ("Explanation", "समझाना"),
    "f_exp_s": ("Gemini writes it in English or Hindi, from the verdicts only",
                "Gemini इसे अंग्रेज़ी या हिन्दी में लिखता है, सिर्फ़ फ़ैसलों के आधार पर"),
    "f_rep_t": ("Report", "रिपोर्ट"),
    "f_rep_s": ("The answer, what to do, complaint links, and the records with links to verify",
                "जवाब, क्या करें, शिकायत के लिंक, और जाँचने के लिंक के साथ रिकॉर्ड"),
    "num_banks": ("banks' official websites checked", "बैंकों की आधिकारिक वेबसाइटें जाँची जाती हैं"),
    "num_regs": ("official registers and lists", "आधिकारिक रजिस्टर और सूचियाँ"),
    "num_langs": ("languages: English and Hindi", "भाषाएँ: अंग्रेज़ी और हिन्दी"),
    "num_img": ("images sent to any AI", "AI को भेजे गए चित्र"),
    "num_kept": ("messages or screenshots kept", "संदेश या स्क्रीनशॉट रखे जाते हैं"),
    "tech_title": ("Under the hood", "अंदर क्या है"),
    "banks_title": ("The 25 banks' official websites", "25 बैंकों की आधिकारिक वेबसाइटें"),
    "flow_title": ("From your message to the report", "आपके संदेश से रिपोर्ट तक"),
    "col_layer": ("Layer", "परत"),
    "col_tech": ("Technology", "तकनीक"),
    "col_role": ("What it does", "यह क्या करता है"),
    "pr_title": ("What we promise", "हमारा वादा"),
    "p1_t": ("Evidence over opinion", "राय नहीं, सबूत"),
    "p1_d": ("We show what an official record says and when we checked it. We don't guess.",
             "हम दिखाते हैं कि आधिकारिक रिकॉर्ड क्या कहता है और हमने कब जाँचा। हम अंदाज़ा नहीं लगाते।"),
    "p2_t": ("Honest about limits", "सीमाओं के बारे में ईमानदार"),
    "p2_d": ("A match shows a business exists, not who sent the message. When we can't check something, we say so.",
             "रिकॉर्ड में मिलने का मतलब है कि कारोबार मौजूद है, यह नहीं कि संदेश किसने भेजा। जो नहीं जाँच सकते, वह बताते हैं।"),
    "p3_t": ("No accusations", "कोई आरोप नहीं"),
    "p3_d": ("We never call a named business a fraud. We say what the record shows.",
             "हम किसी नामित कारोबार को धोखेबाज़ नहीं कहते। हम बताते हैं कि रिकॉर्ड क्या दिखाता है।"),
    "p4_t": ("Your privacy", "आपकी निजता"),
    "p4_d": ("Personal numbers are hidden before any AI sees your text, and we don't keep your messages or screenshots.",
             "AI के आपका पाठ देखने से पहले निजी नंबर छिपा दिए जाते हैं, और हम आपके संदेश या स्क्रीनशॉट नहीं रखते।"),
    # Sources
    "src_intro": ("Where each check gets its answer. Lists are re-downloaded every 24 hours; if a site is down we use "
                  "our last dated copy and say so.",
                  "हर जाँच का जवाब कहाँ से आता है। सूचियाँ हर 24 घंटे में दोबारा डाउनलोड होती हैं; साइट बंद हो तो "
                  "हम आख़िरी तारीख़ वाली कॉपी इस्तेमाल करते हैं और बताते हैं।"),
    "col_source": ("Source", "स्रोत"),
    "col_org": ("Organisation", "संस्था"),
    "col_how": ("How we read it", "हम इसे कैसे पढ़ते हैं"),
    "col_page": ("Official page", "आधिकारिक पेज"),
    "cached": ("Cached list", "सहेजी गई सूची"),
    "fetched": ("Fetched at", "लाने का समय"),
    "dated": ("List dated", "सूची की तारीख़"),
    "size": ("Size (bytes)", "आकार (बाइट)"),
    "refresh": ("Refresh official lists now", "आधिकारिक सूचियाँ अभी ताज़ा करें"),
    "refreshing": ("Downloading UGC and IRDAI lists…", "UGC और IRDAI सूचियाँ डाउनलोड हो रही हैं…"),
}
EVIDENCE_LEVEL_HI = {"Strong": "मज़बूत", "Medium": "मध्यम", "Limited": "सीमित"}

# Short names for the warning signs (the full sentence lives in verdict.RED_FLAGS).
FLAG_NAMES = {
    "guaranteed_returns": ("Promises guaranteed returns", "गारंटीड मुनाफ़े का वादा"),
    "sebi_claim_no_number": ("Says \"SEBI registered\" but gives no number", "\"SEBI पंजीकृत\" कहता है पर नंबर नहीं देता"),
    "admits_unregistered": ("Sells tips while admitting it isn't registered", "पंजीकृत न होने की बात मानकर टिप बेचता है"),
    "tip_group": ("Invites you to a paid tip group", "पैसे वाले टिप ग्रुप में बुलाता है"),
    "unexpected_money": ("Offers money or a refund out of the blue", "अचानक पैसे या रिफंड का ऑफ़र"),
    "official_via_link": ("Claims to be official but asks you to click a link", "आधिकारिक होने का दावा, पर लिंक दबाने को कहता है"),
    "bank_details_link": ("Asks for bank details through a link", "लिंक से बैंक की जानकारी माँगता है"),
    "task_job": ("Easy money for simple online tasks", "आसान ऑनलाइन काम के बदले आसान पैसा"),
    "urgency": ("Pushes you to act fast", "जल्दबाज़ी करवाता है"),
    "threat": ("Threatens arrest or legal action", "गिरफ़्तारी या क़ानूनी कार्रवाई की धमकी"),
    "pay_to_resolve": ("Asks you to pay first", "पहले पैसे माँगता है"),
    "kyc_block": ("Says your account will be blocked", "खाता बंद होने की बात कहता है"),
    "secrecy": ("Asks you to keep it secret", "इसे गुप्त रखने को कहता है"),
    "otp_or_remote": ("Asks for an OTP or remote access", "OTP या रिमोट एक्सेस माँगता है"),
    "app_outside_store": ("Asks you to install an app from a link", "लिंक से ऐप इंस्टॉल करने को कहता है"),
    "qr_mismatch": ("The payment QR doesn't match the story", "पेमेंट QR कहानी से मेल नहीं खाता"),
    "new_website": ("The website was registered very recently", "वेबसाइट हाल ही में बनी है"),
    "impersonation": ("Pretends to be someone it isn't", "किसी और के होने का दिखावा करता है"),
}

# The demo forwards: real messages from official advisories, kept in test_forwards/forwards.json.
DEMOS = {
    "UGC-B": (("Fake university", "A degree offer from a university on UGC's fake list"),
              ("फ़र्ज़ी विश्वविद्यालय", "UGC की फ़र्ज़ी सूची वाले विश्वविद्यालय का डिग्री ऑफ़र")),
    "INV-2": (("Stock tip channel", "A tip channel that claims to be SEBI registered"),
              ("शेयर टिप चैनल", "एक टिप चैनल जो SEBI-पंजीकृत होने का दावा करता है")),
    "TAX-1": (("Fake tax link", "An income-tax notice that links to a fake website"),
              ("फ़र्ज़ी टैक्स लिंक", "आयकर नोटिस जो एक फ़र्ज़ी वेबसाइट से जुड़ता है")),
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Mukta:wght@400;600;700;800&display=swap');
.stApp, .stApp textarea, .stApp button, .stApp input, .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label,
.stApp li, .stApp td, .stApp th { font-family: 'Mukta', 'Nirmala UI', 'Segoe UI', sans-serif; }
.block-container { max-width: 1000px; padding-top: 3.2rem; padding-bottom: 4rem; }
footer, #MainMenu { visibility: hidden; }
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #DCE6F4; }

.page-title { font-size: 2.4rem; font-weight: 800; color: #0A1F3B; margin: 0.4rem 0 0.2rem; line-height: 1.15; }
.lede { font-size: 1.2rem; color: #0A1F3B; margin: 0 0 0.5rem; line-height: 1.5; }
.privacy { font-size: 0.95rem; color: #4D6482; margin: 0 0 1.4rem; line-height: 1.5; }
h2.section { font-size: 1.5rem; font-weight: 800; color: #0A1F3B; margin: 2rem 0 0.8rem; }

/* the big paste box and the upload area */
.stTextArea textarea { font-size: 1.1rem; line-height: 1.5; border: 2px solid #BFD0E6; border-radius: 14px; padding: 1rem; }
.stTextArea textarea:focus { border-color: #0868F1; box-shadow: none; }
.stTextArea label p, .stFileUploader label p { font-size: 1.1rem; font-weight: 700; color: #0A1F3B; }
[data-testid="stFileUploaderDropzone"] { border: 2px dashed #8FB2E6; border-radius: 14px; background: #FFFFFF; }

/* the Check button: big and the loudest thing on the page */
button[data-testid="stBaseButton-primary"], div.stButton > button[kind="primary"] {
    height: 3.8rem; border-radius: 14px; background: #0868F1; border: none; margin-top: 0.6rem; }
button[data-testid="stBaseButton-primary"]:hover, div.stButton > button[kind="primary"]:hover { background: #0654C4; }
button[data-testid="stBaseButton-primary"] p, div.stButton > button[kind="primary"] p {
    font-size: 1.45rem; font-weight: 800; color: #FFFFFF; letter-spacing: 0.01em; }
button[data-testid="stBaseButton-secondary"] { border: 2px solid #BFD0E6; border-radius: 12px; background: #FFFFFF; }
button[data-testid="stBaseButton-secondary"]:hover { border-color: #0868F1; }
a[data-testid="stBaseLinkButton-secondary"] { border: 2px solid #0868F1; border-radius: 12px; background: #FFFFFF; }
a[data-testid="stBaseLinkButton-secondary"] p { font-weight: 700; color: #0868F1; }
a[data-testid="stBaseLinkButton-secondary"]:hover { background: #EAF2FE; }

/* the loading screen */
.loader { background: #FFFFFF; border: 1px solid #DCE6F4; border-radius: 20px; padding: 2.2rem 2rem 1.6rem;
          text-align: center; margin-top: 1rem; }
.spin { width: 56px; height: 56px; border: 6px solid #D6E6FB; border-top-color: #0868F1; border-radius: 50%;
        animation: spin 0.9s linear infinite; margin: 0 auto 1.1rem; }
@keyframes spin { to { transform: rotate(360deg); } }
.loader h2 { margin: 0 0 0.3rem; font-size: 1.7rem; font-weight: 800; color: #0A1F3B; }
.loader p { margin: 0 0 1.2rem; color: #4D6482; font-size: 1.05rem; }
ul.steps { list-style: none; padding: 0; margin: 0 auto; max-width: 720px; text-align: left; }
ul.steps li { padding: 0.45rem 0.2rem 0.45rem 2rem; position: relative; font-size: 1.05rem; color: #0A1F3B;
              border-top: 1px solid #EAF0F8; }
ul.steps li.done::before { content: "✓"; position: absolute; left: 0.4rem; color: #03A89E; font-weight: 800; }
ul.steps li.now::before { content: ""; position: absolute; left: 0.3rem; top: 0.75rem; width: 0.9rem; height: 0.9rem;
                          border: 3px solid #D6E6FB; border-top-color: #0868F1; border-radius: 50%; animation: spin 0.8s linear infinite; }
ul.steps li.sub { padding-left: 3rem; font-size: 0.95rem; color: #4D6482; border-top: none; padding-top: 0; }

/* the report */
.result { border-radius: 18px; padding: 1.4rem 1.6rem 1.3rem; margin: 0.6rem 0 1rem; border: 1px solid; }
.result.high { background: #FDECEA; border-color: #F2C0BB; }
.result.care { background: #FEF1E4; border-color: #F4D0A8; }
.result.ok { background: #E3F6F3; border-color: #A5DDD5; }
.result-label { font-size: 0.85rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #4D6482; }
.result .verdict { font-size: 2rem; font-weight: 800; line-height: 1.2; margin: 0.15rem 0 0.4rem; }
.result.high .verdict { color: #B42318; } .result.care .verdict { color: #9A4A06; } .result.ok .verdict { color: #0B7A70; }
.result .why { font-size: 1.15rem; line-height: 1.5; margin: 0 0 0.9rem; color: #0A1F3B; }
.chip { display: inline-block; background: #FFFFFF; border: 1px solid #BFD0E6; border-radius: 999px;
        padding: 0.15rem 0.8rem; font-size: 0.95rem; font-weight: 700; color: #0A1F3B; }
.callout { background: #FFF8E6; border: 1px solid #F3DDA0; border-radius: 12px; padding: 0.7rem 1rem; margin: 0.4rem 0 0.9rem;
           color: #5C4300; font-weight: 600; }
ol.todo { margin: 0.2rem 0 0.4rem 1.2rem; padding: 0; } ol.todo li { margin: 0.3rem 0; font-size: 1.08rem; line-height: 1.5; }
ul.flags { margin: 0.2rem 0 0 1.2rem; padding: 0; } ul.flags li { margin: 0.25rem 0; font-size: 1.05rem; }

table.ev { width: 100%; border-collapse: collapse; background: #FFFFFF; border: 1px solid #DCE6F4; border-radius: 14px;
           overflow: hidden; font-size: 0.98rem; }
table.ev th { text-align: left; font-size: 0.8rem; letter-spacing: 0.06em; text-transform: uppercase; color: #4D6482;
              background: #F0F5FC; padding: 0.6rem 0.8rem; }
table.ev td { padding: 0.65rem 0.8rem; border-top: 1px solid #EAF0F8; vertical-align: top; color: #0A1F3B; }
table.ev td.src small { display: block; color: #4D6482; margin-top: 0.1rem; }
table.ev a { color: #0868F1; font-weight: 700; text-decoration: none; } table.ev a:hover { text-decoration: underline; }
.badge { display: inline-block; border-radius: 999px; padding: 0.1rem 0.6rem; font-size: 0.85rem; font-weight: 700; white-space: nowrap; }
.badge.red { background: #FDECEA; color: #B42318; } .badge.orange { background: #FEF1E4; color: #9A4A06; }
.badge.green { background: #E3F6F3; color: #0B7A70; } .badge.blue { background: #E8F1FE; color: #0654C4; }
.badge.gray { background: #EEF1F5; color: #4D6482; }
.also { color: #4D6482; font-size: 0.95rem; margin-top: 0.6rem; }

/* How to use / How it works */
.step { background: #FFFFFF; border: 1px solid #DCE6F4; border-radius: 16px; padding: 1.1rem 1.2rem; height: 100%; }
.step .num { display: inline-block; width: 2rem; height: 2rem; line-height: 2rem; text-align: center; border-radius: 50%;
             background: #0A1F3B; color: #FFFFFF; font-weight: 800; margin-bottom: 0.5rem; }
.step h4 { margin: 0 0 0.3rem; font-size: 1.15rem; color: #0A1F3B; }
.step p { margin: 0; font-size: 1rem; color: #35506F; line-height: 1.5; }
.mean { border-radius: 14px; padding: 0.9rem 1.1rem; margin-bottom: 0.6rem; border: 1px solid; }
.mean b { display: block; font-size: 1.1rem; margin-bottom: 0.1rem; }
.mean.high { background: #FDECEA; border-color: #F2C0BB; } .mean.high b { color: #B42318; }
.mean.care { background: #FEF1E4; border-color: #F4D0A8; } .mean.care b { color: #9A4A06; }
.mean.ok { background: #E3F6F3; border-color: #A5DDD5; } .mean.ok b { color: #0B7A70; }
.mean span { color: #0A1F3B; font-size: 1rem; }
.promise { background: #FFFFFF; border: 1px solid #DCE6F4; border-radius: 14px; padding: 0.9rem 1.1rem; height: 100%; }
.promise b { display: block; color: #0868F1; margin-bottom: 0.15rem; font-size: 1.05rem; }
.promise span { color: #35506F; font-size: 0.98rem; line-height: 1.5; }

/* How it works: numbers, legend, flowchart */
.nums { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.7rem; margin: 0.6rem 0 0.4rem; }
.num2 { background: #FFFFFF; border: 1px solid #DCE6F4; border-radius: 14px; padding: 0.8rem 0.6rem; text-align: center; }
.num2 b { display: block; font-size: 2rem; font-weight: 800; color: #0868F1; line-height: 1.1; }
.num2 span { font-size: 0.9rem; color: #4D6482; line-height: 1.3; display: block; margin-top: 0.2rem; }
.legend { display: flex; flex-wrap: wrap; gap: 1.2rem; margin: 0 0 1.2rem; font-size: 0.95rem; color: #35506F; }
.legend .dot { display: inline-block; width: 0.8rem; height: 0.8rem; border-radius: 4px; margin-right: 0.4rem; vertical-align: -1px; }
.dot.dev { background: #03BEB4; } .dot.net { background: #0868F1; } .dot.rule { background: #0A1F3B; }
.flow { max-width: 760px; margin: 0 auto; }
.fnode { position: relative; background: #FFFFFF; border: 2px solid; border-radius: 14px; padding: 0.9rem 1.1rem 0.8rem; text-align: center; }
.fnode.dev { border-color: #03BEB4; } .fnode.net { border-color: #0868F1; }
.fnode.rule { background: #0A1F3B; border-color: #0A1F3B; color: #FFFFFF; }
.fnode b { display: block; font-size: 1.15rem; font-weight: 800; color: #0A1F3B; }
.fnode.rule b { color: #FFFFFF; }
.fnode small { display: block; font-size: 0.95rem; color: #35506F; line-height: 1.45; margin-top: 0.2rem; }
.fnode.rule small { color: #D5E3F5; }
.ftag { position: absolute; top: -0.7rem; right: 0.9rem; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em;
        text-transform: uppercase; padding: 0.1rem 0.6rem; border-radius: 999px; }
.ftag.dev { background: #E3F6F3; color: #0B7A70; border: 1px solid #A5DDD5; }
.ftag.net { background: #E8F1FE; color: #0654C4; border: 1px solid #B7D2F8; }
.fchips { margin-top: 0.6rem; display: flex; flex-wrap: wrap; gap: 0.4rem; justify-content: center; }
a.fchip { text-decoration: none; }
a.fchip:hover { border-color: #0868F1; color: #0868F1; }
.fchips.left { justify-content: flex-start; margin-bottom: 1rem; }
ol.todo a, table.ev a { color: #0868F1; font-weight: 700; text-decoration: none; }
ol.todo a:hover, table.ev a:hover { text-decoration: underline; }
.fchip { background: #F0F5FC; border: 1px solid #C9D9EE; border-radius: 999px; padding: 0.1rem 0.7rem; font-size: 0.88rem; font-weight: 600; color: #0A1F3B; }
.flane-title { text-align: center; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #4D6482; margin-bottom: 0.7rem; }
.flane { display: grid; grid-template-columns: 1fr 1fr; gap: 0.9rem; }
.farrow { position: relative; height: 38px; }
.farrow::before { content: ""; position: absolute; left: 50%; top: 0; bottom: 8px; width: 2px; margin-left: -1px; background: #8FB2E6; }
.farrow::after { content: ""; position: absolute; left: 50%; bottom: 0; margin-left: -6px; border-left: 6px solid transparent;
                 border-right: 6px solid transparent; border-top: 9px solid #8FB2E6; }
.farrow span { position: absolute; left: calc(50% + 16px); top: 50%; transform: translateY(-50%); font-size: 0.85rem; color: #4D6482; white-space: nowrap; }
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# Language buttons at the top of every page.
_, lang_col = st.columns([5, 2])
with lang_col:
    choice = st.segmented_control("Language", list(LANGS), default="English", key="lang_choice",
                                  label_visibility="collapsed")
lang = LANGS.get(choice, "en")


def T(key):
    return UI[key][1 if lang == "hi" else 0]


def label(key, table):
    english, hindi, colour = table[key]
    return (hindi if lang == "hi" else english), colour


def esc(text):
    return html.escape(str(text))


# Official sites we link to. Each address was opened on 1 Nov 2026 and led to the page named. Two exceptions:
# the MCA address cannot be opened by a script (MCA blocks them), and IDBI's site answers browsers but not Python.
SEBI_INTM = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId="
LINKS = {
    "sebi_adv": SEBI_INTM + "13",
    "sebi_ra": SEBI_INTM + "14",
    "sebi_br": SEBI_INTM + "30",
    "sebi_orders": "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=0",
    "sebi_check": "https://siportal.sebi.gov.in/intermediary/sebi-check",
    "rbi_nbfc": "https://www.rbi.org.in/Scripts/BS_NBFCList.aspx",  # registered and cancelled NBFCs are both on this page
    "rbi_alert": "https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=4235",
    "rbi_circular": "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12837",  # RBI/2025-26/28, .bank.in
    "ugc": lists.UGC_URL,
    "irdai": "https://irdai.gov.in/list-of-life-insurers1",
    "amfi": lists.AMFI_PAGE,
    "rdap": "https://lookup.icann.org/",
    "urlhaus": "https://urlhaus.abuse.ch/",
    "gst": "https://services.gst.gov.in/services/searchtp",
    "itax": "https://www.incometax.gov.in/iec/foportal/",
    "ecourts": "https://services.ecourts.gov.in/ecourtindia_v6/",
    "cbic": "https://esanchar.cbic.gov.in/DIN/DINSearch",
    "mca": "https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html",
    "cyber": "https://cybercrime.gov.in",
    "chakshu": "https://sancharsaathi.gov.in/sfc/",
    "scores": "https://scores.sebi.gov.in",
    "sachet": "https://sachet.rbi.org.in",
}
# When a result carries no address of its own, link the organisation's website.
ORG_SITES = {"SEBI": "https://www.sebi.gov.in", "RBI": "https://www.rbi.org.in", "UGC": "https://www.ugc.gov.in",
             "IRDAI": "https://irdai.gov.in", "AMFI": "https://www.amfiindia.com", "abuse.ch": LINKS["urlhaus"],
             "RDAP": LINKS["rdap"]}


def a(url, text, cls=""):
    """A link that opens in a new tab. Only http(s) addresses become links."""
    if not str(url).startswith("http"):
        return esc(text)
    c = f" class='{cls}'" if cls else ""
    return f"<a{c} href='{html.escape(url, quote=True)}' target='_blank' rel='noopener'>{esc(text)}</a>"


def site_of(result):
    """The official site behind a result: its own address, or its organisation's website."""
    if result.get("source_url"):
        return result["source_url"]
    org = result.get("organisation", "")
    return next((u for k, u in ORG_SITES.items() if k.lower() in org.lower()), "")


def linkify(text):
    """Make the two official portals named in the next steps clickable."""
    t = esc(text)
    t = t.replace("cybercrime.gov.in", a(LINKS["cyber"], "cybercrime.gov.in"))
    return t.replace("sancharsaathi.gov.in", a("https://sancharsaathi.gov.in/", "sancharsaathi.gov.in"))


def title(key, lede=None):
    st.markdown(f"<h1 class='page-title'>{esc(T(key))}</h1>", unsafe_allow_html=True)
    if lede:
        st.markdown(f"<p class='lede'>{esc(T(lede))}</p>", unsafe_allow_html=True)


def sentences(text):
    """Split into sentences without breaking at abbreviations such as "Mr." or "Pvt. Ltd."."""
    text = re.sub(r"\b(Mr|Mrs|Ms|Dr|Shri|Smt|St|No|Pvt|Ltd|Co|Inc|Rs|Regn|vs)\.", r"\1", str(text).strip())
    return re.split(r"(?<=[.!?।])\s+", text)


def first_sentence(text, cap=150):
    one = sentences(text)[0]
    return one if len(one) <= cap else one[:cap - 1].rsplit(" ", 1)[0] + "…"


def when(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%d %b, %H:%M")
    except ValueError:
        return iso


# ---------- Check a forward: input -> loading -> report ----------

LEVEL = {"HIGH_RISK": "high", "CAUTION": "care", "CONSISTENT": "ok"}


def screenshot_texts(files):
    """For each screenshot: show it with its OCR text in an editable box. Returns the (corrected) texts."""
    texts = []
    for f in files:
        if not f.type.startswith("image/"):
            continue
        key = f"ocr_{f.name}_{f.size}"
        if key not in st.session_state:  # read once per file, so the user's edits aren't overwritten
            with st.spinner(T("reading")):
                try:
                    st.session_state[key] = agent.read_image(f.getvalue())
                except Exception:  # a broken image or OCR must never crash the page
                    st.session_state[key] = ""
        st.image(f, caption=f.name, width=320)
        if not st.session_state[key].strip():
            st.warning(T("ocr_empty"))
        st.text_area(T("ocr_title") + f": {f.name}", key=key, height=150, help=T("ocr_help"))
        texts.append(st.session_state[key])
    return texts


def start(full_text, pdfs):
    """Hand the message to the loading screen. (The input widgets disappear, so keep what they held.)"""
    st.session_state.job = {"text": full_text, "pdfs": pdfs}
    st.session_state.stage = "running"
    st.rerun()


def input_view():
    title("nav_check", "intro")
    st.markdown(f"<p class='privacy'>{esc(T('privacy'))}</p>", unsafe_allow_html=True)
    if "prefill" in st.session_state:  # a demo chosen on the How to use page
        st.session_state["text"] = st.session_state.pop("prefill")
    text = st.text_area(T("paste"), key="text", height=190, placeholder=T("placeholder"))
    files = st.file_uploader(T("upload"), type=["png", "jpg", "jpeg", "webp", "pdf"], accept_multiple_files=True)
    image_texts = screenshot_texts(files)
    go = st.session_state.pop("go", False)  # set by a demo button
    if st.button(T("check"), type="primary", width="stretch") or go:
        pdfs = [(f.name, f.getvalue(), f.type) for f in files if f.type == "application/pdf"]
        full_text = "\n".join([text] + image_texts)
        if not full_text.strip() and not pdfs:
            st.warning(T("empty"))
        else:
            start(full_text, pdfs)


def steps_html(steps):
    """The steps so far: finished ones ticked, the latest one spinning, result lines indented under their check."""
    items = []
    last = max((i for i, s in enumerate(steps) if not s.startswith("  ")), default=-1)
    for i, s in enumerate(steps):
        if s.startswith("  "):
            items.append(f"<li class='sub'>{esc(ids.mask(s.strip()))}</li>")
        else:
            items.append(f"<li class='{'now' if i == last else 'done'}'>{esc(ids.mask(s))}</li>")
    return f"<ul class='steps'>{''.join(items)}</ul>"


def running_view():
    job = st.session_state.job
    st.markdown(f"<div class='loader'><div class='spin'></div><h2>{esc(T('loading_title'))}</h2>"
                f"<p>{esc(T('loading_sub'))}</p></div>", unsafe_allow_html=True)
    box, steps = st.empty(), []
    for _ in range(24):  # Streamlit keeps the previous page's elements (faded) until a run ends: overwrite them now
        st.empty()

    def on_step(line):
        steps.append(str(line))
        box.markdown(steps_html(steps), unsafe_allow_html=True)

    try:
        report = agent.run_check(job["text"], job["pdfs"], lang, on_step=on_step)
    except Exception:  # never show a stack trace to a user, and never guess a verdict
        st.session_state.stage = "error"
        st.rerun()
    st.session_state.report = report
    st.session_state.stage = "report"
    st.rerun()


def error_view():
    st.error(T("crashed"))
    if st.button(T("retry"), type="primary", width="stretch"):
        st.session_state.stage = "input"
        st.rerun()


def short_answer(report, headline_text):
    """One or two short sentences from the explanation (the headline is shown above, so it isn't repeated)."""
    if report["mode"].startswith("rules"):  # no AI wrote an explanation: say it from the findings instead
        official = [c for c in report["checks"] if c["verdict"] in ("ON_WARNING_LIST", "INVALID", "IN_SEBI_ORDER")]
        bits = [first_sentence(ids.mask(official[0]["reason"]), 150)] if official else []
        names = [FLAG_NAMES[f["code"]][1 if lang == "hi" else 0] for f in report["flags"] if f["code"] in FLAG_NAMES]
        if names:
            bits.append(("चेतावनी के संकेत: " if lang == "hi" else "Warning signs: ") + "; ".join(names[:2]) + ".")
        if bits:
            return " ".join(bits)
    plain = lambda s: re.sub(r"[^\w\s]", "", s.lower())  # compare without quotes and punctuation
    head = plain(headline_text)
    parts = [p for p in sentences(ids.mask(report["explanation"])) if head not in plain(p)]
    if not parts:
        return ""
    out = parts[0]
    if len(parts) > 1 and len(out) + len(parts[1]) < 230:  # a second sentence only if the answer stays short
        out += " " + parts[1]
    return out if len(out) <= 260 else out[:257].rsplit(" ", 1)[0] + "…"


def finding(c):
    """What the record shows, in a few words."""
    r, v = c["result"], c["verdict"]
    top = r["matches"][0] if r["matches"] else None
    if top and v in ("MATCHED", "ON_WARNING_LIST", "NEEDS_CLARIFICATION"):
        return f"{top['name']}" + (f" ({top['id']})" if top.get("id") else "")
    if top and v == "IN_SEBI_ORDER":
        return f"{top['name']} · {top.get('id', '')}"
    if v == "NOT_FOUND":
        return T("no_record")
    return first_sentence(ids.mask(c["reason"]))


def evidence_rows(report):
    """The records we matched, one compact row each. Format-only passes go in a one-line note instead."""
    rows, quiet, seen = [], [], set()
    quiet_verdicts = {"CONFIRM_OFFICIALLY", "NOT_LISTED", "NO_SEBI_ORDER"}
    for c in sorted(report["checks"], key=lambda c: verdict.RANK.index(c["verdict"])):
        item, r = ids.mask(c["item"]), c["result"]
        if c["verdict"] in quiet_verdicts:
            if item not in quiet:
                quiet.append(item)
            continue
        name, colour = label(c["verdict"], verdict.VERDICTS)
        top = r["matches"][0] if r["matches"] else None
        site = site_of(r)
        link = (top.get("url") if c["verdict"] == "IN_SEBI_ORDER" and top else None) or site
        row = (item, name, colour, finding(c), r["source"], when(r["checked_at"]), site, link)
        if row[:5] not in seen:  # the same finding twice adds nothing
            seen.add(row[:5])
            rows.append(row)
    return rows, quiet


def evidence_html(rows):
    head = "".join(f"<th>{esc(T(k))}</th>" for k in ("col_item", "col_result", "col_record", "col_where", "col_verify"))
    body = []
    for item, name, colour, record, source, checked, site, link in rows:
        verify = a(link, T("verify")) if link.startswith("http") else "—"
        body.append(f"<tr><td><b>{esc(item)}</b></td><td><span class='badge {colour}'>{esc(name)}</span></td>"
                    f"<td>{esc(record)}</td><td class='src'>{a(site, source)}<small>{esc(checked)}</small></td>"
                    f"<td>{verify}</td></tr>")
    return f"<table class='ev'><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def complaint_links(report):
    """Official places to complain. Always the cyber-crime portal and Sanchar Saathi; SEBI and RBI when relevant."""
    tools = " ".join(c["tool"] for c in report["checks"])
    codes = {f["code"] for f in report["flags"]}
    links = [("btn_cyber", LINKS["cyber"]), ("btn_chakshu", LINKS["chakshu"])]
    if "SEBI" in tools or codes & {"guaranteed_returns", "sebi_claim_no_number", "admits_unregistered", "tip_group"}:
        links.append(("btn_sebi", LINKS["scores"]))
    if "RBI" in tools or "unexpected_money" in codes:
        links.append(("btn_rbi", LINKS["sachet"]))
    return links


def report_view():
    report = st.session_state.report
    if report.get("language") != lang and "job" in st.session_state:
        # The explanation and the next steps were written in the old language: check again in the new one
        # (official answers are kept for a while, so this is quick).
        st.session_state.stage = "running"
        st.rerun()
    head, back = st.columns([3, 2])
    head.markdown(f"<h1 class='page-title'>{esc(T('report_title'))}</h1>", unsafe_allow_html=True)
    if back.button(T("another"), width="stretch", icon=":material/arrow_back:"):
        st.session_state.stage = "input"
        st.session_state.pop("report", None)
        st.session_state["text"] = ""
        st.rerun()

    text, _ = label(report["headline"], verdict.HEADLINES)
    level = report.get("evidence", {}).get("level", "")
    chip = ""
    if level:
        chip = f"<span class='chip'>{esc(T('evidence_chip'))}: {esc(EVIDENCE_LEVEL_HI.get(level, level) if lang == 'hi' else level)}</span>"
    st.markdown(
        f"<div class='result {LEVEL[report['headline']]}'><div class='result-label'>{esc(T('result'))}</div>"
        f"<div class='verdict'>{esc(text)}</div><p class='why'>{esc(short_answer(report, text))}</p>{chip}</div>",
        unsafe_allow_html=True)
    if report.get("summary"):
        st.caption(T("asks") + ids.mask(report["summary"]))

    # What to do now, and where to complain
    st.markdown(f"<h2 class='section'>{esc(T('todo_title'))}</h2>", unsafe_allow_html=True)
    st.markdown("<ol class='todo'>" + "".join(f"<li>{linkify(s)}</li>" for s in report["next_steps"]) + "</ol>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='callout'>{esc(T('call1930'))}</div>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='section'>{esc(T('report_title2'))}</h2>", unsafe_allow_html=True)
    st.write(T("report_bad") if report["headline"] != "CONSISTENT" else T("report_ok"))
    links = complaint_links(report)
    for i in range(0, len(links), 2):  # two to a row so the labels stay readable
        for col, (key, url) in zip(st.columns(2), links[i:i + 2]):
            col.link_button(T(key), url, width="stretch", icon=":material/open_in_new:")

    # What we found
    st.markdown(f"<h2 class='section'>{esc(T('found_title'))}</h2>", unsafe_allow_html=True)
    rows, quiet = evidence_rows(report)
    if rows:
        st.markdown(evidence_html(rows), unsafe_allow_html=True)
    elif not quiet:
        st.info(T("nothing"))
    if quiet:
        st.markdown(f"<p class='also'>{esc(T('also'))}{esc(', '.join(quiet[:6]))}</p>", unsafe_allow_html=True)
    if any(c["verdict"] == "COULDNT_VERIFY" for c in report["checks"]):
        st.warning(T("cant_verify"))
    flags = [f for f in report["flags"] if not (f["by"] == "AI" and f.get("code") == "other")]
    if flags:
        st.markdown(f"<h2 class='section'>{esc(T('warn_title'))}</h2>", unsafe_allow_html=True)
        names = lambda f: FLAG_NAMES[f["code"]][1 if lang == "hi" else 0] if f["code"] in FLAG_NAMES else first_sentence(f["reason"], 90)
        st.markdown("<ul class='flags'>" + "".join(
            f"<li>{esc(names(f))}" + (f" <i>({esc(T('by_ai'))})</i>" if f["by"] == "AI" else "") + "</li>" for f in flags)
            + "</ul>", unsafe_allow_html=True)
    st.caption(f"{when(datetime.now().astimezone().isoformat())} · {report['duration_ms'] / 1000:.1f} s · "
               f"{len(report['checks'])} {'checks' if lang == 'en' else 'जाँचें'}")


def check_page():
    stage = st.session_state.get("stage", "input")
    if stage == "running" and "job" in st.session_state:
        running_view()
    elif stage == "report" and "report" in st.session_state:
        report_view()
    elif stage == "error":
        error_view()
    else:
        st.session_state.stage = "input"
        input_view()


# ---------- How to use / How it works ----------

def learn_page():
    title("nav_learn", "learn_intro")
    for col, n in zip(st.columns(3), "123"):
        col.markdown(f"<div class='step'><span class='num'>{n}</span><h4>{esc(T(f's{n}_t'))}</h4>"
                     f"<p>{esc(T(f's{n}_d'))}</p></div>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='section'>{esc(T('means_title'))}</h2>", unsafe_allow_html=True)
    for cls, key in (("high", "HIGH_RISK"), ("care", "CAUTION"), ("ok", "CONSISTENT")):
        name, _ = label(key, verdict.HEADLINES)
        st.markdown(f"<div class='mean {cls}'><b>{esc(name)}</b><span>{esc(T('m_' + cls))}</span></div>",
                    unsafe_allow_html=True)
    st.markdown(f"<h2 class='section'>{esc(T('try_title'))}</h2>", unsafe_allow_html=True)
    st.write(T("try_intro"))
    for fid, (en, hi) in DEMOS.items():
        name, desc = hi if lang == "hi" else en
        if st.button(f"**{name}**  ·  {desc}", key=f"demo_{fid}", width="stretch"):
            forwards = json.loads(Path("test_forwards/forwards.json").read_text(encoding="utf-8"))
            st.session_state["prefill"] = next(f["text"] for f in forwards if f["id"] == fid)
            st.session_state["go"] = True  # the Check page runs it live as soon as it opens
            st.session_state["stage"] = "input"
            st.switch_page(check_pg)


TECH = [
    (("App", "ऐप"), "Python · Streamlit", ("The web app you are using", "यह वेब ऐप जिसे आप इस्तेमाल कर रहे हैं")),
    (("AI", "AI"), "Gemini via an OpenAI-compatible API (three free-tier models in turn)",
     ("Plans the checks and writes the explanation. It never decides the result",
      "जाँच की योजना बनाता है और समझाता है। नतीजा कभी तय नहीं करता")),
    (("Reading", "पढ़ना"), "Tesseract OCR · pdfplumber · OpenCV",
     ("Turns screenshots, PDFs and payment QR codes into text, on your device",
      "स्क्रीनशॉट, PDF और पेमेंट QR को आपके डिवाइस पर पाठ में बदलता है")),
    (("Matching", "मिलान"), "rapidfuzz · exact number matching",
     ("Fuzzy matching for names; exact matching for registration numbers",
      "नामों के लिए अनुमानित मिलान; पंजीकरण नंबरों के लिए सटीक मिलान")),
    (("Official data", "आधिकारिक डेटा"), "requests · BeautifulSoup · RDAP",
     ("Live lookups of regulator websites, and dated downloads where a site blocks scripts",
      "नियामकों की वेबसाइटों पर लाइव खोज, और जहाँ साइट स्क्रिप्ट रोकती है वहाँ तारीख़ वाले डाउनलोड")),
    (("Privacy", "निजता"), "Masking before every AI call",
     ("Personal numbers are hidden before the AI sees anything. No messages or screenshots are kept",
      "AI के कुछ भी देखने से पहले निजी नंबर छिपा दिए जाते हैं। कोई संदेश या स्क्रीनशॉट नहीं रखा जाता")),
    (("Storage", "भंडारण"), "SQLite",
     ("Only cached copies of official lists, with the time they were fetched",
      "सिर्फ़ आधिकारिक सूचियों की सहेजी हुई कॉपी, लाने के समय के साथ")),
]
SOURCE_CHIPS = [("SEBI registers", "sebi_adv"), ("SEBI orders", "sebi_orders"), ("RBI lists", "rbi_nbfc"), ("UGC", "ugc"),
                ("IRDAI", "irdai"), ("AMFI", "amfi"), ("25 bank websites", "rbi_circular"), ("RDAP", "rdap"),
                ("URLhaus", "urlhaus")]


def node(kind, title_key, sub_key, tag=True):
    tagline = (f"<span class='ftag {kind}'>{esc(T('tag_net' if kind == 'net' else 'tag_dev'))}</span>"
               if tag and kind != "rule" else "")
    return f"<div class='fnode {kind}'>{tagline}<b>{esc(T(title_key))}</b><small>{esc(T(sub_key))}</small></div>"


def arrow(caption_key=None):
    cap = f"<span>{esc(T(caption_key))}</span>" if caption_key else ""
    return f"<div class='farrow'>{cap}</div>"


def flow_html():
    chips = "".join(a(LINKS[key], name, "fchip") for name, key in SOURCE_CHIPS)
    parts = [
        "<div class='flow'>",
        node("dev", "f_in_t", "f_in_s", tag=False), arrow(),
        node("dev", "f_read_t", "f_read_s"), arrow(),
        node("dev", "f_prot_t", "f_prot_s"), arrow("f_a1"),
        f"<div class='flane-title'>{esc(T('f_par'))}</div>",
        f"<div class='flane'>{node('net', 'f_ai_t', 'f_ai_s')}{node('dev', 'f_bi_t', 'f_bi_s')}</div>", arrow("f_a2"),
        f"<div class='fnode net'><span class='ftag net'>{esc(T('tag_net'))}</span><b>{esc(T('f_src_t'))}</b>"
        f"<small>{esc(T('f_src_s'))}</small><div class='fchips'>{chips}</div></div>", arrow(),
        node("net", "f_fu_t", "f_fu_s"), arrow("f_a3"),
        node("rule", "f_rule_t", "f_rule_s"), arrow(),
        f"<div class='flane'>{node('net', 'f_exp_t', 'f_exp_s')}{node('dev', 'f_rep_t', 'f_rep_s')}</div>",
        "</div>",
    ]
    return "".join(parts)


def numbers_html():
    items = [("25", "num_banks"), ("10", "num_regs"), ("2", "num_langs"), ("0", "num_img"), ("0", "num_kept")]
    return "<div class='nums'>" + "".join(
        f"<div class='num2'><b>{n}</b><span>{esc(T(k))}</span></div>" for n, k in items) + "</div>"


def how_page():
    """For the curious: what happens and what it is built with. The rules, thresholds and patterns stay out on purpose."""
    title("nav_how", "how_intro")
    st.markdown(numbers_html(), unsafe_allow_html=True)
    st.markdown(f"<h2 class='section'>{esc(T('flow_title'))}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='legend'>"
                f"<span><i class='dot dev'></i>{esc(T('f_legend_dev'))}</span>"
                f"<span><i class='dot net'></i>{esc(T('f_legend_net'))}</span>"
                f"<span><i class='dot rule'></i>{esc(T('f_legend_rule'))}</span></div>", unsafe_allow_html=True)
    st.markdown(flow_html(), unsafe_allow_html=True)
    st.markdown(f"<h2 class='section'>{esc(T('tech_title'))}</h2>", unsafe_allow_html=True)
    i = 1 if lang == "hi" else 0
    rows = "".join(f"<tr><td><b>{esc(layer[i])}</b></td><td>{esc(tech)}</td><td>{esc(role[i])}</td></tr>"
                   for layer, tech, role in TECH)
    head = "".join(f"<th>{esc(T(k))}</th>" for k in ("col_layer", "col_tech", "col_role"))
    st.markdown(f"<table class='ev'><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='section'>{esc(T('pr_title'))}</h2>", unsafe_allow_html=True)
    for row in (("1", "2"), ("3", "4")):
        for col, n in zip(st.columns(2), row):
            col.markdown(f"<div class='promise'><b>{esc(T(f'p{n}_t'))}</b><span>{esc(T(f'p{n}_d'))}</span></div>",
                         unsafe_allow_html=True)
        st.write("")


# ---------- Sources ----------

SOURCES = [  # (source, organisation, how we read it, [(link label, address)])
    ("SEBI investment advisers", "SEBI", "Live search every time", [("sebi_adv", None)]),
    ("SEBI research analysts", "SEBI", "Live search every time", [("sebi_ra", None)]),
    ("SEBI stock brokers (equity segment)", "SEBI", "Live search every time", [("sebi_br", None)]),
    ("SEBI enforcement orders", "SEBI", "Live search of order titles every time", [("sebi_orders", None)]),
    ("RBI registered NBFCs and ARCs", "RBI", "Downloaded by hand; list as on 30 Sep 2026", [("rbi_nbfc", None)]),
    ("RBI cancelled NBFC registrations", "RBI", "Downloaded by hand; list as on 30 Sep 2026 (same RBI page)",
     [("rbi_nbfc", None)]),
    ("RBI Alert List (unauthorised forex platforms)", "RBI", "Downloaded by hand; list updated 19 Nov 2025",
     [("rbi_alert", None)]),
    ("UGC list of fake universities", "UGC", "Live page, cached 24 h", [("ugc", None)]),
    ("IRDAI insurers and brokers", "IRDAI", "Live pages, cached 24 h", [("irdai", None)]),
    ("AMFI mutual fund distributors", "AMFI", "Live search every time", [("amfi", None)]),
    ("Website age and short-link destination", "RDAP (public domain registry)", "Live lookup every time",
     [("rdap", None)]),
    ("Bank websites (25 banks' official domains)", "RBI .bank.in circular", "Domain list read from each bank's own "
     "site on 1 Nov 2026 (full list below)", [("rbi_circular", "RBI circular")]),
    ("UPI payment QR codes", "SEBI Check", "Decoded offline (OpenCV) and compared with the message. The recipient is "
     "never verified: a QR's name is typed by whoever made it", [("sebi_check", "SEBI Check")]),
    ("URLhaus malware URL list (links inside QR codes)", "abuse.ch", "Last-30-days export, cached 1 h; needs a free "
     "key", [("urlhaus", None)]),
    ("ID numbers: GST, PAN, company, court case, tax and customs notices", "Official portals", "Format and check "
     "digits only, offline. These portals need a captcha or login, so you confirm there",
     [("gst", "GST"), ("itax", "Income Tax"), ("ecourts", "eCourts"), ("cbic", "CBIC"), ("mca", "MCA")]),
]


def sources_page():
    title("nav_sources", "src_intro")
    head = "".join(f"<th>{esc(T(k))}</th>" for k in ("col_source", "col_org", "col_how", "col_page"))
    body = []
    for name, org, how, links in SOURCES:
        urls = [(label or T("verify"), LINKS[key]) for key, label in links]
        first = a(urls[0][1], name) if len(urls) == 1 else esc(name)
        body.append(f"<tr><td><b>{first}</b></td><td>{esc(org)}</td><td>{esc(how)}</td>"
                    f"<td>{' · '.join(a(u, lab) for lab, u in urls)}</td></tr>")
    st.markdown(f"<table class='ev'><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>",
                unsafe_allow_html=True)
    st.markdown(f"<h2 class='section'>{esc(T('banks_title'))}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='fchips left'>" + "".join(
        a(v[3], v[0], "fchip") for v in banks.BANKS.values()) + "</div>", unsafe_allow_html=True)
    snaps = store.snapshots()
    if snaps:
        st.markdown("")
        st.dataframe(pd.DataFrame(snaps, columns=[T("cached"), T("fetched"), T("dated"), T("size")]),
                     hide_index=True, width="stretch")
    if st.button(T("refresh")):
        store.clear_snapshots()
        with st.spinner(T("refreshing")):
            lists.search_ugc_fake("refresh")
            lists.search_irdai("refresh")
        st.rerun()


check_pg = st.Page(check_page, title=T("nav_check"), icon=":material/search:", default=True)
learn_pg = st.Page(learn_page, title=T("nav_learn"), icon=":material/school:", url_path="how-to-use")
how_pg = st.Page(how_page, title=T("nav_how"), icon=":material/lightbulb:", url_path="how-it-works")
sources_pg = st.Page(sources_page, title=T("nav_sources"), icon=":material/library_books:", url_path="sources")
st.navigation([check_pg, learn_pg, how_pg, sources_pg], position="sidebar").run()
