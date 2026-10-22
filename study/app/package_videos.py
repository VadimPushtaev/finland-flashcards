"""Package bilingual exports as HLS with one shared, unchanged video stream."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def duration(path):
    """Read media duration for a basic narration alignment check."""
    result = subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'json', str(path),
    ], text=True)
    return float(json.loads(result)['format']['duration'])


def package(source, destination):
    """Build a new serving directory; never alter source exports."""
    source, destination = source.resolve(), destination.resolve()
    if destination.exists():
        raise ValueError('Output directory must not exist; choose a new directory.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        output = Path(temporary) / 'videos'
        output.mkdir()
        for video in sorted(source.glob('*.mp4')):
            russian = video.with_suffix('.ru.m4a')
            credits = video.with_suffix('.CREDITS.md')
            if credits.is_file():
                shutil.copyfile(credits, output / credits.name)
            if not russian.is_file():
                shutil.copyfile(video, output / video.name)
                continue
            if abs(duration(video) - duration(russian)) > 1:
                raise ValueError(f'{russian.name}: narration must match video duration within one second.')
            folder = output / video.stem
            folder.mkdir()
            for name, media, stream in [('video', video, '0:v:0'), ('sv', video, '0:a:0'), ('ru', russian, '0:a:0')]:
                subprocess.run([
                    'ffmpeg', '-v', 'error', '-nostdin', '-i', str(media),
                    '-map', stream, '-c', 'copy', '-f', 'hls', '-hls_time', '6',
                    '-hls_playlist_type', 'vod', '-hls_segment_type', 'fmp4',
                    '-hls_flags', 'single_file', '-hls_segment_filename', f'{name}.m4s',
                    f'{name}.m3u8',
                ], cwd=folder, check=True)
            tracks = [('sv', 'Svenska'), ('ru', 'Русский')]
            for filename, languages in [('master', tracks), ('master-sv', tracks[:1]), ('master-ru', tracks[1:])]:
                lines = ['#EXTM3U', '#EXT-X-VERSION:7']
                for index, (language, label) in enumerate(languages):
                    lines.append(f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{label}",LANGUAGE="{language}",DEFAULT={"YES" if index == 0 else "NO"},AUTOSELECT=YES,URI="{language}.m3u8"')
                lines += ['#EXT-X-STREAM-INF:BANDWIDTH=10000000,AUDIO="audio"', 'video.m3u8']
                (folder / f'{filename}.m3u8').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        output.rename(destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    package(args.source, args.destination)
