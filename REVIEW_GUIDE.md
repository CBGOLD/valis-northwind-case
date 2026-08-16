# Review guide

## 5-minute reviewer route

The fastest route is the live page. If it is unavailable, open the root `index.html` directly; both are the same self-contained artifact.

1. **Open the live site** — <https://cbgold.github.io/valis-northwind-case/>
   **Proves:** the submission has a zero-command executive surface; the local-file fallback proves it has no runtime service dependency.

2. **Read the three decisions** at the top: SaaS spend, Sales hiring, and automate-first.
   **Proves:** the real supplied bundle resolves into answer-first decisions with confidence, boundary, and next action—not a generic dashboard.

3. **Run baseline** in Deliverable 03.
   **Proves:** the browser executes the committed synthetic fixture locally and reproduces the deterministic control: 20/28 deal IDs auto-clear (71.4%); 8 evidence-backed findings enter the queue.

4. **Inspect one exception** by selecting an evidence row.
   **Proves:** a finding is not just a red count: it carries a category, a plain-language disagreement, and exact source-row references for review.

5. **Inject orphan** using the safe stress-test control.
   **Proves:** a payout-only deal cannot disappear behind a false tie-out; it becomes a visible `ORPHAN_PAYOUT` while the CRM-scoped conservation equation remains honestly scoped.

6. **Export queue** as CSV.
   **Proves:** the operational output is a portable review queue with deal ID, category, disagreement, and evidence—not a ceremonial visualization.

7. **Inspect AI/process logs** in [`llm_logs/`](llm_logs/README.md) and [`BUILD_LOG.md`](BUILD_LOG.md).
   **Proves:** builder, audit, fixes, failed-tool adaptations, model-role boundaries, commits, and verification are disclosed rather than reconstructed as a success story.

## Deliberately out of scope

- **No production reconciliation result:** real operational exports were not supplied. The fixture and every derived demo rate are brutally labeled synthetic.
- **No measured savings claim:** ~3 analyst-days/month is reported testimony, not telemetry; this artifact does not convert it into invented ROI or hours saved.
- **No deployment/integration claim:** source-system authentication, scheduling, write-back, approvals, ownership/SLA design, and production monitoring require a pilot on the real exports.
- **No claim that fixture exception rates represent Northwind:** the fixture proves mechanics and failure handling only.
- **No autonomous publication:** nothing is pushed or published without explicit human review.

For deeper reproduction, run `make clean && make all`. It needs Python 3.9+ (stdlib only), plus
Node.js for the four browser-parity tests that execute the site's embedded engine. Opening the
website itself requires nothing installed.
