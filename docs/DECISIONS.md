# Dirty-data judgment calls

Every place the data was inconsistent, ambiguous, or untrustworthy, what I did about it, and why —
one line of reason each. Citations are verifiable: `python3 ask.py check`.

## Financial

1. **Two Amplitude lines, $7,500 each (`pnl_q1_2026.csv:12–13`)** — kept in the booked figure,
   removed in the adjusted figure, answer stated as a bounded range. *Reason: finance itself is 90%
   sure it's a double-entry but the invoice never came back (`slack_export.md:147,150,153`); neither
   asserting nor ignoring the duplicate is defensible, so the answer carries both states.*
2. **Salesforce $12,000 vs $60k/yr renewal (`pnl_q1_2026.csv:9`, `slack_export.md:119`)** — Q1 left
   unadjusted. *Reason: the renewal was signed 2026-05-14 (Q2) covering "through next May"; it cannot
   restate Q1. Forward run-rate +$3,000/qtr noted separately.*
3. **The finance-review note's direction is backwards (`finance_review_2026-05-28.md:23`)** — called
   out, not repeated. *Reason: "looks higher than a $60k annual would imply" fails arithmetic —
   $12k/qtr annualizes to $48k, below $60k; a note that fails its own math is evidence to audit, not
   to quote.*
4. **Subtotal row shares the `Software & SaaS` category (`pnl_q1_2026.csv:24`)** — excluded from all
   sums. *Reason: a naive category sum returns $162,000, a 100% overstatement; `tests/test_finance.py`
   proves the code avoids it.*
5. **Cloudflare billed €1,900 in a USD column (`pnl_q1_2026.csv:26`)** — left unconverted and
   flagged. *Reason: no FX rate exists anywhere in the bundle; converting would be a fabricated input.*
6. **Blank cells: Office supplies, Infrastructure subtotal (`pnl_q1_2026.csv:35,27`)** — no values
   invented; noted that the P&L cannot be totaled as supplied. *Reason: blanks are pending AP coding /
   FX by finance's own annotation.*
7. **SaaS completeness** — flagged that $81k is the booked line, not a software inventory (CMS and
   ticketing system in daily use with no line item; no HRIS/payroll or accounting line for ~300 FTE).
   *Reason: usage evidence exists (`slack_export.md:165`; the ticket log itself); magnitude does not,
   so it is flagged, never estimated.*

## Hiring

8. **Roster says REQ-114 APPROVED (`headcount_roster.csv:22`)** — treated as a stale snapshot, not
   current state. *Reason: the 2026-06-11 minutes explicitly supersede it and People declared it stale
   (`leadership_sync_2026-06-11.md:16`, `slack_export.md:230`); chronology + authority beat a snapshot.*
9. **Decision date: announced vs minuted** — reported as "announced 2026-06-10, minuted 2026-06-11".
   *Reason: Slack timestamp, the minutes' date, and Elena's "yesterday's leadership call" reconcile
   cleanly under that reading; substance is identical either way.*
10. **Freeze executed in systems?** — reported as UNVERIFIED. *Reason: no evidence the Greenhouse req
    was paused, the roster was never restated, and the late-stage-candidate action (due 2026-06-13)
    shows no resolution; decided-in-humans ≠ done-in-systems.*

## Support / workflow

11. **"Easily 40 hrs/week" (`slack_export.md:176`)** — measured against the company's own log and not
    monetized. *Reason: 140 tickets, 4,230 minutes = 5.48 h/week; the claim is 7.3× the whole queue
    and 8.1× like-for-like on the categories named. Vibes are not savings.*
12. **"Thumbnail swap request #47 this week" (`slack_export.md:193`)** — left open, two readings
    stated. *Reason: no Q2 ticket data exists; as a weekly rate it's ~10× Q1, as a cumulative count
    it's consistent — unverifiable, so it must not silently support either side.*
13. **Recon baseline (~3 days/month)** — used as a *reported* figure, labeled as such everywhere.
    *Reason: seven corroborating statements across three source types, but no timesheet exists in the
    bundle; corroborated testimony is strong evidence and still not a measurement.*
14. **The three recon exports are absent from the bundle** — the automation runs on a clearly-labeled
    synthetic fixture; the builder spec carries the real data contract. *Reason: the brief forbids
    manufacturing source-system evidence; the fixture simulates June 2026, a month with no actuals
    anywhere in the bundle, so synthetic output can never be mistaken for a Northwind number.*

## Cross-cutting data quality

15. **Slack weekday labels match the 2025 calendar for 13 of 20 dates** (e.g. "Fri May 2" is a
    Saturday in 2026) — ISO-style dates treated as authoritative, weekday labels ignored. *Reason:
    the ISO dates are internally consistent and both decision-bearing dates (Jun 10/11) carry correct
    2026 weekdays; judged a generation artifact, logged, not built on.*
16. **Roster defects** — invalid start date `2026-13-02`, a blank start date, a blank req target
    date, two spellings of one team, and a 29-row employee sample against a stated 300 headcount.
    *Reason: the roster is used only for cited rows and the summary section; nothing aggregates its
    employee list.*
17. **Org chart vs roster reporting-line conflict** (Ben Okoro under CEO in the chart, under Raj Patel
    in the roster) — flagged, unresolved. *Reason: no third source arbitrates; headcounts, by
    contrast, tie exactly to 300 in both files.*
18. **Ticket log tail out of order** (TCK-1131–1140 carry January–March dates after the March block)
    — included in all counts. *Reason: dates are in-quarter; ordering suggests late logging, which is
    a process note, not an exclusion reason.*
19. **4 tickets with blank `Assigned_To`, 2 still `Open` at quarter end** — included; flagged.
    *Reason: handle-minutes are recorded either way; excluding them would understate the queue.*
20. **Hours/week denominator** — 90-day quarter (12.86 weeks), stated explicitly. *Reason: the
    alternative (13 calendar weeks) shifts 5.48 to 5.42 h/week; immaterial, but the denominator
    should never be silent.*
21. **Creator count 1,210 vs 1,840** — not used in any answer. *Reason: it is a definitional split
    (posted-in-30d vs under-contract), not an error; it's logged in the evidence store because the
    CEO will eventually ask.*
