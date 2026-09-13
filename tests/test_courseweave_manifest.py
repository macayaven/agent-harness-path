"""Native adapter/content checks; real installed contract: scripts/verify_courseweave.py."""
from __future__ import annotations
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LAUNCHER_PATH = ROOT / "scripts/courseweave"
MANIFEST_PATH = ROOT / "courseweave.json"
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
    "s09": ["9be8b060", "a555e356", "6216d055", "c082f091", "f3687a78", "1e9aff30", "fc8aee1d", "3b5d8f4f"],
    "s10": ["e29ddac3", "de444d72", "1ed050d0"],
    "s11": ["2c72bb15", "c05d5679", "8d2df87f", "3b20842f", "bb698748"],
    "s12": ["b894417f", "acdca975", "a6cbf006", "35f8b325", "0f450635"],
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
    "s10": ["69244ac3", "c3ba0e2b", "03d0a7b8", "06f30ddd"],
    "s11": ["e2126f69", "64044c9e", "3ac65de6", "17c6235c", "6d57264e"],
    "s12": ["59b0dc59", "64fcf43f", "32fe1e01", "a2358ced", "323068e0", "9da60997"],
}

EXPECTED_SOURCE_PATHS = {
    "s01": {
        "labs/client.py",
        "labs/deck.py",
        "labs/house_rules.py",
        "labs/schemas.py",
        "labs/trivia_host/tools.py",
        "labs/trivia_host/loop.py",
        "labs/trivia_host/engine.py",
    },
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



def load_manifest_data():
    return json.loads(MANIFEST_PATH.read_text())

def phase_map(module):
    return {phase["id"]: phase for phase in module["phases"]}

def all_surfaces(manifest):
    return [s for m in manifest["modules"] for p in m["phases"] for s in p["surfaces"]]

class CourseWeaveManifestTests(unittest.TestCase):
    def test_practical_suite_commands_select_the_student_implementation(self):
        import importlib.util
        import re
        import shlex
        import sys
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location("pilot_lab_runner", ROOT/"labs/run.py")
        runner = importlib.util.module_from_spec(spec)
        with patch.object(sys, "path", [str(ROOT/"labs"), *sys.path]):
            spec.loader.exec_module(runner)
        commands = [shlex.split(command)[4:] for command in re.findall(
            r"`(uv run python labs/run.py[^`]+)`",
            (ROOT/"lessons/src/S13-rebuild-from-memory.md").read_text(),
        )]
        review = phase_map(load_manifest_data()["modules"][13])["review"]
        commands.extend(surface["command"][4:] for surface in review["surfaces"]
                        if surface["id"] == "replay-command")
        self.assertGreaterEqual(len(commands), 3)
        # Stop before any execution: prove the real CLI selects the learner's
        # implementation, even though --all defaults to the reference.
        for args in commands:
            with patch.object(runner, "load_impl", side_effect=RuntimeError("selection observed")) as selected:
                with self.assertRaisesRegex(RuntimeError, "selection observed"):
                    runner.main(args)
            selected.assert_called_once_with("student")

    def test_lesson_scope_labels_identify_the_session_after_navigation(self):
        labels = []
        for module in load_manifest_data()["modules"]:
            for phase in module["phases"]:
                for surface in phase["surfaces"]:
                    if surface["type"] in {"html", "markdown"}:
                        self.assertIn(module["id"].upper(), surface["label"])
                        labels.append(surface["label"])
        self.assertEqual(len(labels), len(set(labels)))

    def test_v2_read_notebook_self_check_optional_lab_route(self):
        manifest = load_manifest_data()
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual([m["id"] for m in manifest["modules"]], [f"s{n:02d}" for n in range(1,15)])
        for module in manifest["modules"][:12]:
            phases = phase_map(module)
            self.assertEqual(list(phases), ["read", "notebook", "self-check", "lab"])
            self.assertEqual([p["progress"] for p in phases.values()], ["required"]*3+["optional"])
            self.assertEqual(phases["read"]["surfaces"][0]["fragment"], "the-theory-in-depth")
            self.assertEqual(phases["self-check"]["surfaces"][0]["fragment"], "self-check")
            self.assertEqual(phases["notebook"]["teacher"]["access"]["requires"], [module["id"]+"-prediction"])
            self.assertEqual(len(phases["notebook"]["completion"]["requirements"]), 3)
            self.assertEqual(phases["notebook"]["surfaces"][0]["id"], "notebook")
            self.assertEqual(phases["notebook"]["surfaces"][0]["purpose"], "primary")
            self.assertTrue(phases["self-check"]["learning"]["checks"])
            for phase in phases.values():
                learning = phase["learning"]
                self.assertTrue(learning["objectives"])
                self.assertTrue(learning["overview"])
                self.assertTrue(learning["hints"])
            for check in phases["self-check"]["learning"]["checks"]:
                self.assertTrue(all(option["feedback"] for option in check["options"]))
        self.assertNotIn("limited guidance", json.dumps(manifest).lower())

    def test_maps_every_course_file_video_and_original_prediction_cell(self):
        modules = {m["id"]:m for m in load_manifest_data()["modules"]}
        for mid,(lesson, notebook, lab) in EXPECTED_MODULES.items():
            surfaces = all_surfaces({"modules":[modules[mid]]})
            paths = {s.get("path") for s in surfaces}
            self.assertTrue({f"lessons/{lesson}.html",f"notebooks/{notebook}.ipynb",f"labs/{lab}.md"} <= paths)
            self.assertEqual(next(s for s in surfaces if s["type"]=="video")["src"],
                f"https://storage.googleapis.com/macayaven-agent-harness-path-videos/{lesson}.mp4")
            cells = {c["id"]:c for c in json.loads((ROOT/f"notebooks/{notebook}.ipynb").read_text())["cells"]}
            selected = set()
            for surface in surfaces:
                if surface["type"]=="notebook":
                    ids = set(surface["selector"]["values"])
                    self.assertTrue(ids <= cells.keys())
                    selected |= ids
            self.assertTrue(set(EXPECTED_PREDICT_CELL_IDS[mid]) <= selected)
            # The complete notebook remains runnable, while pre-attempt grounding
            # selects the original prediction/attempt cells rather than answers.
            self.assertTrue(selected.isdisjoint(EXPECTED_EXPERIMENT_CELL_IDS[mid]))
            self.assertTrue(set(EXPECTED_EXPERIMENT_CELL_IDS[mid]) <= cells.keys())
            self.assertFalse(any("# SOLUTION" in "".join(cells[c]["source"]) for c in selected))
        for mid, expected in EXPECTED_SOURCE_PATHS.items():
            self.assertEqual({s["path"] for s in all_surfaces({"modules":[modules[mid]]}) if s["type"]=="source"}, expected)
        for mid, slug in {"s13":"S13-rebuild-from-memory","s14":"S14-ship-and-pilot"}.items():
            surfaces = all_surfaces({"modules":[modules[mid]]})
            self.assertIn(f"lessons/{slug}.html", {s.get("path") for s in surfaces})
            self.assertTrue(next(s for s in surfaces if s["type"]=="video")["src"].endswith(slug+".mp4"))
            self.assertFalse(any(s["type"] == "notebook" for s in surfaces))
            self.assertTrue(all(p["progress"] == "optional" for p in modules[mid]["phases"]))

    def test_practical_protocols_separate_unaided_work_from_permitted_review(self):
        modules = {m["id"]: phase_map(m) for m in load_manifest_data()["modules"]}
        for mid, pid in [("s13", "audit"), ("s14", "acceptance"), ("s14", "pilot")]:
            phase = modules[mid][pid]
            self.assertEqual(phase["teacher"]["access"], {"mode": "observer_only", "requires": []})
            self.assertEqual(phase["teacher"]["sharing"]["allow"], [])
            self.assertEqual(phase["teacher"]["proposals"]["allow"], [])
            self.assertEqual(phase["learning"]["hints"], [])
            self.assertFalse(any(s["type"] in {"source", "notebook"} for s in phase["surfaces"]))
        for mid in ["s13", "s14"]:
            review = modules[mid]["review"]
            self.assertEqual(review["teacher"]["access"], {"mode": "available", "requires": [mid+"-closed"]})
            self.assertTrue(review["learning"]["checks"])

    def test_unique_coordinates_local_jail_and_learner_authority(self):
        manifest = load_manifest_data()
        policies = manifest["policies"]
        self.assertEqual(policies["content_sharing"], "explicit_only")
        self.assertEqual(policies["durable_mutation"], "proposal_or_direct_student_action")
        self.assertEqual(policies["terminal_execution"], "student_only")
        self.assertEqual(policies["conversation_memory"], "session_only")
        self.assertEqual(policies["workspace_write_globs"], [])
        self.assertEqual(policies["allowed_proposal_types"], ["profile"])
        for module in manifest["modules"]:
            self.assertEqual(len(module["phases"]), len(phase_map(module)))
            for phase in module["phases"]:
                self.assertEqual(len(phase["surfaces"]), len({s["id"] for s in phase["surfaces"]}))
                self.assertFalse(set(phase["teacher"]["proposals"]["allow"]) - {"profile"})
        for s in all_surfaces(manifest):
            relative = s.get("path", s.get("cwd"))
            if relative:
                target = (ROOT / relative).resolve()
                self.assertTrue(target.is_relative_to(ROOT.resolve()), relative)
                self.assertTrue(target.is_dir() if s["type"]=="terminal" else target.is_file(), relative)

    def test_copy_commands_match_actual_lab_modes(self):
        modules = {m["id"]:m for m in load_manifest_data()["modules"]}
        terminals = [s for s in all_surfaces(load_manifest_data()) if s["type"]=="terminal"]
        self.assertEqual(len(terminals),16)  # original 14 replay commands + S01/S02 explicit live
        for s in terminals:
            self.assertEqual(s["command"][:4],["uv","run","python","labs/run.py"])
            self.assertEqual(s["cwd"],".")
            self.assertIn("Copy",s["label"])
            self.assertEqual(sum(flag in s["command"] for flag in ["--replay","--live"]),1)
        def commands(mid):
            return {s["id"]:s["command"] for s in all_surfaces({"modules":[modules[mid]]}) if s["type"]=="terminal"}
        self.assertEqual(commands("s06"), {"replay-command":["uv","run","python","labs/run.py","--session","s06","--replay","--impl","reference"]})
        self.assertEqual(commands("s08"), {"replay-command":["uv","run","python","labs/run.py","--session","s08","--replay"],"s01-replay-command":["uv","run","python","labs/run.py","--session","s01","--replay"]})

class CourseWeaveLauncherTests(unittest.TestCase):
    def test_explicit_interpreters_and_external_state_preserve_argv(self):
        with tempfile.TemporaryDirectory() as directory:
            temp=Path(directory); capture=temp/"args"
            platform=temp/"platform python"; kernel=temp/"kernel python"
            platform.write_text('#!/bin/sh\ncase "$*" in *--help*) echo --kernel-python;; *) printf "%s\\n" "$@" > "$CAPTURE_PATH";; esac\n')
            platform.chmod(0o755); kernel.write_text("unused"); kernel.chmod(0o755)
            result=subprocess.run([str(LAUNCHER_PATH),"--platform-python",str(platform),"--kernel-python",str(kernel),"--state-dir",str((temp/"state").resolve()),"--port","9001"],capture_output=True,text=True,env=os.environ|{"CAPTURE_PATH":str(capture)})
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(capture.read_text().splitlines(),["-m","courseweave","launch","--course-root",str(ROOT),"--kernel-python",str(kernel),"--state-dir",str((temp/"state").resolve()),"--port","9001"])
            self.assertIn("Course kernel",result.stderr)

    def test_no_implicit_path_or_sibling_discovery(self):
        result=subprocess.run([str(LAUNCHER_PATH)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("--platform-python",result.stderr)

    def test_unsupported_artifact_fails_before_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"old-python";p.write_text("#!/bin/sh\necho old-help\n");p.chmod(0o755)
            result=subprocess.run([str(LAUNCHER_PATH),"--platform-python",str(p),"--kernel-python",str(p),"--state-dir",directory],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn("pilot artifact",result.stderr)

    def test_manifest_commands_are_never_executed_and_path_functions_are_ignored(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            temp=Path(directory);course=temp/'course';(course/'scripts').mkdir(parents=True)
            launcher=course/'scripts/courseweave';shutil.copy2(LAUNCHER_PATH,launcher)
            marker=temp/'must-not-exist'
            (course/'courseweave.json').write_text(json.dumps({'terminal':{'command':['touch',str(marker)]}}))
            platform=temp/'platform';platform.write_text('#!/bin/sh\ncase "$*" in *--help*) echo --kernel-python;; *) exit 0;; esac\n');platform.chmod(0o755)
            kernel=temp/'kernel';kernel.symlink_to(platform)
            shell='courseweave() { touch "$MARKER"; }; export -f courseweave; exec "$@"'
            result=subprocess.run(['/bin/bash','-c',shell,'test',str(launcher),'--platform-python',str(platform),'--kernel-python',str(kernel),'--state-dir',str(temp/'state')],capture_output=True,text=True,env=os.environ|{'MARKER':str(marker)})
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertFalse(marker.exists())
            self.assertIn(str(kernel),result.stderr)
        for name in ["OPENAI_API_KEY","ANTHROPIC_API_KEY","curl ","wget "]:
            self.assertNotIn(name,LAUNCHER_PATH.read_text())

    def test_external_state_cannot_alias_course_or_its_ancestor(self):
        with tempfile.TemporaryDirectory() as directory:
            platform=Path(directory)/'platform';platform.write_text('#!/bin/sh\necho --kernel-python\n');platform.chmod(0o755)
            for state in [ROOT/'state',ROOT,ROOT.parent]:
                result=subprocess.run([str(LAUNCHER_PATH),'--platform-python',str(platform),'--kernel-python',str(platform),'--state-dir',str(state)],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('outside the course',result.stderr)

class CourseWeaveDocumentationTests(unittest.TestCase):
    def test_optional_native_route_and_external_state(self):
        readme=(ROOT/"README.md").read_text()
        self.assertIn("Recommended optional CourseWeave experience",readme)
        self.assertIn("uv run jupyter lab",readme)
        self.assertIn("zero network",readme.lower())
        self.assertIn("--platform-python",readme)
        self.assertIn(".courseweave/",(ROOT/".gitignore").read_text().splitlines())

if __name__=="__main__": unittest.main()
