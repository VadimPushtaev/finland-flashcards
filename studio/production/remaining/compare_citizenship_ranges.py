"""Generate one bounded comparison of two explicit Swedish age ranges.

Run only after the coordinator allocates a released TTS lane. Original selected
WAVs, complete metrics and diagnostics remain preserved; selection is manual.
"""
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SECTION = 'hb-c12-medborgarskap'
OUTPUT = 'studio/media/' + SECTION + '/age-range-comparison-20261103'


def main():
    episode = ROOT / 'studio/episodes' / SECTION
    plan = json.loads((episode / 'age-range-comparison.json').read_text())
    assert plan['status'] == 'prepared', 'Do not repeat an existing comparison'
    assert not (ROOT / OUTPUT / 'metrics.json').exists(), 'Preserve existing takes'
    commands = [
        ['studio/runtime/.venv/bin/python', 'studio/tools/audition.py',
         'supertonic', '--voice', 'F1', '--speed', '.95', '--threads', '2',
         '--section', SECTION, '--indices', '15,16', '--output', OUTPUT],
        ['studio/runtime/.venv/bin/python', 'studio/tools/check_audio.py',
         OUTPUT, '--language', 'sv', '--pattern', 'hb-*.wav', '--threads', '2'],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    print('One two-range comparison complete; original selection unchanged.',
          flush=True)


if __name__ == '__main__':
    main()
