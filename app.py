"""Parakh web app. Run:  streamlit run app.py

Owner: Rahul (frontend). The check log tab is Atharva's.
The page only shows what agent.run_check returns; every verdict comes from verdict.py, never from this file.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

import agent
import brain
import store
import verdict
from connectors import ids, lists

st.set_page_config(page_title="Parakh", page_icon="🔎", layout="centered")
LANGS = {"English": "en", "हिन्दी (Hindi)": "hi"}

# Every label on the page, in both languages. T("key") picks the one for the chosen language.
UI = {
    "tagline": ("Don't trust the forward. Verify the evidence.", "फ़ॉर्वर्ड पर भरोसा न करें। सबूत जाँचें।"),
    "reply_lang": ("Reply language", "जवाब की भाषा"),
    "tab_check": ("Check a forward", "संदेश जाँचें"),
    "tab_log": ("Check log", "जाँच का रिकॉर्ड"),
    "tab_sources": ("Sources", "स्रोत"),
    "ai_on": ("AI investigator: ", "AI जाँचकर्ता: "),
    "ai_off": ("AI off (no key in .env): plain rules pick the checks.", "AI बंद है (.env में कोई कुंजी नहीं): सादे नियम जाँच चुनते हैं।"),
    "rules_note": ("Verdicts always come from fixed rules, never from the AI. Connected checks: ",
                   "फ़ैसले हमेशा तय नियमों से आते हैं, AI से कभी नहीं। जुड़ी हुई जाँचें: "),
    "privacy": ("Aadhaar, PAN and mobile numbers are masked before any text goes to the AI, and never looked up. "
                "Screenshots are read on this computer and never sent to the AI. "
                "We store a fingerprint of each forward, never the forward itself.",
                "आधार, PAN और मोबाइल नंबर AI को भेजने से पहले छिपा दिए जाते हैं और कभी खोजे नहीं जाते। "
                "स्क्रीनशॉट इसी कंप्यूटर पर पढ़े जाते हैं, AI को नहीं भेजे जाते। "
                "हम हर संदेश की सिर्फ़ फ़िंगरप्रिंट रखते हैं, संदेश नहीं।"),
    "paste": ("Paste the message", "संदेश यहाँ चिपकाएँ"),
    "placeholder": ("e.g. Invest ₹50,000 with ABC Investments. Our SEBI-registered adviser guarantees 4% monthly returns…",
                    "जैसे: ABC Investments में ₹50,000 लगाएँ। हमारे SEBI-पंजीकृत सलाहकार हर महीने 4% की गारंटी देते हैं…"),
    "upload": ("…or add a screenshot or PDF", "…या स्क्रीनशॉट या PDF जोड़ें"),
    "demo": ("Try a real forward (checked live):", "एक असली फ़ॉर्वर्ड आज़माएँ (लाइव जाँच होगी):"),
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
    "investigating": ("Investigating…", "जाँच हो रही है…"),
    "done": ("Done in", "पूरा हुआ:"),
    "checks": ("checks", "जाँचें"),
    "crashed": ("Something went wrong while checking. Nothing was decided. Please try again.",
                "जाँच के दौरान कुछ गड़बड़ हुई। कोई फ़ैसला नहीं लिया गया। कृपया फिर कोशिश करें।"),
    "asks": ("What the message asks: ", "संदेश क्या कहता है: "),
    "warn_title": ("Warning signs in the wording", "शब्दों में चेतावनी के संकेत"),
    "by_ai": ("spotted by AI", "AI ने पकड़ा"),
    "evidence": ("Evidence, item by item", "सबूत, एक-एक बात करके"),
    "nothing": ("Nothing checkable was found: no names, ID numbers, UPI IDs or links.",
                "जाँचने लायक कुछ नहीं मिला: कोई नाम, ID नंबर, UPI ID या लिंक नहीं।"),
    "source": ("Source", "स्रोत"),
    "record": ("Record", "रिकॉर्ड"),
    "match": ("match", "मेल"),
    "checked": ("Checked", "जाँच का समय"),
    "official": ("Open the official page ↗", "आधिकारिक पेज खोलें ↗"),
    "limits": ("Limits of this check: ", "इस जाँच की सीमाएँ: "),
    "order": ("SEBI order", "SEBI आदेश"),
    "read_order": ("Read the order ↗", "आदेश पढ़ें ↗"),
    "cant_verify": ("Couldn't verify this just now. That is not a clean result: open the official page and check it yourself.",
                    "यह अभी जाँचा नहीं जा सका। यह साफ़ नतीजा नहीं है: आधिकारिक पेज खोलकर खुद जाँचें।"),
    "next": ("What to do now", "अब क्या करें"),
    "no_log": ("No checks yet.", "अभी तक कोई जाँच नहीं हुई।"),
    "runs": ("Checks run", "की गई जाँचें"),
    "median": ("Median time", "औसत समय"),
    "high": ("High risk", "ज़्यादा जोखिम"),
    "log_note": ("Every check is logged with the time, the verdicts and a fingerprint (hash) of the forward. "
                 "The forward itself is never stored.",
                 "हर जाँच समय, फ़ैसलों और संदेश की फ़िंगरप्रिंट (हैश) के साथ दर्ज होती है। संदेश खुद कभी नहीं रखा जाता।"),
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

# The three demo buttons: real forwards from official advisories, kept in test_forwards/forwards.json.
DEMOS = {"UGC-B": "Fake university", "INV-2": "Stock tip channel", "TAX-1": "Fake tax link"}
DEMOS_HI = {"UGC-B": "फ़र्ज़ी विश्वविद्यालय", "INV-2": "शेयर टिप चैनल", "TAX-1": "फ़र्ज़ी टैक्स लिंक"}

with st.sidebar:
    lang = LANGS[st.radio("Reply language / भाषा", list(LANGS))]


def T(key):
    return UI[key][1 if lang == "hi" else 0]


def label(key, table):
    english, hindi, colour = table[key]
    return (hindi if lang == "hi" else english), colour


with st.sidebar:
    ai = brain.available()
    st.caption((T("ai_on") + " → ".join(ai) + " → rules") if ai else T("ai_off"))
    st.caption(T("rules_note") + ", ".join(agent.TOOLS))
    st.caption(T("privacy"))

st.title("Parakh")
st.caption(T("tagline"))


def show_check(c):
    """One check inside an item's box: verdict, reason, then the dated evidence line and the official link."""
    r = c["result"]
    name, _ = label(c["verdict"], verdict.VERDICTS)
    st.badge(name, color=label(c["verdict"], verdict.VERDICTS)[1])
    st.write(ids.mask(c["reason"]))
    if c["verdict"] == "COULDNT_VERIFY":
        st.warning(T("cant_verify"))
    top = r["matches"][0] if r["matches"] else None
    bits = [f"{T('source')}: {r['source']}" + (f" ({r['organisation']})" if r["organisation"] else "")]
    if r["list_type"] == "orders" and r["status"] == "found" and top:
        # A SEBI order: the match holds the order's title, its date (in "id") and a link to read it.
        bits.append(f"{T('order')}: {top['name']} · {top.get('id', '')}")
    elif top:
        bits.append(f"{T('record')}: {top['name']} {top.get('id', '')} · {T('match')} {top['score']}%")
    if r["checked_at"]:
        bits.append(f"{T('checked')} {r['checked_at'].replace('T', ' ')}")
    st.caption(ids.mask(" · ".join(bits)))
    if r["list_type"] == "orders" and r["status"] == "found" and top and top.get("url"):
        st.markdown(f"[{T('read_order')}]({top['url']})")
    if r["source_url"]:
        st.markdown(f"[{T('official')}]({r['source_url']})")
    if r["limitations"]:
        st.caption(T("limits") + r["limitations"])


def show(report):
    text, colour = label(report["headline"], verdict.HEADLINES)
    st.markdown(f"## :{colour}[{text}]")
    if report.get("summary"):
        st.caption(T("asks") + ids.mask(report["summary"]))
    st.write(ids.mask(report["explanation"]))

    if report["flags"]:
        st.subheader(T("warn_title"))
        for f in report["flags"]:
            st.markdown(f"- {ids.mask(f['reason'])}" + (f" *({T('by_ai')})*" if f["by"] == "AI" else ""))

    st.subheader(T("evidence"))
    by_item = {}
    for c in report["checks"]:
        by_item.setdefault(c["item"], []).append(c)
    if not by_item:
        st.info(T("nothing"))
    for item, checks in by_item.items():
        with st.container(border=True):
            overall, colour = label(report["items"][item], verdict.VERDICTS)
            st.markdown(f"**{ids.mask(item)}** · :{colour}[{overall}]")  # the report holds phone numbers in full
            for c in checks:
                show_check(c)

    st.subheader(T("next"))
    steps = report["next_steps"]
    st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)))


def load_demo(forward_id):
    """Button callback: put a real forward into the text box and ask for a live check."""
    forwards = json.loads(Path("test_forwards/forwards.json").read_text(encoding="utf-8"))
    st.session_state.text = next(f["text"] for f in forwards if f["id"] == forward_id)
    st.session_state.go = True


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


check_tab, log_tab, sources_tab = st.tabs([T("tab_check"), T("tab_log"), T("tab_sources")])

with check_tab:
    st.caption(T("demo"))
    cols = st.columns(len(DEMOS))
    for col, (fid, name) in zip(cols, DEMOS.items()):
        col.button(DEMOS_HI[fid] if lang == "hi" else name, key=f"demo_{fid}", on_click=load_demo, args=(fid,),
                   width="stretch")
    text = st.text_area(T("paste"), key="text", height=170, placeholder=T("placeholder"))
    files = st.file_uploader(T("upload"), type=["png", "jpg", "jpeg", "webp", "pdf"], accept_multiple_files=True)
    image_texts = screenshot_texts(files)
    go = st.session_state.pop("go", False)  # set by a demo button
    if st.button(T("check"), type="primary") or go:
        pdfs = [(f.name, f.getvalue(), f.type) for f in files if f.type == "application/pdf"]
        full_text = "\n".join([text] + image_texts)
        if not full_text.strip() and not pdfs:
            st.warning(T("empty"))
        else:
            with st.status(T("investigating"), expanded=True) as status:
                try:
                    report = agent.run_check(full_text, pdfs, lang, on_step=st.write)
                    status.update(label=f"{T('done')} {report['duration_ms'] / 1000:.1f} s · "
                                        f"{len(report['checks'])} {T('checks')} · {report['mode']}",
                                  state="complete", expanded=False)
                    st.session_state.report = report
                except Exception:  # never show a stack trace to a user, and never guess a verdict
                    status.update(label=T("crashed"), state="error")
    if "report" in st.session_state:
        show(st.session_state.report)

with log_tab:
    rows = store.recent_checks()
    if not rows:
        st.info(T("no_log"))
    else:
        df = pd.DataFrame(rows, columns=["time", "headline", "items", "verdicts", "ms", "mode", "fingerprint"])
        c1, c2, c3 = st.columns(3)
        c1.metric(T("runs"), len(df))
        c2.metric(T("median"), f"{df['ms'].median() / 1000:.1f} s")
        c3.metric(T("high"), int((df["headline"] == "HIGH_RISK").sum()))
        st.dataframe(df, hide_index=True, width="stretch")
        st.caption(T("log_note"))

with sources_tab:
    st.write(T("src_intro"))
    sebi_page = "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId="
    sources = [
        ("SEBI investment advisers", "SEBI", "Live search every time", sebi_page + "13"),
        ("SEBI research analysts", "SEBI", "Live search every time", sebi_page + "14"),
        ("SEBI stock brokers (equity segment)", "SEBI", "Live search every time", sebi_page + "30"),
        ("SEBI enforcement orders", "SEBI", "Live search of order titles every time",
         "https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=0"),
        ("Website age and short-link destination", "RDAP (public domain registry)", "Live lookup every time",
         "https://rdap.org"),
        ("RBI registered NBFCs and ARCs", "RBI", "Downloaded by hand; list as on 30 Sep 2026",
         "https://www.rbi.org.in/Scripts/BS_NBFCList.aspx"),
        ("RBI cancelled NBFC registrations", "RBI", "Downloaded by hand; list as on 30 Sep 2026",
         "https://www.rbi.org.in/Scripts/BS_NBFCList.aspx"),
        ("RBI Alert List (unauthorised forex platforms)", "RBI", "Downloaded by hand; list updated 19 Nov 2025",
         "https://www.rbi.org.in/Scripts/bs_viewcontent.aspx?Id=4235"),
        ("UGC list of fake universities", "UGC", "Live page, cached 24 h", lists.UGC_URL),
        ("IRDAI insurers and brokers", "IRDAI", "Live pages, cached 24 h", "https://irdai.gov.in/list-of-life-insurers1"),
        ("AMFI mutual fund distributors", "AMFI", "Live search every time", lists.AMFI_PAGE),
        ("ID and link format checks", "Parakh rules", "Offline, never fails", ""),
        ("Bank websites (25 banks' official domains)", "RBI .bank.in mandate", "Domain list read from each bank's "
         "own site on 1 Nov 2026", "https://website.rbi.org.in/web/rbi/-/notifications/circular-migration-to-.bank.in-domain"),
        ("UPI payment QR codes", "Parakh rules", "Decoded offline (OpenCV); compared with the message. Recipient is never "
         "verified: a QR's name is typed by its maker", "https://siportal.sebi.gov.in/intermediary/sebi-check"),
        ("URLhaus malware URL list (links inside QR codes)", "abuse.ch",
         "Last-30-days export, cached 1 h; needs a free key (URLHAUS_AUTH_KEY)", "https://urlhaus.abuse.ch/"),
    ]
    st.dataframe(pd.DataFrame(sources, columns=[T("col_source"), T("col_org"), T("col_how"), T("col_page")]),
                 hide_index=True, width="stretch",
                 column_config={T("col_page"): st.column_config.LinkColumn()})
    snaps = store.snapshots()
    if snaps:
        st.dataframe(pd.DataFrame(snaps, columns=[T("cached"), T("fetched"), T("dated"), T("size")]),
                     hide_index=True, width="stretch")
    if st.button(T("refresh")):
        store.clear_snapshots()
        with st.spinner(T("refreshing")):
            lists.search_ugc_fake("refresh")
            lists.search_irdai("refresh")
        st.rerun()
