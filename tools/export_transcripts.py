#!/usr/bin/env python3
"""Export submission-safe Claude Code transcripts from local session JSONL.

Keeps prompts, assistant text, tool calls, and bounded tool results. Drops
thinking/signature payloads, hooks/attachments, and connector inventories.
"""
import json
import pathlib
import re

HOME = pathlib.Path.home()
SOURCE = HOME / ".claude/projects/-Users-cb-workspace-valis-northwind-case"
DEST = pathlib.Path(__file__).resolve().parents[1] / "llm_logs/transcripts"
SESSIONS = {
    "01-fable-builder.md": ("3d2c2126-fb2b-4552-bf47-24bc21f6f7aa.jsonl", "Claude Fable 5 — builder + resumed build"),
    "02-opus-ground-truth.md": ("4974fb22-4550-4be8-803b-216b1ba7e627.jsonl", "Claude Opus 5 — independent ground-truth pass"),
    "03-opus-gauntlet.md": ("4ee4790d-7ab2-47cb-9d27-d640920e705e.jsonl", "Claude Opus 5 — committed-artifact gauntlet critic"),
    "04-fable-gauntlet.md": ("b55b2c81-d141-41d1-a1f5-0b035979cf25.jsonl", "Claude Fable 5 — committed-artifact gauntlet critic"),
    "05-fable-revision.md": ("f1173d23-88a6-41c4-ac8f-5e283e981bb4.jsonl", "Claude Fable 5 — targeted defect revision"),
}


def sanitize(value):
    text = str(value).replace(str(HOME), "$HOME").replace("/Users/vo2group", "$LEGACY_HOME")
    return re.sub(
        r"(?i)(api[_-]?key|token|password|secret)([\"'\s:=]+)[A-Za-z0-9_./+\-=]{16,}",
        r"\1\2[REDACTED]",
        text,
    )


def bounded(value, limit=8000):
    text = sanitize(value)
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n[… tool result truncated after {limit} characters; raw source intentionally not shipped …]"


def export(source, destination, title):
    blocks = [
        f"# {title}",
        "",
        "> Sanitized transcript export. Preserves user prompts, assistant text, tool calls, and bounded tool results.",
        "> Excludes internal thinking/signature payloads, startup hooks, connector inventories, and unrelated machine context.",
        "> Absolute home paths are normalized. Oversized tool results carry an explicit truncation marker; raw JSONL stays local.",
        "",
        f"- **Claude session ID:** `{source.stem}`",
        "",
    ]
    users = assistants = tools = 0
    for raw in source.read_text(errors="replace").splitlines():
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        msg = obj.get("message") or {}
        if obj.get("type") == "user" and msg.get("role") == "user":
            content = msg.get("content")
            if isinstance(content, str):
                users += 1
                blocks += [f"## User {users}", "", bounded(content, 16000), ""]
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict) or item.get("type") != "tool_result":
                        continue
                    value = item.get("content", "")
                    if isinstance(value, list):
                        value = json.dumps(value, ensure_ascii=False, indent=2)
                    tools += 1
                    blocks += [f"### Tool result {tools}", "", "```text", bounded(value), "```", ""]
        elif obj.get("type") == "assistant" and msg.get("role") == "assistant":
            model = msg.get("model", "unknown")
            content = msg.get("content") or []
            if isinstance(content, str):
                content = [{"type": "text", "text": content}]
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") == "text" and item.get("text"):
                    assistants += 1
                    blocks += [f"## Assistant {assistants} — `{model}`", "", bounded(item["text"], 20000), ""]
                elif item.get("type") == "tool_use":
                    tools += 1
                    payload = json.dumps(item.get("input", {}), ensure_ascii=False, indent=2)
                    blocks += [f"### Tool call {tools} — `{item.get('name', 'unknown')}`", "", "```json", bounded(payload), "```", ""]
                # Intentionally exclude thinking/signature blocks.
    blocks += ["", "---", f"Export counts: {users} user prompts · {assistants} assistant text blocks · {tools} tool call/result blocks.", ""]
    destination.write_text("\n".join(blocks), encoding="utf-8")
    return users, assistants, tools


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for name, (session, title) in SESSIONS.items():
        source = SOURCE / session
        if not source.exists():
            raise SystemExit(f"missing session: {source}")
        counts = export(source, DEST / name, title)
        print(f"{name}: {counts[0]} prompts, {counts[1]} assistant blocks, {counts[2]} tool blocks")


if __name__ == "__main__":
    main()
