"""Freeze the reviewed disability-services candidate without changing media."""
from pathlib import Path
import hashlib
import json
import yaml

R = Path(__file__).resolve().parents[3]
SID = 'hb-c10-funktionsnedsattning'
E = R / 'studio/episodes' / SID
M = R / 'studio/media' / SID
s = yaml.load((E / 'script.yaml').read_text(), Loader=yaml.CSafeLoader)
m = json.loads((M / 'narration/metrics.json').read_text())
a = {r['file']: r for r in json.loads((M / 'narration/asr.json').read_text())}
assert len(m) == len(a) == len(s['sentences']) == 67
records = []
for i, (x, y) in enumerate(zip(m, s['sentences'])):
    assert x['sentence_id'] == y['sentence_id']
    assert hashlib.sha256((R / x['path']).read_bytes()).hexdigest() == a[x['path']]['sha256']
    records.append(dict(index=i, sentence_id=x['sentence_id'], tts_input=x['text'], asr_text=a[x['path']]['asr_text']))
(E / 'audio-diagnostics.json').write_text(json.dumps(dict(
    section_id=SID, selected_clips=67, current_asr_hashes_checked=67,
    all_transcripts_read=True, asr_key='actual filename, never sorted filename position',
    whole_video_listening=False, records=records,
    diagnostic_indices=[0,1,2,7,8,10,18,20,23,25,28,37,40,43,44,45,47,48,49,50,57,61,63,65],
    priorities=[
        'Compound words funktionshinderservice/färdtjänst and Finnish perhehoito,laitos,työtoiminta,päivätoiminta need whole-video listening.',
        'Index8 diagnostic repeats a short phrase and index44 repeats part of funktionshinderservicen; ASR alone cannot establish an acoustic error or justify repeated synthesis.',
        'Eligibility AND/OR, granted-right condition, card A, under65 and partial reimbursement require listening; matching diagnostic words are not auditory proof.'
    ]), ensure_ascii=False, indent=2) + '\n')
t = json.loads((M / 'render/timeline.json').read_text())
seconds = (t[-1]['start_frame'] + t[-1]['frames']) / 24
frames = sorted((M / 'render').glob('frame-*.png'))
assert len(frames) == 80
v = json.loads((E / 'visible-structure-audit.json').read_text())
assert v['distinct_visible_structures'] == 62
notes = [
    'All67 exact Swedish/current reviewed Russian pairs once in stored source order; source and ready validators passed.',
    'Residence permit AND Finnish home municipality; some chronic-illness services only if daily OR work difficulties DUE illness. Transport inability to use public transport OR outside-help need; assistance DUE disability OR illness.',
    'County pays assistant salary, resident pays own housing costs; free special home support distinct from rent. Wheelchair and guide-dog masters accurately identified, no photographed person assigned diagnosis or benefit status.',
    'Interpreting for hearing OR combined sight/hearing OR speech; municipality education categories distinct from FPA application. Free use IF right granted; no foreign-language translation assumption.',
    'EU card CAN APPLY, permanent disability OR long illness; MANY places AND card shown AND A marking give assistant OR interpreter free entry, not universal free cardholder admission.',
    'Necessary home changes OR fixed aids MAY reimbursement; social worker WITH user assesses. Public ramp photograph not labelled as private-home modification.',
    'Severe disability OR illness AND UNDER65 permits FPA MAY arrange demanding medical rehabilitation and reimburse PART of cost; no new threshold or award guarantee.',
    'Family care outside own home and MAY ALSO own home. Intellectual disability AND continuous care AND neither home NOR service housing works permits institution; no automatic placement.',
    'Day activities severe disability AND cannot participate in work activity; no employment/wage guarantee or pictured participant status.',
    '64 source pictures/67=95.52%; conservative62 visible structures/67=92.54%, honestly grouping useful photo continuations and two similar mechanisms.100percent pictured body planned.'
]
out = dict(section_id=SID, status='assets_ready', planned_seconds=seconds,
    exact_pairs=67, selected_narration_clips=67, current_asr_hashes=67,
    pictured_slides=67, distinct_pictures=64, photographs=19, original_diagrams=45,
    picture_body_fraction=1, distinct_picture_fraction=64/67,
    conservative_visible_structures=62, conservative_visible_fraction=62/67,
    body_fonts='Indices0,8,31,50 at44/36;index1 at40/34;others48/40. Zero-based stored order.',
    planned_visual_inspection=['All19 selected licensed primary photographs viewed; misleading wheelchair icon candidate rejected with raw research preserved.',
        'All80 actual preflight title/body/12credit cards viewed; corrected caption/shape spacing inspected in16 current full-card samples.',
        'Independent C8 all67SVRU/all80 current stills/19primary-photo/10native/12simulated768pixel review passed, no findings; producer simulated640pixel frames01/02/27/39/51/62 inspected; no whole-video/device claim.'],
    source_fidelity_notes=notes, whole_video_listening=False,
    physical_device_playback=False, export=False, user_acceptance=False,
    hashes={n: hashlib.sha256((E/n).read_bytes()).hexdigest() for n in ['script.yaml','assets.yaml','sources.yaml','CREDITS.md']},
    preflight_frames=[dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in frames])
(E/'prerender-handoff.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
b=yaml.safe_load((E/'brief.yaml').read_text())
b.update(production_status='assets_ready',issues=['All67 current WAV/ASR hashes and diagnostic transcripts checked; all80 preflight cards inspected. Full export and listening/user acceptance pending.','Finnish terms, compound words and diagnostic repetitions at8/44 need whole-video listening; no acoustic error claim.'])
(E/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False,width=100))
print(SID,'assets_ready',seconds)
