#!/usr/bin/env python3
"""Eval runner: naïve vs engine, cassette replay/live/record.

Default mode is replay. --all uses the reference implementation.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from datetime import date
from pathlib import Path

LABS = Path(__file__).resolve().parent
if str(LABS) not in sys.path:
    sys.path.insert(0, str(LABS))

from client import Client, OrphanedToolResult, ReplayMismatch, RouteRefused  # noqa: E402
from evals.tasks import TASKS, select  # noqa: E402

ROOT = LABS.parent
CASSETTES = LABS / "cassettes"
REPORTS = LABS / "reports"

S02_IDS = [f"p0{i}" for i in range(1, 7)]
S10_IDS = [f"p0{i}" for i in range(1, 10)]

SESSION_TASKS = {
    "s01": [],
    "s02": S02_IDS,
    "s03": S02_IDS,
    "s04": S02_IDS,
    "s05": S02_IDS,
    "s06": S02_IDS,
    "s07": S02_IDS,
    "s08": S02_IDS,
    "s09": S02_IDS,
    "s10": S10_IDS,
    "s11": S10_IDS,
    "s12": S10_IDS,
}


def parse_mode(args: argparse.Namespace) -> str:
    flags = [name for name in ("replay", "live", "record") if getattr(args, name)]
    if len(flags) > 1:
        raise SystemExit("choose one of --replay / --live / --record")
    return flags[0] if flags else "replay"


def load_impl(name: str):
    if name == "reference":
        engine = importlib.import_module("reference.engine")
        loop = importlib.import_module("reference.loop")
    elif name == "student":
        engine = importlib.import_module("trivia_host.engine")
        loop = importlib.import_module("trivia_host.loop")
    else:
        raise SystemExit(f"unknown --impl {name}")
    return engine, loop


def cassette_path(kind: str) -> Path:
    return CASSETTES / f"{kind}.jsonl"


def make_client(mode: str, path: Path) -> Client:
    if mode == "live":
        return Client(mode="live")
    if mode == "record":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return Client(mode="record", cassette_path=path)
    return Client(mode="replay", cassette_path=path)


def run_s01_pairing() -> str:
    from client import check_orphans

    try:
        check_orphans(
            [
                {"role": "user", "content": "hi"},
                {"role": "tool", "tool_call_id": "missing", "content": "{}"},
            ]
        )
        return "FAIL pairing: orphan was accepted"
    except OrphanedToolResult:
        pass
    check_orphans(
        [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "c1",
                        "type": "function",
                        "function": {"name": "end_round", "arguments": "{}"},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "c1", "content": "{}"},
        ]
    )
    return "PASS pairing: orphaned tool result rejected"


def run_pin_test(engine) -> str:
    compact = getattr(engine, "compact", None)
    if compact is None:
        return "FAIL s03: compact() missing"
    import house_rules

    pin = {"role": "system", "content": house_rules.PINNED_RULES}
    messages = [pin, {"role": "system", "content": house_rules.STARTER_PERSONA}]
    messages.extend({"role": "user", "content": f"pad {i}"} for i in range(20))
    out = compact(messages, keep=6)
    if not out or out[0].get("content") != house_rules.PINNED_RULES:
        return "FAIL s03: pin dropped under compact"
    return "PASS s03: pin survived compact"


class _NoModelClient:
    def chat(self, *args, **kwargs):
        raise AssertionError("medical gate reached the model")


def run_medical_gate(engine) -> str:
    try:
        result = engine.run_engine(
            _NoModelClient(),
            ["What medicine should I take for this headache?"],
            spec=select(["p05"])[0].spec,
        )
    except (AssertionError, NotImplementedError) as exc:
        return f"FAIL s06 medical gate: {exc}"
    if result.get("stop_reason") != "policy_refusal":
        return "FAIL s06 medical gate: missing policy_refusal"
    if (result.get("state") or {}).get("tool_log"):
        return "FAIL s06 medical gate: tool side effects"
    return "PASS s06 medical gate: refused before model/tool call"


def run_s01_round(client: Client, engine) -> dict:
    spec = {
        "theme": "science",
        "difficulty": "easy",
        "categories": ["science"],
        "clue_count": 1,
        "off_limits": ["medical advice"],
        "language": "en",
        "house_rules": ["clues from tools only"],
    }
    return engine.run_engine(
        client,
        ["Draw an easy science clue, wait, then end the round."],
        spec=spec,
        generate_from_brief=False,
    )


def run_task(client: Client, engine, task, mode: str) -> dict:
    if mode == "naive":
        result = engine.run_naive(client, list(task.script))
    else:
        result = engine.run_engine(
            client,
            list(task.script),
            spec=task.spec,
            generate_from_brief=task.generate_from_brief,
        )
    ok, reason = task.check(result)
    result["pass"] = ok
    result["reason"] = reason
    result["task_id"] = task.id
    result["run_mode"] = mode
    return result


def render_report(rows: list[dict], *, impl: str, mode: str, denom: int) -> str:
    naive_p = sum(1 for r in rows if r["run_mode"] == "naive" and r["pass"])
    eng_p = sum(1 for r in rows if r["run_mode"] == "engine" and r["pass"])
    naive_n = sum(1 for r in rows if r["run_mode"] == "naive")
    eng_n = sum(1 for r in rows if r["run_mode"] == "engine")
    lines = [
        f"# Lab report — {date.today().isoformat()}",
        "",
        f"impl={impl}  client_mode={mode}  denominator={denom}",
        "",
        f"naïve {naive_p}/{naive_n} vs engine {eng_p}/{eng_n}",
        "",
        "| task | mode | pass | reason |",
        "|---|---|---|---|",
    ]
    for r in rows:
        flag = "PASS" if r["pass"] else "FAIL"
        reason = (r.get("reason") or "").replace("|", "/")
        lines.append(f"| {r['task_id']} | {r['run_mode']} | {flag} | {reason} |")
    lines.append("")
    lines.append(
        "This number is only evidence if you can explain every cell. "
        "Notebook assertions are not a substitute."
    )
    return "\n".join(lines) + "\n"


def maybe_write_report(
    text: str, impl: str, all_mode: bool, mode: str
) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    if impl == "reference" and all_mode and mode == "record":
        path = REPORTS / "REFERENCE-p0-baseline.md"
        banner = (
            "# Course cassette-era baseline (reference implementation)\n\n"
            "Not a student bank. Regenerated only with `--all --record`.\n\n"
        )
        path.write_text(banner + text, encoding="utf-8")
        return
    path = REPORTS / "last.md"
    path.write_text(text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Trivia-host lab runner")
    p.add_argument("--session", choices=[f"s{i:02d}" for i in range(1, 13)])
    p.add_argument("--all", action="store_true", help="CI path: reference + full suite")
    p.add_argument("--replay", action="store_true", help="default if no mode flag")
    p.add_argument("--live", action="store_true")
    p.add_argument("--record", action="store_true")
    p.add_argument("--impl", choices=["reference", "student"])
    p.add_argument("--cassette", type=Path, help="override cassette path")
    p.add_argument(
        "--tasks",
        help="comma-separated task ids (default: session or all p01–p09)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.session and not args.all:
        raise SystemExit("pass --session sNN or --all")
    mode = parse_mode(args)
    impl = args.impl or ("reference" if args.all else "student")
    engine, _loop = load_impl(impl)

    rows: list[dict] = []
    exit_code = 0

    if args.all or args.session == "s01":
        pairing = run_s01_pairing()
        print(pairing)
        if pairing.startswith("FAIL"):
            exit_code = 1
        cassette = args.cassette or cassette_path("s01-round")
        client = make_client(mode, cassette)
        try:
            round_result = run_s01_round(client, engine)
            used_tools = bool((round_result.get("state") or {}).get("tool_log"))
            if mode == "replay":
                client.assert_exhausted()
            print("PASS s01 round" if used_tools else "FAIL s01 round: no tools")
            if not used_tools and impl == "reference":
                exit_code = 1
        except NotImplementedError as exc:
            print(f"s01 round skipped (not implemented): {exc}")
            if impl == "reference":
                exit_code = 1
        except (ReplayMismatch, RouteRefused) as exc:
            print(f"FAIL s01 round: {exc}")
            exit_code = 1
        if args.session == "s01" and not args.all:
            return exit_code

    if args.all or args.session == "s03":
        pin = run_pin_test(engine)
        print(pin)
        if pin.startswith("FAIL") and impl == "reference":
            exit_code = 1

    if args.all or args.session == "s06":
        medical = run_medical_gate(engine)
        print(medical)
        if medical.startswith("FAIL") and impl == "reference":
            exit_code = 1

    if args.all or (args.session and SESSION_TASKS.get(args.session)):
        ids = S10_IDS if args.all else SESSION_TASKS[args.session]
        if args.tasks:
            ids = [t.strip() for t in args.tasks.split(",") if t.strip()]
        tasks = select(ids)
        if args.session == "s01":
            tasks = []
        for task in tasks:
            for run_mode in ("naive", "engine"):
                path = args.cassette or cassette_path(f"{task.id}-{run_mode}")
                try:
                    client = make_client(mode, path)
                    row = run_task(client, engine, task, run_mode)
                    if mode == "replay":
                        client.assert_exhausted()
                except NotImplementedError as exc:
                    row = {
                        "task_id": task.id,
                        "run_mode": run_mode,
                        "pass": False,
                        "reason": f"not implemented: {exc}",
                    }
                    if impl == "reference":
                        exit_code = 1
                except (ReplayMismatch, RouteRefused) as exc:
                    row = {
                        "task_id": task.id,
                        "run_mode": run_mode,
                        "pass": False,
                        "reason": str(exc)[:200],
                    }
                    exit_code = 1
                rows.append(row)
                flag = "PASS" if row["pass"] else "FAIL"
                print(f"{row['task_id']} {row['run_mode']}: {flag} ({row.get('reason', '')})")
                if impl == "reference" and run_mode == "engine" and not row["pass"]:
                    exit_code = 1

    if args.all or args.session == "s11":
        try:
            engine.run_engine(
                Client.__new__(Client),
                ["hello"],
                spec=select(["p05"])[0].spec,
                route_kind="cloud",
            )
            print("FAIL s11: cloud route was accepted")
            exit_code = 1
        except RouteRefused:
            print("PASS s11: cloud route refused")
        except NotImplementedError:
            print("s11 refuse skipped (student not implemented)")
            if impl == "reference":
                exit_code = 1

    if rows:
        report = render_report(
            rows, impl=impl, mode=mode, denom=len({r["task_id"] for r in rows})
        )
        print(report)
        maybe_write_report(report, impl, args.all, mode)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
