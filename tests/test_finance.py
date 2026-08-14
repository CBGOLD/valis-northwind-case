import tempfile
import unittest
from pathlib import Path

from src.finance import parse_money_cents, saas_breakdown, usd


class TestSaaS(unittest.TestCase):
    def setUp(self):
        self.s = saas_breakdown()

    def test_booked_ties_to_stated_subtotal(self):
        self.assertEqual(self.s["booked_cents"], 81000_00)
        self.assertEqual(self.s["stated_subtotal_cents"], 81000_00)
        self.assertTrue(self.s["ties_out"])
        self.assertEqual(self.s["n_items"], 15)

    def test_naive_category_sum_is_the_trap(self):
        """A groupby('Category').sum() that keeps the subtotal row doubles
        the answer. The code must expose the trap and avoid it."""
        self.assertEqual(self.s["naive_category_sum_cents"], 162000_00)

    def test_amplitude_duplicate_detected_generically(self):
        pairs = self.s["duplicate_pairs"]
        self.assertEqual(len(pairs), 1)
        vendors = {pairs[0]["keep"]["vendor"], pairs[0]["drop"]["vendor"]}
        self.assertEqual(vendors, {"Amplitude", "Amplitude Analytics"})
        self.assertEqual(self.s["suspected_duplicate_cents"], 7500_00)
        self.assertEqual(self.s["adjusted_cents"], 73500_00)

    def test_money_parser(self):
        self.assertEqual(parse_money_cents("12000"), (1200000, None))
        self.assertEqual(parse_money_cents("1,200.50"), (120050, None))
        self.assertEqual(parse_money_cents(""), (None, "blank"))
        self.assertEqual(parse_money_cents("€1900"), (None, "non-usd-or-unparseable"))

    def test_usd_formatting(self):
        self.assertEqual(usd(7500_00), "$7,500")
        self.assertEqual(usd(120050), "$1,200.50")

    def test_fresh_pnl_recomputes(self):
        """Fresh-input mode: a compatible file with different numbers and no
        duplicates changes the answer — nothing is hardcoded."""
        rows = (
            "Category,Line Item,Q1_2026_USD,Notes\n"
            "Software & SaaS,ToolA,1000,x\n"
            "Software & SaaS,ToolB,2000,y\n"
            "Software & SaaS,Software & SaaS subtotal,3000,sum\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(rows)
        s = saas_breakdown(f.name)
        self.assertEqual(s["booked_cents"], 3000_00)
        self.assertTrue(s["ties_out"])
        self.assertEqual(s["duplicate_pairs"], [])
        self.assertEqual(s["adjusted_cents"], 3000_00)
        Path(f.name).unlink()

    def test_fresh_pnl_duplicate_and_flags(self):
        """Duplicate heuristic and non-USD flag generalize to unseen vendors."""
        rows = (
            "Category,Line Item,Q1_2026_USD,Notes\n"
            "Software & SaaS,Foo,500,analytics\n"
            "Software & SaaS,Foo Platform,500,analytics\n"
            "Software & SaaS,Bar,€99,eur billed\n"
            "Software & SaaS,Software & SaaS subtotal,1000,sum\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write(rows)
        s = saas_breakdown(f.name)
        self.assertEqual(len(s["duplicate_pairs"]), 1)
        self.assertEqual(s["suspected_duplicate_cents"], 500_00)
        self.assertEqual(len(s["flags"]), 1)
        self.assertIn("non-usd-or-unparseable", s["flags"][0])
        Path(f.name).unlink()

    def test_wrong_schema_fails_loudly(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("A,B\n1,2\n")
        with self.assertRaises(ValueError) as ctx:
            saas_breakdown(f.name)
        self.assertIn("Missing columns", str(ctx.exception))
        Path(f.name).unlink()


if __name__ == "__main__":
    unittest.main()
