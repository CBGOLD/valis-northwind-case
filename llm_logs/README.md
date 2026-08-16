# LLM logs

AI-native build, disclosed without leaking the workstation or turning failed tool calls into model achievements.

## Layout

- `prompts/` — prompts supplied to builders, auditors, revision passes, and the Hermes-led final pass.
- `runs/` — direct run envelopes and factual orchestration records. Empty/failed records are retained rather than rewritten as success.
- `transcripts/` — submission-safe visible transcripts: prompts, assistant-visible text, tool calls, and bounded tool results. Hidden reasoning is excluded.
- `hermes_manifest.json` — deterministic inventory, SHA-256 digest, role, result, and model-metadata boundary for each supplied Hermes delegation.
- `tools/export_transcripts.py` — deterministic exporter for the original Claude Code JSONL records.
- `tools/export_hermes_transcripts.py` — deterministic exporter for the three supplied Hermes live transcripts.

## Roles

- **Hermes Agent orchestrator — GPT-5.6-sol via openai-codex** — orchestrated the final implementation pass: source/provenance inspection, Deliverable 03 redesign, tests, browser verification, diff review, and local commit. This is the known parent runtime.
- **Hermes delegated workers** — implementation (`deleg_d02432f8`), independent audit (`deleg_d79665c8`), and audit fixes (`deleg_c2c5d5b7`). Their transcript envelopes do **not** expose child model/provider metadata, so none is inferred or attributed. “Hermes orchestrator” and “delegated worker” are deliberately separate roles.
- **Claude Fable 5** — original primary builder and targeted revision worker in the prior, already-valid records.
- **Claude Opus 5** — original independent ground-truth and gauntlet auditor in the prior records.
- **Claude Opus 5 + Claude Fable 5** — prior separate fresh-context critics against the then-committed artifact. Their historical verdicts remain valid for those commits; this final pass does not claim a new Fable review.

## Final-pass provenance and adaptations

Known delegated results are preserved with exact IDs and commits:

- `deleg_d02432f8` → microsite implementation → commit `579db2b57a89b67889f2341d82dd13d9956cd405`; 66 tests at that stage; browser baseline exercised.
- `deleg_d79665c8` → read-only audit → **FAIL 83/100**; browser baseline/orphan/CSV/console checks passed, while the then-advertised live route returned 404 and three implementation findings were recorded.
- `deleg_c2c5d5b7` → audit fixes → commit `ef5d2f7b89aaa3c8b5beee67b0059a6c55b3246a`; 69 tests; duplicate-ID rejection, CSV escaping, and table accessibility hardened.

Two failed prerequisites are adaptations, **not a model success**:

1. A Claude CLI authentication check returned **Expired**. No new Claude/Fable review occurred.
2. A standalone **Codex CLI** review attempt returned **command not found**. No Codex CLI worker ran. The known `openai-codex` provider of the Hermes parent runtime is not evidence that a standalone CLI invocation succeeded.

The final test/browser result is recorded in `BUILD_LOG.md` after execution rather than predicted here.

## Sanitization policy

Raw local session files are not shipped because they can contain hidden reasoning/signature payloads, startup attachments, connector inventories, absolute machine context, identity data, and repeated source dumps irrelevant to evaluation. The exporters:

1. preserve visible prompts/responses, tool names/inputs, and bounded tool results;
2. exclude hidden reasoning/signature blocks and unrelated startup/connector context;
3. normalize home-directory paths and redact identity/credential-shaped strings;
4. truncate large individual fields with an explicit marker;
5. record when child model metadata was not exposed rather than guessing it.

The raw sources remain local. Re-run `python3 tools/export_hermes_transcripts.py` to reproduce the Hermes exports and manifest from the supplied cache records. This boundary is disclosed rather than presenting sanitized logs as raw logs.
