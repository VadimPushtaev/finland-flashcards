"""Restore pinned foreground pictures and regenerate proportional PNG previews."""
from pathlib import Path
import json, hashlib, re, time, requests, yaml
from PIL import Image
ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parent
SID = EP.name
MEDIA = ROOT / 'studio/media' / SID

def info(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}

def main():
    assets = []
    downloads = []
    credits = []
    for rec in json.loads((EP / 'foreground-plan.json').read_text()):
        pi = rec['imageinfo']
        key = rec['key']
        meta = pi['extmetadata']
        clean = lambda k: re.sub('<[^>]+>', '', meta.get(k, {}).get('value', '')).strip()
        url = pi.get('thumburl', pi['url'])
        raw = MEDIA / 'sources' / ('picture-' + key + ('.png' if '.svg' in pi['url'] or '.png' in pi['url'] else '.jpg'))
        raw.parent.mkdir(parents=True, exist_ok=True)
        if not raw.exists():
            for attempt in range(8):
                r = requests.get(url, headers={'User-Agent': 'HomebrewVideoStudio/1.0 (educational documentary production)'}, timeout=90)
                if r.status_code == 429:
                    time.sleep(15)
                    continue
                r.raise_for_status()
                raw.write_bytes(r.content)
                break
        saved = EP / 'foreground-downloads.json'
        if saved.exists():
            old = next((r for r in json.loads(saved.read_text()) if r['path'] == str(raw.relative_to(ROOT))), None)
            if old and info(raw)['sha256'] != old['sha256']:
                raise ValueError('Changed source ' + str(raw))
        pic = MEDIA / 'pictures' / (key + '.png')
        pic.parent.mkdir(parents=True, exist_ok=True)
        im = Image.open(raw).convert('RGBA')
        if rec.get('crop'):
            im = im.crop(tuple(rec['crop']))
        im.thumbnail((1100, 1000), Image.Resampling.LANCZOS)
        im.save(pic)
        creator = rec.get('creator_override') or clean('Artist') or clean('Credit')
        license = clean('LicenseShortName')
        license_url = clean('LicenseUrl')
        title = rec['title'].removeprefix('File:')
        source = pi['descriptionurl']
        assets.append({'asset_id': 'picture_' + key, 'kind': 'foreground', 'visual_type': 'flag' if 'flag' in title.lower() else 'photograph', 'files': [info(pic)], 'source_url': source, 'creator': creator, 'reuse_terms': license + ' ' + license_url, 'required_credits': f'{title} — {creator}. {license}. {source} {license_url}. Proportionally resized with the complete source image preserved and placed on a foreground panel. Original license retained.', 'relevance_verification': rec['context'] + ' Source metadata: ' + clean('ImageDescription'), 'creation_method': {'tool': str(Path(__file__).relative_to(ROOT)), 'transform': 'Documented crop ' + str(rec['crop']) if rec.get('crop') else 'Proportional downscale only; complete image preserved.'}})
        downloads.append(dict(**info(raw), url=url))
        credits.append(rec.get('credit_label', title) + f' — {creator} · {license}')
        print(SID, key, flush=True)
    (EP / 'foreground-assets.json').write_text(json.dumps(assets, ensure_ascii=False, indent=2) + '\n')
    (EP / 'foreground-downloads.json').write_text(json.dumps(downloads, ensure_ascii=False, indent=2) + '\n')
    d = yaml.safe_load((EP / 'script.yaml').read_text())
    d['render']['credits'] = d['render']['credits'][:2]
    for i in range(0, len(credits), 3):
        d['render']['credits'].append({'heading': 'Förgrundsbilder · Изображения', 'paragraphs': credits[i:i + 3] + ['Bilder proportionellt förminskade.', 'Fullständiga källor och licenser i medföljande CREDITS.md.']})
    (EP / 'script.yaml').write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100))
if __name__ == '__main__':
    main()
