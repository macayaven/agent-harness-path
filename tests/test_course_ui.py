"""The course UI must keep the spine visible: index cards, rail and module strip."""

from pathlib import Path
import re
import sys
import unittest

from test_arc import SHIPS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

LESSONS = [(d, s, o) for d, s, o in build.PAGES if s.startswith("S")]


def page(directory: str, out: str) -> str:
    return (ROOT / "sessions" / directory / out).read_text(encoding="utf-8")


class CourseUiTests(unittest.TestCase):
    def test_index_lists_every_session_as_a_card(self):
        index = page(".", "index.html")
        spine = re.search(r'<nav class="index-spine" aria-label="Sessions">(.*?)</nav>',
                          index, re.S)
        self.assertIsNotNone(spine, "index lost its session cards")
        cards = re.findall(r'<li class="(card|card-optional)"><a href="([^"]+)">', spine.group(1))
        self.assertEqual([href for _, href in cards], [f"{d}/{o}" for d, _, o in LESSONS])
        self.assertEqual([kind for kind, _ in cards], ["card"] * 12 + ["card-optional"] * 2)
        for module in SHIPS.values():
            self.assertIn(f"<code>{module}</code>", spine.group(1))

    def test_core_lessons_show_the_module_strip_in_arc_order(self):
        names = [m.removeprefix("cafe/").removesuffix(".py") for m in SHIPS.values()]
        for here, (directory, slug, out) in enumerate(LESSONS[:12], 1):
            html = page(directory, out)
            chips = re.findall(r'<li class="chip-([a-z]+)"[^>]*>([^<]+)</li>', html)
            self.assertEqual([name for _, name in chips], names, slug)
            self.assertEqual([state for state, _ in chips].index("current"), here - 1, slug)
            self.assertIn(f"S{here:02d} / 12 core", html, slug)

    def test_optional_protocols_keep_the_rail_without_a_strip(self):
        for directory, slug, out in LESSONS[12:]:
            html = page(directory, out)
            self.assertIn('aria-current="page"', html, slug)
            self.assertNotIn('class="strip"', html, slug)


if __name__ == "__main__":
    unittest.main()
