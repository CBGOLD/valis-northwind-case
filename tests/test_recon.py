import json
import tempfile
import unittest
from pathlib import Path

from src.recon.engine import reconcile, summary_markdown
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


class TestOrphanPayoutRegression(unittest.TestCase):
    """Post-fix regression: src/recon/engine.py used to build all_ids from only
    CRM and invoice deal_ids, so a payout referencing a deal_id absent from both
    was silently dropped from every output while conservation still reported
    TIES OUT. These tests pin the fix: the orphan payout must surface as an
    ORPHAN_PAYOUT exception with exact row evidence, and the run's own
    self-reporting (disposition + conservation) must stay truthful about what
    it does and does not cover."""

    def _books(self, d, extra_payout_row=""):
        d = Path(d)
        (d / "crm.csv").write_text(
            "deal_id,brand,creator_handle,amount_usd,close_date,stage,owner_rep,creator_split_pct\n"
            "BD-1,BrandX,fx_a,10000,2026-06-05,Closed Won,rep_a,70\n", encoding="utf-8")
        (d / "inv.csv").write_text(
            "invoice_id,deal_id,brand,amount_usd,invoice_date,status\n"
            "INV-1,BD-1,BrandX,10000,2026-06-10,issued\n", encoding="utf-8")
        (d / "pay.csv").write_text(
            "payout_id,deal_id,creator_handle,amount_usd,paid_date\n"
            "PAY-1,BD-1,fx_a,7000,2026-07-01\n"
            + extra_payout_row, encoding="utf-8")
        return d / "crm.csv", d / "inv.csv", d / "pay.csv"

    def test_orphan_payout_is_not_silently_dropped(self):
        """A payout row against a deal_id in no other file must be
        dispositioned, not vanish — the exact bug Fable's probe found
        (PAY-2, BD-999, $5,000 against a nonexistent deal)."""
        with tempfile.TemporaryDirectory() as tmp:
            crm, inv, pay = self._books(tmp, extra_payout_row="PAY-2,BD-999,fx_z,5000,2026-07-02\n")
            result = reconcile(crm, inv, pay)

        self.assertIn("BD-999", result["exception_deals"])
        self.assertIn("BD-999", [c["deal_id"] for c in result["cleared"]] + result["exception_deals"])
        orphan = [e for e in result["exceptions"] if e["deal_id"] == "BD-999"]
        self.assertEqual(len(orphan), 1, "BD-999 must produce exactly one exception, not disappear")
        self.assertEqual(orphan[0]["category"], "ORPHAN_PAYOUT")
        self.assertNotIn("BD-999", [c["deal_id"] for c in result["cleared"]])

    def test_orphan_payout_evidence_cites_exact_source_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            crm, inv, pay = self._books(tmp, extra_payout_row="PAY-2,BD-999,fx_z,5000,2026-07-02\n")
            result = reconcile(crm, inv, pay)
            raw_line = Path(pay).read_text(encoding="utf-8").splitlines()[2]  # line 3, 1-indexed

        orphan = next(e for e in result["exceptions"] if e["deal_id"] == "BD-999")
        self.assertEqual(orphan["evidence"], ["pay.csv:3"])
        self.assertEqual(raw_line, "PAY-2,BD-999,fx_z,5000,2026-07-02")
        self.assertIn("$5,000", orphan["detail"])

    def test_disposition_and_conservation_stay_truthful_with_orphan_payout(self):
        """Total disposition must count the orphan deal_id; the CRM-scoped
        conservation figure must stay honest about its own scope (it neither
        breaks nor silently absorbs money that was never in the CRM)."""
        with tempfile.TemporaryDirectory() as tmp:
            crm, inv, pay = self._books(tmp, extra_payout_row="PAY-2,BD-999,fx_z,5000,2026-07-02\n")
            result = reconcile(crm, inv, pay)

        disp = result["disposition"]
        cons = result["conservation"]
        self.assertEqual(disp["n_deal_ids_seen"], 2)  # BD-1 and BD-999
        self.assertTrue(disp["complete"], "every deal_id must be cleared XOR exceptioned")
        self.assertEqual(disp["n_cleared"] + disp["n_exception_deals"], disp["n_deal_ids_seen"])

        # BD-999 never touches the CRM, so it must not distort the CRM-scoped total.
        self.assertEqual(cons["crm_total_cents"], 10000_00)
        self.assertTrue(cons["ok"], "CRM-scoped conservation must still tie for the CRM-side deal")
        self.assertEqual(cons["orphan_payout_cents"], 5000_00)
        self.assertIn("CRM-scoped", cons["scope"])

        summary = summary_markdown(result)
        self.assertIn("ORPHAN_PAYOUT", summary)
        self.assertIn("$5,000 in orphan payouts", summary)
        self.assertIn("Total disposition", summary)
        self.assertIn("COMPLETE", summary)

    def test_no_orphan_payout_keeps_reporting_silent_on_it(self):
        """Conservation/summary must not claim an orphan-payout figure when
        there isn't one — the truthful report is silence, not a fabricated
        zero-value callout line."""
        with tempfile.TemporaryDirectory() as tmp:
            crm, inv, pay = self._books(tmp)
            result = reconcile(crm, inv, pay)

        self.assertEqual(result["conservation"]["orphan_payout_cents"], 0)
        self.assertNotIn("ORPHAN_PAYOUT", [e["category"] for e in result["exceptions"]])
        self.assertNotIn("orphan payouts", summary_markdown(result))

    def test_deal_id_with_invoice_and_payout_but_no_crm_flags_both_categories(self):
        """A deal_id with neither a CRM row but present in both invoices and
        payouts must not let one category mask the other."""
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "crm.csv").write_text(
                "deal_id,brand,creator_handle,amount_usd,close_date,stage,owner_rep,creator_split_pct\n",
                encoding="utf-8")
            (d / "inv.csv").write_text(
                "invoice_id,deal_id,brand,amount_usd,invoice_date,status\n"
                "INV-9,BD-GHOST,BrandZ,2450,2026-06-26,issued\n", encoding="utf-8")
            (d / "pay.csv").write_text(
                "payout_id,deal_id,creator_handle,amount_usd,paid_date\n"
                "PAY-9,BD-GHOST,fx_z,1000,2026-07-05\n", encoding="utf-8")
            result = reconcile(d / "crm.csv", d / "inv.csv", d / "pay.csv")

        cats = {e["category"] for e in result["exceptions"] if e["deal_id"] == "BD-GHOST"}
        self.assertEqual(cats, {"MISSING_IN_CRM", "ORPHAN_PAYOUT"})
        self.assertTrue(result["disposition"]["complete"])


if __name__ == "__main__":
    unittest.main()
