"""Draw source-based pictorial diagrams; no photographed identity or added legal claim."""
from pathlib import Path
import hashlib, json, sys, yaml
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parent
SID = EP.name
BG = '#39252b'
FG = '#faf3e8'
MUT = '#e2c8cf'
GOLD = '#dfbd82'
LINE = '#70515a'
FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'

def main():
    script = yaml.safe_load((EP / 'script.yaml').read_text())
    assets = [a for a in json.loads((EP / 'foreground-assets.json').read_text()) if a.get('visual_type') == 'photograph'] if (EP / 'foreground-assets.json').exists() else []
    keys = list(dict.fromkeys((r['render_image'].split('/')[-1].removesuffix('.png') for r in script['sentences'] if r.get('render_image') and r['render_image'].endswith('.png'))))
    for key in keys:
        im = Image.new('RGB', (760, 720), BG)
        d = ImageDraw.Draw(im)

        def line(points, fill=FG, width=6):
            d.line(points, fill=fill, width=width)

        def text(x, y, t, size=30, fill=FG):
            while d.textlength(t, font=ImageFont.truetype(FONT, size)) > 680:
                size -= 1
            d.text((x, y), t, font=ImageFont.truetype(FONT, size), fill=fill, anchor='mm')

        def person(x, y, color=FG, scale=1):
            r = 19 * scale
            d.ellipse((x - r, y - r, x + r, y + r), fill=color)
            line([(x, y + 26 * scale), (x, y + 105 * scale)], color, int(12 * scale))
            line([(x - 32 * scale, y + 55 * scale), (x + 32 * scale, y + 55 * scale)], color, int(9 * scale))
            line([(x, y + 100 * scale), (x - 25 * scale, y + 150 * scale)], color, int(9 * scale))
            line([(x, y + 100 * scale), (x + 25 * scale, y + 150 * scale)], color, int(9 * scale))

        def arrow(a, b, color=GOLD):
            import math
            line([a, b], color, 7)
            angle = math.atan2(b[1] - a[1], b[0] - a[0])
            p1 = (b[0] - 19 * math.cos(angle - 0.5), b[1] - 19 * math.sin(angle - 0.5))
            p2 = (b[0] - 19 * math.cos(angle + 0.5), b[1] - 19 * math.sin(angle + 0.5))
            d.polygon([b, p1, p2], fill=color)

        def building(x, y, label):
            d.polygon([(x - 70, y), (x, y - 40), (x + 70, y)], outline=GOLD, width=5)
            for xx in [x - 45, x, x + 45]:
                line([(xx, y + 10), (xx, y + 100)], FG, 8)
            line([(x - 70, y + 110), (x + 70, y + 110)], FG, 8)
            text(x, y + 145, label, 24)

        def document(x, y, width=120):
            d.rounded_rectangle((x - width / 2, y, x + width / 2, y + 150), radius=7, outline=FG, width=5)
            for yy in range(y + 30, y + 130, 25):
                line([(x - width / 2 + 20, yy), (x + width / 2 - 20, yy)], MUT, 4)

        def speech(x, y):
            d.rounded_rectangle((x - 65, y - 38, x + 65, y + 38), radius=14, outline=GOLD, width=5)
            line([(x - 25, y + 38), (x - 40, y + 61), (x + 8, y + 38)], GOLD, 5)
        titles = {'equality': 'Likabehandling', 'opportunities': 'studera · arbeta · tjänster', 'barriers': 'Diskriminering', 'support': 'stöd', 'work': 'arbetsförhållanden', 'recruitment': 'meriterna för uppgiften', 'consent': 'ditt medgivande', 'hatecrime': 'brott · motiv', 'structures': 'praxis · strukturer · regler', 'interaction': 'interaktion', 'stress': 'minoritetsstress', 'police': 'polisen', 'contact': 'kontakta', 'advice': 'anvisningar · råd', 'workhelp': 'arbetsplatsen'}
        text(380, 70, titles[key], 36, GOLD)
        line([(50, 110), (710, 110)], LINE, 3)
        if key == 'equality':
            line([(380, 230), (380, 500)], GOLD, 10)
            line([(200, 290), (560, 290)], GOLD, 8)
            d.polygon([(320, 530), (440, 530), (380, 480)], fill=GOLD)
            for x in [220, 540]:
                line([(x, 290), (x - 85, 420), (x + 85, 420), (x, 290)], FG, 5)
                person(x, 310, MUT, 0.52)
            text(380, 590, 'lika mycket värda', 30)
        elif key == 'opportunities':
            person(380, 200)
            arrow((330, 370), (170, 440))
            arrow((380, 370), (380, 440))
            arrow((430, 370), (590, 440))
            document(170, 460, 100)
            d.rounded_rectangle((330, 480, 430, 565), radius=9, outline=FG, width=5)
            line([(360, 480), (360, 460), (400, 460), (400, 480)], FG, 5)
            building(590, 480, 'tjänster')
            text(170, 650, 'studera', 23)
            text(380, 650, 'arbeta', 23)
        elif key == 'barriers':
            person(190, 220)
            person(570, 220)
            arrow((190, 400), (190, 530))
            arrow((570, 400), (570, 530))
            line([(90, 550), (290, 550)], GOLD, 8)
            line([(475, 470), (665, 470)], MUT, 17)
            line([(475, 550), (665, 550)], GOLD, 8)
            text(380, 620, 'sämre ställning', 30)
        elif key == 'support':
            person(205, 250)
            person(550, 200)
            line([(80, 490), (310, 490)], FG, 8)
            line([(430, 450), (665, 450)], FG, 8)
            d.rectangle((455, 450, 645, 515), outline=GOLD, width=6)
            arrow((205, 530), (550, 530))
            text(380, 600, 'samma möjligheter', 30)
        elif key in ['work', 'recruitment', 'consent']:
            if key == 'work':
                person(200, 230)
                person(560, 230)
                d.rounded_rectangle((110, 440, 650, 500), radius=8, outline=GOLD, width=6)
                line([(155, 500), (155, 590)], FG, 6)
                line([(605, 500), (605, 590)], FG, 6)
                document(380, 250, 125)
            elif key == 'recruitment':
                for x in [180, 380, 580]:
                    person(x, 230, MUT, 0.7)
                    document(x, 400, 120)
                line([(350, 580), (375, 605), (425, 555)], GOLD, 9)
            else:
                person(180, 260)
                person(580, 260)
                speech(380, 260)
                arrow((250, 420), (510, 420))
                line([(350, 475), (375, 500), (425, 450)], GOLD, 9)
                text(380, 590, 'tillstånd', 30)
        elif key == 'hatecrime':
            d.rounded_rectangle((120, 320, 640, 450), radius=28, outline=FG, width=7)
            d.polygon([(220, 320), (265, 240), (490, 240), (545, 320)], outline=FG, width=7)
            for x in [230, 540]:
                d.ellipse((x - 37, 420, x + 37, 494), fill=BG, outline=GOLD, width=7)
            line([(380, 245), (353, 280), (387, 285), (365, 320)], GOLD, 6)
            speech(560, 180)
            text(380, 570, 'skadegörelse', 30)
        elif key == 'structures':
            for x, label in [(170, 'utbildning'), (380, 'arbetslivet'), (590, 'tjänster')]:
                building(x, 230, label)
            line([(170, 410), (590, 410)], LINE, 7)
            line([(380, 410), (380, 470)], LINE, 7)
            for x in [250, 380, 510]:
                person(x, 490, MUT, 0.6)
        elif key == 'interaction':
            person(200, 300)
            person(560, 300)
            speech(360, 250)
            line([(320, 250), (400, 250)], MUT, 4)
            line([(337, 233), (380, 267)], GOLD, 5)
            text(380, 580, 'ord · gester · utestängning', 27)
        elif key == 'stress':
            person(380, 360, MUT, 1.2)
            for x, y in [(200, 250), (560, 250), (380, 200)]:
                speech(x, y)
                arrow((x, y + 70), (380, 340), LINE)
            text(380, 620, 'välbefinnande', 30)
        elif key == 'police':
            person(190, 310)
            building(560, 300, 'polisen')
            arrow((270, 390), (460, 390))
            document(380, 470, 100)
        elif key in ['contact', 'advice', 'workhelp']:
            person(160, 300)
            arrow((235, 410), (440, 410))
            if key == 'contact':
                d.rounded_rectangle((465, 200, 605, 450), radius=20, outline=FG, width=7)
                line([(490, 240), (580, 240)], MUT, 5)
                d.ellipse((525, 410, 545, 430), outline=GOLD, width=4)
            elif key == 'advice':
                person(570, 300)
                speech(380, 250)
                document(380, 465, 100)
            else:
                person(550, 300)
                speech(380, 250)
                d.polygon([(560, 180), (625, 205), (615, 265), (560, 300), (505, 265), (495, 205)], outline=GOLD, width=6)
                line([(535, 235), (555, 255), (585, 215)], GOLD, 6)
        text(380, 687, 'Källbaserad illustration', 21, MUT)
        p = ROOT / 'studio/media' / SID / 'pictures' / f'{key}.png'
        p.parent.mkdir(parents=True, exist_ok=True)
        im.save(p)
        ids = [r['sentence_id'] for r in script['sentences'] if r.get('render_image') == str(p.relative_to(ROOT))]
        assets.append({'asset_id': 'picture_' + key, 'kind': 'foreground', 'visual_type': 'diagram', 'files': [{'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}], 'creator': 'Homebrew video studio', 'reuse_terms': 'Original source-based explanatory vector-style diagram; underlying source wording credited in sources.yaml.', 'required_credits': 'Source-based illustrative diagrams: Homebrew video studio.', 'relevance_verification': 'Schematic ' + key + ' illustration tied to exact source sentences ' + ', '.join(ids) + '. Anonymous geometric figures, no real person identity or added historical/legal claim. Caption explicitly identifies illustration.', 'creation_method': {'tool': str(Path(__file__).relative_to(ROOT)), 'design': 'Original Pillow line art, 760x720; source labels only'}})
    (EP / 'foreground-assets.json').write_text(json.dumps(assets, ensure_ascii=False, indent=2) + '\n')
    print(SID, len(assets), 'pictorial diagrams')
if __name__ == '__main__':
    main()
