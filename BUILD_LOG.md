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

