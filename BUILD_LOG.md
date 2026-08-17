# Build log

All times CEST. This log records real work only; no timestamps are backfilled.

## 2026-08-14

### 23:40 — Case intake and repository start
- Received the Valis Northwind case bundle and delivery instructions.
- Read the assignment, CEO context/questions, all source files, and the Valis-specific interview context.
- Initialized a local repository under Charles Bernard's personal workspace and committed the untouched synthetic dataset.
- Decision: keep the remote unpublished until Charles reviews; no autonomous push or public sharing.

### 23:42 — Quality bar locked
*(Correction: this entry was originally headed "23:55", but commit `6b73b1f` containing it was made at 23:42. Relabeled to the verifiable commit time; content unchanged. Logged per the no-backfill rule.)*
- Selected a Gauntlet Loop: independent build and critic passes against running output, tests, and source citations.
- Defined the submission as a trust engine, not another dashboard.
- Dirty-data flags identified before implementation:
  1. P&L SaaS subtotal includes two $7,500 Amplitude lines; duplication is suspected but invoice is unavailable.
  2. Salesforce's $12,000 Q1 posting conflicts with a later $60,000 annual renewal; periods may differ and cannot be silently normalized.
  3. May 1 headcount roster says REQ-114 approved, superseded by a June 10/11 Sales freeze.
  4. Support's stated 40 hours/week is a qualitative estimate contradicted by the recorded Q1 ticket workload.
  5. Brand-revenue reconciliation is the strongest documented recurring pain, but the three underlying operational exports are absent.
- Decision: preserve uncertainty explicitly and prohibit invented invoice/source-system evidence.

### 23:50 — Ground truth verified by computation (Fable session)
- Recomputed the P&L SaaS block from `pnl_q1_2026.csv`: 15 line items sum to exactly $81,000 (matches stated subtotal, row 24). Adjusted for one suspected Amplitude duplicate: $73,500.
- Recomputed support load from `support_tickets_q1_2026.csv`: 140 tickets, 4,230 handle-minutes = 70.5 h/quarter = 5.48 h/week over the 90-day quarter — 13.7% of the 40 h/week claimed in #ops (May 6). Claim is refuted by the company's own log.
- Cross-check that decides the automation pick: the brand-deal reconciliation (~3 days/month ≈ 72 h/quarter, corroborated 6× across #finance, finance review, leadership sync) consumes more time than the entire measured support queue (70.5 h/quarter).
  *(Correction, 2026-08-16: "corroborated 6×" was the mid-build tally when this entry was written. The finished citation store carries seven corroborations — `recon.pain_corroborated` in `evidence/citations.json`, machine-verified by `ask.py check` — which is the count README and the site state. The original text is preserved per the no-backfill rule.)*
- Launched the independent Opus ground-truth audit (fresh context, read-only, prompt in `llm_logs/prompts/02_opus_ground_truth.md`) to run in parallel with the build; its verbatim output will be reconciled against my answers before finalization.

## 2026-08-15

### 00:33 — First complete build verified
- Ran `make clean && make build && make test`: 86/86 citations verified; reconciliation demo processed 28 synthetic fixture deals, auto-cleared 20 and emitted 8 evidence-backed exceptions; conservation tied out; 39/39 tests passed.
- Committed the build as four reviewable units: evidence-backed CEO answers, reconciliation automation, test suite, and executive/audit documentation.

### 00:38 — Independent gauntlet verdicts
- Fresh-context Claude Opus 5 critic: **PASS, 87/100**, zero BLOCKER/HIGH defects.
- Fresh-context Claude Fable 5 critic: **PASS, 86/100**, zero BLOCKER/HIGH defects.
- Both independently re-ran the artifact and identified the same substantive trust defect: fresh-P&L math recomputed correctly, but bundle-specific testimony/citations could leak into fresh-input prose.
- Other defects accepted for closure: missing `fixtures/README.md`, over-broad Q2 citation grouping, financially asymmetric value-number headline, unsourced external product claim, invented check duration, and a dropped accent in Tomás.

### 00:46 — Gauntlet defects closed and re-verified
- Added explicit fresh-input mode: prominent banner, computed-only statements, no bundle testimony/citations/knowledge horizon, dynamic reversal values, and Salesforce output only when present in the supplied file.
- Added two new regression suites covering stale-context leakage and exact Q2 citation scoping.
- Added the authored fixture-provenance document and changed `make clean` to preserve it.
- Reframed the value number into its two financially distinct branches; removed unsourced/invented claims.
- Claude Fable completed most of the targeted revision before the organization hit its monthly spend limit on resume. The limit message is preserved in `llm_logs/runs/05b-fable-revision-resume.json`; remaining verification was executed locally rather than fabricated.
- Ran `make clean && make all && git diff --check`: **86/86 citations, 51/51 tests, reconciliation conservation TIES OUT, zero whitespace errors**.

### 03:42 — Post-fix audits closed a payout conservation hole
- Ran two independent fresh-context audits against exact committed HEAD `2d955659bda40fce499a2daaccc74d2ada34d3c8`. Both exercised the repository; their initial runs hit the 20-turn cap and their resumed sessions produced final verdicts.
- Claude Opus 5: **FAIL, 79/100**. Claude Fable 5: **FAIL, 84/100**. Both identified the stale README test count as a MEDIUM trust defect; Fable also proved a HIGH defect by injecting a payout-only deal ID that disappeared while the engine reported `TIES OUT`.
- Fixed the bounded defects: payout IDs now participate in the disposition union, payout-only rows emit evidence-backed `ORPHAN_PAYOUT`, reporting names both CRM-dollar conservation and orphan-payout coverage, and the data contract documents the category.
- Added five orphan-payout regression tests plus a README-count drift guard; updated the README to the discovered suite count.
- Ran `make clean && make all && git diff --check`: **86/86 citations, 57/57 tests, deterministic generated artifacts, zero whitespace errors**.

## 2026-08-16

### 15:53 CEST — Executive microsite committed (`579db2b`)
- Commit timestamp from `579db2b57a89b67889f2341d82dd13d9956cd405`; no wall time was backfilled.
- Hermes delegation `deleg_d02432f8` implemented the self-contained root site and browser reconciliation; the stage ended with 66 tests passing.
- Local browser verification exercised baseline reconciliation: 20/28 synthetic deal IDs auto-cleared, 8 exception deals/findings, conservation tied out, disposition complete, and no console errors.

### 16:05 CEST — Audit fixes committed (`ef5d2f7`)
- Commit timestamp from `ef5d2f7b89aaa3c8b5beee67b0059a6c55b3246a`; no wall time was backfilled.
- Read-only Hermes delegation `deleg_d79665c8` had returned FAIL 83/100: its browser checks proved baseline/orphan/CSV behavior, but the then-advertised live URL returned 404 and it found a duplicate-ID parity defect plus accessibility/test gaps.
- Claude CLI authentication was checked and returned **Expired**; no new Claude/Fable review occurred. A standalone Codex CLI review attempt returned **command not found**; no Codex CLI worker ran. Both are recorded as failed adaptations, not model successes.
- Hermes delegation `deleg_c2c5d5b7` fixed duplicate CRM-ID rejection, visible failure handling, accessible table naming, and deterministic CSV coverage. The commit ended with 69 tests passing.

### Final thorough pass — sequence after `ef5d2f7` (Hermes Agent)
- Parent runtime disclosed as Hermes Agent orchestration on GPT-5.6-sol via openai-codex; delegated child model metadata was not exposed and is not inferred.
- Redesigned Deliverable 03 around a four-step reviewer journey, added `REVIEW_GUIDE.md`, and exported sanitized Hermes provenance with deterministic SHA-256 manifest entries.
- Final execution results are appended below after `make clean && make all` and browser interaction checks; the local commit follows verification.

### 20:27 CEST — Final verification completed
- Wall time captured directly during verification (`2026-08-16 20:27:11 CEST`); not reconstructed from narrative.
- `make clean && make all`: 86/86 citations verified, deterministic outputs rebuilt, reconciliation baseline 20/28 auto-cleared (71.4%), 8 queued findings, conservation tied out, and **77/77 tests passed**.
- Local browser interaction: baseline → evidence drill-down → orphan injection → CSV export completed through steps 2/3/4; CSV contained the expected quoted header plus 9 findings; orphan row present; zero console/JavaScript errors; zero horizontal overflow at the checked desktop viewport.
- Live route loaded successfully and served the committed pre-final site. The final redesign remains local-only until an explicit push; no push occurred in this pass.
- `git diff --check` and added-line secret/injection scan passed. Sanitized Hermes transcript exports contained no internal-reasoning markers or raw private home paths.

### 20:56 CEST — Authenticated final Fable review and bounded fix chain recorded
- Claude Fable 5 session `9b8063b5-283f-4740-9cad-410fd348d63a` reviewed exact commit `7f75ea21d4588168a3c8f3edac142af1ecf9268d` from fresh context and returned **PASS 91/100**, recommendation GO, with zero BLOCKER/HIGH findings. Review envelope: completed, 30 reported turns, **$5.769933**.
- The same session made only the bounded release-prep fixes it identified: dependency wording, publication-safe review-guide language, the historical 6×/final 7 citation correction, visible `noscript` fallback, and tighter workstation-skill sanitization. Its two continuation envelopes ended `error_max_turns`, not success: 16 reported turns / 15-turn configured limit at **$3.893864**, then 13 reported turns / 12-turn configured limit at **$5.644601000000001**.
- Three-envelope total: **59 reported turns**, **$15.308398000000001**; the two configured fix limits total 27 turns. Terminal outcomes remain explicit rather than being inferred from the valid dirty diff they left behind.
- Located the raw local Claude session JSONL read-only. Exported the exact final-review prompt, a normalized three-envelope record, and a sanitized visible transcript containing all three prompts; hidden thinking/signatures, hooks, connector inventories, absolute home paths, emails, credential-shaped strings, and unrelated workstation skill bodies are excluded. The two fix prompts are therefore normalized in the transcript rather than duplicated raw with their absolute source path. Deterministic SHA-256 hashes live in `llm_logs/fable_final_manifest.json`.
- The final candidate remains a local release-prep commit until explicit human publication; this entry does not claim it is already published.

### 21:01 CEST — Release-prep verification completed
- `make clean && make all`: **86/86 citations verified**, deterministic answer/reconciliation outputs rebuilt, baseline **20/28 auto-cleared (71.4%)**, **8/8 findings**, conservation `TIES OUT`, and **80/80 tests passed**.
- Focused local Chromium script (after correcting its test-only table selector) exercised baseline → evidence drill-down → orphan → CSV: baseline `20 / 28`, `8 / 8`, `TIES OUT`, `COMPLETE`; orphan `20 / 29`, `9 / 9`, visible `BD-DEMO-ORPHAN`; CSV header `deal_id,category,detail,evidence`, nine findings, one orphan row; zero console/page errors.
- `git diff --check`, added-line secret/injection scan, final-log absolute-path/email/credential/hook/thinking/signature/workstation-skill scan, manifest hash/path verification, and byte-identical Fable re-export all passed.
- No push or publication was performed; the release-prep commit remains local for human review.

## 2026-08-17

### 16:18 CEST — Reviewer-friction pass verified
- Re-read the exercise, CEO context/questions, interview coaching state, existing evidence, value worksheet, build history, and the live page before editing.
- Rebuilt the public page around the four requested deliverables, direct CEO answers, a plain-English CFO number, one primary automation action, and a visible timestamped build timeline.
- Replaced unstable public links with relative repository paths and added deterministic local-link coverage.
- Ran `make clean && make all`: **86/86 citations verified**, baseline **20/28 auto-cleared**, **8 findings**, conservation `TIES OUT`, and **84/84 tests passed**.
- Browser review confirmed the four deliverables are visible in the first viewport, the synthetic boundary is explicit, and advanced failure/export controls remain available without dominating the main path.

