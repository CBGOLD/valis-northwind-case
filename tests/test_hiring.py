import unittest

from src.hiring import resolve


class TestHiring(unittest.TestCase):
    def setUp(self):
        self.r = resolve()

    def test_state_is_frozen(self):
        self.assertEqual(self.r["state"], "FROZEN")

    def test_dates_announced_and_minuted(self):
        self.assertEqual(self.r["decided_on"], "2026-06-10")
        self.assertEqual(self.r["formalized_on"], "2026-06-11")

    def test_owners(self):
        self.assertIn("Dana Whitfield", self.r["decision_owner"])
        self.assertIn("Priya Raman", self.r["enforcement_owner"])

    def test_roster_superseded(self):
        superseded = {e["id"] for e in self.r["superseded"]}
        self.assertIn("h2_roster_snapshot", superseded)
        self.assertIn("h1_req114_advocacy", superseded)

    def test_no_contradictions_after_decision(self):
        self.assertEqual(self.r["contradictions"], [])

    def test_open_followups_present(self):
        ids = {f["id"] for f in self.r["open_followups"]}
        self.assertIn("f1_late_stage_candidate", ids)
        self.assertIn("f2_greenhouse_unconfirmed", ids)
        self.assertGreaterEqual(len(ids), 3)

    def test_supersession_is_chronology_based(self):
        """A stale-but-newer-looking record must never outrank a later
        decision: the current decision postdates every superseded event."""
        cur = self.r["decision_event"]["date"]
        for e in self.r["superseded"]:
            self.assertLess(e["date"], cur)


if __name__ == "__main__":
    unittest.main()
