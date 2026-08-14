"""Sales-hiring state: resolve a decision timeline with supersession.

The events themselves live in evidence/citations.json (each with exact
file/line citations that `ask.py check` re-verifies). This module applies
the resolution rules and returns the current state:

  1. Chronology first — later information supersedes earlier information.
  2. Authority second — an explicit CEO decision outranks a system snapshot;
     a snapshot (roster) is state-as-of-its-date, never a rebuttal of a
     later decision.
  3. Anything after the bundle's export date is unknowable; the answer must
     carry an as-of date.
"""
from .evidence import load_store
from .paths import BUNDLE_AS_OF

# Higher wins when events tie on date.
AUTHORITY = {"ceo_decision": 4, "meeting_decision": 3, "operational": 2, "record": 1, "advocacy": 0}


def resolve(store=None):
    store = store or load_store()
    events = sorted(
        store["hiring_events"],
        key=lambda e: (e["date"], AUTHORITY.get(e["kind"], 0)),
    )
    decisions = [e for e in events if e["kind"] in ("ceo_decision", "meeting_decision")]
    if not decisions:
        return {"state": "UNKNOWN", "reason": "no decision events in evidence store"}
    current = decisions[-1]
    # A decision may be announced (CEO, Slack) then formalized (sync minutes):
    # first event with the current position is the decision date.
    same_position = [d for d in decisions if d["position"] == current["position"]]
    first = same_position[0]
    superseded = [
        e for e in events
        if e["date"] < current["date"] and e["kind"] in ("record", "advocacy")
    ]
    confirmations = [
        e for e in events
        if e["date"] >= current["date"] and e["id"] != current["id"]
    ]
    contradictions = [
        e for e in confirmations
        if e.get("position") and e["position"] != current["position"]
    ]
    return {
        "state": current["position"],          # e.g. "FROZEN"
        "decided_on": first["date"],
        "formalized_on": current["date"] if current["date"] != first["date"] else None,
        "decision_owner": current["owner"],
        "enforcement_owner": current["enforcement"],
        "scope": current["scope"],
        "revisit": current["revisit"],
        "decision_event": current,
        "superseded": superseded,
        "confirmations": confirmations,
        "contradictions": contradictions,
        "open_followups": store.get("hiring_open_followups", []),
        "as_of": BUNDLE_AS_OF,
    }
