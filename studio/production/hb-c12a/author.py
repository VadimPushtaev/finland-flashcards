"""Apply source-specific plans to the exclusively owned first ten Chapter 12 episodes."""
from pathlib import Path
import copy,json,sys,yaml
ROOT=Path(__file__).resolve().parents[3];PALETTE=dict(background='#352e49',text='#faf3e8',secondary='#d7cce7',highlight='#e2c58b',separator='#685881');SLUGS=['integration','tjanster','sprak','tolkning','myndigheter','egna-arenden','personuppgifter','hemkommun','e-tjanster','norden-eu'];BASE=yaml.safe_load((ROOT/'studio/episodes/hb-c08-forskola/script.yaml').read_text())
def author(slug,plans):
 sid='hb-c12-'+slug;ep=ROOT/'studio/episodes'/sid;d=yaml.safe_load((ep/'script.yaml').read_text());assert len(plans)==len(d['sentences']),(sid,len(plans),len(d['sentences']));d['episode_decisions']=copy.deepcopy(BASE['episode_decisions'])
 for x in d['episode_decisions']:
  x['status']='proposed'
  if x['id']=='text_and_layout':x['decision']='1920x1080 at24fps; Chapter12 violet palette '+str(PALETTE)+'. Liberation Sans Bold48/Regular40 with a fixed right bilingual panel and relevant left foreground pictures.'
  if x['id']=='story_structure':x['decision']='Exact source paragraphs/list items define consecutive topic scenes. Sentence-specific objects and source relationships are planned individually; no added spoken transitions or current-law updates.'
  if x['id']=='foreground_selection':x['decision']='Distinct relevant picture for nearly every body sentence slide: actual places/objects where identity and license are verified, plus original pictorial diagrams for source-stated eligibility, administrative steps and personal-data protections. Avoid real personal identifiers and invented legal rules.'
  if x['id']=='visual_motion':x['decision']='Distinct centrally reserved topic photograph, darkened42%, blurred2.5px, continuous diagonal pan and15%relative zoom with140second cycles. Final identity and measured cycle count are recorded during assets.'
  if x['id']=='music_selection':x['decision']='Distinct centrally reserved instrumental KevinMacLeod track, verified composer title/ISRC and CC BY4.0. Accepted+2dB adjustment, narration ducking,2second/3second fades,4second crossfades only when the same track needs repeating.'
  if x['id']=='voice_selection':x['decision']='Local Swedish Supertonic3/F1,32steps,speed0.95,NumPyseed42 per invocation,44100HzmonoPCM16; initial2ONNXthreads shared with Chapter8 allocation. Exact synthesis inputs and actual seed scope are retained; whole-video listening remains pending.'
 d['scenes']=[];d['asset_requests']=[copy.deepcopy(a) for a in BASE['asset_requests'] if a['id'] in ('episode_background','music_bed','narration')];specs={};units=[]
 for i,(r,p) in enumerate(zip(d['sentences'],plans)):
  p=list(p);unit=r['sentence_id'].rsplit('-s',1)[0]
  if unit not in units:units.append(unit);d['scenes'].append(dict(id=unit,description=r['sv']))
  for k in(1,3):
   at=r['sv'].casefold().find(p[k].casefold())
   if at<0:raise ValueError((sid,i,p[k]))
   p[k]=r['sv'][at:at+len(p[k])]
  key='picture-'+str(i+1).zfill(3);specs[key]=dict(composition=p[0],nodes=[dict(label=p[1],icon=p[2]),dict(label=p[3],icon=p[4])],source_sentence_ids=[r['sentence_id']]);r.update(scene_id=unit,asset_ids=['episode_background',key],text_highlights=[],pause_after_seconds=2.5 if len(r['sv'])+len(r['ru'])>330 else 1.5,render_caption=False,render_image=f'studio/media/{sid}/pictures/{key}.png',visual_cue='Source-specific pictorial composition '+p[0]+': '+p[1]+' / '+p[3]+'. Show only source-stated relations, no fabricated personal data.',pronunciation_notes=['Whole-video listening priorities include Swedish compounds,Finnish agency names,numerals and abbreviations. ASR diagnostics do not establish correct pronunciation.'])
  if len(r['sv'])+len(r['ru'])>330:r['text_style']={'sv_size':44,'ru_size':36}
  d['asset_requests'].append(dict(id=key,kind='foreground',description=r['visual_cue'],fallback='Use another accurate source-based pictorial composition or verified relevant photo; omit honestly and document a genuine shortfall if neither is accurate.'))
 for a,b in zip(d['sentences'],d['sentences'][1:]):
  if a['scene_id']!=b['scene_id']:a['pause_after_seconds']=max(a['pause_after_seconds'],2.2)
 d['render']=copy.deepcopy(BASE['render']);d['render']['palette']=PALETTE;d['render']['background_image']=f'studio/media/{sid}/sources/background.jpg';d['render']['music_path']=f'studio/media/{sid}/sources/music-bed.flac';d['render'].pop('background_identity',None);d['render']['background_style'].pop('motion_cycles',None)
 sources=yaml.safe_load((ep/'sources.yaml').read_text())['sources'];d['render']['credits']=[dict(heading='Källor · Источники',paragraphs=['Svensk källtext med granskad rysk översättning.',*list(dict.fromkeys(s['attribution']['title'] for s in sources)),*list(dict.fromkeys(s['attribution']['credit'] for s in sources)),'Fullständiga källor och villkor i medföljande CREDITS.md.']),dict(heading='Bild, musik & röst · Изображения, музыка и голос',paragraphs=['Verifierade fotografier och original källbaserad illustrationsgrafik.','Varje upphovsperson, källa och licens i CREDITS.md.','Musik: Kevin MacLeod · CC BY4.0.','Svensk lokal berättarröst: Supertonic3 · F1.'])];d['render']['adaptation_notes']=['Exact archived Swedish and reviewed Russian retained in source order; no current-law claims added.','Original foreground illustrations represent source-stated administrative steps and relationships; no real or fabricated personal identifiers.','Distinct background photograph cropped,darkened,blurred and animated continuously; original photo license retained.','Instrumental music faded,ducked,+2dBadjusted and repeated using4second equal-power crossfades when necessary.']
 (ep/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(ep/'picture-plan.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((ep/'brief.yaml').read_text());b['production_status']='script_ready';b['issues']=['Assets and export not yet prepared; whole-video listening and user acceptance pending.'];(ep/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False));print(sid,len(specs),'source-specific planned pictures',flush=True)
if __name__=='__main__':
 from plans import PLANS
 for slug,plans in PLANS.items():author(slug,plans)
