# Audit appendix — every claim, every quote, verified

Each citation below was re-verified at build time: the cited file was opened and the
quote checked as a substring of the exact cited line. Regenerate anytime with
**Result: 86 citations verified, 0 failed.**

`python3 ask.py build`; verify without building via `python3 ask.py check`.

## Claims

### `saas.booked_subtotal`
*confidence: high*

Q1 2026 Software & SaaS spend as booked is $81,000; the 15 line items sum to the stated subtotal exactly, and the CFO confirmed the figure in #finance.

- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:24` — “Software & SaaS subtotal,81000”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:144` — “subtotal as listed is $81k for the quarter”

### `saas.amplitude_duplicate_suspected`
*confidence: moderate*

Two SaaS lines, 'Amplitude' and 'Amplitude Analytics', each post $7,500 with identical notes. Finance's own analyst is '90% sure' it is one product entered twice, but the invoice was never pulled; the CSV was left as-is. No Amplitude invoice, contract, or vendor statement exists in the bundle, so the duplicate is suspected, not verified.

- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:12` — “,Amplitude,7500,”
- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:13` — “Amplitude Analytics,7500”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:147` — “the same product entered twice”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:150` — “that smells like a double-count”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:153` — “leaving the CSV as-is until I can confirm”

### `saas.salesforce_timing`
*confidence: high*

Q1 posts Salesforce at $12,000. The $60k/yr renewal was signed 2026-05-14 (Q2) covering 'through next May', so it does not restate Q1. Run-rate impact is +$3,000/quarter from Q2 2026. The 2026-05-28 finance note's direction is backwards: $12,000/qtr annualizes to $48,000, BELOW the $60k contract, not above it.

- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:9` — “Salesforce,12000”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:119` — “closed the Salesforce renewal. $60k for the year, locked”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/finance_review_2026-05-28.md:23` — “the current quarterly P&L figure looks higher than a $60k annual would imply”

### `saas.salesforce_check_still_open`
*confidence: high*

The action to reconcile the posted Salesforce figure against the signed contract was due 'next week' from 2026-05-28 and shows no closure anywhere in the corpus through 2026-06-17.

- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/finance_review_2026-05-28.md:37` — “Confirm Salesforce posted figure against the signed $60k/yr contract”

### `saas.aws_out_of_scope`
*confidence: high*

AWS (~$38,000) sits under Infrastructure, not SaaS, per the CFO's explicit instruction not to fold them together. Including AWS answers a different question and must be labeled.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:144` — “AWS infra (~$38k) sits under Infrastructure, not here”
- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:25` — “AWS,38000”

### `saas.cloudflare_fx_unconvertible`
*confidence: high*

Cloudflare is billed at EUR 1,900 in a USD column; the Infrastructure subtotal is blank pending FX normalization, and no FX rate exists anywhere in the bundle. The line cannot be converted with supplied data and no rate is invented.

- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:26` — “Cloudflare,€1900”
- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:27` — “Subtotal pending FX normalization”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/finance_review_2026-05-28.md:25` — “normalize to USD at month-end FX”

### `pnl.cannot_total`
*confidence: high*

The P&L cannot be totaled as supplied: Office supplies is blank pending AP coding, the Infrastructure subtotal is blank, and the Cloudflare line is non-numeric. Any 'total opex' or margin figure from this file is unsupported.

- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:35` — “Office supplies,,”
- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:27` — “Infrastructure subtotal,,”

### `recon.pain_corroborated`
*confidence: high*

Month-end brand-deal revenue reconciliation takes ~3 analyst-days every month, corroborated across two people, three file types, and three months (April, May, June mentions). It is Finance's self-declared #1 time sink and automation vote.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:97` — “the brand-deal revenue recon is the thing that eats my life every month”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:108` — “took me basically three full days again”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:111` — “the biggest recurring time sink in finance right now”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:114` — “If we automated the three-way match”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:158` — “Same brand-deal recon grind”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/finance_review_2026-05-28.md:11` — “took ~3 full days this cycle”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:35` — “eating ~3 days of Maya's time every month”

### `recon.three_sources_named`
*confidence: high*

The three systems in the reconciliation are named in the sources: the CRM deal export (what Sales says closed), the invoicing sheet (what was billed), and the payout tracker (what creators were paid against deals). Deal amounts, close dates, and payout splits drift between all three. None of the three exports is present in the bundle.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:100` — “the CRM export (what Sales says closed), the invoicing sheet (what we billed), and the payout tracker”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/finance_review_2026-05-28.md:12` — “Deal amounts, close dates, and payout splits drift between all three”

### `recon.self_reported_not_logged`
*confidence: moderate*

The ~3 days/month figure is self-reported in Slack and meeting notes; no timesheet or work log exists in the bundle to verify it. It is treated as an observed-claim baseline, not a measured one.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:108` — “basically three full days”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:35` — “never ties out first pass”

### `recon.revenue_at_stake`
*confidence: high*

The reconciliation sits under brand-partnership revenue of $4.2M in Q1 2026 - 80% of total revenue - which is why trustworthy first-pass numbers matter more than the analyst hours.

- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:2` — “Brand partnerships,4200000”

### `tickets.claim_40h_falsified`
*confidence: high*

Ops claimed 'easily 40 hrs/week' of creator support and 'a full-time person's worth, minimum'. The company's own Q1 ticket log measures 140 tickets and 4,230 handle-minutes = 70.5 h/quarter = 5.48 h/week (0.137 FTE). Like-for-like on the three categories Liam named, the claim is 8.1x the measured rate (7.3x against all tickets). Elena asked whether the number was 'measured or a vibe'; Ben predicted felt-volume would exceed measured volume. The log answers: vibe.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:176` — “easily 40 hrs/week on creator support”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:179` — “is that measured or a vibe?”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:185` — “I suspect the felt-volume is higher than the measured volume”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:188` — “it FEELS like a full-time person”

### `tickets.liam_right_on_volume`
*confidence: high*

Liam is 8x off on hours but right on volume share: he said self-serve thumbnail replacement would remove 'half my tickets'; thumbnail re-uploads are 63 of 140 tickets = 45.0% by count (but only 32% of minutes).

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:193` — “half my tickets would vanish”

### `tickets.q2_rate_unverifiable`
*confidence: low*

'Thumbnail swap request #47 this week' (2026-05-21) cannot be verified: there is no Q2 ticket data in the bundle. Read as a weekly rate it is ~9.6x the measured Q1 rate; read as cumulative since Apr 1 it is consistent with history. Only the cumulative reading is supported by data; the conflict is left open.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:193` — “Thumbnail swap request #47 this week”

### `value.blended_rate`
*confidence: moderate*

The only loaded labor rate derivable from the bundle: $3,120,000 quarterly salaries & benefits x 4 / 300 FTE / 2,080 hrs = $20.00/hr. This is a company-wide blend; a Finance Analyst's true loaded cost is almost certainly higher, but no per-person or per-team compensation data exists in the bundle, so no uplift is invented.

- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:7` — “Salaries & benefits (all teams),3120000”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:18` — “TOTAL,300”

### `definitions.creator_count_unreconciled`
*confidence: high*

Two irreconciled creator counts circulate: Data's 'active' = 1,210 (posted >=1 in last 30 days) vs Finance/Talent's 1,840 under contract. Finance models per-creator economics on 1,840; the single-definition decision was still open at the 2026-06-11 sync.

- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/data_review_2026-05-20.md:14` — “active creators = 1,210”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:130` — “1,840 creators under contract”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/finance_review_2026-05-28.md:18` — “1,840 creators under contract”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:31` — “pick ONE headline definition”

### `integrity.weekday_labels_unreliable`
*confidence: high*

13 of 20 unique dated message headers in the Slack export carry weekday labels that do not match their dates (e.g. 'Fri May 2' is a Saturday; 'Mon Jun 2' is a Tuesday). ISO-style dates are treated as authoritative; weekday labels are ignored. Both dates carrying the hiring decision (Jun 10 = Wed, Jun 11 = Thu) are among the seven correct ones.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:107` — “Fri May 2”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:143` — “Mon Jun 2”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:157` — “Fri Jun 13”

### `integrity.roster_defects`
*confidence: high*

The roster snapshot has an impossible start date (2026-13-02), a blank start date, a blank requisition target date, and two labels for one team ('Creator Mgmt' vs 'Creator Management'). Its employee list is a 29-row sample against a stated 300 headcount - team sizes must come from the summary section, never from counting employee rows.

- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:46` — “2026-13-02”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:50` — “Onboarding Specialist,Active,,”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:25` — “REQ-125,Data,Analytics Engineer,OPEN,,”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:47` — “Creator Mgmt”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:49` — “Creator Management”

### `integrity.org_chart_manager_conflict`
*confidence: moderate*

org_chart.md places Ben Okoro (Data) directly under the CEO in the reporting tree, while the roster records his manager as Raj Patel; several VP reporting lines differ the same way (roster says Marcus, chart says Dana). The COO 'cross-functional delivery oversight' note partially explains it, but not for Data or Engineering. Headcounts, by contrast, tie exactly to 300 in both files.

- VERIFIED · `input/Northwind-in-a-box_charles/org_chart.md:51` — “Ben Okoro”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:37` — “Ben Okoro,Data,Head of Data,Active,2021-11-02,Raj Patel”

### `saas.completeness_gap`
*confidence: moderate*

The $81,000 is spend booked to the SaaS line, not a complete inventory of software in use: the bundle shows a CMS and a ticketing system in daily operational use with no corresponding SaaS line item, and no HRIS/payroll or accounting-system line appears for a ~300-FTE company. Unquantifiable from this bundle; flagged, not estimated.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:165` — “it's all manual through the CMS”
- VERIFIED · `input/Northwind-in-a-box_charles/support_tickets_q1_2026.csv:1` — “Ticket_ID,Date,Category,Submitted_By,Assigned_To,Handle_Minutes,Status”

### `tickets.taxform_buy_not_build`
*confidence: high*

Tax-form chasing (W-9/W-8) is the largest support category by minutes, and already has a buy-not-build answer: People says cheap e-sign/tax-form services exist, revisit at Q3 planning.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:201` — “chasing W-8s from the international creators. Manual every time.”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:204` — “There are e-sign + tax form services. Cheap.”

### `hiring.chronology_note`
*confidence: moderate*

Dana announced the freeze in #leadership at 08:47 on 2026-06-10; the meeting note is dated 2026-06-11; Elena's 2026-06-11 message says 'yesterday's leadership call'. Substance is identical under either reading; the decision date is reported as 'announced 2026-06-10, minuted 2026-06-11' with moderate confidence on the date-of-record only.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:66` — “Wed Jun 10, 8:47 AM”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:3` — “2026-06-11 (Thu)”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:230` — “Following yesterday's leadership call”

## Hiring timeline events

### `hiring event — h1_req114_advocacy`
Tomás argues for AE capacity; REQ-114 approved, wants an AE seated by mid-July. Marcus pushes back; Dana parks the debate.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:17` — “REQ-114 approved and I want to get an AE seated by mid-July”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:20` — “see how Q2 pipeline looks before we add bodies”

### `hiring event — h2_roster_snapshot`
Board roster snapshot locked with REQ-114 = APPROVED, target start 2026-07-15. This record was accurate on its date and is now stale.

- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:22` — “REQ-114,Sales,Account Executive,APPROVED,2026-07-15”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:222` — “a Sales AE (REQ-114, approved, target start mid-July)”

### `hiring event — h3_ceo_freeze_announcement`
Dana announces in #leadership: freezing all new Sales headcount until pipeline recovers, REQ-114 included; Priya holds the line on reqs. Priya confirms REQ-114 is paused, not killed. Tomás records his objection.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:67` — “FREEZING all new Sales headcount until pipeline recovers”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:70` — “REQ-114 is paused, not killed”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:73` — “Putting my objection on record”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:79` — “current state is frozen on Sales hiring”

### `hiring event — h4_leadership_sync_minuted`
The freeze is minuted as a DECISION. The note explicitly supersedes the 2026-05-01 roster line showing REQ-114 APPROVED.

- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:16` — “Freeze all new Sales headcount until pipeline recovers”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:16` — “superseded by this decision”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:17` — “Backfills for regretted attrition to be reviewed case-by-case”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:18` — “no new Sales req moves forward without her sign-off”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:19` — “pipeline coverage back to target + two consecutive months of recovered conversion”

### `hiring event — h5_people_cascade`
People cascades the freeze: REQ-114 paused per Dana's decision, Priya enforcing; the May 1 roster is declared stale on this point; freeze is Sales-only, other teams' reqs unaffected.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:230` — “REQ-114 is paused per Dana's decision, Priya enforcing on reqs”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:236` — “freeze is Sales-only for now”

### `hiring event — h6_freeze_still_in_force`
Latest evidence in the corpus: Q3 planning instruction confirms Sales remains on freeze.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:244` — “Sales is on freeze so don't bother submitting Sales reqs until that lifts”

## Open follow-ups

### `open follow-up — f1_late_stage_candidate`
A candidate was in late-stage interviews for REQ-114 when the freeze landed. Priya + Tomás were to decide pause-vs-finish-loop by 2026-06-13. No resolution appears anywhere in the corpus through 2026-06-17.

*Risk if ignored: A live candidate may still be interviewing for a frozen role.*

- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:20` — “candidate already in late-stage interviews for REQ-114”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:42` — “pause vs finish loop, no offer”

### `open follow-up — f2_greenhouse_unconfirmed`
Marcus was to notify Elena so recruiting pauses the req in Greenhouse (due 2026-06-12). Elena's Slack instruction is not an ATS state change; no confirmation exists that Greenhouse - a live, paid system - shows the req paused.

*Risk if ignored: The ATS may still show REQ-114 as approved and actively recruitable.*

- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:43` — “Notify Elena/People to pause Sales req in Greenhouse”
- VERIFIED · `input/Northwind-in-a-box_charles/pnl_q1_2026.csv:22` — “Greenhouse,4000”

### `open follow-up — f3_roster_never_restated`
The board-facing roster snapshot still reads APPROVED for REQ-114; it was never restated after the freeze. Anyone querying the official snapshot gets the superseded answer.

*Risk if ignored: The system of record contradicts the standing decision.*

- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:22` — “APPROVED”
- VERIFIED · `input/Northwind-in-a-box_charles/meeting_notes/leadership_sync_2026-06-11.md:16` — “superseded by this decision”

### `open follow-up — f4_req_list_mismatch`
Elena's 'official picture for the board' names three open reqs (Sales AE, Creator Mgmt backfill, an Eng role); the CSV she prepared lists four (Sales, Eng, Content, Data) and the Creator Mgmt backfill appears in no req row at all, yet it is real and proceeding.

*Risk if ignored: The req tracker and the board summary disagree in both directions.*

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:222` — “plus a Creator Management backfill and an Eng role”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:24` — “REQ-121,Content/Production”
- VERIFIED · `input/Northwind-in-a-box_charles/headcount_roster.csv:25` — “REQ-125,Data”
- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:239` — “proceeding with the backfill”

## Knowledge horizon

### `as_of`
All answers are stated as of 2026-06-18 — the bundle's own export date.

- VERIFIED · `input/Northwind-in-a-box_charles/slack_export.md:3` — “Export generated 2026-06-18”
