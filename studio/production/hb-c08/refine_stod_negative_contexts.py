"""Author only the two source-bound Stod crisis/prohibited-harm illustrations."""
from pathlib import Path
import hashlib
import importlib.util
import json
import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
EP = ROOT / 'studio/episodes/hb-c08-stod'
OUT = ROOT / 'studio/media/hb-c08-stod/pictures'
spec = importlib.util.spec_from_file_location('education_primitives', Path(__file__).with_name('pictures.py'))
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)
script = yaml.load((EP / 'script.yaml').read_text(), Loader=yaml.CSafeLoader)
assert script['sentences'][86]['sv'] == 'Planen inkluderar skolans handlingsprinciper för plötsliga kriser och hotfulla och farliga situationer.'
assert script['sentences'][87]['sv'] == 'I skolorna accepteras inte diskriminering, mobbning, trakasserier eller våld.'

def canvas():
    image = Image.new('RGB', (760, 720), P.BG)
    draw = ImageDraw.Draw(image)
    draw.line((72, 62, 182, 62), fill=P.GOLD, width=5)
    draw.text((380, 675), 'Schematisk illustration',
              font=ImageFont.truetype(P.F, 22), fill=P.SOFT, anchor='mt')
    return image, draw

updates = {}
image, draw = canvas()
P.wrap(draw, 'Planen inkluderar', 380, 105, 650, 30)
P.icon(draw, 'hazard', 220, 300, 1.1)
P.icon(draw, 'document', 540, 300, 1.1)
draw.line((325, 300, 435, 300), fill=P.LINE, width=6)
P.wrap(draw, 'plötsliga kriser', 220, 440, 295, 31)
P.wrap(draw, 'skolans handlingsprinciper', 540, 440, 295, 31)
P.wrap(draw, 'hotfulla och farliga situationer', 380, 580, 660, 27)
updates['picture-087'] = (image, dict(composition='crisis_action_principles',
    nodes=[dict(label='plötsliga kriser', icon='hazard'),
           dict(label='skolans handlingsprinciper', icon='document')],
    qualifier='hotfulla och farliga situationer'),
    'Warning identifies crises/threats/danger; the document identifies the school action principles. No approving shield attached to harm.')

image, draw = canvas()
P.wrap(draw, 'I skolorna', 380, 100, 660, 30)
P.icon(draw, 'school', 380, 200, .7)
P.wrap(draw, 'accepteras inte', 380, 290, 660, 30)
P.icon(draw, 'children', 190, 425, .9)
P.icon(draw, 'child', 590, 425, 1.1)
# The prohibition crosses the harmful action/alert between pupils, never a person.
draw.line((295, 414, 475, 414), fill=P.GOLD, width=5)
draw.polygon([(475, 414), (459, 404), (459, 424)], fill=P.GOLD)
P.icon(draw, 'hazard', 380, 414, .62)
draw.ellipse((292, 326, 468, 502), outline=P.FG, width=6)
draw.line((318, 476, 442, 352), fill=P.FG, width=9)
P.wrap(draw, 'diskriminering, mobbning,', 380, 555, 660, 29)
P.wrap(draw, 'trakasserier eller våld', 380, 599, 660, 29)
updates['picture-088'] = (image, dict(composition='prohibited_harm_scene',
    nodes=[dict(label='I skolorna', icon='school'), dict(label='mobbning', icon='children'),
           dict(label='våld', icon='hazard', crossed=True), dict(label='', icon='child')],
    qualifier='accepteras inte'),
    'School and generic pupils contextualize harm. The crossed arrow/warning explicitly prohibits harmful action; pupils themselves are not crossed or excluded.')

plans = json.loads((EP / 'picture-plan.json').read_text())
assets = json.loads((EP / 'foreground-assets.json').read_text())
by_id = {row['asset_id']: row for row in assets}
for key, (image, plan, relevance) in updates.items():
    number = int(key[-3:])
    sentence = script['sentences'][number - 1]
    path = OUT / (key + '.png')
    image.save(path)
    plan['source_sentence_ids'] = [sentence['sentence_id']]
    plans[key] = plan
    record = by_id[key]
    record['files'] = [dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size,
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest())]
    record['relevance_verification'] = relevance + ' Exact full archived SV and reviewed RU remain beside the illustration.'
    record['creation_method'] = dict(tool=str(Path(__file__).relative_to(ROOT)),
                                   source_sentence_ids=[sentence['sentence_id']], composition=plan['composition'])
    sentence['visual_cue'] = relevance
(EP / 'picture-plan.json').write_text(json.dumps(plans, ensure_ascii=False, indent=2) + '\n')
(EP / 'foreground-assets.json').write_text(json.dumps(assets, ensure_ascii=False, indent=2) + '\n')
(EP / 'script.yaml').write_text(yaml.safe_dump(script, allow_unicode=True, sort_keys=False, width=100))
registry = yaml.load((EP / 'assets.yaml').read_text(), Loader=yaml.CSafeLoader)
registry['assets'] = [by_id[row['asset_id']] if row['asset_id'] in updates else row
                      for row in registry['assets']]
(EP / 'assets.yaml').write_text(yaml.safe_dump(registry, allow_unicode=True, sort_keys=False, width=100))
print('Only Stod087/088 source-bound pictures and their exact asset records updated; narration untouched.')
