"""Record a producer's completed visual review after current prerequisites pass.

This command does not inspect images. Supply the actual number of already
inspected preflight frames and concrete review notes; never run it speculatively.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('--inspected-frames', type=int, required=True)
    parser.add_argument('--note', action='append', required=True)
    args = parser.parse_args()
    episode = ROOT / 'studio/episodes' / args.section
    prepared = json.loads((episode / 'prepared-preflight.json').read_text())
    frames = sorted((ROOT / 'studio/media' / args.section / 'render').glob('frame-*.png'))
    assert len(frames) == args.inspected_frames, 'Inspect every current preflight frame first'
    assert not (episode / 'render.json').exists(), 'Use export review for completed episodes'
    digest = lambda name: hashlib.sha256((episode / name).read_bytes()).hexdigest()
    before = {name: digest(name) for name in ('script.yaml', 'assets.yaml')}
    assert before['script.yaml'] == prepared['script_sha256']
    assert before['assets.yaml'] == prepared['assets_sha256']
    commands = [
        ['studio/runtime/.venv/bin/python', 'studio/production/remaining/audio_diagnostics.py', args.section],
        ['studio/runtime/.venv/bin/python', 'studio/tools/validate_assets.py', args.section],
        ['.venv/bin/python', 'studio/tools/script.py', 'validate', args.section, '--ready'],
        ['.venv/bin/python', 'studio/tools/picture_coverage.py', args.section, '--planned', '--require-target'],
        ['.venv/bin/python', 'studio/production/remaining/picture_diversity.py', args.section],
    ]
    with (episode / 'final-preflight-check.log').open('w') as log:
        for command in commands:
            subprocess.run(command, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
    assert all(before[name] == digest(name) for name in before), 'Concurrent production edit'
    record = dict(section_id=args.section, reviewer='root producer',
                  producer_visual_review=True, actual_preflight_frames_inspected=len(frames),
                  script_sha256=before['script.yaml'], assets_sha256=before['assets.yaml'],
                  checks=args.note,
                  frame_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in frames},
                  whole_video_listening=False, physical_device_playback=False, user_acceptance=False)
    (episode / 'producer-preflight-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    brief_path = episode / 'brief.yaml'
    brief = yaml.safe_load(brief_path.read_text())
    brief['production_status'] = 'assets_ready'
    brief['issues'] = ['Awaiting an allocated canonical export and full technical verification.',
                       'Whole-video listening, physical-device playback and user acceptance are pending.']
    brief_path.write_text(yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
    print(args.section, 'assets_ready:', len(frames), 'already-inspected preflight frames')


if __name__ == '__main__':
    main()
