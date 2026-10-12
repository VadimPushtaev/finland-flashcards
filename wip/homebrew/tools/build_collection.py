"""Build independently reviewed chapters and refresh the collection index locally."""
import argparse
import hashlib
from pathlib import Path
from build_pilot import (CHAPTER_FILE, DEST, ROOT, WORK, build, dump_yaml,
                         load_sources, read_yaml, render)

SLUGS = {
    '01': 'finland_befolkningen_och_spraken', '02': 'finlands_historia',
    '03': 'kultur_varderingar_och_traditioner', '04': 'demokrati_forvaltning_och_paverkan',
    '05': 'rattigheter_jamlikhet_och_skyldigheter', '06': 'lagar_rattsvasende_och_rattsskydd',
    '07': 'arbete_naringsliv_och_beskattning', '08': 'utbildning_och_larande',
    '09': 'familj_barn_och_relationer', '10': 'halsa_social_trygghet_och_aldrande',
    '11': 'boende_vardag_och_miljo', '12': 'integration_uppehall_och_medborgarskap',
}


def chapter_path(number):
    return f'sv/chapters/{number}_{SLUGS[number]}.yaml'


def inputs(number):
    if number == '05':
        return WORK / 'pilot_selection.yaml', WORK / 'pilot_sentences.yaml', WORK / 'PILOT.sv.md'
    directory = WORK / 'chapters' / number
    return directory / 'selection.yaml', directory / 'sentences.yaml', directory / 'READING.sv.md'


def refresh_index(documents=None):
    """Index only chapter outputs already built; ignore drafts in agent work areas."""
    documents = documents or load_sources()
    entries, provenance_paths, audits, used = [], [], [], set()
    for number in SLUGS:
        path = chapter_path(number)
        if not (DEST / path).exists():
            continue
        entries.append({'id': f'hb-c{number}', 'order': int(number), 'path': path})
        provenance_path = f'metadata/{number}_provenance.yaml'
        provenance_paths.append(provenance_path)
        audits.append(f'metadata/{number}_editorial_review.yaml')
        used.update(u['source_path'] for u in read_yaml(DEST / provenance_path)['units'].values())
    records = []
    for path in sorted(used):
        doc = documents[path]
        group = 'textbook' if path.endswith('.pdf') else ('infofinland' if '/infofinland/' in path else 'orientation')
        record = {k: doc[k] for k in ['path', 'sha256', 'bytes', 'extraction']}
        record.update(source_group=group, attribution_record=group)
        for key in ['title', 'source_url', 'visible_dates', 'pdf_metadata']:
            if key in doc:
                record[key] = doc[key]
        records.append(record)
    dump_yaml(DEST / 'metadata/sources.yaml', {'schema_version': 1, 'sources': records})
    dump_yaml(DEST / 'manifest.yaml', {
        'schema_version': 1, 'id': 'homebrew', 'language': 'sv',
        'title': 'Samhällskunskap inför medborgarskapsprovet',
        'status': 'complete_archived_edition' if len(entries) == 12 else 'in_progress',
        'chapters': entries,
        'metadata': {'sources': 'metadata/sources.yaml', 'attribution': 'metadata/attribution.yaml',
                     'provenance': provenance_paths, 'editorial_reviews': audits}})
    lines = ['# Swedish Homebrew reading copies', '',
             'Generated chapter text; see [collection metadata](../../../data/homebrew/README.md) for provenance, source dates and limitations.', '']
    for entry in entries:
        number = f'{entry["order"]:02d}'
        label = read_yaml(DEST / entry['path'])['title']
        relative = '../PILOT.sv.md' if number == '05' else f'{number}/READING.sv.md'
        lines.append(f'- [{number}. {label}]({relative})')
    path = WORK / 'chapters/README.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def build_one(number, initialize=False):
    selection_path, registry_path, readable_path = inputs(number)
    selection = read_yaml(selection_path)
    assert selection['chapter_id'] == f'hb-c{number}'
    registry = read_yaml(registry_path) if registry_path.exists() else {'schema_version': 1, 'units': {}}
    documents = load_sources()
    selected_paths = {u['source_path'] for s in selection['sections'] for b in s['blocks'] for u in b.get('items', [b])}
    frozen = {s['path']: s['sha256'] for s in read_yaml(WORK / 'source_inventory.yaml')['files']}
    for path in selected_paths:
        digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert digest == documents[path]['sha256'] == frozen[path], path
    chapter, provenance = build(selection, registry, documents, initialize)
    if initialize:
        dump_yaml(registry_path, registry)
    dump_yaml(DEST / chapter_path(number), chapter)
    dump_yaml(DEST / f'metadata/{number}_provenance.yaml', provenance)
    if number != '05':
        audit = read_yaml(WORK / 'chapters' / number / 'audit.yaml')
        assert audit['chapter_id'] == selection['chapter_id']
        dump_yaml(DEST / f'metadata/{number}_editorial_review.yaml', audit)
    readable_path.write_text(render(chapter), encoding='utf-8')
    refresh_index(documents)
    print(f'Built {number}: {len(chapter["sections"])} sections, {len(provenance["units"])} text units')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chapter', default='05', choices=list(SLUGS))
    parser.add_argument('--initialize-sentences', action='store_true')
    parser.add_argument('--refresh-index', action='store_true')
    args = parser.parse_args()
    if args.refresh_index:
        refresh_index()
    else:
        build_one(args.chapter, args.initialize_sentences)


if __name__ == '__main__':
    main()
