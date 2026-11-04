"""Report foreground picture reuse separately from timeline picture coverage.

Photograph identity follows its source URL, so different crops do not inflate
the distinct count. Original diagrams use their file checksum; a visual review
must still reject merely relabelled copies and misleading compositions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.parse

import yaml

ROOT = Path(__file__).resolve().parents[3]
PICTURES = {'photograph', 'map', 'flag', 'illustration', 'diagram'}


def report(section):
    episode = ROOT / 'studio/episodes' / section
    script_path = episode / 'script.yaml'
    assets_path = episode / 'assets.yaml'
    script = yaml.safe_load(script_path.read_text())
    assets = yaml.safe_load(assets_path.read_text())
    by_path = {}
    for asset in assets['assets']:
        if asset['kind'] != 'foreground':
            continue
        for entry in asset['files']:
            visual_type = entry.get('visual_type', asset.get('visual_type'))
            if visual_type not in PICTURES:
                continue
            source = entry.get('source_url', asset.get('source_url'))
            if source:
                parsed = urllib.parse.urlsplit(source)
                identity = urllib.parse.unquote(parsed.netloc.lower()+parsed.path).replace('_', ' ')
            else:
                identity = 'original:'+entry['sha256']
            by_path[entry['path']] = dict(identity=identity, visual_type=visual_type,
                                         asset_id=asset['asset_id'])
    uses = []
    for row in script['sentences']:
        picture = by_path.get(row.get('render_image'))
        uses.append(dict(sentence_id=row['sentence_id'], path=row.get('render_image'),
                         picture=picture))
    count = sum(bool(x['picture']) for x in uses)
    identities = {x['picture']['identity'] for x in uses if x['picture']}
    transitions = sum(a['picture'] != b['picture'] for a,b in zip(uses, uses[1:]))
    output = dict(section_id=section, script_sha256=hashlib.sha256(script_path.read_bytes()).hexdigest(),
                  assets_sha256=hashlib.sha256(assets_path.read_bytes()).hexdigest(),
                  body_sentence_slides=len(uses), pictured_sentence_slides=count,
                  distinct_picture_sources=len(identities), picture_changes=transitions,
                  distinct_sources_per_body_slide=len(identities)/len(uses) if uses else 0,
                  photographed_slides=sum(bool(x['picture']) and x['picture']['visual_type']=='photograph' for x in uses),
                  original_diagram_limit='File uniqueness does not establish meaningful visual diversity; inspect the actual pictures.',
                  uses=uses)
    render = episode / 'render.json'
    if render.exists():
        output['export_sha256'] = json.loads(render.read_text())['sha256']
    (episode / 'picture-diversity.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    data = report(parser.parse_args().section)
    print(f"{data['section_id']}: {data['distinct_picture_sources']} distinct picture sources / "
          f"{data['body_sentence_slides']} sentence slides; "
          f"{data['pictured_sentence_slides']} pictured slides")
