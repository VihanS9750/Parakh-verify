# Parakh without Claude: what we can build ourselves

Written 1 Nov 2026, 14:10 IST, with about 10 hours left. Nothing here is decided; the team picks.

**Constraints:** no paid API; no pretrained model (the organisers confirmed this); laptop with 8 CPU cores, 16 GB RAM and no GPU; cost ₹0.

**What already works without Claude:** rules-only mode, which covers ID and link checks, UGC, IRDAI and AMFI lookups, warning-sign rules, verdicts and the app. Removing Claude is deleting code, not rebuilding.

## Pipeline after the change

Screenshot, PDF or text, then:

1. Get the text out (OCR, or paste).
2. Find items such as names, IDs and links (regex, built).
3. A planner picks the checks (rules, built).
4. Official registers (built), plus a new **official-document index**.
5. **Our own trained scam-language model** adds a score.
6. Rules decide the verdict (built).
7. A template explanation in en, hi, ta or mr.

## 1. Getting text out of screenshots

| Option | Tools | Time | Notes |
|---|---|---|---|
| A. Tesseract OCR | pytesseract, the Tesseract Windows installer, hin/tam/mar language packs | ~1 hr | Free and offline; reads clean WhatsApp screenshots well. **Tesseract ships its own trained model, so ask the organisers whether it counts as pretrained.** |
| B. Our own OCR from scratch | A CRNN model, synthetic training text, a GPU | not feasible tonight | |
| C. No OCR | Paste text; PDFs with a text layer (pdfplumber, built) | 0 | Screenshots aren't supported, and the app says so. |

Image clean-up before OCR (greyscale, contrast, threshold) uses Pillow, which is classical processing with no model.

## 2. Our own trained model: scam-language classifier

**What it is:**
- Word and character counts (TF-IDF over words, plus 3–5 letter chunks so misspellings and Hinglish still match) feed into logistic regression.
- It is trained from scratch on the laptop in seconds with scikit-learn. Every weight is learned from our training data only, so nothing is pretrained.

**What it shows:**
- A score, for example "Scam-like wording: 0.87", and the words that pushed the score up (the model's own weights). It appears as one more warning sign.
- The verdict still comes from the registers and the rules.

**Training data (public, free):**
- [Mendeley SMS Phishing Dataset](https://data.mendeley.com/datasets/f45bkkt8pr) (Mishra & Soni, Jaypee Noida, 2022): 5,971 SMS (4,844 genuine, 638 smishing, 489 spam). About 4,750 of them overlap with the older UCI SMS Spam Collection (UK/Singapore, ~2011). Check the licence on the page.
- UCI SMS Spam Collection: 5,574 SMS, 747 spam.
- [Smishtank dataset](https://arxiv.org/html/2402.18430v2): phishing SMS reported by the public, mostly US.
- [Hindi spam SMS, IEEE DataPort](https://ieee-dataport.org/documents/spam-sms-hindi-language): 3,894 messages, but the files appear not to be uploaded, so don't count on it.
- Ours: 35 real Indian scam messages (research notes) and 23 test forwards. **These stay as the test set and are never trained on.**

**Main risk:** no public labelled set of Indian WhatsApp investment, KYC or "digital arrest" scams exists that we found. The public sets are old English SMS spam ("You have won a prize"), so the model may miss Indian investment tips. We measure it on our 23 Indian forwards. If it doesn't beat the existing warning-sign rules, we show that honestly and don't sell it as a feature.

**Cost and time:** 2–3 hrs. Install scikit-learn (free).

## 3. Official-document index (the "store government documents every 6 hours" idea)

**Sources, all tested from this laptop at 14:06 today with our honest user agent:**

| Source | Result | What's inside |
|---|---|---|
| SEBI RSS feed (sebi.gov.in/sebirss.xml) | 200 | Orders, circulars, press releases; today's includes an order against an investment adviser |
| RBI press-release RSS (rbi.org.in/pressreleases_rss.xml) | 200 | Full text of each release. RBI's web pages block scripts; this public feed doesn't. |
| PIB press-release RSS | 200 | Government press releases, Hindi and English |
| UGC and IRDAI websites | 200 | Notices, warnings |
| Existing registers | built | UGC fake list, IRDAI, AMFI |

**Where it's stored:**
- SQLite (store.py already exists), with FTS5 full-text search. FTS5 is built into Python's sqlite3, checked working with SQLite 3.49.1 on the laptop, and ranks results by BM25.
- There's no vector database and no embedding model, because embeddings need a pretrained model.

**Refresh every 6 hours:**
- Simplest way: when a check runs and the newest copy is older than 6 hours, refresh first. `store.cached_list` already does this; the limit changes from 24 hours to 6.
- Windows Task Scheduler can also run it in the background.

**How a forward gets matched:**
1. **Names in the forward are searched in orders and warnings.** A match shows "SEBI order dated 30 Oct 2026 names X" with a link. This is the strongest use.
2. **"As per new RBI rule/circular …"** is searched for an official publication on that topic. If one is found, the link is shown. If not, the result is "No matching official publication found", never "fake".
3. **Personal notices** (tax, police, court, CBI) are never published, so the index can't match them. The ID-format checks (built) cover those.

**Honest naming:** this is retrieval, not RAG, because nothing generates text; the explanations are our templates. Call it the "official-document index" when talking to judges.

**General web search** needs a search API (paid or rate-limited), or scraping Google or Bing, which breaks their terms. Skip it; the index searches the official sites instead.

**Limits:** feeds hold only recent items, so going further back means politely reading listing pages (a few hundred documents). Indexing "all government documents" isn't possible tonight; these five sources are.

**Cost and time:** 3–4 hrs, disk under 100 MB.

## 4. Deepfake / edited images

| Option | Tools and data | Time | Verdict |
|---|---|---|---|
| D1. Train a deepfake face or video detector | [FaceForensics++](https://github.com/ondyari/FaceForensics) needs Google-form approval (days); DFDC is ~470 GB; no GPU | n/a | Not feasible tonight |
| D2. Train a small "AI-generated image" model from scratch | [CIFAKE](https://gts.ai/dataset-download/cifake-real-and-ai-generated-synthetic-images/): 120,000 tiny 32×32 images (real CIFAR-10 photos vs Stable Diffusion 1.4 fakes), MIT licence, Kaggle; PyTorch on CPU | 2–3 hrs, ~1 hr of that training | Paper reports ~93% on its own test set, but likely unreliable on real WhatsApp images (other generators, compression, shrinking to 32×32). A judge's photo may get a wrong answer on stage. |
| D3. Classical image forensics, no model | Pillow: metadata (editing-software tags) and Error Level Analysis (shows areas re-saved differently); OpenCV: copy-pasted regions | ~2 hrs | Hints only: WhatsApp strips metadata and recompresses images, which hides most signs. |

## 5. The "agent" without an LLM

- **Already built:** `investigate_with_rules` picks checks based on what's in the message, runs them, and retries names.
- **The change:** make it an explicit loop of plan, check, read the result, re-plan:
  - If a name isn't found, try a shorter name.
  - If a SEBI number is found, look up that register.
  - If an entity is found in an order, flag it.
- Each step already shows live in the app.
- **Risk:** the "AI reasoning / agentic" criterion is 25 points, and judges may expect an LLM. Our answer is that we trained our own model, built a document index and a planner, and every decision can be traced.
- **Removing Claude means:**
  - Delete the AI branch in agent.py and the AI status in the sidebar.
  - Drop anthropic from requirements.txt.
  - Write Tamil and Marathi explanation templates by hand.
  - About 1 hr.

## Priority for the ~10 hours left (team decides)

| # | Work | Time | Value |
|---|---|---|---|
| 1 | Remove the Claude path | 1 hr | Required by the no-pretrained-model rule |
| 2 | Official-document index | 3–4 hrs | Highest; live data; Vihan's idea |
| 3 | Scam-language model | 2–3 hrs | "We trained our own model" story; real risk it's weak on Indian forwards |
| 4 | Tesseract OCR | 1 hr | Only if the organisers allow it |
| 5 | Image hints (D3) | 2 hrs | Only if time is left |

Rahul's SEBI and RBI merge runs alongside all of these. Everything costs ₹0; the only cost is time.

## Decisions needed

1. Ask the organisers: is Tesseract OCR allowed (it contains a trained model)? Is a model we train ourselves with scikit-learn fine?
2. Which of items 2–5 to build.
3. Deepfake: D2, D3, or skip.
