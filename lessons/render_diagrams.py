#!/usr/bin/env python3
"""Re-render pilot Mermaid with the course's pinned optional Playwright dependency.

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
from static_diagrams import HERE, PILOT, OPTIONS, VIEWPORT, ALT, inputs, sha


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    out=HERE/'diagrams'
    receipt={'environment':{'playwright':importlib.metadata.version('playwright'),
                            'system':platform.system(), 'machine':platform.machine(),
                            'font':'Arial, sans-serif; host font resolution'}, 'diagrams':{}}
    generated={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        receipt['environment']['chromium']=browser.version
        for slug in sorted(PILOT):
            text=(HERE/'src'/f'{slug}.md').read_text()
            blocks=re.findall(r'```mermaid\n(.*?)```',text,re.S)
            if len(blocks)!=1:raise ValueError(f'{slug}: expected exactly one pilot diagram')
            source=blocks[0].strip(); source_hash=sha(source.encode())
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
                svg=svg.replace('>', '><title>'+html.escape(slug)+'</title><desc>'+html.escape(ALT[slug])+'</desc>',1)+'\n'
                renders.append(svg.encode());page.close()
            if renders[0]!=renders[1]:raise ValueError(f'{slug}: two fresh pages rendered different bytes')
            generated[f'{slug}.svg']=renders[0]
            receipt['diagrams'][slug]={'inputs':inputs(source),'svg_sha256':sha(renders[0])}
        browser.close()
    generated['receipt.json']=(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n').encode()
    if args.check:
        for name,data in generated.items():
            if not (out/name).is_file() or (out/name).read_bytes()!=data:
                raise SystemExit(f'{name}: fresh render differs; environment recorded in receipt.json')
        print('Two fresh pages per diagram match committed SVG and receipt on this host.')
    else:
        out.mkdir(exist_ok=True)
        for name,data in generated.items():(out/name).write_bytes(data)
        print('Rendered two static pilot diagrams; verified two fresh pages each.')


if __name__=='__main__':main()
