"""Hard-path domain contract: the labs speak café, nothing else.

The 2026-09 re-skin moved the whole hard path (engine, tasks, protocols,
companions) into the neighbourhood-café domain. Cassettes are excluded on
purpose — they pin model responses, not course prose — as is the tutor rule,
whose throwaway examples must stay out-of-domain so the assistant never does
the learner's café work.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"
SESSIONS = ROOT / "sessions"

# Word-boundary terms from the retired pub-trivia cut. No exceptions: even
# internal hit/error strings use domain-neutral names.
STALE_HARDPATH = re.compile(
    r"\b(trivia|quiz|clue|deck|draw_clue|propose_round_spec|score_answer"
    r"|end_round|player|championship|off_limits|theme|play|science|geography"
    r"|literature|spoiler)\b",
    re.I,
)

# `s01-round.jsonl` is a frozen cassette filename, not prose.
ROUND_OK = re.compile(r"\bround\b", re.I)


def hardpath_sources() -> list[Path]:
    files: list[Path] = []
    files.extend(sorted((LABS).glob("*.py")))
    files.extend(sorted((LABS / "cafe_host").glob("*.py")))
    files.extend(sorted((LABS / "reference").glob("*.py")))
    files.extend(sorted((LABS / "evals").glob("*.py")))
    files.extend(sorted(SESSIONS.glob("s??-*/lab.md")))
    files.extend(sorted(SESSIONS.glob("s??-*/companion.md")))
    for name in (
        "README.md",
        "cafe_host/README.md",
        "reference/README.md",
        "cassettes/README.md",
        "PROGRESS.template.md",
        "app.py",
    ):
        files.append(LABS / name)
    return [p for p in files if p.is_file() and "__pycache__" not in p.parts]


class HardPathDomain(unittest.TestCase):
    def test_no_trivia_cut_terms_survive(self):
        for path in hardpath_sources():
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(ROOT))):
                bad = STALE_HARDPATH.findall(text)
                self.assertEqual(bad, [], f"stale hard-path terms: {sorted(set(bad))}")

    def test_round_means_the_cassette_filename_only(self):
        for path in hardpath_sources():
            lines = path.read_text(encoding="utf-8").splitlines()
            with self.subTest(file=str(path.relative_to(ROOT))):
                bad = [
                    line.strip()[:80]
                    for line in lines
                    if ROUND_OK.search(line) and "s01-round" not in line
                ]
                self.assertEqual(bad, [], f"bare 'round' outside s01-round: {bad}")


if __name__ == "__main__":
    unittest.main()
