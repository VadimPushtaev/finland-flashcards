"""Select the single improved count comparison while preserving every original."""
from pathlib import Path
import hashlib
import json
import re
import shutil

import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EPISODE = ROOT / 'studio/episodes/hb-c09-foraldraledighet'
MEDIA = ROOT / 'studio/media/hb-c09-foraldraledighet'
assert json.loads((HERE / 'durable-tts-progress.json').read_text())['status'] == 'paused_at_checkpoint'
assert json.loads((HERE / 'parental-count-host-state.json').read_text())['status'] == 'finished'
script_path = EPISODE / 'script.yaml'
script = yaml.safe_load(script_path.read_text())
original_display = [(r['sentence_id'], r['sv'], r['ru']) for r in script['sentences']]
proposals = json.loads((EPISODE / 'count-retake-proposal.json').read_text())
folder = MEDIA / 'retake-expanded-counts'
new_metrics = {row['sentence_id']: row for row in json.loads((folder / 'metrics.json').read_text())}
new_asr = {Path(row['file']).stem: row for row in json.loads((folder / 'asr.json').read_text())}
metrics_path = MEDIA / 'narration/metrics.json'
asr_path = MEDIA / 'narration/asr.json'
metrics = json.loads(metrics_path.read_text())
asr_records = json.loads(asr_path.read_text())
asr_indices = {Path(row['file']).stem: index for index, row in enumerate(asr_records)}
backup = MEDIA / 'narration-before-expanded-counts'
backup.mkdir(exist_ok=True)
assert not (backup / 'metrics.json').exists(), 'Adoption already performed; inspect existing history.'
shutil.copy2(metrics_path, backup / 'metrics.json')
shutil.copy2(asr_path, backup / 'asr.json')
shutil.copy2(script_path, backup / 'script.yaml')
history = []
for proposal in proposals:
    index = proposal['index']
    row = script['sentences'][index]
    sid = row['sentence_id']
    assert row['sv'] == proposal['source_text'] and not row.get('speech_override')
    old = metrics[index]
    selected = dict(new_metrics[sid])
    transcript = dict(new_asr[sid])
    expected_numbers = re.findall(r'\d+', proposal['numeral'])
    observed_numbers = re.findall(r'\d+', transcript['asr_text'])
    assert all(value in observed_numbers for value in expected_numbers), transcript
    original_file = ROOT / old['path']
    new_file = ROOT / selected['path']
    original_sha = hashlib.sha256(original_file.read_bytes()).hexdigest()
    comparison_sha = hashlib.sha256(new_file.read_bytes()).hexdigest()
    assert original_sha == old['sha256']
    assert comparison_sha == transcript['sha256'] == selected['sha256']
    original_backup = backup / original_file.name
    shutil.copy2(original_file, original_backup)
    assert hashlib.sha256(original_backup.read_bytes()).hexdigest() == original_sha
    previous_asr = asr_records[asr_indices[sid]]
    history.append(dict(
        sentence_id=sid, reason=proposal['reason'],
        original=dict(metrics=old, asr=previous_asr,
                      preserved_path=str(original_backup.relative_to(ROOT)), sha256=original_sha),
        retake=dict(metrics=dict(selected), asr=dict(transcript), sha256=comparison_sha),
        selection='Adopt the single bounded expanded-count take: every expected count/range number is now present in local ASR. Displayed Swedish/Russian source wording remains unchanged.',
        listening_status='Automated count/range diagnostic improved; whole-video pronunciation and user listening remain pending.',
    ))
    shutil.copy2(new_file, original_file)
    selected['path'] = str(original_file.relative_to(ROOT))
    selected['retained_comparison_metrics'] = str((folder / 'metrics.json').relative_to(ROOT))
    metrics[index] = selected
    transcript['file'] = selected['path']
    asr_records[asr_indices[sid]] = transcript
    row['speech_override'] = dict(text=proposal['text'], reason=proposal['reason'], review_status='pending')
assert original_display == [(r['sentence_id'], r['sv'], r['ru']) for r in script['sentences']]
for path, value in [(metrics_path, metrics), (asr_path, asr_records),
                    (EPISODE / 'retake-history.json', history)]:
    temporary = path.with_suffix('.writing')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)
script_path.write_text(yaml.safe_dump(script, allow_unicode=True, sort_keys=False, width=100))
print('Adopted four improved numeral comparisons; all originals and display wording retained.')
