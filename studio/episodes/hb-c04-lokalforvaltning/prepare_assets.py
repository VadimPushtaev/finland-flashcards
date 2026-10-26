"""Prepare this episode's source-only cards, crossfaded music bed and asset register.

Run with studio/runtime/.venv/bin/python. Downloads restore through this episode's
pinned runtime manifest. Regeneration updates hashes and requires complete-video review.
"""
from pathlib import Path
import hashlib, json, math, subprocess, sys
import numpy as np
import soundfile as sf
import yaml, imageio_ffmpeg, av
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[3]
EPISODE = Path(__file__).resolve().parent
SECTION = EPISODE.name
MEDIA = ROOT / 'studio/media' / SECTION

def file_info(path):
    result = {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
    if path.suffix in ('.wav', '.flac'):
        info = sf.info(path)
        result.update(seconds=info.duration, sample_rate=info.samplerate, channels=info.channels)
    return result

def verify_pinned_sources():
    """Reject changed downloaded masters before regenerating their asset records."""
    manifest = ROOT / 'studio/runtime' / (SECTION + '-downloads.yaml')
    if manifest.exists():
        for entry in yaml.safe_load(manifest.read_text())['downloads']:
            path = ROOT / entry['path']
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError('Restore the pinned source before regenerating: ' + str(path))

def prepare_map_panel(item):
    """Preserve map geography and add a visible key for the 21+2 distinction."""
    original = Image.open(ROOT / item['source_path']).convert('RGBA')
    neutral = Image.new('RGBA', original.size, item.get('display_background', '#dfebeb'))
    neutral.alpha_composite(original)
    if item['id'] != 'county_map':
        neutral.convert('RGB').save(ROOT / item['path'])
        return
    # The source labels 1–21 identify counties; 22 and 23 are separate areas.
    # Keep every original border/label, fit the complete map, and explain the key.
    panel = Image.new('RGB', (760, 720), '#dfebeb')
    mapped = neutral.convert('RGB')
    mapped.thumbnail((402, 700), Image.Resampling.LANCZOS)
    panel.paste(mapped, (10 + (402 - mapped.width) // 2, 10 + (700 - mapped.height) // 2))
    draw = ImageDraw.Draw(panel)
    regular = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 26)
    bold = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 31)
    ink = '#382d24'
    x = 432
    for y, label, face in [(105, '1–21', bold), (148, 'välfärdsområden', regular),
                           (211, '22: Helsingfors', regular), (255, '23: Åland', regular),
                           (370, '1–21', bold), (413, 'регионы по', regular),
                           (447, 'обеспечению', regular), (481, 'благополучия', regular),
                           (515, 'населения', regular), (566, '22: Хельсинки', regular),
                           (610, '23: Аландские', regular), (646, 'острова', regular)]:
        if draw.textlength(label, font=face) > 306:
            raise ValueError('Map key exceeds its fixed panel: ' + label)
        draw.text((x, y), label, font=face, fill=ink)
    draw.line((432, 328, 732, 328), fill='#695540', width=2)
    panel.save(ROOT / item['path'])

def main():
    verify_pinned_sources()
    d = yaml.safe_load((EPISODE / 'script.yaml').read_text())
    for item in json.loads((EPISODE / 'foreground-sources.json').read_text()):
        if item.get('source_path'):
            prepare_map_panel(item)
    sources = MEDIA / 'sources'
    cards = MEDIA / 'cards'
    cards.mkdir(exist_ok=True, parents=True)
    cardfiles = []
    for row in d['sentences']:
        if not row.get('render_image'):
            continue
        path = ROOT / row['render_image']
        if not path.resolve().is_relative_to(cards.resolve()):
            if not path.is_file():
                raise ValueError('Missing acquired foreground picture: ' + str(path))
            continue
        if path.suffix != '.png':
            raise ValueError('Source-term cards must be PNG files: ' + str(path))
        labels = row['text_highlights']
        canvas = Image.new('RGB', (760, 720), '#382d24')
        draw = ImageDraw.Draw(canvas)
        size = 64 if len(labels) < 5 else 48
        while any((draw.textlength(t, font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', size)) > 660 for t in labels)):
            size -= 1
        face = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', size)
        spacing = min(108, 540 / max(1, len(labels)))
        top = 360 - len(labels) * spacing / 2
        draw.line((50, 85, 165, 85), fill='#dfb96f', width=5)
        for j, t in enumerate(labels):
            draw.text((380, top + j * spacing), t, font=face, fill='#dfb96f' if any((c.isdigit() for c in t)) else '#faf3e8', anchor='mt')
        canvas.save(path)
        cardfiles.append(dict(**file_info(path), sentence_id=row['sentence_id'], source_substrings=labels))
    if '--cards-only' in sys.argv:
        print(SECTION, len(cardfiles), 'source-only typography cards')
        return
    foregrounds = json.loads((EPISODE / 'foreground-sources.json').read_text()) if (EPISODE / 'foreground-sources.json').exists() else []
    # Keep source/background/music credits, then add readable foreground attribution cards.
    d['render']['credits'] = d['render']['credits'][:2]
    for offset in range(0, len(foregrounds), 4):
        paragraphs = []
        for item in foregrounds[offset:offset + 4]:
            meta = item['photo']['extmetadata']
            clean_meta = lambda key: __import__('re').sub('<[^>]+>', '', __import__('html').unescape(meta.get(key, {}).get('value', ''))).strip()
            paragraphs.append(item['label'] + ' — ' + (clean_meta('Artist') or 'Photographer unknown') + ' · ' + clean_meta('LicenseShortName'))
        paragraphs.append('Fullständiga länkar och bildvillkor i medföljande CREDITS.md.')
        d['render']['credits'].append({'heading': 'Bilder i förgrunden · Иллюстрации', 'paragraphs': paragraphs})
    metrics = json.loads((MEDIA / 'narration/metrics.json').read_text())
    if [m['sentence_id'] for m in metrics] != [r['sentence_id'] for r in d['sentences']]:
        raise ValueError('Narration metrics must cover every source sentence in exact order')
    length = 3 + 15 * len(d['render']['credits']) + sum((math.ceil((m['seconds'] + r['pause_after_seconds']) * 24) / 24 + 0.25 for m, r in zip(metrics, d['sentences'])))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    raw = subprocess.run([ffmpeg, '-v', 'error', '-i', str(sources / 'music.mp3'), '-t', str(length + 1), '-f', 'f32le', '-ac', '2', '-ar', '48000', '-'], check=True, capture_output=True).stdout
    music = np.frombuffer(raw, dtype='<f4').reshape(-1, 2).copy()
    master = music.copy()
    original = len(music)
    cross = 4 * 48000
    loops = 0
    with av.open(str(sources / 'music.mp3')) as c:
        master_seconds = c.duration / av.time_base
    while len(music) < math.ceil(length * 48000):
        ramp = np.linspace(0, np.pi / 2, cross)[:, None]
        join = music[-cross:] * np.cos(ramp) + master[:cross] * np.sin(ramp)
        music = np.concatenate([music[:-cross], join, master[cross:]])
        loops += 1
    music = music[:math.ceil(length * 48000)]
    if not np.all(np.isfinite(music)):
        raise ValueError('Non-finite samples in music bed')
    float_peak = float(np.max(np.abs(music)))
    safety_gain = min(1.0, 0.98 / float_peak) if float_peak else 1.0
    music *= safety_gain
    sf.write(sources / 'music-bed.flac', music, 48000, subtype='PCM_24')
    (EPISODE / 'music-headroom.json').write_text(json.dumps({'float_peak_before_gain': float_peak, 'gain': safety_gain, 'float_peak_after_gain': float(np.max(np.abs(music))), 'finite': True}, indent=2) + '\n')
    narration = []
    for row, m in zip(d['sentences'], metrics):
        row['audio_path'] = m['path']
        entry = file_info(ROOT / m['path'])
        entry.update({k: m[k] for k in ['sentence_id', 'sample_rate', 'seconds', 'peak', 'generation_seconds']})
        entry['tts_input'] = m['text']
        entry['intra_op_num_threads'] = m.get('intra_op_num_threads', 4)
        entry['generation_run'] = m.get('generation_run', 'Initial complete episode source-order stream, NumPy seed 42')
        narration.append(entry)
    evidence = json.loads((EPISODE / 'media-sources.json').read_text())
    pi = evidence['photo']
    meta = pi['extmetadata']
    clean = lambda name: __import__('re').sub('<[^>]+>', '', __import__('html').unescape(meta.get(name, {}).get('value', ''))).strip()
    creator = clean('Artist') or 'Photographer unknown; Yle Archives'
    license = clean('LicenseShortName')
    licenseurl = clean('LicenseUrl')
    selected_license = evidence.get('selected_photo_license')
    if selected_license:
        license, licenseurl = selected_license['name'], selected_license['url']
    title = evidence.get('photo_title') or __import__('urllib.parse', fromlist=['unquote']).unquote(pi['descriptionurl'].split('/wiki/')[-1]).replace('_', ' ')
    sourceurl = pi['descriptionurl']
    if not licenseurl:
        licenseurl = sourceurl + '#Licensing'
    photourl = pi.get('download_url', pi.get('thumburl', pi['url']))
    track = evidence['music']['title']
    musicurl = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/' + __import__('urllib.parse', fromlist=['quote']).quote(evidence['music']['filename'])
    photoasset = {'asset_id': 'episode_background', 'kind': 'background', 'files': [file_info(sources / 'background.jpg')], 'source_url': sourceurl, 'creator': creator, 'reuse_terms': license + '; ' + licenseurl, 'required_credits': f"{title.removeprefix('File:')} — {creator} · {license}. {sourceurl} License: {licenseurl}. Cropped, darkened, blurred and pan/zoom adapted; photograph adaptation retains " + license + '.', 'relevance_verification': clean('ImageDescription') + ' ' + evidence['context'] + ' Identity and reuse terms checked against Commons imageinfo metadata; not historical-event evidence.'}
    if selected_license:
        photoasset['required_credits'] += ' ' + selected_license['required_credit']
        photoasset['license_selection_evidence'] = selected_license
    musicasset = {'asset_id': 'music_bed', 'kind': 'music', 'files': [file_info(sources / 'music.mp3'), file_info(sources / 'music-bed.flac')], 'title': track, 'source_url': 'https://incompetech.com/music/royalty-free/index.html?isrc=' + evidence['music']['isrc'], 'source_audio_url': musicurl, 'creator': 'Kevin MacLeod (incompetech.com)', 'reuse_terms': 'CC BY 4.0 https://creativecommons.org/licenses/by/4.0/', 'required_credits': f'"{track}" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution 4.0 License https://creativecommons.org/licenses/by/4.0/. Excerpted, faded, level-adjusted' + (', repeated with 4-second equal-power crossfades.' if loops else '.'), 'relevance_verification': 'Distinct calm instrumental track. Composer catalogue attribution and downloadable master verified; no narration or vocals specified by source. Final perceptual balance remains complete-video review.', 'creation_method': {'tool': str(Path(__file__).relative_to(ROOT)), 'master_seconds': master_seconds, 'prepared_seconds': len(music) / 48000, 'crossfade_seconds': 4, 'crossfade_repeats': loops, 'format': '48000Hz stereo PCM24 FLAC', 'float_peak_before_gain': float_peak, 'headroom_gain': safety_gain, 'peak_after_gain': float(np.max(np.abs(music)))}}
    cardsasset = {'asset_id': 'fact_cards', 'kind': 'foreground', 'files': cardfiles, 'creator': 'Homebrew video studio typography', 'reuse_terms': 'Original layout; text repeats the episode source with its recorded credits.', 'required_credits': 'Source text credits in sources.yaml; no third-party imagery in these cards.', 'relevance_verification': 'Each label is an exact substring of its associated Swedish source sentence; no inferred figures, identities, routes or geographic boundaries.', 'creation_method': {'tool': str(Path(__file__).relative_to(ROOT)), 'fonts': 'Liberation Sans Bold', 'size': '760×720'}}
    narrationasset = {'asset_id': 'narration', 'kind': 'narration', 'files': narration, 'creator': 'Local synthesis with Supertonic 3 by Supertone', 'reuse_terms': 'Code MIT; model OpenRAIL-M. Model licensor claims no rights in generated output; retain license and restrictions at studio/media/models/supertonic3/LICENSE.', 'required_credits': 'Voluntary credit: local Swedish narration Supertonic 3 (Supertone), F1.', 'source_url': 'https://huggingface.co/supertone-oss-archive/supertonic-3/tree/aafc6e32416a594460b32413efc49d7fe4ce6d46', 'relevance_verification': 'One measured clip per source sentence in exact source order; script records meaning-preserving speech expansions. No listening or user approval is claimed; review with complete video.', 'review_status': 'pending_complete_video_review', 'creation_method': {'tool': 'studio/tools/audition.py', 'engine': 'supertonic 1.3.1', 'model': 'supertonic-3', 'model_revision': 'aafc6e32416a594460b32413efc49d7fe4ce6d46', 'voice': 'F1', 'language': 'sv', 'total_steps': 32, 'speed': 0.95, 'seed': 42, 'seed_scope': 'NumPy seed 42 per generation invocation; source order within each invocation. Interruptions and targeted retakes restart the seed; see file generation_run, narration-restart.json and retake-history.json when present', 'device': 'local CPU ONNX; Linux x86_64; intra-op thread count recorded per file (initial takes four, new jobs may use two)' , 'format': '44100Hz mono PCM16 WAV'}}
    acquired_pictures = []
    for item in foregrounds:
        meta = item['photo']['extmetadata']
        clean_meta = lambda key: __import__('re').sub('<[^>]+>', '', __import__('html').unescape(meta.get(key, {}).get('value', ''))).strip()
        fg_creator = clean_meta('Artist') or 'Photographer unknown'
        fg_license = clean_meta('LicenseShortName')
        url = item['photo']['descriptionurl']
        license_url = clean_meta('LicenseUrl') or url + '#Licensing'
        acquired_pictures.append({'asset_id': item['id'], 'kind': 'foreground', 'visual_type': item['visual_type'], 'files': [dict(**file_info(ROOT / item['path']), visual_type=item['visual_type'])], 'source_url': url, 'creator': fg_creator, 'reuse_terms': fg_license + '; ' + license_url, 'required_credits': item['title'] + ' — ' + fg_creator + '. ' + fg_license + '. ' + url + ' License: ' + license_url + '. Resized or cropped to the stationary foreground panel; source license retained.' + (' A bilingual legend distinguishes counties 1–21 from separate Helsinki 22 and Åland 23; all original map borders and labels preserved.' if item['id']=='county_map' else ''), 'relevance_verification': item['context'] + ' Identity and license checked against preserved source metadata and the actual image.'})
    manifest = {'schema_version': 1, 'section_id': SECTION, 'assets': [photoasset] + ([cardsasset] if cardfiles else []) + acquired_pictures + [musicasset, narrationasset]}
    evidence['photo_title'] = title
    (EPISODE / 'media-sources.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    (EPISODE / 'assets.yaml').write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100))
    d['render']['credits'][1]['paragraphs'] = [title.removeprefix('File:') + ' — ' + creator + ' · ' + license, track + ' — Kevin MacLeod (incompetech.com)', 'Musik: CC BY 4.0 · creativecommons.org/licenses/by/4.0', 'Svensk lokal berättarröst: Supertonic 3 · F1.', 'Textgrafik: exakta ord och tal ur källtexten.']
    if selected_license:
        d['render']['credits'][1]['paragraphs'][0] = selected_license['required_credit']
    d['render']['background_identity'] = {'source_url': sourceurl, 'description': clean('ImageDescription'), 'license': license}
    d['render']['background_style']['zoom_end'] = 1.219
    d['render']['background_style']['motion_cycles'] = length / 140
    d['render']['background_style']['motion'] = 'smooth full-timeline cyclic diagonal pan and 15% relative zoom, 140 seconds per cycle, starts in motion without resets'
    for dec in d['episode_decisions']:
        if dec['id'] == 'visual_motion':
            dec['decision'] = 'Use ' + title + ' by ' + creator + ' continuously as decorative background, darkened 42% and blurred 2.5px. Smooth cyclic diagonal pan (0.15,0.15)→(0.85,0.85) and 15% relative zoom 1.06→1.219, 140 seconds per motion cycle, starting in motion, with no sentence resets. Total cycles=' + str(length / 140) + '. Foreground and bilingual text remain fixed.'
        if dec['id'] == 'music_selection':
            dec['status'] = 'proposed'
            dec['decision'] = f'Use {track} by Kevin MacLeod (incompetech.com), CC BY 4.0, as this subchapter’s distinct instrumental track. Original master {master_seconds:.3f} seconds; prepared lossless stereo bed {len(music) / 48000:.3f} seconds. Repeat count {loops}, using 4-second equal-power crossfades when needed. Retain the accepted +2 dB music adjustment, ducking under speech, 2-second fade-in and 3-second fade-out. Full attribution accompanies the video.'
    (EPISODE / 'script.yaml').write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100))
    downloads = []
    for p, url in [(sources / 'background.jpg', photourl), (sources / 'music.mp3', musicurl)]:
        downloads.append(dict(**file_info(p), url=url))
    for item in foregrounds:
        downloads.append(dict(**file_info(ROOT / item.get('source_path', item['path'])), url=item['download_url']))
    (ROOT / 'studio/runtime' / f'{SECTION}-downloads.yaml').write_text(yaml.safe_dump({'schema_version': 1, 'downloads': downloads}, sort_keys=False))
    print(SECTION, len(narration), 'clips; planned', length, 'seconds; music crossfades', loops)
if __name__ == '__main__':
    main()
