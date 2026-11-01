# Indian identifiers in scam messages: formats, validation rules and official verification links (Parakh build sheet)

Current as of 1 Nov 2026. India only. Research done 1 Nov 2026.

**Confidence tags used on every finding**
- `[OFFICIAL]` = I fetched/read the official page or document myself today.
- `[OFFICIAL-via-search]` = official page exists, but my fetcher was blocked (MCA, RBI, incometaxindia.gov.in, NPCI, bhimupi.org.in return 403/bot-challenge to scripted fetches); the text was seen only through search-engine extracts of that official page. Re-verify by hand.
- `[SECONDARY]` = non-official source (tax/legal site, open-source library, blog, exchange circular quoting SEBI).
- `[UNCERTAIN]` = no source located, sources conflict, or it is my inference.
- `[SANDBOX]` = I ran code in my sandbox to test it; this is a test result, not a source.

**Global rules for the app (inferences, apply to all sections)**
- Normalise input before matching: strip spaces, hyphens (except where hyphens are part of the format, see each section), NBSP, zero-width chars; upper-case (except the lower-case `@valid` UPI handles); convert Devanagari/Arabic-Indic digits to ASCII.
- A format match plus checksum pass proves only that the string is well-formed. It never proves the entity is real or registered. Always route to the official register.
- Treat a fake-but-plausible ID as a normal scam tactic. One tax blog among the search results warns that scammers now forge realistic DINs that pass format checks but fail authentication (blog not pinned, so `[UNCERTAIN]`); the Finance Ministry's Jan 2025 advisory on fake CBIC summonses copying the logo and DIN (see CBIC DIN section) supports the same point.

---

## GSTIN (15 characters)

### Takeaway
Structure is 2-digit state code + 10-char PAN + entity number + `Z` + check character. The check character is a Luhn mod-36 (alphanumeric Luhn) over the first 14 characters, which I reproduced and verified against a documented valid GSTIN. No official GSTN document that spells out the checksum steps was found; no official worked example was found.

### Cited Findings
- GSTIN is a 15-digit number; first 2 digits = state code, next 10 = PAN of the legal entity, "next two digits are for entity code", last digit = checksum number. — [CBIC/GST Council registration flyer](https://gstcouncil.gov.in/sites/default/files/e-version-gst-flyers/Registration_under_GST_Law_new.pdf) `[OFFICIAL]`
- Position 13 = entity number (counts registrations of same PAN in that state; `1-9` then `A-Z`), position 14 = `Z` (static), position 15 = check digit from "luhn mod 36". — [Devil7 GSTIN-Validator README](https://github.com/Devil7-Softwares/GSTIN-Validator) `[SECONDARY]`; same structure and "Luhn mod 36" in [python-stdnum `stdnum.in_.gstin`](https://arthurdejong.org/python-stdnum/doc/stdnum.in_.gstin) `[SECONDARY]`
- python-stdnum documents `27AAPFU0939F1ZV` as a **valid** GSTIN and `27AAPFU0939F1ZO` as an invalid-checksum one, `27AAPFU0939F1AA` as invalid (14th char not Z), `369296450896540` as bad format. — [python-stdnum docs](https://arthurdejong.org/python-stdnum/doc/stdnum.in_.gstin) `[SECONDARY]`
- Generic Luhn mod N algorithm with code points `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ`, factor starts at 2 on the rightmost input char and alternates 2/1 going left, each product split in base n and summed, check = (n - sum mod n) mod n. — [Wikipedia, Luhn mod N algorithm](https://en.wikipedia.org/wiki/Luhn_mod_N_algorithm) `[SECONDARY]`
- State-code table (first two digits of GSTIN/TIN): 01 JK, 02 HP, 03 PB, 04 CH, 05 UT, 06 HR, 07 DL, 08 RJ, 09 UP, 10 BR, 11 SK, 12 AR, 13 NL, 14 MN, 15 MZ, 16 TR, 17 ML, 18 AS, 19 WB, 20 JH, 21 OR, 22 CG, 23 MP, 24 GJ, 25 DD, 26 DN, 27 MH, 28 AP, 29 KA, 30 GA, 31 LD, 32 KL, 33 TN, 34 PY, 35 AN, 36 TS, 37 AP (new). — [Delhi VAT Dept state-code list](https://ddvat.gov.in/docs/List%20of%20State%20Code.pdf) `[OFFICIAL]` (state government PDF; table ends at 37)
- Code 38 (Ladakh) and codes 97 ("Other Territory") and 99 ("Other Country", used by foreign OIDAR registrants) also occur; sources differ on whether the range is 01-37 or 01-38. — [LookupTax India guide via search](https://lookuptax.com/docs/tax-identification-number/India-tax-id-guide) `[SECONDARY]`; range conflict seen across [Motilal Oswal / Ai Accountant via search](https://www.aiaccountant.com/blog/gstin-format) `[SECONDARY]`
- Position 14 is described as `Z` "by default"; one secondary source says `D` for tax deductors (TDS) and `C` for tax collectors (TCS), while others say it must always be `Z`. — [taxheal "Structure of GSTIN" via search](https://taxheal.com/structure-of-gstin.html) `[SECONDARY]` vs [python-stdnum](https://arthurdejong.org/python-stdnum/doc/stdnum.in_.gstin) `[SECONDARY]`. The conflict is unresolved: `[UNCERTAIN]`.
- Foreign OIDAR IDs (e.g. `99..` with a country code) and UIN (embassy/UN body) IDs do not follow the PAN-based layout. — [LookupTax via search](https://lookuptax.com/docs/tax-identification-number/India-tax-id-guide) `[SECONDARY]`
- Verification: GST portal "Search Taxpayer" at `https://services.gst.gov.in/services/searchtp`. The URL responds HTTP 200 from my machine but serves a JavaScript/bot challenge to scripted GETs, so I could not read the page body. Existence of the service is `[UNCERTAIN]` as to exact current path; the host `services.gst.gov.in` is the official GST services host ([GST tutorial pages use it](https://tutorial.gst.gov.in/userguide/registration/Apply_for_Registration_Normal_Taxpayer.htm) `[OFFICIAL]`).

### Inferences
- **Regex (regular taxpayer, PAN-based):** `^(0[1-9]|[1-2][0-9]|3[0-8]|9[79])[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$`. Loosen the 14th char to `[ZDC]` if you want to accept TDS/TCS; treat `D`/`C` as `[UNCERTAIN]`.
- **Checksum (step by step)** `[SANDBOX]` (verified: `27AAPFU0939F1ZV` passes, `27AAPFU0939F1ZO` fails):
  1. `CP = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"`, `n = 36`.
  2. Take the first 14 characters. Walk from char 14 down to char 1. `factor` starts at 2 for char 14, then alternates 1, 2, 1, ... (so odd positions get 1, even positions get 2).
  3. For each char: `cp = CP.index(ch)`; `a = factor * cp`; `a = a // 36 + a % 36`; `sum += a`.
  4. `check = CP[(36 - sum % 36) % 36]`; compare with char 15.
- Cross-checks worth doing offline: chars 3-12 must pass the PAN regex (below); char 6 of the GSTIN (the PAN's 4th char) gives entity type, so a GSTIN claiming to be a "Pvt Ltd" whose embedded PAN 4th char is `P` is suspicious.
- Test fixture: `27AAPFU0939F1ZV` (valid, from python-stdnum). Do not use the GST portal's placeholder-looking strings as valid fixtures; I did not locate one on an official page.

### Gaps
- No official GSTN/CBIC document stating the check-digit algorithm was found (only "check sum number"). The algorithm above is standard Luhn mod 36 confirmed against one documented valid GSTIN.
- No official worked-example GSTIN found on gst.gov.in / cbic.gov.in pages I could read.
- The `D`/`C` 14th-character rule for TDS/TCS and the exact set of valid state codes (38, 97, 99) are unconfirmed on an official GSTN page.
- GST "Search Taxpayer" page content could not be read (bot challenge).

---

## PAN (10 characters) and the meaning of the 4th character

### Takeaway
Format `AAAPA9999A`: 3 letters (AAA-ZZZ series), 4th = holder status, 5th = first letter of surname (individuals) or name (others), 4 digits 0001-9999, 1 alphabetic check letter. The 10th-character algorithm is not public.

### Cited Findings
- "A typical PAN is AFZPK7190K." Chars 1-3 alphabetic series AAA to ZZZ; 4th = status: P Individual, F Firm, C Company, H HUF, A AOP, T Trust, B Body of Individuals, L Local Authority, J Artificial Juridical Person, G Government; 5th = first character of last name/surname; next four = sequential 0001-9999; last = alphabetic check digit. — [OECD-hosted India TIN fact sheet supplied by India](https://oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/India-TIN.pdf) `[OFFICIAL]` (Government of India submission, hosted by OECD)
- Same 4th-character table; 5th char is first letter of the entity's name for non-individuals; the 10th char is a check letter generated by a mathematical formula on the first nine characters (formula not given). — [Protean eGov Technologies (NSDL e-Gov, PAN service provider)](https://www.proteantech.in/articles/pan-card-number-10-characters-meaning) `[OFFICIAL]` (PAN issuing agency site; not the Income Tax Department itself)
- Protean labels `F` as "Firm / Limited Liability Partnership (LLP)". — [Protean](https://www.proteantech.in/articles/pan-card-number-10-characters-meaning) `[OFFICIAL]`
- Income Tax Department pages on PAN structure exist at incometaxindia.gov.in but returned 403 to my fetcher. — [ITD "How PAN is formed" (listed in search)](https://www.incometaxindia.gov.in/w/how-pan-is-formed-and-how-it-gets-its-unique-identity-) `[OFFICIAL-via-search]`
- Verification: the OECD sheet points to the "Know your PAN" facility of the e-Filing portal (legacy domain `incometaxindiaefiling.gov.in`, now superseded by `www.incometax.gov.in`). — [OECD India TIN sheet](https://oecd.org/tax/automatic-exchange/crs-implementation-and-assistance/tax-identification-numbers/India-TIN.pdf) `[OFFICIAL]`. The current "Verify Your PAN" deep link on `eportal.incometax.gov.in` is `[UNCERTAIN]` (host responds 200; path not confirmed on a page I could read).

### Inferences
- **Regex:** `^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$`. Optional strictness: if 4th char = `P`, 5th must be a letter (surname initial); the app cannot verify it without the name.
- No checksum can be implemented (algorithm unpublished). Do not claim "valid PAN" from format alone; say "well-formed".
- Link out to `https://www.incometax.gov.in` (Quick Links > Verify Your PAN) rather than a deep link, until the deep link is hand-verified.
- Fixture: `AFZPK7190K` (OECD sheet example; the sheet presents it as a typical PAN).

### Gaps
- PAN check-letter algorithm: not found, believed unpublished.
- Direct fetch of incometaxindia.gov.in PAN pages blocked; 4th-char table is therefore confirmed via the OECD India sheet and Protean, not the ITD page itself.
- Current deep link for ITD's pre-login "Verify Your PAN" not confirmed.

---

## Aadhaar (12 digits, Verhoeff) - never store

### Takeaway
12 digits with the last digit a Verhoeff check digit (UIDAI tells client apps to validate "12 digits and conform to Verhoeff"). A leading-digit rule (2-9) comes only from a library, not UIDAI. Regulations bar publishing/displaying Aadhaar numbers; UIDAI requires vault storage and last-4 masking, so Parakh should validate in memory only and persist nothing.

### Cited Findings
- UIDAI API error 998 guidance: AUA applications "should have a client level validation for Aadhaar number validity i.e. should be 12 digits and conform to Verhoeff algorithm." — [UIDAI API error-code document (copy hosted on nulm.gov.in)](https://nulm.gov.in/PDF/UIDAI-APIerrorcode.pdf) `[OFFICIAL]`
- NIC/MeitY apps page: "UIDAI has recommended Verhoeff algorithm for validating" Aadhaar numbers. — [apps.nic.in Aadhaar validation component (via search)](https://apps.nic.in/apps/government/aadhaar-number-validation-verhoeff-algorithm) `[OFFICIAL-via-search]`
- Aadhaar pattern `^[2-9][0-9]{11}$`: numbers do not begin with 0 or 1; check digit last. — [python-stdnum `stdnum.in_.aadhaar`](https://arthurdejong.org/python-stdnum/doc/stdnum.in_.aadhaar) `[SECONDARY]`. I found no UIDAI page stating the first-digit rule: `[UNCERTAIN]` as official.
- Verhoeff worked example: check digit for `236` is `3`; `2363` validates (c = 0). — [Wikipedia, Verhoeff algorithm](https://en.wikipedia.org/wiki/Verhoeff_algorithm) `[SECONDARY]` (test vector only; these are not Aadhaar numbers)
- Storage: UIDAI Circular No. 14 of 2025 says entities keep the full Aadhaar number only in a segregated, encrypted Aadhaar Data Vault (AES-256 or stronger) and use a reference key elsewhere. — [UIDAI Circular 14 of 2025](https://uidai.gov.in/images/Circular-No.14_of-2025.pdf) `[OFFICIAL-via-search]`; FAQ: [UIDAI Aadhaar Data Vault FAQs](https://uidai.gov.in/images/FAQs_Aadhaar_Data_Vault_03112025_v10.pdf) `[OFFICIAL-via-search]`
- Display: Regulation 6(1) of the Aadhaar (Sharing of Information) Regulations, 2016 bars publishing, displaying or posting an Aadhaar number publicly; contravention is a violation of Section 29(2) of the Aadhaar Act. — [UIDAI regulation PDF](https://uidai.gov.in/images/The_Aadhaar_Sharing_of_information_regulation_2016.pdf) `[OFFICIAL-via-search]`
- Masking: UIDAI compliance checklists say default display should show only the last four digits. — [UIDAI AUA/KUA checklist](https://uidai.gov.in/images/Compliance_checklist_for_certifying_compliance_with_controls_that_the_AUAKUA_is_required_to_have_in_place.pdf) `[OFFICIAL-via-search]`
- Verification page for a holder to check an Aadhaar number exists: `https://myaadhaar.uidai.gov.in/verifyAadhaar` (UIDAI domain; GET returned the UIDAI "myAadhaar" shell only; HEAD returned HTTP 500; content not readable) `[UNCERTAIN]` as to current UI, official domain.

### Inferences
- **Regex:** `^[2-9][0-9]{11}$` (first-digit rule from library; to be safe, on a leading 0/1 report "not a valid Aadhaar pattern" but don't hard-block other analysis).
- **Verhoeff (validate)** `[SANDBOX]` (passes the Wikipedia vectors `2363` and `123451`): tables `d` (10x10 dihedral), `p` (8x10 permutation), `inv`; `c = 0; for i, ch in enumerate(reversed(num)): c = d[c][p[i % 8][int(ch)]]; valid iff c == 0`. Tables are in the reference-code block at the end of this file.
- **Privacy design:** never write the full number to disk, DB, logs, analytics or clipboard history; keep it in a local variable for the single check; echo back only `XXXX XXXX 1234`. Do not send it to any server or LLM. If the user pasted it into a message the app is analysing, redact before any storage.
- **No known official worked Aadhaar example exists** (and should not): use only the Verhoeff vectors above as test data, plus generated numbers built by appending a computed check digit to random 11 digits (clearly labelled synthetic).
- Note scams: no one legitimate asks for Aadhaar number + OTP in a message; the verify service only confirms existence, not who is contacting the user.

### Gaps
- UIDAI-stated first-digit rule (2-9) not found on any UIDAI page.
- Content of the `verifyAadhaar` page (and whether it asks for captcha/OTP) not readable.
- UIDAI PDFs (circular 14/2025, regulation, checklist) were read through search extracts, not fetched in full.

---

## Company CIN (21 characters) and LLPIN

### Takeaway
CIN = listing status (L/U) + 5-digit NIC code + 2-letter state + 4-digit year + 3-letter ownership code + 6-digit number = 21 chars. LLPIN is `AAA-1234` (3 letters, hyphen, 4 digits). Neither has a published checksum. MCA's own site blocked my fetcher, so the segment meanings are secondary, cross-checked against real CINs printed in MCA PDFs (seen via search extracts).

### Cited Findings
- CIN is 21 alphanumeric characters in six sections: listing status, industry code, state code, year of incorporation, ownership, registration number; example `L01631KA2010PTC096843`. — [Wikipedia, Corporate Identification Number](https://en.wikipedia.org/wiki/Corporate_Identification_Number) `[SECONDARY]`
- Segment detail: 1st char `L` listed / `U` unlisted; next 5 digits = economic activity (NIC) code; next 2 letters = state code of registered office (ROC); next 4 digits = year of incorporation; next 3 letters = company type; last 6 digits = ROC registration number. Worked decode of Hindustan Aeronautics: listed, activity `35301`, state `KA`, year `1963`, type `GOI`, number `001622`. — [InstaFinancials "All about CIN"](https://blog.instafinancials.com/2018/07/06/all-about-cin-and-its-structure/) `[SECONDARY]` (so the CIN is `L35301KA1963GOI001622`, reconstructed from those parts)
- Company-type codes listed: `FLC` financial lease company (public), `FTC` subsidiary of a foreign company (private), `GAP` general association (public), `GAT` general association (private), `GOI` owned by Govt of India, `NPL` not-for-profit licence company, `PLC` public limited, `PTC` private limited, `SGC` owned by State Govt, `ULL` public with unlimited liability, `ULT` private with unlimited liability. — [InstaFinancials](https://blog.instafinancials.com/2018/07/06/all-about-cin-and-its-structure/) `[SECONDARY]`; `OPC` (One Person Company) also appears in other guides — [LegalWiz via search](https://www.legalwiz.in/blog/cin-number-what-it-is-structure-importance-how-to-check) `[SECONDARY]`
- Real CINs printed in MCA PDFs (seen via search extract; which of the two lists carries each CIN was not pinned): `U74999RJ1857PLC000649`, `U80100AP1992NPL014292`, `U91110AP1918NPL000029` (the first has year 1857, so do not cap the year at 1900+). — [MCA Section 25 companies list](https://www.mca.gov.in/LLP/dca/RegulatoryRep/pdf/Section25_Companies.pdf) and [MCA 2008 list](https://www.mca.gov.in/Ministry/pdf/Section25_Companies_6nov2008.pdf) `[OFFICIAL-via-search]`
- SPICe+ instruction kit: the NIC code is "the identifier for CIN number" and the first of up to three selected NIC codes goes into the CIN. — [MCA SPICe+ Instruction Kit Part A](https://www.mca.gov.in/content/dam/mca-aem-forms/instructionkits/Instruction%20Kit_SPICe+Part%20A.pdf) `[OFFICIAL-via-search]`
- CIN changes if the company changes state, public/private status, or listing status. — [InstaFinancials](https://blog.instafinancials.com/2018/07/06/all-about-cin-and-its-structure/) `[SECONDARY]`
- LLPIN: 7 characters, pattern `ABC-1234` (three letters, hyphen, four digits). — [IndiaFilings](https://www.indiafilings.com/llp-registration/registration-number) `[SECONDARY]`; [Razorpay Rize](https://razorpay.com/rize/blogs/what-is-llpin-meaning-importance) `[SECONDARY]`. One outlier site claims 10 characters ([Paperli](https://paperli.ai/what-is-llpin) `[SECONDARY]`); treat as wrong. MCA's LLP registration lists carry a combined "CIN/FCRN/LLPIN/FLLPIN" column — [MCA LLP list](https://www.mca.gov.in/Ministry/pdf/llpreg_1980.pdf) `[OFFICIAL-via-search]`.
- Verification: MCA "View Company/LLP Master Data" (company master info page: `https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS/company-master-info.html`); lookup by CIN/LLPIN or name. — [MCA Master Company Info page (listed in search)](https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS/company-master-info.html) `[OFFICIAL-via-search]` (403 to my fetcher). "Find CIN" option on MCA is mentioned by [Ujjivan SFB guide via search](https://www.ujjivansfb.in/banking-blogs/borrow/what-is-cin-number-full-form-and-meaning) `[SECONDARY]`.

### Inferences
- **CIN regex:** `^[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$`. Soft checks: year <= 2026; type code in the set above plus `OPC`; flag unknown 3-letter codes as "unrecognised", not invalid. State code is the ROC state code (letters used on CINs include `KA`, `MH`, `DL`, `AP`, `RJ`, `TG`/`TS`, etc.; I did not source a complete list: `[UNCERTAIN]`).
- A CIN starting `L` that the user is told belongs to a "listed company" can be checked against the stock-exchange listing; an `L` CIN with `PTC` (private) is internally inconsistent and a scam flag (listed companies are public; inference).
- **LLPIN regex:** `^[A-Z]{3}-?[0-9]{4}$` after normalising a missing hyphen to `AAA-1234`. Pattern is thin; high false-positive risk on short strings, so only apply when the message context says LLP.
- No checksum for CIN/LLPIN is known; do not invent one.

### Gaps
- MCA's own FAQ/definition of the CIN segments and the full list of ownership and state codes could not be fetched (403); segment meanings are secondary.
- LLPIN format is secondary-only; no MCA page defining it was readable.
- No full list of valid ROC state codes.

---

## eCourts CNR number (16 characters)

### Takeaway
CNR is a 16-character alphanumeric Case Number Record. The official eCourts search page gives the example `MHAU019999992015`, which decodes as state `MH`, district `AU`, establishment `01`, 6-digit case number, 4-digit year (2+2+2+6+4). Field widths are consistent with the official example but are stated by secondary guides.

### Cited Findings
- eCourts Services "Search by CNR number" page text: "Enter CNR Number, for example MHAU019999992015." — [eCourts Services portal](https://services.ecourts.gov.in/ecourtindia_v6/) `[OFFICIAL]`
- "CNR Number is a unique 16-digit alphanumeric number, which is assigned to each case filed in the High Courts or District Courts." — [Rajasthan HC guide to pay.ecourts.gov.in](https://hcraj.nic.in/hcraj/Allfiles/eFineBilingual.pdf) `[OFFICIAL]`
- CIS 2.0 creates "a 16 digit number which contains the State code, District code, Establishment code, Case filing number, year of the case." — [Calcutta High Court CIS note](https://www.calcuttahighcourt.gov.in/downloads/ecourt_files/cis3/Some_Important_Modules/Case_Number_Record.pdf) `[OFFICIAL]`
- Field widths: first four characters = state (2) + district (2); then establishment (2), 6-digit serial, 4-digit year. — [Hindi legal guides via search, e.g. LegalServiceIndia](https://www.legalserviceindia.com/Legal-Articles/?p=34408) `[SECONDARY]` (one guide uses example `MHPU010012342024`)
- The portal expects the CNR without hyphens or spaces; hyphenated displays like `DLST01-000123-2023` appear in guides. — [Sansa Legal via search](https://www.sansalegal.com/post/how-to-check-court-case-status-online-in-india-ecourts-and-cnr-number-guide) `[SECONDARY]`
- SMS lookup: `ECOURTS <CNR number>` to `9766899899`. — [eCourts home](https://ecourts.gov.in/ecourts_home/) `[OFFICIAL]`
- Scope: district and taluka courts via eCourts services; High Court / Supreme Court have their own portals (CNR also issued by High Courts per the Rajasthan HC text above).
- Verification: `https://services.ecourts.gov.in/ecourtindia_v6/` (CNR Number tab, captcha). — `[OFFICIAL]`

### Inferences
- **Regex:** `^[A-Z]{4}[A-Z0-9]{2}[0-9]{6}[0-9]{4}$` (establishment kept alphanumeric because the official text calls the whole value "alphanumeric" and does not fix the establishment charset; `[UNCERTAIN]`). Year check: 1950 <= year <= 2026.
- Strip hyphens/spaces before matching. Offer the portal link and the SMS number as the next step.
- A message citing a "CNR" that fails this pattern, or a "court notice" with a WhatsApp/UPI payment demand, is a strong scam flag; real court processes do not collect fines by UPI to personal IDs (`pay.ecourts.gov.in` is the official fine/fee portal per the Rajasthan HC guide above).
- Fixture: `MHAU019999992015` (official portal placeholder, not a real case).

### Gaps
- Official eCourts document defining each field width and the state/district code tables was not found.
- Whether establishment codes can contain letters is unconfirmed.

---

## Income Tax Department DIN (notices/orders) and the "Authenticate notice/order" page

### Takeaway
Every ITD communication issued on or after 1 Oct 2019 must carry a DIN; a notice without one is treated as invalid. The ITD authentication service is on the e-Filing portal (no login), accepts either PAN + document type + year + issue date + mobile, or DIN + mobile, with a 6-digit OTP. Official pages do not state the DIN layout; ITAT-hosted orders show the shape `ITBA/AST/M/153C/2021-22/10 digits(1)`. Several websites wrongly attach the CBIC DIN format to income-tax DINs.

### Cited Findings
- "Every communication by Income Tax department issued on or after 1st October, 2019 shall bear an unique Document Identification Number (DIN)"; user can authenticate without logging in; a notice with no DIN "would be treated as invalid". — [ITD e-Filing help: Authenticate the Notice/Order issued by ITD](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/authenticate-noticeorder-issued-itd) `[OFFICIAL]`
- Steps: e-Filing homepage > Quick links > "Authenticate Notice / Order issued by ITD". Option 1: PAN + Document Type + Year Type (Tax Year/Assessment Year) + Date of Issue + Mobile Number. Option 2: Document Identification Number + Mobile Number. A 6-digit OTP is sent to the mobile entered (valid 15 minutes, 3 attempts). Genuine: document number and issue date are shown; otherwise "No record found for the given criteria". — [ITD user manual](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/authenticate-noticeorder-issued-itd-UM) `[OFFICIAL]`
- The same manual lists e-Filing / CPC helplines 1800 103 0025 or 1800 419 0025 (08:00-20:00 Mon-Fri) and PAN/TAN (Protean) +91-20-27218080. — [ITD user manual](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/authenticate-noticeorder-issued-itd-UM) `[OFFICIAL]`
- Legal basis: CBDT Circular No. 19/2019 dated 14 Aug 2019 under section 119, effective 1 Oct 2019; DIN is system-generated on ITBA; manual communications are allowed only in narrow cases with CCIT/DGIT approval and must say they are issued without a DIN. — [Delhi High Court judgment (ITA 163/2023)](https://delhihighcourt.nic.in/app/showFileJudgment/59020032023ITA1632023_120140.pdf) `[OFFICIAL]`; summary at [TaxHeal](https://www.taxheal.com/?p=128709) `[SECONDARY]`
- DIN shape seen in ITAT-hosted orders: `ITBA/AST/M/153C/2021-22/1038299680(1)` (section-153C order DIN). — [ITAT order index via search](https://itat.gov.in/public/files/upload/1695804583-1229-23,%20Harish%20Gupta.pdf) `[OFFICIAL-via-search]`. Shape confirmed on two ITAT PDFs: `ITBA/<module>/<letter>/<section>/<FY>/<10 digits>(<version digit>)`.
- Conflict: [Tax2Win](https://tax2win.in/guide/din-document-identification-number) and [TaxBuddy](https://www.taxbuddy.com/amp/document-identification-number-din-understanding-its-structure-significance-and-advantages) describe the income-tax DIN as "CBIC-YYYY MM ZCDR NNNN" and point to cbic.gov.in; that is the **CBIC** (GST/customs) format, not ITD's. `[SECONDARY]`, treated as an error.
- Direct URL of the authentication tool: the official help pages do not print it (they say "Quick links on the e-Filing homepage"). — [ITD help page](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/authenticate-noticeorder-issued-itd) `[OFFICIAL]`. My recollection of the deep link `https://eportal.incometax.gov.in/iec/foservices/#/pre-login/authenticate-notice-order` is `[UNCERTAIN]` (host responds HTTP 200; path not verified).

### Inferences
- **Loose regex for ITBA-style DIN:** `^ITBA/[A-Z]{2,4}/[A-Z]/[^/\s]+/[0-9]{4}-[0-9]{2}/[0-9]{6,12}\([0-9]\)$`. Only one shape was observed, so mark matches "looks like an ITD DIN" and non-matches "unrecognised format, authenticate anyway" rather than "fake". CPC intimations may use another shape which I could not source.
- Under the Income-tax Act 2025 (tax year replaces assessment year; ITD manual now says "Tax Year/Assessment Year"), the year segment may change style for new documents; do not hard-reject on year format.
- Next step link: `https://www.incometax.gov.in` (Quick Links > Authenticate Notice/Order) plus helpline 1800 103 0025. Tell the user they can authenticate with any mobile number they control; no login or PAN password is needed.
- Fake-notice tells: payment demanded by UPI/WhatsApp to a personal account, or any link/QR in the "notice"; an income-tax notice is shown in the e-Proceedings tab after login.

### Gaps
- No official ITD page publishes the DIN character layout; the ITBA shape is observed from tribunal orders only.
- CPC (intimation u/s 143(1)) DIN/reference shape not found.
- Verified deep link for the authentication page not found.
- The CBDT circular PDF on incometaxindia.gov.in was not fetchable (403).

---

## CBIC DIN (GST/customs) - format and verification URLs

### Takeaway
Format per Circular 122/41/2019-GST is `CBIC-YYYY MM ZCDR NNNNNN`. Length depends on how many characters ZCDR takes (the circular does not say), so sources quote both 19 and 20. The best-evidenced current verification URL is `https://esanchar.cbic.gov.in/DIN/DINSearch`; CBIC's own website menu has several mis-pointed "Verify CBIC-DIN" links, and an older `cbicddm.gov.in` URL appears in blogs.

### Cited Findings
- Circular text: "The format of the DIN shall be CBIC-YYYY MM ZCDR NNNNNN where (a) YYYY = calendar year of generation, (b) MM = month, (c) ZCDR = Zone-Commissionerate-Division-Range Code of the field formation/Directorate of the authorized user generating the DIN, (d) NNNNNN = 6 digit alpha-numeric system generated random number." First phase from 8 Nov 2019 (search authorisations, summons, inspection notices, arrest memos, letters in enquiries). Verification: "entering the CBIC-DIN ... in a window VERIFY CBIC-DIN on CBIC's website www.cbic.gov.in"; only valid DINs return the issuing office and date of generation. A communication without a DIN is treated as invalid. — [Circular 122/41/2019-GST text on GSTZen](https://gstzen.in/a/central-tax-circular-1222019-generation-and-quoting-of-document-identification-number-din-on-any-communication-issued-by-the-officers-of-the-central-board-of-indirect-taxes-and-customs-cbic-to-tax-pa.html) `[SECONDARY]` (official PDF [circular-cgst-122.pdf](https://www.gstcouncil.gov.in/sites/default/files/2024-06/circular-cgst-122.pdf) is an image-only scan I could not text-extract)
- Circular 128/47/2019-GST dated 23 Dec 2019: DIN to be generated and quoted on all communications including e-mails to taxpayers from 24.12.2019; the generation platform is "DDM's online portal cbicddm.gov.in"; recipients verify the DIN on-line at cbic.gov.in. — [GST Council PDF, circular-cgst-128.pdf](https://gstcouncil.gov.in/sites/default/files/2024-06/circular-cgst-128.pdf) `[OFFICIAL]`
- Length conflict: one secondary source says "19 digit ... CBIC-YYYYMMZCDRNNNNN", most say 20 characters; the circular fixes NNNNNN at 6 and does not define the ZCDR width. — [VJM Global via search](https://www.vjmglobal.com/blog/document-identification-number-din-quoted-all-communications-cbic) `[SECONDARY]` vs the circular text above.
- Circular 252/09/2025-GST: for communications sent through the "public option" of CBIC's eOffice, the verifiable eOffice issue number is deemed to be the DIN. — [TaxHeal via search](https://www.taxheal.com/?p=105617) `[SECONDARY]` (a second DIN style may therefore exist).
- Jan 2025 Finance Ministry advisory: fake summonses copy the department logo and DIN; verify first on the CBIC site. — [Taxo via search](https://taxo.online/latest-news/27-01-2025-finance-ministry-asks-taxpayers-to-verify-summons-first-on-cbic-site/) `[SECONDARY]`
- **Candidate verification URLs and evidence:**
  1. `https://esanchar.cbic.gov.in/DIN/DINSearch` - **live today**: page titled "DIN Search | CBIC", form "Enter Document Identification Number (DIN)" with captcha, footer "Directorate of Data Management". CBIC's current website bundle (`www.cbic.gov.in`, `main.9531f77a0f834863.js`) links it as "Verify CBIC DIN GST". `[OFFICIAL]` Best choice.
  2. `https://www.cbic.gov.in/` - the homepage "VERIFY CBIC-DIN" window named in Circular 122 para 8 and Circular 128. The same website bundle labels other "Verify CBIC-DIN" entries pointing to `https://docs.ewaybillgst.gov.in/` and `https://einvoice1.gst.gov.in/`, which are the e-way bill documentation and e-invoice hosts, plus `.../DIN/DINSearch1` under an unrelated "Ease of Doing Business" label. Those look like menu configuration errors; do not use them. `[OFFICIAL]` (read from the site's own code)
  3. `https://www.cbicddm.gov.in/MIS/Home/DINSearch` - quoted by a Masters India guide as the DIN search page. `[SECONDARY]` — [Masters India via search](https://www.mastersindia.co/blog/document-identification-number-gst/). `cbicddm.gov.in` is the DDM portal named in Circular 128, but the host did not respond to my requests and the site bundle does not reference it, so treat as legacy: `[UNCERTAIN]`.
- No official worked-example DIN appears in the circulars; none located elsewhere.

### Inferences
- **Lenient regex (after removing hyphens/spaces/case):** `^CBIC(20[0-9]{2})(0[1-9]|1[0-2])[A-Z0-9]{9,10}$`. Accept 19- and 20-character forms. Do not reject other eOffice-style numbers outright; label "not in the standard CBIC DIN shape - verify on CBIC".
- Month and year give two free checks: month 01-12, year 2019 or later, not in the future (the DIN system started 8 Nov 2019; reject earlier dates as suspicious).
- App link: primary `https://esanchar.cbic.gov.in/DIN/DINSearch`; secondary `https://www.cbic.gov.in/` ("Verify CBIC-DIN"); tell the user the CBIC site menu has had mis-pointed links.
- GST summons also arrive as e-mail from `@gov.in`/`@nic.in`; a DIN alone is not proof (it is copied in fake summonses).

### Gaps
- ZCDR width and the character set of the random part are not stated on any official page I could read.
- The official 122/2019 PDF is a scan; I relied on a GSTZen reproduction of its text.
- Whether `cbicddm.gov.in/MIS/Home/DINSearch` still resolves from India is unknown (it failed from my environment).

---

## SEBI registration number prefixes (INA, INH, INZ, INP, INM, AIF, DP and others)

### Takeaway
SEBI's own "Recognised Intermediaries" lists (current to 31 Oct 2026) show the patterns directly: investment adviser `INA`+9 digits, research analyst `INH`+9, stock broker `INZ`+9 (plus exchange-segment codes `INB`/`INF`/`INE`+9), portfolio manager `INP`+9, merchant banker `INM`+9, depository participant `IN-DP-<n>-<yyyy>`, AIF `IN/AIF<1-3>/<yy-yy>/<nnnn>`. All are checked by looking the number up on SEBI's lists.

### Cited Findings
All below are `[OFFICIAL]` - read from the SEBI list pages today ("Registered intermediaries as on date Oct 31, 2026").
- Master index of categories and their `intmId`: 13 Investment Adviser, 14 Research Analyst, 9 Merchant Bankers, 33 Portfolio Managers, 30 Stock Brokers (equity), 31 (equity derivative), 32 (currency derivative), 38 (interest-rate derivative), 37 (debt), 2 (commodity derivative), 18 DP-CDSL, 19 DP-NSDL, 16 AIF, 23 Mutual Funds, 10 RTA, 6 Debenture Trustee, 5 Banker to an Issue, 7 CRA, 8 KRA, 27 Custodians, 29 FPIs, 25 FVCI, 21 VCF, 42 REIT, 20 InvIT, 46 Vault Managers. — [SEBI Recognised Intermediaries](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognised=yes)
- Investment Adviser: `INA` + 9 digits; e.g. `INA000013323` (The Alchemists Ark Pvt. Ltd, validity "May 16, 2019 - Perpetual"); also `INA000017523`; a `INA2…` series exists (e.g. `INA200000365`). — [SEBI IA list, 1071 records](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13) and [record page](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13&regno=INA000013323)
- Research Analyst: `INH` + 9 digits; e.g. `INH000011431`; a `INH3…` series exists (e.g. `INH300000211`). — [SEBI RA list, 2329 records](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=14)
- Stock broker: `INZ` + 9 digits (e.g. `INZ000333130`, `INZ000010231`); exchange-specific broker codes `INB…` (cash), `INF…` (equity derivatives), `INE…` (currency) + 9 digits also appear (e.g. `INB260992939` on Metropolitan SE). Records are per exchange. — [SEBI equity brokers, 5010 records](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=30), [equity-derivative list](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=31)
- Portfolio Manager: `INP` + 9 digits (e.g. `INP000008464`, 544 records). — [SEBI PMS list](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=33)
- Merchant Banker: `INM` + 9 digits (e.g. `INM000013581`, 253 records). — [SEBI Merchant Bankers list](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=9)
- Depository Participant: `IN-DP-<n>-<yyyy>` (e.g. `IN-DP-723-2022`, `IN-DP-870-2026`) and older `IN-DP-CDSL-<n>-<yyyy>` (e.g. `IN-DP-CDSL-619-2011`). — [CDSL DP list](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=18), [NSDL DP list](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=19)
- AIF: `IN/AIF<category 1-3>/<yy-yy>/<4 digits>` (e.g. `IN/AIF1/25-26/1857`, `IN/AIF3/16-17/0286`). — [SEBI AIF list, 2056 records](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=16)
- Mutual Fund: `MF/<3 digits>/<yy>/<1-2 digits>` (e.g. `MF/067/11/02`, `MF/020/94/8`). — [SEBI MF list](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=23)
- Others: RTA `INR`+9 digits; Debenture Trustee `IND`+9; Banker to an Issue `INBI`+8 digits (e.g. `INBI00001203`); CRA `IN/CRA/<3 digits>/<yyyy>`; KRA `IN/KRA/<3>/<yyyy>`; FPI `IN<2-letter country>FP<6 digits>` (e.g. `INUSFP170516`); FVCI `IN/FVCI/<yy-yy>/<n>`; VCF `IN/VCF/<yy-yy>/<n>`; REIT `IN/REIT/<yy-yy>/<4 digits>`; Vault manager `IN/VM/<3>/<yyyy>`. — same SEBI list pages (`intmId` 10, 6, 5, 7, 8, 29, 25, 21, 42, 46).
- Deep link supported by the page for the IA list: `...OtherAction.do?doRecognisedFpi=yes&intmId=13&regno=INA000013323` returns exactly that record. — [SEBI IA record page](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13&regno=INA000013323) `[OFFICIAL]`. The same `regno=` parameter for other `intmId`s was not tested: `[UNCERTAIN]`.
- Advertising code: IA/RA ads must show the registration number; individual analysts employed by a research entity need no separate registration, the entity's number is what to check. — [SEBI RA master circular (May 2024)](https://www.sebi.gov.in/sebi_data/attachdocs/may-2024/1716290553655.pdf) `[OFFICIAL-via-search]`
- Verification: SEBI Recognised Intermediaries (above); SEBI Check; for IFSC-registered advisers a different pattern such as `INAIFSC10001` is reported. — [search summary of SEBI lists](https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13) `[UNCERTAIN]`

### Inferences
- **Regexes (all uppercase):**
  - IA `^INA[0-9]{9}$`; RA `^INH[0-9]{9}$`; stock broker `^INZ[0-9]{9}$`; exchange-segment broker `^IN[BFE][0-9]{9}$`; PMS `^INP[0-9]{9}$`; merchant banker `^INM[0-9]{9}$`; RTA `^INR[0-9]{9}$`; debenture trustee `^IND[0-9]{9}$`
  - DP `^IN-DP-(?:(?:CDSL|NSDL)-)?[0-9]{1,4}-[0-9]{2,4}$`; AIF `^IN/AIF[123]/[0-9]{2}-[0-9]{2}/[0-9]{4}$`; MF `^MF/[0-9]{3}/[0-9]{2}/[0-9]{1,2}$`
  - Generic detector for a message scan: `\bIN[A-Z]\d{9}\b|\bIN-DP-[\w-]+\b|\bIN/[A-Z]+\d?/[\d/-]+\b`
- No checksum exists (none documented); validity = presence in the SEBI list. Do not deep-link with `regno=` for non-IA categories until hand-tested.
- Scam angle: a stock tip group "SEBI registered" with an IA/RA number that is real but belongs to another firm is common; the app should advise matching the **name** and the **payment account/UPI** (see SEBI Check) to the number's registrant. Name match is the weak point; recommend the user compares the registered name shown on SEBI with the one in the message.
- App link by prefix: INA -> intmId 13; INH -> 14; INZ/INB/INF/INE -> 30; INP -> 33; INM -> 9; IN-DP-CDSL -> 18; IN-DP-NSDL -> 19; IN/AIF -> 16; MF -> 23.

### Gaps
- No SEBI document explains the meaning of the digit(s) after the letters (e.g. `INA0…` vs `INA2…`, `INH0…` vs `INH3…`); only observed.
- Custodian, InvIT, Designated/Qualified DP, ESG, SM REIT list pages showed no ID shapes through my parser.
- Whether `regno=` deep links work for categories other than IA.

---

## SEBI "@valid" UPI handles for registered intermediaries

### Takeaway
Handle format is `<username>.<suffix>@valid<bank>` (e.g. `abc.brk@validhdfc`), allocated by NPCI, exclusive to SEBI-registered intermediaries collecting funds from investors, in force for investors from 1 Oct 2025. Suffix table is in Annexure B of SEBI circular SEBI/HO/DEPA-II/DEPA-II_SRG/P/CIR/2025/86 dated 11 Jun 2025. Verify any UPI ID or bank account with SEBI Check.

### Cited Findings
- Circular **SEBI/HO/DEPA-II/DEPA-II_SRG/P/CIR/2025/86, 11 Jun 2025**, "Adoption of Standardised, Validated and Exclusive UPI IDs for Payment Collection by SEBI Registered Intermediaries from Investors". — [SEBI circular page](https://www.sebi.gov.in/legal/circulars/jun-2025/adoption-of-standardised-validated-and-exclusive-upi-ids-for-payment-collection-by-sebi-registered-intermediaries-from-investors_94535.html) and [PDF](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`
- Username = readable name chosen by the intermediary + "." + segment abbreviation, generated only through the SI-portal utility. UPI handle = "@valid" combined with the name of the bank (from the 52 self-certified syndicate banks in Annexure C), allocated by NPCI. Examples: `abc.brk`, `xyz.mf`; full handle `abc.brk@validhdfc`, `xyz.mf@validhdfc`. — [SEBI circular PDF](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]` (the circular body has one typo, `abc.bkr@validhdfc`, in para 2.1.ii; the Annexure and the press release use `brk`).
- **Annexure B suffixes (exact):** `brk` stock brokers across segments; `bti` banker to an issue; `dp` depository participants; `ra` research analyst; `ia` investment adviser; `invit` infrastructure investment trust; `mf` mutual fund; `pms` portfolio manager; `sreit` SM REIT; `reit` real estate investment trust. — [SEBI circular PDF, Annexure B](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`
- The suffix is mandatory; the same username may exist across banks (`abc.brk@validhdfc` and `abc.brk@validicici`) but must be unique within a bank; an intermediary with several registration categories needs separate handles per category. — circular FAQ, [SEBI circular PDF](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`
- "@valid" UPI IDs are exclusively for payment collection by intermediaries registered with SEBI under merchant category code 6211. — [SEBI circular PDF, para 3.1](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`
- Visual cue: a white "thumbs-up inside a green triangle" icon on the confirmation screen and on the QR code; its absence is a caution. Per-transaction cap up to Rs 5 lakh/day for capital-market UPI. — [SEBI circular PDF](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`
- **Launch/availability:** "available for investors ... w.e.f. October 01, 2025" (circular para 8) and SEBI Press Release **PR No. 64/2025, 1 Oct 2025**, announcing that Validated UPI Handles and SEBI Check "are now live"; major brokers (>90% of investors) and all mutual funds had adopted them. — [SEBI PR 64/2025](https://www.sebi.gov.in/sebi_data/attachdocs/oct-2025/1759322811695.pdf) `[OFFICIAL]`
- Investors may still pay by NEFT/RTGS/IMPS/cheque; "if an investor opts to use UPI ... they have to do so only using the new UPI IDs" of the intermediary. Investors do not need their own @valid handle. — [SEBI circular PDF, FAQ](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`
- Existing mutual-fund SIP mandates continue; new SIPs and renewals/extensions must use new IDs (para 6.1.3). — [SEBI circular PDF](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`
- 7 Aug 2026 SEBI clarification (relayed by exchanges): all investor-facing ("upstreaming") bank accounts of stock-exchange Members must be linked to an @valid UPI ID, compliance by 6 Sep 2026; new such accounts must be linked at opening. — [MSEI circular MSE/MEM/19545/2026, 12 Aug 2026](https://www.msei.in/SX-Content/Circulars/2026/August/Circular-19545.pdf) `[SECONDARY]` (exchange circular quoting SEBI)
- **Verification:** SEBI Check - verifies authenticity of an intermediary's bank account (account number + IFSC) or @valid UPI ID, for UPI or NEFT/RTGS/IMPS payments, at `https://siportal.sebi.gov.in/intermediary/sebi-check` or in SEBI's Saarthi app. — [SEBI PR 64/2025](https://www.sebi.gov.in/sebi_data/attachdocs/oct-2025/1759322811695.pdf) `[OFFICIAL]` (the page itself returned HTTP 505 to my HEAD request; not rendered).
- Exact bank handle strings are documented only for `validhdfc` and `validicici`; the circular says "@valid combined with the name of the bank" without a table of strings. — [SEBI circular PDF](https://www.sebi.gov.in/sebi_data/attachdocs/jun-2025/1749641449497.pdf) `[OFFICIAL]`

### Inferences
- **Regex:** `^[a-z0-9][a-z0-9._-]{0,60}\.(brk|bti|dp|ra|ia|invit|mf|pms|sreit|reit)@valid[a-z]{2,20}$` (case-insensitive input, compare lower-case). Split with `rsplit('.', 1)` on the local part so dotted usernames still work.
- Decision table for the app: (a) matches the regex -> "format of a SEBI validated handle; still verify in SEBI Check"; (b) contains `.brk`/`.mf`/etc. but not `@valid…` -> **strong scam flag** (impersonating the scheme); (c) any other UPI ID asked for "investment", "IPO", "SIP", "trading fund" payments by a claimed intermediary -> warn that registered intermediaries are meant to use @valid and tell the user to check the green-triangle icon and SEBI Check; (d) not every legitimate payee uses UPI, so absence of @valid is a caution, not proof of fraud (investors may pay by NEFT).
- Unknown bank suffix after `@valid`: accept the pattern but mark "bank handle not in my table"; do not hard-code a full bank list, only the two documented ones.
- Charset of the username before the suffix is not specified; the permissive character class above is my choice: `[UNCERTAIN]`.

### Gaps
- Complete list of `@valid<bank>` handle strings is not in the circular.
- SEBI Check page was not renderable by my tooling; its exact input fields not confirmed beyond the press release.
- SEBI's own FAQ page for investors (Sep 2025, as hosted by APMI/Edelweiss) not read.

---

## AMFI ARN for mutual fund distributors

### Takeaway
ARN is AMFI's registration number for mutual-fund distributors (overseas distributors get an `OD`-prefixed series). AMFI's Locate Distributor tool (search by name or ARN) and its "Invalid ARN" list are the verification route. The digit count/format of an ARN is stated only by secondary sources.

### Cited Findings
- AMFI registration number (ARN) is the unique number allotted to a distributor; a non-individual entity needs at least one employee with a valid EUIN; renewal is online via AMFI; "a separate series of ARN, prefixed with letters 'OD'" is used for overseas distributors. — [AMFI Master Circular for MF Distributors (AMFI/MFD-CIR/32/2025-26)](https://www.amfiindia.com/uploads/AMFI_Master_Cicular_for_MF_Ds_3c7f5ee44f.pdf) `[OFFICIAL]`
- Locate a Mutual Fund Distributor tool ("Enter distributor details (Name/AR[N]...)", filter by type and location). — [AMFI Locate Distributor](https://www.amfiindia.com/locate-distributor) `[OFFICIAL]`
- Invalid ARN list: ARNs of non-individual distributors still carrying advisory terms such as "Adviser" were declared INVALID, with AMCs not accepting their business from 1 Jul 2021 until they change names. — [AMFI Invalid ARN list](https://www.amfiindia.com/locate-distributor/invalid-arn) `[OFFICIAL]`
- Investors "must ensure that they invest through AMFI registered distributors and that the distributor has a valid AMFI Registration Number (ARN)". — [SEBI FAQs for mutual fund investors](https://www.sebi.gov.in/sebi_data/faqfiles/sep-2024/1727242783639.pdf) `[OFFICIAL-via-search]`
- AMFI documents say a distributor needs a valid ARN at all times and that transactions received under an invalid ARN are processed under Direct Plan (statement seen in a search extract of AMFI material; the Master Circular above also discusses Direct Plan processing when an ARN is cancelled). — [AMFI Master Circular for MFDs](https://www.amfiindia.com/uploads/AMFI_Master_Cicular_for_MF_Ds_3c7f5ee44f.pdf) `[OFFICIAL-via-search]`
- Written form is commonly `ARN-<digits>`; sources disagree on length ("7-digit" in one guide, "alphanumeric" in another) and I found no AMFI statement of length. — [Rupeezy ARN guide and others, via search](https://rupeezy.in/blog/arn-number-in-mutual-fund) `[SECONDARY]` / `[UNCERTAIN]`

### Inferences
- **Regex (lenient):** `^ARN[- ]?[0-9]{3,7}$`; overseas: `^ARN[- ]?OD[0-9A-Z]{1,8}$` is `[UNCERTAIN]` (only the "OD" prefix is documented).
- An ARN proves registration to sell MF products only; it does not authorise guaranteed returns, "SEBI-approved" schemes, or taking money into a personal account. Combine with the `@valid.mf` / bank-account check (SEBI Check) when payment details are in the message.
- Link: `https://www.amfiindia.com/locate-distributor` and `https://www.amfiindia.com/locate-distributor/invalid-arn`.

### Gaps
- Exact ARN digit length and the format of the number as printed by AMFI are unconfirmed.
- EUIN format not confirmed on an official page (commonly `E` + 6 digits, from my recollection only: `[UNCERTAIN]`); no public EUIN lookup found.

---

## IRDAI registration/licence numbers (insurers, brokers, corporate agents, agents)

### Takeaway
IRDAI numbers do not follow one checksum pattern. Insurers and brokers appear as plain integers on IRDAI lists ("CoR No." / registration number); corporate-agent licences are reported as `CA` + digits (weak source). IRDAI's Agent Locator and PAN lookup, and its broker/insurer lists, are the verification route.

### Cited Findings
- Insurer registration number is a plain integer (e.g. "The registration number allotted by the IRDA is 111" for SBI Life). — [IRDAI-hosted SBI Life document](https://irdai.gov.in/documents/37343/563751/SBI+Life+-+Kalyan+ULIP+Plus_2013-14.pdf/b8990e4c-25b0-525c-083e-3c97bac174a9?version=1.1&t=1668077631309) `[OFFICIAL-via-search]`
- IRDAI broker lists use a "CoR No." column with plain numbers (e.g. 124, 126) and categories "Direct Broker (Life & General)", "Direct Broker (General)", "Composite Broker". — [IRDAI Insurance Brokers list](https://www.irdai.gov.in/ADMINCMS/cms/NormalData_Layout.aspx?page=PageNo2120&mid=9.3.7) and [IRDAI Brokers page](https://new.irdai.gov.in/brokers1) `[OFFICIAL-via-search]`
- Brokers must show their IRDAI registration number, category and validity in correspondence. — [IRDAI (Insurance Brokers) Regulations, 2018](https://policyholder.gov.in/documents/37343/602265/Insurance+Regulatory+and+Development+Authority+of+India+(Insurance+Brokers)+Regulations,+2018.pdf/03fde417-670f-f26f-55fa-f56e0d165c7c?version=1.7&t=1665253680640&download=true) `[OFFICIAL-via-search]`
- A composite corporate agent states its licence as `CA1085`, the only observed corporate-agent number style, from the company's own site. — [search extract of a company page](https://policyholder.gov.in/corporate-agents) `[UNCERTAIN]` (the IRDAI page I fetched (policyholder.gov.in/corporate-agents) did not print numbers in the text I could parse)
- IRDAI database for individual agents is keyed on PAN: "by providing Pan no. of an agent the aspirant can collect details of that particular agent." — [IRDAI individual agents FAQ](https://irdai.gov.in/intermediaries/individual-agents) `[OFFICIAL]`
- Agent Locator: public tool that filters by name, licence no, agent ID, state, insurance type, district, insurer, PIN; separate PAN/Aadhaar lookup with captcha. Both URLs responded HTTP 200 today. — [IRDAI Agent Locator](https://agencyportal.irdai.gov.in/PublicAccess/AgentLocator.aspx), [PAN lookup](https://agencyportal.irdai.gov.in/PublicAccess/LookUpPAN.aspx) `[OFFICIAL]`
- IRDAI policyholder site header shows toll-free **155-255**. — [policyholder.gov.in corporate agents page](https://policyholder.gov.in/corporate-agents) `[OFFICIAL]`
- The "IRDA/DB ..." broker-code style was not confirmed by any source. — `[UNCERTAIN]`

### Inferences
- Because there is no confirmed pattern, do not regex-validate. Detect candidates by context words ("IRDAI", "licence no", "CoR", "reg no", "corporate agent") followed by `\b(CA)?\s?-?\d{2,6}\b` and send to the lookup rather than saying valid/invalid.
- Scam tell: "IRDAI officer"/"unclaimed policy bonus"/"insurance refund" calls; IRDAI does not sell policies or collect fees for bonus release (general knowledge; no source retrieved, `[UNCERTAIN]`).
- Warn users never to enter their Aadhaar/PAN on a lookalike site; the IRDAI PAN lookup takes the **agent's** PAN, which the user may not know.

### Gaps
- No official statement of licence-number formats for corporate agents, brokers or individual agents.
- IRDAI list pages found are dated snapshots (broker list "as on 01.12.2022", corporate agent list "Jul 2021" in the index): current lists were not retrieved.

---

## RBI NBFC Certificate of Registration (CoR) number

### Takeaway
RBI press releases that cancel NBFC registrations print CoR numbers as `N-13.01906` / `B-13.02504` style (letter-hyphen, two digits, dot, five digits) and older `14.00300` without a letter. The authority to operate is the CoR on RBI's NBFC list; RBI also runs a Digital Lending Apps directory (from 1 Jul 2025).

### Cited Findings
- CoR shapes quoted in RBI cancellation releases (extracts seen via search, extraction text partly garbled): `N-13.01906` (cancellation date 31 Aug 2026), `B-13.02504` (13 Jul 2026), `B-13.01612` (22 May 2026, in the 10 Jun 2026 release for 135 NBFCs), `N-13.02199` (Feb 2023), `14.00300` (N.Y. Leasing, May 2025, no letter prefix). — [RBI PR 10 Jun 2026 (135 NBFCs)](https://rbidocs.rbi.org.in/rdocs/PressRelease/PDFs/PR428C79CA02949F748F39C6707948A87255D.PDF) and [RBI PR 29 May 2025](https://rbidocs.rbi.org.in/rdocs/PressRelease/PDFs/PR429C7906552926E460191F9F43EE04EB0EE.PDF) `[OFFICIAL-via-search]` (RBI blocks scripted fetches; which individual release carries each other number was not pinned; see the RBI press-release index at [rbi.org.in](https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=63611))
- Section 45-IA of the RBI Act 1934 bars NBFC business without a CoR; a deposit-taking NBFC needs separate authorisation, so a CoR alone does not authorise deposits. — [RBI NBFC pages via search](https://rbi.org.in/Scripts/NBFC_Pub_lic.aspx) `[OFFICIAL-via-search]`
- RBI's list of NBFCs is on `rbi.org.in` ("NBFC List" under Non-Banking Financial Companies); the version indexed was dated 31 Jan 2022, so the current list location must be checked by hand. — [RBI NBFC list page](https://rbi.org.in/Scripts/NBFC_Pub_lic.aspx) `[OFFICIAL-via-search]` (page returned "Unauthorised Access" to my fetch)
- Digital Lending Apps directory: operational on RBI's website from 1 Jul 2025, listing DLAs deployed by RBI-regulated entities, to let borrowers check an app's association with a regulated lender. — [PIB: Digital Lending Apps / directory](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2241255&reg=3&lang=2) and [PIB: strengthened digital-lending framework](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2287195&lang=1&reg=3) `[OFFICIAL-via-search]`
- MeitY had blocked 87 illegal loan apps under s69A IT Act as of a July 2026 PIB release. — [PIB PRID 2200567](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2200567&reg=3&lang=1) `[OFFICIAL-via-search]`

### Inferences
- **Regex:** `^(?:[A-Z]-)?[0-9]{2}\.[0-9]{5}$`. The meaning of the letter prefix (A, B, N ...) was not sourced; do not interpret it.
- A message quoting a "RBI registration" for a lender should be checked against RBI's NBFC list and, for apps, the DLA directory; an app absent from the directory is a strong flag for illegal lending.
- The CoR belongs to the company, not the app: match company name + CIN + the CoR.

### Gaps
- RBI's own page defining the CoR number format was not accessible; shapes are inferred from cancellation press releases.
- Current URL of the up-to-date NBFC list and the DLA directory could not be fetched.
- Meaning of prefixes `A-`, `B-`, `N-`.

---

## Udyam registration number

### Takeaway
Official format string is `UDYAM-XX-00-0000000` (19 characters including hyphens: `UDYAM`, two letters, two digits, seven digits). The verification page is `udyamregistration.gov.in/Udyam_Verify.aspx`. The meaning of the two letter and two digit blocks (state and district) is commonly stated but unconfirmed.

### Cited Findings
- Official portal verification page "Udyam verification" exists at `https://www.udyamregistration.gov.in/Udyam_Verify.aspx` and the format string used is `UDYAM-XX-00-0000000`. — [Udyam verification page (listed in search; page body not readable by my fetcher)](https://www.udyamregistration.gov.in/Udyam_Verify.aspx) `[OFFICIAL-via-search]`
- Sample on an older MSME site: `UDYAM-XY-07-1234567`. — [ideas.msme.gov.in](http://ideas.msme.gov.in/user/Registration.aspx) `[OFFICIAL-via-search]`
- Portal home notes: Aadhaar is the only identifier needed; PAN and GSTIN required from 1 Apr 2021; UAM (Udyog Aadhaar) holders must re-register; Udyam Assist Platform is a separate option for informal micro enterprises; portal has "Verify Udyog Aadhaar", "Print UAM certificate", "Forgot Udyam/UAM number". — [Udyam Registration home](https://www.udyamregistration.gov.in/Udyam_Verify.aspx) `[OFFICIAL]` (fetched page text)
- Page title states: "This is official website of Govt. of India, Ministry of MSME. No other website/portal/app is official. MSMEs are requested to do MSME Registration here only"; registration is free. — [Udyam portal (listed in search)](https://www.udyamregistration.gov.in/UdyamRegistrationExist.aspx) `[OFFICIAL-via-search]`
- State code in the first block and legacy UAM format (`XX00X0000000`: two letters, two digits, one letter, seven digits): [XFlowPay](https://www.xflowpay.com/blog/udyam-registration-number) `[SECONDARY]`; Udyam Assist numbers (`UDYAM-I...`) are checked at `udyamassist.gov.in` per the same guides `[SECONDARY]`.

### Inferences
- **Regex:** `^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$` after normalising a missing hyphen; also accept old UAM `^[A-Z]{2}[0-9]{2}[A-Z][0-9]{7}$` as "legacy, not valid for Udyam" `[SECONDARY]`.
- Scam angle: sites charging for "Udyam registration", "renewal" or "certificate" are lookalikes; the real service is free (page text above).
- Link: `https://www.udyamregistration.gov.in/Udyam_Verify.aspx`.

### Gaps
- The verify page's field labels and the meaning of the 2-letter / 2-digit blocks (state / district) are not confirmed on an official page.
- Digit count wording on the portal ("19 digit") is loose: only nine characters are digits.

---

## IFSC, UPI ID, Indian mobile number

### Takeaway
IFSC is 11 characters: 4-letter bank code, a fixed `0`, 6-character branch code (RBI NEFT FAQ). UPI IDs are `username@handle`; I found no official character/length rules. Indian mobile numbers are 10 digits (without +91); in practice they start with 6-9, though the 2003 numbering plan text still reserves levels 7 and 8.

### Cited Findings
- IFSC: "11-digit code with the first 4 alpha characters representing the bank, and the last 6 characters representing the branch"; the 5th character is a zero "retained for future use"; layout follows the SWIFT pattern. — [RBI NEFT FAQ (Id=274)](https://www.rbi.org.in/Commonman/English/Scripts/FAQs.aspx?Id=274) and [RBI FAQ Id=60](https://www.rbi.org.in/Scripts/FAQDisplay.aspx?Id=60) `[OFFICIAL-via-search]`
- Worked IFSC from an RBI list: `ADCB0000001` (Abu Dhabi Commercial Bank). — [RBI RTGS participants list](https://www.rbi.org.in/upload/rtgs/pdf/list%20of%20rtgs%20participants.pdf) `[OFFICIAL-via-search]`
- UPI ID has a user prefix and a handle suffix (`username@upihandle`); registration creates a default `mobilenumber@upi`. — [NPCI brand guidelines / BHIM FAQ via search](https://www.bhimupi.org.in/faq-s) `[OFFICIAL-via-search]`
- A 45-character ceiling for the full UPI ID is stated in a BHIM document on UPI use in public issues; scope (ASBA only vs all UPI) unclear. — [BHIM UPI IPO document](https://www.bhimupi.org.in/PDF/bhim/ipo_upi.pdf) `[OFFICIAL-via-search]` / `[UNCERTAIN]`
- Mobile: fixed and mobile numbers are "10 digits excluding the country code". — [TRAI consultation paper](https://trai.gov.in/sites/default/files/2024-09/CP_20092019.pdf) `[OFFICIAL-via-search]`
- National Numbering Plan 2003 (hosted by DoT): all numbers uniformly 10-digit national significant numbers; "level '9' except '90', '95' and '96' reserved for cellular mobile services"; "level '7' & '8' are not being allocated and the same are reserved for new services." — [DoT National Numbering Plan 2003](https://www.dot.gov.in/static/uploads/2026/05/9ed5f19dbf38307edc38a54377d82cd5.pdf) `[OFFICIAL]`
- TRAI's own paper says some sublevels of 7 and 8, and vacated sublevels of 6, have been allocated to mobile, which conflicts with the 2003 plan text. — [TRAI consultation paper](https://trai.gov.in/sites/default/files/2024-09/CP_20092019.pdf) `[OFFICIAL-via-search]`
- TRAI's Feb 2025 numbering-plan recommendation concerns fixed-line revision; no change to the 10-digit mobile format found. — [TRAI recommendation 06 Feb 2025](https://www.trai.gov.in/sites/default/files/2025-02/Recommendation_06022025.pdf) `[OFFICIAL-via-search]`

### Inferences
- **IFSC regex:** `^[A-Z]{4}0[A-Z0-9]{6}$`. IFSC has no checksum. Bank code can be matched to the first 4 letters of known banks if you ship a table (not sourced here). To validate an intermediary's account, use SEBI Check.
- **UPI ID regex (heuristic, unsourced):** `^[A-Za-z0-9._-]{2,64}@[A-Za-z][A-Za-z0-9]{2,40}$`; total length <= 80 as a soft cap; if the part before `@` is exactly 10 digits starting 6-9 treat as a mobile-number VPA. Mark all UPI regex results "format only"; handle allow-lists are not sourced.
- **Mobile regex:** `^(?:\+?91[\s-]?|0)?[6-9][0-9]{9}$` after removing spaces and brackets. For anything that is not `+91`/`91`/`0`-prefixed 10 digits, flag as an international or short-code sender (typical in WhatsApp/job/crypto scams, an inference) rather than invalid. 10-digit numbers starting 0-5 are not mobile numbers (fixed/other), also an inference from the 6-9 allocation.

### Gaps
- NPCI's technical rules for VPA characters/length (NPCI and bhimupi.org.in returned 403).
- Current DoT numbering plan after 2003 (a 2025/26 revision was not found); active mobile prefix allocation list not found.
- No sourced list of UPI PSP handles (e.g. `@oksbi`, `@ybl`).

---

## Official helplines and next-step links

### Takeaway
Use 1930 / cybercrime.gov.in for money lost, Sanchar Saathi Chakshu for suspicious calls/SMS/WhatsApp/links (report within 30 days), SEBI SCORES for securities complaints, RBI Sachet/CMS for lenders and deposit-takers, and the ITD / CBIC / eCourts / SEBI Check pages above to verify a document.

### Cited Findings
- National Cyber Crime Helpline **1930** ("In case of Cyber Financial Fraud, for immediate reporting, call 1930 (earlier 155260), 24x7") and the National Cyber Crime Reporting Portal `https://cybercrime.gov.in`. — [cybercrime.gov.in acceptance page (via search)](https://cybercrime.gov.in/Webform/Accept.aspx) `[OFFICIAL-via-search]` (the page body returned only a title to my fetcher)
- CFCFRMS under I4C links state police, banks, wallets and other intermediaries to freeze fraudulent transfers; a PIB release of Oct 2025 cites over Rs 5,489 crore saved on over 17.82 lakh complaints. — [PIB, Curbing Cyber Frauds in Digital India](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/oct/doc2025107659501.pdf) `[OFFICIAL-via-search]`
- June 2026 PIB: Home Minister directed a national-level 1930 call centre to pick up calls unanswered at state level. — [PIB PRID 2274249](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2274249&reg=48&lang=2) `[OFFICIAL-via-search]`
- **Sanchar Saathi / Chakshu** `https://sancharsaathi.gov.in/sfc/`: three flows: (1) report suspected web links received via SMS/RCS/iMessage/email/social media, (2) report suspected fraud communication by call, SMS or WhatsApp (examples: bank/wallet/SIM/gas/electricity/KYC update, impersonation of government officials, sextortion), (3) report spam/UCC; reports within 30 days are acted on; "If you have already lost money, please report at cyber crime helpline 1930 or cybercrime.gov.in." — [Sanchar Saathi Chakshu page](https://sancharsaathi.gov.in/sfc/) `[OFFICIAL]`
- **SEBI SCORES** `https://scores.sebi.gov.in/`: grievances sent to SEBI e-mail will not be attended to, use the portal; SEBI toll-free **1800 266 7575 / 1800 22 7575** (9:00-18:00); technical help 022-2644-9377 / 022-4045-9377 / 022-2075-2247 and scoreshelp@sebi.gov.in; menu includes "Entity Status". — [SCORES home](https://scores.sebi.gov.in/) `[OFFICIAL]`
- **SEBI Check** `https://siportal.sebi.gov.in/intermediary/sebi-check` and SEBI Saarthi app. — [SEBI PR 64/2025](https://www.sebi.gov.in/sebi_data/attachdocs/oct-2025/1759322811695.pdf) `[OFFICIAL]`
- **RBI Sachet** `https://sachet.rbi.org.in` (complaints against entities collecting deposits/money illegally) and **RBI CMS** `https://cms.rbi.org.in` (complaints against RBI-regulated entities). Both hosts return a bot/unauthorised page to scripted GETs. A 2021 release gives another address (`cmc.rbi.org.in`), so confirm the live URL on rbi.org.in. — [PIB: RBI cautions against unauthorised digital lending platforms/apps](https://www.pib.gov.in/PressReleasePage.aspx?PRID=1683572&reg=48&lang=2) `[OFFICIAL-via-search]`; [PIB: Government and RBI strengthen digital lending ecosystem](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2287195&lang=1&reg=3) `[OFFICIAL-via-search]`
- Income-tax e-Filing helplines 1800 103 0025 / 1800 419 0025; Protean PAN/TAN +91-20-27218080. — [ITD user manual](https://www.incometax.gov.in/iec/foportal/help/all-topics/e-filing-services/authenticate-noticeorder-issued-itd-UM) `[OFFICIAL]`
- IRDAI toll-free 155-255. — [policyholder.gov.in](https://policyholder.gov.in/corporate-agents) `[OFFICIAL]`
- eCourts SMS service: `ECOURTS <CNR>` to 9766899899. — [eCourts home](https://ecourts.gov.in/ecourts_home/) `[OFFICIAL]`

### Inferences
- Suggested routing logic: money already sent -> 1930 first (speed matters), then cybercrime.gov.in; suspicious call/SMS/WhatsApp/URL with no loss -> Chakshu; securities-related -> SEBI Check then SCORES; lender/deposit/app -> RBI NBFC list, DLA directory, then Sachet/CMS; notice -> ITD authenticate / CBIC DIN / eCourts portal.
- Show the 30-day Chakshu window in the UI.
- Never ask the user to paste the full scam message to a server; keep processing local.

### Gaps
- Direct fetches of cybercrime.gov.in, sachet.rbi.org.in and cms.rbi.org.in did not return readable content (SPA/bot protection).
- No current WhatsApp/e-mail alternative channels for 1930 confirmed.

---

## Consolidated implementation sheet (regexes and reference code)

### Takeaway
All regexes below were written from the findings above. Only the checksum code (Verhoeff, Luhn mod 36) is algorithmic; PAN, CIN, LLPIN, SEBI, IFSC, Udyam have no usable public checksum.

### Cited Findings
- Algorithms rely on: Verhoeff worked example (`236 -> 3`, `2363` valid) from [Wikipedia, Verhoeff algorithm](https://en.wikipedia.org/wiki/Verhoeff_algorithm) `[SECONDARY]`; Luhn mod N with the 36-symbol alphabet from [Wikipedia, Luhn mod N algorithm](https://en.wikipedia.org/wiki/Luhn_mod_N_algorithm) `[SECONDARY]`; documented valid GSTIN `27AAPFU0939F1ZV` from [python-stdnum](https://arthurdejong.org/python-stdnum/doc/stdnum.in_.gstin) `[SECONDARY]`.

### Inferences
- **I ran this exact table of regexes against the documented samples in my sandbox** `[SANDBOX]`: GSTIN `27AAPFU0939F1ZV`, PAN `AFZPK7190K`, CIN `L01631KA2010PTC096843`/`L35301KA1963GOI001622`/`U80100AP1992NPL014292`, CNR `MHAU019999992015`, IFSC `ADCB0000001`, Udyam `UDYAM-XY-07-1234567`, SEBI numbers from the SEBI lists, `abc.brk@validhdfc`, ITD DIN shape, NBFC `N-13.01906`: all matched. (The CIN pattern in the earlier draft that capped year at 19xx/20xx wrongly rejected `U74999RJ1857PLC000649`; the table below uses `[0-9]{4}`.)

```python
import re
PAT = {
 "GSTIN":  r"^(0[1-9]|[12][0-9]|3[0-8]|9[79])[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$",
 "PAN":    r"^[A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z]$",
 "AADHAAR":r"^[2-9][0-9]{11}$",                       # + Verhoeff; NEVER store
 "CIN":    r"^[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$",
 "LLPIN":  r"^[A-Z]{3}-[0-9]{4}$",
 "CNR":    r"^[A-Z]{4}[A-Z0-9]{2}[0-9]{6}[0-9]{4}$",
 "ITD_DIN":r"^ITBA/[A-Z]{2,4}/[A-Z]/[^/\s]+/[0-9]{4}-[0-9]{2}/[0-9]{6,12}\([0-9]\)$",
 "CBIC_DIN":r"^CBIC(20[0-9]{2})(0[1-9]|1[0-2])[A-Z0-9]{9,10}$",   # strip '-' and spaces first
 "SEBI_INX":r"^IN[AHZPMRD][0-9]{9}$|^IN[BFE][0-9]{9}$",
 "SEBI_DP":r"^IN-DP-(?:(?:CDSL|NSDL)-)?[0-9]{1,4}-[0-9]{2,4}$",
 "SEBI_AIF":r"^IN/AIF[123]/[0-9]{2}-[0-9]{2}/[0-9]{4}$",
 "SEBI_MF":r"^MF/[0-9]{3}/[0-9]{2}/[0-9]{1,2}$",
 "VALID_UPI":r"^[a-z0-9][a-z0-9._-]{0,60}\.(brk|bti|dp|ra|ia|invit|mf|pms|sreit|reit)@valid[a-z]{2,20}$",
 "ARN":    r"^ARN[- ]?[0-9]{3,7}$",
 "NBFC_COR":r"^(?:[A-Z]-)?[0-9]{2}\.[0-9]{5}$",
 "UDYAM":  r"^UDYAM-[A-Z]{2}-[0-9]{2}-[0-9]{7}$",
 "IFSC":   r"^[A-Z]{4}0[A-Z0-9]{6}$",
 "MOBILE_IN":r"^(?:\+?91[\s-]?|0)?[6-9][0-9]{9}$",
}

# --- GSTIN check char: Luhn mod 36 over first 14 chars (verified on 27AAPFU0939F1ZV)
CP = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def gstin_check_char(g14: str) -> str:
    factor, total = 2, 0
    for ch in reversed(g14):
        a = factor * CP.index(ch)
        factor = 1 if factor == 2 else 2
        total += a // 36 + a % 36
    return CP[(36 - total % 36) % 36]
def gstin_ok(g: str) -> bool:
    return bool(re.match(PAT["GSTIN"], g)) and gstin_check_char(g[:14]) == g[14]

# --- Verhoeff (Aadhaar). Validate in memory only; never persist the number.
_d = [[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],
      [4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],
      [8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]]
_p = [[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],
      [9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],[2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8]]
def verhoeff_ok(num: str) -> bool:
    c = 0
    for i, ch in enumerate(reversed(num)):
        c = _d[c][_p[i % 8][int(ch)]]
    return c == 0
# test vectors (NOT Aadhaar numbers): verhoeff_ok("2363") and verhoeff_ok("123451") are True; "2364" is False
```

### Gaps
- Anything marked `[UNCERTAIN]` above should not be presented to end users as a hard "invalid"; present as "unrecognised format, verify at the official link".
- No official worked examples were found for: GSTIN, Aadhaar (none should exist publicly), CBIC DIN, LLPIN, ARN, IRDAI numbers, RBI CoR (only observed from cancellation notices), CIN (only from MCA lists seen via search).
