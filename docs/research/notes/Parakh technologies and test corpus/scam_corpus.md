# Parakh test corpus: real Indian scam messages, fake notices and genuine reference notices

Compiled 1 Nov 2026. Every record carries a FIDELITY tag so the test harness knows how much to trust the wording:
- VERBATIM = text copied character-for-character from the source (line-wraps from PDFs joined; nothing else changed).
- PARTIAL = some phrases are verbatim (in quotes), the rest is the source's description.
- PARAPHRASED = the source only describes the message; nothing here should be fed to the app as if it were the original wording.

SOURCE TYPE: "Official" = published by the regulator, court or agency itself (SEBI, NSE, ED, Supreme Court, CBDT). "News/PIB" = a news outlet quoting a PIB Fact Check post (PIB posts are X images and could not be fetched directly), or quoting a police advisory. Phone numbers, PANs and e-mail IDs of private individuals that appear unmasked in SEBI orders have been deliberately left out; masking is kept exactly as published.

Roughly 45 records follow (about 36 scam or fake-notice records plus 9 genuine reference items). Items marked "snippet-only" were seen in search-result summaries but the page itself was not opened; treat them as leads.

## 1. Fake investment adviser, stock-tip and WhatsApp/Telegram trading-group messages

### Takeaway
The best verbatim material is in SEBI's own enforcement orders (they reproduce Telegram channel text) and SEBI PR 65/2026 (reproduces the "new group" invitation). I found no official advisory that publishes a fake SEBI registration NUMBER (INH/INA digits); the fakes in the record claim "SEBI REGD." in words, or circulate a forged certificate for an entity that is not on SEBI's list.

### Cited Findings

**INV-1 | SEBI PR 65/2026 "new group" invitation | VERBATIM | Official | 22 Oct 2026**
- Text (SEBI says members receive this "usually from a new number" after a fraudulent group is suspended): "Due to Social Media Platform's risk control measures, our previous group has been banned. This new group will provide daily recommendations of quality stock information and trading guidance. Please join the group."
- SEBI's description of the operators: "unregistered persons ... offering stock tips and trading calls to investors through invitation-only WhatsApp groups ... mostly using overseas WhatsApp numbers ... share unauthorised buy/ sell calls in the name of free investor education"; other members "post false claims of profit and praise the `expert'" (SEBI calls this astroturfing).
- Identifiers: none in the message. SEBI's verification links: https://www.sebi.gov.in/intermediaries.html and https://investor.sebi.gov.in/Investor-support.html
- Expected Parakh verdict: no registry match for the unknown sender, group-invite pattern. — [SEBI PR No.65/2026, 22 Oct 2026](https://www.sebi.gov.in/sebi_data/attachdocs/oct-2026/1792675550417.pdf)

**INV-2 | "OWNED AND CONTROLLED BY NISM AND SEBI REGD. TEAM" Telegram channel | VERBATIM | Official (SEBI order) | 27 Mar 2026**
- Order ref QJA/MN/NRO/NRO-DIV-I/32304/2025-26, "Mr. Yash Garg (Proprietor of Yash Trading Academy)". SEBI found he was running a fake "Yash Trading Academy" and "claiming it to be a SEBI registered intermediary".
- Channel text quoted in the order: "THIS CHANNEL IS OWNED AND CONTROLLED BY NISM AND SEBI REGD. TEAM We provide: Banknifty Calls Portfolio Management Services Trading and Techniques Classes Live Trade with Yash Daily Monthly: 10,000/- for today only"
- Other claims quoted from the same channels: "Guaranteed profit"; "One day account handling charges- Rs 1000"; "Minimum Investment Required 20,000 Profit Ratio 50/50 Charges 1000 per day"; "100% profit guaranteed otherwise full refund without any questions"; "Monthly 11000 profit ratio 50/50"; "Yearly 75000 profit ratio 80/20". A second channel "also claimed to be 'SEBI registered'" and charged "Monthly charges Rs.1,000 ... Yearly charges15000".
- Identifiers as published: Telegram channel "Yash Trading Academy" (211.4k subscribers) / "YTA Premium"; website www.yashtradingacademy.com; WhatsApp link https://api.whatsapp.com/send?phone=91931xxxx200 (masked by SEBI). PAN omitted here.
- Expected verdict: "SEBI REGD." claim, no registration number, guaranteed returns, account handling = unregistered activity. — [SEBI order, 27 Mar 2026](https://www.sebi.gov.in/sebi_data/attachdocs/mar-2026/ORDER_1774618746.pdf)

**INV-3 | "Intraday Jackpot" / "Professional Day Trading Institute" Telegram channels | VERBATIM | Official (SEBI order) | 30 Apr 2026**
- Order ref QJA/MN/ERO/ERO-OTHER/32401/2026-27 (Akshay Kumar and five others), "unregistered investment advisor/research analyst activities".
- Channel descriptions quoted: "Highly Safe Call (Daily 5K to 10K Earn)"; "8 to 10 sure shot positional trades in a month with 100% to 200% returns."; "Sure shot daily 200 points"; "Index Low Premium Call + Stock Options Only Jackpot Calls".
- Pinned message quoted: "If you want to convert your loss into profit, then join now our premium service https://t.me/Rahultrade1 Pay here to Join HNI (https://cosmofeed.com/vig/643d392830ae100021fa23a1) Pay here to Join Index (https://cosmofeed.com/vig/640d90410b82780020c56088)"
- Identifiers as published: channel t.me/BANKNIFTY_NIFTY_INTRADAY_JACKPOT (created 19 Sep 2019); website https://intradayjackpot.net (now defunct). The order also prints an individual's unmasked mobile number and e-mail; deliberately not copied here.
- Expected verdict: unregistered adviser, assured-return language. — [SEBI order, 30 Apr 2026](https://www.sebi.gov.in/sebi_data/attachdocs/apr-2026/ORDER_1777529838.pdf)

**INV-4 | "We are Not SEBI REGISTERED" disclaimer channel (paid Telegram/WhatsApp tips) | VERBATIM | Official (SEBI order) | 28 Nov 2025**
- Order ref QJA/SS/ERO/ERO-OTHER/31816/2025-26, M/s Satyam Shivam Sundaram Trading. Quoted channel description of "Nifty Bank Nifty Stock Options": "This channel is for stock market study and learning purposes only. We are Not SEBI REGISTERED. You are strictly forbidden to take my calls as advisory. Fees are Non Refundable. WhatsApp: XXXXXX0268"
- Channels named: "Nifty BankNifty Stock Options", "Premium Group Nifty BankNifty Options", "Premium Group Stock Equity Options", "Premium Group of Investment". Telegram id "Stock_Analyzer". Pricing from complainants' screenshots: Rs. 9999/- yearly, 24999/- lifetime. Payment-link message texts seen: "1 Month Premium Membership", "Lifetime Premium Membership". SEBI ordered a Rs 3.17 crore refund and Rs 15 lakh penalty (per Moneylife).
- Expected verdict: this is the "educational-only disclaimer" evasion; unregistered entity. — [SEBI order, 28 Nov 2025](https://www.sebi.gov.in/sebi_data/attachdocs/nov-2025/1764324302510_4.pdf); penalty figures from [Moneylife](https://moneylife.in/article/satyam-shivam-sundaram-trading-case-sebi-orders-317-crore-refund-imposes-15-lakh-penalty-on-unregistered-advisers/78984.html) (snippet-only)

**INV-5 | "JO HAMBRO" WhatsApp group with forged SEBI certificate | PARTIAL | Official (NSE press release) | 12 Sep 2024**
- NSE: a WhatsApp group "JO HAMBRO" was "luring retail investors to get discounted prices of shares ... after closure of market"; money collected "under the garb of 'Seat Trading Account'"; the entity "Lazzard Asset Management India is misrepresenting itself as a registered stock broker with the Securities and Exchange Board of India ('SEBI') using a forged SEBI registration certificate."
- NSE's finding, verbatim: "no entity by the name of Lazzard Asset Management India is registered with SEBI as a stock broker. The forged SEBI registration certificate circulated in the WhatsApp group is entirely fabricated and illegitimate."
- Note the spelling: NSE's release says "Lazzard"; Business Standard's headline says "Lazard". Registration number on the forged certificate was not published.
- Expected verdict: entity name absent from SEBI intermediary list. — [NSE press release, 12 Sep 2024](https://nsearchives.nseindia.com/web/sites/default/files/2024-09/PR_cc_12092024_0.pdf); [Business Standard, 13 Sep 2024](https://www.business-standard.com/amp/finance/personal-finance/nse-warns-about-another-whatsapp-group-scam-lazard-asset-management-india-124091300237_1.html)

**INV-6 | Fake "Institutional Account" / FPI sub-account groups | PARTIAL | Official (joint exchanges press release) | 23 Aug 2024**
- Exchanges say persons on "WhatsApp Groups, Telegram Channels, Facebook, Instagram Channels" are "falsely claiming to offer trading opportunities through Foreign Portfolio Investment (FPI) or Foreign Institutional Investor (FII) Sub-accounts or Institutional Accounts with special privileges impersonating reputed financial institutions, showcasing fake certificates purportedly issued by SEBI/ Exchanges."
- Lures listed: groups "which have the features of trading in UPPER CIRCUIT stocks, Block Deals at discounted prices, preferential allotment in IPOs"; "assured/guaranteed returns"; "Institutional account" with no demat account; fake trading apps; asks to "transfer funds to third-party bank accounts". Report via Chakshu on www.sancharsaathi.gov.in, 1930, www.cybercrime.gov.in.
- No message text published. — [Joint exchanges press release, 23 Aug 2024](https://nsearchives.nseindia.com/web/sites/default/files/2024-08/PR_cc_23082024_0.pdf)

**INV-7 | Fake SEBI letters demanding STT to "release funds" | PARAPHRASED | Official release via news | NSE press release 24 Feb 2026**
- Per Angel One's write-up (original NSE release not opened): scammers circulate forged SEBI letterheads (logo, seal) claiming investors "must pay STT under the Finance Act, 2004, to release pending funds"; NSE says neither SEBI nor exchanges issue letters demanding direct tax payments for fund release. Also reported by [5paisa, 5 Jun 2025](https://www.5paisa.com/index.php/news/sebi-issues-urgent-warning-against-fraudulent-letters-impersonating-officials) (earlier wave: fake SEBI notices demanding fines, "exclusive" investment deals, FPI links).
- Source: [Angel One, 26 Feb 2026 (updated 9 Mar 2026)](https://oga-prod.angelone.in/news/personal-finance/nse-issues-public-warning-on-fake-sebi-stt-notices-urges-investors-to-stay-alert)

**INV-8 | "VIP Group / Free Trading Courses" WhatsApp invitations | PARTIAL | Official | SEBI PR 27/2025, 21 May 2025**
- SEBI: entities "send unsolicited invitations in the form of links to join WhatsApp Groups (like VIP Group, Free Trading Courses etc.)", "impersonate SEBI registered intermediaries, well known public figures, celebrities, CEOs/ MDs", show "fake testimonials of achieving huge profits, from other group members". No message text. — [SEBI PR No.27/2025](https://files.hdfcfund.com/s3fs-public/inline-files/2025-05-21-SEBI%20Press%20Release%20%282%29.pdf) (copy hosted by HDFC Mutual Fund)

**INV-9 | INDmoney impersonation groups with forged SEBI certificates | PARAPHRASED | News on a court order | 7-8 Aug 2025**
- Delhi High Court (Indmoney Tech Private Limited & Anr. v. Ashok Kumar And Ors., CS(COMM) 744/2025, 2025 LiveLaw (Del) 945) granted a john doe injunction. Plaintiffs say defendants made "fake WhatsApp and Telegram groups, using names of well-known financial advisors, and even impersonating Plaintiffs' founder", promising returns "through block trading, IPOs, and stock tips", and circulated "forged SEBI registration certificates, fake agreements, and counterfeit loan documents". — [LiveLaw, 8 Aug 2025](https://www.livelaw.in/amp/high-court/delhi-high-court/defrauding-unsuspecting-users-delhi-high-court-grants-john-doe-injunction-over-trademark-infringement-of-share-market-app-indmoney-300291)

### Inferences
- INV-1 to INV-4 give four distinct, SEBI-attested text patterns the app can be tested on: group-migration invite, "SEBI REGD." claim without number, guaranteed-profit language, and the "not SEBI registered / educational only" disclaimer.
- For tests that need a fake registration number, the corpus has none published; a synthetic INH/INA-style number must be constructed and labelled synthetic.

### Gaps
- No official advisory found that prints a specific fake INH/INA registration number. The NSE case (INV-5) mentions a forged certificate but not its number.
- NSE's 24 Feb 2026 release itself (INV-7) was not opened; wording of the fake letter is not available.
- Snippet-only leads, not opened: Delhi HC orders for Moneycontrol (Dec 2025), Aditya Birla Sun Life AMC (Jul 2026), Peak XV/Sequoia (2024); Telangana Today "Hyderabad techie loses Rs 37 lakh in fake SEBI analyst investment scam" (updated 29 Jun 2026): https://telanganatoday.com/hyderabad-techie-loses-rs-37-lakh-in-fake-sebi-analyst-investment-scam

## 2. Illegal loan apps and fake "RBI-approved" lender claims

### Takeaway
I found official warnings and named apps but no verbatim loan-app SMS or "RBI approved" pitch. The usable test inputs are app names (a Himachal Police list of 15) and RBI's statement that unauthorised apps falsely claim RBI registration. Genuine reference: RBI's Digital Lending Apps directory (live 1 Jul 2025).

### Cited Findings

**LOAN-1 | RBI warning on apps falsely claiming RBI registration | PARAPHRASED | Official statement via All India Radio | date not shown on the page (see Gaps)**
- Reported: RBI "has identified several unauthorized digital lending apps and other financial service providers claiming to be registered with the RBI as Non-Banking Financial Companies (NBFCs), digital lending apps, or Payment System Operators"; fraudsters use "fake letterheads and email addresses, impersonating RBI employees" and lures such as "lottery winnings, fund transfers, foreign remittances, and government schemes". RBI "does not maintain any account in the name of individuals, companies, trusts in India to hold funds for disbursal" and does not email or SMS lottery awards. — [Akashvani News (AIR)](https://www.newsonair.gov.in/rbi-issues-warning-against-fraudulent-activities-involving-misuse-of-its-name/)

**LOAN-2 | Himachal Police State Cyber Cell list of 15 fraudulent loan apps | PARTIAL (names verbatim) | State police via news | 26 May 2025**
- Apps listed: Rapid Rupee, CashBus, Go Cash, Rupee Bazaar, Snaplt Loan, Easy Loan, Dhana Dhan Loan, CreditZilla, Flash Loan, Mera Loan, Quick Cash, Rupee King, Cash Tree, CashLion and Instant Loan Pro. Per the report: "The CashBus app has no RBI licence"; "Go Cash is charging fake processing fees and misusing contact data"; "Snaplt Loan is an unverified lender and has been flagged for public shaming". Quote attributed to DIG Cybercrime Mohit Chawla. — [The Tribune, 26 May 2025](https://www.tribuneindia.com/news/himachal/fraudulent-apps-offering-easy-loans-a-major-threat/amp)

**LOAN-3 | "Rup Credit App" harassment case | PARAPHRASED | News on an FIR | 20 Nov 2025**
- FIR: a 46-year-old Bengaluru woman "downloaded the Rup Credit App on November 5 and availed a loan of Rs 2,000"; was made to pay Rs 5,734, then callers "demanded Rs 8,000 and sent her morphed photographs". — [Deccan Herald, 20 Nov 2025](https://www.deccanherald.com/amp/story/india%2Fkarnataka%2Fbengaluru%2Fwoman-faces-threats-with-morphed-images-over-rs-2000-loan-in-bengaluru-3803954)

### Inferences
- App-name matching against RBI's DLA directory is the natural registry check; every app in LOAN-2 and LOAN-3 should fail a "regulated entity behind the app" lookup unless the directory says otherwise (not verified here).

### Gaps
- No verbatim loan-app SMS, WhatsApp pitch or "RBI approved" claim text was found in any official source.
- LOAN-1 date unconfirmed: the page has no date and RBI's own site blocked the fetch. A search-engine summary suggested August 2024, which I could not verify.
- Snippet-only leads: Gurugram arrests of 9 loan-app extortionists incl. "Finsara" app (Daily Pioneer, 2024; page now 404), Hyderabad police case where apps allegedly "sent fake CBI legal notices" (The News Minute, undated).

## 3. Digital arrest and fake police, CBI, ED or court summons and warrants

### Takeaway
The strongest primary material is the Supreme Court's 17 Oct 2025 suo motu order, which lists the forged documents (with a file number) used on an Ambala couple, and ED's 8 Oct 2025 press release on fake summons. No verbatim WhatsApp/call script was published by any official source I could open.

### Cited Findings

**DA-1 | Forged "Freeze Order", "Arrest Order", "Surveillance Order" shown to Ambala couple | PARTIAL | Official (Supreme Court) | 17 Oct 2025**
- Supreme Court, Suo Motu Writ Petition (Criminal) No(s).3/2025, "In re: Victims of Digital Arrest related to Forged Documents". Callers impersonated "CBI officers, ED officials and judicial authorities through telephone and video calls" and "displayed forged orders of the Supreme Court through WhatsApp and video conferencing"; victims transferred Rs.1,05,50,000 (scam period 03.09.2025 to 16.09.2025).
- Forged documents listed by the Court: (i) "Freeze Order" dated 03.09.2025 "bearing reference number F.No. EC/IRA/BZO-I/02/2025, purportedly issued under the Prevention of Money Laundering Act, 2002"; (ii) "Arrest Order" dated 03.09.2025 "bearing the stamp and designation of an officer of the Directorate of Enforcements, Mumbai along with another Court stamp"; (iii) "Surveillance Order" with forged judicial signatures; (iv) "fictitious proceedings before the Bombay High Court". FIRs: No.76/2025 and No.77/2025, Cyber Crime Branch, Ambala.
- Expected verdict: reference number F.No. EC/IRA/BZO-I/02/2025 is a known forged ED-style reference; ED does not arrest digitally. — [Supreme Court order, 17 Oct 2025](https://api.sci.gov.in/supremecourt/2025/59769/59769_2025_2_7_65003_Order_17-Oct-2025.pdf)

**DA-2 | Fake ED summons and "digital arrest" arrest orders | PARAPHRASED (official statement) | Official (ED) | 8 Oct 2025**
- ED: "certain 'unscrupulous' persons (conman) have sent summons to individuals with the motive of cheating or extortion. These fake summons are often similar to the genuine summons issued by ED". Genuine summons format is in GEN-1. — [ED press release, 08.10.2025](https://enforcementdirectorate.gov.in/sites/default/files/latestnews/Press_release_fake%20summons-08.10.2025%201.pdf). Finance Ministry repeated the warning on 20 Nov 2025: [The Tribune](https://www.tribuneindia.com/news/finance-ministry-warns-public-against-fake-ed-summons)

**DA-3 | Noida "parcel to Iran" fake ED notices | PARTIAL | News (PTI) | 25 Nov 2024 (call on 8 Aug 2024)**
- Per PTI: "The fraudsters claimed that a parcel is being sent from Mumbai to Iran in her name containing five passports, two debit cards, two laptops, 900 US dollars and 200 grams of narcotics"; they sent "a complaint via WhatsApp", asked for Rs 34 lakh, video-called "on Skype with the video switched off", and sent "two notices of Enforcement Directorate (ED)". Gautam Buddha cyber crime police station registered a case. — [Deccan Herald / PTI, 25 Nov 2024](https://www.deccanherald.com/amp/story/india%2Fnoida-woman-duped-of-rs-34-lakh-gets-fake-ed-notices-in-case-of-digital-arrest-3290232)

**DA-4 | I4C "Don't Panic" advisory (the official counter-message, not a scam text) | VERBATIM quote | Official (I4C) via news | issued Sat 5 Oct 2024**
- "Don't Panic, Stay Alert. The CBI/Police/Custom/ED/Judges DO NOT arrest you on video call," Report to 1930 or www.cybercrime.gov.in. — [The Tribune, 7 Oct 2024](https://www.tribuneindia.com/news/india/cbi-ed-dont-nab-via-video-calls-advisory-to-curb-digital-arrest/)

**DA-5 | TRAI impersonation: disconnection and "digital arrest" calls and messages | PARAPHRASED | Official (TRAI advisory) via law-news site | 6 Aug 2025**
- TRAI flagged "Calls or messages falsely claiming that a mobile number will be disconnected due to KYC issues unless immediate action is taken", and callers who "impersonate TRAI or law enforcement officials" using "fake legal documents, forged identities, and threats of arrest or account freezing". TRAI "does not initiate communication with customers regarding mobile number disconnection". — [SCC Online blog, 8 Aug 2025](https://www.scconline.com/blog/post/2025/08/08/trai-issues-advisory-on-frauds-misusing-trais-identity/)

**DA-6 | Fake I4C "court notice" e-mail | PARAPHRASED | News/PIB | PIB tweet 23 Aug 2023 (older than the 2024-26 window)**
- A purported I4C letter/e-mail from an administrator named "Rajesh Kumar" says IP-address "cyber-infiltration" was detected and demands a reply within 24 hours. PIB Fact Check: "This letter is fake. No such letter has been issued by any organization under GOI". — [Factly, 25 Aug 2023](https://factly.in/this-purported-letter-of-the-indian-cyber-crime-coordination-centre-i4c-accusing-individuals-of-cybercrimes-is-fake)

### Inferences
- DA-1's reference number and document titles are the only machine-checkable identifiers in this category; the rest is pattern matching (video-call arrest, "parcel containing narcotics", Skype).

### Gaps
- No verbatim WhatsApp text or call script from an official source. Several news pieces (Mumbai "CBI letterhead" notice, Moneylife Nov 2025 case list with "forged warrants") describe forged documents without reproducing them.

## 4. Fake income tax, GST and customs notices

### Takeaway
Best verbatim items: a PIB-flagged refund e-mail (Jul 2025), a fake refund SMS template (PIB, 2023, older), and Moneylife's detailed breakdown of a 2026 "Important Message" phishing e-mail with a made-up ITBA-style reference. No GST-specific fake notice turned up.

### Cited Findings

**TAX-1 | "Assessment Order" AY 2025-26 demand e-mail (Rs 8,38,700) | PARTIAL | News quoting PIB Fact Check | PIB post 10 Mar 2026**
- PIB tweet text as quoted: "An email is circulating online claiming to be issued by the Income Tax Department for Assessment Year 2025–26. The email further asks recipients to pay a tax demand and directs them to click a link to view an 'Assessment Order.'"
- Identifiers as published: sender domain @jcom.zaq.ne.jp; link https://wwtax.icu; reference "Income Escapement 805859921"; sections 143(2) and 143(3); amount Rs 8,38,700. — [StudyCafe, 10 Mar 2026](https://studycafe.in/fake-income-tax-notice-demanding-rs-8-38-lakh-circulating-taxpayers-advised-to-stay-caution-412806.html)

**TAX-2 | "Important Message" e-mail with ITBA-style reference | PARTIAL | News (Moneylife) | undated on page; context suggests late Aug-Sep 2026**
- Subject: 'Income Tax Department | Important Message'; reference number ITBA/AST/F/17/2025-26/1035917840; tag "AY25-26"; mentions 'Information u/s 143(1) — Processing of Return'; button 'View Message on e-Filing Portal'; destination api.teledema.scoding.com/storage/foi/index.html. The sender domain is masked in the article. Moneylife also describes a separate e-mail threatening prosecution for "tax irregularities" under Section 271(1)(c) with a 72-hour deadline (second-hand, from TaxGuru). — [Moneylife](https://www.moneylife.in/article/fraud-alert-that-imp-message-from-the-income-tax-department-could-be-a-trap/81428.html)

**TAX-3 | "Rs 6,000 income tax payment" notice | PARAPHRASED | News/PIB | Outlook Money 17 Aug 2026; StudyCafe 20 Aug 2026**
- PIB Fact Check flagged a circulating notice seeking Rs 6,000 as fake and phishing; exact wording and any link were not published in either article. — [Outlook Money](https://www.outlookmoney.com/tax/income-tax-notice-seeking-rs-6000-is-fake-heres-what-taxpayers-should-do); [StudyCafe](https://studycafe.in/got-a-rs-6-000-income-tax-payment-alert-pib-fact-check-calls-it-a-phishing-scam-426613.html)

**TAX-4 | "Manually verify" refund e-mail (Rs 60,000) | VERBATIM (as quoted by the outlet) | News/PIB | 22 Jul 2025**
- "This is an official notification regarding your Income Tax Refund for Assessment Year 2024-25. Amount eligible: Rs 60,000…all refunds above Rs 25,000 require recipient confirmation to prevent unauthorised payouts and protect taxpayers." Business Standard says the PIB Fact Check Unit flagged this e-mail and that it "typically reads" so; the department says report to webmanager@incometax.gov.in and incident@cert-in.org.in. — [Business Standard, 22 Jul 2025](https://www.business-standard.com/amp/finance/personal-finance/tax-refund-scam-alert-don-t-fall-for-that-manual-verification-email-125072200446_1.html)

**TAX-5 | "Approved tax refund of Rs 15,490" SMS template | VERBATIM | News quoting PIB Fact Check | 3 Aug 2023 (older than the window, a recurring template)**
- "You have been approved an tax refund of Rs 15, 490/- the amount will be credited to your account number 5xxxxx6755. If this is not correct please update your bank account information by visiting the link below." PIB tweet: "A viral message claims that the recipient has been approved for an income tax refund of Rs 15,490. This claim is fake. @IncomeTaxIndia has not sent this message." — [Outlook Money, 3 Aug 2023](https://www.outlookmoney.com/news/did-you-just-get-the-income-tax-refund-message-it-s-a-bait-clarifies-i-b-ministry-news-307861)

**TAX-6 | "Customs held your parcel" calls, SMS and e-mails (and the "press 9" IVR) | PARAPHRASED | Official (CBIC) via news | CBIC campaign 18 Jun 2024; PIB clip reported 20 Aug 2024**
- CBIC: "Fraudsters posing as Courier officials/staff contact via calls, text messages or emails claiming that Customs have held a package or parcel and requires payment of Customs duties or taxes before it can be released"; "Indian Customs officers never contact the general public via phone, SMS, or e-mail for payment of duty in private accounts." CBIC advises verifying any communication by its DIN on the CBIC website. In PIB's clip a pre-recorded message says there is an issue with a parcel and prompts "press 9". A Kerala woman lost Rs 12 lakh after an initial Rs 15,000 "customs duty" demand. — [TaxGuru (CBIC campaign), 18 Jun 2024](https://taxguru.in/custom-duty/cbic-mounts-campaign-frauds-committed-indian-customs.html); [Digit, 20 Aug 2024](https://www.digit.in/news/general/kerala-woman-duped-of-rs-12-lakh-in-customs-scam-government-reveals-how-this-fraud-works.html)

### Inferences
- TAX-4 and TAX-5 are the cleanest input strings. TAX-2's ITBA-style reference tests whether the app checks a DIN against the real portal rather than trusting the format (see GEN-2).

### Gaps
- No fake GST notice found in an official or news source I opened.
- TAX-3 has no original wording; TAX-2 page date missing; the Rs 8.38 lakh e-mail's PIB post itself (X) could not be opened.

## 5. Fake bank KYC and account-block messages

### Takeaway
Most PIB-flagged items in 2026 push an APK or a link under an SBI, RBI or BSNL name. Verbatim text exists for the 2024 BSNL notice tweet and a 2023 HDFC SMS; the 2026 items are described, with a few quoted phrases.

### Cited Findings

**KYC-1 | "SBI KYC AADHAR UPDATE" APK message | PARTIAL | News (IANS) quoting PIB Fact Check | 22 Mar 2026**
- Message addresses "Dear SBI customer", says the YONO account "will be blocked due to incomplete Aadhaar details", and tells the user to download an APK titled "SBI KYC AADHAR UPDATE". SBI's X handle confirmed it does not require APK downloads; report phishing to report.phishing@sbi.co.in. — [IBTimes India / IANS, 22 Mar 2026](https://www.ibtimes.co.in/pib-flags-fake-sbi-yono-message-urging-aadhaar-update-warns-customers-against-phishing-scam-899756)

**KYC-2 | Fake "RBI" WhatsApp message with APK, "linked to suspicious transactions" | PARAPHRASED | News quoting PIB | 12 Jun 2026**
- Claims the recipient's bank account "has been linked to suspicious transactions and may be blocked" and attaches an APK. Per PIB, RBI uses WhatsApp only from two blue-tick numbers (see GEN-5). — [Angel One, 12 Jun 2026](https://oga-prod.angelone.in/news/personal-finance/rbi-whatsapp-scam-alert-pib-warns-users-against-fake-messages-claiming-bank-account-blockage)

**KYC-3 | Fake RBI voicemail: credit-card fraud, account will be blocked | PARAPHRASED | News quoting PIB | date not on the page (a search summary placed it Nov 2025, unverified)**
- Viral voicemail "claims that the account will be blocked due to the involvement of a person's credit card in fraudulent activity"; PIB: "false and a scam". — [Akashvani News](https://www.newsonair.gov.in/pib-fact-check-warns-of-scam-using-fake-rbi-message)

**KYC-4 | "BSNL: TRAI has suspended your SIM KYC, SIM blocked in 24 hrs" notice | VERBATIM (PIB tweet) | News/PIB | PIB 11 Jun 2024; resurfaced May 2026**
- PIB tweet: "Have you also received a notice purportedly from BSNL, claiming that the customer's KYC has been suspended by @TRAI and the sim card will be blocked within 24 hrs❓#PIBFactCheck ❌Beware! This Notice is #Fake. ✅@BSNLCorporate never sends any such notices." The notice also lists a "KYC verification executive" number to call (number not published). — [Factly, 1 Aug 2024](https://factly.in/the-viral-message-about-kyc-suspension-attributed-to-bsnl-is-fake); recirculation reported in [Outlook Money, 4 May 2026](https://www.outlookmoney.com/amp/story/news/government-flags-fake-bsnl-kyc-suspension-message-urges-caution)

**KYC-5 | HDFC "account will be blocked today, update PAN/KYC" SMS | VERBATIM | News/fact-check | 9 Mar 2023 (older than the window, a persistent template)**
- "Dear HDFC Customer Your HDFC Account/Netbanking will be [block] today. Please update you pan card and complete your KYC now [.] click here (link). HDFC TM" Sent from an ordinary number; HDFC says genuine messages come from sender IDs HDFCBK/HDFCBN (see GEN-6). — [Fact Crescendo, 9 Mar 2023](https://english.factcrescendo.com/?p=15481)

**KYC-6 | Fake bank KYC SMS with a deadline link | PARAPHRASED | State police via news | 23 Sep 2024**
- Kerala Police: fake messages with links ask customers to click "within a specified time to update their KYC" or lose the account; the link then triggers an OTP that a fake "bank official" asks for. — [Onmanorama, 23 Sep 2024](https://onmanorama.com/news/kerala/2024/09/23/cyber-fraud-in-the-guise-of-bank-kyc-updation-kerala-police-warn-public.html)

**KYC-7 | WhatsApp "money debited, reply NO" fake bank alert | PARAPHRASED | State police via news | 16 Oct 2026**
- Hyderabad City Police Commissioner VC Sajjanar: a WhatsApp message from an unknown number says money has been debited, then a second message says to reply 'NO' if unauthorised; police say never reply 'YES' or 'NO'. — [Free Press Journal, 16 Oct 2026](https://www.freepressjournal.in/tech/replying-no-on-whatsapp-could-empty-your-bank-account-hyderabad-police-warns)

**KYC-8 | Fake e-challan / RTO APK messages | PARTIAL | News quoting PIB | PIB warning reported 10 Jul 2026; Moneylife illustration (date not on page)**
- Moneylife's example wording: "Your vehicle challan has been generated. Download the receipt from the link below." (presented as an example, not a captured message). Typical APK names: 'RTO Challan.apk', 'RTO E Challan.apk', 'MParivahan.apk', and for gas-bill variants 'Gas Bill Update.apk'. Official portal named by PIB coverage: echallan.parivahan.gov.in. — [Moneylife](https://www.moneylife.in/article/fraud-alert-why-seniors-are-in-the-crosshairs/article/fraud-alert-from-echallan-gas-bill-updates-to-apk-traps-how-malware-scams-are-draining-bank-accounts/79996.html); [Outlook Money, 10 Jul 2026](https://www.outlookmoney.com/news/fake-traffic-e-challan-messages-can-expose-otps-trigger-unauthorised-bank-transactions-pib-warns)

### Inferences
- The 2026 trend in this set is APK delivery under a regulator or bank name, so a "forwarded .apk or shortened link" signal should dominate "urgent KYC" wording in tests.

### Gaps
- Verbatim 2025-26 SMS text from a real handset is rare in the sources; KYC-1 to KYC-3 wording is the outlets' paraphrase of PIB images.

## 6. Fake job offers and task scams

### Takeaway
Sources give victim-side narratives (handles, URLs, amounts) rather than the opening message text. The Delhi Police Aug 2026 case and the Hyderabad Nov 2024 case have concrete identifiers that can seed tests.

### Cited Findings

**JOB-1 | Telegram "review task" then investment pitch (Delhi) | PARTIAL | State police via news (IANS) | 6 Aug 2026**
- Complainant "was initially approached on June 9 by a Telegram user identified as 'Payal Singh Jaat', who assigned him online review tasks related to Foodpanda"; on July 2 he was "introduced to another Telegram user identified as 'Gaurika Ojas' (@mhhgdzs)" who pushed an investment scheme "promising unusually high returns". Loss Rs 2,84,100; E-FIR No. 190/2026 dated July 9, Cyber Police Station, Central District. Handles are the accused's persona names as published. — [IANS Live, 6 Aug 2026](https://ianslive.in/delhi-police-bust-telegram-based-part-time-job-scam-arrest-two-from-rajasthan--20260806131933)

**JOB-2 | WhatsApp "part-time YouTube job" to Telegram to fake trading site (Hyderabad) | PARTIAL | News (Siasat) | 5 Nov 2024**
- A WhatsApp message offered a part-time job; the victim was told to subscribe to a YouTube channel named @priyankatiwarivlogs and screenshot it, install Telegram, join a channel, then "trade through a link to a website called 'digitvisionan.top'"; the dashboard showed Rs 8,99,070 but the withdrawal button failed and a "withdrawal code" never arrived. Loss about Rs 9 lakh. — [Siasat, 5 Nov 2024](https://www.siasat.com/woman-duped-of-rs-9-lakh-in-part-time-job-scam-in-hyderabad-3126314/amp/)

**JOB-3 | "Like YouTube videos, earn Rs 50 per like" task scam | PARAPHRASED | Bank fraud-awareness PDF (Kotak Mahindra Bank, not a regulator) | undated**
- Steps described: SMS/WhatsApp contact; task to "like" YouTube videos "and earn Rs 50 for each like"; they "sometimes also use names of established companies such as Amazon or Flipkart"; a link and UPI ID/mobile number ask for Rs. 100 to 500; later demands for "GST/tax" to withdraw. — [Kotak: The Fake Job Scam](https://www.kotak.bank.in/content/dam/Kotak/others/safe-banking/fake-jobs.pdf)

**JOB-4 | District police advisory on Telegram/WhatsApp task jobs | PARAPHRASED | News on a police advisory | 17 Sep 2026 (advisory dated 16 Sep 2026)**
- Careerindia: tasks pay small amounts first, then deposits are demanded; "Genuine employers never charge candidates"; new UPI IDs change between tasks. District not named in the article. — [Careerindia, 17 Sep 2026](https://www.careerindia.com/features/telegram-and-whatsapp-task-scams-how-to-identify-fake-work-from-home-job-offers-and-protect-your-money-2026-011-65711.html)

### Inferences
- Pattern features for tests: small first payout, move from WhatsApp to Telegram, task dashboard with a balance, "withdrawal code/GST/tax" demand. A named website or Telegram handle is the checkable artifact.

### Gaps
- No verbatim opening message of the "Hi, we are hiring..." type from an official source. Snippet-only lead: Udupi youth, Telegram group paying Rs 20 per task, Rs 900 after 10 tasks, loss Rs 5.7 lakh (Deccan Herald, date not seen): https://www.deccanherald.com/amp/story/india%2Fkarnataka%2Fudupi-youth-loses-rs-57-lakh-in-telegram-work-from-home-fraud-3702817
- No fake recruitment notice (railway/bank/India Post) found.

## 7. Fake universities (UGC list)

### Takeaway
UGC's February 2026 list names 32 institutions; the outlet I could open lists 21 of them by name. Entries are institution names, not messages, so the test input is an admissions ad or message naming one of them.

### Cited Findings

**UGC-1 | UGC "List of Fake Universities" as of Feb 2026 | VERBATIM names (21 of 32) | Official list via news | reported 23 Feb 2026**
- Delhi: All India Institute of Public & Physical Health Sciences (AIIPHS) State Government University; Commercial University Ltd., Daryaganj; United Nations University; Vocational University; ADR-Centric Juridical University, Rajendra Place; Indian Institute of Science and Engineering; Viswakarma Open University for Self-Employment, Sanjay Enclave; Adhyatmik Vishwavidyalaya (Spiritual University), Rohini; World Peace of United Nations University (WPUNU), Pitampura; Institute of Management and Engineering, Kotla Mubarakpur.
- Uttar Pradesh: Gandhi Hindi Vidyapith, Prayag; Netaji Subhash Chandra Bose University (Open University), Aligarh; Bhartiya Shiksha Parishad, Lucknow; Mahamaya Technical University, Noida.
- West Bengal: Indian Institute of Alternative Medicine, Kolkata; Institute of Alternative Medicine and Research, Diamond Harbour Road. Maharashtra: Raja Arabic University, Nagpur. Puducherry: Sree Bodhi Academy of Higher Education, Thilaspet. Karnataka: Badaganvi Sarkar World Open University Education Society, Gokak. Kerala: St. John's University, Kishanpattam. Andhra Pradesh: Christ New Testament Deemed University / Bible Open University of India, Visakhapatnam.
- UGC's stated rule: only universities set up by Act of Parliament or a State Legislature, or declared "deemed to be universities" under Section 3, may award degrees; names with "open university", "state government university" or international-sounding titles confer no status. — [Goodreturns, 23 Feb 2026](https://www.goodreturns.in/news/ugc-flags-32-fake-universities-in-india-check-complete-list-state-wise-before-taking-admission-1491595.html)

**UGC-2 | Suggested test-input framing for individual entries | PARAPHRASED (constructed)**
- Test the app with an admission-offer message that names, e.g., "Viswakarma Open University for Self-Employment" or "AIIPHS State Government University" (note "State Government University" in the AIIPHS name). Do not treat any constructed message as a real circulating one.

**UGC-3 | Earlier UGC list, Oct 2025 (22 institutions) | PARAPHRASED | snippet-only**
- Organiser, Newsgram and Careers360 reported a 22-institution UGC list in late Oct 2025 with Delhi at 10. Lists were not opened. — [Organiser, 30 Oct 2025](https://organiser.org/2025/10/30/323385/bharat/ugc-releases-updated-list-of-22-fake-universities-across-india-delhi-tops-the-chart/)

### Inferences
- Because Delhi and UP names recur across list editions, matching on the institution name plus locality (as UGC prints it) is more reliable than on the name alone.

### Gaps
- Goodreturns says 32 institutions and Delhi has 12, but the names it prints total 21 (Delhi 10); the PDF at ugc.gov.in was not opened. Reconstruct the full 32 from UGC directly before relying on this list in a registry.

## 8. Fake government scheme messages debunked by PIB Fact Check

### Takeaway
2026 is dominated by the "National Student Laptop Scheme 2026" WhatsApp message (debunked at least four times) and a PMJDY 2026 cash message. PIB's own tweet wording is available through news embeds and is the closest to verbatim.

### Cited Findings

**SCH-1 | "National Student Laptop Scheme 2026" free-laptop WhatsApp message | VERBATIM (PIB tweet) | News/PIB | PIB posts reported 12 Jan, 27 Apr, 5 and 14 Jun, 21 Sep 2026**
- PIB tweet as quoted: "A WhatsApp message is circulating claiming that the Government is accepting applications for free laptops under the 'National Student Laptop Scheme 2026'.#PIBFactCheck: ❌ This claim is #FAKE." The message "directs users to an online application form" asking name, qualifications, age. A later PIB tweet (21 Sep 2026) reads: "A #WhatsApp message is being circulated claiming that the Government has invited applications from students for free laptops under the 'National Student Laptop Scheme 2026.'" (via search summary). An Aug 2026 variant carries Ministry of Education branding and a PM image with an "Apply Online" button. — [Digit, 5 Jun 2026](https://www.digit.in/news/general/free-laptops-for-students-heres-the-truth-behind-national-student-laptop-scheme-whatsapp-message.html/amp/); [Akashvani](https://newsonair.gov.in/government-debunks-fake-whatsapp-message-claiming-free-laptops-under-national-student-laptop-scheme/); [Organiser, 22 Sep 2026](https://organiser.org/2026/09/22/381932/bharat/fact-check-govt-did-not-announce-free-laptops-for-students-under-national-student-laptop-scheme-2026-its-fake/) (snippet-only)

**SCH-2 | "PMJDY 2026" application cash-benefit message | VERBATIM (PIB tweet, truncated) | News/PIB | PIB post ~15 Jul 2026; Digit 16 Jul 2026**
- "A viral #WhatsApp message claims that online application for Pradhan Mantri Jan Dhan Yojana (PMJDY) 2026 has started & eligible Indian citizens aged 13–65 years will receive financial assistance ranging from ₹50,000 to ₹2,00,000 under the scheme, based on their age.…" The message ends with a hyperlink to a suspicious registration page. — [Digit, 16 Jul 2026](https://www.digit.in/news/general/beware-this-fake-pm-jan-dhan-yojana-message-can-cost-you-your-savings-here-is-how-to-stay-safe.html)

**SCH-3 | "Rs 46,715 to every citizen" WhatsApp message | PARAPHRASED | News/PIB | 28 Feb 2025**
- Claims the Modi government gives Rs 46,715 to every citizen and urges sharing personal details. Same article lists other PIB-debunked claims: no tax for senior citizens above 75; a forged PMEGP/KVIC approval letter offering a Rs 17 lakh loan for a Rs 51,000 payment. — [Angel One, 28 Feb 2025](https://www.angelone.in/news/market-updates/pib-fact-check-is-the-government-giving-rs-46715-to-every-citizen)

**SCH-4 | Finance Ministry "monetary rewards" message | PARAPHRASED | News/PIB | 5 Jan 2026**
- PIB: the claim that the Finance Ministry is providing monetary rewards "is fake and a part of a scam". Message text not published. — [Akashvani, 5 Jan 2026](https://www.newsonair.gov.in/government-debunks-social-media-message-claiming-that-finance-ministry-is-providing-monetary-rewards)

### Inferences
- SCH-1 and SCH-2 give two short, exact PIB-sourced claim strings; the app can answer them by returning the PIB debunk. Whether Parakh can query PIB posts programmatically was not tested.

### Gaps
- PIB's own X posts and pib.gov.in/factcheck.aspx (an embedded Twitter feed) could not be read; wording is as quoted by the outlets above.

## 9. Genuine official messages and formats the app should match (not flag)

### Takeaway
Five items are checkable against a public source: the genuine ED summons format, the income-tax DIN rule, real SEBI-registered broker disclosures, SEBI's social-media disclosure rule, and RBI's real WhatsApp numbers. I could not independently confirm the broker registration numbers on SEBI's own list.

### Cited Findings

**GEN-1 | Genuine ED summons | Official (ED) | 8 Oct 2025**
- Per ED: summons are issued under "section 50(2) of the Prevention of Money Laundering Act, 2002 (PMLA) and section 37 of Foreign Exchange Management Act, 1999 (FEMA)"; system-generated summons carry "QR code and a unique Passcode at the bottom", are "duly signed and stamped" and "contain his/her official email id and the phone number"; verify at https://enforcementdirectorate.gov.in/ under "Verify Your Summons" using the summons number and Passcode; verification works "after 24 hours of summons issuing date (excluding public holidays, Saturdays and Sundays)". — [ED press release](https://enforcementdirectorate.gov.in/sites/default/files/latestnews/Press_release_fake%20summons-08.10.2025%201.pdf)

**GEN-2 | Genuine income-tax communication carries a DIN | Official (CBDT) | Circular No. 19/2019 dated 14 Aug 2019**
- "No communication shall be issued by any income-tax authority ... on or after the 1st day of October, 2019 unless a computer-generated Document Identification Number (DIN) has been allotted and is duly quoted in the body of such communication." Manual exceptions must state: "This communication issues manually without a DIN on account of reason/reasons given in para 3(i)/3(ii)/3(iii)/3(iv)/3(v) of the CBDT Circular No …dated ….. ... and with the approval of the Chief Commissioner / Director General of Income Tax vide number …. dated …." Non-conforming communications are "treated as invalid and shall be deemed to have never been issued". — [TaxGuru (PIB release and circular text)](https://taxguru.in/income-tax/din-mandatory-all-income-tax-notices-etc-wef-01-10-2019.html)
- Caution: TAX-2 shows a fake can print an ITBA-style reference, so format alone is not proof. An authentic-DIN example string was not retrieved from an official page; verification is via the e-filing portal's "authenticate notice" feature (described by third-party guides, not opened).

**GEN-3 | Real broker disclosure format | Company websites (not SEBI) | retrieved 1 Nov 2026**
- Groww: "Groww Invest Tech Pvt. Ltd. (Formerly known as Nextbillion Technology Pvt. Ltd) (CIN: U65100KA2016PTC092879) is a member of NSE & BSE & MCX with SEBI Registration no: INZ000301838, Depository Participant of CDSL Depository with SEBI Registration no: IN-DP-417-2019 and Mutual Fund distributor with AMFI Registration No: ARN-111686." — [groww.in](https://groww.in/)
- Upstox: "Upstox Securities Pvt. Ltd.: SEBI Registration No. INZ000315837 | NSE TM Code: 13942 | BSE TM Code: 6155 | MCX TM Code: 46510 | CDSL Reg No.: IN-DP-761-2024 | CIN: U65100DL2021PTC376860" — [upstox.com](https://upstox.com/)
- Not cross-checked against SEBI's intermediary page (query not possible from here). Treat as the expected "matched" case only after a manual check at https://www.sebi.gov.in/intermediaries.html.

**GEN-4 | SEBI's social-media disclosure rule (what a genuine registered handle shows) | Official (SEBI circular) | 26 Feb 2026, effective 1 May 2026**
- Circular HO/(79)2026-MIRSD-PODMMC: regulated entities and their agents "shall prominently disclose their registered name and registration number" on their social-media content; applies to groups including WhatsApp and Telegram. — [SEBI circular (NSDL copy)](https://nsdl.com/nsdl/2026-05/09_SEBI_Circular_dated_26_February_2026.pdf); effective date from [Free Press Journal](https://www.freepressjournal.in/amp/business/sebi-mandates-social-media-disclosure-registration-number-must-be-shown-from-may-1-2026) (snippet-only)

**GEN-5 | RBI's genuine WhatsApp numbers | News quoting PIB | 12 Jun 2026**
- RBI "communicates via WhatsApp only through its two verified blue-tick numbers: 99309 91935, 99990 41935". Single secondary source; confirm on rbi.org.in. — [Angel One, 12 Jun 2026](https://oga-prod.angelone.in/news/personal-finance/rbi-whatsapp-scam-alert-pib-warns-users-against-fake-messages-claiming-bank-account-blockage)

**GEN-6 | Other genuine channel facts the app can use | mixed**
- HDFC Bank genuine SMS sender IDs: HDFCBK / HDFCBN, links under hdfcbk.io (bank's tweet as reported, 2023): [Fact Crescendo](https://english.factcrescendo.com/?p=15481). SBI phishing report address report.phishing@sbi.co.in: [IBTimes](https://www.ibtimes.co.in/pib-flags-fake-sbi-yono-message-urging-aadhaar-update-warns-customers-against-phishing-scam-899756). Income-tax phishing report address webmanager@incometax.gov.in: [Business Standard](https://www.business-standard.com/amp/finance/personal-finance/tax-refund-scam-alert-don-t-fall-for-that-manual-verification-email-125072200446_1.html). PIB Fact Check WhatsApp 8799711259: [Outlook Money, 4 May 2026](https://www.outlookmoney.com/amp/story/news/government-flags-fake-bsnl-kyc-suspension-message-urges-caution). RBI's Digital Lending Apps directory live from 1 Jul 2025, "aims to aid the customers in verifying the claim of a DLA's association with a Regulated Entity": [Akashvani, 8 Dec 2025](https://www.newsonair.gov.in/govt-engages-with-rbi-regulators-to-curb-unauthorized-digital-loan-apps/).

### Inferences
- Sets worth testing as true positives: a summons carrying summons number, Passcode and QR (GEN-1); a DIN-bearing notice that verifies on the portal (GEN-2); a registered broker footer whose number appears on SEBI's list (GEN-3).
- A fake can mimic every field in GEN-1 to GEN-3 except the registry lookup, so match status must come from the lookup, not the format.

### Gaps
- No published real SEBI-registered investment adviser or research analyst disclosure block (INA/INH) was retrieved; GEN-3 uses stock-broker (INZ) numbers instead.
- No authentic sample income-tax notice with its full DIN string was found on an official page.
- GEN-5 and the HDFC IDs rest on a single secondary source each.
