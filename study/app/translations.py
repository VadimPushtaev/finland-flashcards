"""Expose only reviewed Russian records that still match their Swedish source."""
import hashlib
import json


def fingerprint(value, *, sort_keys=False):
    """Match the permanent translation workflow's canonical JSON digests."""
    raw = json.dumps(value, ensure_ascii=False, sort_keys=sort_keys, separators=(',', ':'))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def reviewed_records(base, identity, kind, source, terms, read):
    """Fail closed for missing, draft or stale translation/review data."""
    document = read(base / kind / f'{identity}.yaml')
    review = read(base / 'reviews' / f'{identity}.yaml')
    if (document['schema_version'] != 1 or document['language'] != 'ru'
            or document['source_id'] != identity or review['source_id'] != identity
            or document['source_sha256'] != fingerprint(list(source.items()))
            or review['status'] != 'complete' or review['review_mode'] not in ('independent', 'self_review')
            or not review['reviewer'] or not all(review['checks'][key] is True for key in
                ('fidelity', 'one_to_one', 'natural_russian', 'vocabulary', 'terminology', 'headings'))
            or any(i['blocking'] and not i['resolved'] for i in review['issues'])
            or review['result_sha256'] != fingerprint(document, sort_keys=True)
            or [r['source_id'] for r in document['records']] != list(source)):
        return None
    used = sorted({v['glossary_id'] for r in document['records'] for v in r['vocabulary'] if 'glossary_id' in v})
    if review['glossary_sha256'] != fingerprint([terms[k] for k in used], sort_keys=True):
        return None
    result = {}
    for record in document['records']:
        text = source[record['source_id']]
        occupied = set()
        for word in record['vocabulary']:
            previous = -1
            for span in word['spans']:
                start, end = span['start'], span['end']
                if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text)
                        or start < previous or text[start:end] != span['text']
                        or occupied.intersection(range(start, end))):
                    return None
                occupied.update(range(start, end))
                previous = end
        result[record['source_id']] = {**record, 'sv': text}
    return result
