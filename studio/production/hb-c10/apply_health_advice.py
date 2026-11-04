"""Adopt source-validated advisory plans into producer-owned ready scripts.

This prepares editorial intent only. It does not claim acquired images,rendered
art,checked narration or accepted exports. Final producer visual checks remain.
"""
from pathlib import Path
import sys
import json
import hashlib
import yaml
from plan_health_episodes import author
R = Path(__file__).resolve().parents[3]
SID = sys.argv[1]
E = R / 'studio/episodes' / SID
A = R / 'studio/production/health-plans'
advice_path = A / (SID + '.json')
plans = json.loads(advice_path.read_text())
handoff_path = A / (SID + '-handoff.json')
if handoff_path.exists():
    handoff = json.loads(handoff_path.read_text())
else:
    bundle = json.loads((A / 'chapter09a-handoff.json').read_text())
    handoff = next(h for h in bundle['episodes'] if h['section_id'] == SID)
    handoff['pairs_read'] = handoff['source_pairs_read']
original_bytes = (E / 'script.yaml').read_bytes()
original = yaml.safe_load(original_bytes)
assert hashlib.sha256(original_bytes).hexdigest() == handoff['source_script_sha256'], 'Review changed producer script before adopting advice'
if 'source_section_sha256' in handoff:
    assert original['source_section_sha256'] == handoff['source_section_sha256']
if 'translation_file_sha256' in handoff:
    assert original['translation_file_sha256'] == handoff['translation_file_sha256']
assert len(plans) == len(original['sentences']) == handoff['pairs_read']
rows = {r['sentence_id']: r for r in original['sentences']}
requests = []
for i,(p,row) in enumerate(zip(plans,original['sentences'])):
    assert p['source_sentence_ids'][0] == row['sentence_id'], (i,p['source_sentence_ids'],row['sentence_id'])
    assert all(reference in rows for reference in p['source_sentence_ids']), p['source_sentence_ids']
    source = ' '.join(rows[s]['sv'] for s in p['source_sentence_ids'])
    for node in p.get('nodes',[]):
        assert node['label'] in source, (i,node['label'])
    for condition in p.get('conditions',[]):
        assert condition['label'] in source, (i,condition['label'])
    if 'source_text' in p:
        assert p['source_text'] == row['sv']
        assert p['reviewed_translation'] == row['ru']
    preferred = 'photograph' if p.get('photo_request') else p['visual_type']
    subject = p.get('photo_request',{}).get('subject','')
    request = p['description'] + ' Required source logic: ' + p['required_logic']
    request += ' Complete source relationship to illustrate: ' + row['sv']
    request += ' Preferred objects: ' + '; '.join(n['icon'] + ' (' + n['label'] + ')' for n in p.get('nodes',[])) + '.'
    if subject:request += ' Actual-picture research request: ' + subject
    title = ' · '.join(n['label'] for n in p.get('nodes',[])[:2])
    requests.append((title,preferred,request))
# Existing helper retains every exact Swedish/Russian body string and source order.
author(SID,requests)
current = yaml.safe_load((E / 'script.yaml').read_text())
assert [(r['sentence_id'],r['sv'],r['ru']) for r in current['sentences']] == [(r['sentence_id'],r['sv'],r['ru']) for r in original['sentences']]
assert current['render']['background_style']['resampling'] == 'bilinear'
current['advisory_plan'] = dict(path=str(advice_path.relative_to(R)),sha256=hashlib.sha256(advice_path.read_bytes()).hexdigest(),
                                all_pairs_read_by_adviser=True,producer_assets_pending=True)
selection_path = E / 'music-selection.json'
if selection_path.exists():
    selection = json.loads(selection_path.read_text())
else:
    reservation = json.loads((R / 'studio/production/remaining/media-reservations.json').read_text())[SID]
    track = next(t for t in json.loads(Path('/tmp/c07-employment-music-catalogue.json').read_text()) if t.get('isrc') == reservation['music_isrc'])
    selection = dict(selected_catalogue_record=track)
for decision in current['episode_decisions']:
    if decision['id'] == 'music':
        track = selection['selected_catalogue_record']
        decision['decision'] = f"Use centrally reserved {track['title']} ({track['isrc']}) by Kevin MacLeod under CC BY4.0; ducked with the accepted +2dB bed adjustment and smooth crossfade only if needed. Catalogue rationale is retained in music-selection.json; complete-video listening pending."
(E / 'script.yaml').write_text(yaml.safe_dump(current,allow_unicode=True,sort_keys=False,width=100))
(E / 'advisory-picture-plan.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
brief = yaml.safe_load((E / 'brief.yaml').read_text())
brief.update(production_status='script_ready',issues=['Detailed source-validated advisory intent adopted by producer; actual source photographs,individual visual compositions,narration,assets and complete export checks pending.'])
(E / 'brief.yaml').write_text(yaml.safe_dump(brief,allow_unicode=True,sort_keys=False,width=100))
print(SID,'adopted',len(plans),'source-checked advisory rows; exact body/order preserved; bilinear sampler explicit.')
