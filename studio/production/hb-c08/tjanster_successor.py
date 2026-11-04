"""Start the assigned frozen export only after Vuxna's exact render-stage release."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
PROD = ROOT / 'studio/production/hb-c08'
SID = 'hb-c12-tjanster'
STATE = PROD / 'tjanster-successor-state.json'
RELEASE = PROD / 'hb-c08-vuxna-export-state.json'
FREEZE = next(row for row in json.loads((PROD / 'ready-export-freezes.json').read_text())['episodes'] if row['section_id'] == SID)
state = dict(supervisor_pid=os.getpid(), section_id=SID, status='waiting_assigned_slot', started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), expected_predecessor_supervisor=290200)


def save():
    temporary = STATE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.replace(STATE)


def renderers():
    lines = subprocess.check_output(['ps', '-eo', 'pid,ppid,args'], text=True).splitlines()
    active = []
    for line in lines:
        parts = line.split()
        if len(parts) < 4 or not Path(parts[2]).name.startswith('python'):
            continue
        if any(part.endswith('studio/tools/render.py') for part in parts[3:]) and '--stills-only' not in parts:
            active.append(line.strip())
    return active


save()
try:
    while True:
        release = json.loads(RELEASE.read_text())
        assert release['supervisor_pid'] == 290200, 'Assigned predecessor changed; require fresh coordination.'
        if release.get('stages', {}).get('render', {}).get('status') == 'complete':
            assert release['stages']['render']['exit_code'] == 0, 'Assigned predecessor render did not succeed.'
            assert (ROOT/'studio/episodes/hb-c08-vuxna/render.json').exists(), 'Predecessor canonical render record missing.'
            active = renderers()
            budget = json.loads((ROOT/'studio/production/remaining/resource-budget.json').read_text())['max_full_encoders']
            if len(active) < budget:
                for record in FREEZE['input_snapshots'].values():
                    assert hashlib.sha256((ROOT / record['path']).read_bytes()).hexdigest() == record['sha256'], record['path']
                assert not (ROOT / 'studio/episodes' / SID / 'render.json').exists(), 'Export already exists; do not duplicate.'
                with (PROD / (SID + '-export-supervisor.log')).open('ab', buffering=0) as log:
                    child = subprocess.Popen([str(ROOT / 'studio/runtime/.venv/bin/python'), 'studio/production/hb-c08/export_pipeline.py', SID], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                state.update(status='launched', export_supervisor_pid=child.pid, launched_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), predecessor=release, prior_full_renderers=active, max_full_encoders=budget, frozen_inputs=FREEZE)
                save()
                print(SID, 'launched supervisor', child.pid, flush=True)
                break
        state['heartbeat_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save()
        print(state['heartbeat_at'], 'Waiting for assigned successful Vuxna render-stage release; no compute occupied.', flush=True)
        time.sleep(35)
except Exception as exc:
    state.update(status='failed_closed', error=repr(exc))
    save()
    raise
