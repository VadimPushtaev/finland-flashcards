"""Validate built chapters, source fidelity, editorial coverage and collection links."""
import argparse
import hashlib
from build_pilot import DEST, ROOT, WORK, load_sources, read_yaml, render
from build_collection import inputs
from validate_pilot import validate_chapter, verify_provenance


def validate_one(entry, sources, documents):
    number = f'{entry["order"]:02d}'
    chapter = read_yaml(DEST / entry['path'])
    assert chapter['id'] == entry['id'] == f'hb-c{number}'
    units, assets, identities = validate_chapter(chapter)
    assert not assets, 'Add exact asset provenance before introducing a real image'
    provenance = read_yaml(DEST / f'metadata/{number}_provenance.yaml')
    assert provenance['chapter_id'] == chapter['id']
    used = {u['source_path'] for u in provenance['units'].values()}
    verify_provenance(units, provenance, {'sources': [s for s in sources['sources'] if s['path'] in used]})
    _, registry_path, readable_path = inputs(number)
    registry = read_yaml(registry_path)['units']
    assert set(registry) == set(units)
    for identity, unit in units.items():
        assert registry[identity]['text_sha256'] == hashlib.sha256(unit['text'].encode('utf-8')).hexdigest()
        assert registry[identity]['sentences'] == unit['sentences']
    assert readable_path.read_text(encoding='utf-8') == render(chapter)
    review = read_yaml(DEST / f'metadata/{number}_editorial_review.yaml')
    assert review['chapter_id'] == chapter['id']
    coverage = read_yaml(WORK / 'coverage.yaml')['sources']
    expected = {s['id'] for s in coverage if chapter['id'] in s['chapters']}
    assert expected <= {s['id'] for s in review['source_audit']}, expected - {s['id'] for s in review['source_audit']}
    audited_units = set()
    for row in review['source_audit']:
        assert row['reason'] and row['decision']
        for identity in row['selected_unit_ids']:
            assert identity in units and provenance['units'][identity]['source_path'] == row['path'], identity
            audited_units.add(identity)
    assert audited_units == set(units), set(units) - audited_units
    for path, decisions in review.get('primary_block_audit', {}).items():
        ids = [d['source_block'] for d in decisions]
        assert len(ids) == len(set(ids))
        assert set(ids) == {b['id'] for b in documents[path]['blocks']}
    outline = next(c for c in read_yaml(WORK / 'outline.yaml')['chapters'] if c['id'] == chapter['id'])
    assert set(review['topic_coverage']) == set(outline['topics'])
    for topic, destinations in review['topic_coverage'].items():
        assert set(destinations) <= identities, (topic, destinations)
        if not destinations:
            assert any(g['topic'] == topic for g in review['gaps']), f'Unexplained topic gap: {topic}'
    for gap in review['gaps']:
        assert gap['reason'] and gap['source_refs']
    return units, identities, used


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chapter')
    args = parser.parse_args()
    manifest = read_yaml(DEST / 'manifest.yaml')
    assert manifest['status'] in {'in_progress', 'complete_archived_edition'}
    entries = manifest['chapters']
    assert len({e['id'] for e in entries}) == len(entries)
    assert [e['order'] for e in entries] == sorted({e['order'] for e in entries})
    if manifest['status'] == 'complete_archived_edition':
        assert [e['order'] for e in entries] == list(range(1, 13))
    for value in manifest['metadata'].values():
        for relative in value if isinstance(value, list) else [value]:
            path = (DEST / relative).resolve()
            assert path.is_relative_to(DEST.resolve()) and path.is_file()
    sources = read_yaml(DEST / 'metadata/sources.yaml')
    assert len({s['path'] for s in sources['sources']}) == len(sources['sources'])
    attribution = read_yaml(DEST / 'metadata/attribution.yaml')['sources']
    for source in sources['sources']:
        assert source['attribution_record'] == source['source_group'] in attribution
    for notice in attribution.values():
        assert hashlib.sha256((ROOT / notice['local_notice']).read_bytes()).hexdigest() == notice['local_notice_sha256']
    chosen = entries if not args.chapter else [e for e in entries if e['order'] == int(args.chapter)]
    assert chosen, 'Chapter not yet built'
    documents = load_sources()
    total_units = total_sentences = 0
    all_ids, all_used = set(), set()
    for entry in chosen:
        units, identities, used = validate_one(entry, sources, documents)
        assert not all_ids.intersection(identities), 'Cross-chapter ID collision'
        all_ids.update(identities)
        all_used.update(used)
        total_units += len(units)
        total_sentences += sum(len(u['sentences']) for u in units.values())
        print(f'PASS {entry["id"]}: {len(units)} source-verified text units')
    if not args.chapter:
        assert all_used == {s['path'] for s in sources['sources']}
    print(f'PASS: {len(chosen)} chapters, {total_units} text units, {total_sentences} sentence ranges')


if __name__ == '__main__':
    main()
