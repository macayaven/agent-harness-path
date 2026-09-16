## Summary

<!-- What changed and why. One concern per PR when you can. -->

## Evidence and limits

<!-- Name the checks you ran and any observed limit. Do not paste credentials,
raw chats, participant material, private paths or unpublished asset locations. -->

## Checklist

- [ ] `uv run python -m unittest discover -s tests -v`
- [ ] `uv run python lessons/build.py` produces no generated HTML drift
- [ ] `uv run python lessons/check_links.py`
- [ ] `uv run python lessons/check_sota_urls.py`
- [ ] If lesson/SOTA URLs changed: `uv run python lessons/check_links.py --http`
- [ ] If notebooks changed: touched notebooks execute top-to-bottom and remain output-free
- [ ] If lab code/contracts changed: lab contract tests and `uv run python labs/run.py --all --replay` pass (never `--live` in CI)
- [ ] Generated diagrams were visually inspected if Mermaid or diagram inputs changed
- [ ] Public text contains no learner data, credentials, raw logs or private machine paths
- [ ] Toys remain a different domain (not a paste-ready production harness)
