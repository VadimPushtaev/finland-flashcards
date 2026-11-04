"""Refresh the final fire qualification art,assets,source checks and stills."""
from pathlib import Path
import subprocess,json
R=Path(__file__).resolve().parents[3]
commands=[['studio/runtime/.venv/bin/python','studio/production/hb-c11-safety/prepare_fire_pictures.py'],['studio/runtime/.venv/bin/python','studio/episodes/hb-c11-brandsakerhet/prepare_assets.py'],['.venv/bin/python','studio/tools/script.py','review','hb-c11-brandsakerhet'],['.venv/bin/python','studio/tools/script.py','validate','hb-c11-brandsakerhet','--ready'],['studio/runtime/.venv/bin/python','studio/tools/validate_assets.py','hb-c11-brandsakerhet'],['studio/runtime/.venv/bin/python','studio/tools/render.py','hb-c11-brandsakerhet','--stills-only']]
for command in commands:
 print('Starting',json.dumps(command),flush=True);subprocess.run(command,cwd=R,check=True)
print('All final fire preflight stages completed;actual image inspection still required.',flush=True)
