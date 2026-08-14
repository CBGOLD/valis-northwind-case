"""SaaS spend computation from the raw P&L CSV.

Nothing here is hardcoded to Northwind's numbers: booked total, subtotal
tie-out and duplicate detection are computed from whatever compatible CSV is
passed in, so the same code runs on a fresh file during a live walkthrough.
"""
import csv
import re
from .paths import PNL

REQUIRED_COLUMNS = ["Category", "Line Item", "Q1_2026_USD", "Notes"]
SAAS_CATEGORY = "Software & SaaS"

_MONEY_RE = re.compile(r"^-?\d+(\.\d{1,2})?$")


def parse_money_cents(raw):
    """Parse a USD amount into integer cents.

    Returns (cents, flag). flag is None when clean, otherwise a short reason
    ('blank', 'non-usd-or-unparseable') and cents is None. We never guess FX.
    """
    s = (raw or "").strip().replace(",", "").replace("$", "")
    if not s:
        return None, "blank"
    if not _MONEY_RE.match(s):
        return None, "non-usd-or-unparseable"
    if "." in s:
        whole, frac = s.split(".")
        return int(whole) * 100 + int(frac.ljust(2, "0")), None
    return int(s) * 100, None


def _tokens(name):
    return [t for t in re.split(r"[^a-z0-9]+", name.lower()) if t]


def _norm(text):
    return " ".join(_tokens(text))


def find_duplicate_pairs(items):
    """Suspected double-entries: same amount, same normalized notes, and one
    vendor name's tokens are a subset of the other's (e.g. 'Amplitude' vs
    'Amplitude Analytics'). Generic — no vendor names are hardcoded."""
    pairs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            if a["amount_cents"] is None or a["amount_cents"] != b["amount_cents"]:
                continue
            if _norm(a["notes"]) != _norm(b["notes"]):
                continue
            ta, tb = set(_tokens(a["vendor"])), set(_tokens(b["vendor"]))
            if ta and tb and (ta <= tb or tb <= ta):
                keep, drop = (a, b) if len(ta) >= len(tb) else (b, a)
                pairs.append({
                    "keep": keep, "drop": drop,
                    "reason": (
                        "same amount, same notes, vendor-name containment "
                        f"({a['vendor']!r} vs {b['vendor']!r})"
                    ),
                })
    return pairs


def saas_breakdown(pnl_path=None):
    """Compute booked / adjusted SaaS numbers with row-level provenance."""
    path = pnl_path or PNL
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                f"{path}: unexpected P&L schema. Missing columns: {missing}. "
                f"Found: {reader.fieldnames}. Expected: {REQUIRED_COLUMNS}."
            )
        rows = list(reader)

    items, flags = [], []
    stated_subtotal = None
    subtotal_line = None
    for idx, r in enumerate(rows):
        line_no = idx + 2  # header is line 1
        if (r["Category"] or "").strip() != SAAS_CATEGORY:
            continue
        name = (r["Line Item"] or "").strip()
        cents, flag = parse_money_cents(r["Q1_2026_USD"])
        if "subtotal" in name.lower():
            stated_subtotal = cents
            subtotal_line = line_no
            continue
        item = {
            "line": line_no,
            "vendor": name,
            "amount_cents": cents,
            "notes": (r["Notes"] or "").strip(),
        }
        if flag:
            flags.append(f"row {line_no} ({name}): amount {flag}")
        items.append(item)

    booked = sum(i["amount_cents"] or 0 for i in items)
    # The trap a naive groupby('Category').sum() falls into: the subtotal row
    # shares the category, so the naive answer is ~2x the real one.
    naive = booked + (stated_subtotal or 0)
    pairs = find_duplicate_pairs(items)
    dup_total = sum(p["drop"]["amount_cents"] for p in pairs)
    return {
        "path": str(path),
        "items": items,
        "n_items": len(items),
        "booked_cents": booked,
        "naive_category_sum_cents": naive,
        "stated_subtotal_cents": stated_subtotal,
        "subtotal_line": subtotal_line,
        "ties_out": stated_subtotal is not None and stated_subtotal == booked,
        "duplicate_pairs": pairs,
        "suspected_duplicate_cents": dup_total,
        "adjusted_cents": booked - dup_total,
        "flags": flags,
    }


def usd(cents):
    """Format integer cents as $12,345 (or $12,345.67 when non-whole)."""
    if cents is None:
        return "n/a"
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    whole, frac = divmod(cents, 100)
    return f"{sign}${whole:,}" + (f".{frac:02d}" if frac else "")
