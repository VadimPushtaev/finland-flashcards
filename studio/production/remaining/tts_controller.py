"""Run only the missing root-owned complete narration jobs from a control file."""
from pathlib import Path
import json
import subprocess
import time

import yaml

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'studio/production/remaining'


def save(value):
    temporary=BASE/'tts-controller-progress.writing'
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    temporary.replace(BASE/'tts-controller-progress.json')


def main():
    while True:
        control=json.loads((BASE/'tts-control.json').read_text())
        if control.get('stop_after_current'):
            save(dict(status='checkpointed',reason='Explicit control request'))
            return
        owners=yaml.safe_load((BASE/'queue.yaml').read_text())['episodes']
        pending=[]
        for section in control['sections']:
            if next(row['owner'] for row in owners if row['section_id']==section)!='root':
                raise ValueError('Root controller does not own '+section)
            script=yaml.safe_load((ROOT/'studio/episodes'/section/'script.yaml').read_text())
            metrics_path=ROOT/'studio/media'/section/'narration/metrics.json'
            state_path=BASE/(section+'-tts-state.json')
            state=json.loads(state_path.read_text()) if state_path.exists() else {}
            if state.get('status')=='running':
                save(dict(status='waiting_on_owned_existing_job',section_id=section,pid=state.get('pid')))
                print('Waiting for existing owned job:',section,flush=True)
                time.sleep(30)
                break
            if metrics_path.exists():
                metrics=json.loads(metrics_path.read_text())
                if [m['sentence_id'] for m in metrics]!=[r['sentence_id'] for r in script['sentences']]:
                    raise ValueError('Retain partial takes and prepare an explicit separate-folder resume: '+section)
                if not all((ROOT/m['path']).is_file() for m in metrics):
                    raise ValueError('Retained narration file missing: '+section)
                continue
            pending.append(section)
        else:
            if not pending:
                save(dict(status='complete',sections=control['sections']))
                return
            section=pending[0]
            for verb in ('review','validate'):
                subprocess.run(['.venv/bin/python','studio/tools/script.py',verb,section,'--ready'],cwd=ROOT,check=True)
            config=dict(section_id=section,stage='tts',state='studio/production/remaining/'+section+'-tts-state.json',
                log='studio/production/remaining/'+section+'-tts.log',
                command=['studio/runtime/.venv/bin/python','studio/tools/audition.py','supertonic','--voice','F1','--speed','.95','--threads','2','--section',section,'--all','--output','studio/media/'+section+'/narration'],
                refuse_existing_outputs=['studio/media/'+section+'/narration/metrics.json'],
                expected_outputs=['studio/media/'+section+'/narration/metrics.json'])
            config_path=BASE/(section+'-tts-job.json')
            config_path.write_text(json.dumps(config,indent=2)+'\n')
            save(dict(status='running',section_id=section,config=str(config_path.relative_to(ROOT))))
            subprocess.run(['.venv/bin/python','studio/production/remaining/job.py','run',str(config_path)],cwd=ROOT,check=True)


if __name__=='__main__':main()
