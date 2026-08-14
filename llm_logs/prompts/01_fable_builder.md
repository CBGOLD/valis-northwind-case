# Fable builder brief — Valis / Northwind case

## Goal
Build a submission for the Valis Principal/GTM take-home in this repository that would place in the top 0.1% of candidates while remaining truthful, reproducible, concise, and demonstrably produced within an 8-hour case-study discipline.

The quality bar is not visual polish alone. It is: a skeptical CFO can trace every material claim to an exact source; a CEO understands the answer in 60 seconds; an evaluator can run the artifact on a fresh compatible dataset during a live walkthrough; and the repository transparently shows the AI-native build process.

Read the source brief and synthetic data under `input/Northwind-in-a-box_charles/`. The relevant interview context is summarized below; do not copy unrelated personal/client material into the repository.

## Evaluator and candidate context
- Case grader is likely Anton, Valis GTM lead, ex-McKinsey/Bain, hard time-boxer. He completed the case himself in 6.5 hours.
- Valis evaluates hands-on building with Claude plus business and strategic judgment. Product promise: turn fragmented organizational data into trustworthy CEO answers and finance-verified outcomes.
- Candidate strengths: executive synthesis, deployment strategy, business value, strong AI-native workflow.
- Candidate risk: over-scope and over-narration. The artifact must prove ruthless prioritization, explicit trade-offs, and answer-first communication.
- Candidate differentiator: he runs his own agentic operating system daily; this repo should feel like the smallest credible slice of that operating model, not a generic analyst notebook.

## Required deliverables from the assignment
1. A working ask-with-sources slice answering both CEO questions with exact citations and calibrated confidence:
   - Actual Q1 2026 SaaS spend.
   - Current Sales hiring decision/state/owner.
2. One CFO-grade value number with baseline, arithmetic, exact source rows, and explicit unverified items.
3. One automation that runs end-to-end on this data, produces a before→after number, plus a one-page remote-builder spec with scope, actual data contract, acceptance test, and in/out.
4. Timestamped build log including prompts, files, dead ends, dirty-data judgments, and one-line rationales.
5. LLM chat logs in the deliverables.

## Strategic constraints
- Treat every source as fallible. Reconcile temporal precedence and source authority explicitly.
- Never manufacture missing invoice-level evidence or source-system exports.
- Distinguish booked, adjusted, and verified numbers. The P&L SaaS subtotal has an Amplitude duplicate risk; Salesforce has a period/contract inconsistency. The clean answer may be a bounded or conditional one, not false precision.
- The staffing roster is stale relative to June decisions. Model supersession and ownership.
- The 40-hours/week support claim is contradicted by ticket data; do not use vibes as savings.
- The strongest workflow candidate appears to be monthly brand-deal revenue reconciliation across CRM, invoicing, and payout systems. The bundle lacks the three raw exports, so build a working automation on a clearly labeled synthetic fixture/data contract derived from the documented workflow, or choose a different workflow if you can defend a stronger end-to-end result. Never blur fixture output with observed Northwind actuals.
- Keep the submission self-contained, local-first, and dependency-light. A fresh evaluator should be able to run it in minutes.
- Preserve the untouched input. Never edit source files.
- Do not push, publish, add a remote, email, or use external services. Local git commits are allowed and expected.
- No secrets or unrelated personal/client data in the repo.

## Gauntlet method
Choose the architecture. Divide the work into independently judgeable pieces. For each material piece, use a fresh-context builder/critic loop when possible. Critics must inspect real outputs and test results, not the builder's summary. Keep iterating until critical gaps close.

Concrete bar:
- Decision quality: answer-first, three load-bearing points maximum, explicit confidence and reversal conditions.
- Evidence quality: every number/decision has machine-checkable citations to exact file lines/rows; no dangling or incorrect citations.
- Product quality: one-command run, deterministic outputs, fresh-input test, helpful errors, automated tests.
- Executive quality: mobile/desktop-readable CEO view plus audit appendix; no dashboard sludge.
- Transparency: prompts, model metadata, judgments, time log, and audit findings are included.

## Repository expectations
Create a professional structure with a clear `README.md`, runnable source, tests, output artifacts, decision/audit documentation, builder spec, and `llm_logs/`. Maintain a timestamped `BUILD_LOG.md`. Make several logical local commits so the evolution is visible. Do not fake timestamps or effort.

End by running all tests and the complete build from a clean state. Leave the working tree clean. In your final result, report only: the headline answers, artifact architecture, exact commands run, tests/results, commit list, unresolved caveats, and `FILES:` list.
