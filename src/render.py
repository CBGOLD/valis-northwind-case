"""Render answers for three audiences: terminal (evaluator), markdown +
HTML one-pager (CEO), audit appendix (CFO). No timestamps are embedded so
outputs are byte-deterministic run-to-run."""
import html as _html

from .evidence import load_store, verify_citation


def _citations_for(store, answer_part):
    cits = []
    for cid in answer_part.get("claims", []):
        for c in store["claims"][cid]["citations"]:
            cits.append(c)
    for eid in answer_part.get("events", []):
        ev = next(e for e in store["hiring_events"] if e["id"] == eid)
        cits.extend(ev["citations"])
    if answer_part.get("followups"):
        for fu in store.get("hiring_open_followups", []):
            cits.extend(fu["citations"])
    seen, out = set(), []
    for c in cits:
        key = (c["file"], c["line"], c["quote"])
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def _fmt_cit(c):
    return f"{c['file']}:{c['line']}  “{c['quote']}”"


def _badge_class(v):
    u = v.strip().upper()
    if u.startswith("HIGH"):
        return "hi"
    if u.startswith("LOW"):
        return "lo"
    return "med"


def terminal(answer, store=None, show_sources=True):
    store = store or load_store()
    lines = []
    lines.append("=" * 78)
    lines.append(f"Q: {answer['question']}" if "question" in answer else answer["headline"])
    lines.append("=" * 78)
    if "question" in answer:
        lines.append(f"\nANSWER: {answer['headline']}\n")
    for i, p in enumerate(answer.get("points", []), 1):
        lines.append(f"{i}. {p['text']}")
        if show_sources:
            for c in _citations_for(store, p):
                lines.append(f"     -> {_fmt_cit(c)}")
        lines.append("")
    for fn in answer.get("footnotes", []):
        lines.append(f"Note: {fn['text']}")
        if show_sources:
            for c in _citations_for(store, fn):
                lines.append(f"     -> {_fmt_cit(c)}")
        lines.append("")
    lines.append("CONFIDENCE:")
    for k, v in answer["confidence"].items():
        lines.append(f"  - {k.replace('_', ' ')}: {v}")
    lines.append("WHAT WOULD CHANGE THIS ANSWER:")
    for rv in answer.get("reversal", []):
        lines.append(f"  - {rv}")
    lines.append(f"As of {answer['as_of']} (bundle export date). Run `python3 ask.py check` to re-verify every citation.")
    return "\n".join(lines)


def _md_answer(answer, store):
    md = [f"## {answer['question']}", "", f"**{answer['headline']}**", ""]
    for i, p in enumerate(answer.get("points", []), 1):
        md.append(f"{i}. {p['text']}")
        cits = _citations_for(store, p)
        if cits:
            md.append("   " + " · ".join(f"`{c['file'].split('/')[-1]}:{c['line']}`" for c in cits))
    for fn in answer.get("footnotes", []):
        md.append(f"\n*{fn['text']}*")
        cits = _citations_for(store, fn)
        if cits:
            md.append("   " + " · ".join(f"`{c['file'].split('/')[-1]}:{c['line']}`" for c in cits))
    md.append("\n**Confidence:** " + " — ".join(f"{k.replace('_',' ')}: {v}" for k, v in answer["confidence"].items()))
    md.append("\n**What would change this answer:** " + " ".join(answer.get("reversal", [])))
    md.append("")
    return "\n".join(md)


def ceo_markdown(answers, store=None):
    store = store or load_store()
    md = [
        "# Northwind — straight answers, with receipts",
        "",
        f"*Everything below traces to an exact file and line in the bundle; knowledge stops at "
        f"{answers[0]['as_of']} (the Slack export date). Full quote-level audit: `AUDIT.md`. "
        f"Re-verify any time: `python3 ask.py check`.*",
        "",
    ]
    for a in answers:
        md.append(_md_answer(a, store))
        md.append("---")
    return "\n".join(md[:-1]) + "\n"


_CSS = """
:root{--ink:#16211c;--sub:#5b6b63;--card:#ffffff;--bg:#f2f4f1;--acc:#0e5e46;--warn:#8a4b08;--bad:#8a1e1e;--line:#dde3dd}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;padding:24px}
main{max-width:840px;margin:0 auto}h1{font-size:26px;margin:0 0 4px}
.sub{color:var(--sub);font-size:14px;margin-bottom:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:14px 0}
.q{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--sub);margin:0 0 6px}
.headline{font-size:19px;font-weight:650;margin:0 0 12px}
ol{margin:0 0 8px;padding-left:20px}li{margin:0 0 10px}
.cite{display:block;color:var(--sub);font-size:12.5px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;margin-top:3px}
.badge{display:inline-block;font-size:12px;font-weight:600;border-radius:999px;padding:2px 10px;margin:2px 6px 2px 0}
.hi{background:#e2f0e9;color:var(--acc)}.med{background:#f7ead8;color:var(--warn)}.lo{background:#f6e0e0;color:var(--bad)}
.meta{font-size:13.5px;color:var(--sub);margin-top:10px}
.fnote{font-size:13.5px;color:var(--sub);font-style:italic}
@media(max-width:520px){body{padding:12px}.card{padding:16px}}
"""


def ceo_html(answers, store=None):
    store = store or load_store()
    e = _html.escape
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>Northwind — answers with receipts</title>",
        f"<style>{_CSS}</style></head><body><main>",
        "<h1>Northwind — straight answers, with receipts</h1>",
        f"<p class='sub'>Every claim cites an exact file:line in the bundle · knowledge as of "
        f"{e(answers[0]['as_of'])} (Slack export date) · audit trail in AUDIT.md · "
        f"re-verify with <code>python3 ask.py check</code></p>",
    ]
    for a in answers:
        parts.append("<section class='card'>")
        parts.append(f"<p class='q'>{e(a['question'])}</p>")
        parts.append(f"<p class='headline'>{e(a['headline'])}</p><ol>")
        for p in a.get("points", []):
            parts.append(f"<li>{e(p['text'])}")
            for c in _citations_for(store, p):
                parts.append(f"<span class='cite'>{e(c['file'].split('/')[-1])}:{c['line']} — “{e(c['quote'])}”</span>")
            parts.append("</li>")
        parts.append("</ol>")
        for fn in a.get("footnotes", []):
            parts.append(f"<p class='fnote'>{e(fn['text'])}</p>")
        badges = "".join(
            f"<span class='badge {_badge_class(v)}'>"
            f"{e(k.replace('_', ' '))}: {e(v.split('—')[0].strip())}</span>"
            for k, v in a["confidence"].items()
        )
        parts.append(f"<div>{badges}</div>")
        parts.append("<p class='meta'>Would change this answer: " + " ".join(e(r) for r in a.get("reversal", [])) + "</p>")
        parts.append("</section>")
    parts.append("</main></body></html>")
    return "".join(parts)


def audit_markdown(store=None, root=None):
    """CFO appendix: every claim, every quote, live verification status."""
    store = store or load_store()
    md = [
        "# Audit appendix — every claim, every quote, verified",
        "",
        "Each citation below was re-verified at build time: the cited file was opened and the",
        "quote checked as a substring of the exact cited line. Regenerate anytime with",
        "`python3 ask.py build`; verify without building via `python3 ask.py check`.",
        "",
    ]
    sections = [("Claims", list(store["claims"].items()))]
    ev_items = [(f"hiring event — {ev['id']}", ev) for ev in store.get("hiring_events", [])]
    fu_items = [(f"open follow-up — {fu['id']}", fu) for fu in store.get("hiring_open_followups", [])]
    sections.append(("Hiring timeline events", ev_items))
    sections.append(("Open follow-ups", fu_items))
    if "as_of_source" in store:
        sections.append(("Knowledge horizon", [("as_of", {
            "statement": f"All answers are stated as of {store.get('as_of')} — the bundle's own export date.",
            "citations": [store["as_of_source"]],
        })]))
    n_ok = n_fail = 0
    for title, items in sections:
        md.append(f"## {title}\n")
        for cid, claim in items:
            label = claim.get("statement") or claim.get("summary") or ""
            md.append(f"### `{cid}`")
            if claim.get("confidence"):
                md.append(f"*confidence: {claim['confidence']}*\n")
            md.append(f"{label}\n")
            if claim.get("risk"):
                md.append(f"*Risk if ignored: {claim['risk']}*\n")
            for c in claim["citations"]:
                ok, _ = verify_citation(c, root=root)
                n_ok += ok
                n_fail += not ok
                status = "VERIFIED" if ok else "**FAILED**"
                md.append(f"- {status} · `{c['file']}:{c['line']}` — “{c['quote']}”")
            md.append("")
    md.insert(4, f"**Result: {n_ok} citations verified, {n_fail} failed.**\n")
    return "\n".join(md)
