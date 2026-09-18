"""Public URL for Video Overviews in generated HTML.

Git LFS session videos under sessions/ are the maintainer archive. Generated
HTML points video hrefs at the GCS replica so ▶ works from a small clone
without fetching mp4s. Publishing to the replica is a maintainer step outside
this repo.
"""
import re

VIDEO_CDN_BASE = (
    "https://storage.googleapis.com/macayaven-agent-harness-path-videos"
)

# The course overview keeps its bucket-object name in the sessions/ root.
OVERVIEW_ASSET = "S00-course-overview.mp4"

# Index and study-plan tables link per-session videos, e.g.
# href="s02-golden-evals/video.mp4".
SESSION_VIDEO_RE = re.compile(
    r'href="(?P<session>s[0-9]{2}-[a-z0-9-]+)/video\.mp4"')


def rewrite_video_hrefs(html: str, cdn_name: str) -> str:
    """Point one page's video at the CDN replica.

    Session pages link a same-directory `video.mp4`; cdn_name is that
    session's bucket object (e.g. S01-agent-loop.mp4). Index tables link
    `<session>/video.mp4`, which maps by directory name. The index links the
    overview asset, which maps by basename.
    """
    html = html.replace(
        'href="video.mp4"', f'href="{VIDEO_CDN_BASE}/{cdn_name}"')
    html = html.replace(
        "href='video.mp4'", f"href='{VIDEO_CDN_BASE}/{cdn_name}'")
    html = SESSION_VIDEO_RE.sub(
        lambda m: f'href="{VIDEO_CDN_BASE}/S{m.group("session")[1:]}.mp4"',
        html)
    html = html.replace(
        f'href="{OVERVIEW_ASSET}"', f'href="{VIDEO_CDN_BASE}/{OVERVIEW_ASSET}"')
    return html
