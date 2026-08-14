"""Evidence store: claims mapped to exact file/line citations, plus a
verifier that re-opens every cited file and checks the quoted text is
actually on the cited line.

The store records *where evidence lives*; all headline numbers are
recomputed from the raw CSVs at runtime (see finance.py / tickets.py) so a
fresh compatible file changes the answer, not just the citation.
"""
import json
from pathlib import Path

from .paths import ROOT, EVIDENCE


def load_store(path=None):
    p = Path(path) if path else EVIDENCE
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def verify_citation(cit, root=None):
    """Check one citation: file exists, line exists, quote is a substring
    of that exact line. Returns (ok: bool, detail: str)."""
    root = Path(root) if root else ROOT
    fp = root / cit["file"]
    if not fp.exists():
        return False, f"missing file: {cit['file']}"
    try:
        lines = fp.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return False, f"undecodable file: {cit['file']}"
    n = cit["line"]
    if not (1 <= n <= len(lines)):
        return False, f"{cit['file']}: line {n} out of range (file has {len(lines)})"
    if cit["quote"] not in lines[n - 1]:
        return False, (
            f"{cit['file']}:{n} quote not found. expected substring "
            f"{cit['quote']!r}, line reads {lines[n - 1][:160]!r}"
        )
    return True, f"{cit['file']}:{n} OK"


def verify_claim(claim, root=None):
    """Verify every citation behind one claim. Returns list of (ok, detail)."""
    return [verify_citation(c, root=root) for c in claim["citations"]]


def verify_all(store=None, root=None):
    """Verify the whole store. Returns (n_ok, n_fail, report_lines)."""
    store = store or load_store()
    ok = fail = 0
    report = []
    items = list(store["claims"].items())
    for ev in store.get("hiring_events", []):
        items.append((f"event:{ev['id']}", ev))
    for fu in store.get("hiring_open_followups", []):
        items.append((f"followup:{fu['id']}", fu))
    if "as_of_source" in store:
        items.append(("as_of", {"citations": [store["as_of_source"]]}))
    for cid, claim in items:
        for good, detail in verify_claim(claim, root=root):
            if good:
                ok += 1
                report.append(f"PASS  {cid}: {detail}")
            else:
                fail += 1
                report.append(f"FAIL  {cid}: {detail}")
    return ok, fail, report


def claim(store, cid):
    """Fetch a claim by id (raises KeyError loudly if a claim id dangles)."""
    return store["claims"][cid]
