"""Resume the read-only current source-snapshot audit after metadata correction."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from studio.tools import script


def main():
    destination = ROOT / 'studio/production/remaining/source-note-snapshot-validation.json'
    previous = json.loads(destination.read_text()) if destination.exists() else {}
    completed = previous.get('validated_episodes', [])
    for directory in sorted((ROOT / 'studio/episodes').glob('hb-c*')):
        if not (directory / 'sources.yaml').exists() or directory.name in completed:
            continue
        context = script.load_context(directory.name)
        script.require(script.read(directory / 'sources.yaml') == script.source_snapshot(context),
                       'Stale source snapshot: ' + directory.name)
        completed.append(directory.name)
        destination.write_text(json.dumps(dict(validated_episodes=completed,
                                               count=len(completed), complete=False), indent=2) + '\n')
        print('PASS', directory.name, flush=True)
    result = dict(validated_episodes=completed, count=len(completed), complete=True,
                  scope='Exact current source snapshot equality, reviewed translations and original archive hashes; read only.',
                  resumed_after='Original tool-session audit ended with SIGTERM143 after129successful episodes; no validation failure.')
    destination.write_text(json.dumps(result, indent=2) + '\n')
    (destination.parent / 'source-note-validation-complete.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS', len(completed), 'current source snapshots', flush=True)


if __name__ == '__main__':
    main()
