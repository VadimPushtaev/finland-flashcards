"""Acquire pinned, relevant object/institution foregrounds for four episodes."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path.cwd()
metadata = json.loads((ROOT / 'studio/production/hb-c09a/research-maternity-box.json').read_text())
pages = {row['title']: row['imageinfo'][0]
         for row in metadata['query']['pages'].values()}


def clean(value):
    return re.sub('<[^>]+>', '', value).strip()


def record(slug, index, title, imageinfo, raw, caption, context,
           attribution=None, collection=None):
    meta = imageinfo['extmetadata']
    rec = dict(
        index=index, title=title, imageinfo=imageinfo,
        raw_path=str(raw.relative_to(ROOT)), caption=caption, context=context,
        attribution=attribution or clean(meta['Artist']['value']),
        license=clean(meta['LicenseShortName']['value']),
        license_url=clean(meta.get('LicenseUrl', {}).get('value', 'https://commons.wikimedia.org/wiki/Commons:Public_domain' if meta['LicenseShortName']['value'] == 'Public domain' else '')),
        description=clean(meta.get('ImageDescription', {}).get('value', '')),
        metadata_source='Unchanged Commons imageinfo extmetadata; pinned original image.',
        download_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
    )
    if collection:
        rec['collection_credit'] = collection
    path = ROOT / 'studio/episodes' / ('hb-c09-' + slug) / f'photo-source-{index:03}.json'
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + '\n')


for index, title, caption, attribution, collection in [
    (11, 'File:Finnish maternity package of 2014.jpg',
     'Moderskapsförpackning · 2014', None, None),
    (12, 'File:Vauvan ensimmäinen sänky vuodevaatteineen.jpg',
     'Vauvansänky · 1940–1960', 'Photographer unrecorded', 'Helsingin kaupunginmuseo'),
    (15, 'File:Äitiyspakkauksen sisältöä vuonna 1957.jpg',
     'Äitiyspakkaus · 1957', None, 'Museovirasto / JOKA Journalistinen kuva-arkisto / UA Saarisen kokoelma'),
]:
    info = pages[title]
    raw = ROOT / 'studio/media/hb-c09-radgivning/sources' / f'photo-{index:03}.jpg'
    subprocess.run(['.venv/bin/python', 'studio/production/remaining/download.py',
                    '--url', info.get('thumburl', info['url']), '--output', str(raw)],
                   check=True)
    record('radgivning', index, title, info, raw, caption,
           'Verified dated Finnish maternity-package object photograph. The caption states its archive year/range; no current package contents, individual benefit entitlement or clinical recommendation is inferred.',
           attribution, collection)

for slug, index, origin, caption, context in [
    ('radgivning', 1, 'foraldraskap', 'Tikkurilan neuvola · Vantaa · 2022',
     'Actual Finnish maternity/child clinic exterior supports the named clinic service; no depicted patient or current opening/service claim.'),
    ('radgivning', 9, 'barnbidrag', 'FPA · Seinäjoki',
     'Actual Kela office supports the source application to FPA; no individual eligibility is inferred.'),
    ('skilsmassa', 4, 'heder', 'Länsi-Uudenmaan käräjäoikeus · Tammisaari',
     'Actual Finnish district court illustrates the institution receiving a divorce application; no claim about the depicted building handling a specific case.'),
    ('skilsmassa', 28, 'makar', 'Vartiosaari · Helsinki · 2020',
     'Actual Finnish dwelling illustrates the physical shared-home question; no photographed owner, family or divorce case is identified.'),
    ('vardnad', 12, 'makar', 'Vartiosaari · Helsinki · 2020',
     'Actual dwelling illustrates a place of residence; no photographed child, custody status or official address is identified.'),
    ('skydd', 17, 'vald', 'Poliisiasema · Imatra',
     'Actual Finnish police station illustrates police as the emergency service; no opening hours, specific incident or photographed victim is inferred.'),
    ('skydd', 36, 'heder', 'Länsi-Uudenmaan käräjäoikeus · Tammisaari',
     'Actual Finnish district court illustrates the source institution for a restraining-order application; no court case or photographed victim is inferred.'),
]:
    source = json.loads((ROOT / 'studio/episodes' / ('hb-c09-' + origin) / 'media-sources.json').read_text())
    original = ROOT / 'studio/media' / ('hb-c09-' + origin) / 'sources/background.jpg'
    raw = ROOT / 'studio/media' / ('hb-c09-' + slug) / 'sources' / f'photo-{index:03}.jpg'
    shutil.copy2(original, raw)
    record(slug, index, source['photo_title'], source['photo'], raw, caption, context,
           source.get('attribution_override'))
