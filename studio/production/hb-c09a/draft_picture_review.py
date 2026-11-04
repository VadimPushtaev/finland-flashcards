"""Pair future source text/pictures for review without fabricating audio/timing.

Outputs are internal draft sheets only. No episode, media, milestone, credits,
audio, timeline or export file is written by this helper.
"""
from pathlib import Path
import hashlib
import json
import sys
import time

from PIL import Image, ImageDraw
import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'studio/tools'))
import render

sections = ['radgivning', 'skydd', 'vardnad', 'skilsmassa', 'flersprakighet',
            'dodsfall', 'begravning', 'foraldraskap', 'familjetjanster',
            'barnskydd', 'vald', 'uppfostran']
report = dict(kind='Draft visual pairing only; no narration, timing, motion, credits or export approval.',
              episodes={}, started=time.time())
for slug in sections:
    sid = 'hb-c09-' + slug
    episode = ROOT / 'studio/episodes' / sid
    script_path = episode / 'script.yaml'
    script = yaml.safe_load(script_path.read_text())
    rows = {row['sentence_id']: row for row in script['sentences']}
    render.configure_style(script)
    paths = {row['render_image'] for row in rows.values()}
    background_path = script['render']['background_image']
    images = {path: Image.open(ROOT / path).convert('RGB')
              for path in paths | {background_path}}
    style = script['render']['background_style']
    backdrop = render.prepare_background(images[background_path], style)
    output = HERE / 'draft-picture-review' / sid
    output.mkdir(parents=True, exist_ok=True)
    contact = Image.new('RGB', (1536, ((len(rows) + 3) // 4) * 240), '#222222')
    draw = ImageDraw.Draw(contact)
    frames = []
    for index, row in enumerate(script['sentences'], 1):
        card, _ = render.make_card(script, dict(kind='sentence', sentence_id=row['sentence_id']),
                                   rows, images)
        frame = render.composite_rgb_frame(backdrop, .5, style,
                                            card.convert('RGB'), card.getchannel('A'))
        phone = output / f'draft-{index:03}.png'
        frame.resize((768, 432)).save(phone)
        thumbnail = frame.resize((384, 216))
        x = (index - 1) % 4 * 384
        y = (index - 1) // 4 * 240
        contact.paste(thumbnail, (x, y))
        draw.text((x + 3, y + 217), f'{index}: {row["sentence_id"]}', fill='white')
        frames.append(dict(sentence_id=row['sentence_id'],
                           draft_frame=str(phone.relative_to(ROOT)),
                           foreground_sha256=hashlib.sha256((ROOT / row['render_image']).read_bytes()).hexdigest()))
    contact.save(output / 'contact.jpg')
    report['episodes'][sid] = dict(frames=frames,
                                  source_script_snapshot_sha256=hashlib.sha256(script_path.read_bytes()).hexdigest(),
                                  paired_layout='passed actual renderer text/card functions',
                                  producer_visual_review='pending',
                                  audio_timing='not generated or asserted by this helper')
    (HERE / 'draft-picture-review-progress.json').write_text(json.dumps(report, indent=2) + '\n')
    print(sid, len(rows), 'draft pairings prepared; human source/image review remains.', flush=True)
report['completed'] = time.time()
(HERE / 'draft-picture-review-completed.json').write_text(json.dumps(report, indent=2) + '\n')
