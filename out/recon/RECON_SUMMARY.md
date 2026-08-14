# Three-way brand-deal reconciliation — run summary

> **SYNTHETIC FIXTURE — these are generated numbers, NOT Northwind actuals.** The bundle
> documents the workflow but not the three raw exports, so the engine runs on a labeled
> fixture built to the data contract (docs/BUILDER_SPEC.md). Nothing below feeds the P&L.

## What ran
- CRM export: `SYNTHETIC_crm_deals_2026-06.csv` — 27 deals, $1,515,500 closed-won
- Invoicing sheet: `SYNTHETIC_invoices_2026-06.csv` — 27 invoices
- Payout tracker: `SYNTHETIC_payouts_2026-06.csv` — 40 payout rows

## Result
- **20 of 28 deals auto-cleared (71.4%)** — all three systems agree exactly.
- **8 deals in the exception queue** (8 findings), each with a category, the disagreeing values, and file:line evidence:
  - AMOUNT_MISMATCH: 2
  - DATE_SLIP: 2
  - DUPLICATE_PAYOUT: 1
  - MISSING_INVOICE: 1
  - MISSING_IN_CRM: 1
  - PAYOUT_SPLIT_MISMATCH: 1

## Conservation check (self-audit)
- CRM closed-won total $1,515,500 = cleared $1,146,000 + exceptions $369,500 → TIES OUT

## Before → after
- **Before (observed at Northwind, cited):** ~3 analyst-days per monthly close, 100% manual
  line-by-line tie-out, never agrees first pass — slack_export.md:108, slack_export.md:158,
  finance_review_2026-05-28.md:11, leadership_sync_2026-06-11.md:35.
- **After (measured on THIS synthetic fixture):** 28 deals dispositioned in under a
  second; 71.4% cleared automatically; human work shrinks to 8 pre-categorized,
  pre-evidenced exceptions.
- **Projection (assumption-labeled, NOT a measurement):** at 10–20 min per exception, this month's
  queue is ~80–160 minutes of review vs ~24 hours of manual tie-out — roughly a 90% reduction,
  IF Northwind's real exports conform to the data contract and drift at a similar rate. The
  3-day baseline is self-reported (labeled in the workflow answer); the acceptance test for the
  real build is in docs/BUILDER_SPEC.md.
