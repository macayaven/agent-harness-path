## Summary

<!-- What changed and why. One concern per PR when you can. -->

## Checklist

- [ ] `uv run python lessons/build.py` and committed HTML if `lessons/src` changed
- [ ] `uv run python lessons/check_links.py` is clean
- [ ] `uv run python lessons/check_links.py --http` if HTML or SOTA URLs changed
- [ ] Touched notebooks execute top-to-bottom; no outputs committed
- [ ] `uv run python lessons/check_sota_urls.py` is clean
- [ ] `uv run python labs/run.py --all --replay` is clean (never `--live`)
