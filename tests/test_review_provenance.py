import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "index.html"
README = ROOT / "README.md"
GUIDE = ROOT / "REVIEW_GUIDE.md"
LOGS = ROOT / "llm_logs"
MANIFEST = LOGS / "hermes_manifest.json"


class TestReviewerRoute(unittest.TestCase):
    def test_review_guide_has_ordered_five_minute_route_and_proof(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("5-minute reviewer route", text)
        actions = [
            "Open the live site",
            "Read the three decisions",
            "Run baseline",
            "Inspect one exception",
            "Inject orphan",
            "Export queue",
            "Inspect AI/process logs",
        ]
        positions = [text.index(action) for action in actions]
        self.assertEqual(positions, sorted(positions))
        self.assertGreaterEqual(text.count("**Proves:**"), len(actions))
        self.assertIn("Deliberately out of scope", text)
        self.assertIn("real operational exports were not supplied", text.lower())

    def test_review_guide_is_prominently_linked(self):
        readme = README.read_text(encoding="utf-8")[:1800]
        site = SITE.read_text(encoding="utf-8")
        self.assertIn("REVIEW_GUIDE.md", readme)
        self.assertIn("REVIEW_GUIDE.md", site)
        self.assertIn("5-minute review", site)


class TestDeliverableThreeContract(unittest.TestCase):
    def test_guided_sequence_and_executive_explainer_are_explicit(self):
        html = SITE.read_text(encoding="utf-8")
        for phrase in (
            "1 Understand",
            "2 Run baseline",
            "3 Break it",
            "4 Export queue",
            "Why this workflow",
            "What goes in",
            "What Run does",
            "How to read the result",
            "Operational output",
        ):
            self.assertIn(phrase, html)

    def test_fixture_facts_and_truth_boundaries_are_exact(self):
        html = SITE.read_text(encoding="utf-8")
        for phrase in (
            "27 CRM rows",
            "27 invoice rows",
            "40 payout rows",
            "28 deal IDs",
            "20 / 28",
            "71.4%",
            "8 evidence-backed findings",
            "~3 analyst-days/month is reported, not measured",
            "$4.2M/qtr brand revenue",
            "REAL OPERATIONAL EXPORTS WERE NOT SUPPLIED",
        ):
            self.assertIn(phrase, html)

    def test_demo_has_progression_drilldown_conservation_and_output(self):
        html = SITE.read_text(encoding="utf-8")
        for token in (
            'id="demo-progress"',
            'id="input-panel"',
            'id="output-panel"',
            'id="exception-detail"',
            'id="run-recon"',
            'id="inject-orphan"',
            'id="export-exceptions"',
            "Conservation",
            "Disposition",
            "CSV review queue",
        ):
            self.assertIn(token, html)


class TestHermesProvenance(unittest.TestCase):
    def test_manifest_lists_verified_delegations_and_hashes(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        ids = {item["delegation_id"] for item in manifest["delegations"]}
        self.assertEqual(ids, {"deleg_d02432f8", "deleg_d79665c8", "deleg_c2c5d5b7"})
        for item in manifest["delegations"]:
            self.assertEqual(item["child_model_metadata"], "not exposed by delegation transcript")
            path = ROOT / item["transcript"]
            self.assertTrue(path.is_file())
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(item["sha256"], digest)
        self.assertEqual(manifest["orchestrator"]["model"], "gpt-5.6-sol")
        self.assertEqual(manifest["orchestrator"]["provider"], "openai-codex")

    def test_logs_record_adaptations_as_failures_not_model_successes(self):
        text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(LOGS.rglob("*")) if path.is_file()
        )
        self.assertIn("Expired", text)
        self.assertIn("Codex CLI", text)
        self.assertIn("command not found", text)
        self.assertIn("not a model success", text)
        self.assertIn("579db2b57a89b67889f2341d82dd13d9956cd405", text)
        self.assertIn("ef5d2f7b89aaa3c8b5beee67b0059a6c55b3246a", text)
        self.assertIn("69 tests", text)
        self.assertIn("browser", text.lower())

    def test_new_public_process_files_have_no_private_paths_or_identity_leaks(self):
        paths = [GUIDE, ROOT / "BUILD_LOG.md", LOGS / "README.md", MANIFEST]
        paths += list((LOGS / "prompts").glob("06*"))
        paths += list((LOGS / "runs").glob("06*"))
        paths += list((LOGS / "transcripts").glob("0[6-8]*"))
        paths += [ROOT / "tools" / "export_hermes_transcripts.py"]
        combined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)
        banned = (
            "/Users/cb/", "/Users/vo2group/", "/home/cb/", "charles.bernard@", "VO2 GROUP",
            "api_key=", "password=", "secret=", "token=",
        )
        for value in banned:
            self.assertNotIn(value, combined)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{12,}")
        self.assertNotRegex(combined, r"(?i)bearer\s+[A-Za-z0-9._-]{12,}")


if __name__ == "__main__":
    unittest.main()
