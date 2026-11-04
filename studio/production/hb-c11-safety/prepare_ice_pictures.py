"""Draw source-specific ice-safety explanations and retain six actual photographs."""
from pathlib import Path
import json,yaml,hashlib,re,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];SID='hb-c11-naturens-sakerhet';EP=ROOT/'studio/episodes'/SID;MEDIA=ROOT/'studio/media'/SID;OUT=MEDIA/'pictures';OUT.mkdir(parents=True,exist_ok=True)
code=(ROOT/'studio/production/hb-c10/author_utkomststod.py').read_text().split('specs=')[0];ns={'__file__':str(Path(__file__))};exec(compile(code,'ice-drawing-primitives','exec'),ns);ns.update(BG='#243c32',PANEL='#2f4d40',FG='#faf3e8',SOFT='#c5dfce',GOLD='#e3c58c',LINE='#4d7560')
canvas,label,person,paper,arrow=[ns[k] for k in ['canvas','label','person','paper','arrow']];FG,SOFT,GOLD,LINE,PANEL,BG=[ns[k] for k in ['FG','SOFT','GOLD','LINE','PANEL','BG']]
def info(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def water(d,y=450):
    for k in range(3):
        pts=[(x,y+k*25+8*math.sin(x/35)) for x in range(50,711,12)];d.line(pts,fill=LINE,width=4)
def ice(d,y=380,bottom=460):
    d.polygon([(50,y),(710,y),(710,bottom),(50,bottom)],fill=SOFT);d.line((50,y,710,y),fill=FG,width=5)
def boat(d,x,y):
    d.polygon([(x-110,y),(x+110,y),(x+70,y+65),(x-60,y+65)],outline=SOFT,width=6);d.line((x,y-145,x,y),fill=GOLD,width=6);d.polygon([(x+8,y-140),(x+8,y-12),(x+100,y-12)],outline=GOLD,width=6)
def picks(d,x,y):
    for sign in[-1,1]:
        xx=x+sign*42;d.rounded_rectangle((xx-16,y-40,xx+16,y+65),radius=10,fill=GOLD);d.line((xx,y+65,xx,y+112),fill=SOFT,width=5)
    d.arc((x-43,y-105,x+43,y+5),180,360,fill=SOFT,width=5)
d=yaml.safe_load((EP/'script.yaml').read_text());photos=json.loads((EP/'selected-photos.json').read_text());assets=[];downloads=[];screen=[]
subjects={2:('Säkerhet till sjöss','Watercraft and protection symbol represent the source safety statement; no additional navigation rule.'),3:('Väder och flytväst','Conceptual weather report and a life jacket with source right-size label; no invented forecast or equipment certification.'),7:('Tjockhet och hållbarhet','Unmeasured ice section with a question represents checking bearing capacity; no safe centimetre threshold is invented.'),8:('Checklista för isen','Six object-based checklist symbols summarize the following source statements without adding a safety procedure.'),9:('Då isen fryser','Thin newly forming ice and a crossed walking path illustrate the source warning, not a measured physical model.'),10:('Tjockleken kan variera','Qualitative variation in ice thickness across one short span; no dimensions or safe/unsafe threshold.'),11:('Våris','Sun, porous ice and a question represent difficulty judging spring bearing capacity; no visual test guarantees safety.'),13:('Svårt att ta sig upp','Ice edge, person and unavailable rescue picks represent the source difficulty statement without step-by-step self-rescue instruction.'),14:('Om du inte är säker','Person remains on shore while uncertain ice is marked with a question/stop symbol, matching the exact source warning.')}
for i,r in enumerate(d['sentences']):
    key=f'picture-{i+1:03}';dest=OUT/f'sentence-{i+1:02}.png'
    if str(i) in photos:
        p=photos[str(i)];pi=p['imageinfo'];meta=pi['extmetadata'];clean=lambda k:re.sub('<[^>]+>','',meta.get(k,{}).get('value','')).strip();raw=ROOT/p['path'];im=Image.open(raw).convert('RGB');im.thumbnail((1100,1000));im.save(dest)
        asset=dict(asset_id=key,kind='foreground',visual_type='photograph',files=[info(dest)],source_url=pi['descriptionurl'],creator=clean('Artist'),reuse_terms=clean('LicenseShortName')+' '+clean('LicenseUrl'),required_credits=p['title'].removeprefix('File:')+' — '+clean('Artist')+'. '+clean('LicenseShortName')+'. '+pi['descriptionurl']+' '+clean('LicenseUrl')+'. Complete photograph proportionally resized; original terms retained.',relevance_verification=p['context'],creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),transform='Complete source photograph proportionally resized.'))
        downloads.append(dict(**info(raw),url=p['download_url']));screen.append(p['title'].removeprefix('File:')+' — '+clean('Artist')+' · '+clean('LicenseShortName'))
    else:
        title,meaning=subjects[i];im,draw=canvas(title)
        if i==2:
            boat(draw,260,365);water(draw,470);draw.polygon([(510,235),(575,215),(640,235),(628,355),(575,420),(522,355)],outline=GOLD,width=7);draw.line([(540,315),(565,344),(612,283)],fill=SOFT,width=7)
        elif i==3:
            draw.rounded_rectangle((100,185,310,510),radius=26,outline=SOFT,width=6);draw.ellipse((140,260,210,330),fill=GOLD);draw.ellipse((170,285,255,350),fill=SOFT);draw.line((143,410,267,410),fill=LINE,width=6)
            draw.polygon([(475,235),(530,200),(570,280),(610,200),(665,235),(640,490),(500,490)],outline=GOLD,width=7);draw.line((570,290,570,490),fill=SOFT,width=6);draw.line((505,360,638,360),fill=SOFT,width=6);label(draw,(570,555),'rätt storlek',30)
        elif i==7:
            ice(draw,330,470);water(draw,515);draw.line((600,338,600,460),fill=GOLD,width=7);draw.line((575,338,625,338),fill=GOLD,width=5);draw.line((575,460,625,460),fill=GOLD,width=5);label(draw,(380,210),'?',65);label(draw,(380,585),'Ta reda på innan du går ut',29)
        elif i==8:
            paper(draw,380,365,470,440)
            for j in range(6):
                x=220 if j%2==0 else 445;y=205+(j//2)*135;draw.rounded_rectangle((x-24,y-15,x+18,y+25),radius=5,outline=GOLD,width=4)
                if j==0:draw.line((x+40,y+5,x+145,y+5),fill=SOFT,width=5);draw.line((x+40,y+22,x+145,y+32),fill=SOFT,width=4)
                elif j==1:draw.line([(x+42,y-5),(x+88,y+20),(x+145,y-12)],fill=SOFT,width=5)
                elif j==2:draw.ellipse((x+75,y-20,x+125,y+30),outline=GOLD,width=5)
                elif j==3:picks(draw,x+95,y-5)
                elif j==4:draw.arc((x+55,y-25,x+135,y+45),0,180,fill=SOFT,width=5)
                else:label(draw,(x+95,y-20),'?',36)
        elif i==9:
            water(draw,400);draw.line((70,365,690,365),fill=SOFT,width=12);draw.ellipse((295,195,360,250),fill=SOFT);draw.line((327,252,327,310),fill=SOFT,width=7);draw.line([(280,355),(327,310),(375,355)],fill=SOFT,width=7);draw.line((260,170,410,375),fill=GOLD,width=10);label(draw,(380,540),'håller inte genast',32)
        elif i==10:
            draw.polygon([(75,280),(685,280),(685,445),(550,420),(425,480),(290,355),(160,405),(75,340)],fill=SOFT);draw.line((75,280,685,280),fill=FG,width=5);water(draw,510);label(draw,(380,190),'korta sträckor',32);label(draw,(380,600),'tjockleken kan variera',30)
        elif i==11:
            draw.ellipse((90,180,200,290),outline=GOLD,width=7)
            for a in range(8):
                ang=a*math.pi/4;draw.line((145+75*math.cos(ang),235+75*math.sin(ang),145+100*math.cos(ang),235+100*math.sin(ang)),fill=GOLD,width=5)
            ice(draw,405,490)
            for x,y in[(155,430),(285,450),(420,425),(575,460)]:draw.ellipse((x-22,y-13,x+22,y+13),fill=LINE)
            label(draw,(485,200),'?',75);label(draw,(380,585),'svårt att bedöma bärkraften',29)
        elif i==13:
            draw.polygon([(60,330),(270,330),(270,450),(60,450)],fill=SOFT);draw.polygon([(550,330),(710,330),(710,450),(550,450)],fill=SOFT);water(draw,490);person(draw,405,325,.9);picks(draw,140,190);draw.line((80,140,205,305),fill=GOLD,width=8);label(draw,(380,590),'mycket svårt utan dem',30)
        elif i==14:
            draw.polygon([(50,430),(350,430),(350,590),(50,590)],fill=LINE);ice(draw,465,505);draw.rectangle((50,430,350,590),fill=LINE);person(draw,190,290,1.05);arrow(draw,(265,370),(425,370));draw.line((430,285,430,455),fill=GOLD,width=10);label(draw,(575,285),'?',65);label(draw,(380,610),'gå inte ut om du inte är säker',27)
        im.save(dest);asset=dict(asset_id=key,kind='foreground',visual_type='diagram',files=[info(dest)],creator='Homebrew video studio',reuse_terms='Original schematic artwork under repository MIT license; source wording retains publisher terms.',required_credits='Original source-based ice-safety illustrations: Homebrew video studio; source text attribution in sources.yaml and CREDITS.md.',relevance_verification=meaning,creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),source_sentence_ids=[r['sentence_id']]))
    assets.append(asset);r['render_image']=str(dest.relative_to(ROOT));r['render_caption']=False
    # Use the actual selected asset ID while keeping source-owned fields unchanged.
    r['asset_ids']=['episode_background',key]
    d['asset_requests'][i+3]['id']=key
    d['asset_requests'][i+3]['description']=asset['relevance_verification']
d['render']['credits']=d['render']['credits'][:2]
for i in range(0,len(screen),2):d['render']['credits'].append(dict(heading='Förgrundsbilder · Изображения',paragraphs=screen[i:i+2]+['Original schematisk grafik: Homebrew video studio.','Fullständiga källor och licenser i CREDITS.md.']))
(EP/'script.yaml').write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=100));(EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n');(EP/'foreground-downloads.json').write_text(json.dumps(downloads,ensure_ascii=False,indent=2)+'\n');(EP/'prepare_assets.py').write_text((ROOT/'studio/episodes/hb-c10-utkomststod/prepare_assets.py').read_text());print('Prepared15distinct ice-safety pictures,6photographs and9source-specific diagrams.')
