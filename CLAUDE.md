# Parakh: project context for Claude Code

Read this before writing any code. Three beginners (Vihan, Rahul, Atharva) are building this in 48 hours for the Forge AI buildathon (NxtWave), problem statement **T1.4: fact-verification and deepfake audit**. Each of them must be able to explain every line to the judges, so keep code simple and explain what you change.

## What we are building

Someone forwards a scary notice, a stock tip, an adviser's details or a loan app. Parakh reads it, checks it against **live official Indian records**, and replies with:

1. a verdict,
2. the source links it checked, with the time of each check,
3. what to do next (for example, call 1930 or report on cybercrime.gov.in).

Pitch line: **"Don't trust the forward. Verify the evidence."** The product is the verification engine, not a chatbot. We sell the quality of each investigation, not the number of sources.

**Hero feature: one forward, many checks.** Given "Invest ₹50,000 with ABC Investments. Our SEBI-registered adviser guarantees 4% monthly returns. Download our app here.", Parakh extracts every item (firm, adviser registration, the return claim, the app), checks each against the right record, and returns one consolidated report. Build and demo this path first.

We are not first. SEBI's "Spot a Scam" and SEBI Check, RBI Sachet and Truecaller's Scam Checker each cover a slice. Our edge is: the forward itself as input, every item checked, one dated evidence report. Market context and competitors: [docs/market-analysis.md](docs/market-analysis.md).

## Hard rules (breaking 1–4 disqualifies the team)

1. **No fake data, ever.** Never write mock, sample, placeholder or hardcoded registry data, not even in tests or demos. Every result comes from a live lookup or a dated download from the official site. Store `checked_at` / `fetched_at` and show it.
2. **Built during the event.** Commit small and often; the git history is our proof. Reuse no code from other projects (especially RaazMD or its Bolna voice agent).
3. **Live demo only.** No pre-recorded output passed off as live.
4. **Everyone can explain everything.** Prefer plain functions and the standard library. No frameworks or abstractions we don't need. After each change, explain it in two or three sentences.
5. **Never call a named firm or person a "fraud".** Say "not found in the SEBI investment adviser register as of 14:32 IST".
6. **Never automate a captcha, login or OTP portal** (CBIC, income tax, eCourts, GST search, cybercrime.gov.in). Validate the ID offline and give the user the official link. No captcha-solving libraries. Wait a few seconds between requests to the same site. Respect each site's terms.
7. **Narrow purpose.** Parakh is a verification service, not a general chatbot (WhatsApp has banned general-purpose AI bots since Jan 2026).
8. **Protect personal data.** Redact Aadhaar, PAN and account numbers before sending anything to Claude. Never store them; mask them in logs.
9. **Secrets live in `.env`** (never committed). See `.env.example`.

## How it works

```
user forward (text / screenshot / PDF)
  -> app.py      Streamlit page                     (Vihan)
  -> agent.py    Claude reads it, plans checks,     (Vihan)
                 calls connectors, writes verdict
  -> connectors/ one file per official source       (Rahul: money, Atharva: government)
  -> store.py    SQLite: dated downloads + check log (Atharva)
  -> verdict card back in app.py
```

Claude (`claude-sonnet-5-5` via the `anthropic` Python SDK, with tool use) reads screenshots and PDFs directly, so there is no separate OCR step.

## The connector contract

Every connector is one function in `connectors/<source>.py` that returns this dict. This is what lets three people build in parallel.

```python
{
    "source": "SEBI investment adviser register",
    "organisation": "SEBI",
    "query": "29K Investment Advisers",
    "status": "found",          # found | not_found | unavailable | needs_user
    "matches": [{"name": "29K INVESTMENT ADVISERS PRIVATE LTD", "id": "INA200000365", "score": 97}],
    "source_url": "https://www.sebi.gov.in/...",
    "checked_at": "2026-10-31T14:32:05+05:30",
    "limitations": "Covers SEBI-registered investment advisers only; absence is not proof of fraud.",
}
```

`score` is the match confidence (0–100) shown to the user.

- `unavailable`: the site timed out or errored (time out after a few seconds, retry once).
- `needs_user`: the source is gated (captcha/OTP), so we return the official link for the user to confirm there.
- Each connector file ends with an `if __name__ == "__main__":` block that runs one **live** lookup and asserts the shape. That is our only test per connector.

**The verdict is decided by plain code rules, never by Claude.** Claude only extracts items from the forward, chooses which connectors to call, and explains the result in plain language. Per item:

1. **Matched:** exact ID match, or name + ID match
2. **Needs clarification:** several close matches, or the name matches but the ID doesn't
3. **Not found in the checked register:** the search succeeded and returned nothing (never "fraud")
4. **Couldn't verify:** source unavailable or gated, so give the official link

Claims get separate **warning signs** (guaranteed returns, urgency, secrecy, "pay to avoid arrest", payment handle of a claimed adviser not ending in "@valid").

Careful with what a match means:
- A lender being a registered NBFC does **not** make an app claiming to work with it legitimate. Check the app–lender link in RBI's digital lending app list.
- A court case involving a person or firm does **not** mean they are fraudulent.

Translate the next steps, not just the verdict (Hindi plus one more language).

## How we measure it

Run 20 real forwards and report: items extracted correctly, right source chosen, checks that succeeded, false alarms, average time, and correct "couldn't verify" answers. Abstaining correctly counts as a win.

## Planned layout

```
app.py              Streamlit page                         Vihan
agent.py            Claude tool loop + verdict             Vihan
store.py            SQLite: downloads + check log          Atharva
connectors/
  sebi.py           SEBI registers (live, cached)          Rahul
  rbi.py            RBI NBFC / forex Alert / lending apps  Rahul
  lists.py          UGC fake list, AMFI, IRDAI             Atharva
  ids.py            GSTIN / CIN / CNR / DIN format checks  Atharva
                    + official deep links
docs/               market analysis, pitch notes
test_forwards/      real forwards for testing (redact private people's details first)
```

Create files only when the plan reaches them. Don't scaffold ahead.

## Sources and what we know

Tested 31 Oct 2026 from a fetcher that may be outside India. Full detail: [docs/market-analysis.md](docs/market-analysis.md).

| Source | How we use it | Status |
|---|---|---|
| SEBI registered intermediaries (advisers: ~1,071 rows, "as on" date shown) | **Live**, polite fetch + cache | Loaded; no captcha, no export, robots.txt allows |
| AMFI distributor search (ARN) | Live or dated list | Loaded |
| IRDAI insurer / broker / agent lists | Dated list | Homepage loaded; list pages not opened |
| RBI NBFC list, forex Alert List (95 names, Nov 2025), lending-app list | **Dated list, downloaded by hand in a browser** | RBI returned HTTP 418 to scripts |
| UGC fake universities (32, Feb 2026) | Dated list | Not loaded in test |
| eCourts, income tax notice check, CBIC DIN, GST search, cybercrime.gov.in, PIB Fact Check | **Format check + official link only** | Captcha, OTP or login-gated |

No source has an official public API. Atharva re-checks each from an Indian connection on Day 1 and updates this table.

Wording: say "not found in the <list> downloaded on <date>", never "fraud", unless an official source (a SEBI caution, the RBI Alert List) names it.

## Git workflow

- One branch per person: `vihan/<thing>`, `rahul/<thing>`, `atharva/<thing>`.
- Pull `main` before starting; open a small pull request into `main` when a part works.
- Never commit `.env`, `*.db` or unredacted forwards.
