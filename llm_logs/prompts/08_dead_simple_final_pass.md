# Claude Sonnet 5 -- dead-simple final UX pass -- prompts

> Exact visible prompt text for every turn of this session, exported read-only from the local Claude session JSONL.
> The heading and this note are export metadata; each fenced block is a complete prompt body.

## Prompt 1

```text
You are doing the true final pass on a high-stakes Valis Principal GTM hiring exercise in this isolated worktree. Inspect the full repository and especially input/Northwind-in-a-box_charles/00_START_HERE.md, CEO_CONTEXT.md, CEO_QUESTIONS.md, the root index.html, README, REVIEW_GUIDE, BUILD_LOG, docs, evidence, tests, and git history before changing anything. The exercise requires four obvious deliverables: (1) working ask-with-sources answering SaaS spend and sales-hiring status with exact citations/confidence; (2) one CFO-grade value number with baseline/arithmetic/sources/unverified items; (3) one automation shipped and running on the supplied data, with a real before→after number and one-page builder spec; (4) a timestamped build log with prompts, files, dead ends, and dirty-data judgments. Interview context: Charles must look like the embedded operator who turns ambiguity into an AI deployment, directs builders, drives adoption, and owns a finance-verified result—not a consultant producing a clever artifact. User feedback after seeing the live page: links out from the live submission produce 404s; timed logs seem to have disappeared; the deliverable is not self-explanatory/intuitive enough; it must be dead simple to use and prove real value easily; remove jargon, weird wording, and AI slop. Current live-page audit confirms the page is technically impressive but reviewer-hostile: it opens with opaque language such as “verify two loose ends”, “bounded answer”, “reconciliation”, “conservation”, and “disposition”; it buries the four requested deliverables; it makes the automation feel like a test harness; the build log is only a link; and the llm_logs live path is actually absent from GitHub Pages/public contents. Redesign and implement a dead-simple, first-time-reviewer experience while preserving all truth, caveats, exact calculations, citations, deterministic browser automation, synthetic-vs-actual boundary, accessibility, no external assets, and existing functionality. Required UX: within 30 seconds the reviewer must see “the four things you asked for” with plain-English labels and status; a simple start-here path; direct CEO answers with a one-click “show proof”; the CFO value case in plain English including baseline, arithmetic, what is unverified, and the business decision it enables; automation framed as “turn three messy files into a short list a finance analyst reviews” with one primary Run button, an instantly understandable before→after outcome, and advanced break/export details secondary; a visible compact timestamped build-log timeline on the page; a visible concise AI/tooling disclosure without model theatre; all links from the live page must resolve publicly (prefer stable relative/public routes, or render content on-page rather than relying on directories GitHub Pages cannot serve). Remove navigation and labels that require decoding, reduce vertical bulk, and aggressively rewrite AI-ish slogans, slash constructions, overclaiming, jargon, and internal test language. The page must explicitly distinguish that the exercise says the automation should run on supplied data while the three operational exports are absent; explain in one sentence why a synthetic fixture is the only honest runnable proof, without making the experience defensive. Add/adjust deterministic tests that assert the four deliverables, visible timestamps, plain-language path, automation parity, no broken local/public paths, no prohibited jargon in primary copy, and current test-count drift. Run make clean && make all, make test if distinct, git diff --check, and a link checker against every href. Commit locally only on feat/dead-simple-final; do not push or modify the main checkout. End with RESULT, FILES, TESTS, LINK_CHECK, COMMIT, and COST-SENSITIVE concise summary.
```

## Prompt 2

```text
Execute now, do not repeat analysis. Implement the redesign in this worktree, prioritize index.html and deterministic tests, keep all existing truthful functionality, run verification, commit locally, and return the required compact result fields. Do not stop before a working committed artifact.
```

## Prompt 3

```text
Implement now in this worktree. Do not analyze further. Write the simplified final page and tests, verify, commit, and return concise RESULT/FILES/TESTS/LINK_CHECK/COMMIT.
```

## Prompt 4

```text
Finish only. Inspect the current diff you wrote, add/update only the necessary deterministic tests and public link handling, run make clean && make all plus href checks and git diff --check, fix failures, commit locally, and return RESULT/FILES/TESTS/LINK_CHECK/COMMIT. No new redesign or analysis.
```
