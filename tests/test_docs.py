import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"


def _count_tests(suite):
    total = 0
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            total += _count_tests(item)
        else:
            total += 1
    return total


class TestReadmeTestCountGuard(unittest.TestCase):
    """A post-fix audit found README.md claiming 39 tests while the suite
    actually ran 51 — a stale, machine-checkable number on the front page of
    a trust-first artifact whose whole thesis is that no number ships without
    its own proof. This test discovers the real count the same way `make
    test` does (unittest discovery from tests/, top-level dir = repo root)
    and asserts every README test-count claim matches it exactly, so the
    count can never drift silently again."""

    def test_readme_test_count_matches_unittest_discovery(self):
        suite = unittest.TestLoader().discover(start_dir=str(REPO_ROOT / "tests"), top_level_dir=str(REPO_ROOT))
        actual = _count_tests(suite)

        text = README.read_text(encoding="utf-8")
        mentions = re.findall(r"(\d+)[- ]tests?\b", text, flags=re.IGNORECASE)
        self.assertTrue(mentions, "README.md no longer states a test count — update this guard test")
        for n in mentions:
            self.assertEqual(
                int(n), actual,
                f"README.md claims {n} tests but unittest discovery finds {actual} — update README.md",
            )


if __name__ == "__main__":
    unittest.main()
