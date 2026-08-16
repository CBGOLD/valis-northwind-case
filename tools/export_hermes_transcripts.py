#!/usr/bin/env python3
"""Deterministically export the three supplied Hermes delegation logs.

The source map is deliberately expressed relative to the active home directory.
Exports omit internal reasoning and sanitize machine/identity/credential context.
"""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = pathlib.Path.home() / ".hermes" / "cache" / "delegation" / "live"
DEST = ROOT / "llm_logs" / "transcripts"
MANIFEST = ROOT / "llm_logs" / "hermes_manifest.json"
MAX_FIELD = 3000

DELEGATIONS = (
    {
        "delegation_id": "deleg_d02432f8",
        "source": "deleg_d02432f8/task-0.log",
        "transcript": "llm_logs/transcripts/06-hermes-microsite-implementation.md",
        "role": "delegated microsite implementation worker",
        "result": "completed; commit 579db2b57a89b67889f2341d82dd13d9956cd405; 66 tests passed at that stage",
    },
    {
        "delegation_id": "deleg_d79665c8",
        "source": "deleg_d79665c8/task-0.log",
        "transcript": "llm_logs/transcripts/07-hermes-independent-audit.md",
        "role": "delegated independent read-only auditor",
        "result": "completed; FAIL 83/100 because the then-advertised live route returned 404; three implementation findings recorded",
    },
    {
        "delegation_id": "deleg_c2c5d5b7",
        "source": "deleg_c2c5d5b7/task-0.log",
        "transcript": "llm_logs/transcripts/08-hermes-audit-fixes.md",
        "role": "delegated audit-fix worker",
        "result": "completed; commit ef5d2f7b89aaa3c8b5beee67b0059a6c55b3246a; 69 tests passed",
    },
)


def sanitize(value):
    text = str(value)
    text = re.sub(r"/Users/[^/\s]+", "$HOME", text)
    text = re.sub(r"/home/[^/\s]+", "$HOME", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[REDACTED EMAIL]", text)
    text = text.replace("VO2" + " GROUP", "[REDACTED ORGANIZATION]")
    text = text.replace("OAuth session", "authentication session")
    text = re.sub(
        r"(?i)(api[_-]?key|token|password|secret)([\"'\s:=]+)[A-Za-z0-9_./+\-=]{12,}",
        r"\1\2[REDACTED]",
        text,
    )
    return text


def bounded(value):
    text = sanitize(value)
    if len(text) <= MAX_FIELD:
        return text
    return text[:MAX_FIELD] + f" …[truncated at {MAX_FIELD} characters]"


def export_one(record):
    source = CACHE / record["source"]
    if not source.is_file():
        raise SystemExit(f"missing supplied delegation source: {record['delegation_id']}")
    blocks = [
        f"# Hermes delegation — {record['role']}",
        "",
        "> Submission-safe export from the supplied Hermes live transcript.",
        "> Internal reasoning is excluded. Tool fields are bounded; machine paths, identity data, and credential-shaped strings are sanitized.",
        "> Child model/provider metadata was not exposed by this transcript; no child model is inferred.",
        "",
        f"- **Delegation ID:** `{record['delegation_id']}`",
        f"- **Result:** {record['result']}",
        "",
    ]
    counts = {"user": 0, "assistant": 0, "tool": 0, "result": 0, "final": 0}
    pattern = re.compile(r"^\d{2}:\d{2}:\d{2}\s+(user|assistant|tool|result|final)\s+\|\s?(.*)$")
    for line in source.read_text(encoding="utf-8", errors="replace").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        role, content = match.groups()
        counts[role] += 1
        label = {"user": "User", "assistant": "Assistant", "tool": "Tool call", "result": "Tool result", "final": "Final"}[role]
        blocks.extend([f"## {label} {counts[role]}", "", bounded(content), ""])
    blocks.extend(["---", "", "Export counts: " + " · ".join(f"{counts[key]} {key}" for key in counts) + ".", ""])
    destination = ROOT / record["transcript"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(blocks), encoding="utf-8")
    return hashlib.sha256(destination.read_bytes()).hexdigest(), counts


def main():
    exported = []
    for record in DELEGATIONS:
        digest, counts = export_one(record)
        item = {
            "delegation_id": record["delegation_id"],
            "transcript": record["transcript"],
            "role": record["role"],
            "result": record["result"],
            "child_model_metadata": "not exposed by delegation transcript",
            "sha256": digest,
            "export_counts": counts,
            "source_alias": f"Hermes cache/{record['delegation_id']}/task-0.log",
        }
        exported.append(item)
        print(f"{record['delegation_id']}: {digest}")
    manifest = {
        "schema_version": 1,
        "orchestrator": {
            "harness": "Hermes Agent",
            "model": "gpt-5.6-sol",
            "provider": "openai-codex",
            "role": "orchestration and final implementation pass",
        },
        "delegations": exported,
        "adaptations": [
            "Claude CLI authentication check returned Expired; no new Claude/Fable review was claimed.",
            "Standalone Codex CLI invocation returned command not found; this is an environment adaptation, not a model success.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
