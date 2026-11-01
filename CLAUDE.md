# Parakh: project context for Claude Code

Read this before writing any code. Three beginners (Vihan, Rahul, Atharva) are building this for the Forge AI buildathon (NxtWave), problem statement **T1.4: fact-verification and deepfake audit**. Each of them must be able to explain every line to the judges, so keep code simple and explain what you change.

## What we are building

Someone forwards a scary notice, a stock tip, an adviser's details or a loan app. Parakh reads it, checks it against **live official Indian records**, and replies with:

1. a verdict for each item in the message, and one overall verdict,
2. the official source checked for each item, with the time of the check,
3. what to do next (for example, call 1930 or report on cybercrime.gov.in), in English or Hindi.

Input: pasted text, a screenshot, a PDF or a voice note.

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
8. **Protect personal data.** The AI only ever gets masked text: `brain.py` runs `ids.mask` on everything it sends, so Aadhaar, PAN and phone numbers keep only their last 4 characters. Images are never sent to the AI (an image can't be masked); Tesseract reads screenshots on the laptop and that text is masked like typed text. Aadhaar and PAN are never looked up. The check log stores a hash of the forward, never the forward.
9. **Free AI only, and the AI never decides a verdict.** Pretrained models are allowed (organisers, checked again 1 Nov afternoon); we use free tiers only (no paid API). Keys live in `.env`, never committed.

## How it works

```
forward (text / screenshot / PDF / voice note)
  -> app.py         Streamlit page: check, check log, sources            (Vihan, Atharva)
  -> agent.py       1. get the text: pdfplumber, Tesseract OCR (eng+hin, offline), Whisper for audio
                    2. brain.py: masks Aadhaar/PAN/phone numbers, then the AI reads the text and calls our checks as tools
                       (no images are ever sent to the AI)
                       Gemini 3.5 Flash-Lite (free) -> Groq Qwen 3.8 27B (free) -> plain rules
                       the rules' checks ALWAYS run too (safety net); duplicates are dropped
                       follow-up: every SEBI register check is followed by a SEBI enforcement-order search
                    4. the AI explains the result in English or Hindi (template when AI is off)
  -> verdict.py     3. plain rules decide every verdict + warning signs   (Vihan)
  -> connectors/    one function per official source                     (Rahul: SEBI/RBI, Atharva: rest)
  -> store.py       SQLite: dated copies of lists + check log              (Atharva)
```

The AI may add warning signs it spots (labelled "spotted by AI"), but they can only back up a rule-based finding: AI signs alone never make a message High risk (`verdict.headline`).

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

**Rahul's connectors** use their own shape (`connectors/base.py`: `note`, `data_as_of`, found at 70+). `agent._sebi` wraps `sebi.search()` into the dict above and re-applies our found-at-90 bar: a number goes to its own register (INA adviser, INH analyst, INZ broker); a name is searched in all three in turn, stopping at a strong match. Names go to SEBI only when the message is about investing. `rbi.search_rbi(name)` returns the dict above from three RBI files downloaded by hand into `data/` on 1 Nov 2026: Alert List (`warning_list`), registered NBFCs (`register`), cancelled NBFC registrations (`warning_list`); see its docstring for the order. `rbi_alert_list.search()` also matches a website/URL. Details: `connectors/FOR_VIHAN.md`.

## Verdicts (verdict.py, plain rules)

| Verdict | When |
|---|---|
| Matches the official record | register match ≥ 95, no rival within 3 points, claimed ID (if any) agrees, not expired |
| On an official warning list | ≥ 95 match on UGC fake list / RBI Alert List |
| Fails an authenticity check | bad GSTIN check digit, fake government-looking link, shortener, .apk |
| Not found in the checked register | search worked, nothing ≥ 90 |
| Needs clarification | 90–94 match, close rivals, name matches but number differs, registration expired |
| Named in a SEBI enforcement order | an order title names the firm (orange: evidence to read, never proof; some orders close a case) |
| Not on the official warning list | neutral: not proof of anything |
| No SEBI enforcement order found | neutral |
| Format OK: confirm on the official page | valid format, gated source (eCourts, income tax, CBIC, GST) |
| Couldn't verify right now | source down |

Each item takes its most telling verdict (`verdict.RANK`). Overall: **High risk** if any red verdict, or a doubtful item plus a warning sign, or 2+ warning signs of which at least one comes from the rules; **No adverse finding** (label `CONSISTENT`) only if every item matched and there are no warning signs; otherwise **Be careful**. Warning signs come from fixed patterns based on SEBI/RBI/I4C/PIB advisories (`verdict.RED_FLAGS`).

Careful with what a match means: a registered NBFC doesn't make an app claiming to work with it legitimate (check RBI's lending-app list); a court case doesn't mean fraud; a valid ID format doesn't prove the ID was issued.

## Layout

```
app.py              Streamlit page                         Vihan / Atharva
agent.py            pipeline: text, masking, rules checks, follow-ups, report   Vihan
brain.py            the AI: Gemini -> Groq tool loop, explanation, voice transcription   Vihan
verdict.py          verdict rules, warning signs, next steps     Vihan
store.py            SQLite: list snapshots + check log           Atharva
eval.py             runs test_forwards/forwards.json             Rahul (scaffolded)
connectors/
  net.py            polite GET + result() shape                  Atharva
  lists.py          UGC fake list, IRDAI, AMFI (live)            Atharva
  ids.py            GSTIN/PAN/CIN/CNR/DIN/SEBI/ARN/UPI/link checks Atharva
  links.py          short-link destination + website age (RDAP)    Vihan
  sebi_orders.py    live search of SEBI enforcement order titles   Vihan
  sebi.py           SEBI adviser/analyst/broker search (live)     Rahul
  rbi.py            RBI lists in the contract above (search_rbi)   Rahul
  rbi_nbfc.py, rbi_alert_list.py   search the RBI files in data/   Rahul
  base.py, matching.py, local_list.py   Rahul's helpers; local_list = hand-downloaded lists (RBI)
data/               RBI files downloaded by hand (dated) + CSVs   Rahul
test_forwards/      23 forwards from official advisories/news, with sources
docs/               build log, market analysis, eval results, research/
```

## Run and test

```
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
copy .env.example .env   (free GEMINI_API_KEY and GROQ_API_KEY)
winget install UB-Mannheim.TesseractOCR   (+ eng/hin tessdata_fast files in tessdata\, see README)
.venv\Scripts\streamlit run app.py
.venv\Scripts\python verdict.py ; .venv\Scripts\python -m connectors.ids ; .venv\Scripts\python -m connectors.lists ; .venv\Scripts\python -m connectors.links ; .venv\Scripts\python -m connectors.sebi_orders ; .venv\Scripts\python -m connectors.rbi ; .venv\Scripts\python agent.py ; .venv\Scripts\python brain.py
.venv\Scripts\python eval.py rules     (no AI requests; "python eval.py" uses ~3 AI requests per forward)
```

## Sources (tested from an Indian connection, 1 Nov 2026)

| Source | How we use it | Status |
|---|---|---|
| SEBI advisers, research analysts, brokers | Live search (Rahul's `sebi.py`) | Working |
| SEBI enforcement orders | Live search of order titles (`sebi_orders.py`) | Working |
| Website registration date | Public RDAP registry (rdap.org) | Working; .edu and some country domains have no records |
| SEBI/RBI/PIB RSS feeds | Not used: they hold only 1–5 days of items | Checked 1 Nov |
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
