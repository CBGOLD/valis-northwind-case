# Review guide

## 5-minute reviewer route

The fastest route is the live page. If it is unavailable, open the root `index.html` directly; both are the same self-contained page — every link on it is a relative path, so it works either way.

1. **Open the live site** — <https://cbgold.github.io/valis-northwind-case/>
   **Proves:** no install, no command, no service dependency — the local-file fallback proves it.

2. **Read "the four things you asked for"** at the top, then the two direct answers below it.
   **Proves:** the real supplied bundle resolves into plain-English answers with confidence, sources, and a next action — not a generic dashboard.

3. **Run the automation** in the Automation section.
   **Proves:** the browser executes the committed stand-in file locally and reproduces the deterministic result: 20 of 28 deals clear automatically; 8 are flagged for review.

4. **Pick one flagged deal** from the review list under "Advanced."
   **Proves:** a flagged item isn't just a red count — it carries a category, a plain-language disagreement, and the exact source rows behind it.

5. **Add a payout with no matching deal** using the stress-test button.
   **Proves:** a payout with nothing behind it cannot disappear behind a false "all clear" — it shows up as a separate, named exception instead.

6. **Export the review list** as CSV.
   **Proves:** the output is a portable list with deal ID, category, disagreement, and evidence — not a ceremonial visualization.

7. **Read the build log and AI disclosure** directly on the page, then open [`llm_logs/`](llm_logs/README.md) and [`BUILD_LOG.md`](BUILD_LOG.md) for the full detail.
   **Proves:** builder, audits, fixes, failed-tool adaptations, and verification are disclosed rather than reconstructed as a success story.

## Deliberately out of scope

- **No production reconciliation result:** real operational exports were not supplied. The fixture and every derived demo rate are brutally labeled synthetic.
- **No measured savings claim:** ~3 analyst-days/month is reported testimony, not telemetry; this artifact does not convert it into invented ROI or hours saved.
- **No deployment/integration claim:** source-system authentication, scheduling, write-back, approvals, ownership/SLA design, and production monitoring require a pilot on the real exports.
- **No claim that fixture exception rates represent Northwind:** the fixture proves mechanics and failure handling only.
- **No autonomous publication:** nothing is pushed or published without explicit human review.

For deeper reproduction, run `make clean && make all`. It needs Python 3.9+ (stdlib only), plus
Node.js for the four browser-parity tests that execute the site's embedded engine. Opening the
website itself requires nothing installed.
