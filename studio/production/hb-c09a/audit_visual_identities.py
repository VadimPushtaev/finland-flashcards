"""Count visible foreground structures, ignoring labels and equivalent aliases."""
from pathlib import Path
import json

import yaml

ROOT = Path(__file__).resolve().parents[3]
ALIASES = {
    'adult': 'person', 'woman': 'person', 'man': 'person',
    'couple': 'parents', 'family': 'family1', 'equality': 'scales',
    'briefcase': 'work', 'marriage': 'rings', 'institution': 'court',
    'homes': 'house', 'notice': 'document',
}
ARROWS = {'branch': 'flow', 'support': 'flow', 'inherit': 'flow', 'notify': 'flow'}


def signature(specification):
    """Normalize the actual choices the diagram renderer draws."""
    objects = [ALIASES.get(kind, kind) for kind, _ in specification['objects']]
    count = len(objects)
    relation = specification.get('relation', 'none')
    if count == 1:
        edges = []
    elif count == 2:
        edges = [relation]
    elif specification.get('layout') == 'tree':
        edges = [relation, relation]
    else:
        edges = specification.get('relations', [relation, relation])
    return json.dumps(dict(
        objects=objects,
        edges=[ARROWS.get(value, value) for value in edges],
        layout='tree' if specification.get('layout') == 'tree' else 'linear',
        chart=[entry['percent'] for entry in specification.get('chart', [])],
    ), sort_keys=True)


def audit(section):
    episode = ROOT / 'studio/episodes' / section
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    plan = json.loads((episode / 'visual-plan.json').read_text())
    foregrounds = json.loads((episode / 'foreground-assets.json').read_text())
    if isinstance(foregrounds, dict):
        foregrounds = foregrounds.get('assets', foregrounds)
    by_path = {entry['path']: asset for asset in foregrounds for entry in asset['files']}
    groups = {}
    photographs = 0
    for number, (row, specification) in enumerate(zip(script['sentences'], plan), 1):
        asset = by_path[row['render_image']]
        if asset.get('visual_type') == 'photograph':
            identity = 'photo:' + asset['source_url']
            photographs += 1
        else:
            identity = signature(specification)
        groups.setdefault(identity, []).append(number)
    return dict(
        sentences=len(plan), photographs=photographs,
        distinct_visible_identities=len(groups), fraction=len(groups) / len(plan),
        repeated_sentence_groups=[values for values in groups.values() if len(values) > 1],
    )


if __name__ == '__main__':
    report = dict(
        method='Foreground photographs use verified source identity. Diagrams normalize icons that draw identically and actual edge styles, including explicit/default none edges; titles, labels, filenames and source IDs are ignored. Tree arrangement and visible chart proportions count. This supplements performed visual review and does not measure playback duration.',
        episodes={path.name: audit(path.name) for path in sorted((ROOT / 'studio/episodes').glob('hb-c09-*'))},
    )
    (Path(__file__).resolve().parent / 'conservative-visual-diversity.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    for section, row in report['episodes'].items():
        print(section, f"{row['distinct_visible_identities']}/{row['sentences']}", f"{row['fraction']:.1%}", row['repeated_sentence_groups'])
