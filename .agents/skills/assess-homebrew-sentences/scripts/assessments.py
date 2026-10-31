"""Prepare source context and validate Homebrew sentence assessments, read-only."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

SCORES = {
    'exam_relevance', 'knowledge_value', 'factual_specificity',
    'question_suitability', 'change_risk',
}
FACT_TYPES = {
    'date', 'number', 'name', 'definition', 'institution', 'right',
    'obligation', 'rule', 'procedure', 'exception', 'explanation',
}
RECORD_FIELDS = {
    'sentence_id', 'scores', 'fact_types', 'context_sentence_ids',
    'duplicate_of', 'assessment_confidence', 'rationale',
}


def require(condition, message):
    """Raise a useful validation error, including under optimized Python."""
    if not condition:
        raise ValueError(message)


def exact_keys(value, keys, label):
    """Reject missing or unexpected fields."""
    require(isinstance(value, dict) and set(value) == set(keys),
            f'{label}: expected exactly {sorted(keys)}')


def string_list(value, label):
    """Require a list of distinct, nonempty strings."""
    require(isinstance(value, list) and
            all(isinstance(v, str) and v.strip() for v in value),
            f'{label}: expected a list of nonempty strings')
    require(len(value) == len(set(value)), f'{label}: repeated values')


def source_index(root):
    """Reuse the repository's canonical source slicing and fingerprint helpers."""
    sys.path.insert(0, str(root))
    from translation.homebrew.tools.workflow import (
        fingerprint, library, source_records,
    )

    sections, sentences, targets = {}, {}, {}
    for chapter in library(root):
        chapter_ids = []
        for section in chapter['sections']:
            records = source_records(chapter, section)
            body = {key: value for key, value in records.items()
                    if key != section['id']}
            sections[section['id']] = {
                'chapter_id': chapter['id'], 'chapter_title': chapter['title'],
                'section': section, 'sentences': body,
                'source_sha256': fingerprint(records),
            }
            for identity, text in body.items():
                require(identity not in sentences, f'Duplicate source ID: {identity}')
                sentences[identity] = {
                    'section_id': section['id'], 'text': text,
                    'position': len(sentences),
                }
                targets[identity] = [identity]
            targets[section['id']] = list(body)
            chapter_ids.extend(body)
        targets[chapter['id']] = chapter_ids
    return sections, sentences, targets


def resolve(requested, sentences, targets):
    """Expand canonical chapter/section/sentence IDs, deduplicating in source order."""
    selected = set()
    for target in requested:
        require(target in targets, f'Unknown target ID: {target}')
        selected.update(targets[target])
    require(selected, 'No body sentences selected')
    return [identity for identity in sentences if identity in selected]


def prepare(selected, sections, sentences):
    """Produce exact context without writing assessments or guessing ratings."""
    touched = dict.fromkeys(sentences[s]['section_id'] for s in selected)
    return {
        'requested_sentence_ids': selected,
        'sections': [
            {
                'section_id': identity,
                'chapter_id': sections[identity]['chapter_id'],
                'chapter_title': sections[identity]['chapter_title'],
                'source_sha256': sections[identity]['source_sha256'],
                'section': sections[identity]['section'],
                'sentences': sections[identity]['sentences'],
            }
            for identity in touched
        ],
    }


def validate_document(document, section_id, section, sentences):
    """Check a possibly partial section file and return its assessed IDs."""
    exact_keys(document, {'schema_version', 'section_id', 'source_sha256',
                          'assessments'}, section_id)
    require(type(document['schema_version']) is int and
            document['schema_version'] == 1, f'{section_id}: invalid schema version')
    require(document['section_id'] == section_id, f'{section_id}: wrong section ID')
    require(document['source_sha256'] == section['source_sha256'],
            f'{section_id}: stale source fingerprint; reassessment required')
    records = document['assessments']
    require(isinstance(records, list) and records, f'{section_id}: no assessments')
    seen = []
    for record in records:
        exact_keys(record, RECORD_FIELDS, section_id)
        identity = record['sentence_id']
        require(isinstance(identity, str) and identity in section['sentences'],
                f'{section_id}: unknown/non-body sentence ID: {identity!r}')
        require(identity not in seen, f'{identity}: repeated assessment')
        seen.append(identity)
        exact_keys(record['scores'], SCORES, identity)
        for key, score in record['scores'].items():
            require(type(score) is int and 0 <= score <= 3,
                    f'{identity}: {key} must be an integer from 0 through 3')
        string_list(record['fact_types'], f'{identity} fact_types')
        require(set(record['fact_types']) <= FACT_TYPES,
                f'{identity}: unknown fact type')
        string_list(record['context_sentence_ids'], f'{identity} context_sentence_ids')
        for reference in record['context_sentence_ids']:
            require(reference in sentences and reference != identity,
                    f'{identity}: unknown or self context reference: {reference}')
        duplicate = record['duplicate_of']
        if duplicate is not None:
            require(isinstance(duplicate, str) and duplicate in sentences,
                    f'{identity}: unknown duplicate reference: {duplicate!r}')
            require(sentences[duplicate]['position'] < sentences[identity]['position'],
                    f'{identity}: duplicate_of must reference an earlier sentence')
        require(record['assessment_confidence'] in ('low', 'medium', 'high'),
                f'{identity}: invalid assessment confidence')
        require(isinstance(record['rationale'], str) and record['rationale'].strip(),
                f'{identity}: rationale must be nonempty text')
    require(seen == [s for s in section['sentences'] if s in set(seen)],
            f'{section_id}: assessments must follow source order')
    return set(seen)


def validate(selected, sections, sentences, data_dir):
    """Require coverage of the actual requested scope, not just available files."""
    touched = dict.fromkeys(sentences[s]['section_id'] for s in selected)
    covered = set()
    for section_id in touched:
        path = data_dir / f'{section_id}.yaml'
        require(path.is_file(), f'Missing assessment file: {path}')
        document = yaml.safe_load(path.read_text(encoding='utf-8'))
        covered.update(validate_document(document, section_id, sections[section_id], sentences))
    missing = set(selected) - covered
    require(not missing, f'Missing requested assessments: {sorted(missing)}')
    return len(touched)


def main():
    """Run from the repository checkout; never mutate sources or output records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'validate'))
    parser.add_argument('targets', nargs='+', help='Canonical chapter, section, or sentence IDs')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--data-dir', type=Path,
                        help='Assessment directory (default: card_creator/homebrew/assessments)')
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        sections, sentences, targets = source_index(root)
        selected = resolve(args.targets, sentences, targets)
        if args.command == 'prepare':
            print(yaml.safe_dump(prepare(selected, sections, sentences),
                                 allow_unicode=True, sort_keys=False), end='')
        else:
            count = validate(selected, sections, sentences, args.data_dir or
                             root / 'card_creator/homebrew/assessments')
            print(f'Validated {len(selected)} requested sentences in {count} section files.')
    except (ValueError, OSError, yaml.YAMLError) as error:
        parser.exit(1, f'Assessment error: {error}\n')


if __name__ == '__main__':
    main()
