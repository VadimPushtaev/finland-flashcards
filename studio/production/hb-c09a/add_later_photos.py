"""Pin source-backed multilingual books and institutional/object photos."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path.cwd()


def clean(value):
    return re.sub('<[^>]+>', '', value).strip()


def record(slug, index, title, info, raw, caption, context, attribution=None):
    metadata = info['extmetadata']
    license_name = clean(metadata['LicenseShortName']['value'])
    assert license_name.startswith('CC ') or license_name == 'Public domain'
    credit = attribution or clean(metadata.get('Artist', {}).get('value', ''))
    assert credit
    value = dict(
        index=index, title=title, imageinfo=info, raw_path=str(raw.relative_to(ROOT)),
        caption=caption, context=context, attribution=credit, license=license_name,
        license_url=clean(metadata.get('LicenseUrl', {}).get(
            'value', 'https://commons.wikimedia.org/wiki/Commons:Public_domain')),
        description=clean(metadata.get('ImageDescription', {}).get('value', '')),
        metadata_source='Unchanged Commons imageinfo extmetadata, object identity and license.',
        download_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
    )
    (ROOT / 'studio/episodes' / ('hb-c09-' + slug) / f'photo-source-{index:03}.json').write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + '\n')


for slug, index, file_name, title, caption, context in [
    ('flersprakighet', 33, 'research-language-books.json',
     'File:Multilingual sign for the Saami-language and German-language kids books at Iso Omena Library 7AUG2026.jpg',
     'Barnböcker på flera språk · Iso Omena · 2026',
     'Actual labelled multilingual children\'s-book shelves illustrate multiple languages. The photograph shows a library object, not a claim about a photographed person\'s language or any current entitlement.'),
    ('flersprakighet', 35, 'research-language-books.json',
     'File:Saami-language kids books at Iso Omena Library 7AUG2026.jpg',
     'Barnböcker på samiska · Iso Omena · 2026',
     'Actual children\'s books in Saami languages illustrate reading with a child regardless of language. No specific teaching curriculum or family identity is inferred.'),
    ('begravning', 16, 'research-urn-grove.json',
     'File:Inkeri Lehtisen hauta Hietniemen hautausmaalla (Uurnalehto).jpg',
     'Uurnalehto · Hietaniemi · Helsinki',
     'Commons specifically identifies the pictured grave as lying in Hietaniemi urn grove, a concrete example of the named cemetery area. No new claim about burial procedure, religion or the deceased person is made.'),
]:
    metadata = json.loads((ROOT / 'studio/production/hb-c09a' / file_name).read_text())
    info = next(row['imageinfo'][0] for row in metadata['query']['pages'].values()
                if row['title'] == title)
    raw = ROOT / 'studio/media' / ('hb-c09-' + slug) / 'sources' / f'photo-{index:03}.jpg'
    subprocess.run(['.venv/bin/python', 'studio/production/remaining/download.py',
                    '--url', info.get('thumburl', info['url']), '--output', str(raw)], check=True)
    record(slug, index, title, info, raw, caption, context)

for slug, index, origin, caption, context in [
    ('flersprakighet', 6, 'vardledighet', 'Annalan päiväkoti · Helsinki',
     'Verified actual Finnish daycare exterior illustrates the source daycare option without identifying any family, current service place or school entitlement.'),
    ('dodsfall', 8, 'barnbidrag', 'FPA · Seinäjoki',
     'Verified Kela office illustrates the source institutional recipient of population-system information. No death, person, office opening or case is inferred.'),
    ('dodsfall', 23, 'vald', 'Poliisiasema · Imatra',
     'Verified Finnish police station illustrates the named institutional responsibility for forensic death investigation. No photographed deceased person or actual incident is inferred.'),
    ('begravning', 40, 'underhall', 'FPA · Myyrmäki · Vantaa · 2022',
     'Verified Kela office supports the source conditional application for funeral-cost assistance; no entitlement, current payment amount or particular applicant is inferred.'),
    ('foraldraskap', 28, 'radgivning', 'Rajakylän neuvola · Vantaa',
     'Verified actual maternity/child clinic supports the source option of recognition at maternity care before birth. No patient or treatment history is assigned.'),
    ('familjetjanster', 7, 'foraldraskap', 'Tikkurilan neuvola · Vantaa · 2022',
     'Actual Finnish clinic supports one of the source examples of preventive services. No pictured family is identified as a service client.'),
    ('familjetjanster', 12, 'kon', 'Tvätt · hushållsarbete',
     'The existing verified laundry-machine object photograph illustrates domestic tasks, without portraying the household as a social-service client.'),
    ('barnskydd', 2, 'vardnad', 'Pelle Hermannin leikkipuisto · Pori',
     'Verified public playground illustrates a concrete safe play environment as a general upbringing setting. No child, park user or home is identified as being in child-protection care.'),
    ('barnskydd', 12, 'vardledighet', 'Annalan päiväkoti · Helsinki',
     'Verified actual daycare exterior illustrates the source institutional category subject to reporting duties. No specific notification, violation or child is inferred.'),
]:
    episode = ROOT / 'studio/episodes' / ('hb-c09-' + origin)
    if slug == 'familjetjanster' and index == 12:
        existing = json.loads((episode / 'photo-source-061.json').read_text())
        info = existing['imageinfo']
        title = existing['title']
        source_raw = ROOT / existing['raw_path']
        attribution = existing['attribution']
    else:
        source = json.loads((episode / 'media-sources.json').read_text())
        info, title = source['photo'], source['photo_title']
        source_raw = ROOT / 'studio/media' / ('hb-c09-' + origin) / 'sources/background.jpg'
        attribution = source.get('attribution_override')
    raw = ROOT / 'studio/media' / ('hb-c09-' + slug) / 'sources' / f'photo-{index:03}.jpg'
    shutil.copy2(source_raw, raw)
    record(slug, index, title, info, raw, caption, context, attribution)
