# Rahul's money connectors — guide for Vihan's Claude

Hi Claude! This explains the "money" connectors Rahul built for Parakh: what each one checks, when to call it, and how to turn its result into a verdict. Please read all of it before wiring them in. Code: GitHub repo `singularity713/parakh-rahul`, folders `connectors/` and `data/`.

## 1. Setup

- Copy **both** `connectors/` and `data/` into the project root as sibling folders. The RBI connectors find their files at `connectors/../data/`.
- The modules import each other by bare name (`from base import result`), so put `connectors/` on the path before importing:
  ```python
  import sys; sys.path.insert(0, "connectors")
  import sebi, rbi_nbfc, rbi_alert_list
  ```
- Install: `pip install requests beautifulsoup4 rapidfuzz pdfplumber openpyxl`
- The connectors make **no Claude calls**. They're plain Python and **never raise**: on any error they return `status: "unavailable"` with the reason in `note`.

## 2. The functions

| Call | What it checks | Live or file | Accepts |
|---|---|---|---|
| `sebi.search(q, kind="adviser")` | SEBI registered investment advisers | live sebi.gov.in | name, or reg. no. `INA` + 9 digits |
| `sebi.search(q, kind="analyst")` | SEBI registered research analysts | live | name, or `INH` + 9 digits |
| `sebi.search(q, kind="broker")` | SEBI registered stock brokers (equity segment) | live | name, or `INZ` + 9 digits |
| `rbi_nbfc.search(q)` | Companies **registered** with RBI as NBFCs/ARCs (loans, deposits, finance cos.) | file, list as on 2026-09-30 | name (current or former), or CIN |
| `rbi_nbfc.search_cancelled(q)` | Companies whose RBI registration was **cancelled** | file, as on 2026-09-30 | name only |
| `rbi_alert_list.search(q)` | RBI **Alert List**: forex/trading platforms RBI says are **not authorised** | file, list updated 2025-11-19 | name, or website/URL |

RBI blocks scripts, so the RBI lists were downloaded by hand on 2026-11-01 and are searched offline. SEBI is queried live and takes 1–5 s; a misspelt name can take up to ~15 s because the code retries word by word, with polite pauses.

## 3. What every call returns (same shape for all)

```json
{ "source": "SEBI investment adviser register",
  "query": "29k investmnt advisor",
  "status": "found | not_found | unavailable | needs_user",
  "matches": [{"name": "29K INVESTMENT ADVISERS PRIVATE LTD", "id": "INA200000365", "score": 91}],
  "source_url": "https://www.sebi.gov.in/...",
  "checked_at": "2026-11-01T14:54:10+05:30",
  "data_as_of": null,
  "note": "" }
```
- `matches` holds up to 3 results, best first. `score` runs 0–100 (fuzzy name match; 100 for an exact registration number, CIN or website).
- `data_as_of` is set for the RBI file-based lists (download date). `note` says which list version was used. Show it to the user.
- **"found" only means "some name looked similar". The `score` decides how sure we are.**

## 4. When to call which (routing)

Pull out each **firm/platform name, registration number and website** mentioned in the forward. Pass the name alone, not the whole message. Then:

- **Investment / portfolio advice, "SEBI registered adviser", paid advisory, guaranteed returns** → `sebi.search(name, "adviser")`
- **Stock tips, buy/sell calls, Telegram/WhatsApp tip groups, "research reports", "SEBI registered RA"** → `sebi.search(name, "analyst")`. Also try `"adviser"`: scammers mix up the two.
- **Trading/demat account, "open an account with us", broker names** → `sebi.search(name, "broker")`
- **Loans, loan apps, fixed deposits, "RBI registered NBFC", finance companies** → `rbi_nbfc.search(name)` **and** `rbi_nbfc.search_cancelled(name)`
- **Forex, currency/commodity trading platforms, binary options, "earn in dollars", prop-trading firms** → `rbi_alert_list.search(website_or_url)` if a link is present, **and** `rbi_alert_list.search(name)`
- **A registration number in the text:** `INA…` → adviser, `INH…` → analyst, `INZ…` → broker, a 21-character CIN like `U65990MH1994PLC080646` → `rbi_nbfc.search`
- If unsure which SEBI register applies, call more than one; each call is cheap.

**Not covered by these connectors:** banks, insurance (IRDAI), mutual funds (AMFI), crypto exchanges, UPI handles, and SEBI brokers registered only in non-equity segments. Don't report "not found" for something that was never checked.

## 5. Turning results into verdicts (rules from the team plan)

**Never call anyone a "fraud" or "scam".** Say what the official list shows, which list, and as of when.

### SEBI registers and `rbi_nbfc.search` (being FOUND is good)
| Result | Verdict | Wording example |
|---|---|---|
| top score **≥ 95** | **Matched** | "Found in the SEBI investment adviser register as 29K INVESTMENT ADVISERS PRIVATE LTD (INA200000365), checked 1 Nov 2026 14:54." |
| top score **70–94** | **Needs clarification** | "Not an exact match. Did you mean 29K INVESTMENT ADVISERS PRIVATE LTD (INA200000365)?" |
| `not_found` | **Not found in checked register** | "No firm with this name in the SEBI investment adviser register as of 1 Nov 2026 14:54." Add the next step: check the name on the official page (`source_url`). |
| `unavailable` | **Couldn't verify** | "Couldn't reach SEBI's website just now. Try again later." Never treat this as not-found. |

### `rbi_alert_list.search` (being FOUND is the WARNING)
| Result | Verdict | Wording example |
|---|---|---|
| top score **≥ 95** (a website match is always 100) | **Matched (warning)** | "This platform (Exness, exness.com) is on RBI's Alert List of entities not authorised for forex trading (list updated 19 Nov 2025)." |
| top score **70–94** | **Needs clarification** | "A similar name is on RBI's Alert List: Exness. Is this the same platform?" |
| `not_found` | Say **nothing reassuring** | RBI states the list "is not exhaustive", and absence does **not** mean authorised. At most: "Not on RBI's Alert List, but that list is not complete." |

### `rbi_nbfc.search_cancelled` (being FOUND is a warning, with care)
- The cancelled list has **names only (no CIN)**, and different companies can share similar names. Phrase a ≥95 match as: "RBI's list of cancelled NBFC registrations (as on 30 Sep 2026) includes a company named X."
- **If `rbi_nbfc.search` already gave a ≥95 match for the same query, ignore the "did you mean" results from `search_cancelled`.** Example: "Bajaj Finance" is registered (100), while the cancelled list suggests *Bajaj Finserv Limited* (77), a **different company**. Showing that would wrongly suggest Bajaj Finance lost its licence.

## 6. Known limits (say so honestly if they come up)

- **Legal names only.** Lists hold the registered company name, not app/brand names. "Groww" is not found under that name. When a brand isn't found, say "not found under this name" and suggest checking the company's legal name (usually printed at the bottom of its website or app).
- A query made only of generic words ("Finance Limited") can match a firm by accident. Only send real, distinctive names.
- SEBI returns at most 25 records per search, so very short or generic queries may miss the right firm.
- SEBI's site can be slow or change. Then the connector returns `unavailable`, which should become "Couldn't verify", not a guess.

## 7. Quick test (run from the project root)

```bash
cd connectors
python sebi.py "29K Investment Advisers"        # found, INA200000365, 100
python sebi.py broker "zerodah broking"          # found, ZERODHA BROKING LIMITED, 93
python rbi_nbfc.py "bajaj finanse"               # found, Bajaj Finance Limited, 92
python rbi_alert_list.py "https://www.exness.com/in"   # found on Alert List (warning), 100
python rbi_alert_list.py "Zerodha"               # not_found
```

Questions → Rahul (GitHub `singularity713`).
