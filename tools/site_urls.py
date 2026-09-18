"""Public URL for the course overview video in generated HTML.

The S00 overview mp4 under sessions/ is the maintainer archive (Git LFS).
Generated HTML points its href at the GCS replica so it streams from a
small clone without fetching the mp4. Publishing to the replica is a
maintainer step outside this repo.
"""

VIDEO_CDN_BASE = (
    "https://storage.googleapis.com/macayaven-agent-harness-path-videos"
)

# The course overview keeps its bucket-object name in the sessions/ root.
OVERVIEW_ASSET = "S00-course-overview.mp4"


def rewrite_overview_href(html: str) -> str:
    """Point the index page's overview link at the CDN replica."""
    return html.replace(
        f'href="{OVERVIEW_ASSET}"', f'href="{VIDEO_CDN_BASE}/{OVERVIEW_ASSET}"')
