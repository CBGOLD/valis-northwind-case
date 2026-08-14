"""Default paths. Everything resolves relative to the repository root so the
tool can be run from a fresh clone with no configuration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "input" / "Northwind-in-a-box_charles"
PNL = INPUT_DIR / "pnl_q1_2026.csv"
TICKETS = INPUT_DIR / "support_tickets_q1_2026.csv"
ROSTER = INPUT_DIR / "headcount_roster.csv"
EVIDENCE = ROOT / "evidence" / "citations.json"
OUT = ROOT / "out"
FIXTURES = ROOT / "fixtures"

# Everything in the bundle is dated; answers must say when knowledge stops.
BUNDLE_AS_OF = "2026-06-18"  # slack_export.md:3 "Export generated 2026-06-18"
