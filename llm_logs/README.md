# LLM logs

AI-native build, disclosed without leaking the workstation or turning failed tool calls into model achievements.

## Layout

- `prompts/` — prompts supplied to builders, auditors, revision passes, the Hermes-led final pass, and the authenticated final Fable review/fix chain.
- `runs/` — direct run envelopes and factual orchestration records. Empty/failed records are retained rather than rewritten as success.
- `transcripts/` — submission-safe visible transcripts: prompts, assistant-visible text, tool calls, and bounded tool results. Hidden reasoning is excluded.
- `hermes_manifest.json` — deterministic inventory, SHA-256 digest, role, result, and model-metadata boundary for each supplied Hermes delegation.
- `fable_final_manifest.json` — deterministic SHA-256 inventory for the final Fable prompt, normalized three-envelope run record, and sanitized visible transcript.
- `tools/export_transcripts.py` — deterministic exporter for the original Claude Code JSONL records.
- `tools/export_hermes_transcripts.py` — deterministic exporter for the four supplied Hermes live transcripts.
- `tools/export_final_fable.py` — read-only exporter for the authenticated final Fable session plus its three supplied run envelopes.

## Roles

- **Hermes Agent orchestrator — GPT-5.6-sol via openai-codex** — orchestrated the final implementation pass: source/provenance inspection, Deliverable 03 redesign, tests, browser verification, diff review, and local commit. This is the known parent runtime.
- **Hermes delegated workers** — implementation (`deleg_d02432f8`), independent audit (`deleg_d79665c8`), audit fixes (`deleg_c2c5d5b7`), and the final thorough pass (`deleg_5d1fc70f`). Their transcript envelopes do **not** expose child model/provider metadata, so none is inferred or attributed. “Hermes orchestrator” and “delegated worker” are deliberately separate roles.
- **Claude Fable 5** — original primary builder and targeted revision worker in the prior, already-valid records.
- **Claude Opus 5** — original independent ground-truth and gauntlet auditor in the prior records.
- **Claude Opus 5 + Claude Fable 5** — prior separate fresh-context critics against the then-committed artifact. Their historical verdicts remain valid for those commits; the `deleg_5d1fc70f` pass itself did not claim a new Fable review.
- **Claude Fable 5 (post-`7f75ea2` critique and bounded fixes)** — authenticated session `9b8063b5-283f-4740-9cad-410fd348d63a` independently reviewed exact commit `7f75ea21d4588168a3c8f3edac142af1ecf9268d`: **PASS 91/100**, zero BLOCKER/HIGH. The same session then made the bounded fixes now in this candidate. Its two fix invocations ended transparently at their 15- and 12-turn limits; neither terminal envelope is relabeled as success.

## Final-pass provenance and adaptations

Known delegated results are preserved with exact IDs and commits:

- `deleg_d02432f8` → microsite implementation → commit `579db2b57a89b67889f2341d82dd13d9956cd405`; 66 tests at that stage; browser baseline exercised.
- `deleg_d79665c8` → read-only audit → **FAIL 83/100**; browser baseline/orphan/CSV/console checks passed, while the then-advertised live route returned 404 and three implementation findings were recorded.
- `deleg_c2c5d5b7` → audit fixes → commit `ef5d2f7b89aaa3c8b5beee67b0059a6c55b3246a`; 69 tests; duplicate-ID rejection, CSV escaping, and table accessibility hardened.
- `deleg_5d1fc70f` → final thorough pass (Deliverable 03 redesign, `REVIEW_GUIDE.md`, provenance exports, new tests) → commit `7f75ea21d4588168a3c8f3edac142af1ecf9268d`; 77 tests pass at that commit; the session ended at its iteration budget immediately after the local commit.

Two failed prerequisites are adaptations, **not a model success**:

1. A Claude CLI authentication check returned **Expired**. No new Claude/Fable review occurred.
2. A standalone **Codex CLI** review attempt returned **command not found**. No Codex CLI worker ran. The known `openai-codex` provider of the Hermes parent runtime is not evidence that a standalone CLI invocation succeeded.

Those prerequisite failures occurred during the earlier Hermes pass. Authentication was subsequently available for the separately recorded final Fable session; that later success does not rewrite the earlier failed checks.

## Authenticated final Fable chain

- Exact final-review prompt: [`prompts/07_fable_final_review_and_fixes.md`](prompts/07_fable_final_review_and_fixes.md). The two bounded-fix prompts are preserved in normalized form inside the visible transcript so their one raw absolute source path is not published.
- Normalized supplied envelopes: [`runs/07-fable-final-review-and-fixes.json`](runs/07-fable-final-review-and-fixes.json). Review: completed in 30 reported turns, **$5.769933**. Fix attempt 1: `error_max_turns`, 16 reported envelope turns / configured 15-turn limit, **$3.893864**. Fix attempt 2: `error_max_turns`, 13 reported envelope turns / configured 12-turn limit, **$5.644601000000001**. Exact total: **$15.308398000000001** and **59 reported envelope turns** (27 configured fix-limit turns).
- Sanitized visible session: [`transcripts/10-fable-final-review-and-fixes.md`](transcripts/10-fable-final-review-and-fixes.md), exported read-only from the located local JSONL; 3 user prompts, 20 assistant text blocks, 57 tool calls, and 57 tool results.
- Deterministic hashes: [`fable_final_manifest.json`](fable_final_manifest.json).

The final test/browser result is recorded in `BUILD_LOG.md` after execution rather than predicted here. This candidate is prepared locally; these logs do not claim it has been published.

## Sanitization policy

Raw local session files are not shipped because they can contain hidden reasoning/signature payloads, startup attachments, connector inventories, absolute machine context, identity data, and repeated source dumps irrelevant to evaluation. The exporters:

1. preserve visible prompts/responses, tool names/inputs, and bounded tool results;
2. exclude hidden reasoning/signature blocks and unrelated startup/connector context;
3. normalize home-directory paths and redact identity/credential-shaped strings;
4. truncate large individual fields with an explicit marker;
5. omit `skill_view` result bodies (workstation skill documentation, including personal tooling unrelated to this repository) with an explicit marker, keeping only the skill name, status, and duration;
6. record when child model metadata was not exposed rather than guessing it.

The raw sources remain local, so `python3 tools/export_hermes_transcripts.py` and `python3 tools/export_final_fable.py` reproduce their respective exports/manifests only on the original workstation (elsewhere they fail fast with a clear missing-source error). The committed SHA-256 digests let anyone verify the shipped exports are the ones the exporters produced. This boundary is disclosed rather than presenting sanitized logs as raw logs.
