# Indian official registries and verification services for Parakh (48-hour hackathon build sheet)

Test conditions: fetches made 31 Oct 2026 via WebFetch from a tool whose network location is unknown (possibly outside India). Failures marked "geo/bot-block?" may be that or WebFetch being blocked by the site's bot filter; I cannot tell which. WebFetch returns a summarised page, not raw HTML, so "loaded" means content was returned, not that the form works for a script. Statuses: LOADED = loaded in my test; DOC = documented (search snippets/secondary sources) but not tested; NF = not found.

## Which sources offer an API, search page, downloadable file, or only a captcha form?

### Takeaway
Almost none of these registries has a free official public API. The practical 48-hour pattern is: (a) bulk-download or scrape-with-permission static lists (RBI PDFs/lists, UGC PDF, IRDAI lists, SEBI intermediary pages) into a local SQLite/CSV and match offline; (b) deep-link the user to captcha/OTP-gated tools (eCourts, IT notice authentication, GST search, CBIC DIN, cybercrime.gov.in) rather than automate them; (c) use paid/licensed API resellers only for MCA/GST if budget allows.

### Cited Findings (build sheet, per source)

**1. SEBI registered intermediaries (investment advisers, research analysts, brokers, PMS etc.)**
- URL tested: https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13 (intmId=13 = investment advisers; other intermediary types use other intmId values, not individually tested). Status: LOADED. — [SEBI](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13)
- Answers: is this name/registration number a SEBI-registered investment adviser; validity date, address, email, phone, contact person. Page showed "1 to 25 of 1071 records" and "Registered intermediaries as on date Oct 30, 2026" (an as-of date IS shown). — same source
- Input: name/trade name, registration no., contact person, email, location; A-Z filter; "Show All Records". Output: HTML table, 25 per page. No export/CSV/PDF link seen. No captcha on search (captcha only on the login panel). — same source
- Access method: HTML search form (JavaScript-driven; paging is JS so scripting needs care). Rate limits: not stated.
- robots.txt (LOADED): `User-agent: *`, disallows only /js, /hindi/js, /css, /hindi/css; the intermediary page is not disallowed. — [SEBI robots.txt](https://www.sebi.gov.in/robots.txt)
- Terms of use: not read in my test (NOT TESTED). Check the SEBI website terms/disclaimer before scraping; a polite low-rate fetch of ~1,100 rows then caching locally is the lowest-risk pattern.

**2. SEBI orders / debarred entities**
- URL tested: https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=6 (Orders of AO listing). Status: LOADED. 12,018 records, 25 per page, filters: keyword (title/entity name), date range, section dropdowns. Page links are JS calls so result pages have no own URL; individual orders have direct URLs. No "last updated" stamp (only per-entry dates). No RSS found on the page; email-subscription link requires registration with captcha. — [SEBI orders](https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=6)
- Tested listing is adjudication orders only; I did not locate a single "debarred entities" register page. Gap below.

**3. SEBI Check / validated UPI handles (@valid)**
- Went live 1 Oct 2025 (circular 11 Jun 2025). Lets users verify an intermediary's UPI ID, bank account number and IFSC before paying; available via SEBI Check portal, Saarthi app, SEBI website. Intermediary UPI IDs carry the "@valid" suffix issued by NPCI. — [Outlook Money](https://www.outlookmoney.com/invest/equity/sebi-launches-validated-upi-handles-sebi-check-to-curb-payment-fraud), [Business Standard](https://www.business-standard.com/amp/finance/personal-finance/pay-safe-invest-smart-sebi-s-new-valid-upi-handles-protect-your-money-125100200130_1.html)
- Status: DOC (news summaries only). My guess URL https://sebicheck.sebi.gov.in did not resolve (DNS ENOTFOUND), so the real URL is unconfirmed. No API found. Cheap useful rule for Parakh without the tool: a payment handle claiming to be an adviser/broker that does not end in "@valid" is a red flag (inference from the rule above; individuals' personal UPIs are exempt).

**4. NSE (unauthorised entities / authorised persons) and BSE (investor alerts)**
- NSE https://www.nseindia.com/investor-protection-unauthorised-entities: fetch timed out (60 s). Status: not loaded (NSE is known to be hostile to bots; cause unknown). Content unverified.
- BSE https://www.bseindia.com/investors/investor_alert.aspx: HTTP 403 Forbidden. Status: geo/bot-block? Not loaded.
- Both: NF for any official API for these lists in my search. NSE publishes a data-sharing policy dataset list for research (not an entity-verification API) — [NSE data list PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Data%20list%20under%20NSE%20Data%20Sharing%20Policy%20for%20Research%20and%20Analysis_20250728.pdf).
- Recommendation: use SEBI's intermediary list as the primary check and link to NSE/BSE pages for the user; do not rely on scripted access.

**5. AMFI distributor (ARN) search**
- URL: https://www.amfiindia.com/locate-distributor. Status: LOADED. Search by name or ARN (provide any one detail), location filter, a "Download" button whose format is not stated, no captcha mentioned, no as-of date shown for distributor data. — [AMFI](https://www.amfiindia.com/locate-distributor)
- Official API: NF. Terms: not read. Note AMFI's NAV file (portal.amfiindia.com NAVAll.txt) is a different well-known plain-text download; not tested here.

**6. RBI lists (NBFC list, cancelled certificates, Alert List, payment system operators, Sachet)**
- RBI https://www.rbi.org.in/Scripts/BS_NBFCList.aspx , https://www.rbi.org.in/Scripts/BS_ViewForexAlertList.aspx , https://www.rbi.org.in/commonman/english/Scripts/Sachet.aspx : all returned HTTP 418 "I'm a Teapot" to my fetcher. Status: not loaded; looks like bot-filtering rather than geo-blocking (418 is not a normal geo response), but cause unconfirmed. Content not verified by me.
- Alert List of unauthorised forex platforms: latest update found 19 Nov 2025 added 7 names, total 95; RBI says list is not exhaustive and absence does not mean authorised. Earlier: Oct 2024 total 88; Nov 2023 total 75; Sept 2022 original 34. — [Outlook Money](https://www.outlookmoney.com/amp/story/invest/check-rbis-updated-alert-list-for-unauthorised-forex-trading-platforms), [RBI press release](https://website.rbi.org.in/web/rbi/-/press-releases/rbi-issues-an-updated-alert-list-55201). Status: DOC. I found no update after Nov 2025, but this does not prove none exists.
- Digital lending apps (DLA) directory: RBI Digital Lending Directions 2025 require REs to report apps on the CIMS portal (operational from 13 May 2025); RBI publishes the list on its website under Citizen's Corner ("DLAs deployed by Regulated Entities") from 1 Jul 2025. Data are as-reported by REs, not validated by RBI; RBI does not endorse. — [Medianama](https://www.medianama.com/2025/05/223-rbi-digital-lending-apps-centralised-directory/), [RBI directions](https://website.rbi.org.in/documents/d/rbi/pr288directionsondigitallending), [Angel One](https://www.angelone.in/news/market-updates/rbi-makes-it-mandatory-to-report-digital-lending-apps-in-cims-portal-from-may-13). Status: DOC; exact live URL and format not confirmed.
- Reasoning for Parakh: a loan app NOT on the DLA list and not run by a listed NBFC/bank is a strong red flag; but absence on a partly self-reported list is "not found in directory", not "fraud".
- Sachet (state-level unregistered-deposit complaints/info), payment system operators list, NBFC cancelled-certificate list: URLs not confirmed by me; DOC at best (from background knowledge, unsourced, so treat as unverified).
- Search hit claims RBI open-data API endpoints live since 23 Sep 2025 per a third-party registry, unconfirmed against RBI — [weboftrust](https://www.weboftrust.org/entity/reserve_bank_of_india-7377).

**7. IRDAI**
- URL: https://www.irdai.gov.in/ . Status: LOADED. Lists pages: life insurers /list-of-life-insurers1, general /list-of-general-insurers, health /list-of-health-insurers, reinsurers /list-of-reinsurers, brokers /list-of-brokers, corporate agents /list-of-corporate-agents1, IMFs /list-of-imfs, surveyors, TPAs, web aggregators, repositories (all under https://irdai.gov.in/). Complaints portal Bima Bharosa https://bimabharosa.irdai.gov.in/. — [IRDAI](https://www.irdai.gov.in/)
- Individual list pages not opened; format (HTML/PDF/XLSX), as-of date and individual-agent lookup unverified. Individual insurance agent licence lookup: NF in my test. Bima Sugam not mentioned on the homepage.

**8. MCA company master data (CIN)**
- https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html : HTTP 403. Status: geo/bot-block? Not loaded. Captcha/login behaviour unverified.
- No official free MCA/API Setu CIN API confirmed (search surfaced none). Paid resellers (Decentro, Meon, Qorpiq, AuthBridge) offer CIN/LLPIN lookup by API key; they are commercial, not official. — [Decentro](https://decentro.tech/api-hub/cin-verification-api), [Qorpiq docs](https://developers.qorpiq.com/docs/mca-company-master-data)

**9. Income Tax "Authenticate notice/order issued by ITD"**
- Page URL I tried returned 404 (fetcher), so Status: not loaded; function documented in the e-filing help FAQ. Works without login: enter DIN + mobile number, validate with OTP; or PAN, document type, assessment year, issue date and mobile (AY 2011-12 onward). Success message if issued by ITD, otherwise "No record found for the given criteria". All ITD communications since 1 Oct 2019 must carry a DIN. — [e-filing help via search](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/authenticate-noticeorder-issued-itd), [Quicko guide](https://learn.quicko.com/authenticate-notice-order-issued-by-itd)
- OTP to the user's own mobile means it cannot be automated by Parakh; build as a deep link plus extraction of the DIN from the forwarded notice (the agent can check DIN format and presence, not validity).

**10. CBIC DIN verification**
- Documented: recipient enters DIN in the "Verify CBIC-DIN" window (DIN + captcha) and sees issuing office and generation date; DIN mandatory on CBIC communications from 24 Dec 2019. Source URLs conflict (cbic.gov.in, cbicddm.gov.in, esanchar.cbic.gov.in); Circular 252/09/2025-GST (23 Sep 2025) makes the eOffice issue number the DIN; a utility at verifydocument.cbic.gov.in is mentioned by one blog only. Status: DOC, not tested; live URL unconfirmed. — [Taxo](https://taxo.online/latest-news/27-01-2025-finance-ministry-asks-taxpayers-to-verify-summons-first-on-cbic-site/), [VJM Global](https://www.vjmglobal.com/blog/document-identification-number-din-quoted-all-communications-cbic), [GST Gyaan](https://gstgyaan.com/quoting-of-din-on-documents-issued-by-officers-of-cbic)
- Captcha-gated: deep link only.

**11. GST portal search taxpayer (GSTIN)**
- Pre-login search needs GSTIN/UIN/PAN/temp ID plus captcha; shows legal name, trade name, registration date, constitution; no name search. — [GST tutorial](https://tutorial.gst.gov.in/userguide/taxpayersdashboard/Search_Taxpayer_manual.htm). Status: DOC, not tested.
- Third-party scrapers (e.g. an Apify actor) advertise captcha-solving. Do not use; this circumvents the captcha. A GSTIN can be format/checksum-validated offline (15 chars, check digit) as a free first pass, but passing the checksum does not mean active (noted by [RegisterKaro](https://www.registerkaro.in/gst-number-search), a commercial site).

**12. eCourts**
- https://services.ecourts.gov.in/ecourtindia_v6/ : Status: LOADED. CNR search (16 alphanumeric chars, no spaces/hyphens, example MHAU019999992015), image captcha required (audio option), other search by case number/party/advocate. No dedicated terms-of-use page listed (Copyright, Hyperlinking Policy, Disclaimer, Accessibility). No API mentioned; mobile app exists. — [eCourts](https://services.ecourts.gov.in/ecourtindia_v6/)
- High court services: https://hcservices.ecourts.gov.in/ (captcha too, per search result). SMS status by CNR to 9766899899 (blog claim, unverified). A third-party Apify actor auto-solves captcha; do not use. — [Vikaspedia](https://en.vikaspedia.in/viewcontent/e-governance/online-legal-services/how-to-check-court-case-status-online-in-india-a-complete-guide-to-ecourts-cnr-number-case-number-and-case-history?lgn=en)
- Parakh use: extract CNR from a forwarded "court notice", validate format, deep-link the user to the official page. Official API: NF.

**13. PIB Fact Check**
- https://factcheck.pib.gov.in/ : fetch returned a 401 "Unauthorized" OTP/email login page with captcha (content not visible to my fetcher). Footer said last updated 31 Oct 2026. Status: not usefully loaded. No RSS found on the page or via search. Telegram channel t.me/PIB_FactCheck linked. Sitemap factcheck.pib.gov.in/sitemap.aspx exists per footer, not opened. — [PIB Fact Check](https://factcheck.pib.gov.in/), [PIB FAQ](https://www.pib.gov.in/FAQ_fact.aspx)
- Official X account handle is @PIBFactCheck (from background knowledge; not verified here). X API is paid, so not a viable 48-hour source; treat the Telegram channel and the website as manual deep links.

**14. I4C / cybercrime.gov.in suspect registry**
- https://cybercrime.gov.in fetch returned only the title "Cybercrime Portal": Status: not usefully loaded. Secondary sources say the public NCRP Suspect Repository lets citizens search mobile numbers, emails, bank accounts and UPI IDs; the wider I4C Suspect Registry (launched 10 Sep 2024) is shared with banks and is not public; helpline 1930. — [The420](https://the420.in/indias-cyber-crackdown-rs-2889-crore-saved-as-i4c-tracks-20-lakh-fraud-accounts/), [Policy Edge](https://www.policyedge.in/p/ministry-of-home-affairs-strengthening-the-indian-cyber-crime-coordination-centre-i4c). Status: DOC.
- No public API found. Treat as a deep link; the registry's own caveat is that "flagged" is not "convicted", so Parakh should phrase results as "reported", not "scammer".

**15. UGC fake universities**
- https://www.ugc.gov.in/ : fetch showed maintenance/timeout messages; menu has "Fake Universities" link; list contents not loaded. Status: not usefully loaded. News: latest list Feb 2026 names 32 institutions (Delhi 12, UP 4); earlier counts 22 and 24; official list is a PDF per secondary sources. — [Kashmir Life](https://kashmirlife.net/ugc-identifies-32-fake-universities-across-india-states-asked-to-take-legal-action-446704/), [Shiksha](https://www.shiksha.com/humanities-social-sciences/articles/list-of-fake-universities-published-by-ugc-blogId-4044). Best 48-hour approach: download the PDF once manually, hand-curate 32 rows into a CSV with source link and date.

**16. data.gov.in / API Setu**
- Searches found no API Setu or data.gov.in entries for any of the above (MCA, GST, SEBI, AMFI). NF. data.gov.in had ~4,015 APIs as of 2019 per a MediaNama report, but nothing identified relevant. — [MediaNama](https://www.medianama.com/2019/09/223-fintech-report-open-data-land-records/). Check https://apisetu.gov.in/ by hand; most API Setu APIs need organisation onboarding and are issuer/consent-based (background knowledge, unverified).

### Inferences
- Only SEBI intermediaries, AMFI, IRDAI lists and eCourts (form only) are confirmed reachable plain pages; of those only SEBI has a stated as-of date.
- A realistic MVP: local SQLite of SEBI IA/RA/broker rows (scrape politely or manual export), RBI alert list and NBFC list (manual download), UGC list (manual), IRDAI lists (manual), plus deterministic validators (GSTIN checksum, CIN pattern, CNR format, DIN format, UPI "@valid" suffix) and deep links for captcha/OTP tools.

### Gaps
- Live format and as-of date of RBI NBFC list, RBI DLA directory, Sachet, payment system operator list (all RBI URLs returned 418 to my fetcher).
- Whether NSE/BSE/MCA pages work from an Indian IP (403/timeout from my side).
- Exact URL of SEBI Check portal and of a consolidated SEBI debarred-entities register; other SEBI intermediary type IDs.
- Terms of use text for any site (not read for SEBI, AMFI, IRDAI, RBI, eCourts beyond the policy-page list).
- Official CBIC DIN verification URL; official PIB Fact Check RSS (not found); public NCRP suspect-search URL and its captcha/OTP behaviour.

## Captcha, login, OTP, rate limits, robots.txt and terms

### Takeaway
Captcha or OTP gates: eCourts (captcha), GST search (captcha), CBIC DIN (captcha, documented), IT notice authenticate (OTP to user's mobile), PIB fact check site (OTP login), SEBI login panel (captcha, search itself not). These are meant for humans; Parakh should deep-link, not automate. Only SEBI robots.txt was read; it permits the intermediary pages.

### Cited Findings
- SEBI robots.txt allows everything except js/css directories — [SEBI](https://www.sebi.gov.in/robots.txt)
- eCourts CNR search requires image/audio captcha — [eCourts](https://services.ecourts.gov.in/ecourtindia_v6/)
- IT notice authentication requires an OTP to the entered mobile number — [Quicko](https://learn.quicko.com/authenticate-notice-order-issued-by-itd)
- GST pre-login search requires captcha — [GST tutorial](https://tutorial.gst.gov.in/userguide/taxpayersdashboard/Search_Taxpayer_manual.htm)
- Rate limits: none stated on any page I read.

### Inferences
- Where there is a captcha or OTP, the safe design is "Parakh extracts the identifier and hands the user a link", which is also faster to build.

### Gaps
- robots.txt for AMFI, IRDAI, RBI, NSE, BSE, MCA, eCourts not read (RBI blocked; others not attempted).
- No site terms of use were read; get these checked by a human before scraping.

## Update frequency and "as of" dates

### Takeaway
SEBI shows "as on Oct 30, 2026" on its intermediary page (fresh); others show none or unverified.

### Cited Findings
- SEBI intermediaries page: "Registered intermediaries as on date Oct 30, 2026" — [SEBI](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13)
- AMFI distributor page: no as-of date shown — [AMFI](https://www.amfiindia.com/locate-distributor)
- SEBI orders listing: no last-updated stamp, per-entry dates only — [SEBI orders](https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=6)
- RBI Alert List updated irregularly (Sep 2022, Jun 2023, Nov 2023, Oct 2024, Nov 2025) — [Outlook Money](https://www.outlookmoney.com/amp/story/invest/check-rbis-updated-alert-list-for-unauthorised-forex-trading-platforms)
- UGC fake list: reissued periodically (22, 24, then 32 in Feb 2026 per news) — [Kashmir Life](https://kashmirlife.net/ugc-identifies-32-fake-universities-across-india-states-asked-to-take-legal-action-446704/)

### Inferences
- Parakh should store and display its own "fetched on" timestamp for every source, and word negatives as "not found in list fetched on <date>".

### Gaps
- Update cadence of IRDAI, AMFI, RBI NBFC and DLA lists not established.

## Test summary (31 Oct 2026)

- Loaded in my test: SEBI intermediaries; SEBI orders listing; SEBI robots.txt; AMFI locate-distributor; IRDAI homepage; eCourts services home.
- Loaded but unusable/partial: PIB Fact Check (401 login page); UGC (maintenance/timeout text); cybercrime.gov.in (title only).
- Failed: RBI x3 (418), BSE (403), MCA master data (403), NSE (timeout), IT e-filing help URL (404 for my guessed path), sebicheck.sebi.gov.in (DNS not found).
- Documented but not tested: SEBI Check, RBI Alert List/DLA directory, CBIC DIN, GST search, NCRP suspect search, UGC PDF.
- Not found: official public APIs for most registries; PIB RSS; API Setu/data.gov.in entries for these sources.
- Ethics: no captcha-solving or terms-bypassing approaches recommended; third-party captcha-solving scrapers found in search should be avoided.
