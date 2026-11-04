"""Refresh opted-in unrendered captions; retain every selected audio take."""
from pathlib import Path
import fcntl
import hashlib
import json
import subprocess
import time

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
lock = (HERE / 'source-label-refresh.lock').open('a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
targets = json.loads((HERE / 'source-label-fit-targets.json').read_text())['episodes']
ready = ['hb-c09-vardledighet', 'hb-c09-foraldraledighet',
         'hb-c09-forandring', 'hb-c09-familjeformer', 'hb-c09-kon']
state = dict(status='running', episodes={})


def save():
    temporary = HERE / 'source-label-refresh.writing'
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.replace(HERE / 'source-label-refresh-progress.json')


def run(command, section):
    with (HERE / (section + '-source-label-refresh.log')).open('a') as stream:
        child = subprocess.Popen(command, cwd=ROOT, stdout=stream,
                                 stderr=subprocess.STDOUT)
        state.update(section_id=section, child_pid=child.pid, command=command)
        save()
        while child.poll() is None:
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                print(section, 'picture-label refresh is running.', flush=True)
        assert child.returncode == 0, section + ' label refresh failed; inspect owned log.'


for section in ready:
    episode = ROOT / 'studio/episodes' / section
    brief = yaml.safe_load((episode / 'brief.yaml').read_text())
    brief.update(production_status='script_ready', issues=[
        'Foreground-caption line breaking is refreshing; final visual review remains.',
        'Whole-video listening and user acceptance remain pending.',
    ])
    (episode / 'brief.yaml').write_text(yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))

for section in targets:
    episode = ROOT / 'studio/episodes' / section
    metrics = ROOT / 'studio/media' / section / 'narration/metrics.json'
    old = json.loads(metrics.read_text()) if metrics.exists() else []
    retained = {row['path']: hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
                for row in old}
    run(['studio/runtime/.venv/bin/python',
         str((episode / 'prepare_foregrounds.py').relative_to(ROOT))], section)
    for name, fingerprint in retained.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == fingerprint
    state['episodes'][section] = dict(foregrounds='complete', retained_audio=len(old))
    print(section, 'source captions fitted; selected audio retained.', flush=True)
    save()

for section in ready:
    episode = ROOT / 'studio/episodes' / section
    commands = [
        ['studio/runtime/.venv/bin/python', str((episode / 'prepare_assets.py').relative_to(ROOT))],
        ['studio/runtime/.venv/bin/python', 'studio/tools/validate_assets.py', section],
        ['studio/runtime/.venv/bin/python', 'studio/tools/render.py', section, '--stills-only'],
        ['.venv/bin/python', 'studio/tools/script.py', 'review', section, '--ready'],
        ['.venv/bin/python', 'studio/tools/script.py', 'validate', section, '--ready'],
        ['.venv/bin/python', 'studio/tools/picture_coverage.py', section, '--planned', '--require-target'],
    ]
    for command in commands:
        run(command, section)
    state['episodes'][section]['timed_stills'] = 'passed; producer review pending'
    print(section, 'refreshed asset, layout and source checks passed.', flush=True)
    save()
state.update(status='complete', completed=time.time())
save()
(HERE / 'source-label-refresh-completed.json').write_text(json.dumps(state, indent=2) + '\n')
