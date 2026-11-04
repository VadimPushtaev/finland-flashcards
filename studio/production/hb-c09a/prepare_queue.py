"""Prepare independently ready owned episodes; human visual review stays separate."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

import yaml

ROOT = Path(__file__).resolve().parents[3]
PRODUCTION = Path(__file__).resolve().parent
CONTROL = PRODUCTION / 'prepare-control.json'
STATE = PRODUCTION / 'preparation-progress.json'


def save(value):
    temporary = STATE.with_suffix('.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(STATE)


def run(command, log_path, row):
    with log_path.open('a') as stream:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stream,
                                   stderr=subprocess.STDOUT)
        row.update(pid=process.pid, command=command, started=time.time())
        while process.poll() is None:
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                print(row['section_id'], row['stage'], 'is still running.', flush=True)
        if process.returncode:
            raise RuntimeError(f'Owned preparation stage failed: {log_path}')


state = {}
while True:
    control = json.loads(CONTROL.read_text())
    if control.get('pause'):
        print('Owned preparation queue paused at a stage boundary.', flush=True)
        break
    pending = []
    for section_id in control['episodes']:
        row = state.setdefault(section_id, {'section_id': section_id, 'status': 'waiting'})
        if row['status'] in ('needs_visual_review', 'failed'):
            continue
        episode = ROOT / 'studio/episodes' / section_id
        script_path = episode / 'script.yaml'
        script = yaml.safe_load(script_path.read_text())
        metrics_path = ROOT / 'studio/media' / section_id / 'narration/metrics.json'
        metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else []
        if len(metrics) != len(script['sentences']):
            pending.append(section_id)
            continue
        if not (episode / 'foreground-assets.json').exists():
            pending.append(section_id)
            row['status'] = 'waiting_for_curated_pictures'
            continue
        commands = [
            ['studio/runtime/.venv/bin/python', str((episode / 'prepare_assets.py').relative_to(ROOT))],
            ['studio/runtime/.venv/bin/python', 'studio/tools/validate_assets.py', section_id],
            ['studio/runtime/.venv/bin/python', 'studio/tools/render.py', section_id, '--stills-only'],
            ['.venv/bin/python', 'studio/tools/script.py', 'review', section_id, '--ready'],
            ['.venv/bin/python', 'studio/tools/script.py', 'validate', section_id, '--ready'],
            ['.venv/bin/python', 'studio/tools/picture_coverage.py', section_id, '--planned', '--require-target'],
            ['.venv/bin/python', 'studio/production/remaining/picture_diversity.py', section_id],
        ]
        try:
            for index, command in enumerate(commands):
                row.update(stage=f'prepare_{index + 1}', status='running')
                save(state)
                run(command, PRODUCTION / f'{section_id}-preparation.log', row)
            row.update(status='needs_visual_review', stage='stills_preflight_done',
                       script_sha256=hashlib.sha256(script_path.read_bytes()).hexdigest(),
                       assets_sha256=hashlib.sha256((episode / 'assets.yaml').read_bytes()).hexdigest())
            print(section_id, 'assets and still checks passed; producer visual review remains.', flush=True)
        except Exception as error:
            row.update(status='failed', error=str(error))
            print(section_id, 'preparation failed:', error, flush=True)
        save(state)
    if not pending:
        break
    print('Waiting for owned narration/pictures:', ', '.join(pending), flush=True)
    time.sleep(15)
