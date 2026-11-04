"""Refresh owned timed assets after foreground changes; approval stays separate."""
from pathlib import Path
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
report = dict(status='running', episodes={})
for sid in sys.argv[1:]:
    assert sid.startswith('hb-c09-')
    commands = [
        ['studio/runtime/.venv/bin/python', f'studio/episodes/{sid}/prepare_assets.py'],
        ['studio/runtime/.venv/bin/python', 'studio/tools/validate_assets.py', sid],
        ['studio/runtime/.venv/bin/python', 'studio/tools/render.py', sid, '--stills-only'],
        ['.venv/bin/python', 'studio/tools/script.py', 'review', sid, '--ready'],
        ['.venv/bin/python', 'studio/tools/script.py', 'validate', sid, '--ready'],
        ['.venv/bin/python', 'studio/tools/picture_coverage.py', sid, '--planned', '--require-target'],
        ['.venv/bin/python', 'studio/production/remaining/picture_diversity.py', sid],
    ]
    for command in commands:
        with (HERE / (sid + '-timed-refresh.log')).open('a') as stream:
            child = subprocess.Popen(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
            while child.poll() is None:
                try:
                    child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    print(sid, 'timed still refresh is running.', flush=True)
            assert child.returncode == 0, sid + ' timed refresh failed; inspect log.'
    report['episodes'][sid] = dict(technical_checks='passed', producer_review='pending')
    print(sid, 'fresh timed stills ready for producer review.', flush=True)
report.update(status='complete', completed=time.time())
(HERE / 'timed-refresh-completed.json').write_text(json.dumps(report, indent=2) + '\n')
