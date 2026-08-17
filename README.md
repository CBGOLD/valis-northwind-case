# Northwind — a trust slice, not another dashboard

Dana's problem is not missing data; it's that no number she sees carries its own proof. This repo is
the smallest slice of the fix: **ask a question, get an answer-first read with exact file:line
receipts, calibrated confidence, and what would change the answer** — plus one shipped automation
aimed at the company's #1 documented time sink.

## Start here

**Live website:** [cbgold.github.io/valis-northwind-case](https://cbgold.github.io/valis-northwind-case/)
— the executive Decide/Learn surface plus a working in-browser reconciliation. It is a self-contained
root `index.html`: a zero-command path with no install, framework, font, CDN, or network dependency.
Download the repo and open `index.html` directly if GitHub Pages is unavailable.

**Review it in five minutes:** follow [`REVIEW_GUIDE.md`](REVIEW_GUIDE.md) for the exact route—read the
three decisions, run the baseline, inspect evidence, inject an orphan, export the queue, then audit
the AI/process logs—with what each action proves and what remains deliberately out of scope.

**Build & AI logs:** [`BUILD_LOG.md`](BUILD_LOG.md) is the timestamped work log. [`llm_logs/README.md`](llm_logs/README.md)
is the index of every prompt, run, and transcript. These are plain files in this repository, not GitHub
"commit history with timers" — open them directly if the GitHub UI doesn't surface timing for you.

Opening the website needs nothing installed — it is one self-contained HTML file. Reproducing the
build needs Python 3.9+ (stdlib only); `make test` additionally uses Node.js to execute the four
browser-parity tests against the embedded engine. The untouched source bundle lives in
`input/Northwind-in-a-box_charles/`.

## Reproduce it (optional; two commands)

```bash
make demo    # the CEO's questions answered in the terminal, with receipts
make all     # verify all 86 citations + rebuild out/ + run the 85-test suite
```

## The answers (60-second version, as of 2026-06-18 — the bundle's export date)

**Q1 — SaaS spend last quarter?** Best estimate **$73,500**. The books say **$81,000** and the
arithmetic ties, but that includes a suspected $7,500 double-entry ("Amplitude" + "Amplitude
Analytics", identical amounts, identical notes) that finance itself is 90% sure about and never
confirmed — the invoice hasn't come back. Bounded: $73,500–$81,000; one invoice pull settles it.
Salesforce ($12,000) stands for Q1 — the $60k/yr renewal is a Q2 signing — but is booked-but-unverified,
and finance's own review note gets the comparison backwards. Excludes Infrastructure (AWS $38k;
Cloudflare €1,900 — unconverted, no FX rate exists in the bundle).

**Q2 — Sales hiring?** **FROZEN.** Dana announced it 2026-06-10 in #leadership, minuted 2026-06-11:
all net-new Sales headcount frozen until pipeline recovers; REQ-114 paused, not killed; Sales-only.
Dana owns the decision, Priya enforces it (no Sales req without her sign-off). The May 1 roster
still says APPROVED — explicitly superseded. Revisit: pipeline coverage at target + two consecutive
months of recovered conversion, re-evaluated at the July sync. Caveat that matters: the freeze is
unambiguous in the humans and **unconfirmed in the systems** (Greenhouse pause unverified; a
late-stage candidate's handling was due 2026-06-13 with no resolution on record).

**Workflow — automate what first?** The **monthly brand-deal three-way reconciliation** (CRM vs
invoicing vs payout tracker): ~3 analyst-days every month, corroborated seven times across three
source types, sitting under $4.2M/quarter of brand revenue. Meanwhile the loudly-claimed support
crisis measures at **5.48 h/week** against a claimed 40 — the company's own ticket log kills the
case for a support hire. Tax forms have a buy-not-build answer. So: reconcile first, buy the
tax-form tool, automate thumbnails later.

**The CFO number:** $7,500/quarter of suspected double-booked SaaS (9.3% of the line; $30,000/yr
run-rate if it recurs) — full worksheet with attack surface in `docs/VALUE_NUMBER.md`.

## What runs on what (honest split)

- **On the real bundle:** the ask slice — every number recomputed from the raw CSVs at answer time
  (booked/adjusted SaaS, the $162k naive-sum trap, ticket arithmetic), the hiring supersession
  resolver, and machine-verification of all 86 citations (`python3 ask.py check` re-opens every
  cited file and asserts each quote sits on its exact line).
- **On a labeled synthetic fixture:** the reconciliation engine (`python3 recon.py demo`) — the
  bundle documents the workflow but not the three raw exports, so the engine demonstrates on
  generated data built to the real data contract (`docs/BUILDER_SPEC.md`), simulating a month that
  has no actuals in the bundle. Fixture provenance and anti-confusion measures: `fixtures/README.md`.
  Nothing synthetic feeds any Northwind answer.

## Try to break it (live-walkthrough script)

```bash
python3 ask.py q1 --pnl your_fresh_pnl.csv     # numbers recompute; duplicates re-detected generically
python3 ask.py check                            # tamper with a quote in evidence/citations.json first — it fails loudly
python3 recon.py fixture --seed 7 --outdir /tmp/f && \
python3 recon.py run --crm /tmp/f/SYNTHETIC_crm_deals_2026-06.csv \
  --invoices /tmp/f/SYNTHETIC_invoices_2026-06.csv \
  --payouts /tmp/f/SYNTHETIC_payouts_2026-06.csv --outdir /tmp/f/out   # unseen seed, same guarantees
make test                                       # 85 tests incl. browser/Python recon parity (Node.js) + fixture scoring
```

Hand `recon.py run` any three CSVs matching the contract — a schema mismatch names the missing
columns instead of guessing.

## Map

| Path | What |
|---|---|
| `ask.py` / `recon.py` | the two entry points (CLI help in each) |
| `out/CEO_ANSWERS.md` / `.html` | the CEO one-pager (mobile-readable); `out/AUDIT.md` = quote-level audit appendix |
| `out/recon/` | reconciliation run: matched, exceptions (with row evidence), summary with before→after |
| `evidence/citations.json` | the claim→citation store (all claims, confidence, exact quotes) |
| `docs/VALUE_NUMBER.md` | the CFO worksheet, attacks pre-answered |
| `docs/BUILDER_SPEC.md` | one-page remote-builder spec: scope, data contract, acceptance test |
| `docs/DECISIONS.md` | all 21 dirty-data judgment calls, one-line reasons |
| `REVIEW_GUIDE.md` | explicit 5-minute reviewer route: action → proof → deliberate boundary |
| `BUILD_LOG.md` / `llm_logs/` | timestamped build log; prompts + model runs (AI-native process, disclosed) |

## Limits, stated plainly

The citation store was curated by a human+AI pass over the bundle (that judgment is logged); the
artifact then makes it mechanical — quotes are machine-verified, numbers recomputed, supersession
resolved by rule. On a fresh bundle the math and checks port; the curated claims are Northwind-
specific by design. The recon baseline (~3 days/month) is corroborated testimony, never a
measurement — it is labeled that way everywhere it appears.
