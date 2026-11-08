"""Prepare scoped card translation jobs and validate the existing Russian schema."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from translation.homebrew.tools import workflow as w
from study.app.translations import reviewed_records


def catalog(root):
    """Resolve chapter, section and stable card IDs from canonical Swedish YAML."""
    cards, groups = {}, {}
    for chapter in w.library(root):
        cid = chapter['id']
        sections = {s['id'] for s in chapter['sections']}
        groups[cid] = []
        groups.update({sid: [] for sid in sections})
        path = root / 'data/homebrew/cards' / f'{cid}.yaml'
        if not path.exists():
            continue
        doc = w.read(path)
        w.require(doc['schema_version'] == 1 and doc['language'] == 'sv'
                  and doc['chapter_id'] == cid, f'Invalid card document: {path}')
        for card in doc['cards']:
            identity, sid = card['id'], card['section_id']
            w.require(re.fullmatch(r'hb-c\d{2}-[a-z0-9-]+-\d{4}', identity)
                      and identity.startswith(sid + '-') and sid in sections
                      and identity not in cards, f'Invalid/duplicate card ID: {identity}')
            options = card['options']
            w.require([o['id'] for o in options] == ['a0', 'a1', 'a2', 'a3']
                      and card['correct_option_id'] in ('a0', 'a1', 'a2', 'a3'),
                      f'Invalid answer IDs: {identity}')
            records = {identity + ':q': card['question']}
            records.update({identity + ':' + o['id']: o['text'] for o in options})
            for value in records.values():
                w.nonempty(value)
            cards[identity] = {'card': card, 'chapter_id': cid, 'source_records': records}
            groups[cid].append(identity)
            groups[sid].append(identity)
    return cards, groups


def select(cards, groups, targets):
    """Expand requested scopes, rejecting typos instead of dropping targets."""
    selected = []
    for target in targets:
        w.require(target in cards or target in groups, f'Unknown target: {target}')
        selected.extend([target] if target in cards else groups[target])
    return list(dict.fromkeys(selected))


def prepare(root, targets):
    """Include full parent section context once and exact five-surface card jobs."""
    cards, groups = catalog(root)
    selected = select(cards, groups, targets)
    section_ids = list(dict.fromkeys(cards[i]['card']['section_id'] for i in selected))
    jobs = []
    for identity in selected:
        entry = cards[identity]
        jobs.append({'card_id': identity, **entry,
                     'source_sha256': w.fingerprint(entry['source_records']),
                     'result_path': f'data/homebrew/ru/cards/{identity}.yaml',
                     'review_path': f'data/homebrew/ru/reviews/{identity}.yaml'})
    return {'schema_version': 1, 'requested_targets': targets, 'cards': jobs,
            'section_contexts': {sid: w.prepare_context(root, sid) for sid in section_ids},
            'card_provenance': {sid: w.read(path) for sid in section_ids
                if (path := root / 'card_creator/homebrew/card_sources' / f'{sid}.yaml').exists()}}


def validate(root, targets=(), require_complete=False):
    """Validate explicit scope including missing files, or all available outputs."""
    cards, groups = catalog(root)
    base = root / 'data/homebrew/ru'
    terms = w.glossary_entries(w.read(base / 'glossary.yaml'))
    available = {p.stem for p in (base / 'cards').glob('*.yaml')}
    selected = select(cards, groups, targets) if targets else sorted(available)
    if not targets:
        orphan = {p.stem for p in (base / 'reviews').glob('*.yaml')
                  if re.fullmatch(r'hb-c\d{2}-[a-z0-9-]+-\d{4}', p.stem)} - available
        w.require(not orphan, f'Orphan card reviews: {sorted(orphan)}')
    summaries = []
    for identity in selected:
        w.require(identity in cards, f'Unknown card translation: {identity}')
        records = cards[identity]['source_records']
        document = w.read(base / 'cards' / f'{identity}.yaml')
        review = w.read(base / 'reviews' / f'{identity}.yaml')
        w.validate_document(document, records, terms, review, target_id=identity)
        if require_complete:
            w.require(review['status'] == 'complete', f'Draft card: {identity}')
        if review['status'] == 'complete':
            w.require(reviewed_records(base, identity, 'cards', records, terms, w.read) is not None,
                      f'Card is not available to the study app: {identity}')
        summaries.append({'source_id': identity, 'status': review['status']})
    return {'validated': summaries, 'validated_count': len(summaries), 'total_cards': len(cards),
            'note': 'Explicit scopes require every selected card; no targets validates available files only.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('targets', nargs='+')
    prep.add_argument('--output', type=Path, required=True)
    check = sub.add_parser('validate')
    check.add_argument('targets', nargs='*')
    check.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'prepare':
            destination = args.output.resolve()
            w.require(ROOT / 'data' not in destination.parents, 'Keep context outside data/')
            w.require(not destination.exists(), 'Context output already exists')
            bundle = prepare(ROOT, args.targets)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open('x', encoding='utf-8') as handle:
                w.yaml.safe_dump(bundle, handle, allow_unicode=True, sort_keys=False, width=100)
            print(f'Prepared {len(bundle["cards"])} cards: {destination}')
        else:
            print(json.dumps(validate(ROOT, args.targets, args.require_complete), indent=2))
    except (OSError, ValueError, KeyError, TypeError, w.yaml.YAMLError) as error:
        parser.exit(1, f'Card translation error: {error}\n')


if __name__ == '__main__':
    main()
