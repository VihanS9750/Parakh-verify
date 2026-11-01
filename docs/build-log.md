# Build log

How Parakh was built during the Forge buildathon (31 Oct to 1 Nov 2026), taken from the git history and our notes. Times are IST.

## Timeline

| When | Who | What | Commit |
|---|---|---|---|
| 31 Oct | Vihan | Scored the listed problem statements against the rubric and picked **T1.4 (fact-verification)**. Reasons: live official data exists, the demo can be tried by any judge, and the problem is large. See [research/Forge buildathon problem statement ranking.md](research/Forge%20buildathon%20problem%20statement%20ranking.md). | |
| 31 Oct 07:50 | Vihan | Project brief, rules and setup files | `180db67` |
| 31 Oct 07:56 | Vihan | Market analysis; first source-access tests | `3a36a4d` |
| 31 Oct 08:18 | Vihan | Hero feature (one forward, many checks), rule-based verdicts, evidence fields | `db3564a` |
| 31 Oct 15:54 | Rahul | Connector base, name matcher, SEBI page parser (separate repo) | `18ba9f4` |
| 31 Oct 16:49 | Rahul | Live SEBI investment adviser search | `ba57585` |
| 1 Nov 06:31 | Vihan | Agent pipeline, verdict rules, SQLite store, live UGC/IRDAI/AMFI connectors, ID checks, Streamlit app, evaluation | `641f655` |
| 1 Nov 06:32–06:37 | Vihan | Brief updated to match the build; CBIC DIN, SEBI @valid UPI handles; government-named messages linking to other domains | `5ed13d4`, `08f98da`, `ceba917` |
| 1 Nov 15:11 | Vihan | Merged Rahul's repo, keeping both histories | `3910636` |
| 1 Nov 15:14 | Vihan | Removed the Claude API and connected Rahul's SEBI search to the agent | `ca5b021`, `2e73f43` |

## Decisions and why

**Rules decide verdicts, not a model.** From the start, every verdict comes from fixed rules in `verdict.py` that can be read line by line. A judge can ask "why High risk?" and we point to the rule.

**We dropped the Claude API on 1 Nov.**
- The first design used Claude to read screenshots, pick checks and write explanations in four languages. Rules ran as the fallback.
- The organisers confirmed that pretrained models are not allowed, so we removed the Claude code. The rules path, which already worked on its own, became the whole pipeline.
- What we lost: reading screenshots, Tamil and Marathi explanations, and AI-spotted warning signs.
- Options for our own model are in [research/own-model-plan.md](research/own-model-plan.md); the team is deciding.

**We never get around a block.**
- RBI returns HTTP 418 to scripts even from an Indian connection, and MCA returns 403. GST, eCourts and Income Tax need a captcha, OTP or login.
- We don't fake a browser, solve captchas or automate logins. Those sources get a format check plus a link to the official page, and RBI lists are to be downloaded by hand with their download date shown.
- Our user agent names the project, and we send at most one request per second per site.

**Fixes found by testing against live data:**

| Problem found | Fix |
|---|---|
| "Sunrise Life Assurance" (not real) scored 86% against a real insurer | A match must now score 90+ to count as found. "Matches the official record" needs 95+ with no close rival. |
| "Star Health" was missed because word-order matching fails on short names | Switched to `rapidfuzz.WRatio` |
| AMFI's search matches exact substrings, so "Sunil Kamdar" missed "Sunil A Kamdar" | Retry on the longest and first words, then rank the results ourselves |
| An email address was read as a UPI ID | Tightened the UPI pattern |
| Short links (bit.ly) were not detected | Wider link pattern; shorteners count as a warning |
| IRDAI's table address column was read as the registration number | Pick the column by its header |
| Rahul's SEBI search counted a 70% name match as found | Our adapter applies the same 90+ bar as the other lists |

**What we chose not to claim.**
- The test set is 23 messages. We report counts with 95% ranges, not an accuracy percentage.
- The warning-sign rules were written from the same advisories as the test messages, so we expect lower numbers on new messages.

## How we worked

- The code was written with AI coding assistants (Claude Code), as the rules allow. Each owner reviews their files and can explain them; see the team table in the [README](../README.md).
- Everything is in git with small commits. Rahul's history (31 Oct) is merged in, not copied, so his commits keep their original times.
- Research notes and sources are in [docs/research/](research/).
