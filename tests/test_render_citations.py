"""Q2 citation grouping (gauntlet defect: Opus M2 / Fable #3).

The revisit-condition bullet had absorbed the entire open-follow-up citation
list — including pnl_q1_2026.csv:22, the Greenhouse SaaS row, which supports
a follow-through claim and has nothing to do with a pipeline-recovery
trigger. Each rendered block must carry only its own claim's citations.
"""
import unittest

from src import answers as A
from src import render
from src.evidence import load_store


def _refs(store, part):
    return {f"{c['file'].split('/')[-1]}:{c['line']}"
            for c in render._citations_for(store, part)}


class TestQ2CitationScoping(unittest.TestCase):
    def setUp(self):
        self.store = load_store()
        self.q2 = A.q2(self.store)

    def test_revisit_condition_carries_only_its_own_citations(self):
        revisit = next(p for p in self.q2["points"] if p["text"].startswith("Revisit condition"))
        refs = _refs(self.store, revisit)
        self.assertEqual(refs, {"slack_export.md:244"})
        self.assertNotIn("pnl_q1_2026.csv:22", refs)

    def test_followthrough_footnote_keeps_its_own_citations(self):
        fn = self.q2["footnotes"][0]
        refs = _refs(self.store, fn)
        self.assertIn("pnl_q1_2026.csv:22", refs)  # the Greenhouse row belongs HERE
        self.assertIn("leadership_sync_2026-06-11.md:43", refs)

    def test_followups_flag_only_on_followthrough_footnote(self):
        """The defect's root cause: the followups flag on a points bullet
        splices every follow-up citation into that bullet's block."""
        self.assertEqual([p for p in self.q2["points"] if p.get("followups")], [])
        self.assertTrue(self.q2["footnotes"][0].get("followups"))

    def test_rendered_markdown_revisit_block_excludes_greenhouse_row(self):
        md = render.ceo_markdown([self.q2], self.store)
        lines = md.splitlines()
        i = next(idx for idx, line in enumerate(lines)
                 if line.startswith("3. Revisit condition"))
        cit_line = lines[i + 1]
        self.assertTrue(cit_line.strip().startswith("`"),
                        f"expected a citation line under the revisit bullet, got {cit_line!r}")
        self.assertNotIn("pnl_q1_2026.csv:22", cit_line)
        self.assertIn("slack_export.md:244", cit_line)
        self.assertIn("pnl_q1_2026.csv:22", md)  # still cited by the follow-through block


if __name__ == "__main__":
    unittest.main()
