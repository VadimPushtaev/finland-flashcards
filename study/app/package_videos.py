"""Package bilingual exports as HLS with one shared, unchanged video stream."""
import argparse
import hashlib
import json
import os
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


def prepare_mounted(source):
    """Prepare only bilingual HLS beside mounted originals, reusing unchanged media.

    Versioned output and an atomic symlink switch preserve the previous playable
    package if FFmpeg fails. Ordinary MP4s are served directly without copying.
    """
    source = source.resolve()
    source.mkdir(parents=True, exist_ok=True)
    # The runtime uses an unprivileged reader; host files may have been created
    # with a restrictive umask. Grant read/traverse access without copying bytes.
    for directory in (source.parent, source):
        directory.chmod(directory.stat().st_mode | 0o555)
    for pattern in ('*.mp4', '*.ru.m4a', '*.CREDITS.md'):
        for path in source.glob(pattern):
            path.chmod(path.stat().st_mode | 0o444)
    cache = source.parent / '.hls'
    for video in sorted(source.glob('*.mp4')):
        russian = video.with_suffix('.ru.m4a')
        if not russian.is_file():
            continue
        digest = hashlib.sha256(Path(__file__).read_bytes())
        for path in (video, russian):
            digest.update(str(path.stat().st_size).encode() + b'\0')
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(chunk)
        cache.mkdir(exist_ok=True)
        cache.chmod(cache.stat().st_mode | 0o555)
        target = cache / (video.stem + '-' + digest.hexdigest())
        link = video.with_suffix('')
        if link.exists() and not link.is_symlink():
            raise ValueError(f'Refusing to replace an existing directory: {link}')
        expected = [f'{name}.{suffix}' for name in ('video', 'sv', 'ru')
                    for suffix in ('m4s', 'm3u8')]
        expected += [f'{name}.m3u8' for name in ('master', 'master-sv', 'master-ru')]
        if not target.exists():
            print(f'Packaging bilingual video: {video.name}', flush=True)
            with tempfile.TemporaryDirectory(dir=cache) as temporary:
                temporary = Path(temporary)
                inputs = temporary / 'input'
                inputs.mkdir()
                for path in (video, russian):
                    (inputs / path.name).symlink_to(path)
                output = temporary / 'output'
                package(inputs, output)
                (output / video.stem).rename(target)
        if not all((target / name).is_file() for name in expected):
            raise ValueError(f'Incomplete HLS cache: {target}')
        target.chmod(target.stat().st_mode | 0o555)
        for name in expected:
            path = target / name
            path.chmod(path.stat().st_mode | 0o444)
        # The relative link works both on the host and inside the ./videos mount.
        relative = Path('..') / '.hls' / target.name
        if link.is_symlink() and link.readlink() == relative:
            continue
        with tempfile.TemporaryDirectory(dir=source) as temporary:
            replacement = Path(temporary) / 'link'
            replacement.symlink_to(relative)
            os.replace(replacement, link)
    # Removing alternate audio must restore ordinary MP4 playback. Only touch
    # links owned by this packager; retain old cached versions for active readers.
    for link in source.iterdir():
        if (link.is_symlink() and str(link.readlink()).startswith('../.hls/')
                and not (link.with_suffix('.mp4').is_file()
                         and link.with_suffix('.ru.m4a').is_file())):
            link.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path, nargs='?')
    parser.add_argument('--mounted', action='store_true',
                        help='Prepare incremental HLS in the mounted videos tree')
    args = parser.parse_args()
    if args.mounted:
        if args.destination is not None:
            parser.error('--mounted takes only the source directory')
        prepare_mounted(args.source)
    elif args.destination is None:
        parser.error('destination is required unless --mounted is used')
    else:
        package(args.source, args.destination)
