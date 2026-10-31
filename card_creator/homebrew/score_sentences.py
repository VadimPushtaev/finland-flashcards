"""Score validated Homebrew assessments and select study-priority tiers, read-only."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
WEIGHTS = {'exam_relevance': 9, 'knowledge_value': 6,
           'question_suitability': 4, 'factual_specificity': 1}
TIERS = ('CORE', 'SUPPORTING', 'SKIP')
REFERENCE_CUTOFFS = (41, 40)


def score(scores):
    """Return the agreed 0-60 score; risk and confidence do not reduce priority."""
    total = 0
    for key, weight in WEIGHTS.items():
        value = scores.get(key)
        if type(value) is not int or not 0 <= value <= 3:
            raise ValueError(f'{key} must be an integer from 0 through 3')
        total += weight * value
    return total


def validate_cutoffs(core_min, supporting_min):
    """Allow empty tiers without splitting any tied score group."""
    if not (type(core_min) is int and type(supporting_min) is int and
            0 <= supporting_min < core_min <= 61):
        raise ValueError('Cutoffs require 0 <= SUPPORTING_MIN < CORE_MIN <= 61')


def classify(value, core_min=41, supporting_min=40):
    """Classify a score with inclusive lower boundaries."""
    validate_cutoffs(core_min, supporting_min)
    if type(value) is not int or not 0 <= value <= 60:
        raise ValueError('Score must be an integer from 0 through 60')
    return 'CORE' if value >= core_min else 'SUPPORTING' if value >= supporting_min else 'SKIP'


def calibrate(values):
    """Fit whole-collection 21% CORE / 14% SUPPORTING targets with intact ties."""
    counts = Counter(values)
    if not counts:
        raise ValueError('No current assessments available for calibration')
    for value in counts:
        classify(value)
    n = sum(counts.values())
    at_least = {cut: sum(count for value, count in counts.items() if value >= cut)
                for cut in range(62)}
    candidates = []
    for core_min in range(1, 62):
        for supporting_min in range(core_min):
            core = at_least[core_min]
            supporting = at_least[supporting_min] - core
            # Integer arithmetic avoids floating-point differences in tied fits.
            error = abs(100 * core - 21 * n) + abs(100 * supporting - 14 * n)
            reference_distance = abs(core_min - 41) + abs(supporting_min - 40)
            candidates.append((error, reference_distance, -core_min, -supporting_min))
    _, _, core_negative, supporting_negative = min(candidates)
    return -core_negative, -supporting_negative


def assessment_helper(root):
    """Load the existing assessment skill's source and validation implementation."""
    path = root / '.agents/skills/assess-homebrew-sentences/scripts/assessments.py'
    spec = importlib.util.spec_from_file_location('homebrew_assessments', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_assessments(helper, sections, sentences, data_dir):
    """Read all current records; report invalid files rather than calibrating on them."""
    records, inputs, excluded = {}, {}, []
    for path in sorted(data_dir.glob('*.yaml')):
        try:
            section_id = path.stem
            if section_id not in sections:
                raise ValueError(f'Unknown section filename: {section_id}')
            raw = path.read_bytes()
            document = yaml.safe_load(raw)
            helper.validate_document(document, section_id, sections[section_id], sentences)
            records.update((r['sentence_id'], r) for r in document['assessments'])
            inputs[section_id] = {
                'assessment_sha256': hashlib.sha256(raw).hexdigest(),
                'source_sha256': document['source_sha256'],
            }
        except (ValueError, OSError, yaml.YAMLError) as error:
            excluded.append({'path': str(path), 'error': str(error)})
    return records, inputs, excluded


def review_flags(record):
    """Identify review needs without changing scores or removing candidates."""
    flags = []
    if record['scores']['change_risk'] >= 2:
        flags.append('verify_changeable_fact')
    if record['assessment_confidence'] == 'low':
        flags.append('low_assessment_confidence')
    if record['scores']['question_suitability'] <= 1:
        flags.append('question_needs_reworking')
    return flags


def distribution(values, cutoffs):
    """Count all tiers, including those with zero candidates."""
    counts = Counter(classify(value, *cutoffs) for value in values)
    return {tier: counts[tier] for tier in TIERS}


def make_report(root, requested, *, all_assessed=False, tiers=('CORE',),
                cutoffs=None, data_dir=None):
    """Validate requested coverage before applying one global cutoff pair."""
    helper = assessment_helper(root)
    sections, sentences, targets = helper.source_index(root)
    records, inputs, excluded = load_assessments(
        helper, sections, sentences, data_dir or root / 'card_creator/homebrew/assessments')
    if all_assessed:
        selected = [s for s in sentences if s in records]
    else:
        selected = helper.resolve(requested, sentences, targets)
    missing = [s for s in selected if s not in records]
    if missing:
        detail = '; '.join(f"{item['path']}: {item['error']}" for item in excluded)
        raise ValueError(
            'Missing or invalid requested assessments: ' + ', '.join(missing) +
            '. Use $assess-homebrew-sentences for these targets, then retry.' +
            (' Invalid files: ' + detail if detail else ''))
    values = {s: score(r['scores']) for s, r in records.items()}
    if not values:
        raise ValueError('No current assessments; use $assess-homebrew-sentences first')
    effective = cutoffs or calibrate(values.values())
    validate_cutoffs(*effective)
    output = []
    for identity in selected:
        value = values[identity]
        tier = classify(value, *effective)
        if tier in tiers:
            record = records[identity]
            output.append({
                **record, 'section_id': sentences[identity]['section_id'],
                'text': sentences[identity]['text'], 'score': value,
                'priority': tier, 'review_flags': review_flags(record),
            })
    return {
        'schema_version': 1,
        'formula': '9*exam_relevance + 6*knowledge_value + 4*question_suitability + factual_specificity',
        'score_range': [0, 60],
        'calibration': {
            'mode': 'explicit_cutoffs' if cutoffs else 'global_tied_scores',
            'targets_percent': {'CORE': 21, 'SUPPORTING': 14},
            'core_min': effective[0], 'supporting_min': effective[1],
            'assessed_sentences': len(records), 'assessed_sections': len(inputs),
            'counts': distribution(values.values(), effective),
        },
        'assessment_inputs': inputs,
        'excluded_invalid_files': excluded,
        'requested_sentence_ids': selected,
        'requested_counts': distribution((values[s] for s in selected), effective),
        'included_tiers': list(tiers),
        'selected_count': len(output),
        'sentences': output,
    }


def main():
    """Emit a reproducible selection report; do not edit assessment files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('targets', nargs='*', help='Canonical chapter, section, or sentence IDs')
    parser.add_argument('--all-assessed', action='store_true', help='Report all current assessed sentences')
    parser.add_argument('--tiers', choices=TIERS, nargs='+', default=['CORE'])
    parser.add_argument('--cutoffs', type=int, nargs=2, metavar=('CORE_MIN', 'SUPPORTING_MIN'),
                        help='Explicit global cutoffs; default fits all current assessments')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--data-dir', type=Path, help='Alternative assessment directory')
    args = parser.parse_args()
    if bool(args.targets) == args.all_assessed:
        parser.error('Provide target IDs or --all-assessed, exclusively')
    try:
        report = make_report(args.root.resolve(), args.targets, all_assessed=args.all_assessed,
                             tiers=tuple(dict.fromkeys(args.tiers)),
                             cutoffs=args.cutoffs, data_dir=args.data_dir)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    except (ValueError, OSError, yaml.YAMLError) as error:
        parser.exit(1, f'Scoring error: {error}\n')


if __name__ == '__main__':
    main()
