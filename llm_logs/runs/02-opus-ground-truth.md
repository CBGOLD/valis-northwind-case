# Opus ground-truth run — verbatim output

Model: claude-opus-5 (subagent, fresh context, read-only) · launched 2026-08-14 ~23:50 CEST ·
duration 577s · 22 tool uses · prompt: `llm_logs/prompts/02_opus_ground_truth.md` (passed verbatim,
plus a read-only guard preamble). Transport HTML entities (`&amp;`) de-escaped; otherwise unedited.

---

I have the full picture. Every number below was computed with actual commands against the raw files, not estimated.

---

# NORTHWIND GROUND TRUTH — independent audit

Sources inspected: all 11 substantive files under `$HOME/workspace/valis-northwind-case/input/Northwind-in-a-box_charles/`. I did not read `BUILD_LOG.md` or any builder output, to keep this independent. Line numbers are literal file lines.

---

## 1. Q1 2026 SaaS spend — three states

**Answer: `$73,500 ≤ true Q1 SaaS ≤ $81,000`. The single published number is `$81,000` and it is not defensible until one invoice is pulled.**

### State A — Booked / as-listed: **$81,000** · confidence HIGH
- `pnl_q1_2026.csv` L24: `Software & SaaS,Software & SaaS subtotal,81000,As-listed sum of SaaS line items`
- Corroborated `slack_export.md` L144 (Priya Raman, #finance, Jun 2 10:30 AM): *"Software & SaaS line is finalized for Q1, subtotal as listed is $81k for the quarter."*
- **I recomputed L9–L23: sum = exactly 81,000.00. Delta to stated subtotal = 0.** The subtotal has no arithmetic error. Every gap below is definitional or evidentiary, not a maths error. This matters — most candidates will hunt for a broken sum that isn't there.

### State B — Suspected-adjusted: **$73,500** (−$7,500, −9.26%)
- `pnl_q1_2026.csv` L12 `Software & SaaS,Amplitude,7500,Product analytics`
- `pnl_q1_2026.csv` L13 `Software & SaaS,Amplitude Analytics,7500,Product analytics` — **identical amount, identical Notes string, adjacent rows, same vendor stem.**
- `slack_export.md` L147 (Maya Fortin, Jun 2 10:38 AM): *"we've got both an 'Amplitude' line and an 'Amplitude Analytics' line, each at $7.5k. **I'm 90% sure** that's the same product entered twice but **I haven't confirmed against the invoice.**"*
- L150 (Priya, 10:45 AM): *"that smells like a double-count. Pull the Amplitude invoice… we'll fix it if it's one contract."*
- L153 (Maya, 10:47 AM): *"Haven't gotten the invoice back yet so I'm leaving the CSV as-is."*
- **Unresolved for 15 days** (Jun 2 → Jun 17, end of Slack range).

### State C — Verified: **nothing above $73,500 is verified; nothing below it is contested.**
The only honest answer is a range, not a point. $73,500 is the floor (13 uncontested lines + one Amplitude subscription that certainly exists). $81,000 is the ceiling. The $7,500 band is live. Separately, €1,900 sits outside the band as a classification question.

### Reconciliation gaps — all eight

| # | Gap | Evidence | Status |
|---|---|---|---|
| G1 | Amplitude $7,500 duplicate | pnl L12/L13; slack L147, L150, L153 | **Open 15d.** No invoice, no AP subledger, no vendor statement in bundle |
| G2 | Cloudflare **€1,900** unconverted | pnl L26 `€1900` — *"billed in EUR — normalize before totaling"*; L27 `Infrastructure subtotal` **blank**, *"pending FX normalization"* | **Unverifiable — no FX rate exists anywhere in the bundle.** ≈$2.0–2.1k at plausible rates, but that is my assumption, not the data's |
| G3 | Salesforce posted vs signed | pnl L9 `Salesforce,12000`; slack L119 (May 14): *"$60k for the year, locked"*; `finance_review_2026-05-28.md` §3 | **$12,000 × 4 = $48,000/yr run-rate vs $60,000/yr signed.** See below — the meeting note is wrong about this |
| G4 | Category-column trap | 16 rows carry `Category = Software & SaaS`; the subtotal row is one of them | **A naive `groupby(Category).sum()` returns $162,000 — a 100% overstatement.** This is the trap |
| G5 | Scope boundary | pnl L25 `AWS,38000` + L26 Cloudflare, both under `Infrastructure`; slack L144: *"AWS infra (~$38k) sits under Infrastructure, not here — don't let anyone fold them together"* | **Definitional, Dana's to set.** If "SaaS tools" means all software+cloud vendors → ~$121k. If it means the SaaS line → $81k |
| G6 | Completeness | Bundle proves tools in daily use that appear on no P&L line: a **CMS** (slack L165, Liam: *"it's all manual through the CMS"*); a **helpdesk** (`support_tickets_q1_2026.csv` has Ticket_IDs, Assigned_To, Status → some system logs these); no **HRIS/payroll** for 300 FTE (Greenhouse L22 is ATS only); no **accounting/ERP** for a 6-person finance team running month-end close. Creator payout rail is booked to G&A (L34, $31,000), not SaaS | **15 named tools for 300 people = $270/FTE/quarter.** The completeness gap is almost certainly larger than the accuracy gap |
| G7 | Pre-close blanks | pnl L35 `G&A,Office supplies,,Blank — pending AP coding` | Open |
| G8 | "Finalized" is false | Priya says *"finalized"* (L144, Jun 2 10:30) — **17 minutes later** Maya says she is leaving a known-suspect line as-is (L153, 10:47) | A line with an open double-count flag is not finalized |

### G3 deserves its own paragraph — the meeting note contradicts the CSV in the wrong direction

`finance_review_2026-05-28.md` §3 states: *"the current quarterly P&L figure **looks higher** than a $60k annual would imply."*

$60,000 ÷ 4 = **$15,000/quarter**. The posted figure is **$12,000**. It is **$3,000 LOWER**, not higher. The meeting note's directional claim is factually wrong on its face.

The coherent reading the note misses: the renewal was signed **2026-05-14 — that is Q2**. Q1 (Jan–Mar) correctly carries the prior contract at $48k/yr straight-lined. **The $12,000 needs no adjustment.** What it does create is a forward exposure: **+$3,000/quarter, +$12,000/year** from the renewal date, not in any baseline. Forward run-rate, if the Amplitude duplicate is confirmed: $73,500 + $3,000 = **$76,500/quarter = $306,000/yr**, vs $324,000 if you naively annualize the as-listed figure.

Action item #2 in that file ("Confirm Salesforce posted figure against the signed $60k/yr contract", due "next week" ≈ 2026-06-04) shows **no confirmation anywhere through 2026-06-17 — 13 days overdue.**

---

## 2. Sales hiring — decided, frozen, and operationally unconfirmed

**Answer: Sales hiring is FROZEN. Dana Whitfield (CEO) made the call. Priya Raman (CFO) enforces it on the req side. REQ-114 is paused, not killed. The freeze is Sales-only. It is unconfirmed whether the freeze was ever executed in the system of record.** Confidence HIGH on the decision, LOW on the operational state.

### Source authority ranking
1. **`meeting_notes/leadership_sync_2026-06-11.md` §1** — authoritative. Only source stating scope, decision owner, enforcement owner, and revisit trigger together, and the only one that **explicitly declares supersession**: *"The 2026-05-01 roster showing it APPROVED is superseded by this decision."*
2. **`slack_export.md` L67–L79** (#leadership, Wed Jun 10) — the decision as announced by the decision-maker herself.
3. **`slack_export.md` L230–L236** (#people, Thu Jun 11) — People-function propagation.
4. **`headcount_roster.csv` L22** — **stale artifact, do not cite as current state.**

### Chronology

| When | Source | Event |
|---|---|---|
| 2026-04-21 09:31 | slack L17 | Tomás: *"We've got REQ-114 approved and I want to get an AE seated by mid-July."* |
| 2026-04-21 09:40 | slack L20 | Marcus pushes back: *"Let's see how Q2 pipeline looks before we add bodies."* |
| 2026-04-21 09:52 | slack L26 | Dana: *"Park it."* — **deferred, not decided** |
| **2026-05-01** | `headcount_roster.csv` L22 | `REQ-114,Sales,Account Executive,**APPROVED**,2026-07-15,Tomás Reyes` |
| 2026-05-01 16:30 | slack L222 | Elena locks the snapshot |
| **2026-06-10 08:47** | slack L67 | **Dana: *"OK, decision on Sales hiring. After the Q1 sales miss we're FREEZING all new Sales headcount until pipeline recovers. No new AE reqs move forward, REQ-114 included. Priya holds the line on reqs."*** |
| 2026-06-10 08:52 | slack L70 | Priya: *"REQ-114 is **paused, not killed**"* |
| 2026-06-10 09:05 | slack L73 | Tomás logs a formal objection — dissent recorded, decision stands |
| 2026-06-10 09:14 | slack L79 | Dana: *"current state is frozen on Sales hiring, I'm making the call, Priya enforces it on the req side."* |
| **2026-06-11 09:00–10:05** | leadership_sync §1 | **DECISION formally minuted with scope, owners, revisit trigger, supersession** |
| 2026-06-11 09:30 | slack L230 | Elena: *"frozen effective immediately… The May 1 roster is now stale on that point."* |
| 2026-06-11 09:41 | slack L236 | Elena: *"freeze is **Sales-only**. Other teams' open reqs are unaffected."* |
| 2026-06-15 14:00 | slack L244 | Elena: *"Sales is on freeze so don't bother submitting Sales reqs until that lifts"* — **freeze still in force at latest evidence** |

### The dimensions Dana asked for
- **Decision owner:** Dana Whitfield, CEO. Self-declared twice (slack L79; leadership_sync §1: *"Decision made by **Dana (CEO)**"*).
- **Enforcement owner:** Priya Raman, CFO. *"no new Sales req moves forward without her sign-off"* (leadership_sync §1; slack L67, L79).
- **Scope:** net-new Sales reqs only. Backfills for regretted attrition reviewed case-by-case by **Priya + Tomás**, not auto-approved (leadership_sync §1). Non-Sales reqs unaffected — REQ-118 (Eng), REQ-121 (Content), REQ-125 (Data) all live; Creator Mgmt backfill explicitly cleared (slack L236, L239).
- **Revisit trigger — two conditions, both required:** (a) pipeline coverage back to target **AND** (b) two consecutive months of recovered conversion. Scheduled re-evaluation: **July leadership sync** (leadership_sync §1). Note Marcus says *"Q2 review"* (slack L76) — slightly looser phrasing; the minuted trigger governs.

### Unresolved operational follow-through — the sharpest part of this answer

**The decision is unambiguous in humans and unconfirmed in systems.**

1. **REQ-114 is still `APPROVED` in `headcount_roster.csv` L22.** Correct as a 2026-05-01 snapshot, wrong as an answer. Any system reading the roster returns the superseded state.
2. **No source confirms the req was actually paused in Greenhouse.** Leadership sync action #2: *"Notify Elena/People to pause Sales req in Greenhouse | Marcus | 2026-06-12."* Elena's Jun 11 09:30 post says *"**Updating my notes**; please don't recruit against it"* — a note update, not an ATS state change. Greenhouse is a live paid system (`pnl_q1_2026.csv` L22, $4,000). **System of record state: unverified.**
3. **A candidate is stranded mid-loop.** Leadership sync §1: *"Tomás flagged candidate already in late-stage interviews for REQ-114 — Priya to confirm whether to pause or let the loop finish without an offer."* Action #1, due **2026-06-13**. Slack runs to 2026-06-17 with **no resolution — 4 days overdue.** This is the only item in the bundle with a third party's time and a reputational/legal surface hanging on it.
4. Leadership sync actions #3 (Q2 re-baseline, due 06-18) and #4 (creator definition, due next sync 06-25) fall **after** the export window — not assessable, and a candidate who claims they're overdue is fabricating.

### Chronology note I checked and dismissed
Dana's Slack decision is Wed Jun 10; the minutes are dated Thu Jun 11; Elena on Jun 11 09:30 refers to *"yesterday's leadership call."* Consistent reading: the call and announcement were Jun 10, the Jun 11 sync formally minuted it. Not a contradiction. **Separately** I verified all 20 Slack date labels against the calendar: **13 of 20 carry 2025 weekdays, 7 carry correct 2026 weekdays** — the export was partly generated against a 2025 calendar. Notably, every date load-bearing for these two questions (05-01, 05-12, 05-21, 05-28, 06-10, 06-11, 06-15) is **correct for 2026**. Two of the mismatches land on Maya's recon messages (2026-05-02 and 2026-06-13, both labeled Fri, both Saturdays in 2026). Non-material — ISO dates are correctly ordered, no conclusion depends on weekday, and both recon claims are independently corroborated in dated meeting notes. Log it as a judgment call; don't build on it.

---

## 3. Automation candidates — ranked

**The central trap: the best-evidenced, highest-value workflow is the one you cannot build on the supplied data.** The brief demands something that "actually runs on this data." Northwind's own people vote unanimously for the workflow whose three input files are absent from the bundle. Resolving that tension correctly is the discriminator.

| | Candidate | Observed time value | Evidence strength | Feasibility w/ supplied data | Strategic fit |
|---|---|---|---|---|---|
| **1** | **Close-integrity / P&L linter** | Not time-denominated. **Value is defect-denominated: $7,500 caught + a $162,000 vs $81,000 aggregation error prevented + 2 blank subtotals + 1 unconverted FX cell** | HIGH — every defect class is physically present in `pnl_q1_2026.csv`; Priya asked for exactly this (slack L45: *"a couple of line items I want a second set of eyes on"*) | **100%.** The file is in the bundle. Runs today, on real rows | **HIGHEST.** Directly answers *"I don't fully trust my own numbers"* |
| **2** | **Brand-deal three-way recon** (CRM export ↔ invoicing sheet ↔ payout tracker) | **288 hrs/yr** (3 days × 8h × 12) — largest single time sink in the bundle | **HIGHEST — 6 citations, 3 files, 2 authors, minuted at leadership level, magnitude identical every time.** slack L97, L100, L108, L114, L158; finance_review §1 (*"single biggest finance time-sink"*); leadership_sync §4 | **0%. None of the three source files exist in the bundle.** Anything "shipped" here runs on fabricated inputs | **HIGHEST** — it is the mechanism producing Dana's distrust |
| **3** | **Support-ticket deflection / triage** | **282 hrs/yr** total queue. Thumbnail 91 hrs/yr; tax form 104 hrs/yr | MIXED — Q1 rows are hard data, but Liam's Q2 claims contradict them 8.7× | **100% for the analysis, 0% for the deflection** (self-serve thumbnail swap needs the CMS, absent) | MEDIUM — Liam's pain, not Dana's |

### Observed vs hypothetical — the distinction that matters

**Actually observed** (computed from supplied rows, reproducible):
- 140 tickets, **4,230 handle-minutes = 70.5 hrs across Q1** = **5.42 hrs/week**, 10.77 tickets/week.
- Category split: Tax form 36 tix / 1,555 min (36.8% of minutes) · Thumbnail 63 tix / 1,365 min (32.3%) · Payout 18 tix / 875 min (20.7%) · Account access 7/170 · Login 13/135 · Takedown 3/130.
- Amplitude $7,500. Two rows. Visible.

**Hypothetical** (asserted, no underlying data supplied):
- **Maya's 3 days/month is testimony, not data.** No timesheet, no workpaper, no recon output in the bundle. It is *excellent* testimony — self-reported by the operator, corroborated by the CFO, minuted at leadership — but a hostile CFO will still call it self-reported by the person requesting the tool.
- **Liam's 40 hrs/week is testimony contradicted by the only hard dataset bearing on it.** I reconstructed his claims and they are internally self-consistent: 47 thumbnails/week (slack L193) × 21.67 min measured avg = 17.0 hrs/wk; *"half my tickets"* → ~94 tickets/wk × 30.21 min = **47.3 hrs/wk** — consistent with his *"easily 40"* (L176). **It is the ticket log that disagrees, and it disagrees on volume, not on handle time: 94/wk claimed vs 10.77/wk logged = 8.7×. Q1's maximum thumbnail week was 6 tickets. Liam claims 47.** Either the log misses ~90% of volume, or volume 10×'d in Q2, or the claim is inflated. **No Q2 ticket data exists in the bundle to adjudicate.** Ben Okoro predicted exactly this on 2026-05-06 (slack L185: *"I suspect the felt-volume is higher than the measured volume"*) and offered to pull the numbers — **42 days later, no delivery appears in the export.**

### The finding to lead with
**One analyst's month-end recon (288 hrs/yr) consumes marginally more time than the entire creator support queue across all six categories (282 hrs/yr).** Ops is loud; Finance is expensive. The company is discussing a support hire and has never quantified either.

### Correct strategic answer
Ship **#1** (runs on real supplied rows, produces the largest verified dollar), and hand **#2** as the one-page builder spec with an explicit data contract naming the three missing files, their required columns, and join keys. Use **#3** as the evidence that kills the support-hire request. Anyone who "ships" #2 has fabricated its inputs.

---

## 4. The CFO-grade value number

> ## **$30,000/year of at-risk SaaS spend on one vendor line — $7,500 of it sitting in Q1 as reported — resolvable by pulling one invoice.**

Framed as **exposure with a named resolution test**, never as a booked saving. That framing is what makes it survive.

### Arithmetic, every step
```
pnl_q1_2026.csv L12   Software & SaaS, Amplitude,           7500, "Product analytics"
pnl_q1_2026.csv L13   Software & SaaS, Amplitude Analytics, 7500, "Product analytics"
                                       ↑ identical amount, identical note, adjacent rows

Q1 SaaS as published (L24, slack L144)          =  $81,000
Less contested duplicate                         −   $7,500
Q1 SaaS if duplicate confirmed                   =  $73,500
Overstatement as % of the published line         =   7,500 / 81,000 = 9.26%

Annualised at the Q1 rate                        =   $7,500 × 4 = $30,000/yr
Forward run-rate if confirmed, incl. Salesforce step-up:
   $73,500 + $3,000 (=$60,000/4 − $12,000)       =  $76,500/qtr = $306,000/yr
   vs naive annualisation of the published line  =  $324,000/yr        Δ = $18,000/yr
```

### Why this number and not a bigger one
The two larger-sounding numbers both die under cross-examination:
- **$41,600/yr avoided support hire** (loaded FTE cost, derived below) — dies on *"your ticket log may be incomplete,"* and I cannot refute that from the bundle. The 8.7× volume discrepancy is unresolvable without Q2 data.
- **$5,760/yr recon automation** (288 hrs × $20/hr) — dies on labour monetisation: you don't fire Maya, so cash saved is zero.

The Amplitude number requires **zero labour monetisation, zero volume assumptions, zero period extrapolation** beyond a stated ×4. Every input is a literal cell.

### The loaded-rate derivation (needed for the alternatives, disclosed for transparency)
```
pnl_q1_2026.csv L7:  Personnel, Salaries & benefits (all teams), 3,120,000, "~300 FTE; loaded cost"
$3,120,000 ÷ 300 FTE          = $10,400 per FTE per quarter
$10,400 ÷ 520 hrs (13wk×40h)  = $20.00/hr exactly
Annual loaded per FTE          = $41,600
```
At 1,800 genuinely productive hrs/yr this rises to $23.11/hr — so **$20.00 is the conservative choice**, which is the right direction to be wrong in.

### Disconfirming evidence — stated before the CFO finds it
1. **It is unverified, by the flagger's own admission.** Maya is *"90% sure"* (slack L147), not certain. Amplitude genuinely sells separately-priced products; a 10% chance of two real SKUs is honest.
2. **If clerical, cash recovery is $0.** One invoice coded twice = a $7,500 expense overstatement and an AP exception to chase, not $30,000 back. Maya's own phrasing — *"the same product entered twice"* — leans clerical. **I am not claiming cash. I am claiming the published number is wrong by 9.26% in one of two ways, and nobody knows which.** For a company that just took a board beating on cost discipline (slack L42, Marcus: *"They pushed on the sales miss and on cost discipline"*), reporting $7,500 of possibly-phantom SaaS cost is itself the finding.
3. **The exact price equality cuts both ways.** $7,500 = $7,500 is weak evidence *against* two distinct SKUs (they rarely price identically) and weak evidence *for* one invoice posted twice.
4. **No AP subledger, no invoice, no vendor statement exists in the bundle.** Unverifiable either way from supplied data. Full stop.
5. **The published number was called "finalized" while this was open.** Priya, Jun 2 10:30 (L144). Maya, Jun 2 10:47 (L153). Seventeen minutes apart.

### The resolution test — this is the actual deliverable
Pull the Amplitude invoice and vendor statement for Q1 2026 (**already owed by Maya since 2026-06-02, 15 days open**). Two outcomes, both actionable within the hour:
- **One contract, posted twice** → restate Q1 SaaS to $73,500, raise an AP exception, check whether cash actually left twice.
- **Two contracts** → $30,000/yr of duplicate tooling to consolidate, and rename both rows so this never recurs.

**The value delivered today is that a $30,000/yr question is now framed, sourced to two exact rows, and answerable by a 15-minute check that has sat undone for two weeks.**

---

## 5. Ten most likely failure modes in a candidate submission

1. **Answering "$162,000" or "$81,000 + $38,000" — the category-column trap.** Sixteen rows carry `Category = Software & SaaS`; one is the subtotal. Any `groupby().sum()`, any spreadsheet autosum over the column, any LLM reading the CSV without noticing the subtotal row returns **$162,000 — a 100% error**. This will be the most common failure and it is instantly fatal.
2. **Giving a single point number.** The defensible answer is a range with a named resolution test. Both $81,000 and $73,500 asserted alone are wrong — the first ignores a live flag, the second asserts an unverified adjustment as fact.
3. **Claiming the Amplitude $7,500/$30,000 as a *saving*.** It is an exposure. Maya says 90%, the invoice was never pulled, and if it's clerical the cash impact is zero. The CFO's first question will be *"did you pull the invoice?"*
4. **Adjusting Salesforce to $15,000 for Q1, or repeating the meeting note's directional error.** The renewal was signed **2026-05-14 — Q2**. The Q1 $12,000 is correct. `finance_review_2026-05-28.md` §3 says the posted figure *"looks higher"* than $60k/yr implies; **it is $3,000 lower**. A candidate who quotes that note without checking it has failed the core test of the exercise.
5. **Building the value number on Liam's 40 hrs/week.** The ticket log says **5.42 hrs/week**. Anyone monetising 40 hrs/wk × 52 × $20 has produced a $41,600 number contradicted by the one dataset that bears on it — the exact failure Elena Novak demanded be avoided on 2026-05-06 (*"is that measured or a vibe?"*).
6. **Citing `headcount_roster.csv` REQ-114 `APPROVED` as current state.** Superseded 2026-06-10/11, explicitly declared stale in two independent sources. Any pipeline that returns "approved" has no supersession logic.
7. **"Shipping" the three-way recon automation.** The CRM export, invoicing sheet, and payout tracker **do not exist in the bundle**. A demo here necessarily runs on fabricated data and directly violates *"runs on this data."* The pull toward it is strong — Northwind's own people vote for it four times — which is precisely why it's the trap.
8. **Silently dropping €1,900 or converting it at an invented FX rate.** No rate exists in the bundle. Either flag it unconverted or state the assumed rate and label it unverifiable. A silent conversion is a fabricated input.
9. **Naive parsing failures nobody notices.** `headcount_roster.csv` is **not rectangular** — a preamble plus three sections with different headers; `pd.read_csv` produces garbage. It contains `Felix Braun, Start_Date = 2026-13-02` (**month 13 — invalid**), a blank Start_Date (Jonas Vik), and **two spellings of one team** (`Creator Mgmt` ×2 vs `Creator Management` ×3) that silently split any groupby. The roster lists **29 people against a claimed 300** — a partial extract. `support_tickets` has 4 blank `Assigned_To` (TCK-1013, 1038, 1068, 1100) and 2 `Open` tickets.
10. **Answering "who owns it" with one name.** Three distinct owners: **Dana decides**, **Priya enforces**, **Marcus/Elena execute in Greenhouse** (unconfirmed). And missing the live consequence — a candidate stranded in a late-stage loop with action #1 four days overdue.

**Bonus, and the rarest miss:** treating $81,000 as a *complete* SaaS inventory. The bundle proves a CMS and a helpdesk are in daily operational use with no P&L line, and there is no HRIS/payroll for 300 FTE nor accounting/ERP for a 6-person finance team. **$270/FTE/quarter.** The completeness gap is probably larger than the accuracy gap, and almost nobody will say so.

---

## 6. Pass/fail tests for a top-0.1% artifact

**Correctness gates — any single failure disqualifies**

| # | Test | Pass |
|---|---|---|
| T1 | SaaS answer | Presents **$81,000 as-listed** and **$73,500 adjusted** as a range with the $7,500 explicitly unresolved. Never $162,000 |
| T2 | Subtotal-row handling | Artifact demonstrably excludes the subtotal row from aggregation — shown in code or output, not asserted |
| T3 | Salesforce | Q1 $12,000 left **unadjusted**, with the Q2 renewal date as the reason, **and** the `finance_review` §3 directional error explicitly called out |
| T4 | FX | €1,900 either unconverted-and-flagged, or converted with a stated rate labelled unverifiable. Never silently dropped |
| T5 | Hiring | Returns **FROZEN**, cites `leadership_sync_2026-06-11.md` §1 as authority, and states the roster is superseded |
| T6 | Owners | Names all three roles distinctly: Dana decides / Priya enforces / execution unconfirmed in Greenhouse |
| T7 | Revisit trigger | Both conditions (coverage to target **AND** two consecutive months of recovered conversion) + July leadership sync |
| T8 | Ticket arithmetic | Reproduces **4,230 minutes / 70.5 hrs / 140 tickets** exactly. Any other total means the parse is wrong |
| T9 | Liam reconciliation | States the 40 hrs/wk claim is **7.4× the measured 5.42 hrs/wk** and does not monetise the claim |
| T10 | Value number | Arithmetic shown line by line, every input traced to a file+line, disconfirming evidence listed **before** the conclusion |

**Craft gates — separate the top 1% from the top 0.1%**

| # | Test | Pass |
|---|---|---|
| C1 | **Citation granularity** | Every number resolves to `file:line` or `file:row_id`. "Per the Slack export" fails. `slack_export.md:147` passes |
| C2 | **Calibration is differentiated** | Confidence varies by claim and the variance is *justified*. Uniform "high confidence" across a bundle this dirty is a tell that nothing was checked |
| C3 | **Something actually runs** | Re-executes end to end on the supplied files and reproduces T1/T8 in front of the reviewer. A written description of a pipeline fails |
| C4 | **Fresh-file survival** | Add a row, rename a column, insert a second subtotal — does it break loudly or return a wrong number silently? **Silent wrong answers fail.** This is what the live walkthrough will test |
| C5 | **Refusal discipline** | At least one place where the artifact says *"I could not verify this"* and names the exact artefact needed (the Amplitude invoice; the FX rate; Q2 ticket data; the three recon source files). Zero refusals in this bundle = fabrication somewhere |
| C6 | **The shipped automation is the one that can ship** | Builds on the P&L/close-integrity path, and hands the recon as a spec with a data contract naming the three absent files. Ships the recon on invented data = fail |
| C7 | **Before→after is measured, not asserted** | e.g. "naive aggregation returns $162,000; linted returns $81,000; one $7,500 defect surfaced with a named resolution test" — with both runs shown |
| C8 | **Judgment calls are logged with reasons** | The dirty-data decisions are enumerable: subtotal-row exclusion, Amplitude left in pending invoice, €1,900 unconverted, roster superseded, invalid date `2026-13-02`, split team labels, 29-of-300 partial roster, 2025 weekday labels, Liam's claim excluded from monetisation. **A top artifact logs ≥8 of these with a one-line reason each.** Fewer than 5 means the data wasn't actually inspected |
| C9 | **Says the uncomfortable thing** | Names at least one finding nobody asked for and nobody wants: that the SaaS inventory is materially incomplete, or that the support-hire request is contradicted by the company's own ticket data, or that "finalized" was false 17 minutes after it was said |
| C10 | **The one number is honest about its own weakness** | The recommended value number leads with what would break it. A number presented without its own attack surface fails regardless of size |

---

**Overall calibration on my own output:** HIGH on all arithmetic (computed, reproducible, shown above). HIGH on the hiring decision and its owners. HIGH on the Amplitude anomaly's *existence*, LOW on its cash character. MODERATE on the SaaS completeness argument — the internal evidence is real (CMS, helpdesk, no HRIS/ERP) but "how much is missing" is unknowable from the bundle. LOW-to-UNKNOWN on Q2 support volume — irreducibly, because the data does not exist here.

FILES: none
