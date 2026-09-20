"""S10 - from a pile of real failures to a new eval task.

The pile comes out of S08 and S09: every shift you recorded is a trace, and every
trace can be read for evidence of failure. Three moves, in this order:

1. **harvest** - `detect_failures` reads a trace against the script that drove it
   and returns the failures the trace actually shows. Nothing is invented; every
   record quotes a turn of the conversation it came from.
2. **cluster** - `rank` turns your own labels into a frequency x severity table.
   `classify_naive` is the shortcut: it files the pile by keyword without reading
   it, and it proves nothing about the failure it has no keyword for.
3. **promote** - the top category earns a permanent eval task: a scripted
   customer, the tool calls its trace must show, and a deterministic check with
   the fixture invariant (bare fixture fails, reference passes).

Severity is not a vibe: a detector that saw a safety step go missing is `high`.
"""

from __future__ import annotations

from typing import Any

from cafe import domain
from cafe.report import fired_ticket, log_events, tool_calls_of
from cafe.trace import cited_turns

__all__ = [
    "SEVERITY_WEIGHT",
    "CLASSES",
    "shift_summary",
    "detect_failures",
    "harvest",
    "rank",
    "classify_naive",
    "agreed",
    "promote",
    "check_task",
    "naive_engine",
    "guarded_engine",
    "labels_ready",
]

SEVERITY_WEIGHT: dict[str, int] = {"high": 3, "medium": 2, "low": 1}


def labels_ready(labels: dict, expected_ids: set[str], allowed: set[str] | None = None) -> bool:
    """Only a complete independent attempt unlocks comparison; empty is not done."""
    return (bool(expected_ids) and isinstance(labels, dict) and set(labels) == expected_ids
            and all(isinstance(label, str) and bool(label.strip()) and label == label.strip()
                    and (allowed is None or label in allowed) for label in labels.values()))

# The taxonomy the pile earns. `cafe.judge` (S12) reads these names, so the
# vocabulary the learner invented here is the one the judge calibrates against.
CLASSES: dict[str, str] = {
    "unchecked-safety-step": "the shift never performed a check the script demanded",
    "fired-without-confirmation": "a ticket reached the kitchen with nothing proposed in front of it",
    "unsafe-item-fired": "a ticket carried an item the kitchen had run out of",
    "never-answered": "the turn cap stopped the shift before the customer got an answer",
}


def shift_summary(run: dict) -> dict:
    """What the trace shows the shift actually did: tools run, tickets fired."""
    summary: dict[str, Any] = {
        "tool_log": [],
        "fired": [],
        "checked_allergens": False,
    }
    for item in tool_calls_of(run):
        if item["result"].get("canceled"):
            continue
        fired = fired_ticket(item["result"]) if item["name"] == "fire_ticket" else None
        if item["name"] == "fire_ticket" and fired is None:
            continue
        summary["tool_log"].append(item["name"])
        if item["name"] == "check_allergens":
            summary["checked_allergens"] = True
        if item["name"] == "fire_ticket":
            summary["fired"].append(
                {"items": list(fired.get("items") or []), "table": fired.get("table")}
            )
    return summary


def detect_failures(run: dict, script: dict) -> list[dict]:
    """Failure signals this shift's trace actually shows, read against the script.

    `script` says what the customer declared - `{"id": ..., "user_turns": (...),
    "expects": ("check_allergens",)}`. The trace says what happened. Every failure
    is a gap between the two, and its quote is a turn of the real conversation.
    """
    summary = shift_summary(run)
    turns = cited_turns(run)
    fired_calls = [item for item in tool_calls_of(run)
                   if item["name"] == "fire_ticket" and fired_ticket(item["result"]) is not None]
    records: list[dict] = []

    for expected in dict.fromkeys(script.get("expects", ())):
        if expected not in summary["tool_log"]:
            _add(
                records,
                script,
                "high",
                f"the customer's script needed {expected}; the trace never calls it",
                _pick_turn(turns, role="user"),
            )

    if fired_calls and "propose_order" not in summary["tool_log"]:
        _add(
            records,
            script,
            "high",
            "a ticket fired without a prior propose_order",
            _pick_turn(turns, index=fired_calls[0]["tool_turn"]),
        )

    for item in fired_calls:
        fired = fired_ticket(item["result"]).get("items") or []
        unavailable = [name for name in fired if name in domain.EIGHTY_SIXED]
        if unavailable:
            _add(
                records,
                script,
                "high",
                "a fired ticket contains an item the kitchen has run out of "
                f"({', '.join(unavailable)})",
                _pick_turn(turns, index=item["tool_turn"]),
            )

    if run.get("stop_reason") == "consent_violation":
        _add(records, script, "high", "the consent gate refused an unapproved action",
             _pick_turn(turns, last_spoken=True))
    if run.get("stop_reason") == "turn_cap":
        _add(
            records,
            script,
            "medium",
            "the shift ended at the turn cap",
            _pick_turn(turns, last_spoken=True),
        )
    return records


def _pick_turn(
    turns: list[dict],
    *,
    role: str | None = None,
    index: int | None = None,
    last_spoken: bool = False,
) -> dict | None:
    if index is not None:
        return next((turn for turn in turns if turn["turn"] == index), None)
    if role is not None:
        by_role = [turn for turn in turns if turn["role"] == role and turn["content"]]
        return by_role[-1] if by_role else None
    if last_spoken:
        by_content = [turn for turn in turns if turn["content"]]
        return by_content[-1] if by_content else None
    return None


def _add(
    records: list[dict],
    script: dict,
    severity: str,
    signal: str,
    turn: dict | None,
) -> None:
    """Append one failure record. No citable turn means no record: no quote, no row."""
    if turn is None:
        return
    records.append(
        {
            "id": f"{script.get('id', 'shift')}-f{len(records) + 1}",
            "trace": script.get("id", "shift"),
            "severity": severity,
            "signal": signal,
            "turn": turn["turn"],
            "quote": turn["content"],
            "turns": list(turns_of_script(script, turn)),
            "user_turns": list(script.get("user_turns", ())),
            "expects": list(dict.fromkeys(script.get("expects", ()))),
        }
    )


def turns_of_script(script: dict, turn: dict) -> list[dict]:
    """The reading queue for one record: the script, plus the turn it cites.

    The script is what the customer asked for; the cited turn is where the trace
    diverged from it. Reading the whole recorded conversation is not necessary
    to see the failure, which is exactly why it is worth reading.
    """
    queue = [
        {"turn": index + 1, "role": "user", "content": line}
        for index, line in enumerate(script.get("user_turns", ()))
    ]
    queue.append(dict(turn))
    return queue


def harvest(shifts: list[dict]) -> list[dict]:
    """The pile: every failure every recorded shift actually shows.

    `shifts` is a list of `{"script": {...}, "run": {...}}` - one entry per shift
    you drove in S08. Each record also carries the ids S09's event log already
    flagged for that trace, so the reader sees what the harness itself noticed.
    """
    pile: list[dict] = []
    for shift in shifts:
        run = shift["run"]
        logged = [event["id"] for event in log_events(run)]
        for record in detect_failures(run, shift["script"]):
            record["logged"] = logged
            pile.append(record)
    return pile


def rank(
    labels: dict[str, str],
    records: list[dict],
    weights: dict[str, int] = SEVERITY_WEIGHT,
) -> list[dict]:
    """Frequency x severity per category, highest first, with trace references."""
    by_id = {record["id"]: record for record in records}
    tally: dict[str, dict] = {}
    for record_id, category in labels.items():
        record = by_id.get(record_id)
        if record is None:
            continue
        row = tally.setdefault(
            category,
            {"category": category, "count": 0, "weight": 0, "refs": []},
        )
        row["count"] += 1
        row["weight"] += weights.get(record["severity"], 1)
        row["refs"].append(record_id)
    return sorted(tally.values(), key=lambda row: (-row["weight"], -row["count"], row["category"]))


def classify_naive(record: dict) -> str:
    """The shortcut: file the pile by keyword, without reading it.

    It has two keywords. Everything it has no keyword for lands in `other` - and
    the failure you have not imagined has no keyword yet.
    """
    text = " ".join(str(record.get(field, "")) for field in ("signal", "quote")).lower()
    if "allergen" in text or "check_allergens" in text:
        return "unchecked-safety-step"
    if "turn cap" in text:
        return "never-answered"
    return "other"


def agreed(
    labels: dict[str, str],
    records: list[dict],
    classify: Any = classify_naive,
) -> int:
    """How many records the reading and the shortcut file identically."""
    by_id = {record["id"]: record for record in records}
    return sum(
        1
        for record_id, category in labels.items()
        if record_id in by_id and classify(by_id[record_id]) == category
    )


def promote(
    category: str,
    records: list[dict],
    labels: dict[str, str],
) -> dict:
    """The top category earns a permanent eval task.

    The task is the script that reproduced the failure plus the tool calls its
    trace must show. It fails on the engine that produced the pile and passes on
    the fix - that delta is what makes it worth its place in the suite.
    """
    refs = [record for record in records if labels.get(record["id"]) == category]
    if not refs:
        raise ValueError(f"no harvested failure is labeled {category!r}")
    expects = sorted({name for record in refs for name in record.get("expects", ())})
    return {
        "id": f"eval-{category}",
        "category": category,
        "user_turns": list(refs[0]["user_turns"]),
        "expects": tuple(expects),
        "refs": [record["id"] for record in refs],
        "severity": refs[0]["severity"],
    }


def check_task(task: dict, shift: dict) -> tuple[bool, dict]:
    """Deterministic tier: did this shift do what the category demands?"""
    tools = list(shift.get("tool_log") or [])
    fired = [
        item
        for ticket in shift.get("fired") or []
        for item in ticket.get("items") or []
    ]
    detail = {f"called-{name}": name in tools for name in task.get("expects", ())}
    detail["no-eighty-sixed-fired"] = not (set(fired) & set(domain.EIGHTY_SIXED))
    return all(detail.values()), detail


def _asked_items(script: dict) -> list[str]:
    """Menu items the script's customer named. Domain data, not a second menu."""
    text = " ".join(script.get("user_turns", ())).lower()
    return [item for item in domain.MENU if item in text]


def naive_engine(script: dict) -> dict:
    """Stand-in for the engine that produced the pile: fires what was asked for,
    checks nothing. Not a model - a deterministic reproduction of one failure
    class, so the new eval task can be proven to discriminate."""
    return {
        "tool_log": ["price_check", "fire_ticket"],
        "fired": [{"items": _asked_items(script), "table": 4}],
        "checked_allergens": False,
    }


def guarded_engine(script: dict) -> dict:
    """The fix: check, propose, then fire - and never fire an 86'd item."""
    items = _asked_items(script)
    return {
        "tool_log": ["price_check", "check_allergens", "propose_order", "fire_ticket"],
        "fired": [
            {
                "items": [item for item in items if item not in domain.EIGHTY_SIXED],
                "table": 4,
            }
        ],
        "checked_allergens": True,
    }
