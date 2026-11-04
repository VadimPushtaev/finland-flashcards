"""Draw conditional citizenship relationships without inventing real-country rules."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import re

from PIL import Image, ImageDraw, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parent
MEDIA = ROOT/'studio/media'/EP.name
SPEC = importlib.util.spec_from_file_location('studio_pictorial_primitives',
    ROOT/'studio/episodes/hb-c07-ekonomi/prepare_foregrounds.py')
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)
BG, FG, SECOND, ACCENT, LINE = '#352e49','#faf3e8','#d7cce7','#e2c58b','#685881'
P.BG, P.TEXT, P.SECOND, P.ACCENT, P.LINE = BG, FG, SECOND, ACCENT, LINE
FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'


def info(path):
    return dict(path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    script=yaml.safe_load((EP/'script.yaml').read_text())
    evidence=json.loads((EP/'media-sources.json').read_text())
    plans=json.loads((EP/'picture-plan.json').read_text())
    out=MEDIA/'pictures'
    out.mkdir(parents=True,exist_ok=True)
    assets=[]
    for index,(name,title,kind,description) in enumerate(plans):
        im=Image.new('RGB',(760,720),BG)
        d=ImageDraw.Draw(im)

        def label(text,x,y,width=650,size=31):
            return P.wrapped(d,text,x,y,width,size=size,color=FG,bold=True)

        def icon(kind,x,y,scale=1):
            P.icon(d,kind,x,y,scale)

        def arrow(start,end):
            d.line([start,end],fill=ACCENT,width=6)
            x,y=end
            angle=math.atan2(y-start[1],x-start[0])
            back_x,back_y=x-20*math.cos(angle),y-20*math.sin(angle)
            d.polygon([(x,y),(back_x-11*math.sin(angle),back_y+11*math.cos(angle)),
                       (back_x+11*math.sin(angle),back_y-11*math.cos(angle))],fill=ACCENT)

        def document(x,y,caption,scale=1,cross=False):
            icon('document',x,y,scale)
            label(caption,x,y+100*scale,width=260,size=28)
            if cross:
                d.line((x-68*scale,y+77*scale,x+68*scale,y-77*scale),fill='#e8b3af',width=8)

        def question(x,y):
            d.ellipse((x-34,y-34,x+34,y+34),outline=SECOND,width=4)
            d.text((x,y),'?',font=ImageFont.truetype(FONT,45),fill=ACCENT,anchor='mm')

        def citizenship_pair(y=260):
            document(212,y,'finskt',1.1)
            document(548,y,'annat land',1.1)

        if kind=='photo':
            photo=Image.open(MEDIA/'sources'/('foreground-'+name+'.jpg')).convert('RGB')
            photo.thumbnail((760,720),Image.Resampling.LANCZOS)
            im.paste(photo,((760-photo.width)//2,(720-photo.height)//2))
        elif name=='multiple':
            icon('person',380,469,1.1)
            citizenship_pair(210)
            d.line((380,420,212,342),fill=SECOND,width=6)
            d.line((380,420,548,342),fill=SECOND,width=6)
            label('flerfaldigt medborgarskap',380,56,size=34)
        elif name=='different_rules':
            for x,accepted in [(212,True),(548,False)]:
                d.rounded_rectangle((x-137,178,x+137,508),radius=24,outline=LINE,width=5)
                document(x-40,286,'',.67)
                document(x+40,286,'',.67)
                if accepted:
                    d.line((x-45,430,x-10,468,x+58,394),fill=ACCENT,width=9)
                else:
                    d.line((x-52,401,x+52,469),fill='#e8b3af',width=9)
                    d.line((x-52,469,x+52,401),fill='#e8b3af',width=9)
            label('Alla stater godkänner dock inte',380,70,size=32)
        elif name=='check_first':
            icon('person',142,352,1.1)
            question(380,201)
            document(593,294,'det land där du är medborgare',1)
            arrow((240,342),(479,342))
            document(380,558,'ansöker om finskt medborgarskap',.62)
            label('ta reda på',380,68,size=38)
        elif name=='possible_loss':
            d.rounded_rectangle((28,24,732,123),radius=18,outline=SECOND,width=4)
            label('Om denna stat inte tillåter flerfaldigt medborgarskap',380,40,width=660,size=28)
            document(172,232,'nuvarande',1.1)
            d.line((138,422,206,490),fill='#e8b3af',width=9)
            d.line((138,490,206,422),fill='#e8b3af',width=9)
            arrow((287,267),(473,267))
            document(588,232,'finskt',1.1)
            question(380,494)
            label('kan förlora',380,615,size=40)
        elif name=='balance':
            d.line((380,191,380,550,245,550),fill=ACCENT,width=9)
            d.line((380,550,515,550),fill=ACCENT,width=9)
            d.line((160,253,600,253),fill=SECOND,width=9)
            for x in (192,568):
                d.line((x,253,x-70,421,x+70,421,x,253),fill=SECOND,width=6)
                d.arc((x-70,389,x+70,455),0,180,fill=ACCENT,width=7)
            label('fördel',192,488,width=250,size=37)
            label('nackdel',568,488,width=250,size=37)
        elif name=='military':
            icon('people',198,245,1.1)
            document(564,245,'intyg',1.25)
            question(380,363)
            label('värnplikten i flera medborgarskapsstater',198,445,width=300,size=28)
            label('fullgjord värnplikt i ett land',564,445,width=310,size=28)
            label('ta reda på',380,76,size=37)
        elif name=='child':
            icon('person',380,439,.72)
            document(193,201,'finskt',1)
            document(567,201,'annat land',1)
            d.line((193,329,380,405,567,329),fill=SECOND,width=6)
            label('Barnet kan ha',380,608,size=38)
        elif name=='child_condition':
            document(210,218,'finskt',1)
            document(552,218,'annat land',1)
            d.rounded_rectangle((138,408,622,506),radius=20,outline=ACCENT,width=6)
            label('det andra landet godkänner',380,432,width=460,size=28)
            icon('person',380,598,.64)
            arrow((380,361),(380,397))
            arrow((380,509),(380,538))
        elif name=='mission':
            icon('person',143,344,1.15)
            question(375,231)
            icon('bank',585,345,1.35)
            arrow((251,344),(463,344))
            label('beskickningen för ditt eget land',380,589,size=32)
        elif name=='age22':
            icon('person',160,288,1.2)
            label('22 år',160,475,width=260,size=40)
            document(550,223,'en annan stat',1)
            d.line((259,402,626,402),fill=SECOND,width=6)
            d.line((409,367,462,437),fill='#e8b3af',width=9)
            d.line((409,437,462,367),fill='#e8b3af',width=9)
            label('saknar tillräcklig anknytning till Finland',488,508,width=440,size=28)
        elif name=='false_info':
            document(380,317,'ansökan eller anmälan',1.8)
            d.polygon([(576,168),(651,303),(501,303)],outline='#e8b3af',width=7)
            d.text((576,256),'!',font=ImageFont.truetype(FONT,64),fill=ACCENT,anchor='mm')
            label('felaktiga eller vilseledande uppgifter',380,615,size=32)
        elif name in ('paternity','maternity'):
            parent_x,child_x=(175,589) if name=='paternity' else (585,171)
            icon('person',parent_x,275,1.15)
            icon('person',child_x,322,.72)
            d.line((parent_x+(-76 if parent_x>child_x else 76),322,
                    child_x+(56 if parent_x>child_x else -56),322),fill=SECOND,width=7)
            d.line((350,280,409,364),fill='#e8b3af',width=9)
            d.line((350,364,409,280),fill='#e8b3af',width=9)
            label('fadern' if name=='paternity' else 'icke-födande modern',parent_x,465,width=310,size=29)
            label('barnet',child_x,465,width=240,size=29)
            arrow((parent_x+(60 if parent_x<child_x else -60),355),(380,508))
            document(380,560,'',.57)
            label('finskt medborgarskap',380,608,width=400,size=24)
            basis=('på grund av faderns medborgarskap' if name=='paternity' else
                   'på grund av den icke-födande moderns finska medborgarskap')
            label(basis,380,650,width=700,size=26)
            label('faderskapet hävs' if name=='paternity' else 'moderskapet hävs',380,59,size=35)
        path=out/(name+'.png')
        im.save(path)
        row=script['sentences'][index]
        asset=dict(asset_id='picture_'+name,kind='foreground',visual_type='diagram',
                   files=[info(path)],creator='Homebrew video studio',
                   reuse_terms='Original schematic artwork under repository MIT license; source text retains publisher terms.',
                   required_credits='Original source-based pictorial diagram: Homebrew video studio. Source wording attribution in sources.yaml.',
                   relevance_verification=description+' Exact source: '+row['sentence_id']+'. Generic documents and unnamed states do not assert policies of real foreign countries.',
                   creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),
                      drawing_primitives='studio/episodes/hb-c07-ekonomi/prepare_foregrounds.py',
                      source_sentence_ids=[row['sentence_id']]))
        if kind=='photo':
            photo=evidence['foreground_photos'][name]
            pi=photo['imageinfo'][0];m=pi['extmetadata']
            clean=lambda key:re.sub('<[^>]+>','',m.get(key,{}).get('value','')).strip()
            asset.update(visual_type='photograph',source_url=pi['descriptionurl'],creator=clean('Artist'),
                         reuse_terms=clean('LicenseShortName')+' '+clean('LicenseUrl'),
                         required_credits=photo['title']+' — '+clean('Artist')+' · '+clean('LicenseShortName')+'. '+pi['descriptionurl']+' '+clean('LicenseUrl')+'. Proportionally resized; source license retained.',
                         relevance_verification=description+' Verified source identity: '+clean('ImageDescription')+'. Contextual object only, not a current passport-design claim or evidence about a named individual.')
        assets.append(asset)
    (EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
    print('Prepared15distinctpictures:2actualobjectphotographs and13conditional-source diagrams.')


if __name__=='__main__':
    main()
