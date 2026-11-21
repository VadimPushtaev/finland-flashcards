"""Assign optional study tiers to existing cards without changing their content.

Historical generation provenance is preserved. A card below today's CORE cutoff
is kept as EXTENDED even if its reassessed primary is now SUPPORTING or SKIP.
Sentence eligibility for future generation remains a separate four-tier policy.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from card_creator.homebrew.score_sentences import make_report, TIERS


def priority_plan(root=ROOT):
    """Match every canonical card to its primary source by exact exported row."""
    report = make_report(root, [f'hb-c{i:02d}' for i in range(1, 13)], tiers=TIERS)
    sentences = {r['sentence_id']: r for r in report['sentences']}
    cards, chapters, updates = [], {}, {}
    for number in range(1, 13):
        chapter = f'hb-c{number:02d}'
        path = root / 'data/homebrew/cards' / f'{chapter}.yaml'
        raw = path.read_text(encoding='utf-8')
        document = yaml.safe_load(raw)
        sources = {}
        for section in {c['section_id'] for c in document['cards']}:
            source_file = root / 'card_creator/homebrew/card_sources' / f'{section}.yaml'
            for item in yaml.safe_load(source_file.read_text())['cards']:
                key = (section, item['row_sha256'])
                if key in sources:
                    raise ValueError(f'Duplicate provenance: {key}')
                sources[key] = item
        seen, priorities = set(), {}
        for card in document['cards']:
            flags = ' '.join('1' if o['id'] == card['correct_option_id'] else '0'
                             for o in card['options'])
            row = '|'.join([card['question'], card['category'], '2',
                            *(o['text'] for o in card['options']), '', flags, '2'])
            key = (card['section_id'], hashlib.sha256(row.encode()).hexdigest())
            if key not in sources or key in seen:
                raise ValueError(f'Missing or repeated provenance: {card["id"]}')
            seen.add(key)
            primary = sentences[sources[key]['primary_sentence_id']]
            if primary['section_id'] != card['section_id']:
                raise ValueError(f'Primary source belongs to another section: {card["id"]}')
            tier = 'CORE' if primary['priority'] == 'CORE' else 'EXTENDED'
            priorities[card['id']] = tier
            cards.append({'card_id': card['id'], 'chapter_id': chapter,
                          'primary_sentence_id': primary['sentence_id'], 'score': primary['score'],
                          'sentence_priority': primary['priority'], 'study_priority': tier,
                          'row_sha256': key[1]})
        if seen != set(sources):
            raise ValueError(f'Unmatched source records: {chapter}')
        counts = Counter(priorities.values())
        chapters[chapter] = {'core_min': report['calibration']['chapter_cutoffs'][chapter]['core_min'],
                             'CORE': counts['CORE'], 'EXTENDED': counts['EXTENDED']}
        if number <= 4:
            if counts['EXTENDED'] or any(c.get('study_priority', 'CORE') != 'CORE'
                                         for c in document['cards']):
                raise ValueError(f'Chapters 1-4 must retain all current CORE cards: {chapter}')
            continue
        # Preserve exact wording, IDs, order and YAML formatting; change one field.
        lines = []
        for line in raw.splitlines(keepends=True):
            if line.startswith('  study_priority:'):
                continue
            lines.append(line)
            if line.startswith('- id: '):
                identity = yaml.safe_load(line)[0]['id']
                lines.append(f'  study_priority: {priorities[identity]}\n')
        expected = ''.join(lines)
        updated = yaml.safe_load(expected)
        without_tier = lambda c: {k: v for k, v in c.items() if k != 'study_priority'}
        if ([without_tier(c) for c in updated['cards']] !=
                [without_tier(c) for c in document['cards']]):
            raise ValueError(f'Unexpected content change: {chapter}')
        if any(c['study_priority'] != priorities[c['id']] for c in updated['cards']):
            raise ValueError(f'Priority insertion failed: {chapter}')
        updates[path] = expected
    return {'policy': report['calibration'], 'assessment_inputs': report['assessment_inputs'],
            'chapters': chapters, 'cards': cards}, updates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--report', type=Path, help='Save an audit of this policy application')
    args = parser.parse_args()
    report, updates = priority_plan()
    stale = [p for p, text in updates.items() if p.read_text(encoding='utf-8') != text]
    if args.check and stale:
        parser.exit(1, 'Stale card priorities: ' + ', '.join(p.name for p in stale) + '\n')
    if not args.check:
        for path in stale:
            path.write_text(updates[path], encoding='utf-8')
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report['chapters'], indent=2))


if __name__ == '__main__':
    main()
