#!/usr/bin/env python3
"""Northwind ask-with-sources slice — answers the CEO's questions with exact
citations, calibrated confidence, and machine-verified receipts.

Usage:
  python3 ask.py q1                 # SaaS spend, with sources
  python3 ask.py q2                 # Sales hiring state, with sources
  python3 ask.py workflow           # where time is wasted / what to automate
  python3 ask.py value              # the one CFO-grade value number
  python3 ask.py check              # re-verify every citation against the raw files
  python3 ask.py build              # write out/: CEO one-pager (md+html) + audit
  python3 ask.py q1 --json          # any answer as JSON
  python3 ask.py q1 --pnl PATH      # run on a fresh compatible P&L
  python3 ask.py workflow --tickets PATH

Stdlib only. Deterministic: same inputs produce byte-identical outputs.
"""
import argparse
import json
import sys
from pathlib import Path

from src import answers as A
from src import render
from src.evidence import load_store, verify_all
from src.paths import OUT


def _emit(answer, args, store):
    if args.json:
        print(json.dumps(answer, indent=2, ensure_ascii=False))
    else:
        print(render.terminal(answer, store))


def cmd_check(_args):
    ok, fail, report = verify_all()
    for line in report:
        print(line)
    print(f"\n{ok} citations verified, {fail} failed.")
    return 1 if fail else 0


def cmd_build(args):
    store = load_store()
    trio = [A.q1(args.pnl, store), A.q2(store), A.workflow(args.tickets, store)]
    OUT.mkdir(parents=True, exist_ok=True)
    targets = {
        OUT / "CEO_ANSWERS.md": render.ceo_markdown(trio, store),
        OUT / "CEO_ANSWERS.html": render.ceo_html(trio, store),
        OUT / "AUDIT.md": render.audit_markdown(store),
    }
    for path, content in targets.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(Path.cwd()) if path.is_relative_to(Path.cwd()) else path}")
    ok, fail, _ = verify_all(store)
    print(f"citation re-verification: {ok} ok, {fail} failed")
    return 1 if fail else 0


def cmd_value(args):
    store = load_store()
    v = A.value(args.pnl, store)
    if args.json:
        print(json.dumps(v, indent=2, ensure_ascii=False))
        return 0
    print("=" * 78)
    print("THE ONE CFO-GRADE VALUE NUMBER")
    print("=" * 78)
    print(f"\n{v['headline']}\n")
    if v.get("framing"):
        print(f"{v['framing']}\n")
    print(f"Baseline: {v['baseline']}")
    print("Arithmetic:")
    for a in v["arithmetic"]:
        print(f"  - {a}")
    print("Exact source rows:")
    for cid in v["claims"]:
        for c in store["claims"][cid]["citations"]:
            print(f"  -> {c['file']}:{c['line']}  “{c['quote']}”")
    print("Explicitly NOT verified:")
    for u in v["unverified"]:
        print(f"  - {u}")
    print(f"Confidence: {v['confidence']}")
    print(f"Worksheet a finance person can attack: docs/VALUE_NUMBER.md")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["q1", "q2", "workflow", "value", "check", "build"])
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    ap.add_argument("--pnl", default=None, help="path to a compatible P&L CSV (fresh-input mode)")
    ap.add_argument("--tickets", default=None, help="path to a compatible ticket CSV (fresh-input mode)")
    args = ap.parse_args(argv)

    if args.command == "check":
        return cmd_check(args)
    if args.command == "build":
        return cmd_build(args)
    if args.command == "value":
        return cmd_value(args)

    store = load_store()
    if args.command == "q1":
        _emit(A.q1(args.pnl, store), args, store)
    elif args.command == "q2":
        _emit(A.q2(store), args, store)
    elif args.command == "workflow":
        _emit(A.workflow(args.tickets, store), args, store)
    return 0


if __name__ == "__main__":
    sys.exit(main())
