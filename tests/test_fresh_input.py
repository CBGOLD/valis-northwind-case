"""Fresh-input integrity (gauntlet defect: Fable #1 MEDIUM, Opus demo note).

Any non-default --pnl file must produce computed content only, behind a loud
banner. No bundle vendor, testimony quote, citation target, figure, or date
may leak into fresh-mode output. If Salesforce exists in the fresh file it is
reported as its computed row only — never with bundle contract context.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tests" / "data"
DATADOG = DATA / "fresh_pnl_datadog.csv"              # Datadog/Datadog APM pair + a Salesforce row
NO_SALESFORCE = DATA / "fresh_pnl_no_salesforce.csv"  # Datadog pair only, no Salesforce
DEFAULT_PNL = ROOT / "input" / "Northwind-in-a-box_charles" / "pnl_q1_2026.csv"

# Bundle-only content that must never appear against a fresh file: vendors,
# testimony fragments, citation targets, bundle figures, bundle dates.
STALE = [
    "Amplitude", "90% sure", "90%-suspected", "smells like a double-count",
    "your own finance team", "Maya", "Priya", "CFO", "analyst",
    "slack_export", "pnl_q1_2026", "finance_review", "leadership_sync",
    "$81,000", "$73,500", "$12,000", "$60k", "renewal", "step-up",
    "2026-06-02", "2026-06-18",
]


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=120)


class TestFreshInputQ1(unittest.TestCase):
    def test_banner_and_computed_numbers(self):
        p = run("ask.py", "q1", "--pnl", str(DATADOG))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("FRESH-INPUT MODE", p.stdout)
        for expected in ("$32,000", "$22,000", "$10,000", "Datadog APM"):
            self.assertIn(expected, p.stdout)

    def test_no_stale_vendor_quote_or_citation(self):
        for fixture in (DATADOG, NO_SALESFORCE):
            p = run("ask.py", "q1", "--pnl", str(fixture))
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            for stale in STALE:
                self.assertNotIn(
                    stale, p.stdout,
                    f"stale bundle content {stale!r} leaked into fresh mode for {fixture.name}")

    def test_salesforce_reported_as_computed_row_only(self):
        p = run("ask.py", "q1", "--pnl", str(DATADOG))
        self.assertIn("Salesforce", p.stdout)
        self.assertIn("$9,000", p.stdout)  # this file's number, not the bundle's
        for bundle_context in ("$12,000", "renewal", "signed", "booked-but-unverified",
                               "step-up", "$60k"):
            self.assertNotIn(bundle_context, p.stdout)

    def test_file_without_salesforce_never_mentions_it(self):
        p = run("ask.py", "q1", "--pnl", str(NO_SALESFORCE))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotIn("Salesforce", p.stdout)

    def test_reversal_and_as_of_recomputed_from_file(self):
        p = run("ask.py", "q1", "--pnl", str(NO_SALESFORCE), "--json")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = json.loads(p.stdout)
        self.assertTrue(data["fresh_input"])
        self.assertIsNone(data["as_of"])
        reversal = " ".join(data["reversal"])
        self.assertIn("$18,000", reversal)      # this file's booked total
        self.assertNotIn("$81,000", p.stdout)   # never the bundle's
        self.assertNotIn("Salesforce", p.stdout)

    def test_default_bundle_keeps_testimony_and_citations(self):
        """Guard against over-suppression: the default bundle still carries
        the corroborated testimony and machine-verified citations."""
        p = run("ask.py", "q1")
        self.assertNotIn("FRESH-INPUT MODE", p.stdout)
        self.assertIn("Amplitude", p.stdout)
        self.assertIn("90% sure", p.stdout)
        self.assertIn("slack_export.md", p.stdout)

    def test_explicit_default_path_is_still_bundle_mode(self):
        p = run("ask.py", "q1", "--pnl", str(DEFAULT_PNL))
        self.assertNotIn("FRESH-INPUT MODE", p.stdout)
        self.assertIn("Amplitude", p.stdout)


class TestFreshInputValue(unittest.TestCase):
    def test_value_fresh_mode_suppresses_bundle(self):
        p = run("ask.py", "value", "--pnl", str(NO_SALESFORCE))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("FRESH-INPUT MODE", p.stdout)
        self.assertIn("$8,000", p.stdout)  # this file's suspected duplicate
        for stale in STALE:
            self.assertNotIn(stale, p.stdout,
                             f"stale bundle content {stale!r} leaked into fresh value mode")


if __name__ == "__main__":
    unittest.main()
