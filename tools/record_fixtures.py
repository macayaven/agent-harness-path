#!/usr/bin/env python3
"""Replay curated real-model comparisons; record replacements into private staging.

These fixtures supplement the authored notebook controls, not model benchmarks.
The notebook's default client and the learner's attempt skeletons stay unchanged.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cafe import consent, domain, repair, report, schema
from cafe.model import _slim, get_client
from cafe.trace import RecordingClient, ReplayClient

CASES = {
    session: ROOT / "sessions" / slug / "recordings/model.jsonl"
    for session, slug in (
        ("s04", "s04-structured-generation"),
        ("s05", "s05-consent-gate"),
        ("s07", "s07-repair-loop"),
        ("s09", "s09-evidence-reports"),
    )
}


class PublicFixtureClient:
    """Keep protocol replies and usage; omit provider routes and reasoning dumps."""

    def __init__(self, client):
        self.client = client
        self.mode = getattr(client, "mode", "wrapped")

    def chat(self, messages, **kwargs):
        body = _slim(self.client.chat(messages, **kwargs))
        body.pop("model", None)
        return body


def run_case(session, client):
    if session == "s04":
        runs = []
        for brief in domain.TICKET_BRIEFS:
            run = schema.ask_ticket_run(client, brief)
            runs.append(run)
            if run["stop_reason"] == "transport_error":
                break  # a client timeout does not prove upstream generation stopped
        return runs
    if session == "s05":
        return consent.run_shift(
            client,
            ["Please propose one espresso for table 1, then wait for my decision."],
            consent.make_responder([("reject", None)]),
        )
    if session == "s07":
        return [
            repair.repair_ticket(
                {"table": table, "items": items}, repair.make_model_generator(client)
            )
            for table, items in (
                (7, ["latte", "tomato toast"]),
                (4, ["latte"]),
                (5, ["croissant"]),
                (6, ["orange juice"]),
            )
        ]
    if session == "s09":
        return consent.run_shift(
            client,
            [
                "Hi, I'm allergic to milk. Does the croissant have milk?",
                "Then get me an espresso and tomato toast.",
                "Nothing else, thanks.",
            ],
            consent.make_responder([("approve", None)]),
        )
    raise ValueError(session)


def admission_errors(session, result):
    """Fixture selection criteria, never an absolute live-model quality assertion."""
    errors = []
    if session == "s04":
        if len(result) != 3:
            return ["all three briefs must finish without a transport failure"]
        for run, (table, items) in zip(result[:2], (
            (4, ["latte", "tomato toast"]),
            (2, ["chocolate croissant", "chocolate croissant", "orange juice"]),
        )):
            ticket = run["ticket"]
            if ticket is None or ticket.get("table") != table or ticket.get("items") != items:
                errors.append("an ordinary order did not produce a valid ticket")
        if result[2]["ticket"] is not None or result[2]["stop_reason"] != "attempt_cap":
            errors.append("the unavailable order must be withheld at the attempt cap")
        if not any(o["stage"] == "meaning" for o in result[2]["outcomes"]):
            errors.append("the unavailable order did not exercise meaning validation")
    elif session == "s05":
        if not any(g["decision"] == "reject" for g in result["gate_log"]):
            errors.append("no customer rejection was exercised")
        if result["state"].fired:
            errors.append("a rejected order fired")
        if result["stop_reason"] == "turn_cap":
            errors.append("the comparison exhausted its turn budget")
    elif session == "s07":
        if len(result) != 4 or any(r["stop_reason"] != "passed" for r in result):
            errors.append("the ordinary orders did not pass the inherited ticket contract")
    elif session == "s09":
        events = report.log_events(result)
        if not any(e["type"].startswith("safety") for e in events):
            return ["no safety event exists for the omission comparison"]
        honest = report.write_report(result, events)
        reassuring = report.reassuring_variant(honest)
        errors.extend(report.validate_citations(honest, result))
        errors.extend(report.validate_coverage(honest, events))
        errors.extend(report.validate_citations(reassuring, result))
        if not report.validate_coverage(reassuring, events):
            errors.append("the omission was not detected")
    else:
        raise ValueError(session)
    return errors


def replay(session, path):
    client = ReplayClient(path)
    result = run_case(session, client)
    client.assert_exhausted()
    errors = admission_errors(session, result)
    for entry in client.entries:
        if entry["response"]["choices"][0]["finish_reason"] not in {"stop", "tool_calls"}:
            errors.append("an incomplete model response cannot be a comparison fixture")
    if errors:
        raise ValueError(f"{session}: " + "; ".join(errors))
    return len(client.entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", choices=["all", *CASES], default="all")
    parser.add_argument("--record", action="store_true", help="explicit live recording")
    parser.add_argument("--output-dir", type=Path, help="new staging directory outside the repository")
    parser.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()
    sessions = list(CASES) if args.session == "all" else [args.session]
    if args.record:
        if os.environ.get("COURSE_MODE") != "live":
            parser.error("recording requires COURSE_MODE=live and the existing CAFE_* or OPENAI_* configuration")
        if args.output_dir is None:
            parser.error("recording requires --output-dir; committed fixtures are never overwritten")
        staging = args.output_dir.resolve()
        if staging.is_relative_to(ROOT):
            parser.error("use private staging outside the repository, then review before promotion")
        staging.mkdir(parents=True, exist_ok=False)
    elif args.output_dir is not None:
        parser.error("--output-dir applies only to --record")
    for session in sessions:
        path = CASES[session]
        if args.record:
            path = staging / f"{session}.jsonl"
            client = RecordingClient(PublicFixtureClient(get_client(timeout=args.timeout)), path)
            result = run_case(session, client)
            errors = admission_errors(session, result)
            if errors:
                raise ValueError(f"{session}: " + "; ".join(errors))
        count = replay(session, path)
        print(f"{session}: {count} recorded responses, exact replay and teaching-purpose checks passed", flush=True)


if __name__ == "__main__":
    main()
