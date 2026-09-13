#!/usr/bin/env python3
"""Mandatory real installed-artifact adapter check; invoke with its Python -I.

No source fallback or conditional skip. This verifies the authored course through
the installed loader, resolver, policy, lesson-grounding, state, and launcher
interfaces. Actual Jupyter/kernel/provider/browser acceptance is performed by
CourseWeave's installed-adapter suite.
"""

import argparse
import hashlib
from html import unescape
from html.parser import HTMLParser
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
import tempfile


EXCLUDED_HASH_PARTS = {".git", ".venv", "__pycache__"}
CORE_MODULE_IDS = tuple(f"s{number:02d}" for number in range(1, 13))
PROTOCOL_MODULE_IDS = ("s13", "s14")
OBSERVER_ONLY_PHASES = {
    ("s13", "audit"),
    ("s14", "acceptance"),
    ("s14", "pilot"),
}
REVIEW_GATES = {"s13": "s13-closed", "s14": "s14-closed"}


def source_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_HASH_PARTS for part in path.relative_to(root).parts)
    }


def phase_for(manifest, module_id: str, phase_id: str):
    module = next(module for module in manifest.modules if module.id == module_id)
    return next(phase for phase in module.phases if phase.id == phase_id)


class NativeDetailsText(HTMLParser):
    """Collect meaningful text nodes that lesson grounding must omit."""

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.texts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "details":
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "details":
            self.depth -= 1

    def handle_data(self, data):
        text = " ".join(unescape(data).split())
        if self.depth and len(text) >= 25:
            self.texts.append(text)


def native_details_text(page: str) -> list[str]:
    parser = NativeDetailsText()
    parser.feed(page)
    return parser.texts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--course-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.course_root.resolve()

    import courseweave
    from courseweave.context import resolve_context
    from courseweave.contracts.records import Coordinate
    from courseweave.engine import curriculum_digest
    from courseweave.engine.policy import effective_teacher_policy
    from courseweave.engine.progress import bind_record, evaluate_progress
    from courseweave.manifest import load_manifest
    from courseweave.models import ResolutionState, WorkspaceContext
    from courseweave.store import CourseStore
    from courseweave.teaching import lesson_scope

    package = Path(courseweave.__file__).resolve()
    assert package.is_relative_to(
        Path(sys.prefix).resolve()
    ), f"Use an installed wheel, not editable/source import: {package}"
    before = source_hashes(root)

    manifest = load_manifest(root, runnable=True)
    assert manifest.schema_version == 2
    assert tuple(module.id for module in manifest.modules) == (
        *CORE_MODULE_IDS,
        *PROTOCOL_MODULE_IDS,
    )
    progress = evaluate_progress(manifest, [], root)
    assert (progress.required_total, progress.required_complete) == (36, 0)

    module_coverage = {
        module.id: {
            "required_phases": [
                phase.id for phase in module.phases if phase.progress == "required"
            ],
            "surface_count": 0,
            "resolved_surfaces": 0,
            "html_surfaces": 0,
            "notebook_surfaces": 0,
            "authored_checks": 0,
            "authored_options": 0,
        }
        for module in manifest.modules
    }

    notebook_gate_count = 0
    for module_id in CORE_MODULE_IDS:
        module = next(module for module in manifest.modules if module.id == module_id)
        assert [phase.id for phase in module.phases if phase.progress == "required"] == [
            "read",
            "notebook",
            "self-check",
        ]
        notebook = phase_for(manifest, module_id, "notebook")
        assert [surface.type for surface in notebook.surfaces] == ["notebook"]
        assert notebook.teacher.access.requires == (f"{module_id}-prediction",)
        assert not effective_teacher_policy(
            manifest, module_id, "notebook", []
        ).provider_callable
        prediction = bind_record(
            manifest,
            Coordinate(
                module_id=module_id,
                phase_id="notebook",
                requirement_id=f"{module_id}-prediction",
            ),
            {"text": "Synthetic adapter-test prediction; no learner outcome claimed."},
        )
        assert effective_teacher_policy(
            manifest, module_id, "notebook", [prediction]
        ).provider_callable
        prediction_progress = evaluate_progress(manifest, [prediction], root)
        notebook_progress = next(
            phase
            for phase in prediction_progress.phases
            if (phase.module_id, phase.phase_id) == (module_id, "notebook")
        )
        assert not notebook_progress.complete
        notebook_gate_count += 1

    for module_id in PROTOCOL_MODULE_IDS:
        assert all(
            surface.type != "notebook"
            for phase in next(
                module for module in manifest.modules if module.id == module_id
            ).phases
            for surface in phase.surfaces
        )

    actual_observer_only = {
        (module.id, phase.id)
        for module in manifest.modules
        for phase in module.phases
        if phase.teacher.access.mode == "observer_only"
    }
    assert actual_observer_only == OBSERVER_ONLY_PHASES
    for module_id, phase_id in sorted(OBSERVER_ONLY_PHASES):
        phase = phase_for(manifest, module_id, phase_id)
        assert phase.teacher.access.requires == ()
        assert phase.teacher.sharing.allow == ()
        assert phase.teacher.proposals.allow == ()
        policy = effective_teacher_policy(manifest, module_id, phase_id, [])
        assert policy.mode == "observer_only"
        assert not policy.provider_callable
        assert policy.allowed_share_kinds == ()
        assert policy.allowed_proposal_types == ()

    for module_id, requirement_id in REVIEW_GATES.items():
        review = phase_for(manifest, module_id, "review")
        assert review.teacher.access.mode == "available"
        assert review.teacher.access.requires == (requirement_id,)
        assert not effective_teacher_policy(
            manifest, module_id, "review", []
        ).provider_callable

    coordinates = []
    native_detail_scopes = 0
    for module in manifest.modules:
        coverage = module_coverage[module.id]
        for phase in module.phases:
            coverage["authored_checks"] += len(phase.learning.checks)
            coverage["authored_options"] += sum(
                len(check.options) for check in phase.learning.checks
            )
            for index, surface in enumerate(phase.surfaces):
                coverage["surface_count"] += 1
                coverage[f"{surface.type}_surfaces"] = (
                    coverage.get(f"{surface.type}_surfaces", 0) + 1
                )
                data = {
                    "source_id": "installed-adapter-check",
                    "sequence": index,
                    "explicit_module_id": module.id,
                    "explicit_phase_id": phase.id,
                    "surface_kind": surface.type,
                }
                if getattr(surface, "path", None):
                    data["active_path"] = str(surface.path)
                if surface.type == "notebook":
                    data["active_cell_id"] = surface.selector.values[0]
                resolved = resolve_context(
                    manifest, ResolutionState(), WorkspaceContext(**data)
                )
                assert (
                    resolved.module_id,
                    resolved.phase_id,
                    resolved.reason,
                ) == (module.id, phase.id, "explicit_phase")
                if getattr(surface, "path", None):
                    assert resolved.surface_id == surface.id, (
                        module.id,
                        phase.id,
                        surface.id,
                        resolved,
                    )
                coverage["resolved_surfaces"] += 1

                if surface.type == "html":
                    page = (root / str(surface.path)).read_text()
                    assert surface.fragment
                    assert f'id="{surface.fragment}"' in page
                    details_text = native_details_text(page)
                    assert details_text, f"Expected native details in {surface.path}"
                    scope = lesson_scope(
                        root, manifest, resolved, "adapter-check", "scope"
                    )
                    assert scope.omitted_sections
                    for text in details_text:
                        assert text not in scope.excerpt
                    native_detail_scopes += 1
                coordinates.append([module.id, phase.id, surface.id])

    digest = curriculum_digest(manifest)
    authored_check_count = sum(
        coverage["authored_checks"] for coverage in module_coverage.values()
    )
    authored_option_count = sum(
        coverage["authored_options"] for coverage in module_coverage.values()
    )
    attempted_options = 0
    state_parent = root.parent.resolve()
    assert not state_parent.is_relative_to(root)
    with tempfile.TemporaryDirectory(
        prefix="courseweave-adapter-state-", dir=state_parent
    ) as temporary:
        state_dir = Path(temporary, "state").resolve()
        assert not state_dir.is_relative_to(root)
        store = CourseStore(root, state_dir=state_dir)
        state = store.get_state()
        initial_view = store.state_view(state)
        assert (
            initial_view["progress"]["required_total"],
            initial_view["progress"]["required_complete"],
        ) == (36, 0)

        for module in manifest.modules:
            for phase in module.phases:
                for check in phase.learning.checks:
                    assert (
                        sum(
                            option.id == check.correct_option_id
                            for option in check.options
                        )
                        == 1
                    )
                    for option in check.options:
                        state = store.apply_state(
                            {
                                "type": "check_attempt",
                                "module_id": module.id,
                                "phase_id": phase.id,
                                "check_id": check.id,
                                "option_id": option.id,
                                "curriculum_digest": digest,
                            },
                            expected_revision=state.revision,
                            idempotency_key=(
                                f"adapter-check-{module.id}-{phase.id}-"
                                f"{check.id}-{option.id}"
                            ),
                        )
                        attempt = state.attempts[-1]
                        assert (
                            attempt.module_id,
                            attempt.phase_id,
                            attempt.check_id,
                            attempt.option_id,
                        ) == (module.id, phase.id, check.id, option.id)
                        assert attempt.correct is (
                            option.id == check.correct_option_id
                        )
                        assert attempt.feedback == option.feedback
                        attempted_options += 1

        answers_view = store.state_view(state)
        assert attempted_options == authored_option_count
        assert len(answers_view["attempt_statuses"]) == authored_option_count
        assert {
            attempt["status"] for attempt in answers_view["attempt_statuses"]
        } == {"valid"}
        assert answers_view["progress"]["required_complete"] == 0

        for module_id, requirement_id in REVIEW_GATES.items():
            coordinate = {
                "module_id": module_id,
                "phase_id": "review",
                "requirement_id": requirement_id,
            }
            state = store.apply_state(
                {
                    "type": "put_record",
                    "coordinate": coordinate,
                    "value": {"attested": False},
                    "curriculum_digest": digest,
                },
                expected_revision=state.revision,
                idempotency_key=f"adapter-review-{module_id}-false",
            )
            false_view = store.state_view(state)
            assert not false_view["teacher_availability"][
                f"{module_id}/review"
            ]["provider_callable"]
            state = store.apply_state(
                {
                    "type": "put_record",
                    "coordinate": coordinate,
                    "value": {"attested": True},
                    "curriculum_digest": digest,
                },
                expected_revision=state.revision,
                idempotency_key=f"adapter-review-{module_id}-true",
            )
            true_view = store.state_view(state)
            assert true_view["teacher_availability"][f"{module_id}/review"][
                "provider_callable"
            ]
        assert store.state_view(state)["progress"]["required_complete"] == 0

    help_result = subprocess.run(
        [sys.executable, "-m", "courseweave", "launch", "--help"],
        capture_output=True,
        text=True,
    )
    assert (
        help_result.returncode == 0 and "--kernel-python" in help_result.stdout
    ), "Installed pilot must support launch --kernel-python; rebuild/install the final artifact."

    after = source_hashes(root)
    assert before == after, "Read-only adapter verification changed course artifacts"
    print(
        json.dumps(
            {
                "courseweave_version": importlib.metadata.version("courseweave"),
                "python": sys.executable,
                "installed_package": str(package),
                "module_count": len(manifest.modules),
                "surface_count": len(coordinates),
                "required_total": progress.required_total,
                "required_complete": progress.required_complete,
                "notebook_prediction_gates": notebook_gate_count,
                "observer_only_phases": [
                    "/".join(coordinate) for coordinate in sorted(OBSERVER_ONLY_PHASES)
                ],
                "review_attestation_gates": REVIEW_GATES,
                "native_detail_scopes": native_detail_scopes,
                "authored_check_count": authored_check_count,
                "authored_option_attempts": attempted_options,
                "module_coverage": module_coverage,
                "manifest_sha256": hashlib.sha256(
                    (root / "courseweave.json").read_bytes()
                ).hexdigest(),
                "read_only": True,
                "external_ephemeral_state": True,
                "launcher_kernel_interface": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
