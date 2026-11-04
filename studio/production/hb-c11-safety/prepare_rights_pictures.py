"""Compose fifteen real nature photographs and six individually drawn source diagrams."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[3];SID='hb-c11-allemansratten';EP=ROOT/'studio/episodes'/SID;MEDIA=ROOT/'studio/media'/SID;OUT=MEDIA/'pictures';OUT.mkdir(parents=True,exist_ok=True)
code=(ROOT/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0];ns={'__file__':str(Path(__file__))};exec(compile(code,'nature-primitives','exec'),ns);ns.update(BG='#243c32',PANEL='#2f4d40',FG='#faf3e8',SOFT='#c5dfce',GOLD='#e3c58c',LINE='#4d7560')
canvas,label,person,house,paper,arrow=[ns[k] for k in ['canvas','label','person','house','paper','arrow']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def tent(d,x,y,s=1):
    d.polygon([(x-90*s,y+60*s),(x,y-75*s),(x+90*s,y+60*s)],outline=SOFT,width=5);d.line((x,y-75*s,x,y+60*s),fill=GOLD,width=5);d.line((x-120*s,y+60*s,x+120*s,y+60*s),fill=LINE,width=5)
def tree(d,x,y,s=1):
    d.line((x,y-5*s,x,y+90*s),fill=GOLD,width=5)
    for yy,w in[(y-80*s,65*s),(y-25*s,80*s),(y+35*s,95*s)]:d.polygon([(x,yy-80*s),(x-w,yy+25*s),(x+w,yy+25*s)],outline=SOFT,width=4)
def bird(d,x,y,s=1):
    d.ellipse((x-50*s,y-25*s,x+35*s,y+35*s),outline=SOFT,width=5);d.ellipse((x+15*s,y-50*s,x+65*s,y),outline=SOFT,width=4);d.polygon([(x+65*s,y-35*s),(x+95*s,y-18*s),(x+65*s,y-10*s)],fill=GOLD);d.polygon([(x-45*s,y),(x-90*s,y-30*s),(x-75*s,y+35*s)],outline=SOFT,width=4);d.line((x-10*s,y+35*s,x-10*s,y+70*s),fill=GOLD,width=4)
def dog(d,x,y,s=1):
    d.rounded_rectangle((x-70*s,y-30*s,x+50*s,y+35*s),radius=15,outline=SOFT,width=5);d.ellipse((x+35*s,y-75*s,x+105*s,y-10*s),outline=SOFT,width=5);d.polygon([(x+45*s,y-65*s),(x+40*s,y-105*s),(x+70*s,y-75*s)],fill=GOLD)
    for xx in[x-50*s,x+30*s]:d.line((xx,y+35*s,xx,y+95*s),fill=SOFT,width=6)
    d.line((x-65*s,y-15*s,x-105*s,y-65*s),fill=SOFT,width=6);d.line((x+70*s,y-20*s,x+120*s,y-130*s),fill=GOLD,width=5)
def bike(d,x,y,s=1):
    for xx in[x-75*s,x+75*s]:d.ellipse((xx-50*s,y-50*s,xx+50*s,y+50*s),outline=SOFT,width=5)
    d.line([(x-75*s,y),(x-20*s,y-80*s),(x+15*s,y),(x-75*s,y),(x+40*s,y-80*s),(x+75*s,y)],fill=GOLD,width=5);d.line((x+30*s,y-100*s,x+65*s,y-100*s),fill=SOFT,width=5)
def no(d,x,y,r):d.ellipse((x-r,y-r,x+r,y+r),outline=GOLD,width=7);d.line((x-r*.7,y-r*.7,x+r*.7,y+r*.7),fill=GOLD,width=8)
photos=json.loads((EP/'selected-photos.json').read_text());old=json.loads((EP/'retained-photo-assets.json').read_text());script=yaml.safe_load((EP/'script.yaml').read_text());plans=json.loads((EP/'picture-plan.json').read_text());assets=[];downloads=[];screen=[]
for i,row in enumerate(script['sentences']):
    key=f'picture-{i+1:03}';dest=OUT/f'sentence-{i+1:02}.png'
    if str(i) in photos or str(i) in old:
        if str(i) in photos:
            p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=ROOT/p['path'];creator=clean('Artist');terms=clean('LicenseShortName')+' '+clean('LicenseUrl');source=pi['descriptionurl'];credit=p['title'].removeprefix('File:')+' — '+creator+'. '+terms+'. '+source+'. Complete photograph proportionally resized and letterboxed; original license retained.';context=p['context'];url=p['download_url'];screen.append(p['title'].removeprefix('File:')+' — '+creator+' · '+clean('LicenseShortName'))
        else:
            p=old[str(i)];a=p['asset_record'];raw=ROOT/p['path'];creator=a['creator'];terms=a['reuse_terms'];source=a['source_url'];credit=a['required_credits'];context=p['context'];url=p['url'];screen.append('Vehnäpelto7 — '+creator+' · '+terms.split('https:')[0])
        image=ImageOps.exif_transpose(Image.open(raw)).convert('RGB');image.thumbnail((760,720),Image.Resampling.LANCZOS);im=Image.new('RGB',(760,720),BG);im.paste(image,((760-image.width)//2,(720-image.height)//2));im.save(dest);downloads.append(dict(**info(raw),url=url));asset=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],creator=creator,reuse_terms=terms,source_url=source,required_credits=credit,relevance_verification=context,creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),transform='Complete source photograph proportionally resized, EXIF orientation respected, letterboxed.'))
    else:
        im,d=canvas(plans[i]['title'])
        if i==2:
            person(d,160,245,.6);bike(d,555,340,.65);tent(d,180,520,.7);d.line((395,195,395,585),fill=LINE,width=4);d.line((90,390,315,390),fill=LINE,width=4);d.line((440,390,680,390),fill=LINE,width=4)
            d.arc((465,415,590,535),180,360,fill=GOLD,width=6);d.line((590,475,590,585),fill=GOLD,width=4);d.arc((575,570,605,600),0,180,fill=SOFT,width=4);label(d,(380,630),'Källans följande exempel',25)
        elif i==8:
            no(d,380,350,155);tree(d,150,260,.6);house(d,600,245,.65);d.rounded_rectangle((110,495,205,590),radius=9,outline=SOFT,width=5);d.line((105,485,210,485),fill=GOLD,width=5);d.polygon([(570,590),(590,510),(620,550),(640,475),(675,590)],outline=SOFT,width=5);label(d,(380,625),'Källans följande förbud',26)
        elif i==9:
            house(d,150,280,.8);person(d,380,320,.85);tree(d,610,260,.65);bird(d,590,495,.65)
            for dx in[0,30,60]:d.arc((420+dx,250-dx*.25,485+dx,370+dx*.25),270,90,fill=GOLD,width=4)
            no(d,490,305,85);d.line((235,425,335,425),fill=LINE,width=4);label(d,(380,600),'andra människor och miljön',28)
        elif i==15:
            house(d,250,260,1.35);tent(d,475,450,1);d.line((340,400,385,400),fill=GOLD,width=7);d.line((340,380,340,420),fill=GOLD,width=5);d.line((385,380,385,420),fill=GOLD,width=5);no(d,440,425,130);label(d,(380,585),'alltför nära en bostad',30)
            for xx in[590,620,650]:d.arc((xx,280,xx+40,390),270,90,fill=LINE,width=4)
        elif i==19:
            label(d,(380,165),'i andra områden · i allmänhet',27)
            for j,t in enumerate(['mars','april','maj','juni','juli','augusti']):
                x=150+j%3*230;y=245+j//3*110;d.rounded_rectangle((x-90,y-15,x+90,y+65),radius=12,outline=GOLD,width=4);label(d,(x,y+5),t,28)
            dog(d,230,495,.6);bird(d,565,505,.7);d.line((355,530,435,530),fill=LINE,width=5);label(d,(380,620),'fåglarnas häckningstid',27)
        elif i==20:
            dog(d,380,240,.7);d.line((380,330,180,390),fill=LINE,width=4);d.line((380,330,580,390),fill=LINE,width=4)
            d.line((120,390,120,535,245,535),fill=SOFT,width=6);d.line((120,390,245,390,245,535),fill=SOFT,width=6);d.line((175,390,175,465),fill=GOLD,width=4);d.arc((150,440,200,480),0,180,fill=GOLD,width=5);no(d,180,455,105)
            d.line((485,510,680,510),fill=SOFT,width=6);d.line((575,400,575,505),fill=GOLD,width=5);d.arc((495,365,655,430),180,360,fill=GOLD,width=5)
            for yy in[535,560]:d.line([(485,yy),(515,yy-8),(545,yy),(575,yy-8),(605,yy),(635,yy-8),(675,yy)],fill=LINE,width=4)
            no(d,580,465,108);label(d,(180,610),'lekplatser',28);label(d,(580,610),'allmänna badstränder',24)
        else:raise ValueError('Missing meaningful source-specific picture '+str(i))
        im.save(dest);asset=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; source wording retains publisher terms.',required_credits='Original source-based nature-access artwork: Homebrew video studio; archived wording credited in sources.yaml and CREDITS.md.',relevance_verification=plans[i]['request']+' Original pictorial composition restricted to the exact archived source; no invented distance,legal sign,calendar day or exception.',creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_ids=[row['sentence_id']]))
    assets.append(asset);row.update(asset_ids=['episode_background',key],render_image=str(dest.relative_to(ROOT)),render_caption=False)
script['asset_requests']=script['asset_requests'][:3]+[dict(id=a['asset_id'],kind='foreground',description=a['relevance_verification'],fallback='A faithful useful pictorial alternative; document any omission after reasonable research.') for a in assets];script['render']['credits']=script['render']['credits'][:2]
for j in range(0,len(screen),2):script['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[j:j+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
for decision in script['episode_decisions']:
    if decision['id']=='visuals':decision['decision']='Every source sentence has a distinct relevant foreground picture: fifteen licensed actual nature/activity/object photographs and six individually composed pictorial explanations. Photographs do not establish current site permissions or allege an actual offence. Source exceptions and qualifications remain exact.'
(EP/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(EP/'prepare_assets.py').write_text((ROOT/'studio/episodes/hb-c11-naturens-sakerhet/prepare_assets.py').read_text());print('Prepared',len(assets),'distinct pictures;',len(screen),'licensed photographs.')
