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

