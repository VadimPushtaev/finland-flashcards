"""Author non-graphic, source-faithful medical care illustrations and script."""
from pathlib import Path
import yaml,json,copy,hashlib,importlib.util,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];SID='hb-c10-konsstympning';EP=ROOT/'studio/episodes'/SID;MEDIA=ROOT/'studio/media'/SID;OUT=MEDIA/'pictures';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('utkomst',ROOT/'studio/production/hb-c10/author_utkomststod.py')
# Importing the author script would rerun another episode; reuse source drawing
# primitives by compiling only the definitions before its explicit specs list.
code=(ROOT/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0];ns={'__file__':str(Path(__file__))};exec(compile(code,'drawing-primitives','exec'),ns)
canvas,label,house,person,coins,paper,arrow=[ns[k] for k in ['canvas','label','house','person','coins','paper','arrow']];FG=ns['FG'];SOFT=ns['SOFT'];GOLD=ns['GOLD'];LINE=ns['LINE'];PANEL=ns['PANEL'];FONT=ns['FONT'];BG=ns['BG']
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def droplet(d,x,y,s=1,fill=SOFT):d.polygon([(x,y-70*s),(x-40*s,y+10*s),(x+40*s,y+10*s)],fill=fill);d.ellipse((x-40*s,y-28*s,x+40*s,y+52*s),fill=fill)
def heart(d,x,y,fill=GOLD):d.ellipse((x-70,y-40,x+2,y+32),fill=fill);d.ellipse((x-2,y-40,x+70,y+32),fill=fill);d.polygon([(x-66,y+10),(x+66,y+10),(x,y+92)],fill=fill)
subjects=[('Hälsoproblem','Non-anatomical schematic of impeded normal fluid flow; no anatomical location or procedural detail invented.'),('Inflammationer','Stethoscope photograph illustrates health problems; no diagnosis of any photographed person.'),('Problem vid sexuellt umgänge','Two fully clothed abstract adult silhouettes separated by a broken connecting line represent difficulty; not an image of an actual survivor.'),('Graviditet och förlossning','Non-graphic schematic pregnancy/maternity care risk context, without numeric risk claims or procedural details.'),('Mental hälsa','Original head/thought-support schematic represents trauma-associated mental-health problems without identifying a person.'),('Två vårdalternativ','Branching diagram names the two procedures from the exact source, without recommending an operation or implying a guarantee.'),('Problem och smärtor','Three source-stated domains represented non-anatomically: urinary flow, menstrual calendar and adult partnership.'),('Poliklinik','Accurately identified healthcare-centre exterior illustrates outpatient care, without alleging a particular operation is offered at that centre.'),('Anatomi och funktion','Original schematic treatment-restoration concept with neutral body-outline/functional connection; no fabricated anatomical reconstruction.'),('Sexuellt välbefinnande','Original complete adult silhouette with protective heart/support circle illustrates intended wellbeing, not guaranteed clinical outcomes.'),('Remiss till sjukhus','Source-specific referral flow: own health station, doctor referral, hospital plastic surgeon; no added referral requirements.')]
photos=json.loads((ROOT/'studio/production/hb-c10/konsstympning-medical-metadata.json').read_text());photopages={p['title']:p for p in photos['query']['pages'].values() if 'imageinfo' in p}
d=yaml.safe_load((EP/'script.yaml').read_text());assets=[]
for i,(title,context) in enumerate(subjects):
    im,draw=canvas(title)
    if i==0:
        droplet(draw,210,270,1.1);arrow(draw,(290,300),(460,300));draw.line((490,205,490,405),fill=GOLD,width=12);draw.line((460,205,520,205),fill=GOLD,width=5);draw.line((460,405,520,405),fill=GOLD,width=5);droplet(draw,585,315,.65,LINE);label(draw,(380,510),'kommer inte ut normalt',32)
    elif i==1:
        # Distinct source-based inflammation illustration, replaced by retained photo
        # when source master is downloaded by the companion fetcher.
        draw.ellipse((220,190,540,510),outline=SOFT,width=7)
        for j in range(10):
            a=j*math.pi/5;x=380+145*math.cos(a);y=350+145*math.sin(a);draw.line((x,y,380+180*math.cos(a),350+180*math.sin(a)),fill=GOLD,width=6)
        draw.ellipse((335,305,425,395),fill=GOLD);label(draw,(380,570),'olika inflammationer',31)
    elif i==2:
        person(draw,200,310,1.2);person(draw,560,310,1.2)
        draw.line((285,340,345,340),fill=GOLD,width=6);draw.line((415,340,475,340),fill=GOLD,width=6);draw.line((365,295,395,385),fill=GOLD,width=6);label(draw,(380,555),'problem och välbefinnande',31)
    elif i==3:
        # Source risk represented by an unnumbered caution triangle beside maternity care.
        person(draw,230,300,1.05);draw.ellipse((215,310,295,390),outline=SOFT,width=6)
        draw.polygon([(520,235),(630,440),(410,440)],outline=GOLD,width=7);draw.line((520,290,520,360),fill=GOLD,width=8);draw.ellipse((513,385,527,399),fill=GOLD);label(draw,(380,550),'ökade risker',32)
    elif i==4:
        draw.arc((210,180,510,510),200,150,fill=SOFT,width=9);draw.line([(230,315),(180,390),(230,405),(230,465),(300,490),(300,555)],fill=SOFT,width=7)
        for j in range(3):draw.arc((320+j*13,245+j*18,445+j*13,370+j*18),20,300,fill=GOLD,width=5)
        label(draw,(380,590),'trauma och mental hälsa',30)
    elif i==5:
        person(draw,380,210,.65);arrow(draw,(340,365),(195,435));arrow(draw,(420,365),(565,435));paper(draw,190,475,160,130);paper(draw,570,475,160,130);label(draw,(190,570),'Öppningsoperation',25);label(draw,(570,570),'Rekonstruerande',25)
    elif i==6:
        droplet(draw,155,310,.7);paper(draw,380,315,120,155);person(draw,610,310,.6);label(draw,(155,470),'urinering',27);label(draw,(380,470),'menstruation',27);label(draw,(610,470),'samlag',27);draw.line((100,550,660,550),fill=GOLD,width=5);label(draw,(380,580),'hjälper i allmänhet',29)
    elif i==7:
        house(draw,380,295,1.7);draw.rectangle((365,285,395,370),fill=GOLD);draw.rectangle((337,312,423,342),fill=GOLD);label(draw,(380,535),'lokalbedövning · poliklinik',30)
    elif i==8:
        person(draw,210,300,1.1);draw.arc((360,210,650,500),220,130,fill=GOLD,width=8);arrow(draw,(450,480),(535,425));draw.ellipse((450,260,525,335),outline=SOFT,width=6);draw.line((488,338,488,415),fill=SOFT,width=6);label(draw,(380,570),'försöker återställa funktion',29)
    elif i==9:
        person(draw,380,300,1.15);draw.arc((195,155,565,580),20,330,fill=SOFT,width=7);heart(draw,565,470);label(draw,(380,600),'underlätta besvären',31)
    elif i==10:
        house(draw,130,300,.8);paper(draw,380,335,130,175);house(draw,625,300,.8);arrow(draw,(215,335),(295,335));arrow(draw,(465,335),(535,335));label(draw,(130,460),'Hälsostation',25);label(draw,(380,460),'Läkarremiss',25);label(draw,(625,460),'Sjukhus',25);label(draw,(625,525),'plastikkirurg',25)
    path=OUT/f'sentence-{i+1:02}.png';im.save(path);assets.append(dict(asset_id=f'picture-{i+1:02}',kind='foreground',visual_type='diagram',files=[info(path)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; source wording retains original publisher terms.',required_credits='Original non-graphic schematic illustrations: Homebrew video studio; source text and publisher terms recorded in sources.yaml and video CREDITS.md.',relevance_verification=context,creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_ids=[d['sentences'][i]['sentence_id']])))
base=yaml.safe_load((ROOT/'studio/episodes/hb-c10-utkomststod/script.yaml').read_text());d['render']=copy.deepcopy(base['render']);d['render']['music_path']=f'studio/media/{SID}/sources/music-bed.flac';d['render']['background_image']=f'studio/media/{SID}/sources/background.jpg';d['render'].pop('background_identity',None)
sources=yaml.safe_load((EP/'sources.yaml').read_text());credits=['Svensk källtext med granskad rysk översättning.']
for item in sources['sources']:credits +=[item['source'].get('title',item['attribution']['title']),item['attribution']['credit']]
credits+=['Fullständiga källor och villkor i medföljande CREDITS.md.'];d['render']['credits']=[dict(heading='Källor · Источники',paragraphs=list(dict.fromkeys(credits))),dict(heading='Bild, musik & röst · Изображения, музыка и голос',paragraphs=['River Flute — Kevin MacLeod (incompetech.com)','Musik: CC BY4.0 · creativecommons.org/licenses/by/4.0','Original schematisk grafik: Homebrew video studio.','Lokal svensk berättarröst: Supertonic3 · F1.'])]
d['scenes']=[dict(id='consequences',description='Hälsoproblem och följder'),dict(id='opening',description='Öppningsoperation och poliklinik'),dict(id='reconstruction',description='Rekonstruerande operation och remiss')]
d['asset_requests']=[dict(id='episode_background',kind='background',description='Distinct source-verified Jorvi Hospital photograph; decorative healthcare setting.',fallback='Another centrally reserved distinct licensed actual Finnish hospital photograph.'),dict(id='music_bed',kind='music',description='River Flute by KevinMacLeod, reserved distinct sourceUSUAN1900005.',fallback='Another centrally reserved distinct calm instrumental with recorded reuse terms.'),dict(id='narration',kind='narration',description='Exact local Swedish F1 full sentence clips.',fallback='Specific diagnostic-led separate retake retaining originals.')]+[dict(id=a['asset_id'],kind='foreground',description=subjects[i][1],fallback='Keep source-specific non-graphic schematic if an actual suitable licensed photograph is unavailable; record exception if imagery would mislead.') for i,a in enumerate(assets)]
d['episode_decisions']=[dict(id=k,decision=v,status='proposed',resolve_during=s) for k,v,s in [('fidelity','Exact11Swedishsentences in stored order, current reviewed Russian; heading is unspoken. No added medical advice.','script'),('visuals','Distinct non-graphic medically neutral source-specific foreground illustrations for all11sentences, actual medical object/emptyhealthcarebuilding photos where useful; no fabricated anatomical diagrams, no photographed person identified as a survivor.','script'),('voice','LocalSwedishSupertonic3F1,32steps,speed.95,seed42,44100HzmonoPCM16. Complete-video pronunciation/listening remains pending.','script'),('pace','3second bilingualtitle, .25second textlead, measured full speech,1.5secondpause,2.2at topicends. Never accelerate to targetduration.','script'),('background','Reserved distinct actualJorviHospital decorative photograph with continuous140secondglobalcyclicpan/zoom,42%darken2.5pxblur and15%relativezoom; sameChapter10oceanpalette.','assets'),('music','DistinctRiverFlute KevinMacLeod USUAN1900005 CCBY4.0, gentleduckedbed withaccepted+2dBadjustmentandsoftfades.','assets'),('closing','Readable15secondcreditcards derived from actualsources.yaml plus full sidecarlicenses.','script')]]
for i,r in enumerate(d['sentences']):r.update(scene_id='consequences' if i<5 else 'opening' if i<8 else 'reconstruction',visual_cue=subjects[i][1],asset_ids=['episode_background',assets[i]['asset_id']],pause_after_seconds=2.2 if i in[4,7,10] else 1.5,render_image=assets[i]['files'][0]['path'],render_caption=False,pronunciation_notes=['Compound medical terminology requires full-video listening; ASR is diagnostic only.'])
(EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text('[]\n');(EP/'prepare_assets.py').write_text((ROOT/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text());print('Authored11source-specific non-graphic picture slides and script.')
