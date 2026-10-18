"""Render the scripted bilingual episode locally with Pillow and FFmpeg."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import soundfile as sf
from scipy.signal import resample_poly
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from studio.tools.outputs import export_stem
W, H, FPS, RATE = 1920, 1080, 24, 48000
BG, FG, MUTED, GOLD = '#102e2b', '#f6f1e6', '#bdd3c9', '#e7bc70'
FONTS = Path('/System/Library/Fonts/Supplemental')


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS / ('Arial Bold.ttf' if bold else 'Arial.ttf')), size)


def fitted_font(text, size, width, bold=False, minimum=30):
    """Fit a single-line label without clipping or changing its wording."""
    while size > minimum and font(size, bold).getlength(text) > width:
        size -= 1
    face = font(size, bold)
    if face.getlength(text) > width:
        raise ValueError('Label exceeds available width: ' + text)
    return face


def sentence_style(row):
    """Use script-selected sizes; require long pairs to remain readable."""
    style = row.get('text_style', {})
    sv_size, ru_size = style.get('sv_size', 48), style.get('ru_size', 40)
    if sv_size < 40 or ru_size < 34:
        raise ValueError('Segment long text instead of shrinking below readable sizes')
    return sv_size, ru_size, round(sv_size * 1.3125), round(ru_size * 1.375)


def loop_music(music, length, crossfade_seconds):
    """Extend one selected track with explicitly requested smooth crossfades."""
    overlap = round(crossfade_seconds * RATE)
    if overlap <= 0 or overlap * 2 >= len(music):
        raise ValueError('Music crossfade must be positive and shorter than half the track')
    result = np.zeros((length, 2), dtype=np.float32)
    first = min(length, len(music))
    result[:first] = music[:first]
    cursor = len(music) - overlap
    ramp = np.linspace(0, 1, overlap, dtype=np.float32)[:, None]
    while cursor < length:
        count = min(len(music), length - cursor)
        blend = min(overlap, count)
        result[cursor:cursor + blend] *= 1 - ramp[:blend]
        result[cursor:cursor + blend] += music[:blend] * ramp[:blend]
        result[cursor + blend:cursor + count] = music[blend:count]
        cursor += len(music) - overlap
    return result


def wrap(text, face, width):
    """Wrap only at source spaces; reject an unrenderable individual word."""
    lines = []
    line = ''
    for word in text.split(' '):
        if face.getlength(word) > width:
            raise ValueError('Word exceeds text panel: ' + word)
        candidate = line + (' ' if line else '') + word
        if face.getlength(candidate) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    if ' '.join(lines) != text:
        raise ValueError('Wrapping changed source text')
    return lines


def text_block(draw, text, xy, face, width, fill, leading, highlights=()):
    lines = wrap(text, face, width)
    x, y = xy
    offset = 0
    spans = []
    for highlight in highlights:
        start = text.find(highlight)
        if start >= 0:
            spans.append((start, start + len(highlight)))
    for line in lines:
        cursor = x
        for i, character in enumerate(line):
            color = GOLD if any(a <= offset + i < b for a, b in spans) else fill
            draw.text((cursor, y + face.getmetrics()[0]), character, font=face, fill=color, anchor='ls')
            cursor = x + face.getlength(line[:i + 1])
        offset += len(line) + 1
        y += leading
    return y


def build_timeline(script):
    timeline = [{'kind': 'title', 'frames': 3 * FPS}]
    cursor = 3 * FPS
    for row in script['sentences']:
        info = sf.info(ROOT / row['audio_path'])
        lead = 6  # 250 ms at 24 fps
        frames = math.ceil((info.duration + row['pause_after_seconds']) * FPS) + lead
        timeline.append(dict(kind='sentence', sentence_id=row['sentence_id'], start_frame=cursor,
                             frames=frames, speech_start_seconds=(cursor + lead) / FPS,
                             speech_end_seconds=(cursor + lead) / FPS + info.duration))
        cursor += frames
    for index in range(len(script['render']['credits'])):
        timeline.append(dict(kind='credits', index=index, start_frame=cursor, frames=15 * FPS))
        cursor += 15 * FPS
    timeline[0]['start_frame'] = 0
    return timeline, cursor


def mix_audio(script, timeline, frames, output):
    length = round(frames / FPS * RATE)
    voice = np.zeros(length, dtype=np.float32)
    music_adjustment_db = float(script['render'].get('music_gain_adjustment_db', 0))
    music_gain = 10 ** (music_adjustment_db / 20)
    envelope = np.full(length, .07 * music_gain, dtype=np.float32)
    rows = {row['sentence_id']: row for row in script['sentences']}
    for item in timeline:
        if item['kind'] != 'sentence':
            continue
        samples, rate = sf.read(ROOT / rows[item['sentence_id']]['audio_path'])
        divisor = math.gcd(rate, RATE)
        samples = resample_poly(samples, RATE // divisor, rate // divisor)
        # Match active speech RMS while retaining at least 3 dB peak headroom.
        active = samples[np.abs(samples) > .012]
        gain = min(.13 / max(np.sqrt(np.mean(active ** 2)), .001), .70 / max(np.max(np.abs(samples)), .001))
        start = round(item['speech_start_seconds'] * RATE)
        voice[start:start + len(samples)] = samples * gain
        a, b = max(0, start - int(.2 * RATE)), min(length, start + len(samples) + int(.2 * RATE))
        envelope[a:b] = .025 * music_gain
    # Smooth ducking transitions over 160 ms.
    window = int(.16 * RATE)
    cumulative = np.cumsum(np.pad(envelope, (window // 2, window // 2), mode='edge'), dtype=np.float64)
    envelope = ((cumulative[window:] - cumulative[:-window])[:length] / window).astype(np.float32)
    del cumulative
    music_path = ROOT / script['render']['music_path']
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    decoded = subprocess.run([ffmpeg, '-v', 'error', '-i', str(music_path), '-t', str(length / RATE + .1), '-f', 'f32le', '-ac', '2', '-ar', str(RATE), '-'], check=True, capture_output=True).stdout
    music = np.frombuffer(decoded, dtype='<f4').reshape(-1, 2).copy()
    del decoded
    if len(music) < length:
        crossfade = script['render'].get('music_loop_crossfade_seconds')
        if crossfade is None:
            raise ValueError('Music is shorter than video; choose an explicit loop/edit in the script')
        music = loop_music(music, length, crossfade)
    music = music[:length]
    music *= .16 / max(np.sqrt(np.mean(music ** 2)), .001)
    fade = np.ones(length, dtype=np.float32)
    fade[:2 * RATE] = np.linspace(0, 1, 2 * RATE)
    fade[-3 * RATE:] = np.linspace(1, 0, 3 * RATE)
    mixed = voice[:, None] + music * (envelope * fade)[:, None]
    peak = float(np.max(np.abs(mixed)))
    if peak >= .95:
        raise ValueError('Mix needs more headroom')
    sf.write(output, mixed, RATE, subtype='PCM_24')
    return dict(seconds=length / RATE, sample_rate=RATE, channels=2, peak=peak,
                music_gain_under_speech=.025 * music_gain, music_gain_between_sentences=.07 * music_gain,
                music_gain_adjustment_db=music_adjustment_db,
                music_loop_crossfade_seconds=script['render'].get('music_loop_crossfade_seconds'),
                active_speech_rms_target=.13, speech_peak_ceiling=.70)


def panel(image, size, photo=False):
    if photo:
        return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    result = Image.new('RGB', size, '#dfebeb')
    fitted = ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)
    result.paste(fitted, ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2))
    return result


def background_extent(size, progress, style):
    """Continuous fractional crop coordinates, independent of sentence boundaries."""
    t = min(1., max(0., progress))
    if style.get('motion_cycles'):
        t = .5 + .5 * math.sin(2 * math.pi * style['motion_cycles'] * t)
    zoom = style['zoom_start'] + (style['zoom_end'] - style['zoom_start']) * t
    width, height = size[0] / zoom, size[1] / zoom
    start = style.get('pan_start', [.35, .45])
    end = style.get('pan_end', [.65, .55])
    left = (size[0] - width) * (start[0] + (end[0] - start[0]) * t)
    top = (size[1] - height) * (start[1] + (end[1] - start[1]) * t)
    return left, top, left + width, top + height


def prepare_background(image, style):
    base = ImageOps.fit(image, (2200, 1238), method=Image.Resampling.LANCZOS)
    base = base.filter(ImageFilter.GaussianBlur(style['blur_pixels']))
    return Image.blend(base, Image.new('RGB', base.size, BG), style['darken'])


def background_frame(base, progress, style):
    return base.transform((W, H), Image.Transform.EXTENT,
                          background_extent(base.size, progress, style),
                          resample=Image.Resampling.BICUBIC).convert('RGBA')


def make_card(script, item, rows, images):
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    if item['kind'] == 'title':
        draw.rectangle((100, 330, 1820, 700), fill=(16, 46, 43, 175))
        title_face = fitted_font(script['title_sv'], 94, 1640, True, minimum=48)
        y = text_block(draw, script['title_sv'], (140, 400), title_face, 1640, FG, 112)
        text_block(draw, script['title_ru'], (144, y + 28), font(46), 1600, MUTED, 58)
        draw.rectangle((144, 350, 250, 358), fill=GOLD)
        return canvas, None
    if item['kind'] == 'credits':
        draw.rectangle((65, 65, 1855, 1005), fill=(16, 46, 43, 228))
        credit = script['render']['credits'][item['index']]
        draw.text((120, 105), credit['heading'], font=font(50, True), fill=FG)
        y = 225
        for paragraph in credit['paragraphs']:
            y = text_block(draw, paragraph, (120, y), font(32), 1670, MUTED, 44) + 30
        if y > 980:
            raise ValueError('Credits overflow')
        return canvas, None
    draw.rounded_rectangle((890, 165, 1860, 980), radius=20, fill=(16, 46, 43, 225))
    row = rows[item['sentence_id']]
    index = script['sentences'].index(row)
    draw.text((90, 65), script['title_sv'], font=fitted_font(script['title_sv'], 30, 1550, True), fill=MUTED)
    draw.text((1740, 65), f'{index + 1:02d} / {len(rows):02d}', font=font(27), fill=MUTED)
    draw.line((90, 125, 1830, 125), fill='#35534b', width=2)
    picture = row['render_image']
    is_photo = bool(picture and Path(picture).suffix.lower() in ('.jpg', '.jpeg', '.webp'))
    if picture:
        canvas.paste(panel(images[picture], (760, 720), is_photo), (90, 180))
    sv_size, ru_size, sv_leading, ru_leading = sentence_style(row)
    sv_lines = wrap(row['sv'], font(sv_size, True), 900)
    ru_lines = wrap(row['ru'], font(ru_size), 900)
    height = len(sv_lines) * sv_leading + len(ru_lines) * ru_leading + 56
    if height > 750:
        raise ValueError('Bilingual text exceeds panel: ' + row['sentence_id'])
    y = max(205, 535 - height // 2)
    y = text_block(draw, row['sv'], (930, y), font(sv_size, True), 900, FG, sv_leading, row['text_highlights'])
    draw.line((930, y + 20, 1010, y + 20), fill=GOLD, width=3)
    y = text_block(draw, row['ru'], (930, y + 56), font(ru_size), 900, MUTED, ru_leading)
    if y > 960:
        raise ValueError('Text bottom overflow')
    if row['text_highlights'] and row.get('render_caption', True):
        highlight = ' · '.join(row['text_highlights'])
        face = fitted_font(highlight, 38 if len(highlight) < 25 else 27, 760, True, minimum=24)
        draw.text((470, 950), highlight, font=face, fill=GOLD, anchor='mm')
    step = min(65, 900 / len(rows))
    for n in range(len(rows)):
        x = 930 + n * step
        draw.rounded_rectangle((x, 1000, x + step * .69, 1005), radius=2, fill=GOLD if n <= index else '#35534b')
    return canvas, picture if is_photo else None


def write_credits(episode, output):
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    sources = yaml.safe_load((episode / 'sources.yaml').read_text())
    assets = yaml.safe_load((episode / 'assets.yaml').read_text())
    lines = [f"# {script['title_sv']} — source and media credits", '',
             'Keep this file with the video. Source texts and media retain their own terms.', '',
             '## Text sources', '']
    for record in sources['sources']:
        source, attribution = record['source'], record['attribution']
        title = source.get('title', attribution['title'])
        url = source.get('source_url') or attribution.get('url')
        label = f'[{title}]({url})' if url else title
        lines += [f"### {title}", '', f"{attribution['credit']}. {label}.", '',
                  attribution['license'], '', attribution.get('publication_note', ''), '',
                  'Source preparation: ' + attribution.get('changes', ''), '']
        if attribution.get('license_url'):
            lines += [f"[License]({attribution['license_url']})", '']
    lines += ['The video preserves the Swedish wording and supplies the existing Russian translation,',
              'bilingual presentation and synthetic narration. Speech-only number/abbreviation expansions',
              'are recorded in the episode script. No endorsement by the sources is implied.', '', '## Media', '']
    for asset in assets['assets']:
        lines += [f"### {asset['asset_id']}", '', asset['required_credits'], '', asset['reuse_terms'], '']
        if asset.get('source_url'):
            url = asset['source_url']
            label = f'[Source]({url})' if url.startswith(('https://', 'http://')) else f'Repository source: `{url}`'
            lines += [label, '']
    lines += ['## Adaptations in this video', '']
    notes = script['render'].get('adaptation_notes', [
        'The selected background is cropped, softly blurred, darkened and continuously panned/zoomed.',
        'Foreground images remain steady. Music is excerpted, faded and reduced under narration.',
        'Source media retain the licenses and adaptation notices listed above.'])
    for note in notes:
        lines += [note, '']
    content = '\n'.join(lines)
    (episode / 'CREDITS.md').write_text(content)
    (output / (export_stem(episode.name) + '.CREDITS.md')).write_text(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('--stills-only', action='store_true')
    args = parser.parse_args()
    episode = ROOT / 'studio/episodes' / args.section
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    output = ROOT / 'studio/media' / args.section / 'render'
    output.mkdir(parents=True, exist_ok=True)
    deliverables = ROOT / 'videos/homebrew'
    deliverables.mkdir(parents=True, exist_ok=True)
    write_credits(episode, deliverables)
    rows = {r['sentence_id']: r for r in script['sentences']}
    images = {p: Image.open(ROOT / p).convert('RGB') for p in {r['render_image'] for r in rows.values() if r['render_image']} | {script['render']['background_image']}}
    timeline, frames = build_timeline(script)
    style = script['render']['background_style']
    backdrop = prepare_background(images[script['render']['background_image']], style)
    cards = []
    for i, item in enumerate(timeline):
        card, photo = make_card(script, item, rows, images)
        still = Image.alpha_composite(background_frame(backdrop, (item['start_frame'] + item['frames'] / 2) / (frames - 1), style), card)
        still.convert('RGB').save(output / f'frame-{i:02d}.png')
        cards.append((card, photo))
    (output / 'timeline.json').write_text(json.dumps(timeline, indent=2) + '\n')
    if args.stills_only:
        print('All text fits; review frames saved to', output)
        return
    mix = mix_audio(script, timeline, frames, output / 'mix.wav')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    destination = deliverables / (export_stem(args.section) + '.mp4')
    temporary = output / 'rendering.mp4'
    command = [ffmpeg, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', str(output / 'mix.wav'), '-c:v', 'libx264', '-threads', '2', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-frames:v', str(frames), str(temporary)]
    with (output / 'encode.log').open('w') as log:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
        try:
            previous = None
            for i, (item, (card, photo)) in enumerate(zip(timeline, cards)):
                for frame in range(item['frames']):
                    overlay = card
                    if previous is not None and item['kind'] == 'sentence' and timeline[i - 1]['kind'] == 'sentence' and frame < 6:
                        overlay = card.copy()
                        overlay.paste(Image.blend(previous.crop((90, 180, 850, 900)), card.crop((90, 180, 850, 900)), (frame + 1) / 6), (90, 180))
                    progress = (item['start_frame'] + frame) / max(1, frames - 1)
                    current = Image.alpha_composite(background_frame(backdrop, progress, style), overlay)
                    process.stdin.write(current.convert('RGB').tobytes())
                previous = card
                print(f'Encoded {i + 1}/{len(cards)}: {item.get("sentence_id", item["kind"])}', flush=True)
            process.stdin.close()
            if process.wait() != 0:
                raise RuntimeError((output / 'encode.log').read_text())
        except BaseException:
            process.kill()
            process.wait()
            raise
    temporary.replace(destination)
    for item in timeline:
        if item['kind'] == 'sentence':
            rows[item['sentence_id']]['start_seconds'] = round(item['speech_start_seconds'], 6)
            rows[item['sentence_id']]['end_seconds'] = round(item['speech_end_seconds'], 6)
    (episode / 'script.yaml').write_text(yaml.safe_dump(script, sort_keys=False, allow_unicode=True, width=100))
    report = dict(output=str(destination.relative_to(ROOT)), sha256=hashlib.sha256(destination.read_bytes()).hexdigest(), width=W, height=H, fps=FPS, frames=frames, seconds=frames/FPS, audio=mix, timeline=timeline, review_status='preview; user audiovisual review pending')
    (episode / 'render.json').write_text(json.dumps(report, indent=2) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
