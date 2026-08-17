#!/usr/bin/env python3
"""Export the three most recent local Claude sessions (dead-simple final UX
pass, its independent review, and the reported button-fix) without mutating
them. Reads local Claude session JSONLs plus their supplied run envelopes.
Writes only submission-safe prompt, visible-transcript, normalized-run, and
manifest files inside llm_logs/. Hidden thinking/signatures, hooks, connector
inventories, absolute home paths, emails, credential-shaped strings, and
oversized unrelated file dumps are excluded or sanitized. Any envelope that
ended at its turn limit or via an aborted stream is labeled exactly that way;
none is relabeled as success.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENVELOPE_DIR = ROOT.parent.parent
CLAUDE_PROJECT_DIR = (
    pathlib.Path.home() / ".claude" / "projects" / str(ROOT).replace("/", "-")
)
MAX_TOOL_FIELD = 4000

SESSIONS = [
    {
        "key": "dead_simple_final_pass",
        "session_id": "f6f2895b-748e-4576-904e-b3783efcb5dd",
        "canonical_model": "claude-sonnet-5",
        "prompt_dest": ROOT / "llm_logs" / "prompts" / "08_dead_simple_final_pass.md",
        "run_dest": ROOT / "llm_logs" / "runs" / "08-dead-simple-final-pass.json",
        "transcript_dest": ROOT / "llm_logs" / "transcripts" / "11-dead-simple-final-pass.md",
        "title": "Claude Sonnet 5 -- dead-simple final UX pass",
        "expected_prompts": 4,
        "envelopes": [
            ("attempt_1", "2026-08-17-valis-dead-simple-final.json"),
            ("attempt_2", "2026-08-17-valis-dead-simple-final-resume2.json"),
            ("attempt_3", "2026-08-17-valis-dead-simple-final-resume.json"),
            ("attempt_4", "2026-08-17-valis-dead-simple-final-resume3.json"),
        ],
        "outcome_note": (
            "All four envelopes ended without a clean success terminal state "
            "(aborted_streaming, then three max_turns cutoffs). The commit that "
            "followed immediately after (5427c9f) is the verifiable product of "
            "this work; the envelopes themselves are not relabeled as success."
        ),
    },
    {
        "key": "independent_review_dead_simple",
        "session_id": "b6b433a2-7137-4bbc-bc5b-cf9affb838e0",
        "canonical_model": "claude-sonnet-5",
        "prompt_dest": ROOT / "llm_logs" / "prompts" / "09_independent_review_dead_simple.md",
        "run_dest": ROOT / "llm_logs" / "runs" / "09-independent-review-dead-simple.json",
        "transcript_dest": ROOT / "llm_logs" / "transcripts" / "12-independent-review-dead-simple.md",
        "title": "Claude Sonnet 5 -- independent review of commit 5427c9f",
        "expected_prompts": 2,
        "envelopes": [
            ("attempt_1", "2026-08-17-valis-dead-simple-independent-review.json"),
            ("attempt_2", "2026-08-17-valis-dead-simple-independent-review-resume.json"),
        ],
        "outcome_note": (
            "First envelope ended at its configured turn limit. The resumed "
            "envelope completed cleanly (terminal_reason completed, subtype "
            "success) and returned the verbatim verdict quoted below."
        ),
    },
    {
        "key": "run_button_fix",
        "session_id": "800ed7d8-9ce4-4d26-8678-77fe46df870a",
        "canonical_model": "claude-sonnet-5",
        "prompt_dest": ROOT / "llm_logs" / "prompts" / "10_run_button_fix.md",
        "run_dest": ROOT / "llm_logs" / "runs" / "10-run-button-fix.json",
        "transcript_dest": ROOT / "llm_logs" / "transcripts" / "13-run-button-fix.md",
        "title": "Claude Sonnet 5 -- broken \"Run the automation\" button fix",
        "expected_prompts": 2,
        "envelopes": [
            ("attempt_1", "2026-08-17-valis-run-button-fix.json"),
            ("attempt_2", "2026-08-17-valis-run-button-fix-resume.json"),
        ],
        "outcome_note": (
            "Both envelopes ended at their configured turn limit (max_turns); "
            "neither is a success terminal state. The commit that followed "
            "immediately after (554126e) is the verifiable product of this "
            "work, verified separately by make test and browser interaction."
        ),
    },
]


def sanitize(value: object) -> str:
    text = str(value)
    text = re.sub(
        r"(?m)^.*skill_view ok .*$",
        "[workstation skill_view result omitted]",
        text,
    )
    text = re.sub(r"/Users/[^/\s\"']+", "$HOME", text)
    text = re.sub(r"/home/[^/\s\"']+", "$HOME", text)
    text = re.sub(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        "[REDACTED EMAIL]",
        text,
    )
    text = re.sub(r"(?<!\w)[A-Za-z0-9._%+-]{2,}@", "[REDACTED EMAIL]@", text)
    text = re.sub(r"(?i)@vo2\b", "@[REDACTED DOMAIN]", text)
    text = text.replace("VO2" + " GROUP", "[REDACTED ORGANIZATION]")
    text = re.sub(
        r"(?i)(api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)"
        r"([\"'\s:=]+)[A-Za-z0-9_./+\-=]{12,}",
        r"\1\2[REDACTED]",
        text,
    )
    text = re.sub(
        r"(?i)\b(api_key|password|secret|token)=",
        r"\1[assignment omitted]",
        text,
    )
    text = re.sub(r"(?<![A-Za-z0-9])(sk-|ghp_|xox[baprs]-|AKIA)[A-Za-z0-9_-]{8,}", "[REDACTED CREDENTIAL]", text)
    text = re.sub(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}", "Bearer [REDACTED]", text)
    return "\n".join(line.rstrip() for line in text.splitlines())


def bounded(value: object, limit: int = MAX_TOOL_FIELD) -> str:
    text = sanitize(value)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n\n[... truncated after {limit} visible characters; raw source is not shipped ...]"


def read_session(session_id: str) -> list[dict]:
    source = CLAUDE_PROJECT_DIR / f"{session_id}.jsonl"
    if not source.is_file():
        raise SystemExit(f"missing read-only Claude session JSONL for {session_id}")
    records = []
    for raw in source.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return records


def visible_prompts(records: list[dict], expected: int) -> list[str]:
    prompts = []
    for obj in records:
        msg = obj.get("message") or {}
        if obj.get("type") == "user" and msg.get("role") == "user" and isinstance(msg.get("content"), str):
            prompts.append(msg["content"])
    if len(prompts) != expected:
        raise SystemExit(f"expected {expected} visible prompts, found {len(prompts)}")
    return prompts


def export_prompts(dest: pathlib.Path, title: str, prompts: list[str]) -> None:
    blocks = [
        f"# {title} -- prompts",
        "",
        "> Exact visible prompt text for every turn of this session, exported read-only from the local Claude session JSONL.",
        "> The heading and this note are export metadata; each fenced block is a complete prompt body.",
        "",
    ]
    for i, prompt in enumerate(prompts, start=1):
        blocks.extend([f"## Prompt {i}", "", "```text", sanitize(prompt), "```", ""])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(blocks), encoding="utf-8")


def export_transcript(dest: pathlib.Path, title: str, session_id: str, model: str, records: list[dict]) -> dict[str, int]:
    blocks = [
        f"# {title}",
        "",
        "> Sanitized visible transcript exported read-only from the local Claude session JSONL.",
        "> Includes visible user prompts, assistant text, tool calls, and bounded tool results only.",
        "> Excludes hidden thinking/signatures, hooks, startup attachments, connector/tool inventories, and unrelated machine context.",
        "> Absolute home paths are normalized; emails, identity/credential-shaped strings, and oversized fields are sanitized.",
        "",
        f"- **Claude session ID:** `{session_id}`",
        f"- **Canonical model:** `{model}`",
        "",
    ]
    counts = {"user_prompts": 0, "assistant_text": 0, "tool_calls": 0, "tool_results": 0}
    for obj in records:
        msg = obj.get("message") or {}
        if obj.get("type") == "user" and msg.get("role") == "user":
            content = msg.get("content")
            if isinstance(content, str):
                counts["user_prompts"] += 1
                blocks.extend([f"## User {counts['user_prompts']}", "", bounded(content, 20000), ""])
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict) or item.get("type") != "tool_result":
                        continue
                    value = item.get("content", "")
                    if isinstance(value, list):
                        value = json.dumps(value, ensure_ascii=False, indent=2)
                    counts["tool_results"] += 1
                    blocks.extend(
                        [
                            f"### Tool result {counts['tool_results']}",
                            "",
                            "~~~~text",
                            bounded(value),
                            "~~~~",
                            "",
                        ]
                    )
        elif obj.get("type") == "assistant" and msg.get("role") == "assistant":
            resp_model = msg.get("model", "unknown")
            content = msg.get("content") or []
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text" and item.get("text"):
                    counts["assistant_text"] += 1
                    blocks.extend(
                        [
                            f"## Assistant {counts['assistant_text']} -- `{resp_model}`",
                            "",
                            bounded(item["text"], 20000),
                            "",
                        ]
                    )
                elif item.get("type") == "tool_use":
                    counts["tool_calls"] += 1
                    payload = json.dumps(item.get("input", {}), ensure_ascii=False, indent=2)
                    blocks.extend(
                        [
                            f"### Tool call {counts['tool_calls']} -- `{item.get('name', 'unknown')}`",
                            "",
                            "~~~~json",
                            bounded(payload),
                            "~~~~",
                            "",
                        ]
                    )
                # thinking/signature blocks are intentionally ignored.
    blocks.extend(
        [
            "---",
            "",
            "Export counts: " + " . ".join(f"{value} {key.replace('_', ' ')}" for key, value in counts.items()) + ".",
            "",
        ]
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(blocks), encoding="utf-8")
    return counts


def export_runs(session: dict) -> list[dict]:
    runs = []
    for role, filename in session["envelopes"]:
        source = ENVELOPE_DIR / filename
        if not source.is_file():
            raise SystemExit(f"missing supplied run envelope: {filename}")
        raw = json.loads(source.read_text(encoding="utf-8"))
        run = {
            "role": role,
            "session_id": raw.get("session_id"),
            "is_error": raw.get("is_error"),
            "num_turns": raw.get("num_turns"),
            "stop_reason": raw.get("stop_reason"),
            "terminal_reason": raw.get("terminal_reason"),
            "subtype": raw.get("subtype"),
            "total_cost_usd": raw.get("total_cost_usd"),
            "errors": raw.get("errors", []),
        }
        if raw.get("result"):
            run["result"] = sanitize(raw["result"])
        runs.append(run)
    if any(run["session_id"] != session["session_id"] for run in runs):
        raise SystemExit(f"supplied envelopes for {session['key']} do not share the expected session ID")
    record = {
        "schema_version": 1,
        "source": "normalized from supplied run envelopes; raw envelopes remain outside the repository",
        "session_id": session["session_id"],
        "canonical_model": session["canonical_model"],
        "runs": runs,
        "totals": {
            "cost_usd": sum(run["total_cost_usd"] for run in runs),
            "reported_num_turns": sum(run["num_turns"] for run in runs),
        },
        "outcome_note": session["outcome_note"],
    }
    session["run_dest"].parent.mkdir(parents=True, exist_ok=True)
    session["run_dest"].write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return runs


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    manifest_sessions = []
    for session in SESSIONS:
        records = read_session(session["session_id"])
        prompts = visible_prompts(records, session["expected_prompts"])
        export_prompts(session["prompt_dest"], session["title"], prompts)
        counts = export_transcript(
            session["transcript_dest"], session["title"], session["session_id"], session["canonical_model"], records
        )
        runs = export_runs(session)
        manifest_sessions.append(
            {
                "key": session["key"],
                "session_id": session["session_id"],
                "canonical_model": session["canonical_model"],
                "artifacts": [
                    {"path": str(session["prompt_dest"].relative_to(ROOT)), "sha256": sha256(session["prompt_dest"])},
                    {"path": str(session["run_dest"].relative_to(ROOT)), "sha256": sha256(session["run_dest"])},
                    {"path": str(session["transcript_dest"].relative_to(ROOT)), "sha256": sha256(session["transcript_dest"])},
                ],
                "visible_transcript_counts": counts,
                "run_outcomes": [
                    {
                        "role": run["role"],
                        "terminal_reason": run["terminal_reason"],
                        "subtype": run["subtype"],
                        "num_turns": run["num_turns"],
                        "total_cost_usd": run["total_cost_usd"],
                    }
                    for run in runs
                ],
            }
        )
        print(f"{session['key']}: " + json.dumps(counts, sort_keys=True))

    manifest_dest = ROOT / "llm_logs" / "recent_finalization_manifest.json"
    manifest_dest.write_text(
        json.dumps({"schema_version": 1, "sessions": manifest_sessions}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("manifest: " + sha256(manifest_dest))


if __name__ == "__main__":
    main()
