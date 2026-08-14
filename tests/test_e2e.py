import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT,
                          capture_output=True, text=True, timeout=120)


class TestEndToEnd(unittest.TestCase):
    def test_check_passes(self):
        p = run("ask.py", "check")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("0 failed", p.stdout)

    def test_answers_render_and_are_deterministic(self):
        p1 = run("ask.py", "build")
        self.assertEqual(p1.returncode, 0, p1.stdout + p1.stderr)
        blobs1 = {n: (ROOT / "out" / n).read_bytes()
                  for n in ("CEO_ANSWERS.md", "CEO_ANSWERS.html", "AUDIT.md")}
        p2 = run("ask.py", "build")
        self.assertEqual(p2.returncode, 0)
        for n, blob in blobs1.items():
            self.assertEqual(blob, (ROOT / "out" / n).read_bytes(), f"{n} not deterministic")

    def test_headline_answers_present(self):
        run("ask.py", "build")
        md = (ROOT / "out" / "CEO_ANSWERS.md").read_text(encoding="utf-8")
        self.assertIn("$73,500", md)
        self.assertIn("$81,000", md)
        self.assertIn("FROZEN", md)
        self.assertIn("reconciliation first", md)
        audit = (ROOT / "out" / "AUDIT.md").read_text(encoding="utf-8")
        self.assertIn(", 0 failed", audit)
        self.assertNotIn("**FAILED**", audit)

    def test_recon_demo_end_to_end(self):
        p = run("recon.py", "demo")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("TIES OUT", p.stdout)
        summary = (ROOT / "out" / "recon" / "RECON_SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC FIXTURE", summary)
        self.assertIn("Before → after", summary)

    def test_json_mode(self):
        p = run("ask.py", "q1", "--json")
        self.assertEqual(p.returncode, 0)
        import json
        data = json.loads(p.stdout)
        self.assertEqual(data["computed"]["booked_cents"], 8100000)
        self.assertEqual(data["computed"]["adjusted_cents"], 7350000)

    def test_fresh_pnl_flag(self):
        """ask.py q1 --pnl on a variant file changes the computed answer."""
        import tempfile
        rows = (
            "Category,Line Item,Q1_2026_USD,Notes\n"
            "Software & SaaS,OnlyTool,4000,x\n"
            "Software & SaaS,Software & SaaS subtotal,4000,sum\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, dir=ROOT) as f:
            f.write(rows)
            name = f.name
        try:
            p = run("ask.py", "q1", "--pnl", name, "--json")
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
            import json
            data = json.loads(p.stdout)
            self.assertEqual(data["computed"]["booked_cents"], 400000)
            self.assertEqual(data["computed"]["suspected_duplicate_cents"], 0)
        finally:
            Path(name).unlink()


if __name__ == "__main__":
    unittest.main()
