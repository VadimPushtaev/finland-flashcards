"""Generate repeatable local TTS candidates using the isolated studio runtime."""
import argparse
import json
import time
import wave
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engine', choices=['supertonic', 'alma', 'omnivoice'])
    parser.add_argument('--voice', default='F1')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--section', default='hb-c01-lage')
    parser.add_argument('--speed', type=float, default=.85)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--indices', default='0,2,8,11,12,13')
    args = parser.parse_args()
    script = yaml.safe_load((ROOT / 'studio/episodes' / args.section / 'script.yaml').read_text())
    rows = script['sentences']
    if not args.all:
        rows = [rows[i] for i in map(int, args.indices.split(','))]
    output = args.output or ROOT / 'studio/media' / args.section / 'auditions' / (args.engine + '-' + args.voice)
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    models = ROOT / 'studio/media/models'
    np.random.seed(42)
    if args.engine == 'supertonic':
        from supertonic import TTS
        model = TTS(model_dir=models / 'supertonic3', auto_download=False, intra_op_num_threads=4)
        style = model.get_voice_style(args.voice)
    elif args.engine == 'alma':
        from piper import PiperVoice, SynthesisConfig
        model = PiperVoice.load(str(models / 'alma/sv_SE-alma-medium.onnx'))
    else:
        import torch
        from omnivoice import OmniVoice
        torch.manual_seed(42)
        model = OmniVoice.from_pretrained(str(models / 'omnivoice'), device_map='mps', dtype=torch.float16)
    records = []
    reference = None
    for row in rows:
        text = (row.get('speech_override') or {}).get('text', row['sv'])
        path = output / (row['sentence_id'] + '.wav')
        start = time.monotonic()
        if args.engine == 'supertonic':
            audio, duration = model.synthesize(text, voice_style=style, lang='sv', total_steps=32, speed=args.speed)
            audio = audio.flatten()
            rate = model.sample_rate
            sf.write(path, audio, rate, subtype='PCM_16')
        elif args.engine == 'alma':
            with wave.open(str(path), 'wb') as handle:
                model.synthesize_wav(text, handle, syn_config=SynthesisConfig(length_scale=1.45, noise_scale=.8, noise_w_scale=.6, volume=.8))
        else:
            options = {'instruct': 'female'} if reference is None else {'ref_audio': str(reference), 'ref_text': rows[0]['sv']}
            audio = model.generate(text=text, language='sv', speed=args.speed, num_step=32, **options)[0]
            sf.write(path, audio, 24000, subtype='PCM_16')
            if reference is None:
                reference = path
        data, rate = sf.read(path)
        record = dict(sentence_id=row['sentence_id'], text=text, engine=args.engine, voice=args.voice, speed=args.speed, seed=42, path=str(path.relative_to(ROOT)), sample_rate=rate, seconds=len(data)/rate, peak=float(np.max(np.abs(data))), generation_seconds=time.monotonic()-start)
        records.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
        (output / 'metrics.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
