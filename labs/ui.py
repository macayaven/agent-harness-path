"""Translate the lab controls into the terminal runner's public arguments."""


def build_argv(session: str, impl: str, mode: str, tasks: str = "") -> list[str]:
    if session not in {"all", *(f"s{i:02d}" for i in range(1, 13))}:
        raise ValueError(f"unknown session: {session!r}")
    if impl not in {"student", "reference"}:
        raise ValueError(f"unknown implementation: {impl!r}")
    if mode not in {"replay", "live", "record"}:
        raise ValueError(f"unknown client mode: {mode!r}")
    argv = ["--all"] if session == "all" else ["--session", session]
    argv += ["--impl", impl, "--" + mode]
    if tasks.strip():
        argv += ["--tasks", tasks.strip()]
    return argv
