## Summary

<!-- What changed and why. One concern per PR when you can. -->

## Checklist

- [ ] `uv run python lessons/build.py` and committed HTML if `lessons/src` changed
- [ ] `uv run python lessons/check_links.py` is clean
- [ ] Touched notebooks execute top-to-bottom; no outputs committed
- [ ] If `labs/` changed: `uv run python -m unittest labs/test_contracts.py` and
      `uv run python labs/run.py --all --replay`
- [ ] SOTA links verified if a SOTA table changed
- [ ] Toys remain a different domain (not a paste-ready production harness)
