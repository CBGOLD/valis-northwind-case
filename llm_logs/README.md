# LLM logs

AI-native build, disclosed without leaking the workstation or turning failed tool calls into model achievements.

GitHub's own UI does not surface per-turn timing for commits, so timing lives here instead: every row
below links straight to the exact prompt, run envelope, and sanitized transcript for that stage. No
directory-hunting required.

## Chronological index

| # | Date (CEST) | Stage | Prompt | Run envelope(s) | Transcript | Outcome |
|---|---|---|---|---|---|---|
| 1 | 2026-08-14 23:50 | Fable — primary builder | [01](prompts/01_fable_builder.md) | [01](runs/01-fable-builder.json) / [01b](runs/01b-fable-resume.json) | [01](transcripts/01-fable-builder.md) | Build completed; commit `bc9fd86`→`6b73b1f` lineage |
| 2 | 2026-08-14 23:50 | Opus — independent ground truth | [02](prompts/02_opus_ground_truth.md) | [02](runs/02-opus-ground-truth.json) | [02](transcripts/02-opus-ground-truth.md) | Ground-truth recompute, reconciled against builder |
| 3 | 2026-08-15 00:38 | Opus — gauntlet review | [03](prompts/03_opus_gauntlet_review.md) | [03](runs/03-opus-gauntlet-review.json) / [03b](runs/03b-opus-gauntlet-verdict.json) | [03](transcripts/03-opus-gauntlet.md) | **PASS 87/100**, zero BLOCKER/HIGH |
| 4 | 2026-08-15 00:38 | Fable — gauntlet review | [04](prompts/04_fable_gauntlet_review.md) | [04](runs/04-fable-gauntlet-review.json) / [04b](runs/04b-fable-gauntlet-verdict.json) | [04](transcripts/04-fable-gauntlet.md) | **PASS 86/100**, zero BLOCKER/HIGH |
| 5 | 2026-08-15 00:46 | Fable — gauntlet-fix revision | [05](prompts/05_fable_revision.md) | [05](runs/05-fable-revision.json) / [05b](runs/05b-fable-revision-resume.json) | [05](transcripts/05-fable-revision.md) | Org spend-limit hit on resume (preserved, not hidden); fixes completed locally |
| 6 | 2026-08-16 15:53 | Hermes delegation `deleg_d02432f8` — microsite implementation | [06](prompts/06_hermes_final_pass.md) | [06](runs/06-hermes-final-pass.json) | [06](transcripts/06-hermes-microsite-implementation.md) | Completed; commit `579db2b`; 66 tests |
| 7 | 2026-08-16 16:05 | Hermes delegation `deleg_d79665c8` — independent audit | [06](prompts/06_hermes_final_pass.md) | [06](runs/06-hermes-final-pass.json) | [07](transcripts/07-hermes-independent-audit.md) | **FAIL 83/100** — live route 404 at the time; findings recorded |
| 8 | 2026-08-16 16:05 | Hermes delegation `deleg_c2c5d5b7` — audit fixes | [06](prompts/06_hermes_final_pass.md) | [06](runs/06-hermes-final-pass.json) | [08](transcripts/08-hermes-audit-fixes.md) | Completed; commit `ef5d2f7`; 69 tests |
| 9 | 2026-08-16 20:28 | Hermes delegation `deleg_5d1fc70f` — final thorough pass | [06](prompts/06_hermes_final_pass.md) | [06](runs/06-hermes-final-pass.json) | [09](transcripts/09-hermes-thorough-pass.md) | Completed; commit `7f75ea2`; 77 tests; ended at iteration budget right after commit |
| 10 | 2026-08-16 20:56 | Fable — authenticated final review + bounded fixes | [07](prompts/07_fable_final_review_and_fixes.md) | [07](runs/07-fable-final-review-and-fixes.json) | [10](transcripts/10-fable-final-review-and-fixes.md) | Review **PASS 91/100**; 2 fix attempts both ended `error_max_turns`, not success; commit `8307007` |
| 11 | 2026-08-17 16:00–16:19 | Sonnet — dead-simple final UX pass | [08](prompts/08_dead_simple_final_pass.md) | [08](runs/08-dead-simple-final-pass.json) | [11](transcripts/11-dead-simple-final-pass.md) | All 4 envelopes ended `aborted_streaming`/`error_max_turns`, not success; commit `5427c9f` followed |
| 12 | 2026-08-17 16:21–16:23 | Sonnet — independent review of `5427c9f` | [09](prompts/09_independent_review_dead_simple.md) | [09](runs/09-independent-review-dead-simple.json) | [12](transcripts/12-independent-review-dead-simple.md) | **PASS**, one self-reported MEDIUM verification gap (reviewer did not run `make test`); LOW: missing `.nojekyll` |
| 13 | 2026-08-17 16:45–16:48 | Sonnet — "Run the automation" button-fix | [10](prompts/10_run_button_fix.md) | [10](runs/10-run-button-fix.json) | [13](transcripts/13-run-button-fix.md) | Both envelopes ended `error_max_turns`, not success; commit `554126e` followed |

Rows 11–13 are the most recent finalization work (Aug 17): the dead-simple redesign, its independent
review, and the reported broken-button fix. See `recent_finalization_manifest.json` for their SHA-256
digests and `BUILD_LOG.md` for the dated narrative tying each row to a commit and a verification run.

## Layout

- `prompts/` — exact prompt text supplied to every builder, auditor, revision pass, the Hermes-led final
  pass, the authenticated final Fable review/fix chain, and the Aug 17 dead-simple/review/button-fix sessions.
- `runs/` — direct run envelopes and factual orchestration records. Empty/failed records are retained
  rather than rewritten as success. Any envelope with `terminal_reason` of `max_turns` or
  `aborted_streaming` is reported as exactly that — never relabeled as success.
- `transcripts/` — submission-safe visible transcripts: prompts, assistant-visible text, tool calls, and
  bounded tool results. Hidden reasoning is excluded.
- `hermes_manifest.json` — deterministic inventory, SHA-256 digest, role, result, and model-metadata
  boundary for each supplied Hermes delegation.
- `fable_final_manifest.json` — deterministic SHA-256 inventory for the final Fable prompt, normalized
  three-envelope run record, and sanitized visible transcript.
- `recent_finalization_manifest.json` — deterministic SHA-256 inventory for the three Aug 17 sessions
  (rows 11–13 above): dead-simple final pass, its independent review, and the button-fix.
- `tools/export_transcripts.py` — deterministic exporter for the original Claude Code JSONL records.
- `tools/export_hermes_transcripts.py` — deterministic exporter for the four supplied Hermes live transcripts.
- `tools/export_final_fable.py` — read-only exporter for the authenticated final Fable session plus its
  three supplied run envelopes.
- `tools/export_recent_finalization.py` — read-only exporter for the three Aug 17 sessions (dead-simple
  final pass, its independent review, and the button-fix) plus their nine supplied run envelopes.

## Roles

- **Hermes Agent orchestrator — GPT-5.6-sol via openai-codex** — orchestrated the final implementation pass: source/provenance inspection, Deliverable 03 redesign, tests, browser verification, diff review, and local commit. This is the known parent runtime.
- **Hermes delegated workers** — implementation (`deleg_d02432f8`), independent audit (`deleg_d79665c8`), audit fixes (`deleg_c2c5d5b7`), and the final thorough pass (`deleg_5d1fc70f`). Their transcript envelopes do **not** expose child model/provider metadata, so none is inferred or attributed. "Hermes orchestrator" and "delegated worker" are deliberately separate roles.
- **Claude Fable 5** — original primary builder and targeted revision worker in the prior, already-valid records.
- **Claude Opus 5** — original independent ground-truth and gauntlet auditor in the prior records.
- **Claude Opus 5 + Claude Fable 5** — prior separate fresh-context critics against the then-committed artifact. Their historical verdicts remain valid for those commits; the `deleg_5d1fc70f` pass itself did not claim a new Fable review.
- **Claude Fable 5 (post-`7f75ea2` critique and bounded fixes)** — authenticated session `9b8063b5-283f-4740-9cad-410fd348d63a` independently reviewed exact commit `7f75ea21d4588168a3c8f3edac142af1ecf9268d`: **PASS 91/100**, zero BLOCKER/HIGH. The same session then made the bounded fixes now in this candidate. Its two fix invocations ended transparently at their 15- and 12-turn limits; neither terminal envelope is relabeled as success.
- **Claude Sonnet 5 (Aug 17 dead-simple final pass)** — session `f6f2895b-748e-4576-904e-b3783efcb5dd` redesigned the public page around four plain-labeled deliverables after direct user feedback that live links 404'd, timed logs looked absent, and the copy read as jargon/AI slop. All four supplied envelopes ended `aborted_streaming` or `error_max_turns`; commit `5427c9f` is the verifiable product, not the envelope terminal state.
- **Claude Sonnet 5 (Aug 17 independent review)** — session `b6b433a2-7137-4bbc-bc5b-cf9affb838e0` reviewed exact commit `5427c9f` from fresh context: **PASS**, with one self-reported MEDIUM verification gap (did not itself run `make test`) and a LOW finding that `.nojekyll` was missing at the time of review.
- **Claude Sonnet 5 (Aug 17 button-fix)** — session `800ed7d8-9ce4-4d26-8678-77fe46df870a` fixed a reported UX defect (the "Run the automation" button gave no visible feedback on activation). Both supplied envelopes ended `error_max_turns`; commit `554126e` is the verifiable product, verified separately by `make test` and browser interaction (see `BUILD_LOG.md`).

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

## Aug 17 dead-simple / review / button-fix sessions

Three sessions, exported by [`tools/export_recent_finalization.py`](tools/export_recent_finalization.py)
from their nine supplied run envelopes plus the local session JSONLs:

- **Dead-simple final UX pass** (session `f6f2895b-748e-4576-904e-b3783efcb5dd`) — [prompts](prompts/08_dead_simple_final_pass.md) (4 turns) · [run record](runs/08-dead-simple-final-pass.json) · [transcript](transcripts/11-dead-simple-final-pass.md). Total reported: **94 turns**, **$9.670542**. All four envelopes ended `aborted_streaming` (attempt 1) or `error_max_turns` (attempts 2–4) — none is a success terminal state. Commit `5427c9f` ("feat: make final case obvious in thirty seconds") is the verifiable output.
- **Independent review of `5427c9f`** (session `b6b433a2-7137-4bbc-bc5b-cf9affb838e0`) — [prompts](prompts/09_independent_review_dead_simple.md) (2 turns) · [run record](runs/09-independent-review-dead-simple.json) · [transcript](transcripts/12-independent-review-dead-simple.md). Attempt 1 ended `error_max_turns`; attempt 2 completed (`subtype: success`) and returned a verbatim **PASS** verdict with one self-reported MEDIUM verification gap (it did not itself run `make test`) and a LOW finding that `.nojekyll` was absent at review time. Total reported: **12 turns**, **$2.1615411**.
- **"Run the automation" button-fix** (session `800ed7d8-9ce4-4d26-8678-77fe46df870a`) — [prompts](prompts/10_run_button_fix.md) (2 turns) · [run record](runs/10-run-button-fix.json) · [transcript](transcripts/13-run-button-fix.md). Both envelopes ended `error_max_turns` — not a success terminal state. Commit `554126e` ("fix: make automation result unmistakable") is the verifiable output, separately verified by `make test` and browser interaction (see `BUILD_LOG.md`).

Grand total across the three sessions: **128 reported turns**, **$14.062860899999999**. Deterministic hashes for
every artifact from this export: [`recent_finalization_manifest.json`](recent_finalization_manifest.json).

The final test/browser result is recorded in `BUILD_LOG.md` after execution rather than predicted here. This candidate is prepared locally; these logs do not claim it has been published beyond what `BUILD_LOG.md` states.

## Sanitization policy

Raw local session files are not shipped because they can contain hidden reasoning/signature payloads, startup attachments, connector inventories, absolute machine context, identity data, and repeated source dumps irrelevant to evaluation. The exporters:

1. preserve visible prompts/responses, tool names/inputs, and bounded tool results;
2. exclude hidden reasoning/signature blocks and unrelated startup/connector context;
3. normalize home-directory paths and redact identity/credential-shaped strings;
4. truncate large individual fields with an explicit marker;
5. omit `skill_view` result bodies (workstation skill documentation, including personal tooling unrelated to this repository) with an explicit marker, keeping only the skill name, status, and duration;
6. record when child model metadata was not exposed rather than guessing it;
7. label every run envelope's exact `terminal_reason`/`subtype` (e.g. `max_turns`, `aborted_streaming`, `completed`/`success`) rather than inferring an outcome from the commit that followed it.

The raw sources remain local, so `python3 tools/export_hermes_transcripts.py`, `python3 tools/export_final_fable.py`, and `python3 tools/export_recent_finalization.py` reproduce their respective exports/manifests only on the original workstation (elsewhere they fail fast with a clear missing-source error). The committed SHA-256 digests let anyone verify the shipped exports are the ones the exporters produced. This boundary is disclosed rather than presenting sanitized logs as raw logs.
