"""Decode the complete export and check its streams, frame count and timeline."""
import argparse
from contextlib import nullcontext
import hashlib
import json
from pathlib import Path

import av
import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parents[2]


def check_display_segments(row, item, fps):
    """Reject missing, stale, reordered, overlapping or gapped display chunks."""
    planned = row.get('display_segments', [])
    displayed = item.get('display_segments', [])
    if len(planned) != len(displayed):
        raise ValueError('Export lost display segments: ' + row['sentence_id'])
    for language in ('sv', 'ru'):
        if any(not s[language].strip() for s in planned):
            raise ValueError('Empty bilingual display segment: ' + row['sentence_id'])
        if planned and (' '.join(s[language] for s in planned).split() != row[language].split()):
            raise ValueError('Display segments change source text: ' + row['sentence_id'])
    cursor = item['start_frame']
    previous_offset = None
    for index, (source, timing) in enumerate(zip(planned, displayed)):
        if timing['index'] != index or any(timing[language] != source[language] for language in ('sv', 'ru')):
            raise ValueError('Export display text differs from script: ' + row['sentence_id'])
        if timing['start_frame'] != cursor or type(timing['frames']) is not int or timing['frames'] <= 0:
            raise ValueError('Display segment gap, overlap or empty interval: ' + row['sentence_id'])
        offset = source.get('speech_offset_seconds')
        duration = item['speech_end_seconds'] - item['speech_start_seconds']
        if type(offset) not in (int, float) or not 0 <= offset < duration or timing.get('speech_offset_seconds') != offset:
            raise ValueError('Stale display segment speech offset: ' + row['sentence_id'])
        if previous_offset is not None and round(offset*fps) <= round(previous_offset*fps):
            raise ValueError('Display segment speech offsets do not increase: ' + row['sentence_id'])
        previous_offset = offset
        expected = item['start_frame'] if index == 0 else round((item['speech_start_seconds'] + offset) * fps)
        if (index == 0 and offset != 0) or timing['start_frame'] != expected:
            raise ValueError('Display segment boundary differs from speech offset: ' + row['sentence_id'])
        cursor += timing['frames']
        for key, value in [('start_seconds', timing['start_frame']/fps), ('end_seconds', cursor/fps)]:
            actual = source.get(key)
            if type(actual) not in (int, float) or abs(actual-value) > .000001:
                raise ValueError('Script and export display timings disagree: ' + row['sentence_id'])
    if displayed and cursor != item['start_frame'] + item['frames']:
        raise ValueError('Display segments do not cover the complete sentence: ' + row['sentence_id'])
    return len(displayed)


def verify(section, save_frames=False):
    episode = ROOT / 'studio/episodes' / section
    report = json.loads((episode / 'render.json').read_text())
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    path = ROOT / report['output']
    if hashlib.sha256(path.read_bytes()).hexdigest() != report['sha256']:
        raise ValueError('Video differs from recorded export')
    speech = [t for t in report['timeline'] if t['kind'] == 'sentence']
    if [t['sentence_id'] for t in speech] != [r['sentence_id'] for r in script['sentences']]:
        raise ValueError('Timeline changed source order or lost sentences')
    segments_checked = 0
    for item, row in zip(speech, script['sentences']):
        for key, timeline_key in [('start_seconds', 'speech_start_seconds'), ('end_seconds', 'speech_end_seconds')]:
            if abs(row[key] - item[timeline_key]) > .000001:
                raise ValueError('Script and export timestamps disagree')
        if item['speech_start_seconds'] < item['start_frame'] / report['fps']:
            raise ValueError('Narration precedes its text')
        if item['speech_end_seconds'] > (item['start_frame'] + item['frames']) / report['fps']:
            raise ValueError('Narration extends beyond its displayed text')
        segments_checked += check_display_segments(row, item, report['fps'])
    scratch = ROOT / 'studio/media' / section / 'render'
    if save_frames:
        scratch.mkdir(parents=True, exist_ok=True)
    targets = {}
    for index, item in enumerate(report['timeline']):
        targets.setdefault(item['start_frame'] + item['frames']//2, []).append(f'{index:02d}')
        for segment in item.get('display_segments', []):
            label = f'{index:02d}-segment-{segment["index"]:02d}'
            targets.setdefault(segment['start_frame'] + segment['frames']//2, []).append(label)
    boundaries = {t['start_frame'] for t in report['timeline'][1:]}
    boundaries.update(segment['start_frame'] for item in speech for segment in item.get('display_segments', [])[1:])
    background_patches = {}
    opening_background = {}
    mix_path = scratch / 'mix.wav'
    audio_actual_energy = audio_reference_energy = audio_product = audio_error = 0.
    compared_audio_values = 0
    count, samples, peak, last_pts = 0, 0, 0., -1
    with av.open(str(path)) as container, (sf.SoundFile(mix_path) if mix_path.exists() else nullcontext(None)) as reference:
        if reference is not None and (reference.samplerate != 48000 or reference.channels != 2 or abs(reference.frames / 48000 - report['seconds']) > .05):
            raise ValueError('Mix master format or duration differs from the export')
        if len(container.streams.video) != 1 or len(container.streams.audio) != 1:
            raise ValueError('Expected one video and one audio stream')
        video, audio = container.streams.video[0], container.streams.audio[0]
        if (video.width, video.height, float(video.average_rate)) != (1920, 1080, 24):
            raise ValueError('Unexpected resolution or frame rate')
        if audio.codec_context.sample_rate != 48000 or audio.codec_context.channels != 2:
            raise ValueError('Unexpected audio format')
        for frame in container.decode():
            if isinstance(frame, av.VideoFrame):
                if frame.pts <= last_pts:
                    raise ValueError('Video timestamps are not strictly increasing')
                last_pts = frame.pts
                if save_frames and count in targets:
                    image = frame.to_image()
                    for label in targets[count]:
                        image.save(scratch / f'export-frame-{label}.png')
                    if '03' in targets[count]:
                        image.resize((960, 540)).save(scratch / 'phone-preview.png')
                if script['render'].get('background_image') and (count in boundaries or count + 1 in boundaries):
                    background_patches[count] = np.asarray(frame.to_image().crop((0, 200, 55, 800)), dtype=np.float32)
                if script['render'].get('background_image') and count in (0, 120, 240):
                    opening_background[count] = np.asarray(frame.to_image().crop((0, 200, 55, 800)), dtype=np.float32)
                count += 1
            else:
                samples += frame.samples
                peak = max(peak, float(np.max(np.abs(frame.to_ndarray()))))
                if reference is not None:
                    decoded = frame.to_ndarray()
                    decoded = decoded.T if frame.format.is_planar else decoded.reshape(-1, 2)
                    expected = reference.read(frame.samples, dtype='float32', always_2d=True)
                    length = min(len(decoded), len(expected))
                    decoded, expected = decoded[:length].astype(np.float64), expected[:length].astype(np.float64)
                    audio_actual_energy += float(np.sum(decoded ** 2))
                    audio_reference_energy += float(np.sum(expected ** 2))
                    audio_product += float(np.sum(decoded * expected))
                    audio_error += float(np.sum((decoded - expected) ** 2))
                    compared_audio_values += decoded.size
    if count != report['frames']:
        raise ValueError('Decoded frame count differs from planned export')
    if abs(samples / 48000 - report['seconds']) > .05:
        raise ValueError('Audio/video duration mismatch')
    if peak >= 1 or peak < .01:
        raise ValueError('Decoded audio clips or is effectively silent')
    audio_reference_check = None
    if compared_audio_values:
        if compared_audio_values < (samples - 2400) * 2:
            raise ValueError('Mix master does not cover the decoded audio')
        correlation = audio_product / max((audio_actual_energy * audio_reference_energy) ** .5, 1e-12)
        relative_error = (audio_error / max(audio_reference_energy, 1e-12)) ** .5
        if correlation < .98 or relative_error > .1:
            raise ValueError('Encoded audio differs from the current mix master')
        audio_reference_check = dict(correlation=correlation, relative_rms_error=relative_error,
                                    mix_sha256=hashlib.sha256(mix_path.read_bytes()).hexdigest())
    boundary_change = None
    if background_patches:
        boundary_change = max(float(np.mean(np.abs(background_patches[n] - background_patches[n - 1]))) for n in boundaries)
        if boundary_change > 6:
            raise ValueError('Unexpected background jump at a card boundary')
    opening_change = None
    if len(opening_background) == 3:
        opening_change = {str(n / report['fps']): float(np.mean(np.abs(opening_background[n] - opening_background[0]))) for n in (120, 240)}
        if max(opening_change.values()) < .05:
            raise ValueError('Decorative background appears static over the opening ten seconds')
    result = dict(background_boundary_max_mean_pixel_change=boundary_change, full_decode='passed', decoded_video_frames=count, decoded_audio_seconds=samples / 48000,
                  decoded_audio_peak=peak, frame_exports=sum(map(len, targets.values())) if save_frames else 0,
                  source_sentences=len(speech), output=report['output'], sha256=report['sha256'],
                  display_segments_checked=segments_checked,
                  opening_background_mean_pixel_change=opening_change,
                  encoded_audio_matches_mix=audio_reference_check,
                  listening_review='Review as part of the complete video; no standalone approval gate.')
    (episode / 'render-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('--save-frames', action='store_true')
    args = parser.parse_args()
    verify(args.section, args.save_frames)
