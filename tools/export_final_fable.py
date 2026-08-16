#!/usr/bin/env python3
"""Export the authenticated final Fable review/fix session without mutating it.

Reads one local Claude session JSONL plus the three supplied run envelopes. Writes
only submission-safe prompt, visible-transcript, normalized-run, and manifest
files inside llm_logs/. Hidden thinking/signatures, hooks, connector inventories,
absolute home paths, emails, credential-shaped strings, and oversized unrelated
file dumps are excluded or sanitized.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SUPPLIED = ROOT.parent
SESSION_ID = "9b8063b5-283f-4740-9cad-410fd348d63a"
SOURCE = (
    pathlib.Path.home()
    / ".claude"
    / "projects"
    / str(ROOT).replace("/", "-")
    / f"{SESSION_ID}.jsonl"
)
PROMPT_DEST = ROOT / "llm_logs" / "prompts" / "07_fable_final_review_and_fixes.md"
RUN_DEST = ROOT / "llm_logs" / "runs" / "07-fable-final-review-and-fixes.json"
TRANSCRIPT_DEST = ROOT / "llm_logs" / "transcripts" / "10-fable-final-review-and-fixes.md"
MANIFEST_DEST = ROOT / "llm_logs" / "fable_final_manifest.json"
ENVELOPES = (
    ("review", "fable-review.json"),
    ("bounded_fix_attempt_1", "fable-fixes.json"),
    ("bounded_fix_attempt_2", "fable-fixes-resume.json"),
)
MAX_TOOL_FIELD = 8000


def sanitize(value: object) -> str:
    text = str(value)
    # A visible grep result in this session quoted an old skill_view result.
    # Remove the whole quoted result line, not just known personal phrases.
    text = re.sub(
        r"(?m)^.*skill_view ok .*$",
        "[workstation skill_view result omitted]",
        text,
    )
    personal_skill_excerpt = "Route short linear answers" + " to Telegram"
    text = re.sub(
        rf"…for Charles… {re.escape(personal_skill_excerpt)}…",
        "[workstation skill description omitted]",
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
    text = re.sub(r"\b(sk-|ghp_|xox[baprs]-|AKIA)[A-Za-z0-9_-]{8,}\b", "[REDACTED CREDENTIAL]", text)
    text = re.sub(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}", "Bearer [REDACTED]", text)
    return "\n".join(line.rstrip() for line in text.splitlines())


def bounded(value: object, limit: int = MAX_TOOL_FIELD) -> str:
    text = sanitize(value)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + f"\n\n[… truncated after {limit} visible characters; raw source is not shipped …]"


def read_session() -> list[dict]:
    if not SOURCE.is_file():
        raise SystemExit(f"missing read-only Claude session JSONL for {SESSION_ID}")
    records = []
    for raw in SOURCE.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            records.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return records


def visible_prompts(records: list[dict]) -> list[str]:
    prompts = []
    for obj in records:
        msg = obj.get("message") or {}
        if obj.get("type") == "user" and msg.get("role") == "user" and isinstance(msg.get("content"), str):
            prompts.append(msg["content"])
    if len(prompts) != 3:
        raise SystemExit(f"expected 3 visible prompts, found {len(prompts)}")
    return prompts


def export_prompts(prompts: list[str]) -> None:
    blocks = [
        "# Authenticated final Fable review prompt",
        "",
        "> Exact visible review prompt text, exported read-only from the authenticated Claude session JSONL.",
        "> The heading and this note are export metadata; the fenced block is the complete prompt body.",
        "",
        "```text",
        prompts[0],
        "```",
        "",
    ]
    PROMPT_DEST.parent.mkdir(parents=True, exist_ok=True)
    PROMPT_DEST.write_text("\n".join(blocks), encoding="utf-8")


def export_transcript(records: list[dict]) -> dict[str, int]:
    blocks = [
        "# Claude Fable 5 — final review and bounded fixes",
        "",
        "> Sanitized visible transcript exported read-only from the local Claude session JSONL.",
        "> Includes visible user prompts, assistant text, tool calls, and bounded tool results only.",
        "> Excludes hidden thinking/signatures, hooks, startup attachments, connector/tool inventories, and unrelated machine context.",
        "> Absolute home paths are normalized; emails, identity/credential-shaped strings, and oversized fields are sanitized.",
        "",
        f"- **Claude session ID:** `{SESSION_ID}`",
        "- **Canonical model:** `claude-fable-5`",
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
            model = msg.get("model", "unknown")
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
                            f"## Assistant {counts['assistant_text']} — `{model}`",
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
                            f"### Tool call {counts['tool_calls']} — `{item.get('name', 'unknown')}`",
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
            "Export counts: " + " · ".join(f"{value} {key.replace('_', ' ')}" for key, value in counts.items()) + ".",
            "",
        ]
    )
    TRANSCRIPT_DEST.parent.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DEST.write_text("\n".join(blocks), encoding="utf-8")
    return counts


def export_runs() -> list[dict]:
    runs = []
    for role, filename in ENVELOPES:
        source = SUPPLIED / filename
        if not source.is_file():
            raise SystemExit(f"missing supplied run envelope: {filename}")
        raw = json.loads(source.read_text(encoding="utf-8"))
        model_usage = raw.get("modelUsage", {}).get("claude-fable-5", {})
        run = {
            "role": role,
            "session_id": raw.get("session_id"),
            "canonical_model": model_usage.get("canonicalModel"),
            "provider": model_usage.get("provider"),
            "is_error": raw.get("is_error"),
            "num_turns": raw.get("num_turns"),
            "stop_reason": raw.get("stop_reason"),
            "terminal_reason": raw.get("terminal_reason"),
            "subtype": raw.get("subtype"),
            "total_cost_usd": raw.get("total_cost_usd"),
            "errors": raw.get("errors", []),
        }
        if role == "review":
            run.update(
                {
                    "verdict": "PASS",
                    "score": 91,
                    "blocker_count": 0,
                    "high_count": 0,
                    "result_summary": "PASS 91/100; recommendation GO after two one-line pre-push documentation edits.",
                }
            )
        runs.append(run)
    if any(run["session_id"] != SESSION_ID for run in runs):
        raise SystemExit("supplied envelopes do not share the expected session ID")
    if any(run["canonical_model"] != "claude-fable-5" for run in runs):
        raise SystemExit("supplied envelopes do not report canonical model claude-fable-5")
    record = {
        "schema_version": 1,
        "source": "normalized from the three supplied run envelopes; raw envelopes remain outside the repository",
        "session_id": SESSION_ID,
        "canonical_model": "claude-fable-5",
        "runs": runs,
        "totals": {
            "cost_usd": sum(run["total_cost_usd"] for run in runs),
            "cost_usd_exact": "15.308398000000001",
            "reported_num_turns": sum(run["num_turns"] for run in runs),
            "bounded_fix_attempt_limit_turns": 27,
        },
    }
    RUN_DEST.parent.mkdir(parents=True, exist_ok=True)
    RUN_DEST.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return runs


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    records = read_session()
    prompts = visible_prompts(records)
    export_prompts(prompts)
    counts = export_transcript(records)
    runs = export_runs()
    manifest = {
        "schema_version": 1,
        "session_id": SESSION_ID,
        "canonical_model": "claude-fable-5",
        "artifacts": [
            {"path": str(PROMPT_DEST.relative_to(ROOT)), "sha256": sha256(PROMPT_DEST)},
            {"path": str(RUN_DEST.relative_to(ROOT)), "sha256": sha256(RUN_DEST)},
            {"path": str(TRANSCRIPT_DEST.relative_to(ROOT)), "sha256": sha256(TRANSCRIPT_DEST)},
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
    MANIFEST_DEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"prompt: {sha256(PROMPT_DEST)}")
    print(f"run: {sha256(RUN_DEST)}")
    print(f"transcript: {sha256(TRANSCRIPT_DEST)}")
    print("manifest: " + sha256(MANIFEST_DEST))
    print("visible transcript counts: " + json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
