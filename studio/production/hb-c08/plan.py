"""Apply episode-specific visual plans while preserving exact source/translation records."""
from pathlib import Path
import copy,json,sys,yaml
ROOT=Path(__file__).resolve().parents[3];PALETTE=dict(background='#193b40',text='#faf3e8',secondary='#c0dce0',highlight='#e8c081',separator='#3f6d73')
BASE=yaml.safe_load((ROOT/'studio/episodes/hb-c07-ekonomi/script.yaml').read_text())
# Each item is a source-based composition, never a replacement narration.
FORSKOLA=[
('path','sex år','child','förskoleundervisning','school'),
('garden','växa','plant','utvecklas och lära sig','book'),
('year','ett år','calendar','innan skolan börjar','school'),
('obligation','delta','child','målen','target'),
('conversation','förskoleundervisningen','teacher','förskola','speech'),
('qualification','lärarna','teacher','utbildning','diploma'),
('team','lärare','teacher','barnskötare eller assistent','adult'),
('meeting','förskolepersonalen','teacher','föräldrarna och vårdnadshavarna','family'),
('meal','avgiftsfri','coins','varm måltid','meal'),
('clock','fyra timmar','clock','per dag','sun'),
('materials','läromedlen','pencils','avgiftsfria','coins'),
('day','förskoleundervisningen','school','på eftermiddagen','play'),
('halfday','normal klientavgift','coins','halva dagen','clock'),
('tools','färdigheter','puzzle','lära sig nya saker','book'),
('social','sociala färdigheter','children','självkänsla','child'),
('language','positiva upplevelser','book','språkliga utveckling','speech'),
('discovery','leka','play','utforska tillsammans','magnify'),
('growth','barnets utvecklingsnivå','child','lärarna','teacher'),
('support','svårigheter','puzzle','förskoleundervisningen','teacher'),
('bridge','skolgång','school','stödjas ända från början','hands'),
('calendarpath','ett års tid','calendar','innan läroplikten börjar','school'),
('birthday','sex år','child','förskoleundervisningen','book'),
('municipality','kommunerna','town','kostnadsfri','coins'),
('qualification','högutbildade pedagoger','teacher','förskoleundervisning','book'),
('week','fyra timmar om dagen','clock','måndag till fredag','calendar'),
('day','förskoleundervisning','school','småbarnspedagogik','play')]

HUX=[('tools','studiefärdigheter','book','studiespråket','speech'),('path','höja vitsord','diploma','utbildningsplats','school'),('path','gymnasieutbildning','school','yrkesutbildning','pencils'),('year','högst ett år','calendar','olika utbildningar','book'),('path','yrkesutbildning','pencils','gymnasium','school'),('team','unga','child','vuxna','adult'),('materials','studiestöd','coins','FPA','town'),('obligation','gemensamma ansökan','book','kontinuerliga ansökan','calendar')]

def apply(sid):
 ep=ROOT/'studio/episodes'/sid;d=yaml.safe_load((ep/'script.yaml').read_text())
 if d['episode_decisions']:return
 d['episode_decisions']=copy.deepcopy(BASE['episode_decisions'])
 for x in d['episode_decisions']:
  x['status']='proposed'
  if x['id']=='text_and_layout':x['decision']='1920x1080 24fps, Chapter 8 teal palette '+str(PALETTE)+'. Liberation Sans Bold48/Regular40 with right bilingual panel and fixed left foreground.'
  if x['id']=='foreground_selection':x['decision']='A distinct relevant source-based illustration for nearly every sentence slide, supplemented by verified photographs where they clarify actual institutions or places. Distinct semantic compositions show only the source statements. Aim at least90% measured body picture coverage and report unique-picture ratio.'
  if x['id']=='visual_motion':x['decision']='Unique centrally reserved topic-related photograph, darkened42%, blurred2.5px; continuous full-timeline140second pan/zoom cycles,15%relative zoom, no sentence resets.'
  if x['id']=='voice_selection':x['decision']='Local Supertonic3/F1 Swedish,32steps,speed0.95,seed42,44100HzmonoPCM16,2ONNXthreads. Whole-video listening and user acceptance pending.'
  if x['id']=='music_selection':x['decision']='Unique centrally reserved gentle KevinMacLeod instrumental, CC BY4.0, accepted+2dB mix adjustment, ducked under speech;4sloopcrossfades,2s/3sfades.'
  if x['id']=='story_structure':x['decision']='Consecutive original source paragraphs/list items define topic scenes; exact wording and stored order are retained. Sentence illustrations follow the individual source claim.'
 d['scenes']=[];d['asset_requests']=[copy.deepcopy(a) for a in BASE['asset_requests'] if a['id'] in ('episode_background','music_bed','narration')];specs={};seen=[]
 for i,r in enumerate(d['sentences']):
  unit=r['sentence_id'].rsplit('-s',1)[0]
  if unit not in seen:
   seen.append(unit);d['scenes'].append(dict(id=unit,description=r['sv']))
  key='picture-'+str(i+1).zfill(3)
  spec=FORSKOLA[i] if sid=='hb-c08-forskola' else HUX[i] if sid=='hb-c08-hux' else None
  r.update(scene_id=unit,asset_ids=['episode_background',key],text_highlights=[],pause_after_seconds=2.5 if len(r['sv'])+len(r['ru'])>330 else 1.5,render_caption=False,render_image=f'studio/media/{sid}/pictures/{key}.png',visual_cue='Distinct source-based foreground illustration: '+(' / '.join(spec) if spec else r['sv']),pronunciation_notes=['Review compounds, Finnish terms and source numerals in whole-video listening; ASR is diagnostic only.'])
  if len(r['sv'])+len(r['ru'])>330:r['text_style']={'sv_size':44,'ru_size':36}
  if spec:
   spec=list(spec)
   for k in (1,3):
    at=r['sv'].lower().find(spec[k].lower())
    if at<0:raise ValueError((sid,i,spec[k]))
    spec[k]=r['sv'][at:at+len(spec[k])]
  if spec:specs[key]=dict(composition=spec[0],nodes=[dict(label=spec[1],icon=spec[2]),dict(label=spec[3],icon=spec[4])],source_sentence_ids=[r['sentence_id']])
  d['asset_requests'].append(dict(id=key,kind='foreground',description=r['visual_cue'],fallback='Use another accurate source-based pictorial composition or verified relevant photograph; record a justified omission if an honest illustration is infeasible.'))
 for a,b in zip(d['sentences'],d['sentences'][1:]):
  if a['scene_id']!=b['scene_id']:a['pause_after_seconds']=max(a['pause_after_seconds'],2.2)
 d['render']=copy.deepcopy(BASE['render']);d['render']['palette']=PALETTE;d['render']['background_image']=f'studio/media/{sid}/sources/background.jpg';d['render']['music_path']=f'studio/media/{sid}/sources/music-bed.flac';d['render'].pop('background_identity',None);d['render']['background_style'].pop('motion_cycles',None)
 sources=yaml.safe_load((ep/'sources.yaml').read_text())['sources'];d['render']['credits']=[dict(heading='Källor · Источники',paragraphs=['Svensk källtext med granskad rysk översättning.',*list(dict.fromkeys(s['attribution']['title'] for s in sources)),*list(dict.fromkeys(s['attribution']['credit'] for s in sources)),'Fullständiga källor och villkor i medföljande CREDITS.md.']),dict(heading='Bild, musik & röst · Изображения, музыка и голос',paragraphs=['Original saklig illustrationsgrafik: Homebrew video studio.','Bildernas identitet och återanvändningsvillkor i CREDITS.md.','Musik: Kevin MacLeod · CC BY4.0.','Svensk lokal berättarröst: Supertonic3 · F1.'])]
 d['render']['adaptation_notes']=['Exact source Swedish and reviewed Russian retained in source order.','Original foreground illustrations depict source-stated objects and relationships; symbolic scenes are not documentary photographs.','Unique photographic background cropped,darkened,blurred and animated continuously.','Music faded,ducked,+2dBadjusted and repeated with4second equal-power crossfades when needed.']
 (ep/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(ep/'picture-plan.json').write_text(json.dumps(specs,ensure_ascii=False,indent=2)+'\n');b=yaml.safe_load((ep/'brief.yaml').read_text());b['production_status']='script_ready';b['issues']=['Assets not yet prepared; whole-video listening and user acceptance pending.'];(ep/'brief.yaml').write_text(yaml.safe_dump(b,allow_unicode=True,sort_keys=False));print(sid,len(d['sentences']),flush=True)
if __name__=='__main__':
 for s in sys.argv[1:]:apply(s)
