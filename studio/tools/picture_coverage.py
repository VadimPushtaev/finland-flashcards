"""Measure registered foreground pictures over the actual narrated body timeline."""
import argparse
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
PICTURE_TYPES = {'photograph', 'map', 'flag', 'illustration', 'diagram'}


def measure(script, assets, timeline, fps):
    """Exclude titles, credits, text cards and copies of the decorative background.

    Visual classification and relevance require human/agent image review. This
    check establishes duration coverage, not whether an image tells the truth.
    """
    if fps <= 0:
        raise ValueError('Frame rate must be positive')
    body = [item for item in timeline if item['kind'] == 'sentence']
    rows = script['sentences']
    if not rows or [item['sentence_id'] for item in body] != [row['sentence_id'] for row in rows]:
        raise ValueError('Timeline must cover every sentence exactly once in source order')
    files = {}
    background_hashes, background_sources = set(), set()
    for asset in assets:
        if asset['kind'] == 'background':
            background_hashes.update(f['sha256'] for f in asset['files'] if f.get('sha256'))
            if asset.get('source_url'):
                background_sources.add(asset['source_url'])
        for file in asset['files']:
            if file['path'] in files:
                raise ValueError('Ambiguous asset path: ' + file['path'])
            files[file['path']] = (asset, file)
    results = []
    for row, item in zip(rows, body):
        if not isinstance(item['frames'], int) or item['frames'] <= 0:
            raise ValueError('Invalid body duration: ' + row['sentence_id'])
        path = row.get('render_image')
        counted, visual_type = False, None
        if path:
            if path not in files:
                raise ValueError('Unregistered foreground: ' + path)
            asset, file = files[path]
            visual_type = file.get('visual_type', asset.get('visual_type'))
            counted = (
                asset['kind'] == 'foreground' and visual_type in PICTURE_TYPES
                and path != script['render'].get('background_image')
                and file.get('sha256') not in background_hashes
                and asset.get('source_url') not in background_sources
            )
        results.append(dict(sentence_id=row['sentence_id'], frames=item['frames'],
                            render_image=path, visual_type=visual_type, picture=counted))
    total = sum(r['frames'] for r in results)
    pictured = sum(r['frames'] for r in results if r['picture'])
    return dict(body_seconds=total / fps, picture_seconds=pictured / fps,
                picture_fraction=pictured / total, target_fraction=.5,
                meets_target=pictured * 2 >= total,
                sentences=len(results), picture_sentences=sum(r['picture'] for r in results),
                method='Whole sentence display intervals, including lead and pause; titles and credits excluded. '
                       'Only explicitly classified registered foreground pictures count. Relevance requires visual review.',
                results=results)


def build_report(section, planned=False):
    """Bind coverage to the current script, assets and measured timeline."""
    episode = ROOT / 'studio/episodes' / section
    script_path, assets_path = episode / 'script.yaml', episode / 'assets.yaml'
    script = yaml.safe_load(script_path.read_text())
    assets = yaml.safe_load(assets_path.read_text())['assets']
    if planned:
        timeline_path = ROOT / 'studio/media' / section / 'render/timeline.json'
        timeline = json.loads(timeline_path.read_text())
        fps, export = 24, None
    else:
        timeline_path = episode / 'render.json'
        export = json.loads(timeline_path.read_text())
        timeline, fps = export['timeline'], export['fps']
    result = measure(script, assets, timeline, fps)
    result.update(section_id=section, stage='planned' if planned else 'exported',
                  script_sha256=hashlib.sha256(script_path.read_bytes()).hexdigest(),
                  assets_sha256=hashlib.sha256(assets_path.read_bytes()).hexdigest(),
                  timeline_sha256=hashlib.sha256(timeline_path.read_bytes()).hexdigest(),
                  output=export['output'] if export else None,
                  export_sha256=export['sha256'] if export else None)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('--planned', action='store_true', help='Use measured still-render timeline before export')
    parser.add_argument('--require-target', action='store_true', help='Fail below 50%; exceptions require documented review')
    args = parser.parse_args()
    report = build_report(args.section, args.planned)
    suffix = 'picture-coverage-planned.json' if args.planned else 'picture-coverage.json'
    (ROOT / 'studio/episodes' / args.section / suffix).write_text(json.dumps(report, indent=2) + '\n')
    print(f"{args.section}: {report['picture_fraction']:.1%} of body duration; "
          f"{report['picture_sentences']}/{report['sentences']} sentences with pictures")
    if args.require_target and not report['meets_target']:
        raise SystemExit('Below 50% picture target; revise imagery or document and review a genuine exception.')
