"""Wait for one owned export's completion,then run its complete technical checks."""
from pathlib import Path
import json
import sys
import time

from verify_episode import main

ROOT=Path(__file__).resolve().parents[3]
section=sys.argv[1]
episode=ROOT/'studio/episodes'/section
state_path=ROOT/'studio/production/remaining'/(section+'-render-state.json')
while not (episode/'render.json').exists():
    state=json.loads(state_path.read_text()) if state_path.exists() else {}
    if state.get('status') in ('failed','terminated'):
        raise RuntimeError('Export stopped; preserve outputs and inspect: '+str(state_path))
    time.sleep(15)
main(section)
