"""Remove an episode-specific aside from shared current attribution metadata."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[3]
ASIDE = 'One complete legal-protection sentence selected from interview coaching.'
PATTERN = re.compile(r'\s+' + r'\s+'.join(map(re.escape, ASIDE.split())))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    archive = ROOT / 'studio/production/remaining/source-note-originals'
    assert not archive.exists(), 'One bounded metadata correction only.'
    archive.mkdir()
    candidates = [ROOT / 'data/homebrew/metadata/attribution.yaml']
    candidates += sorted((ROOT / 'studio/episodes').glob('*/sources.yaml'))
    candidates += sorted((ROOT / 'studio/episodes').glob('*/CREDITS.md'))
    candidates += sorted((ROOT / 'videos/homebrew').glob('*.CREDITS.md'))
    protected = sorted((ROOT / 'studio/episodes').glob('*/script.yaml'))
    protected += sorted((ROOT / 'studio/episodes').glob('*/assets.yaml'))
    fingerprints = {str(p.relative_to(ROOT)): digest(p) for p in protected}
    videos = {str(p.relative_to(ROOT)): [p.stat().st_size, p.stat().st_mtime_ns]
              for p in (ROOT / 'videos/homebrew').glob('*.mp4')}
    changes = []
    for path in candidates:
        original = path.read_text()
        updated, count = PATTERN.subn('', original)
        if not count:
            continue
        if path.suffix == '.yaml':
            before = yaml.safe_load(original)
            expected = deepcopy(before)
            if path.name == 'attribution.yaml':
                records = [expected['sources']['infofinland']]
            else:
                records = [r['attribution'] for r in expected['sources']]
            for record in records:
                record['changes'] = record.get('changes', '').replace(' ' + ASIDE, '')
            assert yaml.safe_load(updated) == expected, str(path)
        relative = path.relative_to(ROOT)
        backup = archive / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(path.read_bytes())
        old_hash = digest(path)
        path.write_text(updated)
        changes.append(dict(path=str(relative), removed_occurrences=count,
                            before_sha256=old_hash, after_sha256=digest(path)))
    assert all(digest(ROOT / p) == value for p, value in fingerprints.items())
    assert all([(ROOT / p).stat().st_size, (ROOT / p).stat().st_mtime_ns] == value
               for p, value in videos.items())
    report = dict(updated_utc=datetime.now(timezone.utc).isoformat(),
                  correction='Remove irrelevant episode-specific aside from shared InfoFinland preparation note.',
                  changes=changes, protected_script_asset_sha256=fingerprints,
                  existing_mp4_size_mtime_unchanged=videos,
                  scope='Only listed current attribution/source/credit files written; historical revisions preserved. No media writes.',
                  validation='Parsed YAML differs only in attribution.changes; all existing scripts/assets fingerprints and MP4 size/mtime unchanged.')
    (ROOT / 'studio/production/remaining/source-note-correction.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Corrected', len(changes), 'metadata/credit files;', len(videos), 'existing MP4 files unchanged.')


if __name__ == '__main__':
    main()
