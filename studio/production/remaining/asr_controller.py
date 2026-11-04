"""Check completed root narration sets sequentially, preserving current results."""
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
        owners=yaml.safe_load((BASE/'queue.yaml').read_text())['episodes']
        waiting=False
        for section in control['sections']:
            if next(row['owner'] for row in owners if row['section_id']==section)!='root':
                raise ValueError('Not owned by root: '+section)
            narration=ROOT/'studio/media'/section/'narration'
            metrics_path=narration/'metrics.json'
            if not metrics_path.exists():
                waiting=True
                continue
            metrics=json.loads(metrics_path.read_text())
            script=yaml.safe_load((ROOT/'studio/episodes'/section/'script.yaml').read_text())
            if [m['sentence_id'] for m in metrics]!=[r['sentence_id'] for r in script['sentences']]:
                waiting=True
                continue
            current={str(ROOT/m['path']):hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest() for m in metrics}
            asr_path=narration/'asr.json'
            asr=json.loads(asr_path.read_text()) if asr_path.exists() else []
            if len(asr)==len(metrics) and all(current.get(str((ROOT/r['file']).resolve()))==r['sha256'] for r in asr):
                continue
            state_path=BASE/(section+'-asr-state.json')
            state=json.loads(state_path.read_text()) if state_path.exists() else {}
            if state.get('status')=='running':
                waiting=True
                continue
            config=dict(section_id=section,stage='asr',state=str(state_path.relative_to(ROOT)),
                log='studio/production/remaining/'+section+'-asr.log',
                command=['studio/runtime/.venv/bin/python','studio/tools/check_audio.py',str(narration.relative_to(ROOT)),
                         '--language','sv','--pattern','hb-*.wav','--threads','2','--resume'],
                expected_outputs=[str(asr_path.relative_to(ROOT))])
            path=BASE/(section+'-asr-job.json');path.write_text(json.dumps(config,indent=2)+'\n')
            progress=dict(section_id=section,status='checking',clips=len(metrics))
            (BASE/'asr-controller-progress.json').write_text(json.dumps(progress,indent=2)+'\n')
            subprocess.run(['.venv/bin/python','studio/production/remaining/job.py','run',str(path)],cwd=ROOT,check=True)
            waiting=True
            break
        if not waiting:
            (BASE/'asr-controller-progress.json').write_text(json.dumps(dict(status='complete',sections=control['sections']),indent=2)+'\n')
            return
        time.sleep(30)


if __name__=='__main__':main()
