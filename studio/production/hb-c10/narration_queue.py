"""Run one recorded two-thread narration/ASR allocation across ready episodes.

Never overwrite a selected take. A partial failed TTS run stops this queue for
explicit missing-only recovery. Every heavy stage has its own durable supervisor.
"""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import time
import yaml

ROOT = Path(__file__).resolve().parents[3]
PROD = Path(__file__).resolve().parent
CONTROL = PROD / 'narration-queue-control.json'
STATUS = PROD / 'narration-queue-status.json'
SECTIONS = ['hb-c10-tillgang', 'hb-c10-lakemedel', 'hb-c11-bibliotek', 'hb-c11-fritid']


def read(path):
    return json.loads(path.read_text()) if path.exists() else {}


def stamp(section, stage, **kwargs):
    status = dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  section_id=section, stage=stage, allocation_threads=2, **kwargs)
    STATUS.write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps(status), flush=True)


def stopped():
    return bool(read(CONTROL).get('stop_before_next_stage'))


def run_stage(section, stage):
    if stopped():
        stamp(section, stage, status='stopped_before_stage')
        raise SystemExit(0)
    episode = ROOT / 'studio/episodes' / section
    media = ROOT / 'studio/media' / section / 'narration'
    owner = PROD if section.startswith('hb-c10-') else ROOT / 'studio/production/hb-c11-safety'
    state = owner / (section + '-' + stage + '-state.json')
    if read(state).get('status') == 'finished' and read(state).get('returncode') == 0:
        verify(section, stage)
        stamp(section, stage, status='previous_complete_checked')
        return
    if stage == 'tts':
        # A review export is required before ready validation; no validation is bypassed.
        subprocess.run([str(ROOT / '.venv/bin/python'), 'studio/tools/script.py', 'review', section], cwd=ROOT, check=True)
        subprocess.run([str(ROOT / '.venv/bin/python'), 'studio/tools/script.py', 'validate', section, '--ready'], cwd=ROOT, check=True)
        if media.exists() and list(media.glob('hb-*.wav')):
            raise RuntimeError('Preserve partial takes and recover only missing clips manually: ' + section)
        command = ['studio/runtime/.venv/bin/python', 'studio/tools/audition.py', 'supertonic',
                   '--voice', 'F1', '--speed', '.95', '--threads', '2', '--section', section,
                   '--all', '--output', str(media.relative_to(ROOT))]
        expected = [str((media / 'metrics.json').relative_to(ROOT))]
    else:
        verify(section, 'tts')
        command = ['studio/runtime/.venv/bin/python', 'studio/tools/check_audio.py', str(media.relative_to(ROOT)),
                   '--language', 'sv', '--pattern', 'hb-*.wav', '--resume', '--threads', '2']
        expected = [str((media / 'asr.json').relative_to(ROOT))]
    config = dict(section_id=section, stage=stage, state=str(state.relative_to(ROOT)),
                  log=str((owner / (section + '-' + stage + '.log')).relative_to(ROOT)),
                  command=command, expected_outputs=expected)
    if stage == 'tts':
        config['refuse_existing_outputs'] = expected
    job = owner / (section + '-' + stage + '-job.json')
    job.write_text(json.dumps(config, indent=2) + '\n')
    subprocess.run([str(ROOT / '.venv/bin/python'), 'studio/production/remaining/job.py', 'start',
                    str(job.relative_to(ROOT))], cwd=ROOT, check=True)
    for tick in range(100000):
        current = read(state)
        if current.get('status') == 'finished':
            if current.get('returncode') != 0 or current.get('missing_outputs'):
                raise RuntimeError('Stage failed; preserve all takes: ' + str(state))
            verify(section, stage)
            stamp(section, stage, status='complete', supervisor_pid=current.get('supervisor_pid'))
            return
        if tick % 6 == 0:
            stamp(section, stage, status=current.get('status', 'starting'),
                  supervisor_pid=current.get('supervisor_pid'), child_pid=current.get('pid'))
        time.sleep(5)
    raise RuntimeError('Unexpected queue time limit')


def verify(section, stage):
    episode = ROOT / 'studio/episodes' / section
    media = ROOT / 'studio/media' / section / 'narration'
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    metrics = read(media / 'metrics.json')
    if [m['sentence_id'] for m in metrics] != [r['sentence_id'] for r in script['sentences']]:
        raise RuntimeError('Narration/source order mismatch: ' + section)
    for row in metrics:
        if not (ROOT / row['path']).is_file():
            raise RuntimeError('Missing retained narration: ' + row['path'])
    if stage == 'asr':
        records = {r['file']: r for r in read(media / 'asr.json')}
        for row in metrics:
            if records[row['path']]['sha256'] != hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest():
                raise RuntimeError('ASR hash mismatch: ' + row['path'])


if __name__ == '__main__':
    dependency = PROD / 'hb-c10-vard-asr-state.json'
    while read(dependency).get('status') != 'finished':
        stamp('hb-c10-vard', 'asr', status='waiting_for_existing_two_thread_allocation')
        time.sleep(30)
    if read(dependency).get('returncode') != 0:
        raise RuntimeError('Existing healthcare ASR failed; do not start another heavy stage.')
    for section in SECTIONS:
        for stage in ['tts', 'asr']:
            run_stage(section, stage)
    stamp(None, 'queue', status='complete')
