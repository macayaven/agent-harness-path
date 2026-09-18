#!/usr/bin/env python3
"""Re-render course Mermaid with the pinned optional Playwright dependency.

--check compares fresh renders with committed files on the same renderer/font host.
Ordinary lesson builds only verify the source/options/tooling and asset hashes.
"""
import argparse
import importlib.metadata
import json
import platform
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from static_diagrams import (
    ALTERNATIVES,
    HERE,
    NOTEBOOK_ALTERNATIVES,
    NOTEBOOK_SESSIONS,
    OPTIONS,
    SESSIONS,
    VIEWPORT,
    asset_name,
    diagram_path,
    inputs,
    lesson_source,
    sha,
)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    receipt={'environment':{'playwright':importlib.metadata.version('playwright'),
                            'system':platform.system(), 'machine':platform.machine(),
                            'font':'Arial, sans-serif; host font resolution'}, 'diagrams':{}}
    generated={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        receipt['environment']['chromium']=browser.version
        def render(source, asset, alternative):
            source_hash=sha(source.encode())
            renders=[]
            for _ in range(2):
                page=browser.new_page(viewport=VIEWPORT)
                page.set_content('<!doctype html><html><body style="margin:0;font-family:Arial,sans-serif"></body></html>')
                page.add_script_tag(path=str(HERE/'vendor/mermaid.min.js'))
                svg=page.evaluate('''async ({source, options, seed}) => {
                  mermaid.initialize({...options, deterministicIDSeed:seed});
                  return (await mermaid.render('ahp-'+seed.slice(0,16),source)).svg;
                }''',{'source':source,'options':OPTIONS,'seed':source_hash})
                # Meaningful native SVG description survives use outside the HTML img.
                import html
                svg=svg.replace('&amp;gt;', '&gt;')
                svg=svg.replace('>', '><title>'+html.escape(asset)+'</title><desc>'+html.escape(alternative)+'</desc>',1)+'\n'
                renders.append(svg.encode());page.close()
            if renders[0]!=renders[1]:raise ValueError(f'{asset}: two fresh pages rendered different bytes')
            return renders[0]
        for slug in sorted(ALTERNATIVES):
            text=lesson_source(slug).read_text()
            blocks=re.findall(r'```mermaid\n(.*?)```',text,re.S)
            if len(blocks)!=len(ALTERNATIVES[slug]):
                raise ValueError(f'{slug}: expected {len(ALTERNATIVES[slug])} diagram(s), found {len(blocks)}')
            for index, block in enumerate(blocks):
                source=block.strip()
                asset=asset_name(slug,index)
                data=render(source,asset,ALTERNATIVES[slug][index])
                dest=diagram_path(slug,asset).parent
                generated[(dest,f'{asset}.svg')]=data
                receipt['diagrams'][asset]={'inputs':inputs(source),'svg_sha256':sha(data)}
        for asset in sorted(NOTEBOOK_ALTERNATIVES):
            dest=SESSIONS/NOTEBOOK_SESSIONS[asset]/'public'/'diagrams'
            source=(dest/f'{asset}.mmd').read_text().strip()
            data=render(source,asset,NOTEBOOK_ALTERNATIVES[asset][0])
            generated[(dest,f'{asset}.svg')]=data
            receipt['diagrams'][asset]={'inputs':inputs(source),'svg_sha256':sha(data)}
        browser.close()
    generated[(HERE,'receipt.json')]=(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n').encode()
    if args.check:
        for (dest,name),data in generated.items():
            if not (dest/name).is_file() or (dest/name).read_bytes()!=data:
                rel=dest.relative_to(HERE.parent)
                raise SystemExit(f'{rel}/{name}: fresh render differs; environment recorded in receipt.json')
        print('Two fresh pages per diagram match committed SVG and receipt on this host.')
    else:
        for (dest,name),data in generated.items():
            dest.mkdir(parents=True,exist_ok=True);(dest/name).write_bytes(data)
        print(f'Rendered {len(receipt["diagrams"])} static course diagrams; verified two fresh pages each.')


if __name__=='__main__':main()
