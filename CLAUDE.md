# Parakh: project context for Claude Code

Read this before writing any code. Three beginners (Vihan, Rahul, Atharva) are building this for the Forge AI buildathon (NxtWave), problem statement **T1.4: fact-verification and deepfake audit**. Each of them must be able to explain every line to the judges, so keep code simple and explain what you change.

## What we are building

Someone forwards a scary notice, a stock tip, an adviser's details or a loan app. Parakh reads it, checks it against **live official Indian records**, and replies with:

1. a verdict for each item in the message, and one overall verdict,
2. the official source checked for each item, with the time of the check,
3. what to do next (for example, call 1930 or report on cybercrime.gov.in), in English, Hindi, Tamil or Marathi.

Pitch line: **"Don't trust the forward. Verify the evidence."** The product is the verification engine, not a chatbot.

**Hero feature: one forward, many checks.** Parakh pulls every item out of one message (firm, registration number, UPI ID, link, university, the "guaranteed returns" claim) and checks each against the right record in one report.

We are not first. SEBI's "Spot a Scam" and SEBI Check, RBI Sachet and Truecaller's Scam Checker each cover a slice, and "LLM extracts, code decides" is a known pattern. Our edge: the forward itself as input, every item checked against several Indian regulators, a dated record per item. Market context: [docs/market-analysis.md](docs/market-analysis.md).

## Hard rules (breaking 1–4 disqualifies the team)

1. **No fake data, ever.** Never write mock, sample, placeholder or hardcoded registry data, not even in tests or demos. Every result comes from a live lookup or a dated download from the official site, with its time shown.
2. **Built during the event.** Commit small and often; the git history is our proof. Reuse no code from other projects (especially RaazMD or its Bolna voice agent).
3. **Live demo only.** No pre-recorded output passed off as live.
4. **Everyone can explain everything.** Prefer plain functions and the standard library. No frameworks or abstractions we don't need. After each change, explain it in two or three sentences.
5. **Never call a named firm or person a "fraud".** Say "not found in the SEBI investment adviser register as of 14:32 IST".
6. **Never get around a block.** No captcha solving, no login/OTP automation, no browser-like headers to dodge a bot filter (RBI returns HTTP 418 to scripts: download its lists by hand). Our user agent says who we are (`connectors/net.py`), 1 request/second per site.
7. **Narrow purpose.** Parakh is a verification service, not a general chatbot (WhatsApp has banned general-purpose AI bots since Jan 2026).
8. **Protect personal data.** Aadhaar and PAN numbers are never looked up or sent anywhere (`agent.investigate` skips them). The check log stores a hash of the forward, never the forward.
9. **No external AI service and no pretrained model** (organisers, 1 Nov). Everything runs on the laptop. A model we train ourselves from public data is allowed in principle; see [docs/research/own-model-plan.md](docs/research/own-model-plan.md).

## How it works

```
forward (pasted text / PDF)
  -> app.py         Streamlit page: check, check log, sources            (Vihan, Atharva)
  -> agent.py       1. regexes find IDs, UPI IDs, links, organisation names   (Vihan)
                    2. keywords in the message pick the register for each item
                    4. a template explains the result (English or Hindi)
  -> verdict.py     3. plain rules decide every verdict + warning signs   (Vihan)
  -> connectors/    one function per official source                     (Rahul: SEBI/RBI, Atharva: rest)
  -> store.py       SQLite: dated copies of lists + check log              (Atharva)
```

Screenshots are not read yet: OCR (Tesseract) waits on the organisers' answer about pretrained models.

## The connector contract

Every connector returns this dict (build it with `net.result(...)`):

```python
{
    "source": "AMFI mutual fund distributor register",
    "organisation": "AMFI",
    "query": "Sunil Kamdar",
    "status": "found",            # found | not_found | unavailable | needs_user | invalid
    "matches": [{"name": "Sunil A Kamdar", "id": "ARN-108", "score": 95}],   # score = match confidence 0-100
    "source_url": "https://www.amfiindia.com/locate-distributor",
    "checked_at": "2026-11-01T06:25:11+05:30",
    "limitations": "AMFI's register of mutual fund distributors ...",
    "list_type": "register",      # register (found = good) | warning_list (found = bad) | format (ID checks)
    "detail": "",
}
```

- `found` means best match scores ≥ 90 (`lists.FOUND_AT`); matching uses rapidfuzz `WRatio` after dropping "Pvt/Ltd/Limited" (`lists.best_matches`).
- `unavailable`: site down after one retry. Lists fall back to the last dated copy and say so.
- `needs_user`: format is valid but only the official page can confirm it (we give the link).
- `invalid`: fails a format/check-digit test, or a link pretends to be a government site.
- Each connector file ends with an `if __name__ == "__main__":` block that runs **live** lookups. Run as `python -m connectors.lists`.

**Rahul's connectors** use their own shape (`connectors/base.py`: `note`, `data_as_of`, found at 70+). `agent._sebi` wraps `sebi.search()` into the dict above and re-applies our found-at-90 bar. Only the investment adviser register is live (`sebi.INTM_IDS`); research analysts and brokers need their `intmId` captured. An RBI connector should provide `rbi.search_rbi(name)` returning the dict above (`list_type="warning_list"` for the Alert List); `agent.py` picks it up automatically.

## Verdicts (verdict.py, plain rules)

| Verdict | When |
|---|---|
| Matches the official record | register match ≥ 95, no rival within 3 points, claimed ID (if any) agrees, not expired |
| On an official warning list | ≥ 95 match on UGC fake list / RBI Alert List |
| Fails an authenticity check | bad GSTIN check digit, fake government-looking link, shortener, .apk |
| Not found in the checked register | search worked, nothing ≥ 90 |
| Needs clarification | 90–94 match, close rivals, name matches but number differs, registration expired |
| Not on the official warning list | neutral: not proof of anything |
| Format OK: confirm on the official page | valid format, gated source (eCourts, income tax, CBIC, GST) |
| Couldn't verify right now | source down |

Each item takes its most telling verdict (`verdict.RANK`). Overall: **High risk** if any red verdict, or a doubtful item plus a warning sign, or 2+ warning signs; **Consistent** only if every item matched and there are no warning signs; otherwise **Be careful**. Warning signs come from fixed patterns based on SEBI/RBI/I4C/PIB advisories (`verdict.RED_FLAGS`).

Careful with what a match means: a registered NBFC doesn't make an app claiming to work with it legitimate (check RBI's lending-app list); a court case doesn't mean fraud; a valid ID format doesn't prove the ID was issued.

## Layout

```
app.py              Streamlit page                         Vihan / Atharva
agent.py            pipeline: find items, pick checks, report      Vihan
verdict.py          verdict rules, warning signs, next steps     Vihan
store.py            SQLite: list snapshots + check log           Atharva
eval.py             runs test_forwards/forwards.json             Rahul (scaffolded)
connectors/
  net.py            polite GET + result() shape                  Atharva
  lists.py          UGC fake list, IRDAI, AMFI (live)            Atharva
  ids.py            GSTIN/PAN/CIN/CNR/DIN/SEBI/ARN/UPI/link checks Atharva
  sebi.py           SEBI adviser search (live) + saved-page backup Rahul
  base.py, matching.py, local_list.py   Rahul's helpers; local_list = hand-downloaded lists (RBI)
test_forwards/      23 forwards from official advisories/news, with sources
docs/               build log, market analysis, eval results, research/
```

## Run and test

```
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app.py
.venv\Scripts\python verdict.py ; .venv\Scripts\python -m connectors.ids ; .venv\Scripts\python -m connectors.lists ; .venv\Scripts\python -m connectors.sebi "29K Investment Advisers" ; .venv\Scripts\python agent.py ; .venv\Scripts\python eval.py
```

## Sources (tested from an Indian connection, 1 Nov 2026)

| Source | How we use it | Status |
|---|---|---|
| SEBI investment advisers | Live search (Rahul's `sebi.py`) | Working |
| SEBI research analysts, brokers | Format check + link (SEBI Check) | `intmId` not captured yet |
| UGC fake universities (32, Feb 2026) | Live HTML table, cached 24 h | Working |
| IRDAI life/general/health insurers, brokers | Live HTML tables, cached 24 h | Working |
| AMFI distributors | Live JSON search behind the public page | Working |
| RBI NBFC / Alert List / Sachet | Hand-downloaded dated lists (Rahul) | HTTP 418 to scripts, even from India |
| MCA | Format check + link only | HTTP 403 |
| CBIC DIN | Format check + link only | Timed out |
| eCourts, income tax, GST, PIB Fact Check | Format check + link only | Captcha / OTP / login |

## Git workflow

- One branch per person: `vihan/<thing>`, `rahul/<thing>`, `atharva/<thing>`.
- Pull `main` before starting; open a small pull request into `main` when a part works.
- Never commit `.env`, `*.db` or unredacted forwards.
