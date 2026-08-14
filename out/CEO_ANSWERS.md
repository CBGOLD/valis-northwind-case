# Northwind — straight answers, with receipts

*Everything below traces to an exact file and line in the bundle; knowledge stops at 2026-06-18 (the Slack export date). Full quote-level audit: `AUDIT.md`. Re-verify any time: `python3 ask.py check`.*

## What did we actually spend on SaaS tools last quarter?

**Best estimate $73,500 for Q1 2026 SaaS — the books say $81,000, which includes a suspected $7,500 duplicate your own finance team has flagged but not yet confirmed.**

1. Booked: $81,000. The 15 SaaS line items sum exactly to the stated subtotal (arithmetic ties out); the CFO confirmed this as the finalized Q1 figure. (A naive category sum that forgets the subtotal row returns $162,000 — the code here excludes it, and a test proves it.)
   `pnl_q1_2026.csv:24` · `slack_export.md:144`
2. Adjusted: $73,500. Two adjacent lines — 'Amplitude' / 'Amplitude Analytics' at $7,500 each — look double-entered. The analyst closest to it is 90% sure; the CFO agrees it 'smells like a double-count'. Unverified: the invoice never came back, so the books deliberately still carry both.
   `pnl_q1_2026.csv:12` · `pnl_q1_2026.csv:13` · `slack_export.md:147` · `slack_export.md:150` · `slack_export.md:153`
3. Not restated: Salesforce, booked $12,000 for Q1. The $60k/yr renewal was signed 2026-05-14 — that's Q2, covering 'through next May' — so Q1 stands, with a +$3,000/quarter step-up from Q2 onward. Two open flags: finance's own check-posted-vs-contract action has sat unclosed since 2026-05-28, and the finance note's direction is backwards ('looks higher': $12k/qtr annualizes to $48k, BELOW $60k). Treat the line as booked-but-unverified.
   `pnl_q1_2026.csv:9` · `slack_export.md:119` · `finance_review_2026-05-28.md:23` · `finance_review_2026-05-28.md:37`

*Scope: the 'Software & SaaS' category only, per your CFO's classification. Infrastructure is excluded — AWS $38,000, and Cloudflare €1,900 which is billed in EUR with no FX rate anywhere in the bundle (left unconverted rather than inventing a rate). Fold infra in and you're asking a different question.*
   `slack_export.md:144` · `pnl_q1_2026.csv:25` · `pnl_q1_2026.csv:26` · `pnl_q1_2026.csv:27` · `finance_review_2026-05-28.md:25`

*Completeness: this is what's booked to the SaaS line, not an inventory of software in use — the bundle shows a CMS and a ticketing system running daily with no SaaS line item, and no HRIS/payroll or accounting line for ~300 FTE. Flagged rather than estimated.*
   `slack_export.md:165` · `support_tickets_q1_2026.csv:1`

**Confidence:** booked: HIGH — recomputed from the P&L rows; sum ties to the stated subtotal. — best estimate: MODERATE-HIGH — the duplicate is 90%-suspected by the person closest to it and endorsed by the CFO, but the invoice is outstanding. Bounded: $73,500 (duplicate confirmed) to $81,000 (duplicate refuted).

**What would change this answer:** If the Amplitude invoice shows two distinct contracts, the answer reverts to $81,000. If the Salesforce contract check finds a mis-posting, the Q1 line adjusts by the difference.

---
## Did we decide to hire in Sales or freeze hiring — current state and owner?

**FROZEN. Dana froze all net-new Sales hiring — announced 2026-06-10 in #leadership, minuted 2026-06-11. REQ-114 is paused, not killed. Dana owns the decision; Priya enforces it.**

1. Decision & scope: all net-new Sales headcount frozen until pipeline recovers, REQ-114 (the AE role) explicitly included and on hold; Tomás's objection is on record. Sales-only — other teams' reqs are unaffected; backfills for regretted attrition go case-by-case through Priya + Tomás.
   `slack_export.md:67` · `slack_export.md:70` · `slack_export.md:73` · `slack_export.md:79` · `slack_export.md:230` · `slack_export.md:236`
2. Ownership: decision — Dana Whitfield (CEO), on record ('I'm making the call'); enforcement — Priya Raman (CFO): no Sales req moves without her sign-off. The 2026-05-01 roster still says REQ-114 APPROVED — that snapshot is explicitly superseded (the sync minutes say so; People declared the roster stale).
   `slack_export.md:66` · `leadership_sync_2026-06-11.md:3` · `slack_export.md:230` · `leadership_sync_2026-06-11.md:16` · `leadership_sync_2026-06-11.md:16` · `leadership_sync_2026-06-11.md:17` · `leadership_sync_2026-06-11.md:18` · `leadership_sync_2026-06-11.md:19` · `headcount_roster.csv:22` · `slack_export.md:222`
3. Revisit condition: Pipeline coverage back to target + two consecutive months of recovered conversion; re-evaluate at July leadership sync. Still true at the last message in the bundle (2026-06-18); loose ends below.
   `slack_export.md:244`

*Open follow-through (decided in humans, unconfirmed in systems): (1) A candidate was in late-stage interviews for REQ-114 when the freeze landed. Priya + Tomás were to decide pause-vs-finish-loop by 2026-06-13. No resolution appears anywhere in the corpus through 2026-06-17. (2) Marcus was to notify Elena so recruiting pauses the req in Greenhouse (due 2026-06-12). Elena's Slack instruction is not an ATS state change; no confirmation exists that Greenhouse - a live, paid system - shows the req paused. (3) The board-facing roster snapshot still reads APPROVED for REQ-114; it was never restated after the freeze. Anyone querying the official snapshot gets the superseded answer. (4) Elena's 'official picture for the board' names three open reqs (Sales AE, Creator Mgmt backfill, an Eng role); the CSV she prepared lists four (Sales, Eng, Content, Data) and the Creator Mgmt backfill appears in no req row at all, yet it is real and proceeding.*
   `leadership_sync_2026-06-11.md:20` · `leadership_sync_2026-06-11.md:42` · `leadership_sync_2026-06-11.md:43` · `pnl_q1_2026.csv:22` · `headcount_roster.csv:22` · `leadership_sync_2026-06-11.md:16` · `slack_export.md:222` · `headcount_roster.csv:24` · `headcount_roster.csv:25` · `slack_export.md:239`

**Confidence:** answer: HIGH — four concordant sources (#leadership Slack, sync minutes, #people Slack ×2), an explicit supersession statement, zero contradicting messages after 2026-06-10. MODERATE on the date-of-record only (announced Jun 10, minuted Jun 11). — operational state: LOW — no evidence the freeze reached the systems of record (roster still APPROVED; Greenhouse pause unconfirmed; late-stage candidate handling unresolved, due date passed).

**What would change this answer:** Freeze lifts when pipeline coverage is back to target plus two consecutive months of recovered conversion — re-evaluated at the July leadership sync (after this bundle's horizon). Any Priya-approved exception (e.g. a regretted-attrition backfill) modifies the state for that req.

---
## Where are we wasting the most time, and what would you automate first?

**Automate the monthly brand-deal three-way reconciliation first. Reported cost: ~3 analyst-days per month (~72 h/quarter) — more than the entire measured support queue (70.5 h/quarter). And it sits under $4.2M of brand revenue: the payoff is trustworthy first-pass numbers, not just hours.**

1. Brand-deal reconciliation (CRM export vs invoicing sheet vs payout tracker): ~3 days every month-end, corroborated across two people, three file types and three months; the CFO calls it the single biggest finance time-sink, the analyst votes it #1. Honest label: that baseline is self-reported, never system-measured — but it is the most corroborated number in the bundle, and 80% of revenue flows through the process it protects.
   `slack_export.md:100` · `finance_review_2026-05-28.md:12` · `slack_export.md:97` · `slack_export.md:108` · `slack_export.md:111` · `slack_export.md:114` · `slack_export.md:158` · `finance_review_2026-05-28.md:11` · `leadership_sync_2026-06-11.md:35` · `slack_export.md:108` · `leadership_sync_2026-06-11.md:35` · `pnl_q1_2026.csv:2`
2. Support is measured, and the measurement kills the vibe: 140 tickets in Q1 = 4230 handle-minutes = 70.5 h/quarter ≈ 5.48 h/week over the 90-day quarter — the 40 h/week claim is 7.3× the whole measured queue, and 8.1× like-for-like on the three categories named. Do not hire or build against it. (Liam IS right on ticket share: thumbnails are 63/140 of tickets by count — but only 22.8 h/quarter of time. His '#47 this week' can't be checked: no Q2 ticket data exists.)
   `slack_export.md:176` · `slack_export.md:179` · `slack_export.md:185` · `slack_export.md:188` · `slack_export.md:193` · `slack_export.md:193`
3. Tax forms (W-9/W-8) are the biggest support category by time (25.9 h/quarter) — and already have a buy-not-build answer: cheap e-sign/tax-form services, parked for Q3 planning by People. Buy it; don't build it. Automating thumbnails is real but third in line.
   `slack_export.md:201` · `slack_export.md:204`

**Confidence:** support measurement: HIGH — computed row-by-row from the company's own ticket log. — recon baseline: MODERATE — self-reported (~3 days/month), never system-measured, but corroborated by seven statements across Slack, the finance review, and the leadership sync; no contradicting evidence exists.

**What would change this answer:** If the real CRM/invoicing/payout exports show trivial monthly drift, the recon build downgrades and thumbnail self-serve moves up. If ticket logging is shown to materially under-capture support work (untracked DMs, walk-ups), the support right-sizing weakens — that completeness is explicitly unverified.

