"""Public URL for Video Overviews in generated HTML.

Git LFS under lessons/videos/ is the maintainer archive. Generated HTML points
video hrefs at the GCS replica so ▶ works from a small clone without fetching
mp4s. Keep scripts/publish_videos.sh in sync with VIDEO_CDN_BASE.
"""

VIDEO_CDN_BASE = (
    "https://storage.googleapis.com/macayaven-agent-harness-path-videos"
)


def rewrite_video_hrefs(html: str) -> str:
    return html.replace('href="videos/', f'href="{VIDEO_CDN_BASE}/').replace(
        "href='videos/", f"href='{VIDEO_CDN_BASE}/"
    )
