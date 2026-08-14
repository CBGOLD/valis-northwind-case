# LLM logs

AI-native build, disclosed without leaking the workstation.

## Layout

- `prompts/` — exact prompts supplied to builder, ground-truth auditor, gauntlet critics, and revision pass.
- `runs/` — direct Claude CLI result envelopes and standalone verdicts. Empty/failed run records are retained rather than rewritten; `05b-fable-revision-resume.json` records the real monthly-spend-limit failure.
- `transcripts/` — submission-safe exports of the underlying Claude Code sessions: user prompts, assistant text, tool calls, and bounded tool results.
- `tools/export_transcripts.py` — deterministic export logic used to produce those transcripts.

## Roles

- **Claude Fable 5** — primary builder.
- **Claude Opus 5** — independent ground-truth audit before the build.
- **Claude Opus 5 + Claude Fable 5** — separate fresh-context critics against committed HEAD. Both returned PASS with no BLOCKER/HIGH defects; their medium findings drove the final revision.

## Sanitization policy

Raw Claude JSONL is not shipped because it contains internal thinking/signature payloads, startup hooks, connector inventories, absolute machine context, and repeated full source dumps that are irrelevant to evaluating the work. The transcript exporter:

1. preserves prompts, visible assistant responses, tool names/inputs, and tool results;
2. excludes hidden thinking/signature blocks and environment hook/connector attachments;
3. normalizes home-directory paths and redacts credential-shaped strings;
4. truncates individual tool results above 8,000 characters with an explicit marker.

The raw local sessions remain on the workstation; the submitted transcripts are inspectable and reproducible with `python3 tools/export_transcripts.py` on that machine. This boundary is itself disclosed rather than pretending sanitized logs are raw logs.
