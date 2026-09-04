"""Contract tests for the Agent Harness Path CourseWeave adapter."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "courseweave.json"
LAUNCHER_PATH = ROOT / "scripts/courseweave"

EXPECTED_MODULES = {
    "s01": ("S01-agent-loop", "s01_agent_loop_toy", "s01_loop"),
    "s02": ("S02-golden-evals", "s02_scripted_user_eval_toy", "s02_evals"),
    "s03": ("S03-context-engineering", "s03_context_engineering_toy", "s03_context"),
    "s04": ("S04-structured-generation", "s04_structured_generation_toy", "s04_schema"),
    "s05": ("S05-consent-gate", "s05_consent_gate_toy", "s05_consent"),
    "s06": ("S06-layered-detection", "s06_layered_detection_toy", "s06_policy"),
    "s07": ("S07-repair-loop", "s07_repair_loop_toy", "s07_repair"),
    "s08": ("S08-observability-replay", "s08_observability_replay_toy", "s08_replay"),
    "s09": ("S09-evidence-reports", "s09_evidence_report_toy", "s09_debrief"),
    "s10": ("S10-error-analysis", "s10_error_analysis_toy", "s10_errors"),
    "s11": ("S11-budgets-routing", "s11_budgets_routing_toy", "s11_budgets"),
    "s12": ("S12-judge-calibration", "s12_judge_calibration_toy", "s12_judge"),
}

EXPECTED_PREDICT_CELL_IDS = {
    "s01": ["69a77fc3", "fd87655a", "15f7e677"],
    "s02": ["9bdffa54", "d3af51d7"],
    "s03": ["a8d55878", "85285862", "e094f110", "aaf16a92", "94033064"],
    "s04": ["e1a23bb2", "6f167291", "7da61be9", "1a4099fe"],
    "s05": ["65dad055", "131facd6", "e2055409", "360ae6a9", "4c3086d8"],
    "s06": ["e6e094bc", "db8764ff", "6fd1e028", "17fc4b40", "eb3312f1"],
    "s07": ["0dfeb0fb", "17144688", "860d1ba8", "87ade9f5", "e78b53c8"],
    "s08": ["a0bcdfb0", "5e7deaae", "a46de06c", "c7bbf262", "4d8877aa"],
    "s09": ["9be8b060", "a555e356", "6216d055", "c082f091", "f3687a78"],
    "s10": ["e29ddac3", "de444d72", "1ed050d0", "06f30ddd"],
    "s11": ["2c72bb15", "c05d5679", "8d2df87f", "3b20842f", "bb698748"],
    "s12": ["b894417f", "59b0dc59", "acdca975", "a6cbf006", "35f8b325", "0f450635"],
}

EXPECTED_EXPERIMENT_CELL_IDS = {
    "s01": ["ec494b3e", "5e6e3097", "fbcd8306", "12a87824"],
    "s02": ["3c77d029", "a2aa48cf"],
    "s03": ["dcf56abf", "93ea5794", "90776c2a", "07bceb19", "09e960ee"],
    "s04": ["38e5ca91", "d8a80401", "09222764", "83a455b4"],
    "s05": ["25cf8dc2", "76836a57", "be1954da", "63b1cfda", "328db237"],
    "s06": ["ea33ec95", "e01f063b", "6f1086f9", "b13582e1", "5cfba0f0"],
    "s07": ["51a7a2df", "ac7c3f22", "378ed1dc", "e87d2e76", "3333d37f"],
    "s08": ["36cb568f", "84af535b", "861de2de", "41138c1d", "6ebe4cbf", "c31c250b"],
    "s09": ["c676a909", "fdc6245d", "f7d9581f", "b399e7d0", "2a5279ba"],
    "s10": ["69244ac3", "c3ba0e2b", "03d0a7b8"],
    "s11": ["e2126f69", "64044c9e", "3ac65de6", "17c6235c", "6d57264e"],
    "s12": ["64fcf43f", "32fe1e01", "a2358ced", "323068e0", "9da60997"],
}

EXPECTED_SOURCE_PATHS = {
    "s01": {"labs/trivia_host/tools.py", "labs/trivia_host/loop.py", "labs/trivia_host/engine.py"},
    "s02": {"labs/trivia_host/engine.py", "labs/evals/tasks.py", "labs/evals/checkers.py"},
    "s03": {"labs/trivia_host/engine.py", "labs/house_rules.py"},
    "s04": {"labs/trivia_host/tools.py", "labs/schemas.py"},
    "s05": {"labs/trivia_host/engine.py", "labs/schemas.py"},
    "s06": {"labs/trivia_host/engine.py", "labs/trivia_host/tools.py"},
    "s07": {"labs/trivia_host/loop.py", "labs/trivia_host/engine.py"},
    "s08": {"labs/client.py", "labs/trivia_host/engine.py"},
    "s09": {"labs/trivia_host/engine.py"},
    "s10": {"labs/evals/tasks.py", "labs/evals/checkers.py"},
    "s11": {"labs/trivia_host/engine.py", "labs/client.py"},
    "s12": {"labs/evals/checkers.py", "labs/evals/tasks.py"},
    "s13": {"labs/trivia_host/tools.py", "labs/trivia_host/loop.py", "labs/trivia_host/engine.py"},
    "s14": {"labs/run.py", "labs/test_contracts.py"},
}


def load_manifest_data() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def phase_map(module: dict[str, object]) -> dict[str, dict[str, object]]:
    return {phase["id"]: phase for phase in module["phases"]}


def all_surfaces(manifest: dict[str, object]) -> list[dict[str, object]]:
    return [
        surface
        for module in manifest["modules"]
        for phase in module["phases"]
        for surface in phase["surfaces"]
    ]


class CourseWeaveManifestTests(unittest.TestCase):
    def test_s01_is_a_complete_predict_first_slice(self) -> None:
        """Catch a missing or incomplete first module before expansion to S02-S14."""

        self.assertTrue(MANIFEST_PATH.is_file(), "courseweave.json must exist")
        manifest = load_manifest_data()
        s01 = manifest["modules"][0]
        self.assertEqual(s01["id"], "s01")

        phases = {phase["id"]: phase for phase in s01["phases"]}
        self.assertEqual(list(phases), ["read", "watch", "predict", "experiment", "lab"])
        self.assertEqual(phases["predict"]["kind"], "predict")
        self.assertEqual(
            phases["predict"]["completion"],
            {"type": "prediction_recorded", "record_id": "s01-prediction"},
        )

        surfaces = [
            surface
            for phase in s01["phases"]
            for surface in phase["surfaces"]
        ]
        local_paths = {surface.get("path") for surface in surfaces}
        self.assertIn("lessons/S01-agent-loop.html", local_paths)
        self.assertIn("notebooks/s01_agent_loop_toy.ipynb", local_paths)
        self.assertIn("labs/s01_loop.md", local_paths)
        self.assertIn("labs/trivia_host/loop.py", local_paths)

        video = next(surface for surface in surfaces if surface["type"] == "video")
        self.assertEqual(
            video["url"],
            "https://storage.googleapis.com/"
            "macayaven-agent-harness-path-videos/S01-agent-loop.mp4",
        )
        self.assertNotIn("path", video)

        notebook_surfaces = [
            surface for surface in surfaces if surface["type"] == "notebook"
        ]
        self.assertEqual(
            notebook_surfaces[0]["match"]["cell_ids"],
            ["69a77fc3", "fd87655a", "15f7e677"],
        )
        all_cell_ids = {
            cell["id"]
            for cell in json.loads(
                (ROOT / "notebooks/s01_agent_loop_toy.ipynb").read_text(
                    encoding="utf-8"
                )
            )["cells"]
        }
        for surface in notebook_surfaces:
            self.assertLessEqual(set(surface["match"]["cell_ids"]), all_cell_ids)

        terminal = next(
            surface for surface in surfaces if surface["type"] == "terminal"
        )
        self.assertEqual(
            terminal["argv"],
            ["uv", "run", "python", "labs/run.py", "--session", "s01", "--replay"],
        )
        self.assertEqual(terminal["cwd"], ".")

    def test_manifest_maps_every_session_and_public_video(self) -> None:
        """Catch a missing course session or a non-playable local-video selection."""

        manifest = load_manifest_data()
        modules = {module["id"]: module for module in manifest["modules"]}
        self.assertEqual(list(modules), [f"s{number:02d}" for number in range(1, 15)])

        for module_id, (lesson_slug, notebook_slug, lab_slug) in EXPECTED_MODULES.items():
            phases = phase_map(modules[module_id])
            self.assertEqual(
                list(phases), ["read", "watch", "predict", "experiment", "lab"]
            )
            surfaces = [
                surface
                for phase in modules[module_id]["phases"]
                for surface in phase["surfaces"]
            ]
            self.assertIn(
                f"lessons/{lesson_slug}.html",
                {surface.get("path") for surface in surfaces},
            )
            self.assertIn(
                f"notebooks/{notebook_slug}.ipynb",
                {surface.get("path") for surface in surfaces},
            )
            self.assertIn(
                f"labs/{lab_slug}.md",
                {surface.get("path") for surface in surfaces},
            )
            video = next(surface for surface in surfaces if surface["type"] == "video")
            self.assertEqual(
                video,
                {
                    "id": "video",
                    "type": "video",
                    "role": "reference",
                    "url": "https://storage.googleapis.com/"
                    f"macayaven-agent-harness-path-videos/{lesson_slug}.mp4",
                },
            )

        for module_id, lesson_slug in {
            "s13": "S13-rebuild-from-memory",
            "s14": "S14-ship-and-pilot",
        }.items():
            paths = {
                surface.get("path")
                for phase in modules[module_id]["phases"]
                for surface in phase["surfaces"]
            }
            self.assertIn(f"lessons/{lesson_slug}.html", paths)
            video = next(
                surface
                for phase in modules[module_id]["phases"]
                for surface in phase["surfaces"]
                if surface["type"] == "video"
            )
            self.assertEqual(
                video["url"],
                "https://storage.googleapis.com/"
                f"macayaven-agent-harness-path-videos/{lesson_slug}.mp4",
            )
            self.assertNotIn("path", video)

    def test_predict_and_experiment_cell_ids_are_real_and_disjoint(self) -> None:
        """Catch stale notebook matches and prediction cells that reveal solutions."""

        modules = {module["id"]: module for module in load_manifest_data()["modules"]}
        for module_id, (_, notebook_slug, _) in EXPECTED_MODULES.items():
            self.assertIn(module_id, modules)
            notebook = json.loads(
                (ROOT / f"notebooks/{notebook_slug}.ipynb").read_text(encoding="utf-8")
            )
            cells = {cell["id"]: cell for cell in notebook["cells"]}
            phases = phase_map(modules[module_id])
            predict_match = phases["predict"]["surfaces"][0]["match"]
            experiment_match = phases["experiment"]["surfaces"][0]["match"]
            self.assertEqual(
                predict_match["cell_ids"], EXPECTED_PREDICT_CELL_IDS[module_id]
            )
            self.assertEqual(
                experiment_match["cell_ids"], EXPECTED_EXPERIMENT_CELL_IDS[module_id]
            )
            self.assertLessEqual(set(predict_match["cell_ids"]), set(cells))
            self.assertLessEqual(set(experiment_match["cell_ids"]), set(cells))
            self.assertTrue(
                set(predict_match["cell_ids"]).isdisjoint(
                    experiment_match["cell_ids"]
                )
            )

    def test_phase_completion_and_capability_policies_preserve_learner_ownership(self) -> None:
        """Catch phase reordering, unlocked predictions, or teacher mutation authority."""

        manifest = load_manifest_data()
        self.assertEqual(
            manifest["policies"],
            {
                "content_sharing": "explicit_only",
                "durable_mutation": "proposal_or_direct_student_action",
                "terminal_execution": "student_only",
                "conversation_memory": "session_only",
                "max_shared_chars": 8192,
                "workspace_write_globs": [],
            },
        )
        for module in manifest["modules"][:12]:
            phases = phase_map(module)
            self.assertLess(
                list(phases).index("predict"), list(phases).index("experiment")
            )
            self.assertEqual(phases["predict"]["kind"], "predict")
            self.assertEqual(phases["predict"]["teacher_mode"], "socratic_guide")
            self.assertEqual(
                phases["predict"]["completion"],
                {
                    "type": "prediction_recorded",
                    "record_id": f"{module['id']}-prediction",
                },
            )
            self.assertEqual(phases["predict"]["capabilities"]["hint_level"], "none")
            for phase in module["phases"]:
                capabilities = phase["capabilities"]
                self.assertFalse(capabilities["create_profile_proposal"])
                self.assertFalse(capabilities["create_course_proposal"])
                self.assertFalse(capabilities["create_workspace_proposal"])

    def test_s13_is_observer_only_and_s14_is_verification_ship(self) -> None:
        """Catch substantive audit help or mutation-capable release coaching."""

        modules = {module["id"]: module for module in load_manifest_data()["modules"]}
        self.assertIn("s13", modules)
        self.assertIn("s14", modules)
        self.assertEqual([phase["id"] for phase in modules["s13"]["phases"]], ["audit"])
        audit = modules["s13"]["phases"][0]
        self.assertEqual((audit["kind"], audit["teacher_mode"]), ("audit", "observer"))
        self.assertEqual(
            audit["completion"],
            {"type": "receipt_recorded", "record_id": "s13-audit-receipt"},
        )
        self.assertEqual(audit["capabilities"]["hint_level"], "none")

        self.assertEqual([phase["id"] for phase in modules["s14"]["phases"]], ["ship"])
        ship = modules["s14"]["phases"][0]
        self.assertEqual((ship["kind"], ship["teacher_mode"]), ("ship", "reviewer"))
        self.assertEqual(
            ship["completion"],
            {"type": "receipt_recorded", "record_id": "s14-ship-receipt"},
        )
        for phase in (audit, ship):
            capabilities = phase["capabilities"]
            self.assertFalse(capabilities["create_profile_proposal"])
            self.assertFalse(capabilities["create_course_proposal"])
            self.assertFalse(capabilities["create_workspace_proposal"])

    def test_ids_are_unique_in_their_schema_scopes(self) -> None:
        """Catch ambiguous module, phase, or surface resolution."""

        manifest = load_manifest_data()
        module_ids = [module["id"] for module in manifest["modules"]]
        self.assertEqual(len(module_ids), len(set(module_ids)))
        for module in manifest["modules"]:
            phase_ids = [phase["id"] for phase in module["phases"]]
            self.assertEqual(len(phase_ids), len(set(phase_ids)))
            for phase in module["phases"]:
                surface_ids = [surface["id"] for surface in phase["surfaces"]]
                self.assertEqual(len(surface_ids), len(set(surface_ids)))

    def test_all_local_paths_exist_and_resolve_inside_the_course(self) -> None:
        """Catch missing artifacts, parent traversal, and symlink jail escapes."""

        manifest = load_manifest_data()
        root = ROOT.resolve()
        for surface in all_surfaces(manifest):
            relative = surface.get("path")
            if relative is None:
                relative = surface.get("cwd")
            if relative is None:
                continue
            target = (ROOT / relative).resolve()
            self.assertTrue(target.is_relative_to(root), relative)
            if surface["type"] == "terminal":
                self.assertTrue(target.is_dir(), relative)
            else:
                self.assertTrue(target.is_file(), relative)

    def test_relevant_learner_python_surfaces_are_mapped(self) -> None:
        """Catch a session whose lab opens prose but omits the code under study."""

        modules = {module["id"]: module for module in load_manifest_data()["modules"]}
        for module_id, expected_paths in EXPECTED_SOURCE_PATHS.items():
            actual_paths = {
                surface["path"]
                for phase in modules[module_id]["phases"]
                for surface in phase["surfaces"]
                if surface["type"] == "source"
            }
            self.assertEqual(actual_paths, expected_paths)

    def test_terminal_surfaces_are_structured_offline_copy_only_commands(self) -> None:
        """Catch shell strings, live mode, or commands outside the replay runner."""

        terminals = [
            surface
            for surface in all_surfaces(load_manifest_data())
            if surface["type"] == "terminal"
        ]
        self.assertEqual(len(terminals), 13)
        for terminal in terminals:
            argv = terminal["argv"]
            self.assertIsInstance(argv, list)
            self.assertEqual(argv[:4], ["uv", "run", "python", "labs/run.py"])
            self.assertIn("--replay", argv)
            self.assertNotIn("--live", argv)
            self.assertEqual(terminal["cwd"], ".")
            self.assertIn("Copy", terminal["label"])

    def test_platform_loader_and_resolver_accept_every_phase(self) -> None:
        """Catch drift from the real CourseWeave schema, jail, and resolver contract."""

        platform_root = ROOT.parent / "courseweave"
        if not (platform_root / "src/courseweave/manifest.py").is_file():
            self.skipTest("exact sibling CourseWeave checkout is unavailable")
        python = platform_root / ".venv/bin/python"
        if not python.is_file():
            self.skipTest("exact sibling CourseWeave environment is unavailable")
        program = """
import json
import sys
from pathlib import Path
from courseweave.context import resolve_context
from courseweave.manifest import load_manifest
from courseweave.models import ResolutionState, WorkspaceContext

manifest = load_manifest(Path(sys.argv[1]), runnable=True)
resolved_phases = []
for sequence, module in enumerate(manifest.modules, start=1):
    for phase in module.phases:
        for surface_index, surface in enumerate(phase.surfaces):
            context_data = {
                "source_id": "adapter-contract",
                "sequence": sequence * 100 + surface_index,
            }
            state = ResolutionState(
                last_module_id=module.id,
                last_phase_id=phase.id,
            )
            if surface.type == "notebook":
                context_data["active_path"] = surface.path
                if surface.match and surface.match.cell_ids:
                    context_data["active_cell_id"] = surface.match.cell_ids[0]
            elif surface.type == "terminal":
                context_data["explicit_module_id"] = module.id
                context_data["terminal_surface_id"] = surface.id
            elif getattr(surface, "path", None) is not None:
                context_data["active_path"] = surface.path
            else:
                context_data["explicit_module_id"] = module.id
                context_data["explicit_phase_id"] = phase.id
            resolved = resolve_context(
                manifest,
                state,
                WorkspaceContext(**context_data),
            )
            assert (resolved.module_id, resolved.phase_id) == (module.id, phase.id)
        resolved_phases.append([module.id, phase.id])
print(json.dumps(resolved_phases))
"""
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(platform_root / "src")
        result = subprocess.run(
            [str(python), "-c", program, str(ROOT)],
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = [
            [module["id"], phase["id"]]
            for module in load_manifest_data()["modules"]
            for phase in module["phases"]
        ]
        self.assertEqual(json.loads(result.stdout), expected)


class CourseWeaveLauncherTests(unittest.TestCase):
    def _write_executable(self, path: Path, body: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(0o755)

    def test_installed_courseweave_is_execed_with_argv_intact(self) -> None:
        """Catch lossy argument joining or a non-learner default subcommand."""

        self.assertTrue(LAUNCHER_PATH.is_file())
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            capture = temp / "args.txt"
            self._write_executable(
                temp / "bin/courseweave", 'printf "%s\\n" "$@" > "$CAPTURE_PATH"'
            )
            environment = os.environ.copy()
            environment["PATH"] = f"{temp / 'bin'}:/usr/bin:/bin"
            environment["CAPTURE_PATH"] = str(capture)
            result = subprocess.run(
                [str(LAUNCHER_PATH), "--port", "9001"],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                capture.read_text(encoding="utf-8").splitlines(),
                ["launch", "--course-root", str(ROOT), "--port", "9001"],
            )

    def test_exact_sibling_checkout_is_the_only_source_fallback(self) -> None:
        """Catch CWD-dependent or arbitrary platform-checkout discovery."""

        self.assertTrue(LAUNCHER_PATH.is_file())
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            course_root = temp / "course with spaces"
            launcher = course_root / "scripts/courseweave"
            launcher.parent.mkdir(parents=True)
            shutil.copy2(LAUNCHER_PATH, launcher)
            sibling = course_root.parent / "courseweave"
            (sibling / "src/courseweave").mkdir(parents=True)
            (sibling / "pyproject.toml").write_text(
                '[project]\nname = "courseweave"\n', encoding="utf-8"
            )
            (sibling / "src/courseweave/cli.py").write_text("", encoding="utf-8")
            capture = temp / "uv-args.txt"
            self._write_executable(
                temp / "bin/uv", 'printf "%s\\n" "$@" > "$CAPTURE_PATH"'
            )
            environment = os.environ.copy()
            environment["PATH"] = f"{temp / 'bin'}:/usr/bin:/bin"
            environment["CAPTURE_PATH"] = str(capture)
            result = subprocess.run(
                [str(launcher), "--port", "9002"],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                capture.read_text(encoding="utf-8").splitlines(),
                [
                    "run",
                    "--project",
                    str(sibling.resolve()),
                    "courseweave",
                    "launch",
                    "--course-root",
                    str(course_root.resolve()),
                    "--port",
                    "9002",
                ],
            )

    def test_missing_installed_and_sibling_courseweave_fails_clearly(self) -> None:
        """Catch silent fallback to an unrelated interpreter or checkout."""

        self.assertTrue(LAUNCHER_PATH.is_file())
        with tempfile.TemporaryDirectory() as directory:
            course_root = Path(directory) / "course"
            launcher = course_root / "scripts/courseweave"
            launcher.parent.mkdir(parents=True)
            shutil.copy2(LAUNCHER_PATH, launcher)
            environment = os.environ.copy()
            environment["PATH"] = "/usr/bin:/bin"
            result = subprocess.run(
                [str(launcher)],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(result.returncode, 127)
            self.assertIn("install CourseWeave or place its checkout at", result.stderr)

    def test_launcher_does_not_execute_manifest_terminal_argv(self) -> None:
        """Catch adapter-side command autonomy before CourseWeave owns the launch."""

        self.assertTrue(LAUNCHER_PATH.is_file())
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            course_root = temp / "course"
            launcher = course_root / "scripts/courseweave"
            launcher.parent.mkdir(parents=True)
            shutil.copy2(LAUNCHER_PATH, launcher)
            marker = temp / "must-not-exist"
            (course_root / "courseweave.json").write_text(
                json.dumps({"terminal": {"argv": ["touch", str(marker)]}}),
                encoding="utf-8",
            )
            self._write_executable(temp / "bin/courseweave", "exit 0")
            environment = os.environ.copy()
            environment["PATH"] = f"{temp / 'bin'}:/usr/bin:/bin"
            result = subprocess.run(
                [str(launcher)],
                text=True,
                capture_output=True,
                env=environment,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists())


class CourseWeaveDocumentationTests(unittest.TestCase):
    def test_courseweave_state_is_ignored(self) -> None:
        """Catch learner state becoming a tracked course artifact."""

        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".courseweave/", ignored)

    def test_quickstart_is_recommended_optional_and_preserves_offline_route(self) -> None:
        """Catch CourseWeave replacing the existing zero-network course path."""

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Recommended optional CourseWeave experience", readme)
        courseweave_section = readme.split(
            "## Recommended optional CourseWeave experience", maxsplit=1
        )[1]
        self.assertIn("./scripts/courseweave", courseweave_section)
        self.assertIn("optional", courseweave_section.lower())
        self.assertIn("uv run jupyter lab", readme)
        self.assertIn("zero network", readme.lower())

    def test_adapter_adds_no_secret_or_live_execution_coupling(self) -> None:
        """Catch credential discovery, live mode, or network clients in adapter wiring."""

        manifest = load_manifest_data()
        serialized = json.dumps(manifest)
        self.assertTrue(LAUNCHER_PATH.is_file())
        launcher = LAUNCHER_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "--live",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "COURSEWEAVE_CAPABILITY_TOKEN",
            "curl ",
            "wget ",
        ):
            self.assertNotIn(forbidden, serialized)
            self.assertNotIn(forbidden, launcher)


if __name__ == "__main__":
    unittest.main()
