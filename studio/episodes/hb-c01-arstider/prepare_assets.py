"""Rebuild this episode's source-based fact cards and hash its acquired assets.

Run after fetch_assets.py on the episode download manifest and the shared local
F1 narration command. Does not download, synthesize, approve, or render anything.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[3]
EPISODE = Path(__file__).resolve().parent
SECTION = EPISODE.name
MEDIA = ROOT / 'studio/media' / SECTION
CLIMATE = SECTION.endswith('arstider')


def file_record(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--graphics-only', action='store_true')
    args = parser.parse_args()
    script = yaml.safe_load((EPISODE / 'script.yaml').read_text())
    graphics = MEDIA / 'graphics'
    graphics.mkdir(parents=True, exist_ok=True)
    generated = []
    for key, labels in script['fact_cards'].items():
        image = Image.new('RGB', (1520, 1440), '#102e2b')
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((35, 35, 1485, 1405), radius=30, outline='#48675e', width=3)
        draw.line((120, 135, 330, 135), fill='#e7bc70', width=8)
        size = 90 if len(labels) <= 3 else 72
        while True:
            face = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', size)
            if max(face.getlength(line) for line in labels) <= 1280:
                break
            size -= 1
        gap = min(165, 1040 // len(labels))
        y = 720 - (len(labels) - 1) * gap / 2
        for i, line in enumerate(labels):
            draw.text((760, y + i * gap), line, font=face, fill='#e7bc70' if any(c.isdigit() for c in line) else '#f6f1e6', anchor='mm')
        path = graphics / (key + '.png')
        image.save(path)
        generated.append(file_record(path))
    if args.graphics_only:
        print(SECTION, len(generated), 'source-based graphics')
        return
    downloads = yaml.safe_load((ROOT / 'studio/runtime' / (SECTION + '-downloads.yaml')).read_text())['downloads']
    music = json.loads((EPISODE / 'music-source.json').read_text())['catalog_record']
    photo_url = 'https://commons.wikimedia.org/wiki/File:Snowy_forest_in_Vuosaari.jpg' if CLIMATE else 'https://commons.wikimedia.org/wiki/File:Helsinki_panorama.jpg'
    photo_title = 'Snowy forest in Vuosaari' if CLIMATE else 'Helsinki panorama'
    creator = 'JIP' if CLIMATE else 'DIMMIS'
    license_url = 'https://creativecommons.org/licenses/by-sa/4.0/' if CLIMATE else 'https://creativecommons.org/licenses/by-sa/3.0/'
    license_name = 'CC BY-SA 4.0' if CLIMATE else 'CC BY-SA 3.0'
    assets = [dict(asset_id='background',kind='background',status='ready',file_path=str((MEDIA/'sources/background.jpg').relative_to(ROOT)),files=[file_record(MEDIA/'sources/background.jpg')],source_url=photo_url,creator=creator,reuse_terms=license_name+' — '+license_url,required_credits=f'{photo_title} — {creator}, {license_name}, via Wikimedia Commons. {photo_url}. Cropped, softened, darkened and continuously panned/zoomed in this video; adapted photograph retains its share-alike license.',relevance_verification='Commons photographer-uploaded description verifies '+('a snowy forest in Vuosaari, Helsinki, on 10 December 2022. Decorative topic illustration; not used as evidence for northern climate or historical weather.' if CLIMATE else 'view of Helsinki from Olympiastadion tower, May 2010. Decorative city illustration; not a statistical population map or historical urbanisation image.')),dict(asset_id='fact_cards',kind='foreground',status='ready',file_path=generated[0]['path'],files=generated,source_url=script['source_path'],creation_method=f'studio/episodes/{SECTION}/prepare_assets.py; Pillow typography based only on script fact_cards',creator='Studio typography; facts from episode source passages',reuse_terms='Original card design reusable under CC0; source text retains the terms recorded in sources.yaml. https://creativecommons.org/publicdomain/zero/1.0/',required_credits='Source-based fact cards: figures and labels from the exact Swedish source passages, credited under Text sources. No invented numerical proportions.',relevance_verification='Each card key names the sentence supplying its labels. Full figures retain their source date and geography in the matching bilingual sentence. No map, scale, extrapolation or new factual claim.'),dict(asset_id='music_bed',kind='music',status='ready',file_path=str((MEDIA/'sources/music.mp3').relative_to(ROOT)),files=[file_record(MEDIA/'sources/music.mp3')],source_url='https://incompetech.com/music/royalty-free/index.html?isrc='+music['isrc'],creator='Kevin MacLeod',reuse_terms='CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/',required_credits=music['title']+' — Kevin MacLeod (incompetech.com). Licensed under Creative Commons Attribution 4.0: https://creativecommons.org/licenses/by/4.0/. Excerpt, fades, level adjustment and narration ducking; no loop.',relevance_verification=f'Official composer pieces.json identifies title, filename, ISRC {music["isrc"]}, {music["length"]}, instruments {music["instruments"]}, feel {music["feel"]}. Original is longer than the episode; distinct track reserved for this subchapter. Whole-video listening/mix review pending.',render_adaptation='Excerpt from beginning, +2 dB music setting matching accepted first episode, fades and ducking. No looping.')]
    selected = yaml.safe_load((ROOT/'studio/episodes/hb-c01-lage/assets.yaml').read_text())
    default = next(a for a in selected['assets'] if a['asset_id']=='narration')
    records = json.loads((MEDIA/'narration/metrics.json').read_text())
    assert len(records) == len(script['sentences']), 'Finish all narration before preparing the register'
    narr = dict(asset_id='narration',kind='narration',status='ready',review_status='complete_video_review_pending',file_path=records[0]['path'],files=[],source_url=default['source_url'],creation_method=default['creation_method'],creator=default['creator'],reuse_terms=default['reuse_terms'],required_credits=default['required_credits'],relevance_verification='One locally generated F1 WAV per exact source sentence, source order; speech-only expansions recorded separately. File coverage/inputs checked automatically. ASR diagnostic does not establish accent, voice quality or pronunciation. Complete-video listening/user review pending.')
    for row, record in zip(script['sentences'], records):
        assert row['sentence_id']==record['sentence_id']
        entry=file_record(ROOT/record['path'])
        entry.update(sentence_id=record['sentence_id'],tts_input=record['text'],sample_rate=record['sample_rate'],seconds=record['seconds'],peak=record['peak'],generation_seconds=record['generation_seconds'])
        if record.get('generation_run'):
            entry['generation_run'] = record['generation_run']
        narr['files'].append(entry)
    if (EPISODE/'narration-revisions.json').exists():
        narr['creation_method']['seed_scope'] = 'Full source-order NumPy stream; recorded targeted retakes start a fresh seed 42 stream (narration-revisions.json).'
    assets.append(narr)
    if CLIMATE:
        path=MEDIA/'sources/autumn.jpg'
        assets.append(dict(asset_id='autumn_photo',kind='foreground',status='ready',file_path=str(path.relative_to(ROOT)),files=[file_record(path)],source_url='https://commons.wikimedia.org/wiki/File:Nuuksio_autumn_colors.jpg',creator='Janne Hellsten',reuse_terms='CC BY 2.0 — https://creativecommons.org/licenses/by/2.0/',required_credits='Nuuksio autumn colors — Janne Hellsten, CC BY 2.0, via Wikimedia Commons/Flickr. https://commons.wikimedia.org/wiki/File:Nuuksio_autumn_colors.jpg. Cropped into a steady foreground panel.',relevance_verification='Commons description identifies Nuuksio National Park and autumn colors; photographer Flickr source https://www.flickr.com/photos/50813633@N00/4982122831. Commons bot verified CC BY 2.0 on 11 July 2013. Metadata identifies 11 September 2010; do not infer national autumn dates from this photo.'))
    (EPISODE/'assets.yaml').write_text(yaml.safe_dump(dict(schema_version=1,section_id=SECTION,assets=assets),allow_unicode=True,sort_keys=False,width=100))
    if CLIMATE:
        import sys
        sys.path.insert(0,str(ROOT/'studio/tools'))
        from render import build_timeline,FPS
        _,frames=build_timeline(script)
        script['render']['background_style']['motion_cycles']=frames/FPS/140
        for decision in script['episode_decisions']:
            if decision['id']=='motion':decision['decision']=decision['decision'].replace('Exact cycle count set after WAV timing.',f'Exact cycle count {frames/FPS/140:.9f} across measured {frames/FPS:.6f}seconds.')
        (EPISODE/'script.yaml').write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100))
    print(SECTION,len(assets),'assets;',len(records),'WAVs')


if __name__=='__main__':
    main()
