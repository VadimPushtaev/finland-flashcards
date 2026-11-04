"""Prepare three contextual photographs and seven source-specific process diagrams."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re

from PIL import Image, ImageDraw, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parent
MEDIA = ROOT / 'studio/media' / EP.name
SPEC = importlib.util.spec_from_file_location(
    'studio_pictorial_primitives',
    ROOT / 'studio/episodes/hb-c07-ekonomi/prepare_foregrounds.py')
PRIMITIVES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRIMITIVES)
PRIMITIVES.BG = '#243c32'
PRIMITIVES.PANEL = '#304d40'
PRIMITIVES.TEXT = '#faf3e8'
PRIMITIVES.SECOND = '#c5dfce'
PRIMITIVES.ACCENT = '#e3c58c'
PRIMITIVES.LINE = '#4d7560'
BG, FG, ACCENT, SECOND = PRIMITIVES.BG, PRIMITIVES.TEXT, PRIMITIVES.ACCENT, PRIMITIVES.SECOND
FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'


def info(path):
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    evidence = json.loads((EP / 'media-sources.json').read_text())
    script = yaml.safe_load((EP / 'script.yaml').read_text())
    plans = json.loads((EP / 'picture-plan.json').read_text())
    out = MEDIA / 'pictures'
    out.mkdir(parents=True, exist_ok=True)
    assets = []
    for index, (name, title, kind, description) in enumerate(plans):
        im = Image.new('RGB', (760, 720), BG)
        d = ImageDraw.Draw(im)

        def icon(kind, x, y, scale=1):
            PRIMITIVES.icon(d, kind, x, y, scale)

        def label(text, x, y, width=650, size=31):
            return PRIMITIVES.wrapped(d, text, x, y, width, size=size, color=FG, bold=True)

        def arrow(x1, y1, x2, y2):
            d.line((x1,y1,x2,y2), fill=ACCENT, width=7)
            if y1 == y2:
                d.polygon([(x2,y2),(x2-20,y2-13),(x2-20,y2+13)],fill=ACCENT)
            else:
                d.polygon([(x2,y2),(x2-13,y2-20),(x2+13,y2-20)],fill=ACCENT)

        def moving_boxes(x, y):
            for dx,dy in [(-50,25),(47,25),(0,-66)]:
                d.rectangle((x+dx-47,y+dy-36,x+dx+41,y+dy+42),outline=FG,width=5)
                d.line((x+dx-6,y+dy-35,x+dx-6,y+dy+42),fill=ACCENT,width=5)

        def finland(x,y):
            d.rectangle((x-65,y-40,x+65,y+40),fill='#f4f4ec')
            d.rectangle((x-21,y-40,x-2,y+40),fill='#194c85')
            d.rectangle((x-65,y-8,x+65,y+9),fill='#194c85')

        def crossed_document(x,y,scale=.8):
            icon('document',x,y,scale)
            d.line((x-64*scale,y+80*scale,x+64*scale,y-80*scale),fill='#e3b29e',width=9)

        if kind == 'photo':
            photo = Image.open(MEDIA/'sources'/('foreground-'+name+'.jpg')).convert('RGB')
            photo.thumbnail((760,720),Image.Resampling.LANCZOS)
            im.paste(photo,((760-photo.width)//2,(720-photo.height)//2))
        elif name == 'declaration':
            label('utanför EU:s tull- och skatteområde',380,45,size=30)
            moving_boxes(145,275)
            arrow(260,275,339,275)
            icon('document',415,275,1.1)
            arrow(493,275,570,275)
            finland(653,275)
            label('tulldeklaration',412,435,width=320,size=32)
            label('flyttsakerna',145,435,width=250,size=29)
            label('Finland',650,435,width=200,size=29)
        elif name == 'deadline':
            moving_boxes(160,250)
            icon('calendar',540,250,1.5)
            d.line((115,492,650,492),fill=SECOND,width=6)
            for x in (115,650):
                d.ellipse((x-13,479,x+13,505),fill=ACCENT)
            arrow(230,492,535,492)
            label('flyttningen',160,555,width=280,size=30)
            label('inom 12 månader',526,555,width=350,size=32)
        elif name in ('inside','car_inside'):
            label('inom EU:s tull- och skatteområde',380,50,size=30)
            d.rounded_rectangle((55,160,705,565),radius=36,outline=SECOND,width=5)
            if name=='inside':
                moving_boxes(202,325)
                label('flyttsakerna',205,465,width=280,size=30)
            else:
                icon('car',202,320,1.2)
                label('bil',205,465,width=280,size=32)
            crossed_document(535,325,1.05)
            label('tulldeklaration' if name=='inside' else 'tullklarering',535,465,width=320,size=29)
        elif name == 'permit':
            label('inte har giltig registrering i ett EU- eller EES-land',380,45,size=28)
            icon('car',175,286,1.2)
            crossed_document(475,255,.85)
            arrow(175,415,175,507)
            icon('document',175,594,.75)
            label('förflyttningstillstånd',469,561,width=410,size=31)
        elif name == 'insurance':
            icon('shield',380,300,2.35)
            icon('car',380,300,1.05)
            finland(380,575)
            label('trafikförsäkring',380,64,size=40)
            label('giltig i Finland',380,650,size=34)
        elif name == 'notification':
            icon('car',145,240,1.1)
            arrow(260,245,350,245)
            icon('document',430,245,1.05)
            arrow(430,370,430,449)
            icon('bank',430,552,1.15)
            label('anmälan om ibruktagande',380,61,size=33)
            label('Skatteförvaltningen',430,665,width=620,size=34)
        path = out/(name+'.png')
        im.save(path)
        row = script['sentences'][index]
        asset = dict(asset_id='picture_'+name, kind='foreground', visual_type='diagram',
                     files=[info(path)], creator='Homebrew video studio',
                     reuse_terms='Original schematic artwork under repository MIT license; source text retains publisher terms.',
                     required_credits='Original source-based schematic: Homebrew video studio. Text source attribution in sources.yaml.',
                     relevance_verification=description+' Source: '+row['sentence_id']+'. No inferred monetary amounts,country membership or additional legal conditions.',
                     creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)),
                                          drawing_primitives='studio/episodes/hb-c07-ekonomi/prepare_foregrounds.py',
                                          source_sentence_ids=[row['sentence_id']]))
        if kind=='photo':
            photo=evidence['foreground_photos'][name]
            pi=photo['imageinfo'][0]
            m=pi['extmetadata']
            clean=lambda key:re.sub('<[^>]+>','',m.get(key,{}).get('value','')).strip()
            asset.update(visual_type='photograph',source_url=pi['descriptionurl'],
                         creator=clean('Artist'),reuse_terms=clean('LicenseShortName')+' '+clean('LicenseUrl'),
                         required_credits=photo['title']+' — '+clean('Artist')+' · '+clean('LicenseShortName')+'. '+pi['descriptionurl']+' '+clean('LicenseUrl')+'. Proportionally resized; source license retained.',
                         relevance_verification=description+' Verified identity: '+clean('ImageDescription')+'. Contextual photograph, not evidence of a customs decision,current crossing availability or a pictured vehicle being imported.')
        assets.append(asset)
    (EP/'foreground-assets.json').write_text(json.dumps(assets,ensure_ascii=False,indent=2)+'\n')
    print('Prepared ten distinct foreground pictures:3photos,7process diagrams.')


if __name__=='__main__':
    main()
