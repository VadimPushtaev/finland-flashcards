"""Launch the allocated frozen Förändring render after one specific root predecessor."""
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / 'studio/production/hb-c08/hb-c08-grundskola-export-state.json'
EXPECTED_SUPERVISOR = 245737
lock = (HERE / 'forandring-successor.lock').open('a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
assert not (HERE / 'forandring-successor-launched.json').exists(), 'Förändring launch already recorded.'


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(report):
    temporary = HERE / 'forandring-successor-progress.writing'
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(HERE / 'forandring-successor-progress.json')


def encoders():
    result = []
    for directory in Path('/proc').iterdir():
        if not directory.name.isdigit():
            continue
        try:
            args = [word.decode(errors='replace')
                    for word in (directory / 'cmdline').read_bytes().split(b'\0') if word]
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if '--stills-only' in args:
            continue
        for index, word in enumerate(args):
            if (Path(word).name == 'render.py' and 'studio/tools' in word
                    and index + 1 < len(args)):
                result.append(dict(pid=int(directory.name), section=args[index + 1]))
                break
    return result


report = dict(status='waiting_for_specific_predecessor', started=stamp(),
              expected_predecessor_supervisor=EXPECTED_SUPERVISOR,
              predecessor_state=str(PREDECESSOR.relative_to(ROOT)))
while True:
    state = json.loads(PREDECESSOR.read_text()) if PREDECESSOR.exists() else {}
    report.update(heartbeat=stamp(), observed_predecessor_supervisor=state.get('supervisor_pid'),
                  observed_predecessor_status=state.get('status'))
    if state.get('supervisor_pid') == EXPECTED_SUPERVISOR:
        if state.get('status') in ('failed', 'terminated'):
            report.update(status='predecessor_failed', predecessor=state)
            save(report)
            raise RuntimeError('Specified Grundskola predecessor failed; root must resolve it.')
        if state.get('status') == 'finished':
            assert state.get('returncode') == 0 and not state.get('missing_outputs')
            live = encoders()
            report.update(status='waiting_for_allocated_encoder', live_full_renderers=live)
            if len(live) <= 1 and all(row['section'] != 'hb-c09-forandring' for row in live):
                frozen = json.loads((HERE / 'forandring-frozen-candidate.json').read_text())
                paths = {
                    'script_sha256': ROOT / 'studio/episodes/hb-c09-forandring/script.yaml',
                    'assets_sha256': ROOT / 'studio/episodes/hb-c09-forandring/assets.yaml',
                    'narration_metrics_sha256': ROOT / 'studio/media/hb-c09-forandring/narration/metrics.json',
                    'preflight_review_sha256': ROOT / 'studio/episodes/hb-c09-forandring/producer-preflight-review.json',
                }
                for key, path in paths.items():
                    assert hashlib.sha256(path.read_bytes()).hexdigest() == frozen[key], key
                command = ['.venv/bin/python', 'studio/production/remaining/job.py', 'start',
                           'studio/production/hb-c09a/forandring-render-job.json']
                launched = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
                assert launched.returncode == 0, launched.stdout + launched.stderr
                result = json.loads(launched.stdout)
                report.update(status='launched', launched_at=stamp(),
                              render_supervisor_pid=result['supervisor_pid'],
                              frozen_hashes_verified=True, predecessor_finished_at=state['finished_at'],
                              launch_result=result)
                save(report)
                (HERE / 'forandring-successor-launched.json').write_text(json.dumps(report, indent=2) + '\n')
                print('Allocated Förändring render launched:', json.dumps(report), flush=True)
                break
    save(report)
    print('Förändring successor is waiting:', report['status'],
          'predecessor supervisor', report.get('observed_predecessor_supervisor'), flush=True)
    time.sleep(30)
