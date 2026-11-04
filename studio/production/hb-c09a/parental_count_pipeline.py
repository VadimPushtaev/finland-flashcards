"""Borrow the owned narration/ASR lanes at safe boundaries for one comparison."""
from pathlib import Path
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def wait_checkpoint(filename, expected):
    while True:
        state = json.loads((HERE / filename).read_text())
        if state.get('status') == expected:
            return state
        print(filename, 'waiting for its safe episode/chunk checkpoint.', flush=True)
        time.sleep(20)


def run(command):
    process = subprocess.Popen(command, cwd=ROOT)
    while process.poll() is None:
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            print('Bounded parental-count comparison PID', process.pid, 'is running.', flush=True)
    assert process.returncode == 0


tts = wait_checkpoint('durable-tts-progress.json', 'paused_at_checkpoint')
(HERE / 'parental-count-checkpoint.json').write_text(json.dumps(dict(
    reason='Both lane controls request safe boundaries; no live synthesis or transcription child is signalled.',
    tts_checkpoint=tts, started=time.time(), selected_takes_changed=False,
), indent=2) + '\n')
run(['studio/runtime/.venv/bin/python', 'studio/production/hb-c09a/retake_parental_counts.py'])
control_path = HERE / 'tts-control.json'
control = json.loads(control_path.read_text())
control['pause'] = False
control.pop('pause_reason', None)
control_path.write_text(json.dumps(control, indent=2) + '\n')
run(['.venv/bin/python', 'studio/production/remaining/job.py', 'start',
     'studio/production/hb-c09a/durable-tts-job.json'])
print('Normal two-thread narration resumed; waiting for the existing ASR lane.', flush=True)
wait_checkpoint('durable-asr-progress.json', 'paused_at_episode_checkpoint')
folder = 'studio/media/hb-c09-foraldraledighet/retake-expanded-counts'
run(['studio/runtime/.venv/bin/python', 'studio/tools/check_audio.py', folder,
     '--language', 'sv', '--pattern', 'hb-*.wav', '--resume', '--threads', '2'])
(HERE / 'parental-count-diagnostics-ready.json').write_text(json.dumps(dict(
    status='comparison_diagnostics_ready', finished=time.time(),
    selected_takes_changed=False,
    remaining='Producer compares four intended numerals and selects or rejects; regular ASR is at a recorded checkpoint.',
), indent=2) + '\n')
