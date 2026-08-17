import csv
import io
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "index.html"
README = ROOT / "README.md"
RESULT = ROOT / "out" / "recon" / "result.json"

# Phrases the live page must never lead with (reviewer feedback: "opens with
# opaque language"). Checked against visible copy only (script contents are
# code, not prose, and are excluded).
BANNED_PHRASES = (
    "verify two loose ends",
    "bounded answer",
    "gauntlet",
)


def site_text():
    return SITE.read_text(encoding="utf-8")


def visible_copy():
    """index.html minus its embedded <script> — i.e. what a reviewer reads."""
    return re.sub(r"<script[\s\S]*?</script>", "", site_text())


def run_embedded_javascript(command):
    html = site_text()
    match = re.search(r'<script id="recon-engine">([\s\S]*?)</script>', html)
    if not match:
        raise AssertionError("missing executable recon-engine script")
    completed = subprocess.run(
        ["node", "-e", match.group(1) + "\n" + command],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout


def run_embedded_recon(inject=False):
    output = run_embedded_javascript(
        "const r = NorthwindRecon.reconcile(NorthwindRecon.fixtures(), "
        + ("{injectOrphan:true}" if inject else "{}")
        + "); console.log(JSON.stringify(r));"
    )
    return json.loads(output)


class TestExecutiveMicrosite(unittest.TestCase):
    def test_site_is_single_file_and_self_contained(self):
        html = site_text()
        self.assertRegex(html, r"<!doctype html>")
        self.assertNotRegex(html, r'<(?:script|link|img)[^>]+(?:src|href)=["\']https?://')
        self.assertNotIn("@import", html)
        self.assertNotIn("url(http", html)
        self.assertIn("<style>", html)
        self.assertIn('<script id="recon-engine">', html)

    def test_all_local_links_are_relative_and_resolve_on_disk(self):
        """Feedback: live links 404'd. Fix: prefer relative paths that resolve
        both on GitHub Pages and when index.html is opened directly (no
        network). Every non-anchor, non-http(s) href must point at a file
        that actually exists in the repo."""
        html = site_text()
        hrefs = re.findall(r'href="([^"]+)"', html)
        local = [h for h in hrefs if not h.startswith(("http://", "https://", "#"))]
        self.assertGreater(len(local), 5, "expected several relative proof links")
        for href in local:
            self.assertFalse(href.startswith("/"), f"{href} is not a relative path")
            target = ROOT / href
            self.assertTrue(target.exists(), f"relative link {href} does not resolve to a real file")

    def test_four_deliverables_are_visible_with_plain_labels_and_status(self):
        html = site_text()
        deliverables = re.search(r'<div class="deliverables"[\s\S]*?</div>\s*</div></section>', html)
        self.assertIsNotNone(deliverables, "the four-deliverables scorecard must be present")
        block = deliverables.group(0)
        self.assertEqual(block.count('class="deliverable"'), 4)
        for anchor in ("#answers", "#value", "#automation", "#buildlog"):
            self.assertIn(f'href="{anchor}"', block)
        for phrase in (
            "Two answers, with sources",
            "One number for the CFO",
            "One automation, running",
            "A build log",
        ):
            self.assertIn(phrase, block)
        self.assertGreaterEqual(block.count("status-pill"), 4)
        # This scorecard is the 30-second surface: it must appear before the
        # detailed answers/value/automation sections, not after them.
        self.assertLess(html.index('id="deliverables"'), html.index('id="answers"'))
        self.assertLess(html.index('id="answers"'), html.index('id="value"'))
        self.assertLess(html.index('id="value"'), html.index('id="automation"'))

    def test_two_answers_have_headline_confidence_and_show_proof(self):
        html = site_text()
        for key, headline in (("saas-spend", "$73,500"), ("sales-hiring", "FROZEN")):
            card = re.search(rf'<article[^>]+data-decision="{key}"[\s\S]*?</article>', html)
            self.assertIsNotNone(card, f"missing answer card for {key}")
            block = card.group(0)
            self.assertIn(headline, block)
            self.assertIn("Confidence", block)
            self.assertIn("Next step", block)
            self.assertIn("Show proof", block)
            self.assertIn('class="receipt"', block)
        self.assertIn("$81,000", html)

    def test_value_number_states_baseline_arithmetic_unverified_and_decision(self):
        html = site_text()
        for phrase in (
            "$81,000",
            "$7,500",
            "9.3%",
            "$30,000",
            "What's not verified",
            "The decision this enables",
            "docs/VALUE_NUMBER.md",
        ):
            self.assertIn(phrase, html)

    def test_automation_section_has_one_primary_run_button_and_plain_before_after(self):
        html = site_text()
        automation = re.search(r'<section class="panel" id="automation">[\s\S]*?</section>', html)
        self.assertIsNotNone(automation)
        block = automation.group(0)
        # exactly one primary Run control outside the advanced disclosure
        primary_zone = block[: block.index('class="advanced-toggle"')]
        self.assertEqual(primary_zone.count('id="run-recon"'), 1)
        self.assertNotIn('id="inject-orphan"', primary_zone)
        self.assertNotIn('id="export-exceptions"', primary_zone)
        self.assertIn("Before", block)
        self.assertIn("~3 days a month", block)
        self.assertIn("stand-in file", block.lower())
        # the honest, non-defensive one-sentence explanation of why synthetic data is used
        self.assertIn("weren't in the bundle", block)
        # advanced/secondary controls are present, just demoted
        self.assertIn('id="inject-orphan"', block)
        self.assertIn('id="export-exceptions"', block)
        self.assertIn("Advanced:", block)
        # A completed run must be impossible to miss: reveal/focus results and relabel the button.
        self.assertIn('id="run-results"', block)
        self.assertIn('tabindex="-1"', block)
        self.assertIn("scrollIntoView", html)
        self.assertIn("runResults.focus", html)
        self.assertIn("✓ Ran — run again", html)

    def test_no_prohibited_jargon_in_primary_copy(self):
        copy = visible_copy()
        for phrase in BANNED_PHRASES:
            self.assertNotIn(phrase, copy.lower())
        # "Conservation" / "Disposition" must not appear as bare UI labels
        # (element ids like conservation-state are fine; the label text is not).
        self.assertNotRegex(copy, r">\s*Conservation\s*<")
        self.assertNotRegex(copy, r">\s*Disposition\s*<")

    def test_ai_disclosure_present_and_concise_without_model_theatre(self):
        html = site_text()
        ai_section = re.search(r'<section class="panel" id="ai">[\s\S]*?</section>', html)
        self.assertIsNotNone(ai_section)
        block = ai_section.group(0)
        self.assertIn("Claude", block)
        self.assertIn("llm_logs", block)
        for name in ("Fable", "Hermes", "Opus", "gpt-5", "GPT-5"):
            self.assertNotIn(name, block)
        word_count = len(re.sub(r"<[^>]+>", " ", block).split())
        self.assertLess(word_count, 140, "AI disclosure should stay concise, not turn into a saga")

    def test_build_log_timeline_is_visible_compact_and_timestamped(self):
        html = site_text()
        timeline = re.search(r'<ol class="timeline"[^>]*>([\s\S]*?)</ol>', html)
        self.assertIsNotNone(timeline, "a visible build-log timeline must be embedded in the page")
        items = re.findall(r"<li>.*?</li>", timeline.group(1))
        self.assertGreaterEqual(len(items), 6)
        for item in items:
            self.assertRegex(item, r"<time>[^<]+</time>")
        self.assertIn("BUILD_LOG.md", html)

    def test_browser_reconciliation_matches_python_baseline(self):
        browser = run_embedded_recon()
        python = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(browser["inputs"], {"crm": 27, "invoices": 27, "payouts": 40})
        self.assertEqual(browser["matched"], len(python["cleared"]))
        self.assertEqual(browser["exceptionDeals"], len(python["exception_deals"]))
        self.assertEqual(browser["findings"], len(python["exceptions"]))
        self.assertEqual(browser["taxonomy"], python["by_category"])
        self.assertEqual(browser["disposition"], python["disposition"])
        self.assertEqual(browser["conservation"], {
            "crmTotalCents": python["conservation"]["crm_total_cents"],
            "clearedTotalCents": python["conservation"]["cleared_total_cents"],
            "exceptionCrmTotalCents": python["conservation"]["exception_crm_total_cents"],
            "ok": python["conservation"]["ok"],
            "orphanPayoutCents": python["conservation"]["orphan_payout_cents"],
        })
        self.assertEqual(browser["exceptions"], python["exceptions"])

    def test_browser_reconciliation_rejects_duplicate_crm_deal_id(self):
        output = run_embedded_javascript("""
const data = NorthwindRecon.fixtures();
data.crm.push({...data.crm[0], _line: 999});
try {
  NorthwindRecon.reconcile(data);
  process.exit(2);
} catch (error) {
  console.log(error.message);
}
""")
        self.assertIn("duplicate deal_id BD-2606-01 in CRM export", output)
        self.assertIn("SYNTHETIC_crm_deals_2026-06.csv:999", output)
        self.assertIn('id="run-status"', site_text())

    def test_orphan_injection_is_safe_visible_and_exportable(self):
        html = site_text()
        self.assertIn('id="inject-orphan"', html)
        self.assertIn('id="export-exceptions"', html)
        self.assertIn('id="reset-demo"', html)
        injected = run_embedded_recon(inject=True)
        orphan = [e for e in injected["exceptions"] if e["category"] == "ORPHAN_PAYOUT"]
        self.assertEqual(len(orphan), 1)
        self.assertEqual(orphan[0]["deal_id"], "BD-DEMO-ORPHAN")
        self.assertEqual(injected["conservation"]["orphanPayoutCents"], 500000)
        self.assertTrue(injected["disposition"]["complete"])

    def test_row_evidence_table_has_an_accessible_name(self):
        html = site_text()
        self.assertRegex(
            html,
            r'<h4 id="row-evidence-title">The review list</h4>[\s\S]*?<table aria-labelledby="row-evidence-title">',
        )

    def test_exception_csv_has_header_row_count_and_rfc4180_escaping(self):
        exceptions = [
            {
                "deal_id": "BD-1",
                "category": "TEST",
                "detail": 'comma, quote " and\nnewline',
                "evidence": ["one.csv:2", "two.csv:3"],
            },
            {
                "deal_id": "BD-2",
                "category": "PLAIN",
                "detail": "ordinary",
                "evidence": [],
            },
        ]
        command = "console.log(JSON.stringify(NorthwindRecon.exceptionsCsv({exceptions:" + json.dumps(exceptions) + "})));"
        exported = json.loads(run_embedded_javascript(command))
        rows = list(csv.reader(io.StringIO(exported, newline="")))
        self.assertEqual(rows[0], ["deal_id", "category", "detail", "evidence"])
        self.assertEqual(len(rows) - 1, len(exceptions))
        self.assertEqual(rows[1], ["BD-1", "TEST", 'comma, quote " and\nnewline', "one.csv:2;two.csv:3"])
        self.assertEqual(rows[2], ["BD-2", "PLAIN", "ordinary", ""])
        self.assertIn('"comma, quote "" and\nnewline"', exported)
        self.assertTrue(exported.endswith("\r\n"))

    def test_proof_section_links_to_evidence_with_relative_paths(self):
        html = site_text()
        self.assertIn('id="proof"', html)
        for path in (
            "evidence/citations.json", "out/AUDIT.md", "docs/DECISIONS.md", "REVIEW_GUIDE.md",
        ):
            self.assertIn(f'href="{path}"', html)
        self.assertIn("86 citations", html)
        self.assertIn("86 receipts", html)
        self.assertIn('href="https://github.com/CBGOLD/valis-northwind-case"', html)

    def test_accessibility_print_and_anti_slop_contract(self):
        html = site_text().lower()
        for token in ("@media (prefers-reduced-motion: reduce)", "@media print", "min-height: 44px", "overflow-x: hidden"):
            self.assertIn(token, html)
        for banned in ("linear-gradient", "radial-gradient", "backdrop-filter", "glassmorphism", "lorem ipsum", "box-shadow"):
            self.assertNotIn(banned, html)
        self.assertIn('href="#content"', html)
        self.assertIn('aria-label="primary"', html)
        self.assertIn(':focus-visible', html)


class TestReadmeWebsiteEntryPoint(unittest.TestCase):
    def test_readme_leads_with_live_site_and_zero_command_path(self):
        text = README.read_text(encoding="utf-8")
        start = text[:1600]
        self.assertIn("Start here", start)
        self.assertIn("https://cbgold.github.io/valis-northwind-case/", start)
        self.assertIn("index.html", start)
        self.assertIn("zero-command", start.lower())


if __name__ == "__main__":
    unittest.main()
