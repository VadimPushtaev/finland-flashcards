"""Refresh owned production counts from retained canonical manifests."""
from pathlib import Path
import datetime
import json
import yaml

ROOT = Path(__file__).resolve().parents[3]
PATH = Path(__file__).with_name('progress.json')
report = json.loads(PATH.read_text())
loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
for row in report['episodes']:
    section = row['section_id']
    episode = ROOT / 'studio/episodes' / section
    narration = ROOT / 'studio/media' / section / 'narration'
    for name, key in [('metrics.json', 'selected_tts'), ('asr.json', 'asr')]:
        path = narration / name
        row[key] = len(json.loads(path.read_text())) if path.exists() else 0
    row['producer_actual_export_review'] = (episode / 'producer-export-review.json').exists()
    row['preflight_review'] = (episode / 'producer-preflight-review.json').exists()
    row['brief_status'] = yaml.load((episode / 'brief.yaml').read_text(), Loader=loader)['production_status']
report['updated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
report['selected_total'] = sum(row['selected_tts'] for row in report['episodes'])
report['asr_total'] = sum(row['asr'] for row in report['episodes'])
report['fully_export_reviewed'] = sum(row['producer_actual_export_review'] for row in report['episodes'])
report['source_pairs_total'] = sum(row['source_pairs'] for row in report['episodes'])
temporary = PATH.with_suffix('.tmp')
temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
temporary.replace(PATH)
print({key: value for key, value in report.items() if key != 'episodes'})
