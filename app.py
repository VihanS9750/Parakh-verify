"""Parakh web app. Run:  streamlit run app.py

Owner: Vihan (check page) and Atharva (check log and sources pages).
"""
import pandas as pd
import streamlit as st

import agent
import store
import verdict
from connectors import lists

st.set_page_config(page_title="Parakh", page_icon="🔎", layout="centered")
LANGS = {"English": "en", "हिन्दी (Hindi)": "hi", "தமிழ் (Tamil)": "ta", "मराठी (Marathi)": "mr"}

with st.sidebar:
    lang = LANGS[st.radio("Reply language", list(LANGS))]
    if agent.ai_available():
        st.success(f"AI on: {agent.MODEL}")
    else:
        st.warning("Rules-only mode. Add ANTHROPIC_API_KEY to .env to let Claude read screenshots and plan checks.")
    st.caption("Connected checks: " + ", ".join(t.replace("_", " ") for t in agent.TOOLS))
    st.caption("Aadhaar and PAN numbers are masked on this computer before anything is sent. "
               "We store a fingerprint of each forward, never the forward itself.")

st.title("Parakh")
st.caption("Don't trust the forward. Verify the evidence.")


def label(key, table):
    english, hindi, colour = table[key]
    return (hindi if lang == "hi" else english), colour


def show(report):
    text, colour = label(report["headline"], verdict.HEADLINES)
    st.markdown(f"## :{colour}[{text}]")
    if report["summary"]:
        st.caption(f"What the message asks you to do: {report['summary']}")
    st.write(report["explanation"])
    if report["language"] != lang:
        st.caption("Press “Check it” again to get the explanation in the newly chosen language.")

    if report["flags"]:
        st.subheader("Warning signs in the wording")
        for f in report["flags"]:
            st.markdown(f"- {f['reason']}" + ("  _(spotted by AI)_" if f["by"] == "AI" else ""))

    st.subheader("Evidence, item by item")
    by_item = {}
    for c in report["checks"]:
        by_item.setdefault(c["item"], []).append(c)
    if not by_item:
        st.info("Nothing checkable was found: no names, ID numbers, UPI IDs or links.")
    for item, checks in by_item.items():
        with st.container(border=True):
            overall, colour = label(report["items"][item], verdict.VERDICTS)
            st.markdown(f"**{item}** · :{colour}[{overall}]")
            for c in checks:
                r = c["result"]
                name, colour = label(c["verdict"], verdict.VERDICTS)
                st.badge(name, color=colour)
                st.write(c["reason"])
                top = r["matches"][0] if r["matches"] else None
                bits = [f"Source: {r['source']}" + (f" ({r['organisation']})" if r["organisation"] else "")]
                if top:
                    bits.append(f"Record: {top['name']} {top.get('id', '')} · match {top['score']}%")
                if r["checked_at"]:
                    bits.append(f"Checked {r['checked_at'].replace('T', ' ')}")
                st.caption(" · ".join(bits))
                if r["source_url"]:
                    st.markdown(f"[Open the official page ↗]({r['source_url']})")
                if r["limitations"]:
                    st.caption(f"Limits of this check: {r['limitations']}")

    st.subheader("What to do now")
    steps = verdict.NEXT_STEPS[report["headline"]].get(lang) or (
        report["next_steps"] if report["language"] == lang else verdict.NEXT_STEPS[report["headline"]]["en"])
    st.markdown("\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)))


check_tab, log_tab, sources_tab = st.tabs(["Check a forward", "Check log", "Sources"])

with check_tab:
    text = st.text_area("Paste the message", height=170,
                        placeholder="e.g. Invest ₹50,000 with ABC Investments. Our SEBI-registered adviser "
                                    "guarantees 4% monthly returns…")
    files = st.file_uploader("…or add screenshots or PDFs", type=["png", "jpg", "jpeg", "webp", "pdf"],
                             accept_multiple_files=True)
    if st.button("Check it", type="primary"):
        if not text.strip() and not files:
            st.warning("Paste a message or add a file first.")
        else:
            if any(f.type.startswith("image/") for f in files) and not agent.ai_available():
                st.warning("Screenshots need AI to read. In rules-only mode only the pasted text and PDFs are checked.")
            with st.status("Investigating…", expanded=True) as status:
                report = agent.run_check(text, [(f.name, f.getvalue(), f.type) for f in files], lang,
                                         on_step=st.write)
                status.update(label=f"Done in {report['duration_ms'] / 1000:.1f} s · {len(report['checks'])} checks"
                                    f" · {report['mode']}", state="complete", expanded=False)
            st.session_state.report = report
    if "report" in st.session_state:
        show(st.session_state.report)

with log_tab:
    rows = store.recent_checks()
    if not rows:
        st.info("No checks yet.")
    else:
        df = pd.DataFrame(rows, columns=["time", "headline", "items", "verdicts", "ms", "mode", "fingerprint"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Checks run", len(df))
        c2.metric("Median time", f"{df['ms'].median() / 1000:.1f} s")
        c3.metric("High risk", int((df["headline"] == "HIGH_RISK").sum()))
        st.dataframe(df, hide_index=True, width="stretch")
        st.caption("Every check is logged with the time, the verdicts and a fingerprint (hash) of the forward. "
                   "The forward itself is never stored.")

with sources_tab:
    st.write("Where each check gets its answer. Lists are re-downloaded every 24 hours; if a site is down we use "
             "our last dated copy and say so.")
    sources = [
        ("UGC list of fake universities", "UGC", "Live page, cached 24 h", lists.UGC_URL),
        ("IRDAI insurers and brokers", "IRDAI", "Live pages, cached 24 h", "https://irdai.gov.in/list-of-life-insurers1"),
        ("AMFI mutual fund distributors", "AMFI", "Live search every time", lists.AMFI_PAGE),
        ("ID and link format checks", "Parakh rules", "Offline, never fails", ""),
        ("SEBI registers", "SEBI", "Rahul's connector" + ("" if agent.sebi else " (not merged yet)"), ""),
        ("RBI lists", "RBI", "Rahul's connector" + ("" if agent.rbi else " (not merged yet)"), ""),
    ]
    st.dataframe(pd.DataFrame(sources, columns=["Source", "Organisation", "How we read it", "Official page"]),
                 hide_index=True, width="stretch",
                 column_config={"Official page": st.column_config.LinkColumn()})
    snaps = store.snapshots()
    if snaps:
        st.dataframe(pd.DataFrame(snaps, columns=["Cached list", "Fetched at", "List dated", "Size (bytes)"]),
                     hide_index=True, width="stretch")
    if st.button("Refresh official lists now"):
        store.clear_snapshots()
        with st.spinner("Downloading UGC and IRDAI lists…"):
            lists.search_ugc_fake("refresh")
            lists.search_irdai("refresh")
        st.rerun()
