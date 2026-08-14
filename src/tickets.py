"""Measured support workload from the raw ticket log.

Exists to settle one dispute with data: #ops claims "easily 40 hrs/week" of
creator support (slack_export.md:176); Elena asked whether that is "measured
or a vibe" (slack_export.md:179). This measures it.
"""
import csv
from collections import Counter
from datetime import date

from .paths import TICKETS

REQUIRED_COLUMNS = [
    "Ticket_ID", "Date", "Category", "Submitted_By",
    "Assigned_To", "Handle_Minutes", "Status",
]
QUARTER_DAYS = 90  # Q1 2026: Jan 1 – Mar 31


def ticket_stats(tickets_path=None, claimed_hours_per_week=40.0):
    path = tickets_path or TICKETS
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(
                f"{path}: unexpected ticket schema. Missing columns: {missing}. "
                f"Found: {reader.fieldnames}. Expected: {REQUIRED_COLUMNS}."
            )
        rows = list(reader)

    total_min = 0
    by_cat_n, by_cat_min = Counter(), Counter()
    blank_assignee, open_at_end, bad_minutes = [], [], []
    dates = []
    for idx, r in enumerate(rows):
        line_no = idx + 2
        try:
            m = int(r["Handle_Minutes"])
        except (TypeError, ValueError):
            bad_minutes.append(f"row {line_no} ({r.get('Ticket_ID')})")
            m = 0
        total_min += m
        by_cat_n[r["Category"]] += 1
        by_cat_min[r["Category"]] += m
        if not (r["Assigned_To"] or "").strip():
            blank_assignee.append(r["Ticket_ID"])
        if (r["Status"] or "").strip() != "Closed":
            open_at_end.append(r["Ticket_ID"])
        try:
            dates.append(date.fromisoformat(r["Date"]))
        except ValueError:
            pass

    hours = total_min / 60.0
    weeks = QUARTER_DAYS / 7.0
    hpw = hours / weeks
    # Like-for-like vs the #ops claim: Liam named thumbnails, tax forms and
    # payout questions (slack_export.md:176), not the whole queue.
    named = ("thumbnail", "tax form", "payout")
    named_min = sum(m for c, m in by_cat_min.items()
                    if any(k in c.lower() for k in named))
    named_hpw = named_min / 60.0 / weeks
    span_days = (max(dates) - min(dates)).days + 1 if dates else 0
    return {
        "path": str(path),
        "n_tickets": len(rows),
        "total_minutes": total_min,
        "total_hours": round(hours, 1),
        "hours_per_week": round(hpw, 2),
        "quarter_days": QUARTER_DAYS,
        "observed_span_days": span_days,
        "date_min": min(dates).isoformat() if dates else None,
        "date_max": max(dates).isoformat() if dates else None,
        "claimed_hours_per_week": claimed_hours_per_week,
        "measured_vs_claimed_pct": round(hpw / claimed_hours_per_week * 100, 1)
        if claimed_hours_per_week else None,
        "claim_multiple_all": round(claimed_hours_per_week / hpw, 1) if hpw else None,
        "named_categories_hours_per_week": round(named_hpw, 2),
        "claim_multiple_like_for_like": round(claimed_hours_per_week / named_hpw, 1)
        if named_hpw else None,
        "by_category": [
            {
                "category": c,
                "n": by_cat_n[c],
                "minutes": by_cat_min[c],
                "hours": round(by_cat_min[c] / 60.0, 1),
            }
            for c in sorted(by_cat_min, key=lambda c: -by_cat_min[c])
        ],
        "blank_assignee": blank_assignee,
        "open_at_quarter_end": open_at_end,
        "bad_minutes_rows": bad_minutes,
    }
