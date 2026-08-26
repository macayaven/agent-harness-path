"""Round-spec schema. Shared by tools, engine, and checkers."""

from __future__ import annotations

import re

SPEC_KEYS = (
    "theme",
    "difficulty",
    "categories",
    "clue_count",
    "off_limits",
    "language",
    "house_rules",
)
DIFFICULTIES = {"easy", "medium", "hard"}
LANGUAGES = {"en", "es"}
CATEGORIES = {"science", "geography", "literature"}
PII_RE = re.compile(
    r"([A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b)",
    re.I,
)


class SpecError(ValueError):
    pass


def _string_list(spec: dict, field: str, *, non_empty: bool = False) -> list[str]:
    value = spec[field]
    if not isinstance(value, list) or (non_empty and not value):
        qualifier = "non-empty " if non_empty else ""
        raise SpecError(f"{field} must be a {qualifier}list")
    if any(not isinstance(item, str) for item in value):
        raise SpecError(f"{field} items must be strings")
    return value


def validate_spec(spec: dict) -> dict:
    if not isinstance(spec, dict):
        raise SpecError("spec must be an object")
    missing = [k for k in SPEC_KEYS if k not in spec]
    if missing:
        raise SpecError("missing fields: " + ", ".join(missing))
    extra = [k for k in spec if k not in SPEC_KEYS]
    if extra:
        raise SpecError("unexpected fields: " + ", ".join(extra))
    if not isinstance(spec["theme"], str):
        raise SpecError("theme must be a string")
    if not isinstance(spec["difficulty"], str) or spec["difficulty"] not in DIFFICULTIES:
        raise SpecError("difficulty must be easy|medium|hard")
    if not isinstance(spec["language"], str) or spec["language"] not in LANGUAGES:
        raise SpecError("language must be en|es")
    n = spec["clue_count"]
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 5:
        raise SpecError("clue_count must be an integer 1–5")
    categories = _string_list(spec, "categories", non_empty=True)
    unknown = [category for category in categories if category not in CATEGORIES]
    if unknown:
        raise SpecError("unknown categories: " + ", ".join(unknown))
    _string_list(spec, "off_limits")
    _string_list(spec, "house_rules")
    return spec
