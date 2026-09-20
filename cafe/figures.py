"""Embed committed notebook figures without marimo's public-file service worker."""

import base64
from pathlib import Path
import re


FIGURE = re.compile(r"(!\[[^\]\n]*\]\()public/diagrams/([A-Za-z0-9_-]+\.svg)(\))")


def embed_figures(markdown: str, notebook_file: str | Path) -> str:
    """Keep the authoring paths and alt text; transport each local SVG inline."""
    directory = Path(notebook_file).resolve().parent / "public" / "diagrams"

    def replace(match):
        svg = (directory / match[2]).read_bytes()
        encoded = base64.b64encode(svg).decode("ascii")
        return f"{match[1]}data:image/svg+xml;base64,{encoded}{match[3]}"

    return FIGURE.sub(replace, markdown)
