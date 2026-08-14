"""Assemble the CEO answers: answer-first, max three load-bearing points,
explicit confidence and reversal conditions. Numbers are computed live from
the raw CSVs; citations come from the verified evidence store.

Fresh-input rule: bundle testimony, vendor contract context, and bundle
citations describe the default bundle only. Any non-default --pnl file gets
computed content exclusively, behind a loud banner (see _q1_fresh)."""
from pathlib import Path

from .evidence import load_store
from .finance import SAAS_CATEGORY, saas_breakdown, usd
from .hiring import resolve
from .paths import BUNDLE_AS_OF, PNL
from .tickets import ticket_stats

# Reported (not measured) baseline for the recon: ~3 days/month, cited in
# recon.pain_corroborated. The hour conversion is arithmetic on that report.
RECON_DAYS_PER_MONTH = 3
HOURS_PER_DAY = 8


def _as_of(store):
    return store.get("as_of", BUNDLE_AS_OF)


def _is_default_pnl(pnl_path):
    """True when the P&L in play is the bundle's own file (or unspecified)."""
    if pnl_path is None:
        return True
    try:
        return Path(pnl_path).resolve() == PNL.resolve()
    except OSError:
        return False


def _fresh_banner(path):
    return [
        f"FRESH-INPUT MODE — computed from: {path}",
        "Every number below is recomputed from this file alone; detection logic "
        "is generic (no vendor names hardcoded).",
        "Bundle-derived testimony, vendor contract context, and bundle citations "
        "are suppressed: they describe the Northwind bundle, not this file. "
        "No human corroboration exists for these rows.",
    ]


def _q1_fresh(s):
    """q1 on a non-default P&L: computed content only. No bundle testimony,
    no bundle citations, no bundle contract context — those describe
    input/Northwind-in-a-box_charles/pnl_q1_2026.csv, not this file. A
    vendor present in both (e.g. Salesforce) is reported as its computed
    row only."""
    booked, adjusted = s["booked_cents"], s["adjusted_cents"]
    dup = s["suspected_duplicate_cents"]
    has_dup = dup > 0
    headline = (
        f"Best estimate {usd(adjusted)} for this file's '{SAAS_CATEGORY}' spend — booked "
        f"{usd(booked)}, including {usd(dup)} of suspected duplicate entry flagged by "
        f"generic same-amount/same-notes/vendor-containment detection."
        if has_dup else
        f"{usd(booked)} booked to '{SAAS_CATEGORY}' in this file ({s['n_items']} line items; "
        f"no duplicate suspects detected)."
    )
    if s["ties_out"]:
        tie = ", which ties exactly to the file's stated subtotal"
    elif s["stated_subtotal_cents"] is not None:
        tie = " — WARNING: the file's stated subtotal does NOT tie to the row sum"
    else:
        tie = "; the file carries no subtotal row to tie against"
    points = [
        {
            "text": (
                f"Booked: {usd(booked)} across {s['n_items']} line items{tie}. "
                f"(A naive category sum that keeps the subtotal row would return "
                f"{usd(s['naive_category_sum_cents'])}; this code excludes it.)"
            ),
            "claims": [],
        },
        {
            "text": (
                "Suspected duplicate(s): "
                + "; ".join(
                    f"'{p['drop']['vendor']}' (row {p['drop']['line']}) vs "
                    f"'{p['keep']['vendor']}' (row {p['keep']['line']}) at "
                    f"{usd(p['drop']['amount_cents'])} each — {p['reason']}"
                    for p in s["duplicate_pairs"]
                )
                + ". Heuristic only: verify against invoices before restating anything."
            ),
            "claims": [],
        } if has_dup else {
            "text": "No same-amount/same-notes vendor-containment duplicates detected in this P&L.",
            "claims": [],
        },
    ]
    sf_rows = [i for i in s["items"] if "salesforce" in i["vendor"].lower()]
    if sf_rows:
        points.append({
            "text": (
                "Salesforce appears in this file: "
                + "; ".join(f"'{i['vendor']}' {usd(i['amount_cents'])} (row {i['line']})"
                            for i in sf_rows)
                + ". Computed row(s) only — bundle contract context does not apply "
                  "to this file and is suppressed."
            ),
            "claims": [],
        })
    reversal = (
        [
            f"If invoices show the flagged pair(s) are distinct products or contracts, "
            f"the answer reverts to {usd(booked)}.",
            f"If any flagged pair is confirmed a double-posting, the defensible figure "
            f"is {usd(adjusted)}.",
        ]
        if has_dup else
        [f"If an invoice audit surfaces a duplicate this heuristic missed, "
         f"{usd(booked)} adjusts down accordingly."]
    )
    return {
        "id": "q1",
        "question": "What did we actually spend on SaaS tools last quarter?",
        "fresh_input": {"path": s["path"], "banner": _fresh_banner(s["path"])},
        "headline": headline,
        "points": points,
        "footnotes": [
            {
                "text": (
                    f"Scope: rows whose Category is '{SAAS_CATEGORY}' in the provided file; "
                    "other categories are not analyzed. "
                    + (f"Rows flagged unparseable: {'; '.join(s['flags'])}."
                       if s["flags"] else "No unparseable amounts.")
                ),
                "claims": [],
            },
        ],
        "confidence": {
            "booked": (
                "Recomputed from the provided file"
                + (", ties to its stated subtotal." if s["ties_out"]
                   else "; no clean subtotal tie — treat with caution.")
            ),
            "best_estimate": (
                (
                    f"Heuristic-only duplicate detection; no testimony or invoices exist "
                    f"for this file. Bounded: {usd(adjusted)} (duplicates confirmed) to "
                    f"{usd(booked)} (duplicates refuted)."
                ) if has_dup else "Equal to booked — no duplicate suspects to adjust for."
            ),
        },
        "reversal": reversal,
        "as_of": None,
        "computed": {
            "booked_cents": booked,
            "adjusted_cents": adjusted,
            "naive_category_sum_cents": s["naive_category_sum_cents"],
            "suspected_duplicate_cents": dup,
            "n_items": s["n_items"],
            "ties_out": s["ties_out"],
            "flags": s["flags"],
            "pnl_path": s["path"],
        },
    }


def q1(pnl_path=None, store=None):
    store = store or load_store()
    s = saas_breakdown(pnl_path)
    if not _is_default_pnl(pnl_path):
        return _q1_fresh(s)
    booked, adjusted = s["booked_cents"], s["adjusted_cents"]
    dup = s["suspected_duplicate_cents"]
    has_dup = dup > 0
    headline = (
        f"Best estimate {usd(adjusted)} for Q1 2026 SaaS — the books say {usd(booked)}, "
        f"which includes a suspected {usd(dup)} duplicate your own finance team has "
        f"flagged but not yet confirmed."
        if has_dup else
        f"{usd(booked)} for Q1 2026 SaaS as booked ({s['n_items']} line items; no duplicate "
        f"suspects detected in this file)."
    )
    points = [
        {
            "text": (
                f"Booked: {usd(booked)}. The {s['n_items']} SaaS line items sum exactly to the "
                f"stated subtotal{' (arithmetic ties out)' if s['ties_out'] else ' — WARNING: subtotal does NOT tie'}; "
                f"the CFO confirmed this as the finalized Q1 figure. (A naive category sum that "
                f"forgets the subtotal row returns {usd(s['naive_category_sum_cents'])} — the code "
                f"here excludes it, and a test proves it.)"
            ),
            "claims": ["saas.booked_subtotal"],
        },
        {
            "text": (
                f"Adjusted: {usd(adjusted)}. Two adjacent lines — "
                + " and ".join(
                    f"'{p['drop']['vendor']}' / '{p['keep']['vendor']}' at {usd(p['drop']['amount_cents'])} each"
                    for p in s["duplicate_pairs"]
                )
                + " — look double-entered. The analyst closest to it is 90% sure; the CFO agrees it "
                  "'smells like a double-count'. Unverified: the invoice never came back, so the books "
                  "deliberately still carry both."
            ),
            "claims": ["saas.amplitude_duplicate_suspected"],
        } if has_dup else {
            "text": "No same-amount/same-notes vendor-containment duplicates detected in this P&L.",
            "claims": [],
        },
        {
            "text": (
                "Not restated: Salesforce, booked $12,000 for Q1. The $60k/yr renewal was signed "
                "2026-05-14 — that's Q2, covering 'through next May' — so Q1 stands, with a "
                "+$3,000/quarter step-up from Q2 onward. Two open flags: finance's own "
                "check-posted-vs-contract action has sat unclosed since 2026-05-28, and the finance "
                "note's direction is backwards ('looks higher': $12k/qtr annualizes to $48k, BELOW "
                "$60k). Treat the line as booked-but-unverified."
            ),
            "claims": ["saas.salesforce_timing", "saas.salesforce_check_still_open"],
        },
    ]
    return {
        "id": "q1",
        "question": "What did we actually spend on SaaS tools last quarter?",
        "headline": headline,
        "points": points,
        "footnotes": [
            {
                "text": (
                    "Scope: the 'Software & SaaS' category only, per your CFO's classification. "
                    "Infrastructure is excluded — AWS $38,000, and Cloudflare €1,900 which is "
                    "billed in EUR with no FX rate anywhere in the bundle (left unconverted rather "
                    "than inventing a rate). Fold infra in and you're asking a different question."
                ),
                "claims": ["saas.aws_out_of_scope", "saas.cloudflare_fx_unconvertible"],
            },
            {
                "text": (
                    "Completeness: this is what's booked to the SaaS line, not an inventory of "
                    "software in use — the bundle shows a CMS and a ticketing system running daily "
                    "with no SaaS line item, and no HRIS/payroll or accounting line for ~300 FTE. "
                    "Flagged rather than estimated."
                ),
                "claims": ["saas.completeness_gap"],
            },
        ],
        "confidence": {
            "booked": "HIGH — recomputed from the P&L rows; sum ties to the stated subtotal.",
            "best_estimate": (
                "MODERATE-HIGH — the duplicate is 90%-suspected by the person closest to it and "
                "endorsed by the CFO, but the invoice is outstanding. Bounded: "
                f"{usd(adjusted)} (duplicate confirmed) to {usd(booked)} (duplicate refuted)."
            ),
        },
        "reversal": [
            "If the Amplitude invoice shows two distinct contracts, the answer reverts to $81,000.",
            "If the Salesforce contract check finds a mis-posting, the Q1 line adjusts by the difference.",
        ],
        "as_of": _as_of(store),
        "computed": {
            "booked_cents": booked,
            "adjusted_cents": adjusted,
            "naive_category_sum_cents": s["naive_category_sum_cents"],
            "suspected_duplicate_cents": dup,
            "n_items": s["n_items"],
            "ties_out": s["ties_out"],
            "flags": s["flags"],
            "pnl_path": s["path"],
        },
    }


def q2(store=None):
    store = store or load_store()
    r = resolve(store)
    ev = r["decision_event"]
    headline = (
        f"{r['state']}. Dana froze all net-new Sales hiring — announced {r['decided_on']} in "
        f"#leadership, minuted {r['formalized_on']}. REQ-114 is paused, not killed. "
        f"Dana owns the decision; Priya enforces it."
    )
    points = [
        {
            "text": (
                "Decision & scope: all net-new Sales headcount frozen until pipeline recovers, "
                "REQ-114 (the AE role) explicitly included and on hold; Tomás's objection is on "
                "record. Sales-only — other teams' reqs are unaffected; backfills for regretted "
                "attrition go case-by-case through Priya + Tomás."
            ),
            "claims": [],
            "events": ["h3_ceo_freeze_announcement", "h5_people_cascade"],
        },
        {
            "text": (
                "Ownership: decision — Dana Whitfield (CEO), on record ('I'm making the call'); "
                "enforcement — Priya Raman (CFO): no Sales req moves without her sign-off. The "
                "2026-05-01 roster still says REQ-114 APPROVED — that snapshot is explicitly "
                "superseded (the sync minutes say so; People declared the roster stale)."
            ),
            "claims": ["hiring.chronology_note"],
            "events": ["h4_leadership_sync_minuted", "h2_roster_snapshot"],
        },
        {
            # Citations here are the revisit-condition evidence only; the open
            # follow-ups cite themselves in the footnote below.
            "text": (
                f"Revisit condition: {ev['revisit']}. Still true at the last message in the bundle "
                f"({r['as_of']}); loose ends below."
            ),
            "claims": [],
            "events": ["h6_freeze_still_in_force"],
        },
    ]
    return {
        "id": "q2",
        "question": "Did we decide to hire in Sales or freeze hiring — current state and owner?",
        "headline": headline,
        "points": points,
        "footnotes": [
            {
                "text": (
                    "Open follow-through (decided in humans, unconfirmed in systems): "
                    + " ".join(f"({i}) {fu['summary']}" for i, fu in
                               enumerate(store.get("hiring_open_followups", []), 1))
                ),
                "claims": [],
                "followups": True,
            },
        ],
        "confidence": {
            "answer": (
                "HIGH — four concordant sources (#leadership Slack, sync minutes, #people Slack ×2), "
                "an explicit supersession statement, zero contradicting messages after 2026-06-10. "
                "MODERATE on the date-of-record only (announced Jun 10, minuted Jun 11)."
            ),
            "operational_state": (
                "LOW — no evidence the freeze reached the systems of record (roster still APPROVED; "
                "Greenhouse pause unconfirmed; late-stage candidate handling unresolved, due date passed)."
            ),
        },
        "reversal": [
            "Freeze lifts when pipeline coverage is back to target plus two consecutive months of "
            "recovered conversion — re-evaluated at the July leadership sync (after this bundle's horizon).",
            "Any Priya-approved exception (e.g. a regretted-attrition backfill) modifies the state for that req.",
        ],
        "as_of": r["as_of"],
        "resolution": r,
    }


def workflow(tickets_path=None, store=None):
    store = store or load_store()
    t = ticket_stats(tickets_path)
    recon_hours_q = RECON_DAYS_PER_MONTH * HOURS_PER_DAY * 3
    thumb = next((c for c in t["by_category"] if "thumbnail" in c["category"].lower()), None)
    tax = next((c for c in t["by_category"] if "tax" in c["category"].lower()), None)
    headline = (
        "Automate the monthly brand-deal three-way reconciliation first. Reported cost: ~3 "
        f"analyst-days per month (~{recon_hours_q} h/quarter) — more than the entire measured "
        f"support queue ({t['total_hours']} h/quarter). And it sits under $4.2M of brand revenue: "
        "the payoff is trustworthy first-pass numbers, not just hours."
    )
    points = [
        {
            "text": (
                "Brand-deal reconciliation (CRM export vs invoicing sheet vs payout tracker): ~3 days "
                "every month-end, corroborated across two people, three file types and three months; "
                "the CFO calls it the single biggest finance time-sink, the analyst votes it #1. "
                "Honest label: that baseline is self-reported, never system-measured — but it is the "
                "most corroborated number in the bundle, and 80% of revenue flows through the process "
                "it protects."
            ),
            "claims": ["recon.three_sources_named", "recon.pain_corroborated",
                       "recon.self_reported_not_logged", "recon.revenue_at_stake"],
        },
        {
            "text": (
                f"Support is measured, and the measurement kills the vibe: {t['n_tickets']} tickets in "
                f"Q1 = {t['total_minutes']} handle-minutes = {t['total_hours']} h/quarter ≈ "
                f"{t['hours_per_week']} h/week over the 90-day quarter — the 40 h/week claim is "
                f"{t['claim_multiple_all']}× the whole measured queue, and "
                f"{t['claim_multiple_like_for_like']}× like-for-like on the three categories named. "
                f"Do not hire or build against it. "
                + (
                    f"(Liam IS right on ticket share: thumbnails are {thumb['n']}/{t['n_tickets']} of "
                    f"tickets by count — but only {thumb['hours']} h/quarter of time. His '#47 this "
                    f"week' can't be checked: no Q2 ticket data exists.)" if thumb else ""
                )
            ),
            "claims": ["tickets.claim_40h_falsified", "tickets.liam_right_on_volume",
                       "tickets.q2_rate_unverifiable"],
        },
        {
            "text": (
                (f"Tax forms (W-9/W-8) are the biggest support category by time ({tax['hours']} "
                 f"h/quarter) — " if tax else "Tax forms: ")
                + "and already have a buy-not-build answer: cheap e-sign/tax-form services, parked "
                  "for Q3 planning by People. Buy it; don't build it. Automating thumbnails is real "
                  "but third in line."
            ),
            "claims": ["tickets.taxform_buy_not_build"],
        },
    ]
    return {
        "id": "workflow",
        "question": "Where are we wasting the most time, and what would you automate first?",
        "headline": headline,
        "points": points,
        "footnotes": [],
        "confidence": {
            "support_measurement": "HIGH — computed row-by-row from the company's own ticket log.",
            "recon_baseline": (
                "MODERATE — self-reported (~3 days/month), never system-measured, but corroborated "
                "by seven statements across Slack, the finance review, and the leadership sync; no "
                "contradicting evidence exists."
            ),
        },
        "reversal": [
            "If the real CRM/invoicing/payout exports show trivial monthly drift, the recon build "
            "downgrades and thumbnail self-serve moves up.",
            "If ticket logging is shown to materially under-capture support work (untracked DMs, "
            "walk-ups), the support right-sizing weakens — that completeness is explicitly unverified.",
        ],
        "as_of": _as_of(store),
        "computed": {"tickets": t, "recon_hours_per_quarter_reported": recon_hours_q},
    }


def _value_fresh(s):
    """value on a non-default P&L: arithmetic only, bundle claims suppressed."""
    dup = s["suspected_duplicate_cents"]
    has_dup = dup > 0
    share = f"{dup / s['booked_cents'] * 100:.1f}%" if has_dup and s["booked_cents"] else None
    return {
        "id": "value",
        "fresh_input": {"path": s["path"], "banner": _fresh_banner(s["path"])},
        "headline": (
            f"{usd(dup)} of this file's booked {usd(s['booked_cents'])} ({share}) is flagged as "
            f"a suspected duplicate by generic detection — verify against invoices before "
            f"treating it as either an overstatement or consolidatable spend."
            if has_dup else
            f"No duplicate suspects detected in this file (booked {usd(s['booked_cents'])}); "
            f"no value number is claimed."
        ),
        "framing": (
            "Heuristic finding on a fresh file: no testimony, invoices, or bundle context "
            "exist for these rows, so no probability or recurrence claim is made."
        ),
        "baseline": f"Booked subtotal {usd(s['booked_cents'])} (recomputed from {s['path']}).",
        "arithmetic": [
            f"Booked {usd(s['booked_cents'])} − suspected duplicate {usd(dup)} "
            f"= {usd(s['adjusted_cents'])}."
        ] + ([f"Share of booked: {share}."] if share else []),
        "claims": [],
        "unverified": [
            "Everything beyond the arithmetic: this file carries no invoices, no testimony, "
            "and no bundle context. The duplicate flag is a same-amount/same-notes/"
            "vendor-containment heuristic, not a confirmed finding.",
        ],
        "confidence": "Arithmetic only. No corroboration exists for this file.",
        "as_of": None,
    }


def value(pnl_path=None, store=None):
    """The one CFO-grade number, as structured data (worksheet in docs/)."""
    store = store or load_store()
    s = saas_breakdown(pnl_path)
    if not _is_default_pnl(pnl_path):
        return _value_fresh(s)
    dup = s["suspected_duplicate_cents"]
    return {
        "id": "value",
        "headline": (
            f"The Q1 SaaS line is {dup / s['booked_cents'] * 100:.1f}% wrong in one of two ways — "
            f"90%-suspected: a {usd(dup)} double-posting to restate (an accounting fix; cash "
            f"recovery $0), or 10%-possible: {usd(dup * 4)}/yr of duplicate tooling to "
            f"consolidate. One invoice pull, already owed to the CFO since 2026-06-02, decides which."
        ),
        "framing": (
            "Framed as exposure with a named resolution test, NOT as a booked saving. If the "
            "duplicate is clerical (one invoice posted twice), cash recovery is $0 and the finding "
            "is a 9.3% overstatement of a published number; if it's two real contracts, it's "
            f"{usd(dup * 4)}/yr of duplicate tooling to consolidate. Either way the books are wrong "
            "or the spend is redundant — and nobody at Northwind currently knows which."
        ),
        "baseline": f"Booked Q1 2026 SaaS subtotal {usd(s['booked_cents'])} (recomputed from rows; ties to stated subtotal).",
        "arithmetic": [
            f"Booked {usd(s['booked_cents'])} − suspected duplicate {usd(dup)} = {usd(s['adjusted_cents'])} defensible Q1 SaaS.",
            f"Share of subtotal: {dup / s['booked_cents'] * 100:.1f}%.",
            f"Annualized IF the entry recurs quarterly: {usd(dup)} × 4 = {usd(dup * 4)} (labeled run-rate, not verified).",
            "Forward context (separate item, not in this number): Salesforce steps up +$3,000/qtr from Q2 under the $60k/yr renewal.",
        ],
        "claims": ["saas.amplitude_duplicate_suspected", "saas.booked_subtotal", "saas.salesforce_timing"],
        "unverified": [
            "The Amplitude invoice itself — not in the bundle; finance requested it 2026-06-02 and it never came back.",
            "Recurrence beyond Q1 — the bundle has one quarter of P&L; the $30,000/yr figure assumes the entry repeats.",
            "Cash character — clerical double-post (cash impact $0, books wrong) vs two real contracts "
            "(real duplicate spend). Identical amounts and identical notes lean clerical; only the invoice decides.",
            "Whether 'Amplitude' and 'Amplitude Analytics' could be two genuinely distinct products — "
            "possible (~10% by the analyst's own estimate); identical pricing makes it unlikely.",
        ],
        "confidence": (
            "MODERATE-HIGH that the published number is wrong by 9.3% in one of two ways; "
            "LOW on cash recovery (deliberately not claimed). If the invoice refutes the duplicate, "
            "this number voids — by design."
        ),
        "as_of": _as_of(store),
    }
