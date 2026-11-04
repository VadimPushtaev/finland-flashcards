"""Resume the single root-allocated render stream, preserving every active job."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CONTROL = HERE / 'third-render-stream-control.json'
PROGRESS = HERE / 'third-render-stream-progress.json'
report = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {'episodes': {}}
report['allocation'] = 'Single root-approved stream; read current control and central budget before each launch.'


def save():
    PROGRESS.write_text(json.dumps(report, indent=2) + '\n')


def full_renderers():
    result = []
    for path in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            arguments = path.read_bytes().split(b'\0')
            if b'studio/tools/render.py' in arguments and b'--stills-only' not in arguments:
                result.append({'pid': int(path.parent.name),
                               'args': [word.decode() for word in arguments if word]})
        except OSError:
            pass
    return result


def current_inputs(section, slug):
    episode = ROOT / 'studio/episodes' / section
    media = ROOT / 'studio/media' / section
    frozen = json.loads((HERE / f'{slug}-frozen-candidate.json').read_text())
    paths = {
        'script_sha256': episode / 'script.yaml',
        'assets_sha256': episode / 'assets.yaml',
        'narration_metrics_sha256': media / 'narration/metrics.json',
        'preflight_review_sha256': episode / 'producer-preflight-review.json',
    }
    for key, path in paths.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == frozen[key], (section, key)
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    metrics = json.loads((media / 'narration/metrics.json').read_text())
    transcripts = {Path(row['file']).stem: row
                   for row in json.loads((media / 'narration/asr.json').read_text())}
    assert [row['sentence_id'] for row in metrics] == [row['sentence_id'] for row in script['sentences']]
    for sentence, take in zip(script['sentences'], metrics):
        assert take['text'] == (sentence.get('speech_override') or {}).get('text', sentence['sv'])
        actual = hashlib.sha256((ROOT / take['path']).read_bytes()).hexdigest()
        assert actual == transcripts[take['sentence_id']]['sha256']
    return frozen


def launch(slug, stage):
    config = HERE / f'{slug}-{stage}-job.json'
    result = subprocess.run(
        ['.venv/bin/python', 'studio/production/remaining/job.py', 'start',
         str(config.relative_to(ROOT))], cwd=ROOT, check=True,
        capture_output=True, text=True,
    )
    print(result.stdout, flush=True)
    return json.loads(result.stdout)['supervisor_pid']


# This second stream replaces only the exact root Skulder321506 encoder.
release_path = ROOT / 'studio/production/hb-c10/hb-c10-funktionsnedsattning-render-state.json'
if 'external_release' not in report:
    while True:
        predecessor = json.loads(release_path.read_text())
        assert predecessor['supervisor_pid'] == 340713, predecessor
        if predecessor['status'] == 'finished':
            assert predecessor['returncode'] == 0 and not predecessor['missing_outputs']
            break
        assert predecessor['status'] == 'running', predecessor
        print('C10 Funktions340713 still rendering; second C9 stream remains held.', flush=True)
        time.sleep(30)
    render_record = ROOT / 'studio/episodes/hb-c10-funktionsnedsattning/render.json'
    rendered = json.loads(render_record.read_text())
    canonical = ROOT / rendered['output']
    assert canonical.is_file()
    assert hashlib.sha256(canonical.read_bytes()).hexdigest() == rendered['sha256']
    report['external_release'] = {
        'state_path': str(release_path.relative_to(ROOT)), 'state': predecessor,
        'canonical_path': str(canonical.relative_to(ROOT)),
        'canonical_sha256': rendered['sha256'],
        'render_record_sha256': hashlib.sha256(render_record.read_bytes()).hexdigest(),
        'checked_at': time.time(),
    }
    save()
index = 0
while True:
    allocated = json.loads(CONTROL.read_text())['episodes']
    if index >= len(allocated):
        break
    assignment = allocated[index]
    slug, section = assignment['slug'], assignment['section_id']
    while assignment.get('hold', False):
        print(assignment['slug'], 'held for approved picture repair and peer review.', flush=True)
        time.sleep(15)
        assignment = next(row for row in json.loads(CONTROL.read_text())['episodes'] if row['slug'] == slug)
    row = report['episodes'].setdefault(slug, {})
    if 'render_supervisor' not in row:
        assert index > 0 or report.get('external_release'), 'Exact external predecessor release is required.'
        frozen = current_inputs(section, slug)
        live = full_renderers()
        budget = json.loads((ROOT / 'studio/production/remaining/resource-budget.json').read_text())['max_full_encoders']
        assert len(live) < budget, live
        report['budget'] = budget
        row.update(render_supervisor=launch(slug, 'render'), frozen=frozen,
                   host_before_launch=live, launched_at=time.time())
        save()
    expected = row['render_supervisor']
    while True:
        state_path = HERE / f'{slug}-render-host-state.json'
        deadline = time.monotonic() + 30
        while not state_path.exists() or json.loads(state_path.read_text())['supervisor_pid'] != expected:
            assert time.monotonic() < deadline, (slug, expected, 'state file did not appear')
            time.sleep(.25)
        state = json.loads(state_path.read_text())
        assert state['supervisor_pid'] == expected
        if state['status'] == 'finished':
            assert state['returncode'] == 0 and not state['missing_outputs']
            break
        assert state['status'] == 'running', state
        print(slug, expected, 'still rendering; next allocated stage held.', flush=True)
        time.sleep(30)
    if 'finished_render' not in row:
        row.update(finished_render=state, host_at_release=full_renderers())
        save()
    if 'verify_supervisor' not in row and not row.get('verification_skipped_for_picture_repair'):
        verification = HERE / f'{slug}-verify-host-state.json'
        if verification.exists():
            existing = json.loads(verification.read_text())
            assert existing['status'] in ('running', 'finished'), existing
            row['verify_supervisor'] = existing['supervisor_pid']
        else:
            row['verify_supervisor'] = launch(slug, 'verify')
        save()
    index += 1
report['complete'] = True
save()
