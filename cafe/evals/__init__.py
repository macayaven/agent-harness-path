"""The S02 golden set: café scenarios, deterministic checkers, naive vs governed.

An eval suite earns its keep by measuring machinery against the status quo, so
this package ships both arms over one golden set. The checkers assert structure,
never taste: an empty run must fail, a hand-built reference run must pass.
"""

from __future__ import annotations

from cafe.evals import checkers, tasks
from cafe.evals.checkers import CHECKERS, evaluate
from cafe.evals.tasks import (
    ARMS,
    GOLDEN,
    Scenario,
    empty_record,
    governed_arm,
    naive_arm,
    naive_vs_governed,
    reference_record,
    score_arm,
)

__all__ = [
    "ARMS",
    "CHECKERS",
    "GOLDEN",
    "Scenario",
    "checkers",
    "empty_record",
    "evaluate",
    "governed_arm",
    "naive_arm",
    "naive_vs_governed",
    "reference_record",
    "score_arm",
    "tasks",
]
