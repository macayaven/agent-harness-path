"""Course-owned static Mermaid assets; no renderer is needed for ordinary HTML builds."""
import hashlib
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PILOT = {'S01-agent-loop', 'S02-golden-evals'}
OPTIONS = {'startOnLoad': False, 'theme': 'dark', 'securityLevel': 'strict',
           'deterministicIds': True, 'flowchart': {'htmlLabels': False},
           'fontFamily': 'Arial, sans-serif'}
VIEWPORT = {'width': 1440, 'height': 900}
ALT = {
    'S01-agent-loop': 'Client-owned weather loop: send the messages list to the model; an answer ends the loop, while tool calls are executed locally and their assistant message and matched results are retained before the next model call.',
    'S02-golden-evals': 'Controlled fitness comparison: the same scripted user feeds naive and governed engines; both transcripts rejoin at the same deterministic checks before results and explicitly labeled metric slots are reported.',
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


def static_image(slug, source):
    path = HERE/'diagrams'/f'{slug}.svg'
    receipt_path = HERE/'diagrams/receipt.json'
    if not receipt_path.is_file() or not path.is_file():
        raise ValueError(f'stale or missing diagram for {slug}; run the documented diagram renderer')
    entry = json.loads(receipt_path.read_text())['diagrams'].get(slug, {})
    if entry.get('inputs') != inputs(source) or entry.get('svg_sha256') != sha(path.read_bytes()):
        raise ValueError(f'stale diagram for {slug}; run uv run --group diagrams python lessons/render_diagrams.py')
    return f'<img class="static-diagram" src="diagrams/{slug}.svg" alt="{html.escape(ALT[slug], quote=True)}" />'
