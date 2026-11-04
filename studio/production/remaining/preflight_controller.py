"""Prepare root episode assets/stills as selected media and narration finish.

This never renders a canonical export or claims visual/listening acceptance.
The producer must inspect the resulting pictures and actual text previews.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import time

import yaml

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'studio/production/remaining'


def main():
    while True:
        control=json.loads((BASE/'tts-control.json').read_text())
        if control.get('stop_after_current'):
            return
        waiting=[]
        for section in control['sections']:
            episode=ROOT/'studio/episodes'/section
            if (episode/'render.json').exists() or (episode/'prepared-preflight.json').exists():
                continue
            source=episode/'media-sources.json'
            metrics=ROOT/'studio/media'/section/'narration/metrics.json'
            pictures=episode/'foreground-assets.json'
            if not all(p.exists() for p in [source,metrics,pictures]):
                waiting.append(section)
                continue
            script=yaml.safe_load((episode/'script.yaml').read_text())
            data=json.loads(metrics.read_text())
            if [r['sentence_id'] for r in data]!=[r['sentence_id'] for r in script['sentences']]:
                waiting.append(section)
                continue
            commands=[
                ['studio/runtime/.venv/bin/python','studio/production/remaining/fit_text.py',section],
                ['studio/runtime/.venv/bin/python','studio/episodes/'+section+'/prepare_assets.py'],
                ['studio/runtime/.venv/bin/python','studio/tools/validate_assets.py',section],
                ['studio/runtime/.venv/bin/python','studio/tools/render.py',section,'--stills-only'],
                ['.venv/bin/python','studio/tools/script.py','review',section,'--ready'],
                ['.venv/bin/python','studio/tools/script.py','validate',section,'--ready'],
                ['.venv/bin/python','studio/tools/picture_coverage.py',section,'--planned','--require-target'],
                ['.venv/bin/python','studio/production/remaining/picture_diversity.py',section],
            ]
            for command in commands:
                print('Preflight:', ' '.join(command),flush=True)
                subprocess.run(command,cwd=ROOT,check=True)
            record=dict(section_id=section,
                script_sha256=hashlib.sha256((episode/'script.yaml').read_bytes()).hexdigest(),
                assets_sha256=hashlib.sha256((episode/'assets.yaml').read_bytes()).hexdigest(),
                technical_preflight=True,producer_visual_review=False,
                narration_diagnostic_review='Separate current-hash ASR required before export',
                whole_video_listening=False,user_acceptance=False)
            (episode/'prepared-preflight.json').write_text(json.dumps(record,indent=2)+'\n')
        (BASE/'preflight-controller-progress.json').write_text(json.dumps(dict(waiting=waiting,status='waiting' if waiting else 'complete'),indent=2)+'\n')
        if not waiting:
            return
        time.sleep(30)


if __name__=='__main__':main()
