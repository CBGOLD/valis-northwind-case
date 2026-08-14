# The one CFO-grade value number — worksheet

> **The Q1 SaaS line is 9.3% wrong in one of two ways. 90%-suspected: a $7,500 double-posting to
> restate — an accounting fix, cash recovery $0. 10%-possible: $30,000/yr of duplicate tooling to
> consolidate. One invoice pull, owed to the CFO since 2026-06-02, decides which.**

The two branches are financially unlike — the likely one returns no cash, only a correct published
number — so the headline carries both, with their probabilities. Framed as **exposure with a named
resolution test**, not as a booked saving. Run `python3 ask.py value` for the live version (numbers
recomputed from the P&L at runtime).

## Baseline

| | |
|---|---|
| Booked Q1 2026 SaaS subtotal | **$81,000** — recomputed from the 15 line items; ties exactly to the stated subtotal (`pnl_q1_2026.csv:24`) and to the CFO's own statement (`slack_export.md:144`) |

## Arithmetic

```
pnl_q1_2026.csv:12   Software & SaaS, Amplitude,           7500, "Product analytics"
pnl_q1_2026.csv:13   Software & SaaS, Amplitude Analytics, 7500, "Product analytics"
                     identical amount · identical note · adjacent rows

Booked Q1 SaaS                                   =  $81,000
− suspected duplicate                            −   $7,500
Defensible Q1 SaaS if duplicate confirmed        =  $73,500
Share of published line                          =   7,500 / 81,000 = 9.26%
Annualized IF the entry recurs quarterly         =   $7,500 × 4 = $30,000/yr   (labeled run-rate)
```

## Exact source rows

- `pnl_q1_2026.csv:12` and `:13` — the two lines.
- `slack_export.md:147` — Maya (Finance Analyst, closest to AP): *"I'm 90% sure that's the same
  product entered twice but I haven't confirmed against the invoice."*
- `slack_export.md:150` — Priya (CFO): *"that smells like a double-count."*
- `slack_export.md:153` — Maya: *"Haven't gotten the invoice back yet so I'm leaving the CSV as-is."*

## Explicitly NOT verified

1. **The Amplitude invoice itself** — not in the bundle; requested 2026-06-02, never returned
   (open ≥15 days at the export date).
2. **Recurrence beyond Q1** — one quarter of P&L exists; $30,000/yr assumes the entry repeats.
3. **Cash character** — if it is one invoice posted twice, cash recovery is $0 and the finding is a
   9.3% overstatement of a published number. **No cash-recovery claim is made.**
4. **Two-distinct-products possibility** — the analyst's own estimate leaves ~10% for it. Nothing in
   the bundle confirms or denies that two distinct products exist behind the two names; identical
   pricing and identical notes make it unlikely; only the invoice decides.

## How a finance person will attack it — answered in advance

| Attack | Answer |
|---|---|
| "Did you pull the invoice?" | No — it isn't in the bundle, and inventing it is disqualifying. That absence *is* the finding: a $30k/yr question has sat unresolved for 15+ days waiting on a single invoice pull. |
| "It might be two real contracts." | Then it's $30,000/yr of duplicate tooling to consolidate and two rows to rename. Both branches of the test are actionable; neither leaves the books as they are. |
| "This is only $7,500." | It's 9.3% of the line the CEO asked about, at a company the board just pushed on cost discipline (`slack_export.md:42`). And it is the only number in the bundle wrong by a *knowable* amount. |
| "Your bigger candidates?" | Considered and rejected below — they die faster under this table's logic. |

## Alternatives considered and rejected

- **$41,600/yr avoided support hire** (kill the 40 h/wk case with the ticket log). Rejected as *the*
  number: it dies on "your ticket log may be incomplete", which cannot be refuted from the bundle
  (no Q2 data; possible untracked work). The analysis still stands in the workflow answer — as a
  hiring input, not a claimed saving.
- **$5,760/yr recon labor** (288 reported hrs/yr × $20/hr blended). Rejected: monetization dies on
  "you don't fire Maya" — cash saved is $0; the real recon payoff is close-speed and first-pass-
  trustworthy revenue, which is not a defensible dollar figure. Blended-rate derivation kept for
  transparency: $3,120,000/qtr ÷ 300 FTE ÷ 520 hrs = **$20.00/hr** (`pnl_q1_2026.csv:7`,
  `headcount_roster.csv:18`) — a company-wide blend, almost certainly understating a finance analyst,
  and deliberately not uplifted (no per-person compensation data exists in the bundle).

## Resolution test (the actual deliverable)

Pull the Q1 Amplitude invoice(s) + vendor statement — already action-itemed by finance on 2026-06-02:

- **One contract, posted twice** → restate Q1 SaaS to $73,500; raise the AP exception; check whether
  cash left twice.
- **Two contracts** → consolidate $30,000/yr of duplicate tooling; rename both rows so this never
  recurs.

**Confidence:** MODERATE-HIGH that the published number is wrong by 9.3% in one of two ways; LOW on
cash recovery (deliberately unclaimed). If the invoice refutes the duplicate, this number voids —
that is the design, not a weakness.
