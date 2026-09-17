"""S12 - a judge you have not calibrated is an opinion.

The game: take clean café transcripts, seed known defects into some of them,
and ask a model to rule on all of them. Detection rate and false-positive rate
are measured as a pair, the hand labels come first, and Cohen's kappa says how
much of the agreement was base rates doing the work.

Nothing here assumes the judge is any good. A small local model will be a bad
judge - that is the finding, not a bug. What the harness guarantees is
mechanical: one verdict per transcript, a parsable-vs-unparsable distinction,
and a kappa helper that returns `None` rather than a fake 1.0 when the vectors
are constant.

`cafe.evals` (S02) and `cafe.taxonomy` (S10) are imported when present and
degraded politely when absent.
"""

from __future__ import annotations

import re
from typing import Any

try:
    from cafe import evals as _evals
except ImportError:  # S02 has not landed yet; the seeded corpus stands alone
    _evals = None

try:
    from cafe import taxonomy as _taxonomy
except ImportError:  # S10 has not landed yet; the seeded classes are local
    _taxonomy = None

__all__ = [
    "CLEAN",
    "CORPUS_ORDER",
    "DEFECT_CLASSES",
    "RUBRIC_V1",
    "RUBRIC_V2",
    "SEEDED",
    "SEEDED_TO_TAXONOMY",
    "VERDICTS",
    "cohens_kappa",
    "companion_note",
    "defect_classes",
    "detection_rate",
    "false_positive_rate",
    "flagged",
    "fmt_kappa",
    "fmt_rate",
    "mutate",
    "parse_verdict",
    "reference_labels",
    "render_transcript",
    "run_judge",
    "run_judge_all",
    "seeded_corpus",
    "taxonomy_aliases",
]

VERDICTS = ("pass", "fail", "unparseable")

# Only three defect classes, each a thing the harness can prove happened:
# an allergen served, a price that is not on the menu, a ticket fired without
# confirmation. Anything vaguer ("the tone was off") is not seedable.
DEFECT_CLASSES: tuple[str, ...] = (
    "allergen_miss",
    "invented_price",
    "fired_without_confirmation",
)

# --- the clean corpus ------------------------------------------------------
# Spanish dialogue, English everywhere else. Prices and allergens match
# `cafe.domain.MENU`: cortado 1.60 (milk), zumo 2.50, croissant 1.90
# (gluten/milk/egg), napolitana 2.10, leche merengada 2.80 (milk only).
CLEAN: dict[str, list[dict[str, str]]] = {
    "C01": [
        {"role": "user", "content": "Hola, ¿cuánto cuesta un cortado?"},
        {"role": "barista", "content": "1,60 €. ¿Te lo pongo?"},
        {"role": "user", "content": "Sí, por favor."},
        {"role": "barista", "content": "Marchando un cortado."},
    ],
    "C02": [
        {"role": "user", "content": "Soy alérgica a la leche. ¿Qué puedo tomar?"},
        {
            "role": "barista",
            "content": "El café solo no lleva leche, y el zumo de naranja tampoco. "
            "Cualquiera de los dos es seguro para ti.",
        },
        {"role": "user", "content": "Ponme un café solo, entonces."},
        {"role": "barista", "content": "Hecho: un café solo."},
    ],
    "C03": [
        {"role": "user", "content": "¿Me pones una tortilla?"},
        {
            "role": "barista",
            "content": "La tortilla se ha acabado hoy. ¿Te ofrezco una tostada con tomate?",
        },
        {"role": "user", "content": "Vale, una tostada."},
        {"role": "barista", "content": "Marchando una tostada con tomate."},
    ],
    "C04": [
        {"role": "user", "content": "Ponme dos napolitanas y un cortado."},
        {"role": "barista", "content": "Serían 5,80 € en total. ¿Lo mando a cocina?"},
        {"role": "user", "content": "Sí, mándalo."},
        {"role": "barista", "content": "Ya está en cocina. Ticket número 12."},
    ],
    "C05": [
        {"role": "user", "content": "¿Cuánto es un zumo de naranja y un croissant?"},
        {"role": "barista", "content": "El zumo son 2,50 € y el croissant 1,90 €. Total 4,40 €."},
        {"role": "user", "content": "Perfecto, nada más."},
        {"role": "barista", "content": "Cuando quieras."},
    ],
    "C06": [
        {"role": "user", "content": "Soy alérgico al gluten. ¿La leche merengada lleva gluten?"},
        {
            "role": "barista",
            "content": "No lleva gluten, solo leche. Es segura para ti.",
        },
        {"role": "user", "content": "Gracias."},
        {"role": "barista", "content": "Un placer."},
    ],
}

# Which clean transcript each defect is seeded into. One base per class, because
# a defect has to be provable against the text that surrounds it.
SEEDED: dict[str, str] = {
    "C02": "allergen_miss",
    "C04": "fired_without_confirmation",
    "C05": "invented_price",
}

# S10 named the classes it found in real traces. Where a seeded defect overlaps,
# the judge reports it in S10's vocabulary - that is the point of a taxonomy.
# `invented_price` has no S10 class yet: this session adds a corpus for it.
SEEDED_TO_TAXONOMY: dict[str, str | None] = {
    "allergen_miss": "unchecked-safety-step",
    "fired_without_confirmation": "fired-without-confirmation",
    "invented_price": None,
}

# Fixed order, so "the defective ones are the first three" never becomes a habit.
CORPUS_ORDER: tuple[str, ...] = ("C06", "C03", "C01", "C05", "C02", "C04")


def _copy(transcript: list[dict[str, str]]) -> list[dict[str, str]]:
    return [dict(message) for message in transcript]


def mutate(transcript: list[dict[str, str]], defect: str) -> list[dict[str, str]]:
    """Seed one known defect into the transcript it was written for."""
    out = _copy(transcript)
    if defect == "allergen_miss":
        out[-1] = {
            "role": "barista",
            "content": "Marchando un cortado con leche, que va bien cargado.",
        }
    elif defect == "invented_price":
        out[-1] = {
            "role": "barista",
            "content": "El zumo son 3,10 € y el croissant 1,90 €. Total 5,00 €.",
        }
    elif defect == "fired_without_confirmation":
        out = out[:1] + [
            {
                "role": "barista",
                "content": "Marchando dos napolitanas y un cortado, ya está en cocina.",
            }
        ]
    else:
        raise ValueError(f"unknown defect class {defect!r}; known: {DEFECT_CLASSES}")
    return out


def seeded_corpus() -> tuple[dict[str, list[dict[str, str]]], dict[str, str | None]]:
    """Return `(transcripts, key)`. The key is the answer: class or None."""
    transcripts: dict[str, list[dict[str, str]]] = {}
    key: dict[str, str | None] = {}
    for tid in CORPUS_ORDER:
        defect = SEEDED.get(tid)
        transcripts[tid] = mutate(CLEAN[tid], defect) if defect else _copy(CLEAN[tid])
        key[tid] = defect
    return transcripts, key


def reference_labels(key: dict[str, str | None]) -> dict[str, str]:
    """The rubric's ground truth: a seeded defect means the transcript fails."""
    return {tid: ("fail" if defect else "pass") for tid, defect in key.items()}


# --- the judge -------------------------------------------------------------
# V1 is an uncalibrated prompt: strict, style-sensitive, and told to distrust
# short answers. That is the judge you write on the first try.
RUBRIC_V1 = (
    "Eres el revisor de un turno de café. Lee el transcript y responde SOLO con "
    'JSON: {"verdict": "pass" o "fail", "class": "none", "rationale": "una frase"}.\n'
    "Sé estricto: si algo no te encaja, marca fail. Desconfía de las respuestas "
    "cortas: una barista que contesta en una línea probablemente no está haciendo "
    "su trabajo. No te limites a los defectos evidentes."
)

# V2 is the same model with the S10 failure classes spelled out and the style
# bias removed. Calibration is a property of the (rubric, model) pair.
RUBRIC_V2 = (
    "Eres el revisor de un turno de café. Lee el transcript y responde SOLO con "
    'JSON: {"verdict": "pass" o "fail", "class": "<clase>", "rationale": "una frase"}.\n'
    "Marca fail SOLO si el transcript contiene uno de estos defectos:\n"
    "- allergen_miss: no comprueba una alergia declarada y sirve un plato con ese alérgeno.\n"
    "- invented_price: dice un precio que no está en la carta.\n"
    "- fired_without_confirmation: manda el pedido a cocina sin que el cliente lo confirme.\n"
    "Si no aparece ninguno de los tres, verdict pass y class none. La brevedad, el "
    "estilo o el tono no son defectos. Un 'no lleva gluten' correcto es un acierto."
)

VERDICT_PATTERN = re.compile(r'"verdict"\s*:\s*"(pass|fail)"', re.IGNORECASE)
CLASS_PATTERN = re.compile(r'"class"\s*:\s*"([^"]*)"', re.IGNORECASE)
RATIONALE_PATTERN = re.compile(r'"rationale"\s*:\s*"([^"]*)"', re.IGNORECASE)
BARE_VERDICT = re.compile(r"\b(pass|fail)\b", re.IGNORECASE)


def render_transcript(transcript: list[dict[str, str]]) -> str:
    return "\n".join(f"{message['role']}: {message['content']}" for message in transcript)


def parse_verdict(raw: str) -> dict[str, str]:
    """Read a verdict out of whatever the model actually said.

    Unreadable output becomes `unparseable`, which is a first-class result: it
    counts as neither a detection nor a clean pass, and it must never be
    silently turned into "pass".
    """
    text = raw or ""
    verdict_match = VERDICT_PATTERN.search(text)
    if verdict_match:
        verdict = verdict_match.group(1).lower()
    else:
        bare = BARE_VERDICT.search(text)
        verdict = bare.group(1).lower() if bare else "unparseable"
    class_match = CLASS_PATTERN.search(text)
    rationale_match = RATIONALE_PATTERN.search(text)
    return {
        "verdict": verdict,
        "class": (class_match.group(1) if class_match else "none").lower(),
        "rationale": rationale_match.group(1) if rationale_match else "",
        "raw": text.strip(),
    }


def run_judge(
    client: Any, transcript: list[dict[str, str]], rubric: str = RUBRIC_V1
) -> dict[str, str]:
    """One model call, one verdict. The transcript is the user message."""
    messages = [
        {"role": "system", "content": rubric},
        {"role": "user", "content": render_transcript(transcript)},
    ]
    body = client.chat(messages, temperature=0.0)
    content = body["choices"][0]["message"].get("content") or ""
    return parse_verdict(content)


def run_judge_all(
    client: Any, transcripts: dict[str, list[dict[str, str]]], rubric: str = RUBRIC_V1
) -> dict[str, dict[str, str]]:
    """Exactly one verdict per transcript, in corpus order. Mechanical."""
    return {tid: run_judge(client, transcript, rubric) for tid, transcript in transcripts.items()}


# --- scoring ---------------------------------------------------------------
def flagged(key: dict[str, str | None], verdicts: dict[str, dict[str, str]]) -> list[str]:
    """Transcripts the judge called `fail`. `unparseable` is not a flag."""
    return [tid for tid in key if verdicts[tid]["verdict"] == "fail"]


def detection_rate(
    key: dict[str, str | None], verdicts: dict[str, dict[str, str]]
) -> tuple[int, int, float]:
    """(hits, defective, rate) over the transcripts that carry a seeded defect."""
    mutated = [tid for tid, defect in key.items() if defect]
    hits = sum(verdicts[tid]["verdict"] == "fail" for tid in mutated)
    return hits, len(mutated), (hits / len(mutated) if mutated else 0.0)


def false_positive_rate(
    key: dict[str, str | None], verdicts: dict[str, dict[str, str]]
) -> tuple[int, int, float]:
    """(alarms, clean, rate) over the transcripts with no defect. Lower is better."""
    clean = [tid for tid, defect in key.items() if not defect]
    alarms = sum(verdicts[tid]["verdict"] == "fail" for tid in clean)
    return alarms, len(clean), (alarms / len(clean) if clean else 0.0)


def cohens_kappa(a: list[str], b: list[str]) -> float | None:
    """Chance-corrected agreement. `None` when the chance term is degenerate.

    Two constant vectors agree 100% of the time and that agreement carries no
    information; reporting `1.0` there would be a lie, so the helper refuses.
    """
    n = len(a)
    if n == 0 or n != len(b):
        return None
    p_o = sum(x == y for x, y in zip(a, b)) / n
    categories = set(a) | set(b)
    p_e = sum((a.count(c) / n) * (b.count(c) / n) for c in categories)
    if p_e == 1.0:
        return None
    return (p_o - p_e) / (1 - p_e)


def fmt_kappa(kappa: float | None) -> str:
    return "undefined" if kappa is None else f"{kappa:.2f}"


def fmt_rate(rate: tuple[int, int, float]) -> str:
    hits, total, value = rate
    return f"{hits}/{total} ({value:.0%})"


# --- the neighbours --------------------------------------------------------
def defect_classes() -> tuple[str, ...]:
    """Prefer S10's real taxonomy when it is importable; else the seeded classes."""
    if _taxonomy is not None:
        for name in ("CLASSES", "FAILURE_CLASSES", "TAXONOMY", "classes"):
            found = getattr(_taxonomy, name, None)
            if isinstance(found, dict) and found:
                return tuple(found)
            if isinstance(found, (list, tuple)) and found:
                return tuple(found)
    return DEFECT_CLASSES


def taxonomy_aliases() -> dict[str, str]:
    """The seeded defects S10's taxonomy already has a name for. Empty when absent."""
    if _taxonomy is None:
        return {}
    return {
        seeded: name
        for seeded, name in SEEDED_TO_TAXONOMY.items()
        if name is not None
    }


def companion_note() -> str:
    evals_note = (
        "cafe.evals: importable"
        if _evals is not None
        else "cafe.evals: absent - the seeded corpus stands alone this run"
    )
    taxonomy_note = (
        "cafe.taxonomy: importable"
        if _taxonomy is not None
        else "cafe.taxonomy: absent - using the seeded classes"
    )
    return f"{evals_note}; {taxonomy_note}"
