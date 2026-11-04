"""Prepare five distinct source-backed consumer diagrams and one shopping photo."""
from pathlib import Path
import hashlib
import json
import re

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parent
MEDIA = ROOT / 'studio/media' / EP.name
BG, INK, ACCENT, SECOND = '#243c32', '#faf3e8', '#e3c58c', '#c5dfce'
FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'


def file_info(path):
    return dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    script = yaml.safe_load((EP / 'script.yaml').read_text())
    evidence = json.loads((EP / 'media-sources.json').read_text())
    out = MEDIA / 'pictures'
    out.mkdir(parents=True, exist_ok=True)
    assets = []
    names = ['buying', 'protection', 'defect', 'remedies', 'seller', 'advice']
    for index, name in enumerate(names):
        canvas = Image.new('RGB', (760, 720), BG)
        d = ImageDraw.Draw(canvas)

        def line(points, color=ACCENT, width=7):
            d.line(points, fill=color, width=width, joint='curve')

        def box(xy, color=ACCENT, radius=16, width=6):
            d.rounded_rectangle(xy, radius=radius, outline=color, width=width)

        def label(text, xy, size=35, color=INK):
            d.text(xy, text, font=ImageFont.truetype(BOLD, size), fill=color, anchor='mm')

        def arrow(start, end):
            line([start, end])
            x, y = end
            d.polygon([(x, y), (x-22, y-14), (x-22, y+14)], fill=ACCENT)

        def person(cx, cy, color=SECOND):
            d.ellipse((cx-28, cy-28, cx+28, cy+28), outline=color, width=6)
            d.arc((cx-61, cy+35, cx+61, cy+169), 180, 360, fill=color, width=7)
            line([(cx-61, cy+102), (cx-61, cy+153), (cx+61, cy+153), (cx+61, cy+102)], color)

        def kettle(cx, cy, broken=False, size=1):
            def pt(x, y):
                return cx + x*size, cy + y*size
            d.rounded_rectangle((*pt(-76, -49), *pt(58, 84)), radius=22,
                                outline=INK, width=6)
            line([pt(-61, -49), pt(-61, -76), pt(35, -76), pt(35, -49)], INK)
            d.arc((*pt(34, -47), *pt(107, 55)), 240, 120, fill=ACCENT, width=8)
            line([pt(-76, -25), pt(-116, -63), pt(-95, 16), pt(-76, 32)], INK)
            line([pt(-84, 96), pt(67, 96)], SECOND)
            if broken:
                line([pt(-5, -36), pt(-29, -1), pt(4, 13), pt(-19, 54)], '#edb3a0', 8)

        if name == 'buying':
            photo = Image.open(MEDIA / 'sources/foreground-shopping.jpg').convert('RGB')
            photo.thumbnail((760, 720), Image.Resampling.LANCZOS)
            canvas.paste(photo, ((760-photo.width)//2, (720-photo.height)//2))
        elif name == 'protection':
            # A legal document within a shield shows protection, not extra rules.
            d.polygon([(380,100),(610,181),(584,417),(509,531),(380,617),
                       (251,531),(176,417),(150,181)], outline=ACCENT, width=9)
            box((281,220,479,468), INK)
            for y in (275,318,361,404):
                line([(313,y),(447,y)], SECOND, 5)
            label('Konsumentskyddslagen', (380,54), 34)
            label('rättigheter', (380,664), 35)
        elif name == 'defect':
            kettle(380,330,broken=True,size=1.8)
            label('varan', (380,106), 42)
            label('fel som inte du har orsakat', (380,628), 34)
        elif name == 'remedies':
            kettle(147,322,broken=True,size=.8)
            line([(255,330),(320,330),(320,195),(396,195)])
            line([(320,330),(320,478),(398,478)])
            arrow((344,195),(398,195))
            arrow((344,478),(398,478))
            kettle(526,195,size=.8)
            label('felfri vara', (541,324), 34)
            for k in range(3):
                d.ellipse((452+38*k,450-10*k,523+38*k,486-10*k), outline=ACCENT, width=6)
            label('pengar tillbaka', (535,554), 34)
        elif name == 'seller':
            person(161,352)
            person(586,352)
            box((66,181,320,300), INK)
            d.polygon([(231,298),(264,329),(269,298)], outline=INK, width=5)
            kettle(194,240,broken=True,size=.39)
            box((462,293,699,326), ACCENT, radius=5)
            line([(491,328),(491,563),(670,563),(670,328)], ACCENT)
            arrow((334,249),(445,249))
            label('först kontakt säljaren', (380,639), 35)
        elif name == 'advice':
            # Consumer, unresolved discussion, then an advice call.
            person(120,372)
            box((245,173,517,312), SECOND)
            line([(288,221),(471,221)], SECOND, 5)
            line([(288,259),(443,259)], SECOND, 5)
            line([(381,332),(381,389)], ACCENT)
            d.polygon([(381,414),(365,386),(397,386)], fill=ACCENT)
            box((310,438,452,612), INK)
            line([(348,469),(415,469)], SECOND, 4)
            d.ellipse((370,577,393,600), outline=SECOND, width=4)
            d.arc((546,399,644,500), 200, 338, fill=ACCENT, width=10)
            box((540,438,560,481), ACCENT, 5)
            box((627,438,647,481), ACCENT, 5)
            label('konsumentrådgivningen', (380,663), 33)
        path = out / (name + '.png')
        canvas.save(path)
        row = script['sentences'][index]
        asset = dict(asset_id='picture_'+name, kind='foreground', visual_type='diagram',
                     files=[file_info(path)], creator='Homebrew video studio',
                     reuse_terms='Original schematic artwork, repository MIT license; source text retains publisher terms.',
                     required_credits='Original schematic artwork: Homebrew video studio. Source text credits in sources.yaml.',
                     relevance_verification='Distinct pictorial composition visualizes only the relationships in '+row['sentence_id']+'. No added legal rules, sums or deadlines.',
                     creation_method=dict(tool=str(Path(__file__).relative_to(ROOT)), source_sentence_ids=[row['sentence_id']]))
        if name == 'buying':
            photo = evidence['foreground_photo']
            info = photo['imageinfo'][0]
            metadata = info['extmetadata']
            clean = lambda key: re.sub('<[^>]+>', '', metadata.get(key, {}).get('value', '')).strip()
            asset.update(visual_type='photograph', source_url=info['descriptionurl'],
                         creator=clean('Artist'), reuse_terms=clean('LicenseShortName')+' '+clean('LicenseUrl'),
                         required_credits=photo['title']+' — '+clean('Artist')+' · '+clean('LicenseShortName')+'. '+info['descriptionurl']+' '+clean('LicenseUrl')+'. Proportionally resized; license retained.',
                         relevance_verification='Verified Ratina shopping-centre interior in Tampere, Finland, illustrates the shopping context; not evidence about any individual consumer. '+clean('ImageDescription'))
        assets.append(asset)
    (EP / 'foreground-assets.json').write_text(json.dumps(assets, ensure_ascii=False, indent=2)+'\n')
    print('Prepared six distinct foreground pictures; source semantics require visual review.')


if __name__ == '__main__':
    main()
