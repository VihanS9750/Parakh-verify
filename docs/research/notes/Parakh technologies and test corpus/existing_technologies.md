# Existing technologies and technical approaches behind AI scam, fraud-message and claim verification (for "Parakh")

Research date: 1 Nov 2026. Scope: what others have built and how, so Parakh can reuse proven patterns and explain what is new. "Cited Findings" are documented facts from the linked sources (vendor claims are marked as such). "Inferences" are mine. Where a fetch failed or only a search-result summary was available, that is stated.

Method note: GitHub star/licence numbers were pulled live from the GitHub API on 1 Nov 2026; Hugging Face dataset metadata from the HF API the same day. The two local experiments (rapidfuzz/cleanco behaviour, Wilson intervals) were run by me on 1 Nov 2026 and are listed under Inferences, not Cited Findings.

---

## 1. Architectures for LLM-based claim / fact verification (extract -> retrieve -> verdict), "LLM extracts, rules decide", abstention, hallucination control

### Takeaway
The dominant research pattern is decompose -> retrieve evidence with tools -> judge each atomic claim, and every serious system has an explicit "not enough evidence / unverifiable" outcome. "LLM extracts, deterministic code decides" is established (Logic-LM, ProgramFC) and already used in a few small India scam-checker repos, so the mechanism itself is prior art; what differs is the evidence source.

### Cited Findings

**Decompose-then-verify pipelines**
- FActScore (EMNLP 2023) breaks a generation into atomic facts and scores the % supported by a reliable knowledge source; ChatGPT scored only 58% on biographies; the automated retrieval+LLM estimator has under 2% error vs human scoring; `pip install factscore` — [ACL Anthology EMNLP 2023](https://preview.aclanthology.org/setup/2023.emnlp-main.741), [Meta AI](https://ai.meta.com/research/publications/factscore-fine-grained-atomic-evaluation-of-factual-precision-in-long-form-text-generation). Repo shmsw25/FActScore: MIT, 461 stars — [GitHub](https://github.com/shmsw25/FActScore).
- SAFE / LongFact (Google DeepMind, NeurIPS 2024): an LLM splits a response into individual facts, issues Google Search queries per fact, and rates each as supported or not. Agreed with crowdsourced human labels on ~72% of ~16k facts; on a 100-item sample of disagreements SAFE was right 76% of the time; >20x cheaper than human annotators. Released implementation used gpt-3.5-turbo-0125 plus Serper — [NeurIPS page](https://nips.cc/virtual/2024/poster/96675), [arXiv 2403.18802](https://www.arxiv-vanity.com/papers/2403.18802). Repo google-deepmind/long-form-factuality: 700 stars, GitHub reports licence as NOASSERTION — [GitHub](https://github.com/google-deepmind/long-form-factuality).
- FacTool (2023): five modules — claim extraction, query generation, tool querying, evidence collection, agreement verification. Claim extraction is done by prompting an LLM, not a trained extractor. Tools include Google Search, Google Scholar, code interpreter, Python — [arXiv 2307.13528](https://arxiv.org/pdf/2307.13528). Repo GAIR-NLP/factool: Apache-2.0, 935 stars, last push Aug 2024 — [GitHub](https://github.com/GAIR-NLP/factool). A later paper argues sentence-level decomposition/decontextualisation in such pipelines hurts downstream verification — [FaStfact arXiv 2510.12839](https://arxiv.org/html/2510.12839v2).
- Loki / OpenFactVerification (COLING 2025 demo): decomposer -> check-worthiness filter (drops vague/opinion claims) -> query generator -> evidence retrieval (Serper/Google) -> per-snippet verdict (supports / refutes / irrelevant); modular, human-in-the-loop by design; converts non-text inputs (speech, image, video) to text first — [arXiv 2410.01794](https://arxiv.org/pdf/2410.01794).
- Claimify (Microsoft Research, ACL 2025): four stages — sentence splitting, selection (non-verifiable / partly / fully verifiable), disambiguation (sentences with unresolved ambiguity are excluded), decomposition into standalone claims — [ACL 2025 paper](https://preview.aclanthology.org/landing_page/2025.acl-long.348.pdf). (The 99% entailment / 93.5% F1 figures came from secondary summaries and should be checked against the PDF before quoting — [summary](https://themoonlight.io/review/towards-effective-extraction-and-evaluation-of-factual-claims).)
- FEVER (2018): 185,445 claims written by altering Wikipedia sentences; labels Supported / Refuted / NotEnoughInfo; annotator agreement Fleiss kappa 0.6841; evidence sentences recorded for Supported/Refuted — [arXiv 1803.05355](https://arxiv.org/abs/1803.05355).
- AVeriTeC (FEVER 2024 shared task): real-world claims with four labels, including "Not Enough Evidence" and "Conflicting Evidence/Cherry-picking"; a prediction counts as correct only if both the label and the evidence are adequate; 21 submissions, winner TUDA_MAI at 63% — [arXiv 2410.23850](https://arxiv.org/pdf/2410.23850).

**"LLM translates/extracts, deterministic component decides"**
- Logic-LM (Findings of EMNLP 2023): LLM rewrites the problem in formal notation, a deterministic symbolic solver does the inference, solver error messages feed back to repair the formalisation; paper reports +39.2% over standard prompting and +18.4% over chain-of-thought (v2; v1 reported larger gains) — [arXiv 2305.12295](https://arxiv.org/pdf/2305.12295). Repo MIT, 413 stars — [GitHub](https://github.com/teacherpeterpan/Logic-LLM).
- ProgramFC (ACL 2023): LLM writes a reasoning program from a claim; an interpreter executes it step by step calling specialised functions; majority vote over several programs; outputs are explainable and debuggable — [arXiv 2305.12744](https://arxiv.org/abs/2305.12744v1). Repo mbzuai-nlp/ProgramFC: MIT, 59 stars — [GitHub](https://github.com/mbzuai-nlp/ProgramFC).
- In small India scam-checker repos: ScamSach runs ~25 offline bilingual rules, lets the LLM choose network checks from a tool menu with code guardrails, scores with rule weights, and "hard evidence" (threat-intel listing, APK link) forces a scam verdict. The LLM judge can raise risk but can lower it by only one step and only at high confidence, and cannot override hard evidence — [ScamSach README](https://github.com/apurvaraj9/scamsach). Nivesh Kavach ("hybrid, deterministic rules + Gemini"): rules engine with 16 red-flag categories scores first, Gemini only explains under a JSON schema, scoring is deterministic, and it falls back to rules-only when the API errors — [Nivesh Kavach README](https://github.com/Kushith1/nivesh-kavach).

**Abstention / "cannot verify"**
- Survey "Know Your Limits: Abstention in LLMs" (TACL 2025) organises methods by query, model and human values, and by when the abstention decision is made — [arXiv 2407.18418](https://arxiv.org/html/2407.18418v3).
- Abdaljalil et al. (Feb 2026) decompose scientific claims into minimal conditions, audit each against evidence with NLI, then support / refute / abstain; confidence-based abstention "substantially reduces risk at moderate coverage" (SciFact, PubMedQA). They note most evaluations assume a definitive answer is always required — [arXiv 2602.14189](https://www.arxiv.org/pdf/2602.14189).
- Selective classification: coverage = share of inputs answered; selective risk = error rate on the answered ones; the risk-coverage curve plots the trade-off (El-Yaniv & Wiener 2010; Geifman & El-Yaniv 2017) — [NeurIPS 2017 paper](https://arxiv.org/pdf/1705.08500v1). Traub et al. (2024) criticise AURC and propose AUGRC, "the average risk of undetected failures" — [arXiv 2407.01032](https://arxiv.org/html/2407.01032v2).
- Scam-checker products with an explicit abstain state: ScamShield Singapore returns "Be careful, we're not sure about this one" (sender "likely not yet reviewed") alongside "looks like a scam", "looks safe" (sender registered with IMDA) and "looks like spam" — [ScamShield guide](https://guide.scamshield.gov.sg/using-scamshield/check-for-scams/how-to-check-a-scam-message). Chetana returns safe / risky / unclear, and "weak evidence results in unclear rather than a guessed score" — [Chetana README](https://github.com/MirrorDNA-Reflection-Protocol/chetana-site). Google's Circle to Search scam check only shows a result "when our systems have high confidence in the quality of the response" — [Google blog, 2 Dec 2025](https://blog.google/products/search/scam-detection-circle-to-search-lens/).

**Hallucination controls**
- Anthropic's documented guardrails: give the model explicit permission to say "I don't know"; extract word-for-word quotes first and base analysis only on them; verify each claim by finding a supporting quote and retract if none; best-of-N consistency checks; restrict to provided documents; the page warns these "don't eliminate" hallucinations — [Anthropic docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations).
- Chain-of-Verification (Meta/ETH, ACL Findings 2024): draft -> plan verification questions -> answer them independently of the draft -> revise; independence prevents repeating the draft's hallucinations — [CoVe summary](https://www.deepai.org/publication/chain-of-verification-reduces-hallucination-in-large-language-models).
- scams-sahi-nahi-hai (Build for India 2026 entry) forces the model to quote each suspicious phrase verbatim so the UI can underline it in place; URL checks are shown separately as lookups — [README](https://github.com/josephkappala/scams-sahi-nahi-hai).
- Nivesh Kavach regex-redacts phone numbers, Aadhaar, PAN, UPI IDs, emails, account numbers and OTPs before anything is sent to Gemini, and runs a guardrail filter on model output — [README](https://github.com/Kushith1/nivesh-kavach). ScamSach masks personal identifiers before any LLM, trace or database write — [README](https://github.com/apurvaraj9/scamsach).

### Inferences
- Parakh's pipeline (LLM extracts entities/claims -> registry tools -> code verdict) maps cleanly onto FacTool/Loki stages 1-4, with the verdict stage replaced by code; the research precedent for replacing the LLM judge with a deterministic one is Logic-LM / ProgramFC, so "plain code decides" should be presented as an application of an established pattern, not as an invention.
- AVeriTeC's rule (label counts only if evidence is also adequate) is the closest published analogue to Parakh's "dated source per item"; it gives a citable justification for not accepting a verdict without its source.
- Claimify's "exclude sentences with unresolved ambiguity" is a precedent for Parakh to drop or flag an entity it cannot resolve to a registry record, rather than guessing.
- Requiring verbatim quotes from the forwarded message (Anthropic guidance, scams-sahi-nahi-hai) gives a cheap structural check that code can run: every extracted entity string must appear in the OCR/text of the input, otherwise it is discarded.

### Gaps
- I found no published ablation comparing "LLM judge" vs "rule verdict" on scam-message verification specifically.
- FActScore/SAFE evaluate free-form generations against Wikipedia/Web; I found no paper applying decompose-and-verify to regulator-registry claims (adviser registration numbers, app lists).

---

## 2. How existing scam checkers work technically (documented facts only)

### Takeaway
Consumer checkers mostly document inputs and UX but not model internals. Signals documented are: reputation databases and community reports (Truecaller, ScamShield), LLM judgement of wording/context (Norton, Bitdefender, Google), and, in Singapore, one official registry (IMDA sender IDs). Among registry lookups specific to Indian finance, SEBI itself now offers "SEBI Check" for payment credentials, but I found no consumer checker that verifies adviser/app/scheme/institution claims across several regulators.

### Cited Findings

**Truecaller Scam Checker (launched India, 27-28 Sep 2026)**
- Free, no app or sign-in; accepts a phone number, a link, or a message; for messages it "picks out a phone number or link" and shows related community reports from ScamFeed; links are expanded through shorteners/redirects and the final destination is checked against a "proprietary risk database and other fraud signals". ~20,000 scam reports live on ScamFeed in India with ~1,300 new per week; no AI model named; no accuracy/false-positive figures; screenshot upload is planned, not live — [TechCrunch, 27 Sep 2026](https://techcrunch.com/2026/09/27/truecaller-takes-its-scam-intelligence-to-the-open-web-as-it-looks-beyond-caller-id/). TechRepublic dates the launch 28 Sep 2026 — [TechRepublic](https://www.techrepublic.com/article/news-truecaller-scam-checker-apac-india/).
- Separate product: Truecaller AI Call Scanner (2024) is a model distinguishing human from synthetic voices, reportedly English-only at launch — [MediaNama](https://www.medianama.com/2024/05/223-truecaller-ai-voice-scanner-spam-call/) (from search summary; page not fetched).

**Norton Genie / Gen Digital**
- March 2026: users tag Norton inside ChatGPT and paste emails, texts, images or URLs; output safe / risky / likely scam plus next steps; Norton says it analyses language and intent alongside URL/domain checks and was trained on millions of scam messages — [SecurityBrief](https://securitybrief.co.uk/story/norton-unveils-genie-scam-detection-assistant-in-chatgpt). Feb 2025 Scam Protection covers texts, calls, email, web, with AI analysing "the meaning of words, not just links" — [Help Net Security](https://www.helpnetsecurity.com/2025/02/20/norton-scam-protection/). Submitted content is uploaded to the AI engine — [TechFinitive](https://www.techfinitive.com/product-guides/how-does-norton-genie-work/). No architecture or accuracy figures published in the sources I reached.

**Bitdefender Scamio (Dec 2023)**
- Free chatbot via web, WhatsApp, Messenger, Discord; accepts emails, texts, images, links, QR codes; user also describes how the item arrived; "powered by Bitdefender threat protection" plus an LLM chatbot and NLP/"context decoding"; returns a verdict "in seconds" with recommended actions and, per the company, a "reliable probability of malicious activity". Where analysis runs is not stated in the launch coverage — [Help Net Security, 14 Dec 2023](https://www.helpnetsecurity.com/?p=286755). A search summary says most processing happens on Bitdefender servers — [Bitdefender support](https://bitdefender.com/consumer/support/answer/97320). Vendor claims only; no independent accuracy tests found.

**Google**
- Messages Scam Detection (4 Mar 2025): on-device AI looks for suspicious conversation patterns in SMS/MMS/RCS from non-contacts; "all message processing remaining on-device"; on by default under Spam Protection; launched English-only in US/UK/Canada — [Google blog](https://blog.google/security/new-ai-powered-scam-detection-features/). Call scam detection: Gemini Nano on Pixel 9, smaller on-device models on Pixel 6+, no audio stored or sent — same post.
- India (Nov 2025): real-call scam detection with on-device Gemini Nano, off by default, unknown numbers only; initially Pixel 9+; TechCrunch later corrected its story to say Hindi and English both work — [TechCrunch 20 Nov 2025](https://techcrunch.com/2025/11/20/google-steps-up-ai-scam-protection-in-india-but-gaps-remain); Google's own figures (500M+ suspicious messages/month stopped; 2.5B link warnings) are company claims — [Storyboard18](https://www.storyboard18.com/digital/google-rolls-out-on-device-scam-detection-in-india-as-digital-fraud-losses-top-%e2%82%b970-billion-84553.htm).
- Oct 2026 announcement (per secondary coverage, rolling out "in coming weeks"): opt-in cloud tier "Scam Detection enhanced with Private AI Compute" to analyse slow-burn conversations with stronger Gemini models, plus on-device Gemini Nano to evaluate unfamiliar links — [Droid Life, 14 Oct 2026](https://www.droid-life.com/2026/10/14/google-messages-is-getting-a-massive-gemini-powered-scam-defense-upgrade/). India availability is not mentioned there.
- Circle to Search / Lens (2 Dec 2025): user circles or screenshots a suspicious message; "AI and information from the web" assess whether it is likely a scam; global; manual, not automatic — [Google blog](https://blog.google/products/search/scam-detection-circle-to-search-lens/).
- Google DeepMind + GovTech Singapore (14 Oct 2026): lightweight Gemma fine-tuned on anonymised Singapore scam reports; two stages (small classifier screens, fine-tuned Gemma reviews more of the conversation on suspicion); on-device; accuracy and false-positive rates not disclosed; no release date — [CRN Asia](https://www.crnasia.com/news/2026/cybersecurity/google-and-singapore-partner-on-ai-scam-detection-and-cyber).
- Google Pay India research: LLM-based UPI scam classification; Gemini Ultra reached 93.33% classification accuracy and 89% reasoning accuracy, and surfaced 32% new accurate reasons human reviewers had missed (curated transaction data, size not stated) — [arXiv 2410.19845](https://arxiv.org/abs/2410.19845).

**Singapore ScamShield**
- App blocks calls from a central NCPC/SPF-managed blocklist; "scam check" accepts pasted text (plus sender number/ID) or screenshot and uses "AI/ML classification"; guidance factors named: similarity to known scam types, report volume, police assessment of sender, latest-report timestamp, and IMDA sender registration; user reports (with screenshots) feed the blocklist — [how it works](https://guide.scamshield.gov.sg/resources/help-center/about-scamshield/how-does-the-scamshield-app-work), [check a message](https://guide.scamshield.gov.sg/using-scamshield/check-for-scams/how-to-check-a-scam-message). Model internals not published; a GovInsider piece cites "95% accuracy" without methodology — [GovInsider](https://govinsider.asia/smart-gov/meet-singapores-latest-weapon-against-scams-open-government-products-scamshield/) (search summary; not verified).

**Microsoft**
- Edge Scareware Blocker (announced Nov 2024, preview Jan 2025): on-device ML model recognises scareware pages locally "without saving or sending images to the cloud"; users can report false positives — [Windows Blogs](https://blogs.windows.com/msedgedev/2025/01/27/stand-up-to-scareware-with-scareware-blocker/), [Microsoft Support](https://support.microsoft.com/en-us/edge/prevent-online-scams-with-the-scareware-blocker-in-microsoft-edge). I did not find a documented Microsoft "is this a scam" assistant for forwarded messages (see Gaps).

**India telecom and official registries**
- Airtel network-level AI (Sept 2024): two filters (network and IT layer); signals are sender/caller behaviour (activity patterns, contact frequency, call duration) compared with known spam patterns; SMS links checked against a central blocklist; CEO claims ~97% of spam calls and 99.5% of spam SMS caught (company figures) — [Bharti press release](https://www.bharti.com/press-release-2023-2024-airtel-cracks-down-on-spam-launches-indias-first-ai-powered-network-solution-for-spam-detection.html), [TelecomTV](https://telecomtv.com/content/digital-platforms-services/airtel-launches-india-s-first-ai-powered-network-solution-for-spam-detection-51375).
- SEBI Check (launched 1 Oct 2025 with "@valid" UPI handles): SEBI's tool to verify payment credentials of registered intermediaries. SEBI's investor page takes a UPI ID + captcha and returns "UPI ID Verified" with Name, Legal A/c Holder, Reg. No., or "No Match Found" ("did not match any verified records") — [SEBI UPI verification](https://investor.sebi.gov.in/upi-verification.html); the portal also has a "Check account details" (NEFT/RTGS) option — [SEBI portal](https://siportal.sebi.gov.in/intermediary/sebi-check). Sources conflict on whether QR codes are supported: Taxmann mentions only bank account details and UPI IDs — [Taxmann](https://www.taxmann.com/post/blog/sebi-introduces-validated-upi-ids-and-sebi-check-tool); a search summary of SEBI material mentions QR codes too — [SEBI QR page](https://investor.sebi.gov.in/qr-verification.html). The page shows no "as of" date stamp in the captured text.
- RBI digital-lending-app directory: regulated entities had to report DLAs on the CIMS portal from 13 May 2025; RBI said the list would appear under Citizen's Corner on or before 1 Jul 2025 "for the limited purpose of aiding the customers in verifying the claim of a DLA's association with a RE", built on regulated entities' submissions "without any further validation" by RBI — [RBI press release](https://rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=60403), [MediaNama](https://www.medianama.com/2025/05/223-rbi-digital-lending-apps-centralised-directory/). Whether the live directory matches this plan was not verified.

### Inferences
- Nobody in the set above documents LLM + deterministic registry lookup on the entities inside a forwarded message. Closest are ScamShield (IMDA sender registry + report database) and SEBI Check (payment credentials only).
- Truecaller's and ScamShield's strength is crowd/blocklist data about numbers and links; that is a data asset Parakh cannot replicate in 48 hours, so Parakh's lookups should lean on regulators' public records (authoritative, dated) rather than reputation.
- Because RBI says its DLA list is unvalidated and SEBI's page shows no date stamp, Parakh should record its own fetch date for every evidence item.
- Vendor privacy architecture divides into on-device (Google Messages, Edge, Gemma/Singapore) and cloud (Scamio, Genie, Truecaller link expansion); a forward-a-screenshot web app like Parakh is inherently the cloud model, so PII redaction before the LLM (as Nivesh Kavach does) is a relevant design point.

### Gaps
- No documentation found on Truecaller Scam Checker's models or whether message scoring is on-device/cloud (TechCrunch: "not mentioned").
- Microsoft Copilot "is this a scam" and a Microsoft "Scam Protection" feature: not found; this does not show they do not exist.
- Google's primary Oct 2026 Messages announcement was not reached; only secondary coverage.
- No independently measured accuracy for Truecaller, Norton, Scamio, ScamShield or Airtel was found.

---

## 3. Open-source projects and datasets (scam/phishing SMS and WhatsApp; India-focused)

### Takeaway
There are many India-focused scam-checker repos, almost all created in 2026 as hackathon or student projects, with 0-3 stars each; most are LLM-plus-rules paste-a-message tools. I found none that looks up SEBI/RBI/AMFI/IRDAI/UGC records; the closest (Nivesh Kavach) extracts SEBI registration numbers but explicitly leaves them as "unverified claims for the user to check". India-specific labelled datasets are small, synthetic, or both.

### Cited Findings

**Repos (GitHub API, queried 1 Nov 2026; stars | licence as detected by GitHub | pushed)**
- [apurvaraj9/scamsach](https://github.com/apurvaraj9/scamsach) — 1 | MIT | 26 Oct 2026. LangGraph agent, Gemini Flash-Lite (Groq fallback), Google Safe Browsing / URLhaus / VirusTotal / RDAP domain age; 52 labelled messages as a "regression gate, not a benchmark".
- [Kushith1/nivesh-kavach](https://github.com/Kushith1/nivesh-kavach) — 0 | none detected | 4 Oct 2026. Built for the SANGYAN hackathon; retail-investor scam checker; text/link/screenshot; Gemini 2.5 Flash; static URL checks only (never fetches user links); SEBI registration numbers extracted and flagged, not looked up; self-reported 21 synthetic samples: 12/12 recall at flag threshold, 10/12 at high-risk threshold, 0 false positives on 6 benign alerts; limitations listed (small synthetic set).
- [josephkappala/scams-sahi-nahi-hai](https://github.com/josephkappala/scams-sahi-nahi-hai) — 0 | none detected | 15 Aug 2026. Build for India (GrowthX) entry; GPT-4.1 judge with verbatim phrase quoting; RDAP domain-age, shortener flag, optional Safe Browsing; Sarvam TTS in nine Indian languages; README says no public registry of reported scam numbers and no open TRAI sender-ID lookup exists.
- [tanishqmudaliar/SilverGuard-AI-Model-Train](https://github.com/tanishqmudaliar/SilverGuard-AI-Model-Train) — 2 | MIT | 23 Feb 2026. MobileBERT fine-tuned on public + synthetic + personal SMS, ONNX export; uses TRAI DLT sender-header format (XX-XXXXXX-X; T/P/S/G suffix) as a signal; README claims public datasets give ~40% false-positive rate on real Indian SMS, falling to <1% with personal data (self-reported; test set not described; precision/recall/F1 not given).
- [ayushmore007/Aegis-AI](https://github.com/ayushmore007/Aegis-AI) — 3 | none | 26 Jul 2026 (React + Flask, Hinglish). [MirrorDNA-Reflection-Protocol/chetana-site](https://github.com/MirrorDNA-Reflection-Protocol/chetana-site) — 1 | MIT badge | Jul 2026 (12 Indian languages, safe/risky/unclear, client-side Tesseract.js OCR, no benchmarks reported). [ASROYAL/scam-shield](https://github.com/ASROYAL/scam-shield) — 0 | no licence shown | Jul 2026 (one gpt-4o-mini call per scan, ~$0.0004; India playbooks; Mesh API Hackathon). Others surfaced by search with 0-2 stars: Yash-world/PHISH_SENSE (Flask, OCR, UPI/KYC/FASTag), pr1yansh7/UPI-SMS_phishing_detector (MIT, 39 features, QR), RohanGupta214/Kavachsms, sammujoshi2k8-karna/Scanshield-India (DLT headers), gignaati/scamshield-india, XORO1337/TruDial (digital-arrest calls).
- UPI transaction-fraud ML repos (tabular, not message verification): Vatshayan/UPI-Fraud-Detection-Using-Machine-Learning 57 stars, no licence detected; kirthika1307/UPI-Fraud-Detection-using-ML 47; Rupali-2507/MULE_HUNTER 11 (GNN mule-account detection) — [GitHub search](https://api.github.com/search/repositories?q=upi+fraud+detection&sort=stars&order=desc).
- Library repos useful to Parakh: RapidFuzz MIT, 4,189 stars, pushed Oct 2026 — [GitHub](https://github.com/rapidfuzz/RapidFuzz); AI4Bharat/IndicTrans2 MIT, 489 stars — [GitHub](https://github.com/AI4Bharat/IndicTrans2).

**Datasets (HF API / pages, 1 Nov 2026)**
- Ridham115/indian-scam-sms-synthetic-audited: CC BY 4.0, ~1,580 rows (797 scam / 783 safe), fully LLM-generated (gpt-oss-120b and Gemini), Hinglish largest group (639), scam_type labels (fake_kyc, lottery, courier_customs, job_offer, electricity_bill, loan_offer, fake_bank_otp); card says "Do not use it to estimate real-world accuracy"; ~85% of rows never individually read; scam rows use invented domains while safe rows use real official domains (shortcut risk) — [dataset card](https://huggingface.co/datasets/Ridham115/indian-scam-sms-synthetic-audited).
- bolewara/hinglish-scam-text-dataset: CC BY 4.0, ~3,787 rows, English mostly from the UCI SMS Spam Collection, only 63 Hinglish rows (35 scam, 28 benign) hand-written — [dataset card](https://huggingface.co/datasets/bolewara/hinglish-scam-text-dataset).
- Hindi Spam SMS (IEEE DataPort): 3,894 messages contributed by students, spam/ham; not UPI-specific — [IEEE DataPort](https://ieee-dataport.org/keywords/spam-detection) (search summary). Shade63/scam-classification-multiclass: ~14,000 Indian-context rows, card says generated by an ML agent so likely synthetic — [HF](https://huggingface.co/datasets/Shade63/scam-classification-multiclass). Also listed on HF but not inspected: CloveAI/india-spam-sms (MIT), sahil456838/india-spam-sms (MIT), vnovaai/INDIA_FRAUD_DETECTION_JSONL_V1 (CC BY 4.0) — [HF dataset search](https://huggingface.co/api/datasets?search=india%20spam%20sms).
- ucirvine/sms_spam is the common base for "spam" corpora; HF tags its licence "unknown" — [HF](https://huggingface.co/datasets/ucirvine/sms_spam). A repo that fine-tuned on "UCI and India SMS spam datasets" reported ~40% FPR on real Indian SMS (self-reported) — [SilverGuard](https://github.com/tanishqmudaliar/SilverGuard-AI-Model-Train).
- Non-India but relevant: BothBosu/scam-dialogue and multi-agent-scam-conversation (Apache-2.0), MOZ-Smishing (mobile-money fraud, Mozambique), Bengali smishing sets (MIT) — [HF search](https://huggingface.co/api/datasets?search=scam).

### Inferences
- None of the datasets contain registry-linked claims (adviser names, registration numbers, app names), so they cannot test Parakh's actual job; Parakh needs its own labelled forwards with ground truth taken from the registries.
- The synthetic sets carry a documented shortcut (invented domains vs real brands), so using them to demonstrate "accuracy" to judges would be weak; they are useful at most as a source of message styles for the 20-test-forward set.
- The star counts show no established open-source incumbent for India scam checking, but also that judges may have seen several near-identical "paste a message, get a risk score" demos during 2026; the registry-lookup layer is the visible differentiator.
- Licence: repos showing "none detected" carry default copyright, so reuse is unsafe without asking; MIT ones (ScamSach, SilverGuard, RapidFuzz, IndicTrans2, Logic-LM) are safe to adapt with attribution.

### Gaps
- I could not verify which GitHub repos are most-starred overall for "scam SMS detection": my API queries returned only India-flavoured terms; global repos (e.g. generic SMS-spam classifiers) were not enumerated.
- No public Indian UPI-scam message dataset with real (non-synthetic) messages was confirmed.
- UCI SMS Spam Collection's true licence and origin were not checked at source.

---

## 4. Hackathon projects (Devpost, Devfolio, Smart India Hackathon) on scam/fraud verification in India

### Takeaway
Direct Devpost/Devfolio enumeration failed (HTTP 403), so this list comes from GitHub READMEs, lablab, a government PDF and news. Documented entries cluster around "paste a message, get an LLM verdict"; I found no evidence that any of them looked up SEBI/RBI/AMFI/IRDAI/UGC registries, and win status is mostly undocumented. The only confirmed winner in the fraud space is a transactions-fraud (not message-verification) entry.

### Cited Findings
- Scam Shield (ASROYAL) — Mesh API Hackathon (branded Dhruv Rathee x Mesh API), July 2026. Stack: FastAPI, OpenAI SDK via the Mesh gateway, gpt-4o-mini, static front end, Render. Demo: paste SMS/WhatsApp/email/UPI request -> 0-100 risk score, verdict, scam type, tactics, next steps, recovery guidance (1930, cybercrime.gov.in); no live lookups; "digital arrest" treated as never real in the prompt. No award mentioned — [README](https://github.com/ASROYAL/scam-shield). I could not find a winners announcement for this event.
- Nivesh Kavach — SANGYAN hackathon: see Section 3; no award mentioned — [README](https://github.com/Kushith1/nivesh-kavach).
- scams-sahi-nahi-hai — Build for India (GrowthX), Bengaluru, 15 Aug 2026; no award mentioned; searches did not confirm the event or its winners — [README](https://github.com/josephkappala/scams-sahi-nahi-hai).
- BobSec Multi-Agent Scam Shield — IBM Bob Hackathon on lablab.ai, listed 17 May 2026 by Team Stellar Stack. Node/Express + React; IBM Bob orchestrates four specialist agents (ScamAgent, FraudAgent for UPI patterns, IntelAgent for external threat intel, PolicyCheckAgent); returns Safe / Suspicious / Scam; preloaded Indian KYC and job-scam samples; demo uses synthetic users; no placement stated — [lablab submission](https://lablab.ai/submissions/rn61q8ln3ow87s2mne93hs4y).
- Central Bank of India cybersecurity hackathon (with MANIT): problem statement "AI-Powered Fraud Detection and Prevention System for Digital/UPI Transactions"; winner VNITx (VNIT Nagpur) with "FraudLens"; second runner-up NIT Rourkela's Phish'n Chips with "VishKill" (real-time scam-call detection using AI voice analysis, emotion detection, speaker diarisation, LLM analysis) — [DFS PDF](https://financialservices.gov.in/beta/sites/default/files/2025-10/Central-Bank-of-India.pdf) (direct fetch returned 404; content taken from the search-tool summary of this PDF, so re-check before quoting). Not confirmed to be on Devfolio.
- Scammune — Google AI competition project page, team "Scam busters" (India), Flutter/Android bot that judges whether messages and links come from legitimate sources; no outcome stated; link to the Gemma model not confirmed — [Google AI project page](https://ai.google.dev/competition/projects/scammune).
- Smart India Hackathon 2025 software-edition winners (K J Somaiya "Vision Craft" took the top ₹1.5 lakh prize; others) — none of the winners found was fraud/scam-specific; I could not retrieve the official SIH 2025 problem-statement list — [KJSCE](https://kjsce.somaiya.edu/en/view-announcement/1043).
- Other search hits (not inspected beyond the snippet): Suraksha.AI (React Native, Firebase, Gemini 1.5 Flash; message scanning, fake-link detection, WhatsApp SOS) — [creator0017 GitHub](https://github.com/creator0017); ScamGuard Securities concept on HackQuest targeting securities-market fraud with alerts to SEBI — [HackQuest](https://hackquest.io/projects/ScamGuardSecurities); RaKsham AI cybersecurity hackathon voice-cloning-fraud track — [Startup Grants India](https://www.startupgrantsindia.com/competitions/raksham-ai-cybersecurity-hackathon).
- Commercial context: ScamDekho (self-described India-specific checker for courier fraud, fake FASTag links, digital arrest; domain age, SSL, blacklists, payment-screenshot tamper checks) has no independent reviews — [Capterra listing](https://www.capterra.in/software/1107107/ScamDekho).

### Inferences
- Typical demo = single prompt + risk score + India playbook text + recovery numbers; a demo that shows a SEBI/RBI record being fetched and cited with a date would look different in kind.
- The honest "this has been done" list for judges: LLM scam classification for Indian SMS/WhatsApp (many), rules+LLM hybrids (Nivesh Kavach, ScamSach), multi-tool agents (ScamSach, BobSec), OCR/screenshot input (Nivesh Kavach, Chetana, PHISH_SENSE), multilingual output (scams-sahi-nahi-hai, Chetana).

### Gaps
- Devpost and Devfolio project search could not be fetched (403); no Devfolio winners list for scam verification was found. This does not mean none exist.
- No result found for winners of the Mesh API Hackathon, SANGYAN, or the 15 Aug 2026 Build for India event.
- BobSec and Scammune outcomes unknown.

---

## 5. Indian-language tooling usable in 48 hours (Bhashini, IndicTrans2, Sarvam, or the LLM itself)

### Takeaway
Fastest path is the LLM itself (Gemini/GPT-class models handled Hindi/Hinglish in every India repo found) for extraction, plus Sarvam if Indic OCR/translate/TTS is wanted (instant key, ₹100 credits). Bhashini needs registration and I could not confirm its limits; IndicTrans2 is MIT but self-hosted (no hosted API documented).

### Cited Findings
- Sarvam credits and limits: verified users get ₹100 free credits, usable on any API, "never expire". Pay-as-you-go limits per minute: Translate 60, Transliteration/Language-ID 60, chat sarvam-105b 60, STT real-time REST 60, Document AI Parse 200 (20 pages/request), Extract 30 (30 pages/request) — [Sarvam rate limits](https://docs.sarvam.ai/api-reference-docs/ratelimits). Prices: Translate ₹2 per 1,000 characters, Language ID ₹0.35 per 1,000 characters, Document Digitization ₹0.50/page, Document Extraction ₹1.00/page, TTS Bulbul v4 Flash ₹1.00 per 1,000 characters, sarvam-105b ₹15/₹60 per million input/output tokens; also serves Gemma 4, GLM, DeepSeek, Kimi, MiMo via Token Factory — [Sarvam pricing](https://docs.sarvam.ai/api-reference-docs/pricing). A search snippet of a different Sarvam page claimed ₹1,000 free credits; the two official pages I fetched both say ₹100 — [apis.io listing](https://apis.io/plans/sarvam-ai/sarvam-ai-plans-pricing/).
- Sarvam in the field: scams-sahi-nahi-hai uses Sarvam Bulbul TTS for nine-language read-aloud while GPT-4.1 does the judging — [README](https://github.com/josephkappala/scams-sahi-nahi-hai).
- IndicTrans2 (AI4Bharat): MIT code and checkpoints; supports the 22 scheduled Indian languages (+English); 1B base and 200M/320M distilled models; Hugging Face-compatible checkpoints; sequence length up to 2048 with RoPE variants; no hosted API documented (a demo link exists) — [GitHub](https://github.com/AI4Bharat/IndicTrans2).
- Bhashini: ULCA platform code is MIT on GitHub — [ULCA repo](https://github.com/bhashini-dibd/ulca). Third-party guides describe sign-up at the Bhashini dashboard yielding a user ID, ULCA API key and inference key, with pipeline config fetched via Dhruva, covering ASR, translation, TTS (also OCR, NER, transliteration in SDKs) — [community client](https://huggingface.co/spaces/pvanand/web-server/blob/d6ef585eb7fe48647e72e08ab1b766a636a5eb2c/ai4b.py), [PyPI bhashini-client](https://pypi.org/project/bhashini-client). These are unofficial; official pricing/limits were not reached (the bhashini.gov.in homepage fetch returned only a title).
- The LLM itself: Nivesh Kavach runs Gemini 2.5 Flash on English/Hindi (including Devanagari rules) with screenshots downscaled client-side to 1024 px — [README](https://github.com/Kushith1/nivesh-kavach); ScamSach runs Gemini Flash-Lite on English/Hindi/Hinglish — [README](https://github.com/apurvaraj9/scamsach); Scam Shield replies in the input's language with gpt-4o-mini — [README](https://github.com/ASROYAL/scam-shield). Google's call scam detection works in Hindi and English in India — [TechCrunch](https://techcrunch.com/2025/11/20/google-steps-up-ai-scam-protection-in-india-but-gaps-remain).
- Synthetic-data caveat: in the Indian scam SMS dataset, regional-language rows (Roman Tamil/Telugu/Bengali/Marathi) were not checked by native speakers — [dataset card](https://huggingface.co/datasets/Ridham115/indian-scam-sms-synthetic-audited).

### Inferences
- For a 48-hour build, the entity-extraction call can be a single multimodal LLM call that reads the screenshot/PDF and the Hindi/Hinglish text together; Sarvam Document AI or Bhashini OCR are only worth adding if the LLM's OCR of Devanagari/regional-script screenshots fails in testing.
- Registry names are in English/Latin script, so extraction should output transliterated Latin names alongside the original script so the fuzzy matcher has something to compare.
- Sarvam's ₹100 credit is small (at ₹0.50/page it buys ~200 pages of Document Digitization, or ~50,000 characters of Translate at ₹2 per 1,000), but enough for a demo, and the 60 requests/min pay-as-you-go limits are fine for a live demo.

### Gaps
- No benchmark of LLM accuracy on Indic-script scam screenshots or Hinglish entity extraction was found.
- Bhashini's current sign-up friction, free-tier limits and approval time are unverified.
- Sarvam's list of supported Indic languages for Translate/Document AI was not on the pages I reached.

---

## 6. Entity resolution / fuzzy name matching against registries and reporting match confidence

### Takeaway
RapidFuzz is the de-facto library and its `token_set_ratio` returns 100 for any subset match, which is dangerous for look-alike company names; legal-suffix stripping must be done with a custom Indian list because the generic `cleanco` library misses at least the "(P) Ltd" form. Published conventions for showing fuzzy-match confidence in scam checkers are essentially absent; the classical record-linkage answer is two thresholds with a "possible match / review" band.

### Cited Findings
- RapidFuzz docs: `token_set_ratio` returns 100 "if one string is a subset of the other, regardless of extra content in the longer string"; score is reduced only on explicit disagreement; `token_sort_ratio` is order-insensitive but penalises extra words; `processor` pre-processes both strings (default none); `score_cutoff` returns 0 below the cutoff — [RapidFuzz fuzz docs](https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html).
- Suffix tools: `cleanco` strips organisation-type terms ("Some Big Pharma, LLC" -> "Some Big Pharma"), with `custom_basename()` for extra terms and an acknowledged risk of missing/incorrect suffixes — [cleanco on PyPI](https://pypi.org/project/cleanco); the Python `name-matching` package offers legal pre/suffix handling — [docs](https://name-matching.readthedocs.io/en/latest/name_matching.html); the R `firmmatchr` package returns the stripped legal-form tokens so they can be audited — [CRAN](https://cran.r-project.org/web/packages/firmmatchr/refman/firmmatchr.html).
- Fellegi-Sunter record linkage: each comparison gets a log-likelihood-ratio match weight; two cutoffs divide results into link / non-link / a middle "clerical review" region; threshold choice is left to human judgement, and a bimodal score histogram is a practical guide — [starling threshold vignette](https://cran.nics.utk.edu/cran/web/packages/starling/vignettes/threshold-selection.html), [(Almost) All of Entity Resolution](https://arxiv.org/pdf/2008.04443).
- How checkers present match results: SEBI's UPI check is binary — "UPI ID Verified" with name, legal account holder and Reg. No., or "No Match Found" — [SEBI](https://investor.sebi.gov.in/upi-verification.html); Chetana outputs safe/risky/unclear with a "confidence band" and no numeric scores — [README](https://github.com/MirrorDNA-Reflection-Protocol/chetana-site); ScamSach's LLM judge outputs a verdict, scam type and confidence — [README](https://github.com/apurvaraj9/scamsach).
- SEBI-registered-entity context: SEBI rules say anyone presenting as a registered adviser/analyst must give a registration number that can be looked up on SEBI's website — [Business Standard](https://www.business-standard.com/amp/finance/personal-finance/sebi-circular-on-frauds-verify-registration-before-taking-investment-tips-125042000636_1.html) (search summary; page 403 on direct fetch).

### Inferences
Own local test, 1 Nov 2026 (rapidfuzz 3.14.6, cleanco 2.3, default_process; invented/illustrative names, not registry data):
- `cleanco.basename` correctly stripped "Pvt Ltd", "Pvt. Ltd", "Private Limited", "Limited", "LLP", but "Acme Capital (P) Ltd." became "Acme Capital (P" — a custom stop-list (`pvt, private, ltd, limited, p, llp, co`) after punctuation removal handled all variants.
- Raw scores: "Acme Capital Pvt Ltd" vs "Acme Capital Private Limited" = 83.3 (all three scorers) but 100 after suffix stripping. "Acme Pvt Ltd" vs "Acme Capital Advisors Pvt Ltd" = token_set 100.0 yet token_sort 58.5 (ratio 32.0 after stripping). "Zerodha Broking Ltd" vs "Zerodha" = token_set 100, ratio 53.8. "Kotak Securities Limited" vs "Kotak Mahindra Bank Limited" = token_set 70.3.
- Implications: (a) strip an Indian suffix list before scoring; (b) never accept on `token_set_ratio` alone — a fake "Acme" would match a registered "Acme Capital Advisors"; use `token_sort_ratio`/`ratio` as the accept score and use `token_set_ratio` only to flag "subset/partial" cases for review; (c) a three-state outcome (exact/high-confidence match; possible match -> show both names and ask; no match) mirrors Fellegi-Sunter's review band and avoids both false "verified" and false "fraud"; (d) prefer exact identifiers (SEBI registration number, RBI NBFC licence, AMFI ARN, IRDAI licence, UGC listing) as the primary key, with name similarity as a cross-check that the number belongs to the claimed name.
- No cut-off values (e.g. 90/85) are validated in the literature for Indian regulator names; Parakh's thresholds should be tuned on its own labelled pairs and reported as such.

### Gaps
- No published guidance on thresholds or confidence display for fuzzy matching against Indian regulator registries was found.
- The Splink (Fellegi-Sunter) library documentation itself was not retrieved; only general theory and an R package.
- Whether the regulator registries expose registration numbers and names in a machine-readable, scrape-friendly way is outside this brief and not checked here.

---

## 7. Evaluation: metrics for scam detection and verification, and small-sample practice for ~20 test forwards

### Takeaway
Published scam-detection numbers are mostly recall/accuracy on small or synthetic sets, with false positives on legitimate-but-urgent messages the recurring weakness; verification research adds label+evidence scoring and coverage/selective-risk reporting. With only 20 forwards, report counts and Wilson intervals, include the abstention column, and be explicit that the set is a regression gate, not a benchmark.

### Cited Findings
- LLM phone-scam detection (real-time dialogue): recall 0.98-1.00 across five models, but precision 0.70-0.77 in real-time mode on the synthetic set vs 0.95-1.00 retrospectively; authors report false-positive difficulty — [arXiv 2502.03964](https://arxiv.org/pdf/2502.03964).
- LLM vs DeBERTa phishing: LLM recall 0.91 / precision 0.72, DeBERTa-v3 0.95 / 0.89; LLM took 13-15 s per sample vs ~3.75 ms; LLM flagged genuine urgent-toned emails — [arXiv 2406.06663](https://arxiv.org/pdf/2406.06663).
- Agentic SMS scam system (authors' own system, 2026): phishing recall 91.3% -> 100%, legitimate false-positive rate 1.5% — [arXiv 2607.11707](https://arxiv.org/pdf/2607.11707).
- Google Pay UPI scam review LLM: 93.33% classification accuracy, 89% reasoning accuracy, 32% extra valid reasons — [arXiv 2410.19845](https://arxiv.org/abs/2410.19845).
- Verification metrics: FActScore = % of atomic facts supported, estimator error <2% vs humans ([ACL](https://preview.aclanthology.org/setup/2023.emnlp-main.741)); SAFE agreement with humans 72% and F1@K combining precision with a recall term ([NeurIPS](https://nips.cc/virtual/2024/poster/96675)); FEVER annotation agreement kappa 0.6841 ([arXiv](https://arxiv.org/abs/1803.05355)); AVeriTeC scores a claim as correct only when label and evidence are both adequate ([arXiv](https://arxiv.org/pdf/2410.23850)).
- Abstention metrics: coverage vs selective risk, risk-coverage curve, AURC/AUGRC ([arXiv 1705.08500](https://arxiv.org/pdf/1705.08500v1), [arXiv 2407.01032](https://arxiv.org/html/2407.01032v2)); Abdaljalil et al. report that confidence-based abstention reduces risk at moderate coverage ([arXiv 2602.14189](https://www.arxiv.org/pdf/2602.14189)).
- Small-sample statistics: for n <= ~40 Brown, Cai & DasGupta recommend the Wilson (or Jeffreys) interval over the Wald interval — [Statistical Science 2001](https://projecteuclid.org/euclid.ss/1009213286); with zero events in n trials, the "rule of three" gives an approximate 95% upper bound of 3/n — [Wikipedia: Rule of three](https://en.wikipedia.org/wiki/Rule_of_three_(statistics)).
- Small-n practice in the repos: ScamSach — 52 labelled messages, dev set 38 and holdout 14 written before tuning, 100% scam recall and 0% false positives on both, 86% exact three-class accuracy on holdout, and states "a regression gate, not a benchmark"; 76 pytest tests and a CI gate — [README](https://github.com/apurvaraj9/scamsach). Nivesh Kavach — 21 synthetic samples, publishes the limitation that the set is small and synthetic — [README](https://github.com/Kushith1/nivesh-kavach). SilverGuard — reports accuracy and real-world FPR but not precision/recall/F1 — [README](https://github.com/tanishqmudaliar/SilverGuard-AI-Model-Train). Synthetic dataset card — "Do not use it to estimate real-world accuracy" — [HF](https://huggingface.co/datasets/Ridham115/indian-scam-sms-synthetic-audited).
- Vendor accuracy claims are unaudited: Airtel 97%/99.5% (company), ScamShield "95%" (no methodology), Google DeepMind/GovTech Gemma gave no accuracy or false-positive rates — sources in Section 2.

### Inferences
Computed by me, 1 Nov 2026 (Wilson 95% two-sided; exact one-sided bound for zero events = 1 - 0.05^(1/n)):

| Result on n | Point estimate | Wilson 95% interval |
|---|---|---|
| 20/20 correct | 100% | 83.9% - 100% |
| 19/20 | 95% | 76.4% - 99.1% |
| 18/20 | 90% | 69.9% - 97.2% |
| 16/20 | 80% | 58.4% - 91.9% |
| 10/10 correct | 100% | 72.2% - 100% |
| 0 false positives among 10 legit forwards | 0% | upper bound ~25.9% (exact one-sided), 27.8% (Wilson two-sided) |
| 0 false positives among 15 | 0% | upper bound ~18.1% (exact one-sided) |

- A perfect score on 20 forwards still leaves a lower bound near 84%; a "zero false positives" claim on ~10 legitimate forwards only rules out rates above ~26%. Say so in the pitch; it reads as rigour, not weakness.
- Suggested report for the 20-forward set (my proposal built from the cited practices): (1) a confusion table whose columns include "cannot verify / abstain"; (2) coverage = items given a definitive verdict / all; (3) "wrong-definitive" count — the two dangerous cells (told a scam is verified/safe; told a genuine notice is fraud) reported separately from abstentions; (4) entity-level extraction recall against a hand-annotated list (what the LLM missed); (5) per-claim evidence correctness (AVeriTeC-style: verdict counts only if the cited record is the right one and dated); (6) Wilson intervals on each rate; (7) a stated mix (e.g. ~half real scam forwards, ~half genuine regulator/bank notices, with languages and input types listed) and the explicit label "regression gate, not a benchmark".
- Because the LLM only extracts and code decides, extraction recall and registry-match correctness can be evaluated separately from the verdict logic, which is a cleaner story than the end-to-end accuracy most repos report.
- Include genuine-but-urgent messages (real SEBI/court/bank notices) among the negatives: the literature identifies urgent legitimate messages as the main false-positive source for LLMs.

### Gaps
- No standard public benchmark reporting precision, recall and false-positive rate together for LLM scam-SMS detection was found; the cited numbers are not comparable across papers.
- No India-specific benchmark with real (non-synthetic) scam forwards was found.
- Whether any published scam-checker reports abstention/coverage explicitly was not found; ScamShield and Chetana have an "unsure/unclear" state but publish no rates.

---

## 8. Synthesis: what Parakh should copy, and what is genuinely new

### Takeaway
Copy the established pipeline shape, the explicit "cannot verify" state, quote-grounding and PII redaction, and honest small-sample reporting. The genuinely new element, as far as I could find, is deterministic verification of the entities inside a forward against several Indian regulators' official records with a dated source per item; the "LLM extracts, code decides" mechanism and the "paste a message" front-end are not new.

### Cited Findings (what to copy, with the precedent)
- Pipeline shape: claim extraction -> per-claim tool queries -> evidence -> verdict — [FacTool](https://arxiv.org/pdf/2307.13528), [Loki](https://arxiv.org/pdf/2410.01794); check-worthiness filtering and dropping ambiguous items — [Loki](https://arxiv.org/pdf/2410.01794), [Claimify](https://preview.aclanthology.org/landing_page/2025.acl-long.348.pdf).
- Three/four-way labels with an explicit insufficient-evidence outcome and evidence-conditioned scoring — [FEVER](https://arxiv.org/abs/1803.05355), [AVeriTeC](https://arxiv.org/pdf/2410.23850); product precedent for an "unsure" verdict — [ScamShield](https://guide.scamshield.gov.sg/using-scamshield/check-for-scams/how-to-check-a-scam-message), [Chetana](https://github.com/MirrorDNA-Reflection-Protocol/chetana-site).
- Code-side limits on the LLM: it can only soften a verdict by one step, cannot override hard evidence, rules-only fallback — [ScamSach](https://github.com/apurvaraj9/scamsach), [Nivesh Kavach](https://github.com/Kushith1/nivesh-kavach); formal precedent — [Logic-LM](https://arxiv.org/pdf/2305.12295), [ProgramFC](https://arxiv.org/abs/2305.12744v1).
- Grounding: verbatim quote requirement — [Anthropic docs](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations), [scams-sahi-nahi-hai](https://github.com/josephkappala/scams-sahi-nahi-hai); PII redaction before the LLM — [Nivesh Kavach](https://github.com/Kushith1/nivesh-kavach).
- Registry-match UX: show the matched record fields (name, registration number) or "No match found" — [SEBI UPI check](https://investor.sebi.gov.in/upi-verification.html); official sender registry as a positive signal — [ScamShield/IMDA](https://guide.scamshield.gov.sg/using-scamshield/check-for-scams/how-to-check-a-scam-message); India's TRAI DLT header format as a rule — [SilverGuard](https://github.com/tanishqmudaliar/SilverGuard-AI-Model-Train).
- Reporting: Wilson intervals for small n — [Brown, Cai, DasGupta](https://projecteuclid.org/euclid.ss/1009213286); coverage/selective-risk framing — [Geifman & El-Yaniv](https://arxiv.org/pdf/1705.08500v1); "regression gate, not a benchmark" language — [ScamSach](https://github.com/apurvaraj9/scamsach).
- Libraries: RapidFuzz (MIT) for matching, with a custom Indian legal-suffix list — [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz); Sarvam (₹100 credits) only if Indic OCR/TTS is needed — [Sarvam](https://docs.sarvam.ai/api-reference-docs/ratelimits).
- Prior art Parakh should acknowledge to judges: SEBI Check already lets investors verify UPI/bank credentials of SEBI intermediaries — [SEBI](https://siportal.sebi.gov.in/intermediary/sebi-check); the RBI DLA list exists for lending-app association checks — [RBI](https://rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=60403); Truecaller (27-28 Sep 2026) and Google Circle to Search (Dec 2025) accept a pasted/screenshot message and return a risk view — [TechCrunch](https://techcrunch.com/2026/09/27/truecaller-takes-its-scam-intelligence-to-the-open-web-as-it-looks-beyond-caller-id/), [Google](https://blog.google/products/search/scam-detection-circle-to-search-lens/).

### Inferences (what is genuinely new, with confidence)
- New (reasonably confident, based on my searches only; absence of evidence is not proof): one forward -> every entity and claim extracted -> each checked against the relevant Indian authority (SEBI, RBI, AMFI, IRDAI, UGC) with the record and fetch date shown per item. Evidence: Nivesh Kavach, the closest investor-focused repo, flags SEBI numbers as "unverified claims for the user to check" rather than looking them up; SEBI Check and the RBI list are single-regulator, single-question tools aimed at payment details or app association; Truecaller/Norton/Scamio/Google output a risk judgement without a per-claim registry citation.
- New in degree, not kind: the LLM never sets the verdict. ScamSach and Nivesh Kavach let the LLM raise risk (ScamSach: lower by one step), so Parakh's strict separation is stronger, but the pattern itself is Logic-LM/ProgramFC. Pitch it as "the LLM is a parser, not a judge", not as a new algorithm.
- New in framing: a verdict state that distinguishes "verified against official record" from "no record found" from "could not check (registry unavailable / ambiguous entity)" — competitors collapse these into a single score. Only ScamShield and Chetana have an "unsure" state, and neither ties it to a record lookup.
- Not new (do not claim): screenshot OCR input, Hindi/Hinglish support, plain-language explanation, recovery steps (1930, cybercrime.gov.in), multi-tool agents, risk scores, atomic claim decomposition.
- Judges will likely have seen several "paste a message -> risk score" demos from 2026 hackathons (Scam Shield, BobSec, Nivesh Kavach, scams-sahi-nahi-hai, and many 0-3 star GitHub repos), so the demo should lead with the registry-lookup step and a case where an LLM-only checker would be wrong or unsure (e.g. a genuine SEBI-registered adviser name used by an impersonator with a mismatched registration number).

### Gaps
- Coverage of the open-source and hackathon landscape is a sample, not a census: Devpost/Devfolio were not searchable here and GitHub search surfaces only repos matching my keywords.
- I did not verify, for any of the five regulators, how machine-readable their registries are or whether the SEBI/RBI pages Parakh would query are stable; that belongs to the registry research track.
- "Genuinely new" claims rest on not finding a counter-example; they should be phrased as "we found no ... in our survey" in any pitch.
