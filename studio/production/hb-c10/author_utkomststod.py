"""Author source-specific illustrations and directing plan for Utkomststod."""
from pathlib import Path
import json,hashlib,yaml,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]; SID='hb-c10-utkomststod';EP=ROOT/'studio/episodes'/SID;MEDIA=ROOT/'studio/media'/SID
BG='#233c50';PANEL='#2d4c63';FG='#faf3e8';SOFT='#c6d9e8';GOLD='#e6c28b';LINE='#4b6e85'
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf';BOLD='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def label(d,xy,text,size=30,fill=FG):
    f=ImageFont.truetype(FONT,size);x,y=xy
    lines=[];line=''
    for word in text.split():
        cand=(line+' '+word).strip()
        if d.textlength(cand,font=f)>650 and line:lines.append(line);line=word
        else:line=cand
    if line:lines.append(line)
    for j,l in enumerate(lines):d.text((x,y+j*(size+7)),l,font=f,fill=fill,anchor='mt')
def house(d,x,y,s=1):
    d.line([(x-70*s,y),(x,y-60*s),(x+70*s,y)],fill=GOLD,width=6)
    d.rectangle((x-52*s,y,x+52*s,y+100*s),outline=SOFT,width=6)
    d.rectangle((x-14*s,y+47*s,x+14*s,y+100*s),outline=GOLD,width=5)
def person(d,x,y,s=1):
    d.ellipse((x-20*s,y-60*s,x+20*s,y-20*s),fill=SOFT);d.rounded_rectangle((x-34*s,y-8*s,x+34*s,y+80*s),radius=15,outline=SOFT,width=5)
    d.line([(x-18*s,y+80*s),(x-22*s,y+125*s)],fill=SOFT,width=6);d.line([(x+18*s,y+80*s),(x+22*s,y+125*s)],fill=SOFT,width=6)
def coins(d,x,y,n=3):
    for j in range(n):d.ellipse((x-40,y-j*22,x+40,y+25-j*22),fill=PANEL,outline=GOLD,width=4)
def paper(d,x,y,w=120,h=155):
    d.rounded_rectangle((x-w/2,y-h/2,x+w/2,y+h/2),radius=10,outline=SOFT,width=5)
    for j in range(3):d.line((x-w*.32,y-h*.25+j*30,x+w*.32,y-h*.25+j*30),fill=LINE,width=4)
def arrow(d,a,b):
    d.line((a,b),fill=GOLD,width=6);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-20*math.cos(ang-.5),b[1]-20*math.sin(ang-.5)),(b[0]-20*math.cos(ang+.5),b[1]-20*math.sin(ang+.5))],fill=GOLD)
def canvas(title):
    im=Image.new('RGB',(760,720),BG);d=ImageDraw.Draw(im);d.rounded_rectangle((15,15,745,705),radius=25,outline=LINE,width=3,fill=PANEL);label(d,(380,45),title,34,GOLD);label(d,(380,665),'Schematisk illustration',22,SOFT);return im,d
specs=[('Ansöka hos FPA','Family and insufficient means lead to an application to FPA; no eligibility guarantee.'),('Nödvändiga utgifter','Four visible objects represent food, clothing, healthcare and housing.'),('Stadigvarande bosatt','Home with Finnish flag represents source residence condition, not geographic eligibility boundaries.'),('Inkomster och tillgångar','Income and assets enter the same calculation; no invented monetary thresholds.'),('Sociala förmåner','Separate benefit sources enter the calculation, without double-counting or invented amounts.'),('Andra bidrag först','Source priority: apply for other entitled benefits before social assistance.'),('Tillfällig hjälp','Hourglass and limited calendar segment show temporary support without implying a fixed deadline.'),('När inkomsterna inte räcker','A schematic shortfall between resources and necessary expenses, without invented sums.'),('Kompletterande stöd','Separate path to wellbeing services county when special expenses are outside basic support.'),('Boende och plötslig förändring','A house under a protective umbrella and a declining income line show the two examples from source.')]
assets=[]
for idx,(title,meaning) in enumerate(specs):
    im,d=canvas(title)
    if idx==0:
        person(d,120,280,.8);person(d,210,320,.55);coins(d,170,525,1);arrow(d,(290,350),(445,350));paper(d,570,350,165,220);label(d,(570,480),'FPA',38)
    elif idx==1:
        # Distinct object drawings: loaf, shirt, medical cross and home.
        d.rounded_rectangle((90,190,300,320),radius=58,fill=GOLD);d.arc((115,190,165,290),270,70,fill=BG,width=5);d.arc((190,190,240,290),270,70,fill=BG,width=5)
        d.polygon([(480,180),(515,220),(555,220),(590,180),(650,230),(615,290),(590,268),(590,350),(480,350),(480,268),(455,290),(420,230)],outline=SOFT,width=5)
        d.rectangle((140,440,180,580),fill=SOFT);d.rectangle((90,490,230,530),fill=SOFT);house(d,545,480,.9)
        for x,y,t in[(195,345,'Mat'),(535,365,'Kläder'),(160,590,'Hälsovård'),(545,595,'Boende')]:label(d,(x,y),t,27)
    elif idx==2:
        house(d,330,320,1.7);d.line((520,235,520,510),fill=SOFT,width=6);d.rectangle((520,230,680,330),fill=FG);d.rectangle((565,230,590,330),fill='#326c9c');d.rectangle((520,267,680,292),fill='#326c9c');d.line((165,560,640,560),fill=LINE,width=6)
    elif idx==3:
        coins(d,170,300,4);label(d,(170,350),'Inkomster',28);paper(d,565,270);label(d,(565,365),'Tillgångar',28);arrow(d,(220,415),(330,510));arrow(d,(520,415),(420,510));d.rounded_rectangle((280,480,480,605),radius=20,outline=GOLD,width=5);label(d,(380,520),'Kalkyl',34)
    elif idx==4:
        for x,t in[(145,'FPA'),(380,'Arbetspension'),(615,'Arbetslöshetskassa')]:
            paper(d,x,260,110,140);label(d,(x,350),t,22);arrow(d,(x,405),(380,500))
        d.rounded_rectangle((255,500,505,610),radius=20,outline=GOLD,width=5);label(d,(380,535),'Kalkylen',32)
    elif idx==5:
        paper(d,190,330,180,230);label(d,(190,470),'Andra bidrag',29);arrow(d,(305,335),(450,335));paper(d,570,330,180,230);label(d,(570,470),'Utkomststöd',29);d.ellipse((130,155,195,220),outline=GOLD,width=5);label(d,(162,165),'1',35);d.ellipse((510,155,575,220),outline=GOLD,width=5);label(d,(542,165),'2',35)
    elif idx==6:
        d.line([(230,180),(530,180),(230,560),(530,560)],fill=GOLD,width=9);d.line([(230,180),(530,560)],fill=SOFT,width=7);d.line([(530,180),(230,560)],fill=SOFT,width=7);d.polygon([(260,205),(500,205),(380,355)],fill=GOLD);d.polygon([(380,410),(285,535),(475,535)],fill=GOLD);d.line((200,600,560,600),fill=LINE,width=7)
    elif idx==7:
        # Unnumbered resource and expense bins show a deficit, not a numerical benefit calculation.
        d.rectangle((130,220,300,540),outline=SOFT,width=5);d.rectangle((440,220,610,540),outline=SOFT,width=5);d.rectangle((136,420,294,535),fill=GOLD);d.rectangle((446,300,604,535),fill=SOFT);d.line((305,300,420,300),fill=GOLD,width=5);d.line((305,420,420,420),fill=GOLD,width=5);d.line((365,300,365,420),fill=GOLD,width=5);label(d,(215,565),'Inkomster',29);label(d,(525,565),'Nödvändiga utgifter',26)
    elif idx==8:
        paper(d,150,290,135,180);label(d,(150,410),'Särskilda utgifter',25);arrow(d,(255,300),(400,300));house(d,560,275,1.2);label(d,(560,430),'Välfärdsområdet',29);d.line((450,510,665,510),fill=SOFT,width=5);label(d,(545,540),'Kompletterande stöd',25)
    elif idx==9:
        house(d,220,410,1.1);d.arc((80,180,365,425),180,360,fill=GOLD,width=8);d.line((222,185,222,410),fill=GOLD,width=6);d.line((450,240,450,520,670,520),fill=SOFT,width=4);d.line([(470,270),(520,310),(555,305),(620,440),(650,470)],fill=GOLD,width=8);label(d,(220,560),'Trygga boendet',27);label(d,(560,560),'Plötsligt försämrad ekonomi',23)
    p=MEDIA/'pictures'/f'sentence-{idx+1:02}.png';p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    assets.append(dict(asset_id=f'picture-{idx+1:02}',kind='foreground',visual_type='diagram',files=[info(p)],creator='Homebrew video studio',reuse_terms='Original schematic illustration under repository MIT license; source wording retains publisher terms.',required_credits='Original schematic illustrations: Homebrew video studio; archived source text credited in sources.yaml and video CREDITS.md.',relevance_verification=meaning,creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_index=idx)))
d=yaml.safe_load((EP/'script.yaml').read_text());d['scenes']=[dict(id='necessities',description='Behov, utgifter och stadigvarande boende'),dict(id='calculation',description='Inkomster och andra bidrag i beräkningen'),dict(id='temporary',description='Tillfällig hjälp när inkomster inte räcker'),dict(id='additional',description='Välfärdsområdets kompletterande stöd')]
d['episode_decisions']=[dict(id=k,decision=v,status='proposed',resolve_during=stage) for k,v,stage in [('opening','Unspoken exact Swedish/Russian heading, 3 seconds; no added narration.','script'),('source','Read every exact source sentence once in stored order with reviewed Russian display.','script'),('visuals','Ten individually composed source-specific pictorial illustrations, one for each sentence, on fixed left; bilingual panel stays right. No invented sums, thresholds, dates or legal conditions.','script'),('voice','Local Supertonic 3 F1, Swedish, 32 steps, speed .95, NumPy seed42, PCM16 44100Hz mono; listening pending complete-video review.','script'),('pace','Text appears .25s before full measured speech, pause1.5s ordinarily and2.2s at topic ends; longer sentence gets2.5s.','script'),('background','Distinct source-identified Kela office photograph, ocean palette, darkened42%,blur2.5px; continuous global140s cyclic pan/zoom, no reset. Final metadata resolved during assets.','assets'),('music','Distinct reserved Organic Meditations One (Kevin MacLeod), USUAN1100760, CC BY4.0; +2dB bed adjustment with speech ducking and fades, crossfade loop only if needed.','assets'),('closing','15 seconds for each readable credit card and full attribution sidecar.','script')]]
d['asset_requests']=[dict(id='episode_background',kind='background',description='Distinct verified Kela office photograph; decorative social-assistance setting.',fallback='Another distinct licensed accurately identified Finnish social-services building.'),dict(id='music_bed',kind='music',description='Organic Meditations One by Kevin MacLeod, distinct reserved source USUAN1100760.',fallback='Another distinct calm source-verified licensed instrumental track.'),dict(id='narration',kind='narration',description='One exact local Swedish F1 clip per source sentence.',fallback='Diagnostic-led targeted meaning-preserving retake, retain original metrics.')]+[dict(id=a['asset_id'],kind='foreground',description=specs[i][1],fallback='Leave foreground open and document why if the schematic misrepresents source meaning.') for i,a in enumerate(assets)]
for i,r in enumerate(d['sentences']):
    r.update(scene_id=['necessities' if i<3 else 'calculation' if i<6 else 'temporary' if i<8 else 'additional'][0],asset_ids=['episode_background',assets[i]['asset_id']],visual_cue=specs[i][1],pause_after_seconds=2.5 if len(r['sv'])>190 else 2.2 if i in(2,5,7,9) else 1.5,render_image=assets[i]['files'][0]['path'],render_caption=False,pronunciation_notes=['FPA and Finnish benefit names require whole-video listening; automated ASR is diagnostic only.'])
    if 'FPA' in r['sv']:r['speech_override']=dict(text=r['sv'].replace('FPA','F P A'),reason='Speak Swedish initial letters distinctly without changing display or meaning.',review_status='pending')
d['render']=dict(music_path=f'studio/media/{SID}/sources/music-bed.flac',background_image=f'studio/media/{SID}/sources/background.jpg',background_style=dict(darken=.42,blur_pixels=2.5,zoom_start=1.06,zoom_end=1.219,pan_start=[.15,.15],pan_end=[.85,.85],resampling='bilinear',motion='Smooth global-timeline cyclic diagonal pan/zoom; no sentence resets',motion_cycles=1),music_gain_adjustment_db=2.,music_loop_crossfade_seconds=4,palette=dict(background=BG,text=FG,secondary=SOFT,highlight=GOLD,separator=LINE),font_files=dict(regular=FONT,bold=BOLD),credits=[dict(heading='Källor · Источники',paragraphs=['Svensk källtext med granskad rysk översättning.','Yhteiskuntaorientaatio.fi.','Finlands Flyktinghjälp; Utbildningsstyrelsen; UF-centret.','Fullständiga källor och villkor i medföljande CREDITS.md.']),dict(heading='Bild, musik & röst · Изображения, музыка и голос',paragraphs=['Original schematisk grafik: Homebrew video studio.','Organic Meditations One — Kevin MacLeod (incompetech.com)','Musik: CC BY4.0 · creativecommons.org/licenses/by/4.0','Lokal svensk berättarröst: Supertonic3 · F1.'])],adaptation_notes=['Ten original source-based schematic illustrations; no invented benefit sums or conditions.','Exact archived Swedish and current reviewed Russian shown together.','Decorative background cropped, darkened, blurred and continuously panned/zoomed; retain source license.','Music faded, ducked, +2dB adjustment, repeated with4second equal-power crossfades only if needed.'])
(EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text('[]\n')
brief=yaml.safe_load((EP/'brief.yaml').read_text());brief['production_status']='script_ready';brief['issues']=['Script source and translation validation pending generated review; assets and whole-video review pending.'];(EP/'brief.yaml').write_text(yaml.safe_dump(brief,allow_unicode=True,sort_keys=False))
print('Authored 10 unique source-specific diagrams and exact bilingual plan.')
