"""Refresh the final disability qualification art,assets,source checks and stills."""
from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[3]
commands=[['studio/runtime/.venv/bin/python','studio/production/hb-c10/prepare_disability_pictures.py'],['studio/runtime/.venv/bin/python','studio/episodes/hb-c10-funktionsnedsattning/prepare_assets.py'],['.venv/bin/python','studio/tools/script.py','review','hb-c10-funktionsnedsattning'],['.venv/bin/python','studio/tools/script.py','validate','hb-c10-funktionsnedsattning','--ready'],['studio/runtime/.venv/bin/python','studio/tools/validate_assets.py','hb-c10-funktionsnedsattning'],['studio/runtime/.venv/bin/python','studio/tools/render.py','hb-c10-funktionsnedsattning','--stills-only']]
for command in commands:
 print('Starting',json.dumps(command),flush=True);subprocess.run(command,cwd=R,check=True)
print('All final disability preflight stages completed;actual image inspection still required.',flush=True)
