# Build log

How Parakh was built during the Forge buildathon (31 Oct to 1 Nov 2026), from the git history. Times are IST.

## Timeline

| When | What |
|---|---|
| 31 Oct | Scored the listed problem statements against the rubric and chose **T1.4: fact-verification** (live official data exists, any judge can try it, the problem is large). Market and competitor research, project brief. Rahul built the SEBI adviser search in a separate repo. |
| 1 Nov, morning | Pipeline, verdict rules, SQLite store, live UGC / IRDAI / AMFI connectors, ID and link checks, Streamlit app, first evaluation. |
| 1 Nov, midday | Merged Rahul's SEBI and RBI connectors, keeping both histories. The first design used an AI model; we removed it after being told pretrained models were not allowed. |
| 1 Nov, afternoon | The organisers' answer was corrected: pretrained models **are** allowed. We added the AI investigator back on Gemini's free tier only (no paid API, and a second provider we first tried was dropped later for that reason), with the rules as the fallback and the safety net. Screenshot reading with offline OCR. |
| 1 Nov, evening | SEBI registers (advisers, analysts, brokers) and enforcement orders, RBI Alert List for links, link evidence (short-link destination, website age), audit fixes, 25-bank impersonation check, UPI QR check, wider masking of personal data, honest wording and evidence labels, a prompt-injection test, Rahul's frontend, and 8 fresh forwards from family WhatsApp groups. |

## Decisions and why

**Rules decide verdicts; the AI investigates and explains.** Every verdict comes from fixed rules in `verdict.py` that can be read line by line. The AI picks checks, re-plans when a search fails, and writes the explanation from the verdicts. Warning signs the AI spots must quote words that are really in the message, and they can never be the sign that tips a message into High risk.

**Only masked text leaves the laptop, and never an image.** An image can't be masked, so screenshots are read on the laptop (Tesseract) and that text is masked like typed text.

**We never get around a block.** RBI returns HTTP 418 to scripts and MCA returns 403; GST, eCourts and Income Tax need a captcha, OTP or login. We don't fake a browser, solve captchas or automate logins. Those sources get a format check plus a link, and the RBI lists were downloaded by hand with their dates shown. Our user agent names the project, and we send at most one request per second per site.

**We only claim what a check shows.** A register match says a firm exists, not who sent the message. A bank link that is not on the bank's domains "doesn't match the bank"; it is not a statement by the bank. A QR code's payee name is typed by whoever made the QR, so we never call a recipient verified. The top verdict reads "No adverse finding in the checks performed", not "genuine".

**Problems found by testing, and fixed:**

| Problem found | Fix |
|---|---|
| No `https://` link was ever detected (a hidden backspace character in a regex) | Fixed, with a regression test |
| A claimed number matched a longer real number by substring | Exact match only |
| "Not found" in an unrelated register overrode a real match | A match in the register that fits now wins; a warning list still wins over a match |
| A short link alone was marked invalid | New neutral verdict: check where it leads |
| "Never share your OTP" counted as an OTP request, and one AI sign tipped a genuine bank message to High risk | Advice is set aside; wording alone needs two signs found by the fixed rules |
| SEBI orders were hidden by "not found" in the evidence count | Orders now rank higher and every check is counted |
| The first fresh test caught only 1 of 4 unseen scams | Four wording rules widened (see [fresh-forwards-note.md](fresh-forwards-note.md)) |
| Punjab & Sind Bank's old site redirected to an unrelated betting site | Not listed; five banks we couldn't confirm are left out rather than guessed |

## What we chose not to claim

- The test set is 31 messages. We report counts with 95% ranges, not an accuracy percentage.
- The wording rules were first written from the same advisories as most test messages, so we expect lower numbers on new messages. The fresh messages showed exactly that, and we record the untuned result.

## How we worked

- The code was written with AI coding assistants (Claude Code), as the rules allow. Every owner reviews their files and can explain them.
- Everything is in git with small commits and pull requests. Rahul's history is merged in, not copied.
- Research notes and sources are in [research/](research/).
