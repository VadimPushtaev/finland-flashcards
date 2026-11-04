"""Run one resumable two-thread local diagnostic job as narration completes."""
from pathlib import Path
import fcntl
import json
import os
import subprocess
import time

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
lock = (HERE / 'durable-asr.lock').open('a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
state = dict(controller_pid=os.getpid(), episodes={})


def save():
    temporary = HERE / 'durable-asr-progress.writing'
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.replace(HERE / 'durable-asr-progress.json')


def run(command, row, log):
    with log.open('a') as stream:
        process = subprocess.Popen(command, cwd=ROOT, stdout=stream,
                                   stderr=subprocess.STDOUT)
        row.update(pid=process.pid, command=command, started=time.time())
        save()
        while process.poll() is None:
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                row['heartbeat'] = time.time()
                save()
                print(row['section_id'], 'local ASR is still running.', flush=True)
        assert process.returncode == 0, f'ASR failed; inspect {log}'


while True:
    control = json.loads((HERE / 'asr-control.json').read_text())
    if control.get('pause'):
        break
    waiting = []
    for sid in control['episodes']:
        if json.loads((HERE / 'asr-control.json').read_text()).get('pause'):
            state['status'] = 'paused_at_episode_checkpoint'
            save()
            raise SystemExit(0)
        row = state['episodes'].setdefault(sid, dict(section_id=sid, status='waiting'))
        if row['status'] == 'complete':
            continue
        episode = ROOT / 'studio/episodes' / sid
        script = yaml.safe_load((episode / 'script.yaml').read_text())
        folder = ROOT / 'studio/media' / sid / 'narration'
        path = folder / 'metrics.json'
        metrics = json.loads(path.read_text()) if path.exists() else []
        if len(metrics) != len(script['sentences']):
            waiting.append(sid)
            continue
        row['status'] = 'running'
        run(['studio/runtime/.venv/bin/python', 'studio/tools/check_audio.py',
             str(folder.relative_to(ROOT)), '--language', 'sv', '--pattern',
             'hb-*.wav', '--resume', '--threads', '2'], row,
            HERE / f'{sid}-durable-asr.log')
        run(['studio/runtime/.venv/bin/python',
             'studio/production/hb-c09a/record_diagnostics.py', sid], row,
            HERE / f'{sid}-durable-asr.log')
        row.update(status='complete', completed=time.time())
        save()
        print(sid, 'diagnostic transcripts and selected-WAV integrity complete.', flush=True)
    if not waiting:
        (HERE / 'asr-durable-completed.json').write_text(json.dumps(state, indent=2) + '\n')
        break
    save()
    print('Waiting for complete owned narration:', ', '.join(waiting), flush=True)
    time.sleep(20)
