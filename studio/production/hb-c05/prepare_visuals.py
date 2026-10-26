"""Draw source-based pictorial explanations and restore retained licensed photos."""
from pathlib import Path
import copy, hashlib, json, shutil, sys
import yaml
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[3]
OLD = Path('/home/vadim/finland-flashcards')
BG = '#39252b'
FG = '#faf3e8'
SOFT = '#e2c8cf'
GOLD = '#dfbd82'
LINE = '#70515a'
FONTS = '/usr/share/fonts/truetype/liberation/LiberationSans-'

def info(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)

def diagram(kind, p, slug):
    im = Image.new('RGB', (1000, 820), BG)
    d = ImageDraw.Draw(im)

    def line(points, fill=GOLD, width=9):
        d.line(points, fill=fill, width=width, joint='curve')

    def label(x, y, t, size=34):
        d.text((x, y), t, font=ImageFont.truetype(FONTS + 'Regular.ttf', size), fill=FG, anchor='mm')

    def person(x, y, s=1, c=SOFT):
        d.ellipse((x - 24 * s, y - 90 * s, x + 24 * s, y - 42 * s), fill=c)
        d.rounded_rectangle((x - 43 * s, y - 30 * s, x + 43 * s, y + 70 * s), radius=20 * s, outline=c, width=max(3, int(7 * s)))
        line([(x - 22 * s, y + 70 * s), (x - 25 * s, y + 139 * s)], c, int(8 * s))
        line([(x + 22 * s, y + 70 * s), (x + 25 * s, y + 139 * s)], c, int(8 * s))

    def arrow(a, b, c=GOLD):
        line([a, b], c)
        x, y = b
        dx, dy = (b[0] - a[0], b[1] - a[1])
        if abs(dx) > abs(dy):
            d.polygon([(x, y), (x - (22 if dx > 0 else -22), y - 14), (x - (22 if dx > 0 else -22), y + 14)], fill=c)
        else:
            d.polygon([(x, y), (x - 14, y - (22 if dy > 0 else -22)), (x + 14, y - (22 if dy > 0 else -22))], fill=c)

    def building(x, y, health=False):
        d.polygon([(x - 115, y - 80), (x, y - 135), (x + 115, y - 80)], outline=FG, width=7)
        d.rectangle((x - 100, y - 80, x + 100, y + 100), outline=FG, width=7)
        if health:
            d.rectangle((x - 12, y - 55, x + 12, y + 30), fill=GOLD)
            d.rectangle((x - 43, y - 24, x + 43, y), fill=GOLD)
        else:
            for xx in [x - 65, x, x + 65]:
                line([(xx, y - 60), (xx, y + 70)], SOFT, 13)
        line([(x - 122, y + 110), (x + 122, y + 110)], FG, 8)

    def book(x, y):
        d.polygon([(x, y - 60), (x - 110, y - 90), (x - 110, y + 80), (x, y + 110), (x + 110, y + 80), (x + 110, y - 90)], outline=FG, width=7)
        line([(x, y - 60), (x, y + 110)], GOLD, 6)
        for yy in [-30, 0, 30]:
            line([(x - 85, y + yy), (x - 25, y + yy + 17)], SOFT, 4)
            line([(x + 25, y + yy + 17), (x + 85, y + yy)], SOFT, 4)

    def shield(x, y):
        d.polygon([(x - 110, y - 105), (x, y - 145), (x + 110, y - 105), (x + 100, y + 40), (x, y + 135), (x - 100, y + 40)], outline=GOLD, width=9)
    if kind in ('consent', 'autonomy'):
        person(270, 345)
        person(730, 345)
        d.rounded_rectangle((170, 180, 370, 530), radius=60, outline=LINE, width=5)
        d.rounded_rectangle((630, 180, 830, 530), radius=60, outline=LINE, width=5)
        arrow((400, 310), (590, 310))
        arrow((590, 420), (400, 420))
        d.rounded_rectangle((400, 160, 600, 240), radius=28, outline=GOLD, width=6)
        label(500, 200, '?')
        label(270, 620, 'Egna val')
        label(730, 620, 'Samtycke')
        label(500, 700, ('Kan tas tillbaka' if slug == 'sexualitet' else 'Barnets samtycke') if kind == 'consent' else 'Egen kropp')
    elif kind == 'family':
        person(240, 290)
        person(760, 290)
        person(500, 535, 0.7)
        arrow((300, 470), (430, 540))
        arrow((700, 470), (570, 540))
        label(500, 100, 'Föräldrar och barn')
        label(500, 750, 'Barnets religion')
    elif kind in ('belief', 'community'):
        person(500, 250)
        arrow((470, 410), (260, 510))
        arrow((530, 410), (740, 510))
        building(240, 610)
        d.ellipse((650, 520, 830, 700), outline=SOFT, width=8)
        label(500, 80, 'Religionsfrihet')
        label(240, 770, 'Gemenskap')
        label(740, 770, 'Eget val')
    elif kind == 'expression':
        for x in [250, 500, 750]:
            person(x, 430)
            d.rounded_rectangle((x - 85, 150, x + 85, 265), radius=25, outline=GOLD, width=6)
            d.polygon([(x - 25, 265), (x - 25, 300), (x + 15, 265)], fill=GOLD)
        label(500, 710, 'Synas och höras')
    elif kind == 'nature':
        for x, y in [(260, 350), (500, 270), (740, 350)]:
            line([(x, y + 60), (x, y + 220)], GOLD, 16)
            d.ellipse((x - 100, y - 90, x + 100, y + 100), outline=SOFT, width=8)
        line([(100, 650), (900, 650)], SOFT, 6)
        d.arc((340, 80, 440, 180), 190, 340, fill=FG, width=6)
        d.arc((440, 80, 540, 180), 200, 350, fill=FG, width=6)
        label(500, 740, 'Naturen och dess mångfald')
    elif kind in ('rights', 'equality', 'participation'):
        for x in [250, 500, 750]:
            person(x, 350, 1, c=FG if x == 500 else SOFT)
        line([(160, 540), (840, 540)], GOLD, 10)
        arrow((250, 610), (750, 610))
        arrow((750, 660), (250, 660))
        label(500, 110, 'Alla')
        label(500, 745, 'Lika rättigheter')
    elif kind in ('health', 'prescription'):
        person(230, 410)
        building(690, 400, True)
        arrow((340, 400), (530, 400))
        label(500, 100, 'Hälsovård')
        if kind == 'prescription':
            d.rounded_rectangle((410, 560, 600, 710), radius=10, outline=SOFT, width=5)
            label(505, 610, 'Recept', 28)
            line([(450, 650), (560, 650)], SOFT, 4)
        else:
            shield(690, 400)
    elif kind == 'privacy':
        person(230, 420)
        d.rounded_rectangle((500, 200, 770, 580), radius=22, outline=FG, width=7)
        for yy in [260, 310, 360]:
            line([(550, yy), (720, yy)], SOFT, 5)
        d.arc((585, 390, 685, 500), 180, 360, fill=GOLD, width=12)
        d.rounded_rectangle((570, 460, 700, 555), radius=12, fill=GOLD)
        label(500, 710, 'Konfidentiella uppgifter')
    elif kind in ('protection', 'report'):
        shield(300, 350)
        person(300, 350, 0.65)
        arrow((450, 360), (600, 360))
        building(760, 350, kind == 'protection')
        label(300, 610, 'Skydd')
        label(760, 610, 'Hjälp' if kind == 'protection' else 'Anmälan')
    elif kind in ('education', 'care', 'age'):
        person(230, 380)
        person(430, 435, 0.65)
        book(750, 400)
        arrow((500, 420), (595, 420))
        label(500, 110, 'Sexualundervisning' if slug == 'sexualitet' else 'Omsorg och lärande')
        label(500, 690, 'Åldersanpassad information' if slug == 'sexualitet' else 'Barn · Vuxna')
    elif kind in ('law', 'ballot'):
        building(280, 350)
        if kind == 'ballot':
            d.rectangle((620, 350, 830, 540), outline=SOFT, width=8)
            line([(650, 380), (800, 380)], GOLD, 7)
            d.polygon([(650, 190), (790, 225), (750, 365), (610, 330)], outline=FG, width=7)
            label(720, 660, 'Rösträtt')
        else:
            line([(720, 190), (720, 520)], GOLD, 10)
            line([(590, 270), (850, 270)], GOLD, 8)
            for x in [610, 830]:
                line([(x, 270), (x - 55, 380), (x + 55, 380), (x, 270)], SOFT, 5)
                d.arc((x - 55, 340, x + 55, 420), 0, 180, fill=SOFT, width=8)
            label(720, 660, 'Finlands lag')
    elif kind in ('passport', 'travel'):
        d.rounded_rectangle((140, 220, 400, 570), radius=18, fill='#733d4e', outline=GOLD, width=6)
        label(270, 300, 'PASS')
        d.ellipse((205, 350, 335, 480), outline=GOLD, width=5)
        line([(270, 350), (270, 480)], GOLD, 3)
        line([(205, 415), (335, 415)], GOLD, 3)
        arrow((450, 410), (620, 410))
        building(780, 390)
        label(500, 710, 'Medborgarskap')
    elif kind == 'service':
        person(500, 220)
        arrow((470, 385), (270, 450))
        arrow((530, 385), (730, 450))
        shield(250, 570)
        building(750, 570)
        label(250, 760, 'Beväringstjänst', 29)
        label(750, 760, 'Civiltjänst', 29)
    elif kind == 'timeline':
        label(500, 110, 'Källtextens graviditetsveckor', 36)
        line([(150, 430), (850, 430)], SOFT, 8)
        for x, t in [(190, '12+0'), (470, '12+1'), (800, '20+0')]:
            line([(x, 400), (x, 460)], GOLD, 8)
            label(x, 510, t, 40)
            d.rounded_rectangle((x - 60, 240, x + 60, 350), radius=8, outline=SOFT, width=5)
            line([(x - 60, 270), (x + 60, 270)], GOLD, 4)
        label(500, 625, 'Schematisk bild, ej skalenlig', 28)
        label(500, 700, 'Villkoren står i källtexten', 28)
    elif kind == 'statistics':
        label(500, 110, '2023', 46)
        for y, width, t in [(280, 600, '75 procent'), (450, 13, '1,6 procent')]:
            d.rounded_rectangle((150, y, 850, y + 70), radius=12, fill=LINE)
            d.rectangle((150, y, 150 + width, y + 70), fill=GOLD)
            label(500, y + 115, t, 34)
        label(500, 730, 'Källtextens uppgifter', 28)
    else:
        raise ValueError(kind)
    padded = Image.new('RGB', (1000, 948), BG)
    padded.paste(im, (0, 64))
    padded.save(p)

def main(slug):
    sid = 'hb-c05-' + slug
    ep = ROOT / 'studio/episodes' / sid
    media = ROOT / 'studio/media' / sid
    out = media / 'diagrams'
    out.mkdir(parents=True, exist_ok=True)
    d = yaml.safe_load((ep / 'script.yaml').read_text())
    assets = []
    downloads = []
    existing = ep / 'foreground-assets.json'
    if existing.exists():
        retained = json.loads(existing.read_text())
        for asset in retained:
            if asset['asset_id'] == 'source_diagrams':
                for file in asset['files']:
                    path = ROOT / file['path']
                    diagram(path.stem, path, slug)
                    file.update(info(path))
            else:
                for file in asset['files']:
                    path = ROOT / file['path']
                    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != file['sha256']:
                        raise ValueError('Restore pinned photograph before preparing visuals: ' + str(path))
        existing.write_text(json.dumps(retained, ensure_ascii=False, indent=2) + '\n')
        print(sid, 'restored diagrams; preserved curated photo assignments')
        return
    d['asset_requests'] = [a for a in d['asset_requests'] if not a['id'].startswith('picture_')]
    if slug == 'religion':
        d['sentences'][8].update(render_image=None, asset_ids=['episode_background'], visual_cue='Sole guardian exception: no two-parent decision diagram.')
        d['sentences'][11].update(render_image=None, asset_ids=['episode_background'], visual_cue='Adult religious choice: leave foreground open without child-consent labels.')
    if slug == 'skyldigheter':
        d['sentences'][7]['render_image'] = 'studio/media/' + sid + '/diagrams/nature.png'
        for row in d['sentences'][9:]:
            row.update(render_image=None, asset_ids=['episode_background'], visual_cue='Age-specific rights: keep foreground open rather than imply schooling.')
    if slug == 'sexualitet':
        for i in [28, 29, 30, 31]:
            d['sentences'][i]['render_image'] = 'studio/media/' + sid + '/diagrams/expression.png'
    if slug == 'reproduktion':
        d['sentences'][4].update(render_image='studio/media/' + sid + '/diagrams/health.png', asset_ids=['episode_background', 'source_diagrams'], visual_cue='Health-service oversight context; no misidentification of the judicial building as Valvira.')
    kinds = sorted({Path(r['render_image']).stem for r in d['sentences'] if '/diagrams/' in (r.get('render_image') or '')})
    for k in kinds:
        diagram(k, out / (k + '.png'), slug)
    assets.append(dict(asset_id='source_diagrams', kind='foreground', visual_type='diagram', files=[info(out / (k + '.png')) for k in kinds], creator='Homebrew video studio', reuse_terms='Original schematic illustrations, CC BY 4.0; source wording retains its recorded source terms.', required_credits='Original pictorial diagrams: Homebrew video studio. Source text attribution accompanies the video.', relevance_verification='Original non-anatomical schematic figures, institutions, objects and directional relationships explain only the adjacent archived source. They are not photographs, clinical illustrations, or evidence about identified people.', creation_method={'tool': str(Path(__file__).relative_to(ROOT)), 'kinds': kinds}))
    choices = {'religion': [('hb-c03-religion', 'episode_background', 'church', list(range(0, 6)))], 'sexualitet': [('hb-c04-foreningar', 'picture_workshop', 'education', [18, 19, 20]), ('hb-c04-demokrati', 'picture_court', 'court', [25, 38, 48, 55, 56, 60, 61, 62, 63])], 'reproduktion': [('hb-c04-demokrati', 'picture_court', 'court', [6])], 'skyldigheter': [('hb-c04-foreningar', 'picture_volunteers', 'volunteers', [5]), ('hb-c04-demokrati', 'picture_court', 'court', [0, 1, 6]), ('hb-c04-foreningar', 'picture_workshop', 'learning', [8])], 'medborgarskap': [('hb-c04-demokrati', 'picture_ballot', 'ballot', [4, 5, 9]), ('hb-c04-demokrati', 'picture_cabinet', 'cabinet', [6]), ('hb-c04-demokrati', 'picture_court', 'court', [13, 14])], 'forsvar': []}
    picdir = media / 'pictures'
    picdir.mkdir(exist_ok=True)
    for oldsid, assetid, key, indices in choices[slug]:
        oldasset = next((a for a in yaml.safe_load((ROOT / 'studio/episodes' / oldsid / 'assets.yaml').read_text())['assets'] if a['asset_id'] == assetid))
        a = copy.deepcopy(oldasset)
        f = a['files'][0]
        src = OLD / f['path']
        dest = picdir / (key + src.suffix)
        if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest() != f['sha256']:
            assert hashlib.sha256(src.read_bytes()).hexdigest() == f['sha256']
            shutil.copyfile(src, dest)
        a.update(asset_id='picture_' + key, kind='foreground', visual_type='photograph', files=[info(dest)])
        a['required_credits'] = a['required_credits'].replace('Cropped, darkened, blurred and pan/zoom adapted; photograph adaptation retains', 'Steady foreground photograph, proportionally resized and cropped to fit; photograph adaptation retains')
        a['relevance_verification'] += ' Here shown as a contextual foreground photograph; no personal status inferred.'
        assets.append(a)
        manifest = yaml.safe_load((ROOT / 'studio/runtime' / (oldsid + '-downloads.yaml')).read_text())
        entry = next((x for x in manifest['downloads'] if x['sha256'] == f['sha256']))
        downloads.append(dict(info(dest), url=entry['url']))
        d['asset_requests'].append(dict(id=a['asset_id'], kind='foreground', description=a['relevance_verification'], fallback='Use a source-based diagram and document missing photo.'))
        for i in indices:
            r = d['sentences'][i]
            r.update(render_image=str(dest.relative_to(ROOT)), asset_ids=['episode_background', a['asset_id']], visual_cue=a['relevance_verification'], render_caption=False)
    if slug in ('sexualitet', 'reproduktion'):
        other = 'reproduktion' if slug == 'sexualitet' else 'sexualitet'
        src = ROOT / 'studio/media' / ('hb-c05-' + other) / 'sources/background.jpg'
        e = json.loads((ROOT / 'studio/episodes' / ('hb-c05-' + other) / 'media-sources.json').read_text())
        pi = e['photo']
        dest = picdir / 'health-centre.jpg'
        Image.open(src).verify()
        shutil.copyfile(src, dest)
        import re
        clean = lambda k: re.sub('<[^>]*>', '', pi['extmetadata'].get(k, {}).get('value', '')).strip()
        a = dict(asset_id='picture_health', kind='foreground', visual_type='photograph', files=[info(dest)], source_url=pi['descriptionurl'], creator=clean('Artist'), reuse_terms=clean('LicenseShortName') + ' ' + clean('LicenseUrl'), required_credits=e['photo_title'] + ' — ' + clean('Artist') + ' · ' + clean('LicenseShortName') + '. ' + pi['descriptionurl'] + ' ' + clean('LicenseUrl') + '. Proportionally resized; original license retained.', relevance_verification=e['context'])
        assets.append(a)
        downloads.append(dict(info(dest), url=pi['download_url']))
        d['asset_requests'].append(dict(id=a['asset_id'], kind='foreground', description=e['context'], fallback='Use original source-based health-services diagram.'))
        indices = [9, 23, 26, 27, 32] if slug == 'sexualitet' else [1, 2, 8, 9, 11, 14, 15, 16, 17, 20, 23, 25, 26, 27, 28, 33, 35, 36, 37]
        for i in indices:
            d['sentences'][i].update(render_image=str(dest.relative_to(ROOT)), asset_ids=['episode_background', 'picture_health'], visual_cue=e['context'], render_caption=False)
    if slug == 'forsvar':
        for name, indices in [('conscripts', [3, 4, 14, 15]), ('civil-service', [2, 5])]:
            e = json.loads((ep / (name + '-source.json')).read_text())
            pi = e['photo']
            dest = media / 'sources' / (name + '.jpg')
            import re
            clean = lambda k: re.sub('<[^>]*>', '', pi['extmetadata'].get(k, {}).get('value', '')).strip()
            context = clean('ImageDescription') + ' Contextual actual service photograph, not a depiction of the numerical statistics or the current eligibility rules.'
            a = dict(asset_id='picture_' + name, kind='foreground', visual_type='photograph', files=[info(dest)], source_url=pi['descriptionurl'], creator=clean('Artist'), reuse_terms=clean('LicenseShortName') + ' ' + clean('LicenseUrl'), required_credits=e['title'] + ' — ' + clean('Artist') + ' · ' + clean('LicenseShortName') + '. ' + pi['descriptionurl'] + ' ' + clean('LicenseUrl') + '. Proportionally resized; original terms retained.', relevance_verification=context)
            assets.append(a)
            downloads.append(dict(info(dest), url=pi['download_url']))
            d['asset_requests'].append(dict(id=a['asset_id'], kind='foreground', description=context, fallback='Use source-based service-path diagram.'))
            for i in indices:
                d['sentences'][i].update(render_image=str(dest.relative_to(ROOT)), asset_ids=['episode_background', a['asset_id']], visual_cue=context, render_caption=False)
    if slug == 'medborgarskap':
        old = json.loads((ep / 'passport-source.json').read_text())
        pi = old['photo']
        dest = media / 'sources/passport.jpg'
        import re
        clean = lambda k: re.sub('<[^>]*>', '', pi['extmetadata'].get(k, {}).get('value', '')).strip()
        context = 'Dated 2007 Finnish passport specimen, used solely to illustrate the right to a Finnish passport; not a representation of the current design.'
        a = dict(asset_id='picture_passport', kind='foreground', visual_type='photograph', files=[info(dest)], source_url=pi['descriptionurl'], creator=clean('Artist'), reuse_terms=clean('LicenseShortName') + ' ' + clean('LicenseUrl'), required_credits=old['photo_title'] + ' — ' + clean('Artist') + ' · ' + clean('LicenseShortName') + '. ' + pi['descriptionurl'] + ' ' + clean('LicenseUrl') + '. Original specimen photograph proportionally resized.', relevance_verification=context)
        assets.append(a)
        downloads.append(dict(info(dest), url=pi['download_url']))
        d['asset_requests'].append(dict(id=a['asset_id'], kind='foreground', description=context, fallback='Use original passport diagram.'))
        for i in [0, 1, 2, 3]:
            d['sentences'][i].update(render_image=str(dest.relative_to(ROOT)), asset_ids=['episode_background', 'picture_passport'], visual_cue=context, render_caption=False)
        for i in [7, 8]:
            d['sentences'][i].update(render_image=None, asset_ids=['episode_background'], visual_cue='Leave left foreground open to the actual Finnish embassy background; no generic courthouse is used for EU movement or consular assistance.', render_caption=False)
    (ep / 'foreground-assets.json').write_text(json.dumps(assets, ensure_ascii=False, indent=2) + '\n')
    (ep / 'foreground-downloads.json').write_text(json.dumps(downloads, ensure_ascii=False, indent=2) + '\n')
    (ep / 'script.yaml').write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100))
    helper = (ROOT / 'studio/episodes/hb-c04-foreningar/prepare_assets.py').read_text().replace('[photoasset, cardsasset, *pictures, musicasset, narrationasset]', '[photoasset, *pictures, musicasset, narrationasset]').replace("'#382d24'", "'#39252b'").replace("'#dfb96f'", "'#dfbd82'")
    (ep / 'prepare_assets.py').write_text(helper)
    print(sid, len(kinds), 'diagrams', len(assets) - 1, 'photos')
if __name__ == '__main__':
    for slug in sys.argv[1:]:
        main(slug)
