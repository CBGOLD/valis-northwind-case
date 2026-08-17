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
FABLE_MANIFEST = LOGS / "fable_final_manifest.json"
FABLE_RUN = LOGS / "runs" / "07-fable-final-review-and-fixes.json"


class TestReviewerRoute(unittest.TestCase):
    def test_review_guide_has_ordered_five_minute_route_and_proof(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("5-minute reviewer route", text)
        actions = [
            "Open the live site",
            "Read \"the four things you asked for\"",
            "Run the automation",
            "Pick one flagged deal",
            "Add a payout with no matching deal",
            "Export the review list",
            "Read the build log and AI disclosure",
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
    """Deliverable 3 (the shipped automation) contract, beyond what
    test_microsite's TestExecutiveMicrosite already covers: the how-it-works
    explainer stays present and demoted under the advanced disclosure."""

    def test_how_it_works_explainer_is_present_under_advanced(self):
        html = SITE.read_text(encoding="utf-8")
        automation = re.search(r'<section class="panel" id="automation">[\s\S]*?</section>', html)
        self.assertIsNotNone(automation)
        block = automation.group(0)
        advanced_start = block.index('class="advanced-toggle"')
        advanced = block[advanced_start:]
        for phrase in ("What goes in", "What Run does", "How to read the result"):
            self.assertIn(phrase, advanced)

    def test_demo_has_progression_drilldown_and_outcome_ids(self):
        html = SITE.read_text(encoding="utf-8")
        for token in (
            'id="demo-progress"',
            'id="input-panel"',
            'id="output-panel"',
            'id="exception-detail"',
            'id="run-recon"',
            'id="inject-orphan"',
            'id="export-exceptions"',
            'id="conservation-state"',
            'id="disposition-state"',
        ):
            self.assertIn(token, html)


class TestHermesProvenance(unittest.TestCase):
    def test_manifest_lists_verified_delegations_and_hashes(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        ids = {item["delegation_id"] for item in manifest["delegations"]}
        self.assertEqual(
            ids,
            {"deleg_d02432f8", "deleg_d79665c8", "deleg_c2c5d5b7", "deleg_5d1fc70f"},
        )
        for item in manifest["delegations"]:
            self.assertEqual(item["child_model_metadata"], "not exposed by delegation transcript")
            path = ROOT / item["transcript"]
            self.assertTrue(path.is_file())
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(item["sha256"], digest)
        self.assertEqual(manifest["orchestrator"]["model"], "gpt-5.6-sol")
        self.assertEqual(manifest["orchestrator"]["provider"], "openai-codex")

    def test_final_fable_manifest_and_three_envelopes_are_exact(self):
        manifest = json.loads(FABLE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["session_id"], "9b8063b5-283f-4740-9cad-410fd348d63a")
        self.assertEqual(manifest["canonical_model"], "claude-fable-5")
        for item in manifest["artifacts"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item["sha256"])

        record = json.loads(FABLE_RUN.read_text(encoding="utf-8"))
        self.assertEqual([run["num_turns"] for run in record["runs"]], [30, 16, 13])
        self.assertEqual(
            [run["terminal_reason"] for run in record["runs"]],
            ["completed", "max_turns", "max_turns"],
        )
        self.assertEqual(
            [run["subtype"] for run in record["runs"]],
            ["success", "error_max_turns", "error_max_turns"],
        )
        self.assertEqual(
            [run["total_cost_usd"] for run in record["runs"]],
            [5.769933, 3.893864, 5.644601000000001],
        )
        self.assertEqual(record["runs"][0]["verdict"], "PASS")
        self.assertEqual(record["runs"][0]["score"], 91)
        self.assertEqual(record["totals"]["reported_num_turns"], 59)
        self.assertEqual(record["totals"]["cost_usd_exact"], "15.308398000000001")

    def test_final_fable_prompt_and_visible_transcript_are_disclosed(self):
        prompt = (LOGS / "prompts" / "07_fable_final_review_and_fixes.md").read_text(encoding="utf-8")
        transcript = (LOGS / "transcripts" / "10-fable-final-review-and-fixes.md").read_text(encoding="utf-8")
        self.assertEqual(prompt.count("```text"), 1)
        self.assertIn("You are the final independent hiring-case critic.", prompt)
        self.assertNotIn("Now switch from read-only critic to bounded revision worker.", prompt)
        self.assertIn("Now switch from read-only critic to bounded revision worker.", transcript)
        self.assertIn("Continue the bounded revision from the current dirty worktree.", transcript)
        self.assertIn("VERDICT: PASS — Score: 91/100", transcript)
        self.assertIn("3 user prompts · 20 assistant text · 57 tool calls · 57 tool results", transcript)

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
        self.assertIn("7f75ea21d4588168a3c8f3edac142af1ecf9268d", text)
        self.assertIn("69 tests", text)
        self.assertIn("iteration budget", text)
        self.assertIn("browser", text.lower())

    def test_new_public_process_files_have_no_private_paths_or_identity_leaks(self):
        paths = [GUIDE, ROOT / "BUILD_LOG.md", LOGS / "README.md", MANIFEST, FABLE_MANIFEST, FABLE_RUN]
        paths += list((LOGS / "prompts").glob("06*"))
        paths += list((LOGS / "runs").glob("06*"))
        paths += list((LOGS / "transcripts").glob("0[6-9]*"))
        paths += [
            LOGS / "prompts" / "07_fable_final_review_and_fixes.md",
            LOGS / "transcripts" / "10-fable-final-review-and-fixes.md",
            ROOT / "tools" / "export_hermes_transcripts.py",
            ROOT / "tools" / "export_final_fable.py",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in paths)
        banned = (
            "/Users/cb/", "/Users/vo2group/", "/home/cb/", "charles.bernard@", "VO2 GROUP",
            "api_key=", "password=", "secret=", "token=",
        )
        for value in banned:
            self.assertNotIn(value, combined)
        self.assertNotRegex(combined, r"sk-[A-Za-z0-9_-]{12,}")
        self.assertNotRegex(combined, r"(?i)bearer\s+[A-Za-z0-9._-]{12,}")
        self.assertNotIn('"type":"thinking"', combined)
        self.assertNotIn('"signature"', combined)

    def test_transcripts_omit_workstation_skill_documentation_bodies(self):
        transcripts = sorted((LOGS / "transcripts").glob("0[6-9]*"))
        self.assertEqual(len(transcripts), 4)
        combined = "\n".join(p.read_text(encoding="utf-8") for p in transcripts)
        self.assertIn("skill documentation body omitted", combined)
        # Personal-tooling skill bodies must never ship; these strings appeared
        # only inside skill_view result bodies before the omission rule.
        for leaked in ("Telegram", "Route short linear answers"):
            self.assertNotIn(leaked, combined)


if __name__ == "__main__":
    unittest.main()
