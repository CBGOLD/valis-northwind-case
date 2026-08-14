# Fable targeted revision brief

Implement the gauntlet fixes on the current repository. You may edit and commit locally; do not add a remote or push.

Read the critic verdicts in:
- `llm_logs/runs/03b-opus-gauntlet-verdict.json`
- `llm_logs/runs/04b-fable-gauntlet-verdict.json`

Required fixes:
1. Fresh-input integrity: when `ask.py q1 --pnl PATH` uses any non-default file, emit a prominent fresh-input banner; compute all numbers and reversal text from that file; suppress bundle-specific analyst/CFO testimony, Salesforce claims, and bundle citations that do not apply. If Salesforce exists in the fresh file, report only the computed row without bundle testimony unless it is the default bundle. Add regression tests using the existing Datadog-style fresh fixture plus a fresh file without Salesforce. No stale vendor, quote, or citation may appear.
2. Add `fixtures/README.md` with fixture purpose, generator, seed, explicit synthetic status, missing real exports, what it may and may not support, and replay commands. Ensure `make clean` preserves this authored file while removing generated fixtures/output. Update Makefile as needed and test clean rebuild determinism.
3. Fix Q2 rendering so the revisit-condition bullet gets only its own citations; open-follow-through gets its own citations. Add a regression assertion that `pnl_q1_2026.csv:22` does not appear under the revisit-condition citation block.
4. Strengthen `docs/VALUE_NUMBER.md` headline: distinguish the 90%-suspected accounting-restatement branch from the 10%-possible consolidatable-tooling branch. Remove the unsourced external claim that Amplitude sells separate SKUs and remove the invented "15-minute check." Preserve the honest no-cash-recovery disclosure.
5. Preserve Tomás accent.
6. Run `make clean && make all` and all tests. Add tests for each fixed defect.
7. Update BUILD_LOG.md with the actual critic scores/defects, fixes, and verified test count. Do not invent timestamps.
8. Commit changes in one logical commit titled `fix: close gauntlet trust defects` and leave a clean tree except new reviewer run logs that the outer orchestrator may add.

Do not weaken evidence standards or hide the synthetic/real-data split. Return a concise summary with exact test count and commit SHA.