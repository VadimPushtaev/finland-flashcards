"""Prepare translation context and validate Russian Homebrew data, without network I/O."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import yaml
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
POS = {'NOUN', 'PROPN', 'VERB', 'ADJ', 'ADV', 'PRON', 'DET', 'ADP', 'AUX',
       'CCONJ', 'SCONJ', 'NUM', 'PART', 'INTJ', 'X'}


def require(condition, message):
    """Raise a validation error even when Python assertions are disabled."""
    if not condition:
        raise ValueError(message)


def read(path):
    """Read a YAML file without executing YAML tags."""
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def digest(text):
    """Hash exact Unicode text encoded as UTF-8."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def fields(value, required, optional=()):
    """Reject missing and unknown fields."""
    require(isinstance(value, dict), 'Expected mapping')
    require(set(required) <= set(value) <= set(required) | set(optional),
            f'Invalid fields: expected {required}, received {list(value)}')


def nonempty(value):
    """Check a nonblank text field."""
    require(isinstance(value, str) and bool(value.strip()), 'Expected nonempty string')


def units(section):
    """Iterate the text units supported by the current published collection."""
    for block in section['blocks']:
        if block['type'] == 'paragraph':
            yield block
        elif block['type'] == 'list':
            yield from block['items']
        else:
            raise ValueError(f"Unsupported source block: {block['type']}")


def source_records(chapter, section=None):
    """Return exact heading/sentence text in source order."""
    if section is None:
        return {chapter['id']: chapter['title']}
    records = {section['id']: section['title']}
    for unit in units(section):
        for sentence in unit['sentences']:
            records[sentence['id']] = unit['text'][sentence['start']:sentence['end']]
    return records


def fingerprint(records):
    """Include source identity, order and exact text in a deterministic digest."""
    return digest(json.dumps(list(records.items()), ensure_ascii=False, separators=(',', ':')))


def library(root):
    """Read published chapters through their manifest, rejecting duplicate identities."""
    base = root / 'data/homebrew'
    chapters = [read(base / entry['path']) for entry in read(base / 'manifest.yaml')['chapters']]
    ids = [c['id'] for c in chapters] + [s['id'] for c in chapters for s in c['sections']]
    require(len(ids) == len(set(ids)), 'Duplicate source chapter/section IDs')
    return chapters


def locate(chapters, identity):
    """Find a section or chapter-heading translation target."""
    for chapter in chapters:
        if chapter['id'] == identity:
            return chapter, None
        for section in chapter['sections']:
            if section['id'] == identity:
                return chapter, section
    raise ValueError(f'Unknown source ID: {identity}')


def glossary_entries(document):
    """Validate the shared approved glossary and return entries by ID."""
    fields(document, ['schema_version', 'entries'])
    require(document['schema_version'] == 1 and isinstance(document['entries'], list), 'Invalid glossary')
    entries, meanings = {}, set()
    for entry in document['entries']:
        fields(entry, ['id', 'lemma', 'pos', 'sense', 'ru', 'note'])
        for key in ('id', 'lemma', 'sense', 'ru'):
            nonempty(entry[key])
        require(entry['pos'] in POS and isinstance(entry['note'], str), 'Invalid glossary POS/note')
        key = (entry['lemma'].casefold(), entry['pos'], entry['sense'].casefold())
        require(entry['id'] not in entries and key not in meanings, 'Duplicate/conflicting glossary entry')
        entries[entry['id']] = entry
        meanings.add(key)
    return entries


def validate_document(document, records, terms, review):
    """Validate a result against exact source records and a separate review record."""
    fields(document, ['schema_version', 'language', 'source_id', 'source_sha256', 'records'])
    require(document['schema_version'] == 1 and document['language'] == 'ru', 'Invalid version/language')
    require(document['source_id'] == next(iter(records)), 'Wrong source target')
    require(document['source_sha256'] == fingerprint(records), 'Stale source fingerprint')
    require(isinstance(document['records'], list), 'Records must be a list')
    require([r.get('source_id') for r in document['records'] if isinstance(r, dict)] == list(records),
            'Missing, duplicated, reordered or unknown source records')
    for record in document['records']:
        fields(record, ['source_id', 'ru', 'vocabulary'])
        nonempty(record['ru'])
        require(isinstance(record['vocabulary'], list), 'Vocabulary must be a list')
        source = records[record['source_id']]
        occupied = set()
        first_starts = []
        for word in record['vocabulary']:
            fields(word, ['spans', 'lemma', 'pos', 'context_ru', 'general_ru'],
                   ['glossary_id', 'terminology_note'])
            for key in ('lemma', 'context_ru', 'general_ru'):
                nonempty(word[key])
            require(word['pos'] in POS, 'Unknown part of speech')
            require(isinstance(word['spans'], list) and word['spans'], 'Empty vocabulary spans')
            previous = -1
            for span in word['spans']:
                fields(span, ['start', 'end', 'text'])
                a, b = span['start'], span['end']
                require(type(a) is int and type(b) is int and 0 <= a < b <= len(source), 'Invalid span bounds')
                require(a >= previous, 'Unordered or overlapping expression spans')
                require(source[a:b] == span['text'] and bool(span['text'].strip()), 'Span text mismatch')
                require(not occupied.intersection(range(a, b)), 'Overlapping vocabulary units')
                require(not span['text'][0].isspace() and not span['text'][-1].isspace(), 'Span includes surrounding whitespace')
                occupied.update(range(a, b))
                previous = b
            first_starts.append(word['spans'][0]['start'])
            if 'terminology_note' in word:
                nonempty(word['terminology_note'])
                require('glossary_id' in word, 'Terminology note requires glossary reference')
            if 'glossary_id' in word:
                require(word['glossary_id'] in terms, 'Unknown glossary reference')
                term = terms[word['glossary_id']]
                require((word['lemma'], word['pos']) == (term['lemma'], term['pos']), 'Glossary lemma/POS conflict')
                require(word['general_ru'] == term['ru'], 'Glossary general meaning conflict')
        require(first_starts == sorted(first_starts), 'Vocabulary must follow first-span source order')
    validate_review(review, document, records, terms)


def validate_review(review, document, records, terms):
    """Require explicit language review attestations; never infer quality from structure."""
    fields(review, ['schema_version', 'source_id', 'result_sha256', 'glossary_sha256', 'status',
                    'review_mode', 'reviewer', 'checks', 'issues', 'references'])
    require(review['schema_version'] == 1 and review['source_id'] == document['source_id'], 'Wrong review identity')
    canonical = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    require(review['result_sha256'] == digest(canonical), 'Review does not match result')
    used = sorted({v['glossary_id'] for r in document['records'] for v in r['vocabulary'] if 'glossary_id' in v})
    canonical_terms = json.dumps([terms[k] for k in used], ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    require(review['glossary_sha256'] == digest(canonical_terms), 'Review does not match glossary')
    require(review['status'] in ('draft', 'complete'), 'Invalid review status')
    require(review['review_mode'] in ('pending', 'independent', 'self_review'), 'Invalid review mode')
    require(isinstance(review['reviewer'], str), 'Invalid reviewer')
    fields(review['checks'], ['fidelity', 'one_to_one', 'natural_russian', 'vocabulary', 'terminology', 'headings'])
    require(all(type(v) is bool for v in review['checks'].values()), 'Review checks must be booleans')
    require(isinstance(review['issues'], list) and isinstance(review['references'], list), 'Invalid review lists')
    for issue in review['issues']:
        fields(issue, ['source_id', 'blocking', 'resolved', 'note'])
        require(issue['source_id'] in records, 'Unknown issue source ID')
        require(type(issue['blocking']) is bool and type(issue['resolved']) is bool, 'Invalid issue flags')
        nonempty(issue['note'])
    for reference in review['references']:
        fields(reference, ['location', 'purpose'])
        nonempty(reference['location'])
        nonempty(reference['purpose'])
    if review['status'] == 'complete':
        require(review['review_mode'] != 'pending' and review['reviewer'].strip(), 'Missing completed review')
        require(all(review['checks'].values()), 'Incomplete language review')
        require(not any(i['blocking'] and not i['resolved'] for i in review['issues']), 'Unresolved blocking issue')


def result_paths(base, identity, section):
    """Use a fixed location for each target and its review metadata."""
    kind = 'sections' if section is not None else 'headings'
    return base / kind / f'{identity}.yaml', base / 'reviews' / f'{identity}.yaml'


def validate_output(root, identity=None, require_complete=False):
    """Validate selected or all stored outputs; return explicit per-target progress."""
    chapters = library(root)
    base = root / 'data/homebrew/ru'
    terms = glossary_entries(read(base / 'glossary.yaml'))
    found = list((base / 'sections').glob('*.yaml')) + list((base / 'headings').glob('*.yaml'))
    if identity:
        chapter, section = locate(chapters, identity)
        found = [result_paths(base, identity, section)[0]]
    summaries, identities = [], set()
    for path in sorted(found):
        chapter, section = locate(chapters, path.stem)
        expected, review_path = result_paths(base, path.stem, section)
        require(path == expected, f'Wrong output location: {path}')
        document, review = read(path), read(review_path)
        validate_document(document, source_records(chapter, section), terms, review)
        require(path.stem not in identities, 'Duplicate translation target')
        identities.add(path.stem)
        if require_complete:
            require(review['status'] == 'complete', f'Draft target: {path.stem}')
        if section is not None and review['status'] == 'complete':
            heading, heading_review = result_paths(base, chapter['id'], None)
            heading_doc, heading_meta = read(heading), read(heading_review)
            validate_document(heading_doc, source_records(chapter), terms, heading_meta)
            require(heading_meta['status'] == 'complete', 'Chapter heading is not complete')
        summaries.append({'source_id': path.stem, 'status': review['status']})
    if identity is None:
        require({p.stem for p in (base / 'reviews').glob('*.yaml')} == identities, 'Orphan/missing review metadata')
    total = sum(len(c['sections']) + 1 for c in chapters)
    return {'validated': summaries, 'available': len(summaries), 'total_targets': total,
            'note': 'Validates available output only; absent translations are not complete.'}


def archived_context(root, provenance):
    """Read whole source articles or cited PDF pages with one neighboring page each."""
    grouped = {}
    for record in provenance.values():
        grouped.setdefault(record['source_path'], []).append(record)
    result = []
    for relative, records in sorted(grouped.items()):
        path = (root / relative).resolve()
        require(root.resolve() in path.parents, 'Source path escapes repository')
        require(path.is_file(), f'Missing required source: {relative}')
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        require(all(r['sha256'] == sha for r in records), f'Changed archived source: {relative}')
        if path.suffix.lower() == '.pdf':
            pdf = PdfReader(path)
            pages = sorted({p for r in records for p in range(r['pdf_page'] - 2, r['pdf_page'] + 1)
                            if 0 <= p < len(pdf.pages)})
            body = [{'page': p + 1, 'text': pdf.pages[p].extract_text() or ''} for p in pages]
            require(all(p['text'].strip() for p in body), f'Empty PDF extraction: {relative}')
        else:
            soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
            for node in soup.select('script, style, nav, header, footer, svg, button, noscript'):
                node.decompose()
            containers = soup.select('.journal-content-article, .ifu-block--article')
            containers = containers or [soup.find('main') or soup.body or soup]
            body = '\n\n'.join(node.get_text(' ', strip=True) for node in containers)
            require(bool(body.strip()), f'Empty article extraction: {relative}')
        result.append({'path': relative, 'sha256': sha, 'context': body})
    return result


def prepare_context(root, identity):
    """Build a complete local context bundle; never fetch external facts."""
    chapters = library(root)
    chapter, section = locate(chapters, identity)
    require(section is not None, 'Prepare expects a section ID, not a chapter ID')
    base = root / 'data/homebrew'
    number = chapter['id'].removeprefix('hb-c')
    provenance = read(base / f'metadata/{number}_provenance.yaml')['units']
    selected = {u['id']: provenance[u['id']] for u in units(section)}
    glossary = read(base / 'ru/glossary.yaml')
    glossary_entries(glossary)
    completed, index = [], []
    for path in sorted((base / 'ru/sections').glob('*.yaml')):
        other_chapter, other_section = locate(chapters, path.stem)
        _, review_path = result_paths(base / 'ru', path.stem, other_section)
        meta = read(review_path)
        if meta['status'] != 'complete':
            continue
        validate_output(root, path.stem, require_complete=True)
        index.append({'source_id': path.stem, 'title': other_section['title'], 'path': str(path.relative_to(root))})
        if other_chapter['id'] == chapter['id']:
            completed.append(read(path))
    records = source_records(chapter, section)
    return {'schema_version': 1, 'target_section_id': identity,
            'source_sha256': fingerprint(records), 'target_records': records,
            'chapter_heading_records': source_records(chapter),
            'chapter_heading_sha256': fingerprint(source_records(chapter)),
            'book_outline': [{'id': c['id'], 'title': c['title'],
                              'sections': [{'id': s['id'], 'title': s['title']} for s in c['sections']]}
                             for c in chapters],
            'parent_chapter': chapter, 'provenance': selected,
            'archived_context': archived_context(root, selected),
            'editorial_review': read(base / f'metadata/{number}_editorial_review.yaml'),
            'attribution': read(base / 'metadata/attribution.yaml'),
            'glossary': glossary, 'completed_same_chapter': completed,
            'completed_translation_index': index,
            'further_context_instruction': 'Read related completed translations and Swedish passages from the index/outline as needed; record consequential terminology references.'}


def main():
    """Expose preparation and validation commands with nonzero failure exits."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prepare = sub.add_parser('prepare')
    prepare.add_argument('section_id')
    prepare.add_argument('--output', type=Path, required=True)
    validate = sub.add_parser('validate')
    validate.add_argument('--source-id')
    validate.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            bundle = prepare_context(ROOT, args.section_id)
            destination = args.output.resolve()
            require(destination != ROOT.resolve() and ROOT / 'data' not in destination.parents,
                    'Context output must not be inside data/')
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('x', encoding='utf-8') as handle:
                yaml.safe_dump(bundle, handle, allow_unicode=True, sort_keys=False, width=100)
            print(f'Prepared {args.section_id}: {destination}')
        else:
            print(json.dumps(validate_output(ROOT, args.source_id, args.require_complete), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
