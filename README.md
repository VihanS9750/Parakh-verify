# Parakh

**Don't trust the forward. Verify the evidence.**

Indians reported losing ₹22,495 crore to cyber fraud in 2025, about three quarters of it to fake investment tips and apps ([sources](docs/market-analysis.md)). Most of these scams can be caught by checking a public official register, but people don't know which register to open.

Parakh takes the forwarded message itself: a "SEBI-registered" stock tip, a tax notice, a university admission offer or a KYC alert. It pulls out every checkable item (firm names, registration numbers, UPI IDs, links, universities, ID numbers) and checks each one against the right live official Indian record. For every item it shows what it found, in which official source, at what time, and what to do next.

Built at the Forge AI buildathon (NxtWave), 31 Oct to 1 Nov 2026, by Vihan, Rahul and Atharva. Problem statement **T1.4: fact-verification**.

## How it works

```
forward (pasted text, screenshot or PDF)
  1. read the text   agent.read_image (Tesseract OCR), pdfplumber   screenshots are read on the laptop, never sent to the AI
  2. find + pick     brain.py (AI) and agent.investigate (rules)   Gemini, then Groq, then plain rules choose the checks;
                                                                   the rules' own checks always run too
  3. check records   connectors/                           live official sources (table below), dated copies if a site is down
  4. decide          verdict.py                            fixed, readable rules turn each result into a verdict
  5. explain         brain.explain (AI) or a template      English or Hindi, with the next steps
  -> app.py shows every item with its source, record, time and a link to the official page
```

**The AI investigates and explains; fixed rules decide.** In AI mode the masked text of the forward is sent to Google (Gemini) or, if that fails, Groq (Qwen), both on free tiers. Aadhaar, PAN and mobile numbers keep only their last 4 characters first (`ids.mask`); other details in the text, such as names, UPI IDs and links, are sent as written. Images are never sent. With no API key the app runs rules-only, entirely on the laptop. Every verdict can be traced to a line in `verdict.py`; an AI-spotted warning sign must quote words that are really in the message and can't make a message High risk alone. Aadhaar and PAN are never looked up. The check log stores a fingerprint (hash) of each forward, never the forward itself.

## Official sources

| Source | How Parakh reads it | Status (tested 1 Nov 2026 from India) |
|---|---|---|
| SEBI investment advisers, research analysts, brokers | Live search, same request as SEBI's own search page (Rahul, `connectors/sebi.py`) | Working |
| SEBI enforcement orders | Live search of order titles (`connectors/sebi_orders.py`) | Working; titles only, the order text is not read |
| UGC list of fake universities (32 names, February 2026) | Live page, cached 24 h | Working |
| IRDAI life, general and health insurers and brokers | Live pages, cached 24 h | Working |
| AMFI mutual fund distributors | Live search behind AMFI's public page | Working |
| GSTIN, PAN, CIN, eCourts CNR, Income Tax DIN, CBIC DIN, SEBI numbers, AMFI ARN, UPI IDs, links | Offline format and check-digit rules, plus the official page to confirm | Working |
| RBI Alert List, registered and cancelled NBFCs | RBI returns HTTP 418 to scripts, so the lists were downloaded by hand on 1 Nov 2026 and are searched offline (`data/`, Rahul) | Connected; every result states the list's own date (NBFC lists as on 30 Sep 2026, Alert List updated 19 Nov 2025) |
| Website age, short-link destination | Public RDAP registry and the shortener's redirect header (`connectors/links.py`) | Working; no record for some `.edu` and country domains |
| MCA, GST, eCourts, Income Tax portals | Captcha, OTP or login: format check and link only. We never get around a block. | By design |

Our user agent says who we are, and we make at most one request per second per site.

## Verdicts

Each item gets one of eleven verdicts, such as *Matches the official record*, *On an official warning list*, *Not found in the checked register* or *Couldn't verify right now*. The message as a whole is rated **High risk**, **Be careful** or **Consistent with official records**.

Parakh never calls a named firm a fraud. It says what the official record shows and when it was checked. The full rules are in [CLAUDE.md](CLAUDE.md#verdicts-verdictpy-plain-rules) and [verdict.py](verdict.py).

## Test results

The test set is 23 messages in [test_forwards/forwards.json](test_forwards/forwards.json), each with its source: 20 scams from SEBI orders, PIB debunks, police advisories and news, and 3 genuine messages. Full table: [docs/eval-results-rules.md](docs/eval-results-rules.md) and [docs/eval-results-ai.md](docs/eval-results-ai.md).

| Measure | Result |
|---|---|
| Scams rated High risk | 16 of 20 rules-only, 19 of 20 with AI (see the two results files) |
| Scams wrongly rated Consistent (the dangerous error) | 0 of 20 |
| Genuine messages wrongly rated High risk | 0 of 3 |

This is a regression check, not an accuracy claim. The sample is small, and the warning-sign rules were written from the same advisories the examples come from.

## Run it

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
copy .env.example .env          (add a free Gemini key from aistudio.google.com; Groq key optional)
winget install UB-Mannheim.TesseractOCR
.venv\Scripts\streamlit run app.py
```

Screenshots are read offline by Tesseract. For Hindi, put `eng.traineddata` and `hin.traineddata` from github.com/tesseract-ocr/tessdata_fast in a `tessdata\` folder here (not committed). Without a key the app runs in rules-only mode. Without Tesseract, screenshots can't be read: images are never sent to the AI, because an image can't be masked. Before any text goes to the AI, Aadhaar, PAN and phone numbers are masked to their last 4 characters.

Self-checks, which run live lookups:

```
.venv\Scripts\python verdict.py
.venv\Scripts\python -m connectors.ids
.venv\Scripts\python -m connectors.lists
.venv\Scripts\python -m connectors.sebi "29K Investment Advisers"
.venv\Scripts\python agent.py
.venv\Scripts\python brain.py      (checks the AI keys and model names)
.venv\Scripts\python eval.py
```

## Team

| Person | Owns (explains to the judges) |
|---|---|
| Vihan | `agent.py` (pipeline), `verdict.py` (rules), `app.py` check page |
| Rahul | `connectors/sebi.py`, `base.py`, `matching.py`, `local_list.py` (SEBI and hand-downloaded lists), `eval.py` |
| Atharva | `connectors/lists.py` (UGC, IRDAI, AMFI), `connectors/ids.py` (ID and link checks), `connectors/net.py`, `store.py`, app check log and sources pages |

We wrote the code with AI coding assistants, as the rules allow. Every owner reviews their files and can explain them.

## How we built it

- [docs/build-log.md](docs/build-log.md): timeline, decisions and what we changed, from the git history.
- [docs/research/](docs/research/): how we chose the problem statement, market and competitor research, Indian ID formats, the scam corpus, and the options for our own model.
- [docs/market-analysis.md](docs/market-analysis.md): problem size, competitors, data access, positioning.
- [CLAUDE.md](CLAUDE.md): the team brief, covering rules, architecture, the connector contract and verdicts.
