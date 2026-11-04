"""Prepare owned export configurations without launching an encoder."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
inventory = yaml.load((ROOT / 'studio/episodes.yaml').read_text(),
                      Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
report = {'at': datetime.now(timezone.utc).isoformat(), 'encoder_launches': 0,
          'episodes': {}}
for row in inventory['episodes']:
    section = row['section_id']
    if not section.startswith('hb-c09-'):
        continue
    slug = section.removeprefix('hb-c09-')
    episode = ROOT / 'studio/episodes' / section
    brief = yaml.load((episode / 'brief.yaml').read_text(),
                      Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
    stem = f"{row['chapter_id']}-{row['section_order']:02d}-{slug}"
    output = f'videos/homebrew/{stem}.mp4'
    for stage, tool in [('render', 'render.py'), ('verify', 'verify_render.py')]:
        if brief['production_status'] == 'preview_ready':
            continue
        config_path = HERE / f'{slug}-{stage}-job.json'
        if config_path.exists():
            continue
        config = {
            'section_id': section, 'stage': stage,
            'state': str((HERE / f'{slug}-{stage}-host-state.json').relative_to(ROOT)),
            'log': str((HERE / f'{slug}-{stage}-host.log').relative_to(ROOT)),
            'command': ['studio/runtime/.venv/bin/python', f'studio/tools/{tool}',
                        section] + (['--save-frames'] if stage == 'verify' else []),
            'expected_outputs': [output, str((episode / (
                'render.json' if stage == 'render' else 'render-check.json'
            )).relative_to(ROOT))],
        }
        if stage == 'render':
            config['refuse_existing_outputs'] = [output]
        config_path.write_text(json.dumps(config, indent=2) + '\n')
    result = {'production_status': brief['production_status'], 'output': output}
    if brief['production_status'] == 'assets_ready':
        paths = {
            'script_sha256': episode / 'script.yaml',
            'assets_sha256': episode / 'assets.yaml',
            'narration_metrics_sha256': ROOT / 'studio/media' / section / 'narration/metrics.json',
            'preflight_review_sha256': episode / 'producer-preflight-review.json',
        }
        fingerprints = {key: hashlib.sha256(path.read_bytes()).hexdigest()
                        for key, path in paths.items()}
        frozen_path = HERE / f'{slug}-frozen-candidate.json'
        if not frozen_path.exists():
            frozen_path.write_text(json.dumps(fingerprints, indent=2) + '\n')
        result['frozen_inputs_current'] = json.loads(frozen_path.read_text()) == fingerprints
        result['allocation_required_before_launch'] = True
    report['episodes'][section] = result
(HERE / 'export-configuration-readiness.json').write_text(
    json.dumps(report, indent=2) + '\n')
print('Prepared configurations; no encoder launched.', flush=True)
print('Ready frozen candidates:', sum(r.get('frozen_inputs_current', False)
                                     for r in report['episodes'].values()), flush=True)
