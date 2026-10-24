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

def main():
    verify_pinned_sources()
    d = yaml.safe_load((EPISODE / 'script.yaml').read_text())
    sources = MEDIA / 'sources'
    cards = MEDIA / 'cards'
    cards.mkdir(exist_ok=True, parents=True)
    cardfiles = []
    for row in d['sentences']:
        if not row.get('render_image'):
            continue
        path = ROOT / row['render_image']
        if not path.resolve().is_relative_to(cards.resolve()) or path.suffix != '.png':
            raise ValueError('This helper only writes episode card PNGs: ' + str(path))
        labels = row['text_highlights']
        canvas = Image.new('RGB', (760, 720), '#342736')
        draw = ImageDraw.Draw(canvas)
        size = 64 if len(labels) < 5 else 48
        while any((draw.textlength(t, font=ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', size)) > 660 for t in labels)):
            size -= 1
        face = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', size)
        spacing = min(108, 540 / max(1, len(labels)))
        top = 360 - len(labels) * spacing / 2
        draw.line((50, 85, 165, 85), fill='#e2bb85', width=5)
        for j, t in enumerate(labels):
            draw.text((380, top + j * spacing), t, font=face, fill='#e2bb85' if any((c.isdigit() for c in t)) else '#faf3e8', anchor='mt')
        canvas.save(path)
        cardfiles.append(dict(**file_info(path), sentence_id=row['sentence_id'], source_substrings=labels))
    if '--cards-only' in sys.argv:
        print(SECTION, len(cardfiles), 'source-only typography cards')
        return
    metrics = json.loads((MEDIA / 'narration/metrics.json').read_text())
    if [m['sentence_id'] for m in metrics] != [r['sentence_id'] for r in d['sentences']]:
        raise ValueError('Narration metrics must cover every source sentence in exact order')
    length = 3 + 30 + sum((math.ceil((m['seconds'] + r['pause_after_seconds']) * 24) / 24 + 0.25 for m, r in zip(metrics, d['sentences'])))
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
    # Decoded MP3 overshoot or equal-power joins may exceed PCM full scale.
    # Attenuate the complete float bed uniformly before integer conversion;
    # accepted mixer normalization and the +2 dB music adjustment remain intact.
    float_peak_before_pcm = float(np.max(np.abs(music)))
    if not np.isfinite(music).all():
        raise ValueError('Non-finite music bed')
    pre_pcm_gain = .98 / float_peak_before_pcm if float_peak_before_pcm >= 1 else 1.
    music *= pre_pcm_gain
    pre_pcm_gain_db = 20 * math.log10(pre_pcm_gain)
    sf.write(sources / 'music-bed.flac', music, 48000, subtype='PCM_24')
    narration = []
    for row, m in zip(d['sentences'], metrics):
        row['audio_path'] = m['path']
        entry = file_info(ROOT / m['path'])
        entry.update({k: m[k] for k in ['sentence_id', 'sample_rate', 'seconds', 'peak', 'generation_seconds']})
        entry['tts_input'] = m['text']
        entry['generation_run'] = m.get('generation_run', 'Initial complete episode source-order stream, NumPy seed42')
        narration.append(entry)
    evidence = json.loads((EPISODE / 'media-sources.json').read_text())
    pi = evidence['photo']
    meta = pi['extmetadata']
    clean = lambda name: __import__('re').sub('<[^>]+>', '', meta.get(name, {}).get('value', '')).strip()
    creator = clean('Artist')
    license = clean('LicenseShortName')
    licenseurl = clean('LicenseUrl')
    title = evidence.get('photo_title') or __import__('urllib.parse', fromlist=['unquote']).unquote(pi['descriptionurl'].split('/wiki/')[-1]).replace('_', ' ')
    sourceurl = pi['descriptionurl']
    photourl = pi.get('download_url', pi.get('thumburl', pi['url']))
    track = evidence['music']['title']
    musicurl = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/' + __import__('urllib.parse', fromlist=['quote']).quote(evidence['music']['filename'])
    photoasset = {'asset_id': 'episode_background', 'kind': 'background', 'files': [file_info(sources / 'background.jpg')], 'source_url': sourceurl, 'creator': creator, 'reuse_terms': license + '; ' + licenseurl, 'required_credits': f"{title.removeprefix('File:')} — {creator} · {license}. {sourceurl} License: {licenseurl}. Cropped, darkened, blurred and pan/zoom adapted; photograph adaptation retains " + license + '.', 'relevance_verification': clean('ImageDescription') + ' ' + evidence['context'] + ' Identity and reuse terms checked against Commons imageinfo metadata; not historical-event evidence.'}
    musicasset = {'asset_id': 'music_bed', 'kind': 'music', 'files': [file_info(sources / 'music.mp3'), file_info(sources / 'music-bed.flac')], 'title': track, 'source_url': 'https://incompetech.com/music/royalty-free/index.html?isrc=' + evidence['music']['isrc'], 'source_audio_url': musicurl, 'creator': 'Kevin MacLeod (incompetech.com)', 'reuse_terms': 'CC BY4.0 https://creativecommons.org/licenses/by/4.0/', 'required_credits': f'"{track}" Kevin MacLeod (incompetech.com). Licensed under Creative Commons: By Attribution4.0 License https://creativecommons.org/licenses/by/4.0/. Excerpted, faded, level-adjusted' + (', repeated with4second equal-power crossfades.' if loops else '.'), 'relevance_verification': 'Distinct calm instrumental track. Composer catalogue attribution and downloadable master verified; no narration or vocals specified by source. Final perceptual balance remains complete-video review.', 'creation_method': {'tool': str(Path(__file__).relative_to(ROOT)), 'master_seconds': master_seconds, 'prepared_seconds': len(music) / 48000, 'crossfade_seconds': 4, 'crossfade_repeats': loops, 'float_peak_before_pcm': float_peak_before_pcm, 'pre_pcm_gain': pre_pcm_gain, 'pre_pcm_gain_db': pre_pcm_gain_db, 'headroom_policy': 'Uniform attenuation to0.98 only when the float bed reaches/exceeds1 before PCM conversion; raw master unchanged, final mix normalization and accepted+2dB retained.', 'format': '48000Hz stereo PCM24 FLAC'}}
    cardsasset = {'asset_id': 'fact_cards', 'kind': 'foreground', 'files': cardfiles, 'creator': 'Homebrew video studio typography', 'reuse_terms': 'Original layout; text repeats the episode source with its recorded credits.', 'required_credits': 'Source text credits in sources.yaml; no third-party imagery in these cards.', 'relevance_verification': 'Each label is an exact substring of its associated Swedish source sentence; no inferred figures, identities, routes or geographic boundaries.', 'creation_method': {'tool': str(Path(__file__).relative_to(ROOT)), 'fonts': 'Liberation Sans Bold', 'size': '760×720'}}
    narrationasset = {'asset_id': 'narration', 'kind': 'narration', 'files': narration, 'creator': 'Local synthesis with Supertonic3 by Supertone', 'reuse_terms': 'Code MIT; model OpenRAIL-M. Model licensor claims no rights in generated output; retain license and restrictions at studio/media/models/supertonic3/LICENSE.', 'required_credits': 'Voluntary credit: local Swedish narration Supertonic3 (Supertone), F1.', 'source_url': 'https://huggingface.co/supertone-oss-archive/supertonic-3/tree/aafc6e32416a594460b32413efc49d7fe4ce6d46', 'relevance_verification': 'One measured clip per source sentence in exact source order; script records meaning-preserving speech expansions. No listening or user approval is claimed; review with complete video.', 'review_status': 'pending_complete_video_review', 'creation_method': {'tool': 'studio/tools/audition.py', 'engine': 'supertonic1.3.1', 'model': 'supertonic-3', 'model_revision': 'aafc6e32416a594460b32413efc49d7fe4ce6d46', 'voice': 'F1', 'language': 'sv', 'total_steps': 32, 'speed': 0.95, 'seed': 42, 'seed_scope': 'NumPy seed 42 per generation invocation; source order within each invocation. Interruptions and targeted retakes restart the seed; see file generation_run, narration-restart.json and retake-history.json when present', 'device': 'local CPU ONNX; four intra-op threads; Linux x86_64', 'format': '44100Hz mono PCM16 WAV'}}
    manifest = {'schema_version': 1, 'section_id': SECTION, 'assets': [photoasset, cardsasset, musicasset, narrationasset]}
    evidence['photo_title'] = title
    (EPISODE / 'media-sources.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    (EPISODE / 'assets.yaml').write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False, width=100))
    d['render']['credits'][1]['paragraphs'] = [title.removeprefix('File:') + ' — ' + creator + ' · ' + license, track + ' — Kevin MacLeod (incompetech.com)', 'Musik: CC BY 4.0 · creativecommons.org/licenses/by/4.0', 'Svensk lokal berättarröst: Supertonic3 · F1.', 'Textgrafik: exakta ord och tal ur källtexten.']
    d['render']['background_identity'] = {'source_url': sourceurl, 'description': clean('ImageDescription'), 'license': license}
    d['render']['background_style']['zoom_end'] = 1.219
    d['render']['background_style']['motion_cycles'] = length / 140
    d['render']['background_style']['motion'] = 'smooth full-timeline cyclic diagonal pan and15%relative zoom,140seconds per cycle, starts in motion without resets'
    for dec in d['episode_decisions']:
        if dec['id'] == 'visual_motion':
            dec['decision'] = 'Use ' + title + ' by ' + creator + ' continuously as decorative background, darkened42% and blurred2.5px. Smooth cyclic diagonal pan(0.15,0.15)→(0.85,0.85) and15%relative zoom1.06→1.219,140seconds per motion cycle, starting in motion, with no sentence resets. Total cycles=' + str(length / 140) + '. Foreground and bilingual text remain fixed.'
        if dec['id'] == 'music_selection':
            dec['status'] = 'proposed'
            dec['decision'] = f'Use {track} by Kevin MacLeod (incompetech.com), CC BY 4.0, as this subchapter’s distinct instrumental track. Original master {master_seconds:.3f} seconds; prepared lossless stereo bed {len(music) / 48000:.3f} seconds. Repeat count {loops}, using 4-second equal-power crossfades when needed. Retain the accepted +2 dB music adjustment, ducking under speech, 2-second fade-in and 3-second fade-out. Full attribution accompanies the video.'
    if pre_pcm_gain < 1:
        for dec in d['episode_decisions']:
            if dec['id'] == 'music_selection':
                dec['decision'] += f' Apply uniform float-bed attenuation {pre_pcm_gain_db:.6f}dB before PCM conversion to avoid clipping; raw master and accepted final mixer normalization/+2dB setting are unchanged.'
    (EPISODE / 'script.yaml').write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False, width=100))
    downloads = []
    for p, url in [(sources / 'background.jpg', photourl), (sources / 'music.mp3', musicurl)]:
        downloads.append(dict(**file_info(p), url=url))
    (ROOT / 'studio/runtime' / f'{SECTION}-downloads.yaml').write_text(yaml.safe_dump({'schema_version': 1, 'downloads': downloads}, sort_keys=False))
    print(SECTION, len(narration), 'clips; planned', length, 'seconds; music crossfades', loops)
if __name__ == '__main__':
    main()
