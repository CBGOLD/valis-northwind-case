#!/usr/bin/env python3
"""Brand-deal three-way reconciliation — the automation for Northwind's #1
documented time sink (CRM export vs invoicing sheet vs payout tracker).

The bundle documents this workflow but does not contain the three raw
exports, so `demo` runs the engine end-to-end on a clearly-labeled SYNTHETIC
fixture generated to the data contract in docs/BUILDER_SPEC.md. `run` works
on any CSVs matching that contract — including a fresh set handed over
during a live walkthrough.

Usage:
  python3 recon.py demo                       # fixture (seed 26) -> engine -> out/recon/
  python3 recon.py fixture --seed 26 --outdir fixtures
  python3 recon.py run --crm F --invoices F --payouts F --outdir out/recon
"""
import argparse
import sys
from pathlib import Path

from src.recon.engine import reconcile, write_outputs
from src.recon.fixture import MONTH, generate


def cmd_fixture(args):
    manifest = generate(seed=args.seed, outdir=args.outdir)
    print(f"SYNTHETIC fixture written to {args.outdir}/ (seed={args.seed}): "
          f"{manifest['n_crm_deals']} CRM deals, {manifest['n_invoices']} invoices, "
          f"{manifest['n_payout_rows']} payout rows")
    return 0


def cmd_run(args):
    result = reconcile(args.crm, args.invoices, args.payouts)
    paths = write_outputs(result, args.outdir)
    cons = result["conservation"]
    print(f"{result['n_deals_seen']} deals: {len(result['cleared'])} auto-cleared "
          f"({result['auto_clear_rate_pct']}%), {len(result['exception_deals'])} in exception queue "
          f"({len(result['exceptions'])} findings)")
    for cat, n in sorted(result["by_category"].items()):
        print(f"  {cat}: {n}")
    print(f"conservation: {'TIES OUT' if cons['ok'] else 'BROKEN'}")
    for p in paths:
        print(f"wrote {p}")
    return 0 if cons["ok"] else 1


def cmd_demo(args):
    fixtures = Path("fixtures")
    generate(seed=args.seed, outdir=fixtures)
    ns = argparse.Namespace(
        crm=fixtures / f"SYNTHETIC_crm_deals_{MONTH}.csv",
        invoices=fixtures / f"SYNTHETIC_invoices_{MONTH}.csv",
        payouts=fixtures / f"SYNTHETIC_payouts_{MONTH}.csv",
        outdir=args.outdir,
    )
    print(f"[demo] generated SYNTHETIC fixture (seed={args.seed}) — labeled, never Northwind actuals")
    return cmd_run(ns)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    f = sub.add_parser("fixture", help="generate the labeled synthetic fixture")
    f.add_argument("--seed", type=int, default=26)
    f.add_argument("--outdir", default="fixtures")

    r = sub.add_parser("run", help="reconcile three CSVs matching the data contract")
    r.add_argument("--crm", required=True)
    r.add_argument("--invoices", required=True)
    r.add_argument("--payouts", required=True)
    r.add_argument("--outdir", default="out/recon")

    d = sub.add_parser("demo", help="fixture + run in one step")
    d.add_argument("--seed", type=int, default=26)
    d.add_argument("--outdir", default="out/recon")

    args = ap.parse_args(argv)
    return {"fixture": cmd_fixture, "run": cmd_run, "demo": cmd_demo}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
