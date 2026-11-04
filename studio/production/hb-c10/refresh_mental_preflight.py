"""Refresh the final mental-health qualification art,assets,source checks and stills."""
from pathlib import Path
import subprocess,json,time
R=Path(__file__).resolve().parents[3]
dependency=R/'studio/production/hb-c10/hb-c10-psykisk-tts-state.json'
while json.loads(dependency.read_text()).get('status')!='finished':
 state=json.loads(dependency.read_text())
 if state.get('status')=='failed':raise RuntimeError('Narration failed;preserve all takes for missing-only recovery.')
 print('Waiting for selected narration completion before timing/stills.',flush=True);time.sleep(30)
assert json.loads(dependency.read_text())['returncode']==0
commands=[['studio/runtime/.venv/bin/python','studio/production/hb-c10/prepare_mental_pictures.py'],['studio/runtime/.venv/bin/python','studio/episodes/hb-c10-psykisk/prepare_assets.py'],['.venv/bin/python','studio/tools/script.py','review','hb-c10-psykisk'],['.venv/bin/python','studio/tools/script.py','validate','hb-c10-psykisk','--ready'],['studio/runtime/.venv/bin/python','studio/tools/validate_assets.py','hb-c10-psykisk'],['studio/runtime/.venv/bin/python','studio/tools/render.py','hb-c10-psykisk','--stills-only']]
for command in commands:
 print('Starting',json.dumps(command),flush=True);subprocess.run(command,cwd=R,check=True)
print('All final mental preflight stages completed;actual image inspection still required.',flush=True)
