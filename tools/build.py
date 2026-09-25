#!/usr/bin/env python3
"""Render sessions/*/lesson.md (+ index, study plan) to HTML in place.

Stdlib + the `markdown` package only (uv-managed, see pyproject.toml).
Mermaid fences use committed static SVG with input/asset freshness checks.
Each page also gets a prev/index/next nav bar, top and bottom of <main>.

Course UI layer (design/course-ui): `render()` additionally wraps the body in
presentation-only markup — the spine card built from the lesson header, the
course rail, section wrappers keyed to the arc, and an outline. No wording is
added to or removed from any lesson; every string comes from the .md source or
from PAGES titles. `render_body()` is unchanged so its contracts stay pinned.
"""

import re
import html
import sys
from itertools import count
from pathlib import Path

import markdown

from site_urls import rewrite_overview_href
from static_diagrams import STATIC_LESSONS, static_image

HERE = Path(__file__).resolve().parent  # tools/
ROOT = HERE.parent
SESSIONS = ROOT / "sessions"
TEMPLATE = (HERE / "template.html").read_text(encoding="utf-8")

MD = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])

# python-markdown emits mermaid fences as <pre><code class="language-mermaid">.
MERMAID_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL
)

# Reading order for the prev/next nav bars. Each entry is
# (directory relative to sessions/, SNN slug, output file name).
PAGES = [
    (".", "index", "index.html"),
    ("s01-agent-loop", "S01-agent-loop", "lesson.html"),
    ("s02-golden-evals", "S02-golden-evals", "lesson.html"),
    ("s03-context-engineering", "S03-context-engineering", "lesson.html"),
    ("s04-structured-generation", "S04-structured-generation", "lesson.html"),
    ("s05-consent-gate", "S05-consent-gate", "lesson.html"),
    ("s06-layered-detection", "S06-layered-detection", "lesson.html"),
    ("s07-repair-loop", "S07-repair-loop", "lesson.html"),
    ("s08-observability-replay", "S08-observability-replay", "lesson.html"),
    ("s09-evidence-reports", "S09-evidence-reports", "lesson.html"),
    ("s10-error-analysis", "S10-error-analysis", "lesson.html"),
    ("s11-budgets-routing", "S11-budgets-routing", "lesson.html"),
    ("s12-judge-calibration", "S12-judge-calibration", "lesson.html"),
    ("s13-rebuild-from-memory", "S13-rebuild-from-memory", "lesson.html"),
    ("s14-ship-and-pilot", "S14-ship-and-pilot", "lesson.html"),
    (".", "study-plan", "study-plan.html"),
]
CORE_SESSIONS = 12

# Source-file links (toy.py, lab.md, ...) must not stay clickable in the
# built lesson: the preview server hands them out as plain text, outside
# the marimo / markdown-preview surface the course teaches. Unlink them at
# build time; the .md sources keep their links for GitHub rendering.
SOURCE_HREF_RE = re.compile(
    r'<a\s+href="(?P<target>[^"]+)">(?P<inner>.*?)</a>', re.DOTALL
)


def unlink_source_hrefs(rendered: str) -> str:
    """Replace <a> wrappers around local .py/.md targets with inner HTML."""
    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        if "://" in target or target.startswith(("mailto:", "data:")):
            return match.group(0)
        path = target.split("#", 1)[0].split("?", 1)[0]
        if path.endswith((".py", ".md")):
            return match.group("inner")
        return match.group(0)

    return SOURCE_HREF_RE.sub(replace, rendered)

def page_source(directory: str, slug: str) -> Path:
    if directory == ".":
        return SESSIONS / f"{slug}.md"
    return SESSIONS / directory / "lesson.md"


def rel_href(from_dir: str, to_dir: str, to_file: str) -> str:
    if from_dir == to_dir:
        return to_file
    if from_dir == ".":
        return f"{to_dir}/{to_file}"
    if to_dir == ".":
        return f"../{to_file}"
    return f"../{to_dir}/{to_file}"


def render_body(source: Path, slug: str) -> tuple[str, str, int]:
    """Convert one source file; return (body HTML, H1 title, mermaid count)."""
    MD.reset()
    body = MD.convert(source.read_text(encoding="utf-8"))
    body = re.sub(
        r"(<table>.*?</table>)",
        r'<div class="table-scroll" role="group" aria-label="Scrollable table" tabindex="0">\1</div>',
        body,
        flags=re.S,
    )
    if slug in STATIC_LESSONS:
        indices = count()
        body, n = MERMAID_RE.subn(
            lambda match: static_image(
                slug,
                next(indices),
                html.unescape(match.group(1)),
            ),
            body,
        )
    else:
        n = len(MERMAID_RE.findall(body))
        if n:
            raise ValueError(f'{source.name}: no static diagram configuration')
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", body)
    title = title_match.group(1) if title_match else slug
    return body, title, n


def build_nav(directory: str, order: list[tuple[str, str, str]],
              titles: dict[tuple[str, str], str], *, filename: str | None = None) -> str:
    """Prev/index/next bar. Index gets only the forward link; the last
    lesson gets no next. Link labels are the targets' rendered H1s."""
    keys = [(d, f) for d, _, f in order]
    filename = out_name(directory) if filename is None else filename
    i = keys.index((directory, filename))
    prev_link = index_link = next_link = ""
    if i > 0:
        prev_dir, prev_file = keys[i - 1]
        prev_link = (
            f'<a href="{rel_href(directory, prev_dir, prev_file)}">'
            f"&larr; Prev: {titles[keys[i - 1]]}</a>"
        )
    if (directory, filename) != (".", "index.html"):
        index_link = (
            f'<a href="{rel_href(directory, ".", "index.html")}">Index</a>'
        )
    if i < len(keys) - 1:
        next_dir, next_file = keys[i + 1]
        next_link = (
            f'<a href="{rel_href(directory, next_dir, next_file)}">'
            f"Next: {titles[keys[i + 1]]} &rarr;</a>"
        )
    return (
        '<nav class="lesson-nav">'
        f'<span class="nav-prev">{prev_link}</span>'
        f'<span class="nav-index">{index_link}</span>'
        f'<span class="nav-next">{next_link}</span>'
        "</nav>"
    )


def out_name(directory: str) -> str:
    for d, _, out in PAGES:
        if d == directory:
            return out
    raise ValueError(f"{directory}: not a course page")


# ---------------------------------------------------------------- course UI

# h2 id prefix -> arc role (drives CSS only). Mirrors tests/test_arc.py order.
ARC_ROLES = (
    ("the-hook", "hook"),
    ("the-promise", "promise"),
    ("the-theory-in-depth", "theory"),
    ("build", "build"),
    ("checkpoint", "checkpoint"),
    ("state-of-the-art", "sota"),
    ("annotated-readings", "readings"),
    ("misconceptions", "misconceptions"),
    ("self-check", "selfcheck"),
    ("what-this-unlocks", "unlocks"),
)
H2_RE = re.compile(r'<h2 id="(?P<id>[^"]+)">(?P<label>.*?)</h2>', re.S)
HEADER_P_RE = re.compile(
    r"<p>(?=<strong>(?:Carried in|Today you ship):</strong>)(?P<inner>.*?)</p>", re.S)
FIELD_RE = re.compile(r"<strong>(?P<label>[A-Z][^<:]{1,40}):</strong>")
SPINE_FIELDS = ("Carried in", "Today you ship")


def strip_tags(fragment: str) -> str:
    return re.sub(r"<[^>]+>", "", fragment).strip()


def short_title(title: str) -> str:
    """'S05-consent-gate — The gate …' -> 'The gate …' (display only)."""
    return title.split(" — ", 1)[1] if " — " in title else title


def arc_role(section_id: str) -> str:
    for prefix, role in ARC_ROLES:
        if section_id.startswith(prefix):
            return role
    return "extra"


def header_fields(body: str) -> tuple[dict[str, str], re.Match[str] | None]:
    """Split the lesson header paragraph into {label: inner HTML}, verbatim."""
    match = HEADER_P_RE.search(body)
    if not match:
        return {}, None
    inner = match.group("inner")
    parts = FIELD_RE.split(inner)
    fields: dict[str, str] = {}
    for label, value in zip(parts[1::2], parts[2::2]):
        fields[label] = value.strip()
    return fields, match


def shipped_module(body: str) -> str:
    fields, _ = header_fields(body)
    code = re.search(r"<code>([^<]+)</code>", fields.get("Today you ship", ""))
    return code.group(1) if code else ""


def split_code_lead(value: str) -> tuple[str, str]:
    """'<code>cafe/x.py</code> — rest' -> ('<code>cafe/x.py</code>', 'rest')."""
    match = re.match(r"(<code>[^<]+</code>)\s*(?:—|-)?\s*(.*)", value, re.S)
    return (match.group(1), match.group(2)) if match else ("", value)


def build_rail(directory: str, filename: str, titles) -> str:
    items = []
    lessons = [(d, s, o) for d, s, o in PAGES if s.startswith("S")]
    here = next((i for i, (d, _, o) in enumerate(lessons, 1)
                 if (d, o) == (directory, filename)), 0)
    for i, (d, s, o) in enumerate(lessons, 1):
        label = html.escape(strip_tags(titles[(d, o)]))
        state = ("current" if i == here else "done" if i < here
                 else "optional" if i > CORE_SESSIONS else "ahead")
        current = ' aria-current="page"' if state == "current" else ""
        items.append(
            f'<li class="rail-{state}"><a href="{rel_href(directory, d, o)}" '
            f'title="{label}"{current}><span class="vh">{label}</span></a></li>')
    where = (f'<span class="rail-count">S{here:02d} / {CORE_SESSIONS} core</span>'
             if 0 < here <= CORE_SESSIONS else
             f'<span class="rail-count">S{here:02d} · optional</span>' if here else "")
    return ('<nav class="rail" aria-label="Course progress"><ol>'
            + "".join(items) + "</ol>" + where + "</nav>")


def build_module_strip(ships: list[str], here: int) -> str:
    chips = []
    for i, module in enumerate(ships, 1):
        name = html.escape(module.removeprefix("cafe/").removesuffix(".py"))
        state = "current" if i == here else "done" if i < here else "ahead"
        current = ' aria-current="step"' if state == "current" else ""
        chips.append(f'<li class="chip-{state}"{current}>{name}</li>')
    return ('<div class="strip"><p class="label"><code>cafe/</code></p>'
            '<ol aria-label="The artifact you are growing">'
            + "".join(chips) + "</ol></div>")


def build_spine(fields, next_link: str, strip: str) -> str:
    cells = []
    for label in SPINE_FIELDS:
        if label not in fields:
            continue
        code, rest = split_code_lead(fields[label])
        role = "ship" if label == "Today you ship" else "in"
        cells.append(
            f'<div class="spine-cell spine-{role}"><p class="label">{label}</p>'
            f'<p class="spine-code">{code}</p><p class="spine-text">{rest}</p></div>')
    if next_link:
        cells.append(
            '<div class="spine-cell spine-next"><p class="label">Unlocks next</p>'
            f'<p class="spine-code">{next_link}</p>'
            '<p class="spine-text"><a href="#what-this-unlocks">What this unlocks</a></p></div>')
    return ('<section class="spine" aria-label="Where this session sits">'
            f'<div class="spine-cells">{"".join(cells)}</div>{strip}</section>')


def build_meta(fields) -> tuple[str, str]:
    """Return (lead paragraph, definition list) for the non-spine fields."""
    lead = ""
    rows = []
    for label, value in fields.items():
        if label in SPINE_FIELDS:
            continue
        if label == "What this teaches":
            lead = f'<p class="lead"><strong>{label}:</strong> {value}</p>'
            continue
        rows.append(f"<div><dt>{label}</dt><dd>{value}</dd></div>")
    meta = f'<dl class="meta-grid">{"".join(rows)}</dl>' if rows else ""
    return lead, meta


def build_outline(body: str) -> tuple[str, str]:
    """(aside for wide screens, collapsed details for narrow screens)."""
    heads = [(m.group("id"), strip_tags(m.group("label"))) for m in H2_RE.finditer(body)]
    if len(heads) < 4:
        return "", ""
    links = "".join(f'<li><a href="#{i}">{html.escape(label)}</a></li>'
                    for i, label in heads)
    aside = (f'<aside class="outline" aria-label="On this page">'
             f'<p class="label">On this page</p><ol>{links}</ol></aside>')
    inline = (f'<details class="outline-inline"><summary>On this page</summary>'
              f'<ol>{links}</ol></details>')
    return aside, inline


def wrap_sections(body: str) -> str:
    """Wrap each h2 and its following content in <section data-arc=…>."""
    starts = [m.start() for m in H2_RE.finditer(body)]
    if not starts:
        return body
    pieces = [body[:starts[0]]]
    for a, b in zip(starts, starts[1:] + [len(body)]):
        chunk = body[a:b]
        section_id = H2_RE.match(chunk).group("id")
        trail = ""
        hr = re.search(r"\s*<hr />\s*$", chunk)
        if hr:  # keep the separator, outside the section
            chunk, trail = chunk[:hr.start()], chunk[hr.start():]
        pieces.append(
            f'<section class="arc" data-arc="{arc_role(section_id)}" '
            f'aria-labelledby="{section_id}">{chunk}</section>{trail}')
    return "".join(pieces)


def mark_predict_items(body: str) -> str:
    return re.sub(r"<li>(\s*<strong>Predict)", r'<li data-arc="predict">\1', body)


def code_in_details(body: str) -> str:
    """Raw <details> blocks are not Markdown-processed; render `x` as code."""
    def fix(match: re.Match[str]) -> str:
        return re.sub(r"`([^`<\n]+)`", r"<code>\1</code>", match.group(0))
    return re.sub(r"<details>.*?</details>", fix, body, flags=re.S)


def split_h1(body: str) -> str:
    return re.sub(
        r'(<h1 id="[^"]+">)(S\d\d-[a-z0-9-]+ —)',
        r'\1<span class="h1-slug">\2</span>', body, count=1)


def enhance(body: str, chrome: dict) -> tuple[str, str]:
    """Presentation-only layer. Returns (body, aside outline)."""
    body = code_in_details(mark_predict_items(body))
    # Before the inline outline: that lands right after </h1> and would
    # stop this pattern from matching the index's first paragraph.
    if chrome.get("index_spine"):
        body = re.sub(r"(</h1>\s*<p>.*?</p>)", lambda m: m.group(1) + chrome["index_spine"],
                      body, count=1, flags=re.S)
    fields, match = header_fields(body)
    aside, inline = build_outline(body)
    if match:
        lead, meta = build_meta(fields)
        spine = build_spine(fields, chrome.get("next_link", ""),
                            chrome.get("strip", ""))
        body = body[:match.start()] + spine + lead + meta + inline + body[match.end():]
    elif inline:
        body = re.sub(r"(</h1>)", r"\1" + inline.replace("\\", r"\\"), body, count=1)
    if chrome.get("kicker"):
        body = re.sub(r"(<h1 )", chrome["kicker"] + r"\1", body, count=1)
    return split_h1(wrap_sections(body)), aside


def build_index_spine(titles, ships) -> str:
    lessons = [(d, s, o) for d, s, o in PAGES if s.startswith("S")]
    cards = []
    for i, (d, s, o) in enumerate(lessons, 1):
        title = short_title(titles[(d, o)])
        module = ships.get(s, "")
        optional = i > CORE_SESSIONS
        tag = (f"<code>{html.escape(module)}</code>" if module and not optional
               else '<span class="card-tag">optional</span>' if optional else "")
        cards.append(
            f'<li class="{"card-optional" if optional else "card"}">'
            f'<a href="{rel_href(".", d, o)}"><span class="card-n">S{i:02d}</span>'
            f'{tag}<span class="card-title">{title}</span></a></li>')
    return ('<nav class="index-spine" aria-label="Sessions"><ol>'
            + "".join(cards) + "</ol></nav>")


def render(source: Path, slug: str, out: Path, nav: str,
           chrome: dict | None = None) -> tuple[str, int]:
    body, title, n = render_body(source, slug)
    chrome = chrome or {}
    body, aside = enhance(body, chrome)
    rendered = (
        TEMPLATE.replace("{{ title }}", strip_tags(title))
        .replace("{{ home }}", chrome.get("home", "index.html"))
        .replace("{{ rail }}", chrome.get("rail", ""))
        .replace("{{ outline }}", aside)
        .replace("{{ page_class }}", "page-lesson" if aside else "page-plain")
        .replace("{{ nav }}", nav)
        .replace("{{ body }}", body)
        .replace("{{ source }}", str(source.relative_to(ROOT)))
    )
    return unlink_source_hrefs(rendered), n


def page_chrome(directory, slug, out, titles, bodies, ships) -> dict:
    lessons = [s for _, s, _ in PAGES if s.startswith("S")]
    chrome = {"home": rel_href(directory, ".", "index.html"),
              "rail": build_rail(directory, out, titles)}
    if slug in lessons:
        here = lessons.index(slug) + 1
        core_ships = [ships[s] for s in lessons[:CORE_SESSIONS] if ships.get(s)]
        if here <= CORE_SESSIONS and len(core_ships) == CORE_SESSIONS:
            chrome["strip"] = build_module_strip(core_ships, here)
        keys = [(d, o) for d, _, o in PAGES]
        i = keys.index((directory, out))
        nd, no = keys[i + 1]
        if 'id="what-this-unlocks"' in bodies[slug] and PAGES[i + 1][1].startswith("S"):
            label = f"S{here + 1:02d} — {short_title(titles[(nd, no)])}"
            chrome["next_link"] = f'<a href="{rel_href(directory, nd, no)}">{label}</a>'
        kind = "core path" if here <= CORE_SESSIONS else "optional protocol"
        chrome["kicker"] = f'<p class="kicker">Session {here:02d} · {kind}</p>'
    if slug == "index":
        chrome["index_spine"] = build_index_spine(titles, ships)
    return chrome


def main() -> int:
    for directory, slug, _ in PAGES:
        source = page_source(directory, slug)
        if not source.is_file():
            print(f"build.py: missing source {source.relative_to(ROOT)}",
                  file=sys.stderr)
            return 1
    known = {SESSIONS / d / "lesson.md" for d, _, _ in PAGES if d != "."}
    strays = sorted(p for p in SESSIONS.glob("*/lesson.md") if p not in known)
    if strays:
        print("build.py: lesson sources outside the manifest: "
              + ", ".join(str(p.relative_to(ROOT)) for p in strays),
              file=sys.stderr)
        return 1
    # Titles are needed up front: each page's nav labels its neighbours.
    titles, bodies, ships = {}, {}, {}
    for directory, slug, out in PAGES:
        body, title, _ = render_body(page_source(directory, slug), slug)
        titles[(directory, out)] = title
        bodies[slug] = body
        ships[slug] = shipped_module(body)
    order = [(d, s, o) for d, s, o in PAGES]
    for directory, slug, out in order:
        source = page_source(directory, slug)
        out_path = SESSIONS / directory / out
        html_out, n_mermaid = render(
            source, slug, out_path, build_nav(directory, order, titles, filename=out),
            page_chrome(directory, slug, out, titles, bodies, ships))
        if slug == "index":
            html_out = rewrite_overview_href(html_out)
        if n_mermaid == 0 and slug != "index":
            print(f"build.py: WARNING {source.relative_to(ROOT)}: "
                  "no mermaid diagram found")
        out_path.write_text(html_out, encoding="utf-8")
        print(f"{source.relative_to(ROOT)} -> {out_path.relative_to(ROOT)} "
              f"({n_mermaid} mermaid block(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
