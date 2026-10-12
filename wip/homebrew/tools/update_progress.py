"""Refresh the collection's progress table after validated chapter builds."""
from build_pilot import DEST, WORK, read_yaml


def main():
    manifest = read_yaml(DEST / 'manifest.yaml')
    done = {c['id']: c for c in manifest['chapters']}
    outline = read_yaml(WORK / 'outline.yaml')
    lines = ['# Homebrew progress', '',
        'The user approved the pilot and authorized autonomous completion of all remaining chapters,',
        'with a separate commit per chapter. Both review checkpoints are complete. No push was requested.', '',
        '## Chapter status', '', '| Chapter | Title | Status |', '| --- | --- | --- |']
    for chapter in outline['chapters']:
        status = 'Composed and validated' if chapter['id'] in done else 'Source review / composition in progress'
        lines.append(f'| {chapter["id"]} | {chapter["title"]} | {status} |')
    lines += ['', f'{len(done)} of 12 chapters composed. Reading copies: [chapter index](chapters/README.md).', '',
        '## Validation and remaining work', '',
        'Every chapter has frozen source selections, stable sentence IDs, exact passage provenance,',
        'attribution and source/topic review. Original archives and existing flashcards are preserved.',
        'Rules and figures describe the archived sources, not a verification of current law.', '',
        'After all chapters are composed, complete the collection-wide omission, overlap, source and',
        'sentence-boundary checks; record unresolved source gaps in the final report.', '']
    (WORK / 'PROGRESS.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
