"""Summarize the completed archive edition and expose remaining editorial gaps."""
from collections import defaultdict

from build_pilot import DEST, WORK, read_yaml


def main():
    manifest = read_yaml(DEST / 'manifest.yaml')
    assert len(manifest['chapters']) == 12, 'Finish all chapters before final review'
    outline = read_yaml(WORK / 'outline.yaml')['chapters']
    lines = ['# Completed collection review', '',
        'All twelve Swedish chapters are composed from the three frozen repository sources.',
        'The approved pilot and remaining chapters have source/topic omission audits.',
        'The archived law defines the scope; it is not used to invent replacement teaching prose.', '',
        '## Collection', '',
        '| Chapter | Sections | Sourced text units | Sentence ranges | Words | Source files |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    total = [0, 0, 0, 0]
    repeats = defaultdict(list)
    reviews = []
    for entry in manifest['chapters']:
        number = f'{entry["order"]:02d}'
        chapter = read_yaml(DEST / entry['path'])
        units = [u for section in chapter['sections'] for block in section['blocks']
                 for u in block.get('items', [block])]
        provenance = read_yaml(DEST / f'metadata/{number}_provenance.yaml')['units']
        counts = [len(chapter['sections']), len(units),
                  sum(len(u['sentences']) for u in units),
                  sum(len(u['text'].split()) for u in units)]
        total = [a + b for a, b in zip(total, counts)]
        reader = 'PILOT.sv.md' if number == '05' else f'chapters/{number}/READING.sv.md'
        lines.append(f'| [{number}]({reader}) | ' + ' | '.join(map(str, counts)) +
                     f' | {len({u["source_path"] for u in provenance.values()})} |')
        for unit in units:
            if len(unit['text'].split()) >= 12:
                repeats[unit['text']].append(unit['id'])
        reviews.append((number, read_yaml(DEST / f'metadata/{number}_editorial_review.yaml')))
    lines += ['| Total | ' + ' | '.join(map(str, total)) + ' | — |', '',
        'Counts include paragraphs and individual list items; words are whitespace-delimited.', '',
        '## Archived legal scope', '',
        '| Scope key | Chapters |', '| --- | --- |']
    for scope in ['society', 'culture', 'history', 'rights', 'equality', 'legislation']:
        lines.append(f'| {scope} | ' + ', '.join(c['id'] for c in outline if scope in c['scope']) + ' |')
    lines += ['', '## Omission and overlap review', '',
        'Every mapped source unit has a chapter-specific disposition and reason. Source headings,',
        'glossaries, examples and practical pages were checked for substantive rights and duties.',
        'Useful qualifications and service-access conditions remain; activities, navigation,',
        'directories, application walkthroughs and clearly peripheral shopping/lifestyle coaching',
        'are omitted. Chapter audits explain the actual decisions, including supplemental sources.', '',
        'Cross-chapter review covered school and welfare history, child/guardian rights, health',
        'access, family support, work permits, housing assistance and protection from violence.',
        'Small repetitions are retained where they make independent chapters understandable.',
        'The repeated municipal/welfare-election eligibility list items within chapter 04 are',
        'intentional: each electoral rule keeps its complete qualifying list.',
        'The following diagnostic lists exact repeats of at least twelve words; it does not detect',
        'paraphrases in the originals or claim that all conceptual repetition has been removed.', '']
    cross = [(text, ids) for text, ids in repeats.items()
             if len({identity.split('-u')[0] for identity in ids}) > 1]
    lines.append(f'{len(cross)} passages repeat verbatim across chapters.')
    lines.append('')
    for text, identities in cross:
        lines.append('- ' + ', '.join(identities) + ': ' + text[:110].replace('\n', ' ') + '…')
    lines += ['', '## Source gaps and limitations', '',
        'These entries are carried from the individual editorial audits. Some concern precision',
        'within a covered topic rather than a wholly missing topic. Conflicts are not silently',
        'reconciled using outside facts. See each linked audit for source references and resolutions.', '']
    for number, review in reviews:
        for gap in review['gaps']:
            lines.append(f'- **{number}: {gap["topic"]}.** {gap["reason"]} '
                         f'([audit](../../data/homebrew/metadata/{number}_editorial_review.yaml))')
    lines += ['', '## Text, sentence and asset review', '',
        'All selected passages are checked against original HTML selectors or PDF page ranges and',
        'frozen source hashes. Only whitespace normalization and recorded contiguous excerpt cuts',
        'are used. Swedish headings are editorial. Source-era spellings and claims are preserved.',
        'Sentence ranges cover the complete text and retain stable IDs. Boundary diagnostics',
        'include abbreviations, decimals, initials, quotations, short list items and lowercase starts.',
        'Two unpublished d.v.s. boundaries were corrected before committing chapters 04 and 12;',
        'the pilot guardian-paragraph correction explicitly retires its removed sentence ID.', '',
        'Selected material is readable as prose and lists. No selected explanation depends on a',
        'missing image; no remote illustrations were fetched. Real image/table ingestion remains',
        'unsupported by the builder and is rejected by the collection validator.', '',
        'Representative selected PDF pages 6, 22, 65, 78 and 124 were visually checked against',
        'their rendered pages, in addition to pilot pages 114 and 115. These passages are prose;',
        'their paragraph boundaries and reading order do not depend on illustrations.', '',
        'This completes the planned archive-based edition, not a certification of current law or',
        'full coverage of an eventual official question bank. Translations and flashcards are deferred.', '']
    (WORK / 'FINAL_REVIEW.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
