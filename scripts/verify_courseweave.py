#!/usr/bin/env python3
"""Mandatory real installed-artifact adapter check; invoke with its Python -I.

No source fallback or conditional skip. This verifies read-only loader/resolver,
lesson grounding and launcher interface. Actual Jupyter/kernel/provider/browser
acceptance is performed by CourseWeave's installed-adapter suite.
"""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--course-root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args();root=args.course_root.resolve()
    import courseweave
    from courseweave.manifest import load_manifest
    from courseweave.context import resolve_context
    from courseweave.models import WorkspaceContext, ResolutionState
    from courseweave.teaching import lesson_scope
    from courseweave.engine.progress import bind_record, evaluate_progress
    from courseweave.engine.policy import effective_teacher_policy
    from courseweave.contracts.records import Coordinate
    package=Path(courseweave.__file__).resolve()
    assert package.is_relative_to(Path(sys.prefix).resolve()), f'Use an installed wheel, not editable/source import: {package}'
    before={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*')
            if p.is_file() and not any(part in {'.git','.venv','__pycache__'} for part in p.relative_to(root).parts)}
    manifest=load_manifest(root,runnable=True)
    assert manifest.schema_version==2
    progress=evaluate_progress(manifest,[],root)
    assert (progress.required_total,progress.required_complete)==(6,0)
    for mid in ('s01','s02'):
        assert not effective_teacher_policy(manifest,mid,'notebook',[]).provider_callable
        record=bind_record(manifest,Coordinate(module_id=mid,phase_id='notebook',requirement_id=mid+'-prediction'),{'text':'Synthetic adapter-test prediction; no learner outcome claimed.'})
        assert effective_teacher_policy(manifest,mid,'notebook',[record]).provider_callable
        progress=evaluate_progress(manifest,[record],root)
        assert not next(p for p in progress.phases if (p.module_id,p.phase_id)==(mid,'notebook')).complete
    coordinates=[]
    for module in manifest.modules:
        for phase in module.phases:
            for index,surface in enumerate(phase.surfaces):
                data={'source_id':'installed-adapter-check','sequence':index,
                      'explicit_module_id':module.id,'explicit_phase_id':phase.id,'surface_kind':surface.type}
                if getattr(surface,'path',None):data['active_path']=str(surface.path)
                if surface.type=='notebook':data['active_cell_id']=surface.selector.values[0]
                resolved=resolve_context(manifest,ResolutionState(),WorkspaceContext(**data))
                assert (resolved.module_id,resolved.phase_id,resolved.reason)==(module.id,phase.id,'explicit_phase')
                if getattr(surface,'path',None):assert resolved.surface_id==surface.id,(module.id,phase.id,surface.id,resolved)
                if module.id in {'s01','s02'} and surface.type=='html':
                    page=(root/str(surface.path)).read_text()
                    assert f'id="{surface.fragment}"' in page
                    scope=lesson_scope(root,manifest,resolved,'adapter-check','scope')
                    assert scope.omitted_sections
                    assert 'proposed_results = [' not in scope.excerpt
                    assert 'def useful_routine(reply)' not in scope.excerpt
                coordinates.append([module.id,phase.id,surface.id])
    help_result=subprocess.run([sys.executable,'-m','courseweave','launch','--help'],capture_output=True,text=True)
    assert help_result.returncode==0 and '--kernel-python' in help_result.stdout, 'Installed pilot must support launch --kernel-python; rebuild/install the final artifact.'
    after={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*')
           if p.is_file() and not any(part in {'.git','.venv','__pycache__'} for part in p.relative_to(root).parts)}
    assert before==after,'Read-only adapter verification changed course artifacts'
    print(json.dumps({'courseweave_version':importlib.metadata.version('courseweave'),
                      'python':sys.executable,'module_count':len(manifest.modules),
                      'surface_count':len(coordinates),'manifest_sha256':hashlib.sha256((root/'courseweave.json').read_bytes()).hexdigest(),
                      'read_only':True,'launcher_kernel_interface':True},indent=2))


if __name__=='__main__':main()
