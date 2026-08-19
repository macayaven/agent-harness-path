#!/usr/bin/env bash
# Publish lessons/videos/*.mp4 to the public CDN bucket.
# Canonical copies remain git LFS. Keep BUCKET in sync with lessons/site_urls.py.
set -euo pipefail

BUCKET="${BUCKET:-macayaven-agent-harness-path-videos}"
# Default project is whatever `gcloud` is configured for. Override with PROJECT=.
if [[ -z "${PROJECT:-}" ]]; then
  PROJECT="$(gcloud config get-value project 2>/dev/null || true)"
fi
if [[ -z "$PROJECT" || "$PROJECT" == "(unset)" ]]; then
  echo "publish_videos.sh: set PROJECT or run: gcloud config set project PROJECT_ID" >&2
  exit 1
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/lessons/videos"

shopt -s nullglob
files=("$SRC"/*.mp4)
if ((${#files[@]} == 0)); then
  echo "publish_videos.sh: no mp4s in $SRC (need Git LFS smudge)" >&2
  exit 1
fi

gcloud storage cp "${files[@]}" "gs://${BUCKET}/" \
  --project="$PROJECT" \
  --cache-control="public, max-age=86400" \
  --content-type=video/mp4

echo "published ${#files[@]} objects to gs://${BUCKET}/"
echo "public base: https://storage.googleapis.com/${BUCKET}/"
