import tempfile
import unittest
from pathlib import Path

from src.tickets import ticket_stats


class TestTickets(unittest.TestCase):
    def setUp(self):
        self.t = ticket_stats()

    def test_headline_arithmetic(self):
        self.assertEqual(self.t["n_tickets"], 140)
        self.assertEqual(self.t["total_minutes"], 4230)
        self.assertEqual(self.t["total_hours"], 70.5)
        self.assertEqual(self.t["hours_per_week"], 5.48)

    def test_claim_vs_measurement(self):
        self.assertEqual(self.t["measured_vs_claimed_pct"], 13.7)
        self.assertEqual(self.t["claim_multiple_all"], 7.3)
        self.assertEqual(self.t["claim_multiple_like_for_like"], 8.1)

    def test_category_split(self):
        cats = {c["category"]: c for c in self.t["by_category"]}
        self.assertEqual(cats["Thumbnail re-upload"]["n"], 63)
        self.assertEqual(cats["Thumbnail re-upload"]["minutes"], 1365)
        self.assertEqual(cats["Tax form (W-9/W-8)"]["n"], 36)
        self.assertEqual(cats["Tax form (W-9/W-8)"]["minutes"], 1555)
        self.assertEqual(cats["Payout question"]["minutes"], 875)

    def test_data_quality_flags(self):
        self.assertEqual(self.t["blank_assignee"],
                         ["TCK-1013", "TCK-1038", "TCK-1068", "TCK-1100"])
        self.assertEqual(self.t["open_at_quarter_end"], ["TCK-1127", "TCK-1128"])
        self.assertEqual(self.t["date_min"], "2026-01-02")
        self.assertEqual(self.t["date_max"], "2026-03-31")

    def test_wrong_schema_fails_loudly(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("X,Y\n1,2\n")
        with self.assertRaises(ValueError) as ctx:
            ticket_stats(f.name)
        self.assertIn("Missing columns", str(ctx.exception))
        Path(f.name).unlink()

    def test_fresh_file_recomputes(self):
        rows = (
            "Ticket_ID,Date,Category,Submitted_By,Assigned_To,Handle_Minutes,Status\n"
            "T-1,2026-01-05,Foo,a,ops,30,Closed\n"
            "T-2,2026-01-06,Foo,b,ops,30,Open\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(rows)
        t = ticket_stats(f.name)
        self.assertEqual(t["n_tickets"], 2)
        self.assertEqual(t["total_minutes"], 60)
        self.assertEqual(t["open_at_quarter_end"], ["T-2"])
        Path(f.name).unlink()


if __name__ == "__main__":
    unittest.main()
