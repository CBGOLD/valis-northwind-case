import unittest

from src.evidence import load_store, verify_all, verify_citation


class TestEvidence(unittest.TestCase):
    def test_every_citation_verifies(self):
        ok, fail, report = verify_all()
        failures = [line for line in report if line.startswith("FAIL")]
        self.assertEqual(fail, 0, "dangling/incorrect citations:\n" + "\n".join(failures))
        self.assertGreater(ok, 50, "suspiciously few citations — store not loaded?")

    def test_tampered_quote_is_detected(self):
        bad = {
            "file": "input/Northwind-in-a-box_charles/pnl_q1_2026.csv",
            "line": 24,
            "quote": "Software & SaaS subtotal,99999",
        }
        ok, detail = verify_citation(bad)
        self.assertFalse(ok)
        self.assertIn("quote not found", detail)

    def test_wrong_line_is_detected(self):
        bad = {
            "file": "input/Northwind-in-a-box_charles/pnl_q1_2026.csv",
            "line": 999,
            "quote": "anything",
        }
        ok, detail = verify_citation(bad)
        self.assertFalse(ok)
        self.assertIn("out of range", detail)

    def test_missing_file_is_detected(self):
        ok, detail = verify_citation({"file": "input/nope.csv", "line": 1, "quote": "x"})
        self.assertFalse(ok)
        self.assertIn("missing file", detail)

    def test_all_answer_claim_ids_resolve(self):
        """Every claim id referenced by the answers exists in the store —
        no dangling citations at the answer layer either."""
        from src import answers as A
        store = load_store()
        for ans in (A.q1(store=store), A.q2(store=store), A.workflow(store=store)):
            for part in ans["points"] + ans.get("footnotes", []):
                for cid in part.get("claims", []):
                    self.assertIn(cid, store["claims"], f"dangling claim id {cid} in {ans['id']}")
                for eid in part.get("events", []):
                    self.assertTrue(any(e["id"] == eid for e in store["hiring_events"]),
                                    f"dangling event id {eid} in {ans['id']}")
        for cid in A.value(store=store)["claims"]:
            self.assertIn(cid, store["claims"], f"dangling claim id {cid} in value")


if __name__ == "__main__":
    unittest.main()
