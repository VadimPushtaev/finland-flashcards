"""Replace only the assigned Citizenship lane with the bounded Stod picture repair."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import time
import yaml

ROOT = Path(__file__).resolve().parents[3]
PROD = Path(__file__).parent
STATE = PROD / 'stod-repair-watcher-state.json'
QUEUE = PROD / 'stod-repair-render-queue.json'
state = dict(supervisor_pid=os.getpid(), status='running',
             predecessor=dict(section_id='hb-c12-medborgarskap', supervisor_pid=365183),
             launched=[])

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save():
    temporary = STATE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    temporary.replace(STATE)

def active():
    rows = []
    for line in subprocess.check_output(['ps', '-eo', 'pid,ppid,args'], text=True).splitlines():
        parts = line.split()
        if (len(parts) > 3 and Path(parts[2]).name.startswith('python')
                and any(p.endswith('studio/tools/render.py') for p in parts[3:])
                and '--stills-only' not in parts):
            rows.append(line.strip())
    return rows

def frozen(section):
    record = next(row for row in json.loads((PROD / 'ready-export-freezes.json').read_text())['episodes']
                  if row['section_id'] == section)
    for item in record['input_snapshots'].values():
        assert sha(ROOT / item['path']) == item['sha256'], item['path']
    episode = ROOT / 'studio/episodes' / section
    narration = ROOT / 'studio/media' / section / 'narration'
    script = yaml.load((episode / 'script.yaml').read_text(), Loader=yaml.CSafeLoader)
    metrics = json.loads((narration / 'metrics.json').read_text())
    asr = {Path(row['file']).stem: row for row in json.loads((narration / 'asr.json').read_text())}
    assert [m['sentence_id'] for m in metrics] == [s['sentence_id'] for s in script['sentences']]
    for sentence, metric in zip(script['sentences'], metrics):
        assert metric['text'] == (sentence.get('speech_override') or {}).get('text', sentence['sv'])
        assert sha(ROOT / metric['path']) == asr[metric['sentence_id']]['sha256']
    assert len(asr) == len(metrics)
    assert section == 'hb-c08-stod' and len(metrics) == 133
    peer_path = ROOT / 'studio/production/hb-c10/peer-review-hb-c08-stod-repair.json'
    peer = json.loads(peer_path.read_text())
    assert peer['status'] == 'bounded_repair_peer_pass' and peer['findings'] == []
    assert sha(ROOT / peer['frozen_candidate']['path']) == peer['frozen_candidate']['sha256']
    assert sha(ROOT / peer['unchanged_owner_proof']['path']) == peer['unchanged_owner_proof']['sha256']
    for name, expected in peer['hashes'].items():
        assert sha(episode / name) == expected
    for frame in peer['current_frames']:
        assert sha(ROOT / frame['path']) == frame['sha256']
    return record

def predecessor_release(predecessor):
    section = predecessor['section_id']
    if section == 'hb-c12-medborgarskap':
        path = ROOT / 'studio/production/remaining/hb-c12-medborgarskap-render-state.json'
        release = json.loads(path.read_text())
        assert release['supervisor_pid'] == predecessor['supervisor_pid'] == 365183
        if release['status'] != 'finished':
            assert release['status'] == 'running', release
            return None
        assert release['returncode'] == 0 and release['missing_outputs'] == [], release
        render = json.loads((ROOT / 'studio/episodes' / section / 'render.json').read_text())
        assert render['output'] == 'videos/homebrew/hb-c12-19-medborgarskap.mp4'
        assert sha(ROOT / render['output']) == render['sha256']
        return dict(state=release, canonical_output=render['output'], canonical_sha256=render['sha256'])
    release = json.loads((PROD / (section + '-export-state.json')).read_text())
    assert release['supervisor_pid'] == predecessor['supervisor_pid']
    stage = release.get('stages', {}).get('render', {})
    if stage.get('status') != 'complete':
        assert stage.get('status') != 'failed', release
        return None
    assert stage['exit_code'] == 0
    render = json.loads((ROOT / 'studio/episodes' / section / 'render.json').read_text())
    assert sha(ROOT / render['output']) == render['sha256']
    return dict(state=stage, canonical_output=render['output'], canonical_sha256=render['sha256'])

state['started_at'] = stamp()
save()
try:
    while True:
        queue = json.loads(QUEUE.read_text())['successors']
        primary = json.loads((PROD / 'c12-stream-queue.json').read_text())['successors']
        secondary = json.loads((PROD / 'c12-secondary-stream-queue.json').read_text())['successors']
        assert not set(queue).intersection(primary + secondary), 'Assigned queues must stay disjoint'
        done = {row['section_id'] for row in state['launched']}
        remaining = [section for section in queue if section not in done]
        if not remaining:
            state.update(status='all_assigned_successors_launched', completed_at=stamp())
            save()
            break
        predecessor = state['predecessor']
        release = predecessor_release(predecessor)
        if release:
            host = active()
            budget = json.loads((ROOT / 'studio/production/remaining/resource-budget.json').read_text())['max_full_encoders']
            if len(host) < budget:
                section = remaining[0]
                candidate = frozen(section)
                assert not (ROOT / 'studio/episodes' / section / 'render.json').exists(), 'Refuse duplicate export'
                with (PROD / (section + '-export-supervisor.log')).open('ab', buffering=0) as log:
                    child = subprocess.Popen([str(ROOT / 'studio/runtime/.venv/bin/python'),
                                              str(PROD / 'export_pipeline.py'), section], cwd=ROOT,
                                             stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                proof = dict(section_id=section, supervisor_pid=child.pid, launched_at=stamp(),
                             predecessor=predecessor, predecessor_release=release,
                             current_frozen_inputs=candidate, selected_wav_asr_hash_checks='all current exact matches',
                             prior_full_renderers=host, max_full_encoders=budget)
                (PROD / (section + '-repair-launch-proof.json')).write_text(json.dumps(proof, indent=2) + '\n')
                state['launched'].append(proof)
                state['predecessor'] = dict(section_id=section, supervisor_pid=child.pid)
                save()
                print('LAUNCHED', section, child.pid, flush=True)
        state['heartbeat_at'] = stamp()
        save()
        print(state['heartbeat_at'], 'assigned Stod repair watcher waiting/monitoring', state['predecessor'], flush=True)
        time.sleep(35)
except Exception as exc:
    state.update(status='failed_closed', error=repr(exc))
    save()
    raise
