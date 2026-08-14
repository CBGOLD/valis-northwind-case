"""Seeded generator for a SYNTHETIC month of brand-deal exports.

Northwind's bundle documents the reconciliation workflow (three systems,
monthly drift: slack_export.md:100, finance_review_2026-05-28.md:12) but does
NOT contain the raw CRM/invoicing/payout exports. So the automation runs on
this clearly-labeled synthetic fixture, generated to the data contract in
docs/BUILDER_SPEC.md with drift types injected 1:1 from the documented drift
("deal amounts, close dates, and payout splits", plus totals that disagree
because records are missing on one side).

The fixture simulates the NEXT close (June 2026) — a month with no actuals
anywhere in the bundle, so synthetic output can never be confused with an
observed Northwind number. The generator writes an answer-key manifest for
testing; the reconciliation engine never reads it.
"""
import csv
import json
import random
from pathlib import Path

MONTH = "2026-06"
BRANDS = [
    "Solstice Beverages", "Nimbus Athletics", "Copperleaf Home", "Vela Cosmetics",
    "Truepath Finance", "Orbit Snacks", "Meridian Travel", "Lumen Audio",
    "Fernwood Outdoors", "Atlas Gaming", "Bluebird Software", "Cascade Skincare",
]
CREATORS = [
    "fx_aurora", "fx_basalt", "fx_cinder", "fx_delta", "fx_ember", "fx_flint",
    "fx_garnet", "fx_harbor", "fx_indigo", "fx_juniper", "fx_krill", "fx_lumen",
]
REPS = ["rep_alvarez", "rep_brooks", "rep_chen", "rep_dubois"]

CRM_COLUMNS = ["deal_id", "brand", "creator_handle", "amount_usd", "close_date", "stage", "owner_rep", "creator_split_pct"]
INV_COLUMNS = ["invoice_id", "deal_id", "brand", "amount_usd", "invoice_date", "status"]
PAY_COLUMNS = ["payout_id", "deal_id", "creator_handle", "amount_usd", "paid_date"]

N_DEALS = 27          # deals present in CRM
INJECTIONS = {        # documented drift types -> how many deals get each
    "AMOUNT_MISMATCH": 2,
    "DATE_SLIP": 2,
    "MISSING_INVOICE": 1,
    "PAYOUT_SPLIT_MISMATCH": 1,
    "DUPLICATE_PAYOUT": 1,
}
# plus one invoice with no CRM deal at all:
GHOST_INVOICE_DEAL = "BD-2606-77"


def _weekday_june(rng):
    while True:
        d = rng.randrange(1, 29)
        # June 1 2026 is a Monday; weekends are day % 7 in {6, 0}
        if d % 7 not in (6, 0):
            return f"2026-06-{d:02d}"


def generate(seed=26, outdir="fixtures"):
    rng = random.Random(seed)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    deals = []
    for i in range(1, N_DEALS + 1):
        deals.append({
            "deal_id": f"BD-2606-{i:02d}",
            "brand": rng.choice(BRANDS),
            "creator_handle": rng.choice(CREATORS),
            "amount_usd": rng.randrange(18000, 96000, 250),
            "close_date": _weekday_june(rng),
            "stage": "Closed Won",
            "owner_rep": rng.choice(REPS),
            "creator_split_pct": rng.choice([65, 70, 75]),
        })

    victims = rng.sample(deals, sum(INJECTIONS.values()))
    injected, k = {}, 0
    for category, count in INJECTIONS.items():
        for _ in range(count):
            injected[victims[k]["deal_id"]] = category
            k += 1
    injected[GHOST_INVOICE_DEAL] = "MISSING_IN_CRM"

    invoices, payouts = [], []
    inv_n = 400
    pay_n = 900
    for d in deals:
        cat = injected.get(d["deal_id"])
        close_day = int(d["close_date"][-2:])

        # --- invoice ---
        if cat != "MISSING_INVOICE":
            inv_amount = d["amount_usd"]
            if cat == "AMOUNT_MISMATCH":
                # e.g. agency commission netted on the invoice side
                inv_amount = round(d["amount_usd"] * rng.choice([0.94, 0.97]))
            if cat == "DATE_SLIP":
                inv_date = f"2026-07-{rng.randrange(2, 10):02d}"
            else:
                inv_date = f"2026-06-{min(close_day + rng.randrange(2, 6), 30):02d}"
            inv_n += 1
            invoices.append({
                "invoice_id": f"INV-{inv_n}",
                "deal_id": d["deal_id"],
                "brand": d["brand"],
                "amount_usd": inv_amount,
                "invoice_date": inv_date,
                "status": rng.choice(["issued", "paid"]),
            })

        # --- payouts (creator share of the CRM amount) ---
        expected_cents = d["amount_usd"] * 100 * d["creator_split_pct"] // 100
        if cat == "PAYOUT_SPLIT_MISMATCH":
            expected_cents -= rng.randrange(200, 900) * 100  # short-paid
        parts = [expected_cents]
        if rng.random() < 0.5:
            first = expected_cents * 3 // 5
            parts = [first, expected_cents - first]
        rows = []
        for p in parts:
            pay_n += 1
            rows.append({
                "payout_id": f"PAY-{pay_n}",
                "deal_id": d["deal_id"],
                "creator_handle": d["creator_handle"],
                "amount_usd": f"{p // 100}" if p % 100 == 0 else f"{p / 100:.2f}",
                "paid_date": f"2026-07-{rng.randrange(1, 15):02d}",
            })
        if cat == "DUPLICATE_PAYOUT":
            rows.append(dict(rows[0]))  # same payout_id, entered twice
        payouts.extend(rows)

    # invoice that exists in invoicing but not in the CRM
    inv_n += 1
    invoices.append({
        "invoice_id": f"INV-{inv_n}",
        "deal_id": GHOST_INVOICE_DEAL,
        "brand": "Vantage Point Media",
        "amount_usd": 24500,
        "invoice_date": "2026-06-26",
        "status": "issued",
    })

    invoices.sort(key=lambda r: r["invoice_id"])
    payouts.sort(key=lambda r: r["payout_id"])

    files = {
        f"SYNTHETIC_crm_deals_{MONTH}.csv": (CRM_COLUMNS, deals),
        f"SYNTHETIC_invoices_{MONTH}.csv": (INV_COLUMNS, invoices),
        f"SYNTHETIC_payouts_{MONTH}.csv": (PAY_COLUMNS, payouts),
    }
    for name, (cols, rows) in files.items():
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    manifest = {
        "WARNING": "SYNTHETIC FIXTURE — generated data, NOT Northwind actuals. See fixtures/README.md.",
        "seed": seed,
        "month": MONTH,
        "n_crm_deals": len(deals),
        "n_invoices": len(invoices),
        "n_payout_rows": len(payouts),
        "injected_answer_key": injected,
        "note": "The reconciliation engine never reads this manifest; tests use it to score the engine.",
    }
    with open(out / "fixture_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return manifest
