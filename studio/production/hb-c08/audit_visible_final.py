"""Conservative caption/ID-independent visual structures for the 22 owned episodes."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import yaml

ROOT = Path(__file__).resolve().parents[3]
PROD = Path(__file__).parent
IDS = ['hb-c08-' + name for name in ['utveckling', 'smabarn', 'forskola', 'grundskola',
    'stod', 'gymnasium', 'yrkesutbildning', 'hux', 'hogskolor', 'vuxna', 'finansiering']]
IDS += ['hb-c12-' + name for name in ['integration', 'tjanster', 'sprak', 'tolkning',
    'myndigheter', 'egna-arenden', 'personuppgifter', 'hemkommun', 'e-tjanster', 'norden-eu']]
IDS += ['hb-c11-trafik']
ALIASES = {}
for geometry, words in [('path', 'path calendarpath year continuous autonomy change cause'),
    ('social', 'meeting conversation team social class family'),
    ('split', 'clock week day halfday contrast split balance grade gradeletters scale'),
    ('arc', 'growth garden discovery tools language subjects globe lifelong'),
    ('diagonal', 'meal materials municipality qualification obligation support choice exam merge')]:
    for word in words.split():
        ALIASES[word] = geometry

# Derived from the actual Traffic drawing calls, not the unique descriptive plan names.
# Captions, IDs, numbers, colours and uniform scales do not enter these signatures.
TRAFFIC = {
    1: ('road', 'two-cars', 'opposing-lane-arrows'),
    5: ('perspective-road', 'two-trees', 'house'),
    6: ('road', 'person-at-left-edge', 'travel-arrow'),
    9: ('row', 'child', 'bike', 'arrow', 'sidewalk'),
    11: ('merge', 'crossed-bike', 'crossed-bike', 'AND', 'car'),
    18: ('row', 'bus', 'clock', 'sparse-two-point-line'),
    19: ('row-plus-bottom', 'car', 'fuel-pump', 'document', 'gear', 'coins'),
    22: ('row', 'car', 'document', 'arrow'),
    23: ('merge', 'police-car', 'document', 'arrow', 'coins'),
    24: ('row', 'flask', 'crossed-car', 'arrow'),
    25: ('limit-circle', 'car'),
    26: ('merge', 'car', 'document', 'arrow', 'shield'),
    27: ('row', 'public-building', 'document', 'arrow'),
    28: ('row-plus-bottom', 'magnifier', 'database', 'AND', 'car'),
    30: ('row-plus-bottom', 'magnifier', 'public-building', 'business-building', 'database'),
    31: ('row', 'laptop', 'database', 'arrow'),
    32: ('merge', 'card', 'car', 'arrow', 'shield'),
    33: ('row', 'globe', 'card', 'arrow'),
    34: ('merge', 'house', 'calendar', 'AND', 'crossed-card'),
    35: ('row', 'card', 'book', 'OR'),
    36: ('row', 'calendar', 'hospital', 'AND'),
    37: ('timeline', 'card', 'calendar'),
    38: ('merge', 'house', 'school', 'OR', 'card'),
    39: ('timeline', 'crossed-card', 'calendar'),
    40: ('row', 'crossed-card', 'medical-document', 'arrow'),
    41: ('merge', 'globe', 'document', 'AND', 'calendar'),
    42: ('row', 'globe', 'calendar'),
    43: ('merge', 'house', 'card', 'arrow', 'card'),
    44: ('timeline', 'house', 'calendar'),
    45: ('row', 'card', 'calendar', 'AND'),
    46: ('single', 'medical-document'),
    47: ('merge', 'calendar', 'crossed-card', 'OR', 'book'),
    48: ('timeline', 'database', 'calendar'),
    49: ('merge', 'calendar', 'car', 'AND', 'book'),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalize_icon(kind):
    return {'bank': 'court', 'adult': 'person', 'child': 'person',
            'pair': 'children', 'town': 'school'}.get(kind, kind)

results = []
for sid in IDS:
    episode = ROOT / 'studio/episodes' / sid
    plan_name = 'picture-implementation.json' if sid == 'hb-c11-trafik' else 'picture-plan.json'
    plans = json.loads((episode / plan_name).read_text())
    assets = {row['asset_id']: row for row in json.loads((episode / 'foreground-assets.json').read_text())}
    script = yaml.load((episode / 'script.yaml').read_text(), Loader=yaml.CSafeLoader)
    groups = collections.defaultdict(list)
    signatures = []
    for number, sentence in enumerate(script['sentences'], 1):
        key = next(key for key in sentence['asset_ids'] if key in assets)
        asset = assets[key]
        if asset.get('visual_type') in ['photograph', 'flag']:
            signature = (asset['visual_type'], asset.get('source_url'),
                         tuple(asset.get('additional_source_urls', [])))
        elif sid == 'hb-c11-trafik':
            signature = TRAFFIC[number]
        else:
            plan = plans[key]
            composition = plan['composition']
            geometry = 'path' if sid.startswith('hb-c12-') and composition == 'bridge' else ALIASES.get(
                composition, composition if composition in ['influence', 'separate', 'threeways',
                    'twoway', 'applicationpath', 'needs_branch', 'cumulative', 'prohibited_harm_scene'] else 'plain')
            nodes = tuple((normalize_icon(node['icon']), bool(node.get('crossed'))) for node in plan['nodes'])
            if geometry in ['plain', 'social', 'split', 'arc', 'diagonal', 'twoway', 'threeways']:
                nodes = tuple(sorted(nodes))
            signature = (geometry, nodes)
        item = dict(source_index=number, sentence_id=sentence['sentence_id'], asset_id=key)
        groups[repr(signature)].append(item)
        signatures.append(dict(**item, normalized_structure=signature))
    bindings = {name: dict(path=str((episode / name).relative_to(ROOT)), sha256=sha(episode / name))
                for name in ['script.yaml', 'assets.yaml', plan_name, 'foreground-assets.json']}
    count = len(script['sentences'])
    row = dict(section_id=sid, slides=count, distinct_visible_structures=len(groups),
               ratio=len(groups) / count, repeated_groups=[[x['source_index'] for x in items]
               for items in groups.values() if len(items) > 1], bindings=bindings,
               script_sha256=bindings['script.yaml']['sha256'], assets_sha256=bindings['assets.yaml']['sha256'],
               picture_plan_sha256=bindings[plan_name]['sha256'],
               foreground_assets_sha256=bindings['foreground-assets.json']['sha256'],
               normalized_structure_evidence=signatures)
    if sid == 'hb-c11-trafik':
        helper = ROOT / 'studio/production/hb-c11-traffic/prepare_pictures.py'
        row['actual_drawing_helper'] = dict(path=str(helper.relative_to(ROOT)), sha256=sha(helper))
    results.append(row)
    print(sid, f'{len(groups)}/{count}', round(len(groups) / count, 4), row['repeated_groups'])

assert len(results) == 22 and sum(row['slides'] for row in results) == 987
report = dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    method='Ignore all captions, IDs, numbers, colours and uniform scale. Normalize actual composition aliases, bank/court identical glyphs, single-person age/scale variants, two-person pair/children variants and town/school baseline variants. Collapse mirrored order for undirected layouts; preserve meaningful directed edges, enclosures, crossings and condition structure. Verified photograph/flag source identities remain distinct; different labels alone never establish diversity. Traffic signatures are explicitly derived from its actual drawing calls, not unique plan names. Strict visual-structure proxy, not a relevance judgment.',
    episodes=results, total_slides=987, total_distinct_visible_structures=sum(row['distinct_visible_structures'] for row in results),
    limits=['Counts are per episode, not a claim of globally unique primitives across the series.',
            'Source-specific repeats and recaps remain honest; no cosmetic production changes were made for counts.',
            'Current script hashes must be rebound after an active renderer writes final timing serialization.'])
path = PROD / 'conservative-visible-diversity.json'
if path.exists() and not (PROD / 'conservative-visible-diversity-before22.json').exists():
    (PROD / 'conservative-visible-diversity-before22.json').write_bytes(path.read_bytes())
path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
