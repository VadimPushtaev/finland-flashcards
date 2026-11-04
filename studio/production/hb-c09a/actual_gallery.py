"""Prepare current decoded-export contact pages and simulated phone stills.

This records hashes only; generating a gallery does not establish inspection.
"""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('section')
parser.add_argument('--phones', required=True)
parser.add_argument('--width', type=int, default=768)
args = parser.parse_args()
assert args.section.startswith('hb-c09-') or args.section == 'hb-c11-nodsituationer'
episode = ROOT / 'studio/episodes' / args.section
record = json.loads((episode / 'render.json').read_text())
checks = json.loads((episode / 'render-check.json').read_text())
assert checks['sha256'] == record['sha256'] and checks['full_decode'] == 'passed'
assert checks['decoded_video_frames'] == record['frames']
frames = [ROOT / 'studio/media' / args.section / 'render' / f'export-frame-{index:02}.png'
          for index in range(len(record['timeline']))]
assert all(frame.is_file() for frame in frames)
output = HERE / (args.section.removeprefix('hb-c09-') + '-actual-gallery')
output.mkdir(exist_ok=True)
for start in range(0, len(frames), 20):
    page = frames[start:start + 20]
    canvas = Image.new('RGB', (1536, 5 * 241), '#222222')
    draw = ImageDraw.Draw(canvas)
    for offset, frame in enumerate(page):
        with Image.open(frame) as source:
            thumbnail = source.convert('RGB').resize((384, 216), Image.Resampling.LANCZOS)
        x, y = (offset % 4) * 384, (offset // 4) * 241
        canvas.paste(thumbnail, (x, y))
        draw.text((x + 4, y + 220), frame.stem, fill='white')
    canvas.save(output / f'contact-{start:02}.jpg', quality=94)
for index in map(int, args.phones.split(',')):
    with Image.open(frames[index]) as source:
        source.resize((args.width, round(source.height * args.width / source.width)),
                      Image.Resampling.LANCZOS).save(output / f'phone-{index:02}.png')
phone_indices = list(map(int, args.phones.split(',')))
phone_height = round(1080 * args.width / 1920)
for start in range(0, len(phone_indices), 4):
    canvas = Image.new('RGB', (args.width * 2, (phone_height + 24) * 2), '#222222')
    draw = ImageDraw.Draw(canvas)
    for offset, index in enumerate(phone_indices[start:start + 4]):
        with Image.open(output / f'phone-{index:02}.png') as source:
            x, y = (offset % 2) * args.width, (offset // 2) * (phone_height + 24)
            canvas.paste(source, (x, y))
            draw.text((x + 4, y + phone_height + 4), f'Actual export {index:02} at {args.width}px', fill='white')
    canvas.save(output / f'phones-{start:02}.jpg', quality=96)
proof = {'section_id': args.section, 'export_sha256': record['sha256'],
         'frame_sha256': {frame.name: hashlib.sha256(frame.read_bytes()).hexdigest()
                          for frame in frames},
         'phone_width': args.width, 'phone_frames': args.phones,
         'inspection_status': 'Prepared only; actual visual inspection must be performed separately.'}
(output / 'gallery-source-hashes.json').write_text(json.dumps(proof, indent=2) + '\n')
print(output.relative_to(ROOT), len(frames), 'actual cards prepared; no inspection claimed')
