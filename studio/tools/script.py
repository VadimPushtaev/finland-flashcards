"""Initialize, validate, and export bilingual episode scripts using local sources."""
from __future__ import annotations

import argparse
import copy
import hashlib
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from translation.homebrew.tools import workflow as translations


def require(condition, message):
    """Fail clearly, including under optimized Python execution."""
    if not condition:
        raise ValueError(message)


def read(path):
    """Load a local YAML document."""
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def write(path, document):
    """Write a deterministic, Unicode YAML document."""
    path.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False,
                                   width=95), encoding='utf-8')


def file_hash(path):
    """Fingerprint exact source-file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_context(section_id, root=ROOT):
    """Resolve canonical source paths and require current reviewed translations."""
    base = root / 'data/homebrew'
    chapter, section = translations.locate(translations.library(root), section_id)
    require(section is not None, 'Choose a section ID, not a chapter ID')
    # Reuse the translation workflow's full record, review, and glossary checks.
    translations.validate_output(root, section_id, require_complete=True)
    translations.validate_output(root, chapter['id'], require_complete=True)
    entry = next(c for c in read(base / 'manifest.yaml')['chapters']
                 if c['id'] == chapter['id'])
    chapter_path = base / entry['path']
    translation_path = base / 'ru/sections' / f'{section_id}.yaml'
    records = translations.source_records(chapter, section)
    russian = {r['source_id']: r['ru'] for r in read(translation_path)['records']}
    return dict(root=root, chapter=chapter, section=section, records=records,
                russian=russian, chapter_path=chapter_path,
                translation_path=translation_path)


def source_snapshot(context):
    """Collect used passage provenance and original credit records without rewriting them."""
    root = context['root']
    base = root / 'data/homebrew'
    chapter_id = context['chapter']['id']
    provenance_path = base / 'metadata' / f'{chapter_id[-2:]}_provenance.yaml'
    provenance = read(provenance_path)['units']
    sources = {s['path']: s for s in read(base / 'metadata/sources.yaml')['sources']}
    credits = read(base / 'metadata/attribution.yaml')['sources']
    unit_ids = [u['id'] for u in translations.units(context['section'])]
    used_paths = list(dict.fromkeys(provenance[u]['source_path'] for u in unit_ids))
    for path in used_paths:
        require(file_hash(root / path) == sources[path]['sha256'],
                f'Changed original source archive: {path}')
    for unit_id in unit_ids:
        source = provenance[unit_id]
        require(source['sha256'] == sources[source['source_path']]['sha256'],
                f'Stale passage provenance: {unit_id}')
    return dict(
        schema_version=1, section_id=context['section']['id'],
        provenance_path=str(provenance_path.relative_to(root)),
        units={u: copy.deepcopy(provenance[u]) for u in unit_ids},
        sources=[dict(source=copy.deepcopy(sources[p]),
                      attribution=copy.deepcopy(credits[sources[p]['source_group']]))
                 for p in used_paths],
    )


def scaffold(context):
    """Copy the template and fill source-owned fields; creative choices stay empty."""
    root = context['root']
    script = read(root / 'studio/templates/script.yaml')
    section = context['section']
    script.update(
        section_id=section['id'], chapter_id=context['chapter']['id'],
        title_sv=section['title'], title_ru=context['russian'][section['id']],
        source_path=str(context['chapter_path'].relative_to(root)),
        translation_path=str(context['translation_path'].relative_to(root)),
        source_section_sha256=translations.fingerprint(context['records']),
        translation_file_sha256=file_hash(context['translation_path']),
    )
    row_template = script['sentences'][0]
    script['sentences'] = []
    for sentence_id, sv in list(context['records'].items())[1:]:
        row = copy.deepcopy(row_template)
        row.update(sentence_id=sentence_id, sv=sv, ru=context['russian'][sentence_id],
                   visual_cue='')
        script['sentences'].append(row)
    return script


def unique_ids(items, label):
    """Check unique nonempty IDs in an ordered list of planning records."""
    require(isinstance(items, list), f'{label} must be a list')
    ids = [item.get('id') for item in items]
    require(all(isinstance(i, str) and i.strip() for i in ids), f'Missing {label} ID')
    require(len(ids) == len(set(ids)), f'Duplicate {label} ID')
    return set(ids)


def validate(script, context, ready=False):
    """Check source fidelity and script references; ready mode checks editorial coverage."""
    require(script['schema_version'] == 1 and script['example_only'] is False,
            'Expected a complete production script, not a partial example')
    expected = scaffold(context)
    for key in ('section_id', 'chapter_id', 'title_sv', 'title_ru', 'source_path',
                'translation_path', 'source_section_sha256', 'translation_file_sha256'):
        require(script[key] == expected[key], f'Stale or incorrect {key}')
    rows = script['sentences']
    require([r['sentence_id'] for r in rows] == [r['sentence_id'] for r in expected['sentences']],
            'Missing, duplicate, reordered, or unknown sentence ID')
    scenes = unique_ids(script['scenes'], 'scene')
    assets = unique_ids(script['asset_requests'], 'asset request')
    unique_ids(script['episode_decisions'], 'episode decision')
    for decision in script['episode_decisions']:
        require(decision['status'] in ('proposed', 'deferred', 'approved'), 'Invalid decision status')
        require(bool(decision['decision'].strip()), 'Empty episode decision')
        require(decision['resolve_during'] in ('script', 'assets', 'render'),
                'Unknown decision stage')
        if ready:
            require(not (decision['status'] == 'deferred' and decision['resolve_during'] == 'script'),
                    'Unresolved script-stage decision')
    for scene in script['scenes']:
        require(bool(scene['description'].strip()), 'Empty scene description')
    for asset in script['asset_requests']:
        require(asset['kind'] in ('background', 'foreground', 'music', 'narration'),
                'Invalid asset kind')
        require(bool(asset['description'].strip()) and bool(asset['fallback'].strip()),
                'Asset request needs a description and fallback')
    used_assets, used_scenes = set(), set()
    for row, source in zip(rows, expected['sentences']):
        sid = row['sentence_id']
        require(row['sv'] == source['sv'] and row['ru'] == source['ru'],
                f'Changed Swedish or Russian text: {sid}')
        require(row['scene_id'] is None or row['scene_id'] in scenes, f'Unknown scene: {sid}')
        require(set(row['asset_ids']) <= assets, f'Unknown asset reference: {sid}')
        used_assets.update(row['asset_ids'])
        used_scenes.add(row['scene_id'])
        require(all(h and h in row['sv'] for h in row['text_highlights']),
                f'Highlight is not exact source text: {sid}')
        pause = row['pause_after_seconds']
        require(pause is None or (type(pause) in (int, float) and 0 <= pause <= 10),
                f'Invalid pause: {sid}')
        start, end = row['start_seconds'], row['end_seconds']
        require((start is None and end is None) or
                (type(start) in (int, float) and type(end) in (int, float) and 0 <= start < end),
                f'Invalid audio timing: {sid}')
        override = row['speech_override']
        if override is not None:
            require(override['text'].strip() and override['reason'].strip(),
                    f'Speech override needs text and reason: {sid}')
            require(override['review_status'] in ('pending', 'approved'),
                    f'Invalid speech override review status: {sid}')
        if row['display_segments']:
            for language in ('sv', 'ru'):
                joined = ' '.join(s[language] for s in row['display_segments'])
                require(joined.split() == row[language].split(),
                        f'Display segments omit, change, or repeat {language} text: {sid}')
        if ready:
            require(row['scene_id'] and row['asset_ids'] and row['visual_cue'].strip(),
                    f'Missing visual plan: {sid}')
            require(pause is not None, f'Missing planned pause: {sid}')
    if ready:
        require(script['episode_decisions'], 'Missing episode decisions')
        require(used_scenes - {None} == scenes, 'Unused scene')
        transitions = [row['scene_id'] for i, row in enumerate(rows)
                       if i == 0 or row['scene_id'] != rows[i - 1]['scene_id']]
        require(transitions == [s['id'] for s in script['scenes']],
                'Scene groups must be consecutive and match scene-list order')
        require({'music', 'narration'} <= {a['kind'] for a in script['asset_requests']},
                'Missing episode music or narration request')
        require(assets - used_assets <= {a['id'] for a in script['asset_requests']
                                        if a['kind'] in ('music', 'narration')},
                'Unused visual asset request')


def review_markdown(script, context):
    """Render a readable review copy; YAML remains the sole editable script."""
    lines = [f"# {script['title_sv']}", '', script['title_ru'], '',
             '> Generated from script.yaml. Edit YAML, then run the review command.', '',
             'Status: source-validated script; see assets.yaml for acquired files and review.md for approval status.', '',
             f"Shared direction: [DIRECTING.md](../../DIRECTING.md). Section: `{script['section_id']}`.", '',
             f"{len(script['sentences'])} sentences; {sum(len(r['sv'].split()) for r in script['sentences'])} Swedish words. "
             'Final timeline timestamps are assigned during assembly from measured audio and planned pauses.', '',
             '## Episode decisions', '']
    for decision in script['episode_decisions']:
        lines.append(f"- **{decision['id']}** ({decision['status']}; {decision['resolve_during']}): {decision['decision']}")
    lines += ['', '## Asset requests', '',
              'Production requirements; see assets.yaml for acquired files and review status.', '']
    for asset in script['asset_requests']:
        lines += [f"- **{asset['id']}** ({asset['kind']}): {asset['description']} Fallback: {asset['fallback']}"]
    lines += ['', '## Sentence script', '']
    scene_map = {s['id']: s['description'] for s in script['scenes']}
    last_scene = None
    for index, row in enumerate(script['sentences'], 1):
        if row['scene_id'] != last_scene:
            last_scene = row['scene_id']
            lines += [f"### {last_scene or 'Scene to plan'}", '', scene_map.get(last_scene, ''), '']
        lines += [f"#### {index:02d} · {row['sentence_id']}", '',
                  f"**SV:** {row['sv']}", '', f"**RU:** {row['ru']}", '',
                  f"**Visual:** {row['visual_cue'] or 'To plan.'}", '',
                  f"**Assets:** {', '.join(row['asset_ids']) or 'To plan.'}", '',
                  f"**Highlights:** {', '.join(row['text_highlights']) or 'None.'}", '',
                  f"**Pause after:** {row['pause_after_seconds']} seconds (planned).", '']
        for note in row['pronunciation_notes']:
            lines += [f'**Pronunciation:** {note}', '']
        if row['speech_override']:
            override = row['speech_override']
            lines += [f"**Proposed TTS input ({override['review_status']}):** {override['text']}", '',
                      f"**Reason:** {override['reason']}", '']
        if row['display_segments']:
            for segment in row['display_segments']:
                lines += [f"- SV: {segment['sv']} / RU: {segment['ru']}"]
            lines.append('')
    lines += ['## Source credits', '',
              'Exact passage provenance and publisher notices: [sources.yaml](sources.yaml).', '']
    for item in source_snapshot(context)['sources']:
        source, credit = item['source'], item['attribution']
        lines += [f"- [{source['title']}]({source['source_url']}): {credit['credit']}. {credit['license']}."]
    lines += ['', 'Swedish wording and existing Russian translations are preserved. Presentation,',
              'visual cues, and proposed speech-only expansions are added for this video.', '']
    return '\n'.join(lines)


def initialize(context, directory):
    """Create a new episode without overwriting an existing editorial workspace."""
    require(not directory.exists(), f'Episode already exists: {directory}; refusing overwrite')
    script = scaffold(context)
    validate(script, context)
    snapshot = source_snapshot(context)
    brief = read(context['root'] / 'studio/templates/brief.yaml')
    for key in ('section_id', 'chapter_id', 'title_sv', 'title_ru', 'source_path', 'translation_path'):
        brief[key] = script[key]
    brief['production_status'] = 'script_draft'
    brief['issues'] = ['Script requires editorial completion and user review.']
    review = (context['root'] / 'studio/templates/review.md').read_text(encoding='utf-8')
    review = review.replace('<existing-section-id>', script['section_id'])
    directory.mkdir(parents=True)
    write(directory / 'script.yaml', script)
    write(directory / 'brief.yaml', brief)
    write(directory / 'sources.yaml', snapshot)
    (directory / 'review.md').write_text(review, encoding='utf-8')
    (directory / 'SCRIPT.md').write_text(review_markdown(script, context), encoding='utf-8')


def main():
    """Run a deliberately small script-authoring CLI; never create media or commit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('init', 'validate', 'review'))
    parser.add_argument('section_id')
    parser.add_argument('--ready', action='store_true', help='Require a complete editorial plan')
    args = parser.parse_args()
    try:
        context = load_context(args.section_id)
        directory = ROOT / 'studio/episodes' / args.section_id
        if args.command == 'init':
            initialize(context, directory)
            print(f'Created {directory.relative_to(ROOT)}; update the inventory to script_draft.')
            return
        script = read(directory / 'script.yaml')
        validate(script, context, args.ready)
        require(read(directory / 'sources.yaml') == source_snapshot(context),
                'Stale source-credit snapshot; review changed provenance before updating it')
        rendered = review_markdown(script, context)
        if args.command == 'review':
            (directory / 'SCRIPT.md').write_text(rendered, encoding='utf-8')
            print('Updated SCRIPT.md from script.yaml.')
        else:
            require((directory / 'SCRIPT.md').read_text(encoding='utf-8') == rendered,
                    'SCRIPT.md is stale; run the review command')
            print(f"PASS: {len(script['sentences'])} sentences; source, translations, reviews, "
                  'credits, references, and readable script match. User approval is separate.')
    except (ValueError, KeyError, TypeError, FileNotFoundError) as error:
        parser.exit(1, f'ERROR: {error}\n')


if __name__ == '__main__':
    main()
