"""The arc contract: sessions must form one continuous chain, not twelve restarts.

This is the mechanical guard for boredom-maker B2. A lesson that does not say
what it carried in, or does not hand off to the next slug, breaks the chain.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SESSIONS = ROOT / "sessions"

SLUGS = [
    "S01-agent-loop",
    "S02-golden-evals",
    "S03-context-engineering",
    "S04-structured-generation",
    "S05-consent-gate",
    "S06-layered-detection",
    "S07-repair-loop",
    "S08-observability-replay",
    "S09-evidence-reports",
    "S10-error-analysis",
    "S11-budgets-routing",
    "S12-judge-calibration",
]

# The module each session ships, and therefore what the next one carries in.
SHIPS = {
    "S01-agent-loop": "cafe/loop.py",
    "S02-golden-evals": "cafe/evals",
    "S03-context-engineering": "cafe/context.py",
    "S04-structured-generation": "cafe/schema.py",
    "S05-consent-gate": "cafe/consent.py",
    "S06-layered-detection": "cafe/detect.py",
    "S07-repair-loop": "cafe/repair.py",
    "S08-observability-replay": "cafe/trace.py",
    "S09-evidence-reports": "cafe/report.py",
    "S10-error-analysis": "cafe/taxonomy.py",
    "S11-budgets-routing": "cafe/routing.py",
    "S12-judge-calibration": "cafe/judge.py",
}

REQUIRED_SECTIONS = [
    "## The hook",
    "## The promise",
    "## The theory in depth",
    "## Checkpoint",
    "## State of the art",
    "## Annotated readings",
    "## Misconceptions and failure modes",
    "## Self-check",
    "## What this unlocks",
]

# Domain nouns from the pre-café cut. None may survive in a rebuilt lesson.
STALE_DOMAIN = (
    "trivia", "pub quiz", "clue", "round spec", "mopbot", "concierge",
    "weather bot", "recipe bot",
)


def session_dir(slug: str) -> str:
    return "s" + slug[1:]


def lesson_path(slug: str) -> Path:
    return SESSIONS / session_dir(slug) / "lesson.md"


def rebuilt_slugs() -> list[str]:
    """Only grade lessons that have been migrated to the café/live cut."""
    out = []
    for slug in SLUGS:
        path = lesson_path(slug)
        if path.exists() and "**Today you ship:**" in path.read_text(encoding="utf-8"):
            out.append(slug)
    return out


class Shape(unittest.TestCase):
    def test_every_rebuilt_lesson_has_the_arc_sections_in_order(self):
        for slug in rebuilt_slugs():
            text = lesson_path(slug).read_text(encoding="utf-8")
            with self.subTest(lesson=slug):
                positions = []
                for section in REQUIRED_SECTIONS:
                    index = text.find(section)
                    self.assertNotEqual(index, -1, f"missing section {section!r}")
                    positions.append(index)
                self.assertEqual(
                    positions, sorted(positions), "arc sections are out of order"
                )

    def test_header_declares_what_carries_in_and_what_ships(self):
        for slug in rebuilt_slugs():
            text = lesson_path(slug).read_text(encoding="utf-8")
            with self.subTest(lesson=slug):
                self.assertIn("**Carried in:**", text)
                self.assertIn("**Today you ship:**", text)

    def test_the_promise_appears_before_the_theory(self):
        """The payoff must be stated before the reader is asked to invest."""
        for slug in rebuilt_slugs():
            text = lesson_path(slug).read_text(encoding="utf-8")
            with self.subTest(lesson=slug):
                self.assertLess(text.find("## The promise"), text.find("## The theory in depth"))


class Chain(unittest.TestCase):
    def test_each_lesson_ships_the_module_it_claims(self):
        for slug in rebuilt_slugs():
            text = lesson_path(slug).read_text(encoding="utf-8")
            with self.subTest(lesson=slug):
                self.assertIn(SHIPS[slug], text, "header must name the module it ships")

    def test_carried_in_names_the_previous_module(self):
        rebuilt = rebuilt_slugs()
        for index, slug in enumerate(SLUGS):
            if slug not in rebuilt or index == 0:
                continue
            previous = SLUGS[index - 1]
            if previous not in rebuilt:
                continue
            header = lesson_path(slug).read_text(encoding="utf-8").split("---", 1)[0]
            with self.subTest(lesson=slug):
                self.assertIn(
                    SHIPS[previous], header,
                    f"{slug} must carry in {previous}'s module {SHIPS[previous]}",
                )

    def test_bridge_names_the_next_slug(self):
        rebuilt = rebuilt_slugs()
        for index, slug in enumerate(SLUGS[:-1]):
            if slug not in rebuilt:
                continue
            nxt = SLUGS[index + 1]
            text = lesson_path(slug).read_text(encoding="utf-8")
            unlocks = text.split("## What this unlocks", 1)[1]
            with self.subTest(lesson=slug):
                self.assertIn(
                    f"{session_dir(nxt)}/lesson.html", unlocks,
                    f"{slug} must hand off to {nxt}")

    def test_the_last_core_session_points_at_the_optional_audit(self):
        if "S12-judge-calibration" not in rebuilt_slugs():
            self.skipTest("S12 not rebuilt yet")
        text = lesson_path("S12-judge-calibration").read_text(encoding="utf-8")
        self.assertIn(
            "s13-rebuild-from-memory/lesson.html",
            text.split("## What this unlocks", 1)[1])


class Domain(unittest.TestCase):
    def test_no_pre_cafe_domain_nouns_survive(self):
        for slug in rebuilt_slugs():
            text = lesson_path(slug).read_text(encoding="utf-8").lower()
            for noun in STALE_DOMAIN:
                with self.subTest(lesson=slug, noun=noun):
                    self.assertNotIn(noun, text)

    def test_hands_on_points_at_a_marimo_notebook(self):
        for slug in rebuilt_slugs():
            text = lesson_path(slug).read_text(encoding="utf-8")
            with self.subTest(lesson=slug):
                self.assertIn("](toy.py)", text)
                self.assertNotIn(".ipynb", text)


class Sota(unittest.TestCase):
    def test_every_sota_row_carries_a_source_url(self):
        row = re.compile(r"^\|\s*\[.+?\]\((https?://[^)]+)\)\s*\|", re.M)
        for slug in rebuilt_slugs():
            text = lesson_path(slug).read_text(encoding="utf-8")
            table = text.split("## State of the art", 1)[1].split("\n## ", 1)[0]
            body = [
                line for line in table.splitlines()
                if line.startswith("|") and not line.startswith("|---")
                and "Development" not in line
            ]
            with self.subTest(lesson=slug):
                self.assertTrue(body, "SOTA table is empty")
                for line in body:
                    self.assertRegex(line, row, f"row without a source URL: {line[:60]}")


if __name__ == "__main__":
    unittest.main()
