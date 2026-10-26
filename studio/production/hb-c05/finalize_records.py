"""Reconcile Chapter 5 deliverable records after all exports and reviews pass."""
from pathlib import Path
import hashlib, json, re
import numpy as np
import soundfile as sf
import yaml
ROOT = Path(__file__).resolve().parents[3]

def stamp(seconds):
    n = round(seconds)
    return f'{n // 3600}:{n // 60 % 60:02d}:{n % 60:02d}' if n >= 3600 else f'{n // 60}:{n % 60:02d}'

def main():
    inv = ROOT / 'studio/episodes.yaml'
    text = inv.read_text()
    entries = [e for e in yaml.safe_load(text)['episodes'] if e['chapter_id'] == 'hb-c05']
    assert len(entries) == 15
    rows = []
    music = []
    reviews = []
    for entry in entries:
        sid = entry['section_id']
        ep = ROOT / 'studio/episodes' / sid
        r = json.loads((ep / 'render.json').read_text())
        check = json.loads((ep / 'render-check.json').read_text())
        coverage = json.loads((ep / 'picture-coverage.json').read_text())
        independent = json.loads((ep / 'independent-export-review.json').read_text())
        assert check['full_decode'] == 'passed' and check['sha256'] == r['sha256'] == coverage['export_sha256']
        assert r['sha256'] in json.dumps(independent), 'Independent review must bind current export: ' + sid
        assert coverage['meets_target']
        assert yaml.safe_load((ep / 'brief.yaml').read_text())['production_status'] == 'preview_ready'
        entry.update(production_status='preview_ready', episode_path='studio/episodes/' + sid, issues=['Whole-video listening, physical-device checks and user acceptance pending; see episode review and listening priorities.'])
        text = re.sub('(?ms)^- section_id: ' + sid + '\\n.*?(?=^- section_id:|\\Z)', yaml.safe_dump([entry], allow_unicode=True, sort_keys=False, width=95), text)
        rows.append(dict(section_id=sid, order=entry['section_order'], title=entry['title_sv'], seconds=r['seconds'], output=r['output'], sha256=r['sha256'], picture_fraction=coverage['picture_fraction'], sentences=check['source_sentences']))
        assets = yaml.safe_load((ep / 'assets.yaml').read_text())['assets']
        script = yaml.safe_load((ep / 'script.yaml').read_text())
        path = ROOT / script['render']['music_path']
        info = sf.info(path)
        peak = 0.0
        positive = negative = 0
        for block in sf.blocks(path, blocksize=48000 * 10, dtype='float32', always_2d=True):
            assert np.isfinite(block).all()
            peak = max(peak, float(np.abs(block).max()))
            positive += int((block >= 1 - 2 ** (-23)).sum())
            negative += int((block <= -1).sum())
        assert positive == negative == 0
        music.append(dict(section_id=sid, path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), subtype=info.subtype, sample_rate=info.samplerate, channels=info.channels, frames=info.frames, peak=peak, positive_rail_samples=positive, negative_rail_samples=negative))
        semantic = next(ep / name for name in ('semantic-foreground-review.json', 'foreground-label-review.json') if (ep / name).exists())
        reviews.append(dict(section_id=sid, semantic_review=str(semantic.relative_to(ROOT)), export_sha256=r['sha256'], independent_review=str((ep / 'independent-export-review.json').relative_to(ROOT)), technical_report=str((ep / 'render-check.json').relative_to(ROOT)), picture_fraction=coverage['picture_fraction'], whole_video_listening=False, physical_device_playback=False, user_acceptance=False))
    inv.write_text(text)
    total = sum((r['seconds'] for r in rows))
    sentences = sum((r['sentences'] for r in rows))
    index = ROOT / 'videos/homebrew/README.md'
    old = index.read_text()
    block = '## Chapter 5 — Grundläggande rättigheter, jämlikhet och skyldigheter\n\n'
    block += '| Video and credits | Duration | Foreground pictures | Status |\n|---|---:|---:|---|\n'
    for r in rows:
        filename = Path(r['output']).name
        credits = Path(filename).stem + '.CREDITS.md'
        block += f'| [5.{r['order']} {r['title']}]({filename}) · [credits]({credits}) | {stamp(r['seconds'])} | {r['picture_fraction']:.1%} | Ready for whole-video review |\n'
    block += f'\nAll {sentences} exact Swedish/Russian sentence pairs are covered in {stamp(total)}, with\ndistinct background photographs and instrumental music sources. Every preview\nmeets the 50% foreground-picture target. Generated media remain local and ignored.\nSee the [chapter audit](../../studio/hb-c05-audit.json),\n[narration checks](../../studio/hb-c05-narration-check.json),\n[music headroom](../../studio/hb-c05-music-headroom.json),\n[export review records](../../studio/hb-c05-visual-review.json), and\n[listening priorities](../../studio/hb-c05-review.md). Whole-video listening,\nphysical-device playback and user acceptance remain pending.\n\n'
    if '## Chapter 5 —' in old:
        old = re.sub('(?ms)^## Chapter 5 —.*?(?=^## |\\Z)', block, old)
    else:
        old = old.replace('## Russian audio', block + '## Russian audio')
    index.write_text(old)
    (ROOT / 'studio/hb-c05-music-headroom.json').write_text(json.dumps(dict(method='Prepared music PCM rail/headroom check; original masters unchanged. Final mix retains accepted +2dB music adjustment.', episodes=15, results=music), indent=2) + '\n')
    (ROOT / 'studio/hb-c05-visual-review.json').write_text(json.dumps(dict(method='All 469 source-to-foreground assignments semantically reviewed, with corrections recorded. Representative planned and actual exported frames inspected by producers/coordinator and independent workers; technical checks bind current exports. Simulated small-screen images are not physical-device playback.', results=reviews), ensure_ascii=False, indent=2) + '\n')
    lines = ['# Chapter 5 — listening review', '', 'All 15 previews are technically verified. No whole-video listening, physical-device', 'playback or user acceptance is claimed. ASR can mishear correct speech: the', 'episode priorities are diagnostic uncertainties, not confirmed audible errors.', '', '| Episode | Duration | Detailed priorities |', '|---|---:|---|']
    for r in rows:
        slug = r['section_id']
        lines.append(f'| [5.{r['order']} {r['title']}](../{r['output']}) | {stamp(r['seconds'])} | [Sentence-level diagnostics](episodes/{slug}/listening-priorities.json) · [review](episodes/{slug}/review.md) |')
    lines += ['', 'Check Swedish compounds, Finnish authority names, ages, dates, percentages and', 'gestational week/day notation in context. The selected targeted retakes and', 'retained originals are recorded in episode retake histories. Review music beneath', 'speech on headphones and ordinary speakers, and reading comfort on the intended', 'devices. Exact archived source wording and reviewed Russian display remain intact.', '']
    (ROOT / 'studio/hb-c05-review.md').write_text('\n'.join(lines))
    p = ROOT / 'studio/README.md'
    s = p.read_text()
    paragraph = f'All fifteen Chapter 5 videos are rendered and technically verified, covering\n{sentences} exact Swedish/Russian sentence pairs in {stamp(total)}. Every preview meets\nthe 50% foreground-picture target. See the [chapter audit](hb-c05-audit.json),\n[export review records](hb-c05-visual-review.json), and\n[listening-review checklist](hb-c05-review.md). Whole-video listening and user\nacceptance remain pending; exports stay local and uncommitted.\n\n'
    if 'All fifteen Chapter 5 videos' not in s:
        s = s.replace('Asset production:', paragraph + 'Asset production:')
    p.write_text(s)
    print(json.dumps(dict(episodes=15, sentences=sentences, seconds=total, duration=stamp(total), min_picture_fraction=min((r['picture_fraction'] for r in rows))), indent=2))
if __name__ == '__main__':
    main()
