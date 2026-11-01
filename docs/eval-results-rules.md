# Parakh evaluation (rules only mode)

31 forwards: 24 scam examples from official advisories, news and family WhatsApp groups (some partial or rebuilt from descriptions; see test_forwards), 7 genuine messages.
A regression gate, not a benchmark: too few forwards to claim an accuracy figure.
The warning-sign rules were written from the same SEBI, RBI, I4C and PIB advisories these examples come from,
so expect lower numbers on messages the team has never seen. Add fresh forwards before quoting results.

| Measure | Result |
|---|---|
| Scams rated **High risk** | 20 of 24 (95% range 64% to 93%) |
| Scams rated **Be careful** (not confirmed, not condemned) | 4 of 24 |
| Scams wrongly rated **Consistent** (the dangerous error) | 0 of 24 |
| Genuine messages wrongly rated **High risk** | 0 of 7 (95% range 0% to 35%) |
| Genuine messages rated **Consistent** | 2 of 7 |
| Median time per check | 0.0 s |

| ID | Real scam? | Result | Items checked | Warning signs |
|---|---|---|---|---|
| INV-1 | yes | CAUTION | - | tip_group |
| INV-2 | yes | HIGH_RISK | www.yashtradingacademy.com: NOT_LISTED | guaranteed_returns, sebi_claim_no_number, official_via_link, urgency |
| INV-3 | yes | HIGH_RISK | https://t.me/Rahultrade1: CONFIRM_OFFICIALLY; https://cosmofeed.com/vig/643d392830ae100021fa23a1: CONFIRM_OFFICIALLY | guaranteed_returns, tip_group |
| INV-4 | yes | HIGH_RISK | - | sebi_claim_no_number, admits_unregistered, tip_group |
| INV-5 | yes | HIGH_RISK | Lazzard Asset Management India: NOT_FOUND | sebi_claim_no_number, tip_group, pay_to_resolve |
| TAX-1 | yes | HIGH_RISK | https://wwtax.icu: INVALID | official_via_link |
| TAX-2 | yes | HIGH_RISK | ITBA/AST/F/17/2025-26/1035917840: CONFIRM_OFFICIALLY; api.teledema.scoding.com/storage/foi/index.html: INVALID | official_via_link |
| TAX-4 | yes | CAUTION | - | unexpected_money |
| TAX-5 | yes | HIGH_RISK | - | unexpected_money, bank_details_link |
| KYC-1 | yes | HIGH_RISK | UPDATE.apk: INVALID | kyc_block, app_outside_store |
| KYC-4 | yes | HIGH_RISK | - | urgency, kyc_block |
| KYC-5 | yes | HIGH_RISK | - | urgency, kyc_block |
| KYC-8 | yes | HIGH_RISK | Challan.apk: INVALID | official_via_link, app_outside_store |
| DA-1 | yes | HIGH_RISK | - | threat, pay_to_resolve, secrecy |
| DA-3 | yes | HIGH_RISK | - | threat, secrecy |
| JOB-3 | yes | HIGH_RISK | - | task_job, pay_to_resolve |
| UGC-A | yes | HIGH_RISK | Viswakarma Open University for Self-Employment: ON_WARNING_LIST | urgency |
| UGC-B | yes | HIGH_RISK | All India Institute of Public & Physical Health Sciences (AIIPHS) State Government University: ON_WARNING_LIST | pay_to_resolve |
| SCH-1 | yes | CAUTION | - | unexpected_money |
| SCH-2 | yes | CAUTION | - | unexpected_money |
| GEN-3 | no | CAUTION | U65100KA2016PTC092879: CONFIRM_OFFICIALLY; INZ000301838: MATCHED; ARN-111686: MATCHED; Groww Invest Tech Pvt Ltd: MATCHED | - |
| GEN-AMFI | no | CONSISTENT | ARN-108: MATCHED | - |
| GEN-LIC | no | CONSISTENT | Life Insurance Corporation of India: MATCHED | - |
| FRESH-1 | yes | HIGH_RISK | - | urgency, kyc_block |
| FRESH-2 | yes | HIGH_RISK | - | urgency, kyc_block |
| FRESH-3 | yes | HIGH_RISK | - | unexpected_money, urgency |
| FRESH-4 | yes | HIGH_RISK | - | unexpected_money, official_via_link |
| FRESH-5 | no | CAUTION | - | - |
| FRESH-6 | no | CAUTION | - | - |
| FRESH-7 | no | CAUTION | - | - |
| FRESH-8 | no | CAUTION | Care Health Insurance: NEEDS_CLARIFICATION | - |
