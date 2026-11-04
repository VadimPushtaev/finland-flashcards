"""Source-specific editorial picture requests for the welfare episode."""
from pathlib import Path
import yaml,json
ROOT=Path(__file__).resolve().parents[3];EP=ROOT/'studio/episodes/hb-c10-valfard';d=yaml.safe_load((EP/'script.yaml').read_text())
subjects=[
('Dignity and residents','A diverse group of residents at eye level, avoiding claims that photographed people receive benefits.'),
('Tax-funded services','Photographic montage of healthcare, school, childcare, library and sport; verified identities.'),
('Accessible services','An actual public library reading room, illustrative of source low-cost services, no invented prices.'),
('Support in difficult circumstances','Original pictorial diagram showing illness, unemployment and financial support without fixed amounts.'),
('Service funding','Schematic tax-funding arrow into public healthcare and education, no numerical tax claims.'),
('Taxation comparison','Tax receipt and public-services icons; no fabricated country comparison statistics.'),
('Individuals and companies','Distinct visible individual worker and company office connected to taxes.'),
('Attitudes to taxes','Research document and public-service illustration; no invented poll percentages.'),
('Public debate','Actual Finnish parliamentary plenary chamber photograph, illustrative, not a particular vote.'),
('Funding choices','Original balance between service provision and tax funding, no implied correct tax rate.'),
('Political opinions','Distinct party discussion/separate speech bubbles representing differing opinions, no party endorsement.'),
('Free discussion','Licensed community public-discussion photograph with accurate context.'),
('Benefit recipients','Original pictorial constellation: families, unemployed people, students, disability, long-term illness and rehabilitation.'),
('Housing support','Photograph of accurately identified Finnish residential housing; no statement that residents receive benefits.'),
('FPA card','Actual verified anonymized FPA card photograph; otherwise schematic card explicitly labeled illustrative.'),
('Pharmacy reimbursement','Licensed actual Finnish pharmacy exterior/interior photograph, not an assertion that particular items are covered.'),
('Own contribution','Receipt schematic with reimbursement and own-contribution segments without amounts.'),
('Benefits and law','Actual Finnish law books photograph or original lawbook illustration, no invented statute number.'),
('Application examination','Original paper-application to FPA-review process, no automatic approval outcome.'),
('Residence and work','Distinct home and workplace photographs linked as source-stated assessment factors.'),
('Individual decision','Individual applicant with separate case file, without identifying real recipients.'),
('Different circumstances','Distinct households with different needs; no ranking or demographic assumptions.'),
('Different benefit amounts','Separate unnumbered support envelopes, no invented benefit amounts.'),
('Your circumstances','Individual confidential consultation photograph or original one-to-one consultation illustration.'),
('Permanent residence','Actual Finnish residential street photograph, no legal boundary map.'),
('Residence in law','Law book beside home icon, source concept only.'),
('Working in Finland','Licensed photograph of an actual Finnish workplace, no asserted personal entitlement.'),
('Moving and assessment','Original luggage/home to FPA-assessment diagram, not guaranteed residence status.'),
('Possible residence situations','Schematic introductory checklist to the following source situations, without independent new conditions.'),
('Return migration','Luggage and return arrow to Finland; no invented border route.'),
('Permanent employment','Actual blank employment contract photograph or original clearly schematic contract.'),
('Close family relation','Licensed family photograph used illustratively without asserting marriage or immigration status of those shown.'),
('Residence permit validity','Clearly schematic permit and unnumbered calendar, no counterfeit document or real identity.'),
('Overall assessment','Original assessment table bringing several case factors together, no scoring formula.'),
('Residence decision','House and two labeled assessment outcomes without asserting every outcome is automatic.'),
('Nonpermanent residence','Travel suitcase beside a muted benefit-envelope icon; retain source usually qualification in main text.'),
('Work-based benefits','Distinct workplace photograph, qualified possible rights in exact text.'),
('Studies and origin','Study notebook with unnumbered timeline and place-origin symbol; no invented duration.'),
('Home-country social security','Accurate separate EU, EEA/Swiss/UK reference symbols or source diagram; avoid incorrect union membership maps.'),
('Other-country studies','Source-stated two-year study timeline with qualified possible access; no extra benefit categories.'),
('Residence history','Source-based home/residence timeline without invented periods.'),
('EU insurance periods','Original accumulation diagram of two unlabelled EU-country insurance periods; no invented durations.'),
('International affairs centre','Licensed photograph of actual FPA premises/contact service or source-based contact illustration without fabricated phone numbers.')]
assert len(subjects)==len(d['sentences'])
breaks=[0,4,8,12,14,17,21,24,27,29,32,35,37,40,42]
d['scenes']=[dict(id=f'scene-{j+1}',description=subjects[i][0]) for j,i in enumerate(breaks)]
d['episode_decisions']=[dict(id=k,decision=v,status='proposed',resolve_during=s) for k,v,s in [('opening','Exact unspoken bilingual source heading3seconds, calm continuous background motion.','script'),('fidelity','Every exact Swedish body sentence/list fragment once in stored order; reviewed Russian retained.','script'),('visuals','A separately planned relevant foreground picture for every sentence, photographs for concrete people/places/objects and useful source-specific diagrams for eligibility relationships. No invented benefit amounts, statistics, boundaries or legal guarantees. Picture acquisition is underway; truthful fallbacks documented per request.','script'),('voice','Local Swedish Supertonic3 F1,steps32,speed.95,NumPyseed42,44100HzmonoPCM16; pronunciation approval pending complete-video listening.','script'),('background','Distinct source-identified Vuosaari health and welfare centre photograph, Chapter10 ocean palette;42%darken,2.5pxblur,15%relativezoom and continuous140second global cyclicpan.','assets'),('music','Distinct reserved Healing by KevinMacLeod,ISRC USUAN1200048,CCBY4.0;+2dB music adjustment, speech ducking and fades,4secondcrossfades if needed.','assets'),('pace','Measured full speech, .25second textlead,1.5second hold and2.2at topic boundaries,2.5forlongtext; source wording stays exact.','script'),('closing','Readable15secondcreditcards with fullsource/media/license sidecar.','script')]]
d['asset_requests']=[dict(id='episode_background',kind='background',description='File:Vuosaaren terveys- ja hyvinvointikeskus - Helsinki - 1.jpg; actual verified centre housing healthcare/family/Kela services.',fallback='Another distinct source-verified licensed Finnish welfare-centre photograph.'),dict(id='music_bed',kind='music',description='Reserved Healing, KevinMacLeod,USUAN1200048.',fallback='Another centrally reserved distinct calm instrumental track with verified reuse terms.'),dict(id='narration',kind='narration',description='Exact local Swedish F1sentenceclips.',fallback='Targeted meaning-preserving diagnosticledretake preserving retained originals.')]+[dict(id=f'picture-{i+1:02}',kind='foreground',description=desc,fallback='Source-specific original pictorial explanation of this sentence, without new factual labels; document genuine shortfall if a useful image cannot be obtained.') for i,(title,desc) in enumerate(subjects)]
for i,r in enumerate(d['sentences']):
    j=max(j for j,k in enumerate(breaks) if k<=i);r.update(scene_id=f'scene-{j+1}',asset_ids=['episode_background',f'picture-{i+1:02}'],visual_cue=subjects[i][1],pause_after_seconds=2.5 if len(r['sv'])>190 else 2.2 if i+1 in breaks or i==42 else 1.5,render_caption=False,pronunciation_notes=['FPA,EU,EES,Schweiz,Storbritannien and numerical study durations need whole-video listening; ASR remains diagnostic.'])
    if 'FPA' in r['sv']:r['speech_override']=dict(text=r['sv'].replace('FPA:s','F P A:s').replace('FPA','F P A'),reason='Speak Swedish initial letters distinctly; exact display remains unchanged.',review_status='pending')
p=ROOT/'studio/episodes/hb-c10-utkomststod/script.yaml';base=yaml.safe_load(p.read_text())['render'];import copy;d['render']=copy.deepcopy(base);d['render']['background_image']='studio/media/hb-c10-valfard/sources/background.jpg';d['render']['music_path']='studio/media/hb-c10-valfard/sources/music-bed.flac';d['render']['credits']=d['render']['credits'][:2];d['render']['credits'][1]['paragraphs']=['Distinct welfare-centre photograph; license attribution resolved during assets.','Healing — KevinMacLeod (incompetech.com)','Musik:CCBY4.0; local narration Supertonic3F1.'];d['render'].pop('background_identity',None)
(EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(EP/'picture-plan.json').write_text(json.dumps([dict(sentence_id=r['sentence_id'],title=t,request=desc) for r,(t,desc) in zip(d['sentences'],subjects)],ensure_ascii=False,indent=2)+'\n')
