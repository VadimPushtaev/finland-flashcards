"""Advance one explicitly assigned root render stream with current-input guards."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'studio/production/remaining'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(section):
    episode = ROOT / 'studio/episodes' / section
    narration = ROOT / 'studio/media' / section / 'narration'
    return {str(p.relative_to(ROOT)): digest(p) for p in
            [episode / n for n in ('script.yaml', 'assets.yaml', 'sources.yaml', 'CREDITS.md',
                                    'producer-preflight-review.json')]
            + [narration / 'metrics.json', narration / 'asr.json']}


def guard(section, frozen):
    assert inputs(section) == frozen, 'Assigned candidate changed: ' + section
    episode = ROOT / 'studio/episodes' / section
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    proof = json.loads((episode / 'producer-preflight-review.json').read_text())
    assert proof['producer_visual_review']
    assert yaml.safe_load((episode / 'brief.yaml').read_text())['production_status'] == 'assets_ready'
    for kind in ('script', 'assets'):
        assert digest(episode / (kind + '.yaml')) == proof[kind + '_sha256']
    render = ROOT / 'studio/media' / section / 'render'
    assert all(digest(render / name) == value for name, value in proof['frame_sha256'].items())
    asr = json.loads((ROOT / 'studio/media' / section / 'narration/asr.json').read_text())
    diagnostics = {r['file']: r['sha256'] for r in asr}
    assert all(diagnostics[row['audio_path']] == digest(ROOT / row['audio_path'])
               for row in script['sentences']), 'Stale selected WAV/ASR: ' + section


def full_count():
    lines = subprocess.check_output(['ps', '-eo', 'pid=,args='], text=True).splitlines()
    count = 0
    for line in lines:
        parts = line.split()
        if len(parts) < 3 or not Path(parts[1]).name.startswith('python'):
            continue
        if any(p.endswith('/studio/tools/render.py') or p == 'studio/tools/render.py'
               for p in parts[2:]) and '--stills-only' not in parts:
            count += 1
    return count


def start(section, stage):
    return json.loads(subprocess.check_output(
        ['.venv/bin/python', 'studio/production/remaining/job.py', 'start',
         str(BASE / f'{section}-{stage}-job.json')], cwd=ROOT, text=True))


def main():
    config = json.loads(Path(sys.argv[1]).read_text())
    if '--check' in sys.argv[2:]:
        for section in config['next']:
            guard(section, config['frozen'][section])
        print('PASS current guards:', len(config['next']), 'assigned root successors')
        return
    progress_path = BASE / (config['stream'] + '-progress.json')
    progress = dict(stream=config['stream'], launches=[])
    predecessor = config['predecessor']
    expected_pid = config['predecessor_pid']
    for section in config['next']:
        while True:
            state = json.loads((BASE / f'{predecessor}-render-state.json').read_text())
            assert state['supervisor_pid'] == expected_pid, 'Predecessor supervisor changed'
            if state['status'] == 'finished':
                assert state['returncode'] == 0 and not state.get('missing_outputs')
                report = json.loads((ROOT / 'studio/episodes' / predecessor / 'render.json').read_text())
                assert digest(ROOT / report['output']) == report['sha256']
                break
            assert state['status'] in ('starting', 'running'), str(state)
            time.sleep(25)
        while full_count() >= json.loads((BASE / 'resource-budget.json').read_text())['max_full_encoders']:
            time.sleep(25)
        guard(section, config['frozen'][section])
        subprocess.run(['.venv/bin/python', 'studio/tools/script.py', 'validate', section, '--ready'],
                       cwd=ROOT, check=True)
        launch = start(section, 'render')
        verify = start(section, 'verify')
        progress['launches'].append(dict(section_id=section, predecessor=predecessor,
                                         render=launch, verify=verify, checked_at=time.time()))
        progress_path.write_text(json.dumps(progress, indent=2) + '\n')
        print('LAUNCHED', section, launch['supervisor_pid'], flush=True)
        predecessor, expected_pid = section, launch['supervisor_pid']
    progress['all_assigned_successors_launched'] = True
    progress_path.write_text(json.dumps(progress, indent=2) + '\n')


if __name__ == '__main__':
    main()
