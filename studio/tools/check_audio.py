"""Transcribe local audition WAVs for comparison; ASR does not replace listening."""
import argparse
import json
import math
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folders', nargs='+', type=Path)
    args = parser.parse_args()
    model = WhisperModel(str(ROOT / 'studio/media/models/whisper-small'), device='cpu', compute_type='int8', cpu_threads=4, local_files_only=True)
    for folder in args.folders:
        folder = folder.resolve()
        records = []
        for path in sorted(folder.glob('*.wav')):
            waveform, rate = sf.read(path, dtype='float32')
            divisor = math.gcd(rate, 16000)
            waveform = resample_poly(waveform, 16000 // divisor, rate // divisor).astype(np.float32)
            segments, _ = model.transcribe(waveform, language='sv', beam_size=5, vad_filter=False, condition_on_previous_text=False)
            text = ''.join(segment.text for segment in segments).strip()
            records.append({'file': str(path.relative_to(ROOT)), 'asr_text': text})
            print(path.name, text, flush=True)
            (folder / 'asr.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
