# S13 — unaided audit card

This optional activity uses the [authored S13 protocol](../lessons/S13-rebuild-from-memory.html#the-protocol). It has no notebook. Read the protocol before the sitting, then close the browser and assistant. This card is preparation and a place to return afterward, not material to consult while rebuilding.

You need a non-trivial system you own, a defended eval suite, a banked baseline and a predeclared tolerance. S01–S02 give enough vocabulary to read the protocol; carrying it out needs the S02–S12 instrument on your own project, or the trivia host you actually built through the optional hard path. A shipped starter or reference implementation is not evidence that you built a system. Deferring is a valid choice and does not block the twelve-session route.

## Prepare outside the timed sitting

1. Choose one core component and identify its load-bearing invariants. Keep the rest of the project intact.
2. Preserve a clean committed original and its banked suite result. The automatically installed study copy has **no Git history**. If using your completed trivia lab, first copy your completed work into a separate nonsynced local project, version it there and verify its suite. Keep the original student folder intact.
3. Create a separate branch or worktree from that committed target in nonsynced local storage. Verify its path before blanking the target file there. Never blank the only copy of your student work. Write down how you will restore this scratch copy from the saved commit.
4. Record the target, commit, suite command, baseline, tolerance and intended cap before starting. Close original/reference tabs, the assistant and the browser. No `git show`, original core or `labs/reference/` during recall. Allowed aids are the language, standard library and `--help`, as specified by the lesson.

For your completed trivia host, bank and later rerun
`uv run python labs/run.py --all --impl student --replay` from the scratch project
root. Confirm **`impl=student`** in the report and inspect every task result and
skipped/not-implemented notice. The runner's exit status alone is not a passing
audit. `--all` without `--impl student` selects the reference and cannot measure
your rebuild. Keep reference smoke results separate from your own baseline.

## During the sitting

Use a visible **60-minute** timer. Rebuild the core at the same path in the scratch project from a blank file. Mark uncertainty with `# UNSURE`. Record actual start/end times and any interruption or accidental exposure. A peek changes the evidence; it must not disappear from your account. The authored closed-book discipline remains yours; no tool can certify that you avoided other help.

## Return after closing the sitting

1. Save the attempted rebuild before looking at the original. Diff against the banked original and classify every hunk as cosmetic, behavior-preserving or a behavioral gap.
2. Run the full suite against the rebuild. Compare with the baseline and tolerance. A green result does not erase a behavioral gap that the suite missed.
3. Save a forgot-list: what you dropped, why it existed and the one-line retrieval rule. Preserve the diff and `UNSURE` marks as evidence, not a replacement production patch.
4. Restore the original **in the scratch checkout** from the banked commit, or retire the scratch branch/worktree after preserving its audit evidence. Keep the canonical student project unchanged.
5. Record the actual evidence in the guide. Use **Review the audit and plan the delay** only when no unaided sitting is active. Review and restudy the forgot-list, then plan a cold repeat roughly a week later.

Keep a planned date separate from an observed repeat date and actual elapsed delay. Do not submit a second-audit result before doing it. A saved note, passing self-check or assistant response does not certify a rebuild or learning gain.
