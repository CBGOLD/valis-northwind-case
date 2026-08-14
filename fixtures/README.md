# Fixtures — SYNTHETIC data, never Northwind actuals

Everything in this directory except this README is **generated, synthetic data**. No file here is,
or is derived from, a real Northwind export. This README is authored and committed; `make clean`
removes the generated files and keeps it.

## Why a synthetic fixture exists at all

The bundle documents the monthly brand-deal three-way reconciliation — the three systems
(`slack_export.md:100`), the drift types (`finance_review_2026-05-28.md:12`), and the ~3 days/month
cost — but it does **not** contain the three raw exports themselves:

1. the CRM deal export,
2. the invoicing sheet,
3. the payout tracker.

Rather than invent "Northwind" data or ship an engine that can't run, the reconciliation engine
demonstrates on this labeled fixture, generated to the data contract in `docs/BUILDER_SPEC.md`.
The fixture simulates **June 2026** — the next close, a month with no actuals anywhere in the
bundle — so a synthetic output can never be confused with an observed Northwind number.

## Provenance

| | |
|---|---|
| Generator | `src/recon/fixture.py` (seeded, deterministic; stdlib `random.Random`) |
| Committed seed | **26** |
| Files | `SYNTHETIC_crm_deals_2026-06.csv`, `SYNTHETIC_invoices_2026-06.csv`, `SYNTHETIC_payouts_2026-06.csv`, `fixture_manifest.json` |
| Injected defects | 1:1 with the drift types documented in the bundle (amount mismatch, date slip, missing invoice, payout-split mismatch, duplicate payout, ghost invoice) |
| Answer key | `fixture_manifest.json` records exactly which deals got which defect. The engine **never reads it**; tests use it to score recall/precision (`tests/test_recon.py`). |

Anti-confusion measures: every filename carries the `SYNTHETIC_` prefix, the manifest opens with a
WARNING line, and the generated `out/recon/RECON_SUMMARY.md` banners its own synthetic status.

## What this fixture may and may not support

**May support:** demonstrating the reconciliation engine end-to-end; scoring the engine against a
known answer key; proving determinism (same seed → byte-identical files) and schema-failure
behavior; proving the matcher is not fitted to one dataset (fresh seeds in `make fresh` and
`tests/test_recon.py`).

**May never support:** any answer about Northwind. No number derived from these files is a
Northwind number — not revenue, not exception rates, not time saved. Nothing synthetic feeds any
CEO answer, the CFO value number, or any citation in `evidence/citations.json` (all of which trace
to the real bundle in `input/Northwind-in-a-box_charles/` only).

## Replay commands

```bash
# regenerate the committed fixture (seed 26) byte-identically:
python3 recon.py fixture --seed 26 --outdir fixtures

# run the engine on it:
python3 recon.py demo

# prove nothing is fitted to seed 26 — any other seed, same guarantees:
python3 recon.py fixture --seed 99 --outdir /tmp/northwind-fresh
python3 recon.py run --crm /tmp/northwind-fresh/SYNTHETIC_crm_deals_2026-06.csv \
  --invoices /tmp/northwind-fresh/SYNTHETIC_invoices_2026-06.csv \
  --payouts /tmp/northwind-fresh/SYNTHETIC_payouts_2026-06.csv \
  --outdir /tmp/northwind-fresh/out

# verify the committed fixture is exactly what seed 26 produces (no hand edits):
python3 -m unittest tests.test_recon.TestFixture.test_committed_fixture_matches_generator -v
```

When the three real exports become available, the engine runs on them unchanged via
`recon.py run` — a schema mismatch fails loudly with the missing columns named
(`docs/BUILDER_SPEC.md` is the contract).
