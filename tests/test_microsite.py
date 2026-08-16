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
REPO_URL = "https://github.com/CBGOLD/valis-northwind-case"


def site_text():
    return SITE.read_text(encoding="utf-8")


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

    def test_first_surface_has_verdict_and_exactly_three_decisions(self):
        html = site_text()
        hero = re.search(r'<main[^>]*id="decide"[\s\S]*?</section>', html)
        self.assertIsNotNone(hero, "Decide section must be the first main surface")
        block = hero.group(0)
        self.assertEqual(len(re.findall(r'data-decision=', block)), 3)
        for key in ("saas-spend", "sales-hiring", "automate-first"):
            decision = re.search(rf'<article[^>]+data-decision="{key}"[\s\S]*?</article>', block)
            self.assertIsNotNone(decision)
            self.assertIn("Confidence", decision.group(0))
            self.assertIn("Next action", decision.group(0))
        self.assertIn("$73,500", block)
        self.assertIn("FROZEN", block)
        self.assertIn("three-way reconciliation", block)

    def test_real_answers_and_synthetic_demo_are_explicitly_separated(self):
        html = site_text()
        self.assertIn("Real Northwind answers", html)
        self.assertGreaterEqual(html.count("SYNTHETIC DEMO"), 2)
        self.assertIn("NOT Northwind actuals", html)
        self.assertIn("Nothing synthetic feeds the Northwind answers", html)
        self.assertIn("as of 2026-06-18", html)

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
        self.assertIn("Reconciliation failed", site_text())

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

    def test_recon_surface_shows_flow_counts_taxonomy_rows_and_before_after(self):
        html = site_text()
        for phrase in (
            "CRM → invoices → payouts", "Matched", "Exception deals", "Conservation",
            "Exception taxonomy", "Row evidence", "Before", "After",
        ):
            self.assertIn(phrase, html)
        self.assertIn('id="run-recon"', html)
        self.assertIn('aria-live="polite"', html)

    def test_row_evidence_table_has_an_accessible_name(self):
        html = site_text()
        self.assertRegex(html, r'<h3 id="row-evidence-title">Row evidence</h3>[\s\S]*?<table aria-labelledby="row-evidence-title">')

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

    def test_evidence_and_method_views_link_to_repository(self):
        html = site_text()
        for section in ("evidence", "method"):
            self.assertIn(f'id="{section}"', html)
        for path in (
            "evidence/citations.json", "out/AUDIT.md", "docs/DECISIONS.md",
            "docs/BUILDER_SPEC.md", "BUILD_LOG.md",
        ):
            self.assertIn(f'href="{REPO_URL}/blob/main/{path}"', html)
        self.assertIn(f'href="{REPO_URL}/tree/main/llm_logs/"', html)
        self.assertIn(f'href="{REPO_URL}"', html)
        self.assertIn("86 citations", html)

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
