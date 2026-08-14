import json
import tempfile
import unittest
from pathlib import Path

from src.recon.engine import reconcile
from src.recon.fixture import MONTH, generate


def _paths(d):
    d = Path(d)
    return (d / f"SYNTHETIC_crm_deals_{MONTH}.csv",
            d / f"SYNTHETIC_invoices_{MONTH}.csv",
            d / f"SYNTHETIC_payouts_{MONTH}.csv")


def _bytes(d):
    return {p.name: p.read_bytes() for p in sorted(Path(d).iterdir())}


class TestFixture(unittest.TestCase):
    def test_deterministic_generation(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            generate(seed=26, outdir=a)
            generate(seed=26, outdir=b)
            self.assertEqual(_bytes(a), _bytes(b))

    def test_committed_fixture_matches_generator(self):
        """The fixture in fixtures/ is exactly what seed 26 produces — no
        hand-edited rows hiding anywhere."""
        with tempfile.TemporaryDirectory() as tmp:
            generate(seed=26, outdir=tmp)
            fresh = _bytes(tmp)
        committed = _bytes("fixtures")
        for name, blob in fresh.items():
            self.assertIn(name, committed)
            self.assertEqual(blob, committed[name], f"{name} drifted from seed-26 output")


class TestEngineAgainstAnswerKey(unittest.TestCase):
    """The engine never reads the manifest; these tests score it against
    the generator's injected answer key — precision and recall must be 100%."""

    def _score(self, seed):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = generate(seed=seed, outdir=tmp)
            result = reconcile(*_paths(tmp))
        key = manifest["injected_answer_key"]
        found = {}
        for e in result["exceptions"]:
            found.setdefault(e["deal_id"], set()).add(e["category"])
        return key, found, result

    def _assert_perfect(self, key, found, result):
        for deal_id, category in key.items():
            self.assertIn(deal_id, found, f"missed injected defect on {deal_id} ({category})")
            self.assertIn(category, found[deal_id],
                          f"{deal_id}: injected {category}, engine said {found[deal_id]}")
        for deal_id in found:
            self.assertIn(deal_id, key, f"false positive: {deal_id} flagged but clean")
        self.assertTrue(result["conservation"]["ok"], "conservation check broken")

    def test_seed_26_recall_and_precision(self):
        key, found, result = self._score(26)
        self._assert_perfect(key, found, result)
        self.assertEqual(len(result["cleared"]), result["n_deals_seen"] - len(key))

    def test_fresh_seed_generalizes(self):
        """A seed the engine was never tuned on — proves the matcher is not
        fitted to the committed fixture."""
        for seed in (99, 4242):
            key, found, result = self._score(seed)
            self._assert_perfect(key, found, result)

    def test_every_exception_carries_row_evidence(self):
        _, _, result = self._score(26)
        for e in result["exceptions"]:
            self.assertTrue(e["evidence"], f"{e['deal_id']} has no row citations")
            for ref in e["evidence"]:
                name, line = ref.rsplit(":", 1)
                self.assertTrue(name.startswith("SYNTHETIC_"))
                self.assertGreaterEqual(int(line), 2)

    def test_wrong_schema_fails_loudly(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(seed=26, outdir=tmp)
            crm, inv, pay = _paths(tmp)
            bad = Path(tmp) / "bad.csv"
            bad.write_text("a,b\n1,2\n", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                reconcile(bad, inv, pay)
            self.assertIn("schema mismatch", str(ctx.exception))
            self.assertIn("BUILDER_SPEC", str(ctx.exception))

    def test_clean_books_produce_zero_exceptions(self):
        """Hand-built tiny clean dataset: one deal, agreeing everywhere."""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "crm.csv").write_text(
                "deal_id,brand,creator_handle,amount_usd,close_date,stage,owner_rep,creator_split_pct\n"
                "BD-1,BrandX,fx_a,10000,2026-06-05,Closed Won,rep_a,70\n", encoding="utf-8")
            (d / "inv.csv").write_text(
                "invoice_id,deal_id,brand,amount_usd,invoice_date,status\n"
                "INV-1,BD-1,BrandX,10000,2026-06-10,issued\n", encoding="utf-8")
            (d / "pay.csv").write_text(
                "payout_id,deal_id,creator_handle,amount_usd,paid_date\n"
                "PAY-1,BD-1,fx_a,7000,2026-07-01\n", encoding="utf-8")
            result = reconcile(d / "crm.csv", d / "inv.csv", d / "pay.csv")
        self.assertEqual(result["exceptions"], [])
        self.assertEqual(len(result["cleared"]), 1)
        self.assertEqual(result["auto_clear_rate_pct"], 100.0)


if __name__ == "__main__":
    unittest.main()
