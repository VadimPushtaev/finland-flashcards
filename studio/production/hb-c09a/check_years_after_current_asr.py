"""Retain the live ASR child, then use that same lane for five comparisons."""
from pathlib import Path
import hashlib
import json
import os
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
state = json.loads((HERE / 'durable-asr-progress.json').read_text())
controller = state['controller_pid']
current = state['episodes']['hb-c09-forandring']
child = current['pid']
assert current['status'] == 'running'
controller_cmd = Path(f'/proc/{controller}/cmdline').read_bytes().replace(b'\0', b' ').decode()
child_cmd = Path(f'/proc/{child}/cmdline').read_bytes().replace(b'\0', b' ').decode()
assert 'studio/production/hb-c09a/durable_asr.py' in controller_cmd
assert 'studio/tools/check_audio.py' in child_cmd
assert 'studio/media/hb-c09-forandring/narration' in child_cmd
control_path = HERE / 'asr-control.json'
control = json.loads(control_path.read_text())
control['pause'] = True
control['pause_reason'] = 'Retain the active full-history ASR child; prioritize five bounded numeral comparisons before the next regular episode.'
control_path.write_text(json.dumps(control, indent=2) + '\n')
journal = dict(reason='Intentional exact-controller checkpoint. The existing ASR child is not signalled and must finish before another ASR starts.',
               controller_pid=controller, controller_command=controller_cmd,
               retained_child_pid=child, retained_child_command=child_cmd,
               child_signal_sent=False, controller_signal='SIGTERM',
               started=time.time())
(HERE / 'year-asr-checkpoint.json').write_text(json.dumps(journal, indent=2) + '\n')
os.kill(controller, signal.SIGTERM)
while True:
    stat = Path(f'/proc/{child}/stat')
    if not stat.exists() or stat.read_text().split(') ', 1)[1].split()[0] == 'Z':
        break
    print('The original two-thread ASR child remains active; comparison is waiting.', flush=True)
    time.sleep(30)
asr_path = ROOT / 'studio/media/hb-c09-forandring/narration/asr.json'
records = json.loads(asr_path.read_text())
assert len(records) == 88
for record in records:
    assert hashlib.sha256((ROOT / record['file']).read_bytes()).hexdigest() == record['sha256']
subprocess.run(['studio/runtime/.venv/bin/python',
                'studio/production/hb-c09a/record_diagnostics.py', 'hb-c09-forandring'],
               cwd=ROOT, check=True)
while True:
    take_state = json.loads((HERE / 'year-retake-host-state.json').read_text())
    if take_state['status'] == 'finished':
        break
    assert take_state['status'] == 'running', take_state
    print('Waiting for the one bounded five-clip numeral comparison.', flush=True)
    time.sleep(20)
folder = 'studio/media/hb-c09-forandring/retake-expanded-years'
assert len(json.loads((ROOT / folder / 'metrics.json').read_text())) == 5
subprocess.run(['studio/runtime/.venv/bin/python', 'studio/tools/check_audio.py',
                folder, '--language', 'sv', '--pattern', 'hb-*.wav', '--resume',
                '--threads', '2'], cwd=ROOT, check=True)
journal.update(status='comparison_diagnostics_ready', finished=time.time(),
               original_asr_sha256=hashlib.sha256(asr_path.read_bytes()).hexdigest())
(HERE / 'year-asr-checkpoint.json').write_text(json.dumps(journal, indent=2) + '\n')
print('Year comparison diagnostics ready. Selected takes remain unchanged; regular ASR is checkpointed.', flush=True)
