"""Course-owned static Mermaid assets; no renderer is needed for ordinary HTML builds."""
import hashlib
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPTIONS = {'startOnLoad': False, 'theme': 'dark', 'securityLevel': 'strict',
           'deterministicIds': True, 'flowchart': {'htmlLabels': False},
           'fontFamily': 'Arial, sans-serif'}
VIEWPORT = {'width': 1440, 'height': 900}
ALTERNATIVES = {
    'study-plan': (
        'A learner chooses between harness and evaluation work or model-layer fundamentals, leads with the corresponding evidence, and then states clearly which claims that evidence does and does not support.',
    ),
    'S01-agent-loop': (
        'Client-owned weather loop: send the messages list to the model; an answer ends the loop, while tool calls are executed locally and their assistant message and matched results are retained before the next model call.',
    ),
    'S02-golden-evals': (
        'Controlled fitness comparison: the same scripted user feeds naive and governed engines; both transcripts rejoin at the same deterministic checks before results and explicitly labeled metric slots are reported.',
    ),
    'S03-context-engineering': (
        'Context assembly keeps safety rules verbatim in a pinned region and trims or summarizes only compactable history when over budget; both regions then feed the model.',
    ),
    'S04-structured-generation': (
        'A structured-generation loop parses model output, validates parsed JSON, and returns specific errors for another bounded attempt; validated output exits, while exhausted attempts escalate the schema.',
    ),
    'S05-consent-gate': (
        'A model proposal must validate and survive human approval or editing before the agent loop may run; only actions inside the approved specification dispatch, and violations stop with a readable report.',
    ),
    'S06-layered-detection': (
        'Untrusted text passes through an injection screen, keyword floor, classifier, and scope governor in order; dangerous input is blocked or handed off before any in-scope reply reaches the model.',
    ),
    'S07-repair-loop': (
        'A draft is scored deterministically and either accepted, retried with a curated failure view, or withheld when attempts run out; policy violations bypass generation entirely.',
    ),
    'S08-observability-replay': (
        'One end-to-end trace contains a session span, phase spans for setup, rounds, and wrap-up, and nested generation spans that record each model input, output, and usage.',
        'During recording, a recorder relays host requests to the live model and stores responses in a cassette; during replay, the unchanged host receives content-equal recorded responses without a live call.',
    ),
    'S09-evidence-reports': (
        'A report model turns the transcript and run record into fixed evidence slots; citation and coverage validators compare the report with that ground truth, returning violations for repair before a short human review.',
    ),
    'S10-error-analysis': (
        'Failure traces move through open coding, axial grouping, and count-by-severity ranking; top categories drive focused fixes and recurrent categories add eval tasks whose results produce new traces.',
    ),
    'S11-budgets-routing': (
        'A pipeline validates its policy route table before any model call, routes allowed content among local and cloud models, meters cost and latency, and stops before a run would breach its budget.',
    ),
    'S12-judge-calibration': (
        'Seeded transcripts feed both a defect critic and a rubric judge; detection and false-positive counts combine with judge agreement against prior hand labels to determine what findings may trigger.',
    ),
    'S13-rebuild-from-memory': (
        'A closed-book audit rebuilds one core file on a branch, classifies every diff, runs the suite against a banked number, restores the original, and turns behavioral gaps into a focused forgot-list for a later re-audit.',
    ),
    'S14-ship-and-pilot': (
        'Shipping begins with frozen acceptance and holdout fixtures, loops failed acceptance runs through trace-led repair, then uses the untouched holdout before a human pilot, artifact-based documentation, adversarial review, and the release tag.',
        'Decision logs, banked eval numbers, traces, and failure counts assemble into architecture and failure documents; those two evidence-backed documents feed the public fixture-run artifact.',
    ),
}
STATIC_LESSONS = frozenset(ALTERNATIVES)
# Notebook-only diagrams: sources are notebooks/public/diagrams/<asset>.mmd,
# next to their renders. Notebook cells embed them as markdown figures
# (`![...](public/diagrams/<asset>.svg)`):
# marimo serves notebook-adjacent files only from a public/ directory, so this
# one reference renders both statically (resolved against the notebook file)
# and at runtime (served by the kernel). No mermaid runs at view time.
PUBLIC_LESSON_ASSETS = frozenset({
    'S01-agent-loop',
    'S02-golden-evals',
    'S04-structured-generation',
    'S06-layered-detection',
    'S07-repair-loop',
    'S09-evidence-reports',
    'S10-error-analysis',
})
NOTEBOOK_ALTERNATIVES = {
    's03-window': (
        'History grows until it crosses a budget, when truncation, summarization, '
        'or pinning compacts it before sending; past a hard limit the call fails '
        'instead of degrading.',
    ),
    's05-consent': (
        'A proposed ticket validates, renders for a human decision, and only fires '
        'on approval; edits re-validate, and anything outside the approved ticket '
        'aborts or degrades at preflight.',
    ),
    's08-replay': (
        'A recording client relays shift calls to the model while appending each '
        'request and response to a trace file; a replay client later serves those '
        'responses back in order and raises on any mismatch.',
    ),
    's11-budget': (
        'A validated route table projects each call cost and refuses before spending '
        'past budget; dispatched calls report usage and latency into a ledger of '
        'real tokens and cost.',
    ),
    's12-judge': (
        'Clean transcripts seed known defects and an answer key before blind '
        'hand-labeling; an uncalibrated judge misses become classes for a '
        'calibrated re-measurement scored by chance-corrected agreement.',
    ),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inputs(source):
    return {'source_sha256': sha(source.strip().encode()),
            'vendor_sha256': sha((HERE/'vendor/mermaid.min.js').read_bytes()),
            'options': OPTIONS, 'viewport': VIEWPORT,
            'renderer_sha256': sha((HERE/'render_diagrams.py').read_bytes()),
            'config_sha256': sha(Path(__file__).read_bytes()),
            'lock_sha256': sha((HERE.parent/'uv.lock').read_bytes())}


def asset_name(slug, index):
    """Keep the first diagram at the historical lesson-slug path."""
    return slug if index == 0 else f'{slug}-{index + 1}'


def static_image(slug, index, source):
    asset = asset_name(slug, index)
    path = HERE/'diagrams'/f'{asset}.svg'
    receipt_path = HERE/'diagrams/receipt.json'
    if not receipt_path.is_file() or not path.is_file():
        raise ValueError(f'stale or missing diagram for {asset}; run the documented diagram renderer')
    svg = path.read_bytes()
    entry = json.loads(receipt_path.read_text())['diagrams'].get(asset, {})
    if entry.get('inputs') != inputs(source) or entry.get('svg_sha256') != sha(svg):
        raise ValueError(f'stale diagram for {asset}; run uv run --group diagrams python lessons/render_diagrams.py')
    viewbox = re.search(rb'viewBox="\S+ \S+ (\S+) \S+"', svg)
    if not viewbox:
        raise ValueError(f'{asset}: static SVG has no readable viewBox')
    display_width = math.ceil(float(viewbox.group(1)))
    alternative = ALTERNATIVES[slug][index]
    return (
        '<div class="static-diagram-scroll" tabindex="0">'
        f'<img class="static-diagram" src="diagrams/{asset}.svg" '
        f'alt="{html.escape(alternative, quote=True)}" '
        f'style="--diagram-width: {display_width}px" />'
        '</div>'
    )
