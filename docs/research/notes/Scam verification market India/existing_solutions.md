# Existing solutions in India for verifying whether a notice, message, adviser, lender, app, number or claim is genuine (competitor map for Parakh), as of 31 Oct 2026

Provenance legend. [OFFICIAL] = text returned from the official page itself (only sancharsaathi.gov.in was fetched directly). [OFFICIAL-QUOTED] = search result quoting an official page or press release (RBI, PIB, ITD, Meta, Google blog, scamshield.gov.sg). [NEWS] = news, explainer or search snippet. [LISTING] = self-published product listing. The research budget was about 20 tool calls. Items marked "not found" or "not researched" were not searched deeply, so they are not claims of non-existence. Most search results are LLM-summarised snippets, so figures should be re-checked before they go on a slide.

## 1. Government tools: what each does, input, registry checked, reach

### Takeaway
Government tools are single-purpose and registry-specific. Each checks one thing (a number, a DIN, an intermediary's UPI ID, an entity's registration) and none takes a pasted or forwarded document or message and checks it across several regulators. I found no single government front door that returns a sourced verdict plus next step. That is the main gap for Parakh.

### Cited Findings
Telecom and cybercrime
- Sanchar Saathi (DoT) lists these citizen services [OFFICIAL]. Source: [sancharsaathi.gov.in](https://sancharsaathi.gov.in)
  - Chakshu reports suspicious call, SMS or WhatsApp. Input: medium, category, details, optional screenshot, your mobile number with OTP. It is a reporting tool, not a verdict tool. The page itself says money lost goes to 1930 or cybercrime.gov.in.
  - TAFCOP ("Know Your Mobile Connections") shows SIMs registered in your name via OTP and lets you flag ones that are not yours.
  - KYM checks handset genuineness by 15-digit IMEI (SMS "KYM <IMEI>" to 14422). It is a device check, not a scam check.
  - International call reporting (spoofed +91 calls), by number plus date and time.
  - "Trusted Contact Details" (Beta) verifies official contact info for banks and financial institutions. Input: institution name, contact number or website. This is the closest government feature to a "is this number genuine" lookup, but it is limited to banks and financial institutions and labelled Beta.
- Chakshu results: over 29 lakh mobile numbers deactivated after Chakshu flags [NEWS, search summary citing the DoT press release] — [Sanchar Saathi press release PDF](https://sancharsaathi.gov.in/SancharSaathiDocuments/ImportantDocuments/Press%20Release%20-%20Sanchar%20Saathi%20Mobile%20App%20crosses%2050%20lakh%20downloads.pdf), [Vikaspedia](https://en.vikaspedia.in/viewcontent/e-governance/mobile-governance/sanchar-saathi-portal?lgn=en)
- The Sanchar Saathi mobile app crossed 50 lakh downloads [OFFICIAL title only; the date is not captured] — same press release.
- I4C Suspect Registry [NEWS]. Launched 10 Sep 2024 by I4C as a database of identifiers of suspected cyber criminals, fed from NCRP data. It is for banks and law enforcement and RBI told banks to integrate it. Public access is not described. — [Drishti IAS](https://www.drishtiias.com/daily-updates/daily-news-analysis/india-s-suspect-registry-and-cybersecurity-initiatives), [AIR](https://www.newsonair.gov.in/suspect-registry-of-identifiers-of-cyber-criminals-launched-in-collaboration-with-banks-and-financial-institutions-centre)
  - Impact figures conflict: about Rs 5,100 crore saved (Drishti) vs Rs 9,518 crore blocked (Policy Edge). Treat as unreconciled. See [Policy Edge](https://www.policyedge.in/p/ministry-of-home-affairs-strengthening-the-indian-cyber-crime-coordination-centre-i4c).
- Samanvaya, the I4C coordination platform, holds about 1.84 million suspect identifier records from banks (Dec 2025 report, with privacy concerns raised) [NEWS]. — [MediaNama](https://www.medianama.com/2025/12/223-samanvaya-portal-tracks-1-8m-suspects-raises-privacy-concerns/)
- The cybercrime.gov.in "Report and Check Suspect" feature: not found. The search found no source naming it, so I cannot confirm its name or whether the public can query it. Needs a direct look at cybercrime.gov.in.
- 1930 helpline and NCRP are the primary victim-reporting channels [NEWS]. They are reactive (post-fraud). — [Drishti IAS](https://www.drishtiias.com/daily-updates/daily-news-analysis/india-s-suspect-registry-and-cybersecurity-initiatives)

RBI
- RBI Sachet (launched 4 Aug 2016) lets users check whether an entity is registered with RBI, SEBI, IRDAI or PFRDA ("Check if an entity is registered") and file complaints about unauthorised deposit-taking, loan or investment activity [NEWS/OFFICIAL-QUOTED: RBI press release and a Business Standard 2025 guide]. It is a manual name lookup, not an AI check. Outlook describes it as preventive, not a remedy. — [Business Standard 2025](https://www.business-standard.com/amp/finance/personal-finance/thinking-of-investing-rbi-s-sachet-lets-you-verify-scheme-before-you-trust-125111201164_1.html), [Outlook Money](https://www.outlookmoney.com/banking/how-rbis-sachet-portal-helps-people-identify-fake-financial-schemes-and-report-them-easily), [RBI PR 2016](https://www.rbi.org.in/SCRIPTs/BS_PressReleaseDisplay.aspx?prid=37689)
- RBI public directory of Digital Lending Apps (DLAs) EXISTS as a policy [OFFICIAL-QUOTED]. Under the Digital Lending Directions 2025, regulated entities report their apps on the CIMS portal, and the public list was due "on or before July 1, 2025" under Citizen's Corner > "DLAs deployed by Regulated Entities". The list is "on as is basis, without any further validation check by the Reserve Bank", and RBI does not endorse it. Its stated purpose is helping customers verify a DLA's association with a regulated entity. — [RBI press release 60403 via search quote](https://rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=60403), [MediaNama May 2025](https://www.medianama.com/2025/05/223-rbi-digital-lending-apps-centralised-directory/). Direct fetch of the RBI page failed (HTTP 418), so I did not confirm that the live list is up and what it contains. A Google blog summary also mentions Google working with RBI on a public list of authorised lending apps and their NBFC partners.
- RBI is reportedly building an AI-based real-time fraud warning system; MuleHunter.AI (RBIH) is used by banks to flag mule accounts [NEWS, "reportedly"]. — [MyMobileIndia](https://www.mymobileindia.com/pib-fact-check-warns-of-sbi-rewards-app-download-scam-rbi-plans-ai-based-anti-fraud-system/)

SEBI
- SEBI Check plus "@valid" UPI handles went live around 1 Oct 2025 [NEWS; Business Standard reported the 1 Oct date]. Input: scan a QR or type a UPI ID. Output: shows the registered intermediary's type, bank account and IFSC, and warns if the payee is not SEBI-registered. Registered intermediaries get "@valid" handles issued through NPCI, and payment apps show a green-triangle thumbs-up. It covers payee verification only. It does not verify a stock-tip message, a WhatsApp group or an adviser's claims. — [SCC Online](https://www.scconline.com/blog/post/2025/10/04/sebi-introduces-verified-upi-handles-and-sebi-check-to-safeguard-investors/), [Moneylife](https://www.moneylife.in/article/sebi-launches-at-valid-upi-handles-and-checking-tool-to-curb-payment-frauds/78469.html), [Business Standard](https://www.business-standard.com/amp/finance/personal-finance/pay-safe-invest-smart-sebi-s-new-valid-upi-handles-protect-your-money-125100200130_1.html). Whether a standalone app exists was not confirmed (one source says it is reachable via SEBI's site and the SEBI Saarthi app).
- SEBI "Authenticate Document Number Issued by SEBI" (menu on sebi.gov.in) lets people check a SEBI letter, notice or summons against its UDIN/document number [NEWS summarising SEBI's warning]. SEBI warned in 2025 that forged notices and its letterhead are being misused (for example "SEBI-authorised merchant accounts"). — [Moneylife](https://moneylife.in/article/sebi-warns-about-forged-notices-misuse-of-its-letterhead-and-official-identity/77331.html), [Angel One](https://www.angelone.in/news/market-updates/sebi-alerts-public-about-fraudulent-notices-and-forged-documents)
- SEBI "registered intermediary search" (investor-adviser, broker and similar lookups): confirmed only indirectly, as advice to "check registration status on SEBI's website" [NEWS]. — [Vision IAS](https://visionias.in/current-affairs/upsc-daily-news-summary/article/2025-04-22/business-standard/economy/sebi-circular-on-frauds-verify-registration-before-taking-investment-tips). I did not capture its input fields or whether it has an API.
- #SEBIvsSCAM awareness campaign with NSE, plus SEBI asking social platforms to act on investment scams [NEWS]. — [Angel One](https://oga-prod.angelone.in/news/market-updates/sebi-launches-sebivsscam-to-save-investors-from-fake-apps-and-fraud-tips)

Tax
- Income Tax "Authenticate notice/order issued by ITD" is a quick link on the e-filing portal and needs no login [OFFICIAL-QUOTED via the portal help page and secondary guides]. Two methods: by DIN, and by document type, assessment year and date of issue for notices without a DIN. DIN is generally required on communications from 1 Oct 2019. It only verifies documents uploaded to the ITD system. Sources disagree on whether a mobile number is mandatory, and one guide's claim that DIN became required in April 2026 conflicts with the October 2019 date and should be ignored. — [ITD help page](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/authenticate-noticeorder-issued-itd), [Outlook Business](https://business.outlookindia.com/personal-finance/tax/received-notice-from-the-income-tax-department-heres-how-to-verify-its-authenticity), [Quicko](https://learn.quicko.com/authenticate-notice-order-issued-by-itd)
- CBIC DIN verification and eCourts case-status checks: not researched in this pass (the CBIC query returned only Income Tax results). Marked "not found / not researched", so Parakh's team should verify these on the official portals.

Misinformation and deepfakes
- PIB Fact Check Unit takes queries via WhatsApp +91 8799711259, email and portal factcheck.pib.gov.in, free [OFFICIAL-QUOTED from PIB FAQ]. Scope is claims about the Government of India. It is not a scam or financial-adviser checker. — [PIB FAQ](https://pib.gov.in/FAQ_fact.aspx), [Vikaspedia](https://en.vikaspedia.in/viewcontent/e-governance/citizen-services/pib-fact-check?lgn=en)
- Deepfakes Analysis Unit (DAU) tipline: WhatsApp +91 9999025044, live from 25 Mar 2024, English, Hindi, Tamil and Telugu. Takes forwarded audio and video and assesses whether AI-generated [OFFICIAL-QUOTED from Meta's Feb 2024 post; NEWS for the launch date]. Operated by the Misinformation Combat Alliance with Meta, so it is not a MeitY unit as far as sources show (MeitY involvement not confirmed). I could not confirm it is still running in Oct 2026. — [Meta](https://about.fb.com/news/2024/02/mcas-whatsapp-helpline-curbing-the-spread-of-ai-generated-misinformation/), [Business Today](https://www.businesstoday.in/amp/technology/news/story/meta-to-launch-whatsapp-tipline-to-detect-deepfakes-in-india-422474-2024-03-22)

### Inferences
- Roughly eight separate portals each hold one slice of the truth (DoT, I4C, RBI x2, SEBI x2-3, ITD, PIB, plus CBIC and eCourts to verify). A consumer has to know which one applies to their notice, then navigate there. Cross-registry routing is the unserved job.
- Only the ITD and SEBI document-authentication tools check an actual document, and only by identifier, so the user must find and type the DIN or UDIN.
- RBI's DLA list is explicitly unvalidated, so a good verdict needs extra signals (app store listing, NBFC partner, domain age).
- Sanchar Saathi's "Trusted Contact Details" (Beta) is the closest government feature to number verification, but limited to banks and financial institutions.

### Gaps
- cybercrime.gov.in "Report and Check Suspect": not found; the public access status is unconfirmed.
- Whether the RBI DLA list is live at the expected path and what fields it exposes (fetch blocked).
- SEBI intermediary search input fields and API availability; CBIC DIN and eCourts details.
- Whether the DAU tipline is still active in late 2026.
- Whether any of these registries expose APIs or only web forms/CAPTCHAs (important for Parakh's "live" claim). Not checked.

## 2. Private tools and platforms

### Takeaway
Private players are strong on call, SMS and link-level scam signals (Truecaller, Google, Airtel) and have started offering "paste it and check" tools. None found cites SEBI, RBI, ITD or other regulator registries. Fact-checkers cover viral claims, not personal financial notices.

### Cited Findings
- Truecaller Scam Checker was launched in India on Android in late Sept 2026 [NEWS]. It checks links for phishing signs and phone numbers against Truecaller's systems and community reports. A screenshot-upload feature is "expected". ScamFeed has about 20,000 India reports at about 1,300 per week. The sources show no regulator-registry checking. — [TechCrunch 27 Sep 2026](https://techcrunch.com/2026/09/27/truecaller-takes-its-scam-intelligence-to-the-open-web-as-it-looks-beyond-caller-id/), [Media Infoline](https://www.mediainfoline.com/brand/truecaller-scam-checker-brings-together-scam-detection-and-community-intelligence). Truecaller's AI Call Scanner (2024) went to the US first, India later. Truecaller's voicemail transcribes 12 Indian languages [NEWS snippet]. — [Business Today Sep 2025](https://www.businesstoday.in/amp/technology/news/story/truecaller-adds-ai-powered-insights-to-caller-id-to-detect-scams-spams-in-real-time-492592-2025-09-04)
- Google India Safety Charter (June 2025) [OFFICIAL-QUOTED from Google's India blog, excerpt only]. Google Messages Scam Detection screens about 500M suspicious messages a month on-device. Play Protect pilot (Oct 2024) stopped about 60M install attempts of high-risk apps on 13M devices. Google Pay issued 41M scam warnings in 2024. Google says it worked with RBI on a public list of authorised lending apps. DigiKavach (2023) targeted predatory loan apps. — [Google blog](https://blog.google/intl/en-in/company-news/googles-safety-charter-for-indias-ai-led-transformation/), [Business Today](https://www.businesstoday.in/amp/technology/news/story/google-launches-safety-charter-to-secure-indias-ai-future-flags-online-fraud-and-cyber-threats-480718-2025-06-17)
- Google on-device call scam detection (Gemini Nano) in India is Pixel 9 and later only, per Google to TechCrunch (Nov 2025). TechCrunch notes fake investment and loan apps have stayed on Play until intervention. — [TechCrunch Nov 2025](https://techcrunch.com/2025/11/20/google-steps-up-ai-scam-protection-in-india-but-gaps-remain). One Tribune snippet says it works in Hindi and English [NEWS]. — [Tribune](https://www.tribuneindia.com/news/business/google-building-safe-trusted-ai-to-protect-vulnerable-users-in-india)
- WhatsApp is testing on-device AI scam-chat alerts for unknown contacts, limited rollout from Aug 2026 [NEWS]. It is a platform feature, not a third-party checker. — [Analytics Insight](https://www.analyticsinsight.net/news/whatsapp-scam-alert-uses-ai-to-catch-chat-scams)
- Airtel AI spam detection filters calls and SMS, with SMS checked against a database of blacklisted URLs [NEWS]. — [Tribune](https://www.tribuneindia.com/news/airtel-launches-ai-powered-spam-detection-service), [TechCrunch 2024](https://techcrunch.com/2024/09/24/airtel-taps-ai-to-combat-india-rampant-spam-calls-problem)
- Fact-checkers: BOOM WhatsApp tipline +91 77009 06588 [OFFICIAL-QUOTED from BOOM methodology page]. — [BOOM methodology](https://www.boomlive.in/methodology). Alt News, Factly and Vishvas News tiplines: not researched in this pass. They address viral claims, and I found no sign they check personal notices or lenders.
- CloudSEK (XVigil) is B2B brand and takedown monitoring: its own write-up claims 3,000+ fake apps and domains removed in 2022–23, with BFSI most targeted. It also reported dozens of fake Android bank apps. These are vendor claims. It is not consumer-facing. — [CloudSEK](https://cloudsek.com/whitepapers-reports/the-story-behind-cloudsek-takedowns), [TechRadar](https://www.techradar.com/pro/security/online-scammers-target-desperate-loan-seekers-using-online-fraud)
- Indian startup and consumer scam-checkers found (all small, self-described, [LISTING]/[NEWS]):
  - Kavach by DigiKavach Technologies, Bengaluru: paste a number, message or link for verification. — [Deccan Herald](https://deccanherald.com/business/startups/bengaluru-startup-launches-kavach-app-to-flag-suspicious-calls-messages-4093714)
  - Bachao.AI: on-device call, SMS and WhatsApp screening, July 2025 launch per YourStory profile. — [YourStory](https://yourstory.com/companies/bachaoai)
  - ScamMukt (Project Bear Corp): links, fake websites and QR codes, priced about Rs 50/month. — [Tribune](https://www.tribuneindia.com/news/business/scammukt-launches-indias-dedicated-ai-scam-protection-app-because-spotting-a-scam-is-now-a-basic-survival-skill-for-every-indian/)
  - ScamDekho (messages, websites, payment screenshots; no launch date) — [Product Hunt](https://www.producthunt.com/products/scamdekho)
  - Seerie (offline, on-device, Indian scams such as UPI fraud and digital arrest) — [Product Hunt](https://www.producthunt.com/products/seerie)
  - "AI Scam Detector WhatsApp Scanner" (India-HQ per listing, founded 2023, 5 free checks a day) — [Stork](https://www.stork.ai/en/ai-scam-detector-whatsapp-scanner)
  - DAPA: GitHub WhatsApp bot for reporting scams in local languages, for trend collection rather than verdicts — [GitHub mirror](https://proxy-dev.blitzz.co/proxy/123456/github.com/raushan-in/dapa)
  - Quick Heal mentions "Antifraud.AI", but the excerpt does not describe it — [Quick Heal PDF](https://www.quickheal.co.in/documents/media/2025/qh-exposes-alarming-rise-in-ai-chatbot-scams-across-india-et-ciso.pdf)
- Bank and fintech in-app fraud warnings: Google Pay's 41M warnings (above). Per-bank and PhonePe/Paytm warnings and Navi/Paytm/GPay screen-sharing alert pilots were mentioned [NEWS, Google/TechCrunch]. Other bank in-app warnings: not researched.

### Inferences
- The crowded layer is signal-based detection (number reputation, URL blacklist, language classifier). The empty layer is authority-based verification: "does this named SEBI adviser, RBI-listed app or ITD notice actually exist in the official record?" None of the Indian consumer tools found describe doing this.
- Truecaller's roadmap (screenshot upload) means a Truecaller entry into "paste and check" is imminent, but its data moat is community reports, not regulator records.
- Indian startup tools are tiny and mostly paste-a-link/number products. Their Indian-language support and registry usage are undocumented (not found).

### Gaps
- Alt News, Factly and Vishvas News tipline details; bank-by-bank in-app warnings; whether Kavach, ScamDekho, Bachao.AI or ScamMukt cite regulator registries (I could only read marketing snippets); user counts and funding for the startups.
- Google Play's specific India loan-app policy text (2023–24 financial-services policy) was not fetched; only the Safety Charter summary.

## 3. International analogues

### Takeaway
Singapore's ScamShield is the best government-run analogue (police database, call blocking, SMS filter, bot to check a message). Norton Genie, Bitdefender Scamio and similar are the closest "paste it and ask an AI" analogues, but they judge by text patterns and general threat intelligence, not by querying national regulator registries.

### Cited Findings
- ScamShield (Singapore), built by Open Government Products with SPF and NCPC [OFFICIAL-QUOTED, scamshield.gov.sg]. It blocks calls against an SPF database, uses an on-device SMS classifier (Android only notifies), and the "ScamShield Bot can check if a message or a call is a scam and report scams to SPF". App reports are not police reports. — [ScamShield set-up page](https://scamshield.gov.sg/set-up-scamshield-app), [GovInsider](https://govinsider.asia/smart-gov/meet-singapores-latest-weapon-against-scams-open-government-products-scamshield/)
- Norton Genie: paste text or upload a screenshot and get an assessment, follow-up Q&A and next-step suggestions; Norton says it may be unable to decide. It is now also in ChatGPT and Claude (2026 reports) [NEWS/vendor]. — [Norton Genie](https://genie.norton.com), [IT Wire](https://itwire.com/security/norton-launches-genie-scam-detector.html), [SC World](https://www.scworld.com/brief/nortons-scam-detection-tool-now-available-in-claude-and-chatgpt)
- Bitdefender Scamio: chatbot, launched on WhatsApp in Australia in May 2024 [NEWS]. — [IT Brief](https://itbrief.com.au/story/bitdefender-launches-ai-scam-detector-scamio-on-whatsapp-in-australia)
- UK Action Fraud / Take Five, Australia Scamwatch, US FTC ReportFraud: the search returned nothing about these, so the details are not found in this pass. From general knowledge only (not sourced here, treat as unverified) they are mainly reporting and awareness channels.
- Microsoft and Google "is this a scam" assistants outside India: not researched.

### Inferences
- The framing that Parakh is "ScamShield or Genie plus live official registries and a sourced verdict" is supported by the sources I found. I found no international analogue that cites regulator registries, but that is "not found", not "does not exist".
- Genie and Scamio show demand for chat-native delivery (WhatsApp, inside an LLM), which supports Parakh's forward-it-to-a-bot input model.

### Gaps
- UK, Australia, US tools and Microsoft/Google assistants were not searched successfully.

## 4. Capability matrix (what I could confirm)

Columns: takes actual document or message / checks several registries / cites sources / Indian languages / gives next step. "?" = not confirmed in sources.

- Sanchar Saathi Chakshu: message details and screenshot (report only) / no, DoT telecom data / no verdict / ? / yes, points to 1930 for money loss
- TAFCOP and KYM: no (OTP or IMEI) / telecom only / n/a / ? / flag action only
- I4C Suspect Registry: not public as far as found / bank-facing / n/a / n/a / n/a
- 1930 and NCRP: reactive reporting / no / no / ? / yes (filing)
- RBI Sachet: name search, not a document / RBI, SEBI, IRDAI, PFRDA entity registration / no / ? / complaint route
- RBI DLA list: app name lookup / RBI-regulated-entity apps only, unvalidated / RBI is the source / ? / no
- SEBI Check: UPI ID or QR / SEBI intermediaries only / SEBI data / ? / warns if unregistered
- SEBI document authenticate: document number / SEBI only / yes / ? / verification result
- ITD Authenticate notice: DIN or notice metadata / Income Tax only / yes / ? / verification result
- PIB Fact Check: claims forwarded on WhatsApp / government claims only / yes, PIB posts / ? / debunk
- DAU tipline: audio and video forwarded on WhatsApp / AI-media detection, not registries / ? / English, Hindi, Tamil, Telugu / assessment
- Truecaller Scam Checker: link or number (screenshot planned) / community reports and own systems, no regulators found / ? / ? / flag
- Google Messages/Play Protect/GPay: device-level, automatic / own signals / n/a / Hindi and English for some features / warnings
- Norton Genie and ScamShield Bot: pasted text or screenshot / own threat intel / ? / English-centric (not confirmed) / yes (Genie gives next steps)
- Indian startups (Kavach, ScamDekho, Bachao.AI, ScamMukt, Seerie): paste or on-device / own models; registries not found / ? / ? / ?

### Inferences
- No tool in the list ticks "several registries + cites sources + takes the real document + next step" together. Parakh's wedge is the combination, not any single check.

## 5. Near-identical products in hackathons or startups

### Takeaway
I found no project that matches Parakh's full definition (forward a notice, tip, adviser or loan app, agent checks SEBI/RBI/CBIC/ITD/eCourts/PIB live, sourced verdict plus next step). I found close cousins. "Not found" does not mean absent, especially since Smart India Hackathon and Devfolio project archives are poorly indexed.

### Cited Findings
- ScamGuard (Devpost): AI app for fraud in India's securities markets, integrating with SEBI SCORES and the 1600 helpline [LISTING]. — [Devpost](https://devpost.com/software/scamguard)
- ScamGuardSecurities (HackQuest): chatbot teaching retail investors to spot red flags [LISTING]. — [HackQuest](https://hackquest.io/projects/ScamGuardSecurities)
- SEBI's own Securities Market Hackathon (powered by SEBI, BSE, CDSL, NSDL, KFINTECH; 2025 round deadline 5 Sep 2025) shows regulators are soliciting investor-protection tooling [NEWS/OFFICIAL]. — [Global Fintech Fest](https://www.globalfintechfest.com/gff-hackathons/sebi-hackathon)
- A "Scam Alert India" awareness site on lovable.app exists [LISTING; content not verified]. — [scamalertindia.lovable.app](https://scamalertindia.lovable.app/)
- No Smart India Hackathon entry was found. The one search returned only scam news, not SIH problem statements or winners.

### Inferences
- The idea space is occupied by awareness chatbots and generic detectors. The "live official-registry agent" claim looks unoccupied in what I found, but I cannot rule out that SIH or Devfolio entries exist.
- Regulator interest (SEBI hackathon, SEBI Check) suggests a regulator could build or bless a competing feature, which is a strategic risk to mention.

### Gaps
- Smart India Hackathon archive search and a direct Devfolio search were not done. A follow-up should check SIH problem statements on cybercrime and fintech fraud.
- Funded startups doing registry-backed verification (for example in KYC/RegTech) were not surveyed.

## 6. Overall gap for Parakh (synthesis for the report writer)

### Takeaway
Gap = cross-registry, document-in, sourced verdict, plain next step, in Indian languages, via chat. Each official tool answers one narrow question after the user already knows which regulator is involved. Private tools answer "does this look scammy" without citing official records.

### Cited Findings
- Per sections 1 to 3 above: official tools are siloed by regulator and mostly identifier-based, private tools are signal-based, and the international AI assistants judge text without national registries.

### Inferences
- Defensibility risks to flag: (a) registries such as RBI's DLA list are unvalidated and may lack APIs; (b) the ITD and SEBI authenticate tools need identifiers and may use CAPTCHAs, which limits "live" automation; (c) Truecaller, Google and WhatsApp can add paste-and-check quickly; (d) liability of a "genuine/fake" verdict, so phrase outputs as "found / not found in official record".
- Messaging to verify with the team: wording such as "no existing tool does this" should be softened to "none found in our survey".

### Gaps
- Registry API or scrape feasibility, Indian-language support of competitors, and user adoption numbers for small Indian startups were not established.
