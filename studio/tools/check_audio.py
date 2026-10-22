"""Transcribe local audition WAVs for comparison; ASR does not replace listening."""
import argparse
import json
import math
import hashlib
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folders', nargs='+', type=Path)
    parser.add_argument('--pattern', default='*.wav', help='Filename glob for selected takes')
    parser.add_argument('--language', default='sv', choices=['sv', 'ru'])
    parser.add_argument('--threads', type=int, default=4,
                        help='CPU threads; use 1 while other episodes are synthesizing')
    parser.add_argument('--resume', action='store_true',
                        help='Reuse transcripts only when their recorded WAV checksum still matches')
    args = parser.parse_args()
    if args.threads < 1:
        parser.error('--threads must be positive')
    model = WhisperModel(str(ROOT / 'studio/media/models/whisper-small'), device='cpu', compute_type='int8', cpu_threads=args.threads, local_files_only=True)
    for folder in args.folders:
        folder = folder.resolve()
        records = []
        report = folder / 'asr.json'
        previous = {r['file']: r for r in json.loads(report.read_text())} if args.resume and report.exists() else {}
        for path in sorted(folder.glob(args.pattern)):
            relative = str(path.relative_to(ROOT))
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            if previous.get(relative, {}).get('sha256') == checksum and previous[relative].get('language', 'sv') == args.language:
                records.append(previous[relative])
                continue
            waveform, rate = sf.read(path, dtype='float32')
            if waveform.ndim == 2:
                waveform = waveform.mean(axis=1)
            divisor = math.gcd(rate, 16000)
            waveform = resample_poly(waveform, 16000 // divisor, rate // divisor).astype(np.float32)
            segments, _ = model.transcribe(waveform, language=args.language, beam_size=5, vad_filter=False, condition_on_previous_text=False)
            text = ''.join(segment.text for segment in segments).strip()
            records.append({'file': relative, 'sha256': checksum, 'language': args.language, 'asr_text': text})
            print(path.name, text, flush=True)
            (folder / 'asr.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
        report.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
