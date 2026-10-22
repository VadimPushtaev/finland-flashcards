"""Synthesize Russian speech and fit it to an existing, unchanged video timeline."""
import argparse
from copy import deepcopy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

import numpy as np
import soundfile as sf
import torch
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from studio.tools.render import mix_audio


def checksum(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_model(config):
    """Load the pinned local Russian model; no remote inference or auto-download."""
    path = ROOT / config['model_path']
    if checksum(path) != config['model_sha256']:
        raise ValueError('Russian model checksum differs from the production configuration.')
    torch.set_num_threads(config['threads'])
    return torch.package.PackageImporter(str(path)).load_pickle('tts_models', 'model')


def speech_text(row, config):
    """Keep displayed translations exact; apply only recorded pronunciation hints."""
    text = config['speech_overrides'].get(row['sentence_id'], {}).get('text', row['ru'])
    for original, stressed in config.get('pronunciation_replacements', {}).items():
        text = text.replace(original, stressed)
    return text


def synthesize(model, text, config, voice=None):
    """Generate one complete sentence with native Russian stress processing."""
    torch.manual_seed(config['seed'])
    with torch.inference_mode():
        audio = model.apply_tts(text=text, speaker=voice or config['voice'],
                                sample_rate=config['sample_rate'],
                                **{key: config[key] for key in ('put_accent', 'put_stress_homo', 'put_yo', 'put_yo_homo')})
    return audio.detach().cpu().numpy().flatten()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('--replace', action='store_true', help='Explicitly regenerate existing Russian takes and export')
    args = parser.parse_args()
    episode = ROOT / 'studio/episodes' / args.section
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    config_path = episode / 'russian-narration.yaml'
    config = yaml.safe_load(config_path.read_text())
    render_path = episode / 'render.json'
    render = json.loads(render_path.read_text())
    video = ROOT / render['output']
    target = video.with_suffix('.ru.m4a')
    if target.exists() and not args.replace:
        raise ValueError('Russian export already exists; use --replace only for an intentional retake.')
    if checksum(video) != render['sha256']:
        raise ValueError('Video changed; recheck its timeline before generating alternate audio.')
    translation_path = ROOT / script['translation_path']
    if checksum(translation_path) != script['translation_file_sha256']:
        raise ValueError('Translation changed; validate and update the script first.')
    translations = {row['source_id']: row['ru'] for row in yaml.safe_load(translation_path.read_text())['records']}
    for row in script['sentences']:
        if row['ru'] != translations[row['sentence_id']]:
            raise ValueError('Script differs from reviewed Russian: ' + row['sentence_id'])
    model = load_model(config)
    output = ROOT / 'studio/media' / args.section / 'narration-ru'
    raw_folder = output / 'raw'
    raw_folder.mkdir(parents=True, exist_ok=True)
    rows = {row['sentence_id']: row for row in script['sentences']}
    timeline = deepcopy(render['timeline'])
    if [item['sentence_id'] for item in timeline if item['kind'] == 'sentence'] != list(rows):
        raise ValueError('Video timeline and script must contain the same sentences in source order.')
    records = []
    for item in timeline:
        if item['kind'] != 'sentence':
            continue
        identity = item['sentence_id']
        row = rows[identity]
        text = speech_text(row, config)
        raw = raw_folder / f'{identity}.wav'
        start = time.monotonic()
        audio = synthesize(model, text, config)
        sf.write(raw, audio, config['sample_rate'], subtype='PCM_16')
        duration = sf.info(raw).duration
        deadline = (item['start_frame'] + item['frames']) / render['fps'] - config['scene_end_margin_seconds']
        budget = deadline - item['speech_start_seconds']
        tempo = max(1., duration / budget)
        if tempo > config['max_tempo']:
            raise ValueError(f'{identity} needs {tempo:.3f}x tempo; do not truncate narration to fit.')
        fitted = output / f'{identity}.wav'
        if tempo == 1:
            shutil.copyfile(raw, fitted)
        else:
            subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', str(raw),
                            '-af', f'atempo={tempo:.9f}', '-ar', str(config['sample_rate']),
                            '-c:a', 'pcm_s16le', str(fitted)], check=True)
        fitted_duration = sf.info(fitted).duration
        item['speech_end_seconds'] = item['speech_start_seconds'] + fitted_duration
        if item['speech_end_seconds'] > deadline + .05:
            raise ValueError(f'{identity} exceeds its scene deadline.')
        row['audio_path'] = str(fitted.relative_to(ROOT))
        samples, rate = sf.read(fitted)
        if not np.isfinite(samples).all() or np.max(np.abs(samples)) >= 1:
            raise ValueError('Invalid or clipped samples: ' + identity)
        record = dict(sentence_id=identity, text=text, source_ru=row['ru'],
                      raw_path=str(raw.relative_to(ROOT)), raw_sha256=checksum(raw),
                      path=row['audio_path'], sha256=checksum(fitted),
                      raw_seconds=duration, seconds=fitted_duration, tempo=tempo,
                      start_seconds=item['speech_start_seconds'], end_seconds=item['speech_end_seconds'],
                      scene_deadline_seconds=deadline, sample_rate=rate,
                      peak=float(np.max(np.abs(samples))), generation_seconds=time.monotonic()-start)
        records.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
        (output / 'metrics.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    mix_path = output / 'mix.wav'
    mix = mix_audio(script, timeline, render['frames'], mix_path)
    subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-y', '-i', str(mix_path),
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(target)], check=True)
    report = dict(language='ru', output=str(target.relative_to(ROOT)), sha256=checksum(target),
                  video_sha256=checksum(video), video_unchanged=checksum(video) == render['sha256'],
                  translation_sha256=checksum(translation_path), timeline_sha256=checksum(render_path),
                  config_sha256=checksum(config_path), config=config,
                  runtime={'python': platform.python_version(), 'platform': platform.platform(),
                           **{name: importlib.metadata.version(name) for name in ['torch', 'numpy', 'soundfile']}},
                  audio=mix, sentences=records, review_status='ready for listening review; not approved')
    (episode / 'russian-narration.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(str(target), flush=True)


if __name__ == '__main__':
    main()
