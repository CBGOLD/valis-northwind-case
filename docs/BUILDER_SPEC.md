# Builder spec — monthly brand-deal three-way reconciliation (one page)

**Hand-off target:** a remote builder with no Northwind context. **Goal:** replace the ~3
analyst-days of manual month-end tie-out (`slack_export.md:108`, `finance_review_2026-05-28.md:11`)
with an automated three-way match that clears agreeing deals and emits an evidence-cited exception
queue. A reference implementation of the matching rules ships in this repo (`src/recon/engine.py`,
runnable via `python3 recon.py`); the builder's job is to wire it to the real exports and schedule it.

## Scope

**In:** ingest the three monthly exports → validate schema → three-way match → write
`matched.csv`, `exceptions.csv`, `RECON_SUMMARY.md` → post the summary to #finance.
**Out:** fixing exceptions (human), changing upstream systems, payments, FX, revenue recognition
policy, dashboards, anything real-time (this is a monthly batch).

## Data contract — the three real files (named in `slack_export.md:100`)

| File (monthly export) | Required columns | Types / rules |
|---|---|---|
| CRM deal export | `deal_id`, `brand`, `creator_handle`, `amount_usd`, `close_date`, `stage`, `owner_rep`, `creator_split_pct` | `deal_id` unique, join key; `amount_usd` USD decimal; `close_date` ISO `YYYY-MM-DD`; `creator_split_pct` integer 0–100 |
| Invoicing sheet | `invoice_id`, `deal_id`, `brand`, `amount_usd`, `invoice_date`, `status` | ≥0 invoices per deal; amounts sum per deal |
| Payout tracker | `payout_id`, `deal_id`, `creator_handle`, `amount_usd`, `paid_date` | ≥0 rows per deal; installments allowed |

Reject the run loudly (named missing columns, no partial output) on any schema mismatch. Money is
compared in integer cents — never floats. **Open item for the builder: these column names are a
proposed contract derived from how the sources describe each system — confirm against the real
exports before build; only the three-system shape and the drift types are documented fact.**

## Matching rules → exception categories (map 1:1 to documented drift, `finance_review_2026-05-28.md:12`)

| Check | Category |
|---|---|
| deal in CRM, no invoice | `MISSING_INVOICE` |
| invoice with no CRM deal | `MISSING_IN_CRM` |
| payout with no CRM deal | `ORPHAN_PAYOUT` |
| CRM amount ≠ invoiced total (cents-exact) | `AMOUNT_MISMATCH` |
| invoice month ≠ close month | `DATE_SLIP` |
| deduped payouts ≠ amount × split (cents-exact) | `PAYOUT_SPLIT_MISMATCH` |
| identical payout row entered twice | `DUPLICATE_PAYOUT` |

A deal clears only if every check passes; every exception row carries the disagreeing values and
`file:line` references into the source exports.

## Acceptance test — "answer-complete"

1. **Total disposition:** every `deal_id` appearing in any of the three files — CRM, invoices, or
   payouts — is dispositioned exactly once (cleared or exception); nothing silently dropped,
   including a payout row referencing a `deal_id` the CRM export never mentions (`ORPHAN_PAYOUT`).
   Shown in the summary's "Total disposition" block and asserted in code (`reconcile()`'s
   `disposition.complete`).
2. **Conservation:** CRM closed-won total = cleared total + exception-deals total, shown in the
   summary and asserted in code. This check is scoped to `deal_id`s present in the CRM export by
   construction — it cannot see money invoiced or paid against a `deal_id` absent from the CRM. That
   money is a separate guarantee (test #1 above) and is reported separately (`MISSING_IN_CRM` /
   `ORPHAN_PAYOUT` totals) rather than being folded into "ties out."
3. **Evidence:** every exception carries ≥1 source-row reference; spot-checking 5 random exceptions
   against the raw files finds zero mismatches.
4. **Determinism:** same inputs → byte-identical outputs, twice in a row.
5. **Fresh-file survival:** a schema-violating file fails loudly with the missing columns named; a
   valid file from a different month runs with no code changes.
6. **Seeded-defect recall:** on a fixture with known injected defects (generator in
   `src/recon/fixture.py`), recall and precision are 100% per category (`tests/test_recon.py` is the
   executable version of this test).

## Definition of done

Runs end-to-end on the three real May-2026 exports in <60s; Maya reviews only the exception queue;
first-pass summary posted to #finance without manual edits. Reported baseline to beat: ~3 days/close,
self-reported (never system-measured — capture actual review time from cycle 1 to replace it).
