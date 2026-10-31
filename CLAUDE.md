# Parakh: project context for Claude Code

Read this before writing any code. Three beginners (Vihan, Rahul, Atharva) are building this in 48 hours for the Forge AI buildathon (NxtWave), problem statement **T1.4: fact-verification and deepfake audit**. Each of them must be able to explain every line to the judges, so keep code simple and explain what you change.

## What we are building

Someone forwards a scary notice, a stock tip, an adviser's details or a loan app. Parakh reads it, checks it against **live official Indian records**, and replies with:

1. a verdict,
2. the source links it checked, with the time of each check,
3. what to do next (for example, call 1930 or report on cybercrime.gov.in).

Market context and competitors: [docs/market-analysis.md](docs/market-analysis.md).

## Hard rules (breaking 1–4 disqualifies the team)

1. **No fake data, ever.** Never write mock, sample, placeholder or hardcoded registry data, not even in tests or demos. Every result comes from a live lookup or a dated download from the official site. Store `checked_at` / `fetched_at` and show it.
2. **Built during the event.** Commit small and often; the git history is our proof. Reuse no code from other projects (especially RaazMD or its Bolna voice agent).
3. **Live demo only.** No pre-recorded output passed off as live.
4. **Everyone can explain everything.** Prefer plain functions and the standard library. No frameworks or abstractions we don't need. After each change, explain it in two or three sentences.
5. **Never call a named firm or person a "fraud".** Say "not found in the SEBI investment adviser register as of 14:32 IST".
6. **Never bypass a captcha, login or OTP.** Show the captcha to the user. Wait a few seconds between requests to the same site. Respect each site's terms.
7. **Protect personal data.** Never store Aadhaar or PAN numbers; mask them in logs.
8. **Secrets live in `.env`** (never committed). See `.env.example`.

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
    "query": "29K Investment Advisers",
    "status": "found",          # found | not_found | unavailable | needs_user
    "matches": [{"name": "29K INVESTMENT ADVISERS PRIVATE LTD", "id": "INA200000365", "score": 97}],
    "source_url": "https://www.sebi.gov.in/...",
    "checked_at": "2026-10-31T14:32:05+05:30",
}
```

- `unavailable`: the site timed out or errored (time out after a few seconds, retry once).
- `needs_user`: a captcha or similar step the user must do.
- Each connector file ends with an `if __name__ == "__main__":` block that runs one **live** lookup and asserts the shape. That is our only test per connector.

The agent turns connector results into one of four verdicts:

1. Matches the official record
2. Not found in the official record
3. Warning signs (no register applies, for example a "digital arrest" call)
4. Couldn't verify right now (a source is down)

## Planned layout

```
app.py              Streamlit page                         Vihan
agent.py            Claude tool loop + verdict             Vihan
store.py            SQLite: downloads + check log          Atharva
connectors/
  sebi.py           SEBI registers                         Rahul
  rbi.py            RBI NBFC / cancelled / forex lists     Rahul
  pib.py            PIB Fact Check                         Atharva
  cbic.py           CBIC document ID (DIN)                 Atharva
  itd.py            Income tax notice check                Atharva
  ecourts.py        eCourts case status                    Atharva
docs/               market analysis, pitch notes
test_forwards/      real forwards for testing (redact private people's details first)
```

Create files only when the plan reaches them. Don't scaffold ahead.

## Sources and what we know

| Source | Status |
|---|---|
| SEBI investment adviser register (search by name or registration no.) | Loaded in a test on 31 Oct 2026; search page, no download |
| RBI list of NBFCs, cancelled list, forex Alert List | Published by RBI as PDFs/pages; not tested yet |
| CBIC DIN lookup | Captcha form; not confirmed (test fetch failed from outside India) |
| Income tax "Authenticate notice/order", eCourts, PIB Fact Check | Not tested yet |

Atharva confirms each from an Indian connection on Day 1 and updates this table.

## Git workflow

- One branch per person: `vihan/<thing>`, `rahul/<thing>`, `atharva/<thing>`.
- Pull `main` before starting; open a small pull request into `main` when a part works.
- Never commit `.env`, `*.db` or unredacted forwards.
