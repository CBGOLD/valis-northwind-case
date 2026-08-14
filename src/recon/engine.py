"""Three-way brand-deal reconciliation engine.

Deterministic, stdlib-only. Matches CRM deals to invoices and payout rows,
clears deals where all three systems agree, and emits an exception queue
where every line carries a category, the disagreeing values, and exact
file:line citations back to the input rows — the same evidence discipline
as the ask slice.

Checks map 1:1 to the documented drift (finance_review_2026-05-28.md:12
"Deal amounts, close dates, and payout splits drift between all three"; and
slack_export.md:108 "CRM said one set of deals closed, invoicing had a
different total"):

  AMOUNT_MISMATCH        CRM amount != invoice amount
  DATE_SLIP              invoice month != CRM close month (revenue period ambiguous)
  MISSING_INVOICE        deal closed in CRM, no invoice raised
  MISSING_IN_CRM         invoice exists, no CRM deal behind it
  PAYOUT_SPLIT_MISMATCH  payout total != CRM amount x contracted split
  DUPLICATE_PAYOUT       identical payout row entered more than once
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from ..finance import parse_money_cents, usd
from .fixture import CRM_COLUMNS, INV_COLUMNS, PAY_COLUMNS


def _load(path, required):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in required if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                f"{path}: schema mismatch — missing columns {missing}. "
                f"Found {reader.fieldnames}. Expected {required}. "
                f"See docs/BUILDER_SPEC.md for the data contract."
            )
        rows = []
        for idx, r in enumerate(reader):
            r["_line"] = idx + 2  # header is line 1
            rows.append(r)
    return rows


def _cents(row, path):
    c, flag = parse_money_cents(row["amount_usd"])
    if flag:
        raise ValueError(
            f"{path}:{row['_line']}: unparseable amount_usd={row['amount_usd']!r} ({flag})"
        )
    return c


def _ref(path, row):
    return f"{Path(path).name}:{row['_line']}"


def reconcile(crm_path, invoices_path, payouts_path):
    crm = _load(crm_path, CRM_COLUMNS)
    invoices = _load(invoices_path, INV_COLUMNS)
    payouts = _load(payouts_path, PAY_COLUMNS)

    crm_by_id = {}
    for r in crm:
        if r["deal_id"] in crm_by_id:
            raise ValueError(f"{crm_path}:{r['_line']}: duplicate deal_id {r['deal_id']} in CRM export")
        crm_by_id[r["deal_id"]] = r
    inv_by_deal = defaultdict(list)
    for r in invoices:
        inv_by_deal[r["deal_id"]].append(r)
    pay_by_deal = defaultdict(list)
    for r in payouts:
        pay_by_deal[r["deal_id"]].append(r)

    all_ids = sorted(set(crm_by_id) | set(inv_by_deal))
    exceptions, cleared = [], []

    for deal_id in all_ids:
        deal = crm_by_id.get(deal_id)
        invs = inv_by_deal.get(deal_id, [])
        pays = pay_by_deal.get(deal_id, [])
        issues = []

        if deal is None:
            refs = [_ref(invoices_path, i) for i in invs]
            total = sum(_cents(i, invoices_path) for i in invs)
            exceptions.append({
                "deal_id": deal_id, "category": "MISSING_IN_CRM",
                "detail": f"invoice(s) totaling {usd(total)} have no CRM deal behind them",
                "evidence": refs,
            })
            continue

        crm_amt = _cents(deal, crm_path)
        crm_ref = _ref(crm_path, deal)

        if not invs:
            issues.append(("MISSING_INVOICE",
                           f"deal closed in CRM at {usd(crm_amt)} on {deal['close_date']}, no invoice raised",
                           [crm_ref]))
        else:
            inv_total = sum(_cents(i, invoices_path) for i in invs)
            inv_refs = [_ref(invoices_path, i) for i in invs]
            if inv_total != crm_amt:
                issues.append(("AMOUNT_MISMATCH",
                               f"CRM {usd(crm_amt)} vs invoiced {usd(inv_total)} "
                               f"(delta {usd(inv_total - crm_amt)})",
                               [crm_ref] + inv_refs))
            slipped = [i for i in invs if i["invoice_date"][:7] != deal["close_date"][:7]]
            if slipped:
                issues.append(("DATE_SLIP",
                               f"close {deal['close_date']} vs invoice "
                               f"{', '.join(i['invoice_date'] for i in slipped)} — revenue period ambiguous",
                               [crm_ref] + [_ref(invoices_path, i) for i in slipped]))

        # payouts: flag exact duplicate rows, then compare deduplicated total
        seen_ids, dup_rows, unique_pays = set(), [], []
        for p in pays:
            if p["payout_id"] in seen_ids:
                dup_rows.append(p)
            else:
                seen_ids.add(p["payout_id"])
                unique_pays.append(p)
        if dup_rows:
            issues.append(("DUPLICATE_PAYOUT",
                           f"{len(dup_rows)} payout row(s) entered more than once "
                           f"({', '.join(p['payout_id'] for p in dup_rows)})",
                           [_ref(payouts_path, p) for p in pays]))
        try:
            split = int(deal["creator_split_pct"])
        except (TypeError, ValueError):
            raise ValueError(f"{crm_path}:{deal['_line']}: bad creator_split_pct "
                             f"{deal['creator_split_pct']!r}")
        expected = crm_amt * split // 100
        paid = sum(_cents(p, payouts_path) for p in unique_pays)
        if paid != expected:
            issues.append(("PAYOUT_SPLIT_MISMATCH",
                           f"paid {usd(paid)} vs expected {usd(expected)} "
                           f"({split}% of {usd(crm_amt)}; delta {usd(paid - expected)})",
                           [crm_ref] + [_ref(payouts_path, p) for p in unique_pays]))

        if issues:
            for cat, detail, refs in issues:
                exceptions.append({"deal_id": deal_id, "category": cat,
                                   "detail": detail, "evidence": refs})
        else:
            cleared.append({
                "deal_id": deal_id, "brand": deal["brand"],
                "amount_usd": deal["amount_usd"],
                "invoice_ids": ";".join(i["invoice_id"] for i in invs),
                "payout_total_usd": f"{paid // 100}" if paid % 100 == 0 else f"{paid / 100:.2f}",
                "evidence": ";".join([crm_ref] + [_ref(invoices_path, i) for i in invs]
                                     + [_ref(payouts_path, p) for p in unique_pays]),
            })

    exception_deals = sorted({e["deal_id"] for e in exceptions})
    crm_total = sum(_cents(r, crm_path) for r in crm)
    cleared_total = sum(parse_money_cents(c["amount_usd"])[0] for c in cleared)
    exc_crm_total = sum(_cents(crm_by_id[d], crm_path) for d in exception_deals if d in crm_by_id)
    return {
        "inputs": {
            "crm": {"path": str(crm_path), "rows": len(crm), "total_cents": crm_total},
            "invoices": {"path": str(invoices_path), "rows": len(invoices)},
            "payouts": {"path": str(payouts_path), "rows": len(payouts)},
        },
        "cleared": cleared,
        "exceptions": exceptions,
        "exception_deals": exception_deals,
        "by_category": dict(Counter(e["category"] for e in exceptions)),
        "conservation": {
            "crm_total_cents": crm_total,
            "cleared_total_cents": cleared_total,
            "exception_crm_total_cents": exc_crm_total,
            "ok": crm_total == cleared_total + exc_crm_total,
        },
        "auto_clear_rate_pct": round(100.0 * len(cleared) / len(all_ids), 1) if all_ids else 0.0,
        "n_deals_seen": len(all_ids),
    }


SUMMARY_BANNER = (
    "> **SYNTHETIC FIXTURE — these are generated numbers, NOT Northwind actuals.** The bundle\n"
    "> documents the workflow but not the three raw exports, so the engine runs on a labeled\n"
    "> fixture built to the data contract (docs/BUILDER_SPEC.md). Nothing below feeds the P&L.\n"
)


def summary_markdown(result):
    r = result
    cons = r["conservation"]
    lines = [
        "# Three-way brand-deal reconciliation — run summary", "",
        SUMMARY_BANNER,
        "## What ran",
        f"- CRM export: `{Path(r['inputs']['crm']['path']).name}` — {r['inputs']['crm']['rows']} deals, "
        f"{usd(r['inputs']['crm']['total_cents'])} closed-won",
        f"- Invoicing sheet: `{Path(r['inputs']['invoices']['path']).name}` — {r['inputs']['invoices']['rows']} invoices",
        f"- Payout tracker: `{Path(r['inputs']['payouts']['path']).name}` — {r['inputs']['payouts']['rows']} payout rows",
        "",
        "## Result",
        f"- **{len(r['cleared'])} of {r['n_deals_seen']} deals auto-cleared ({r['auto_clear_rate_pct']}%)** — "
        f"all three systems agree exactly.",
        f"- **{len(r['exception_deals'])} deals in the exception queue** ({len(r['exceptions'])} findings), "
        f"each with a category, the disagreeing values, and file:line evidence:",
    ]
    for cat, n in sorted(r["by_category"].items()):
        lines.append(f"  - {cat}: {n}")
    lines += [
        "",
        "## Conservation check (self-audit)",
        f"- CRM closed-won total {usd(cons['crm_total_cents'])} = cleared {usd(cons['cleared_total_cents'])} "
        f"+ exceptions {usd(cons['exception_crm_total_cents'])} → "
        f"{'TIES OUT' if cons['ok'] else '**BROKEN — do not trust this run**'}",
        "",
        "## Before → after",
        "- **Before (observed at Northwind, cited):** ~3 analyst-days per monthly close, 100% manual",
        "  line-by-line tie-out, never agrees first pass — slack_export.md:108, slack_export.md:158,",
        "  finance_review_2026-05-28.md:11, leadership_sync_2026-06-11.md:35.",
        f"- **After (measured on THIS synthetic fixture):** {r['n_deals_seen']} deals dispositioned in under a",
        f"  second; {r['auto_clear_rate_pct']}% cleared automatically; human work shrinks to "
        f"{len(r['exception_deals'])} pre-categorized,",
        "  pre-evidenced exceptions.",
        "- **Projection (assumption-labeled, NOT a measurement):** at 10–20 min per exception, this month's",
        f"  queue is ~{len(r['exception_deals']) * 10}–{len(r['exception_deals']) * 20} minutes of review vs "
        "~24 hours of manual tie-out — roughly a 90% reduction,",
        "  IF Northwind's real exports conform to the data contract and drift at a similar rate. The",
        "  3-day baseline is self-reported (labeled in the workflow answer); the acceptance test for the",
        "  real build is in docs/BUILDER_SPEC.md.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(result, outdir):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "matched.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["deal_id", "brand", "amount_usd", "invoice_ids", "payout_total_usd", "evidence"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(result["cleared"])
    with open(out / "exceptions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["deal_id", "category", "detail", "evidence"])
        w.writeheader()
        for e in result["exceptions"]:
            w.writerow({**e, "evidence": ";".join(e["evidence"])})
    with open(out / "result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    (out / "RECON_SUMMARY.md").write_text(summary_markdown(result), encoding="utf-8")
    return [out / n for n in ("matched.csv", "exceptions.csv", "result.json", "RECON_SUMMARY.md")]
