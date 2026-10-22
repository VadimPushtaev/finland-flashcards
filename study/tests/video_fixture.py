"""Generate short, distinct audio tones for real bilingual playback tests."""
from pathlib import Path
import subprocess

from app.package_videos import package


def create_videos(root):
    """Build a small test-only export; no production narration is fabricated."""
    source = Path(root) / 'source'
    source.mkdir(parents=True)
    video = source / 'hb-c01-01-lage.mp4'
    subprocess.run([
        'ffmpeg', '-v', 'error', '-nostdin', '-f', 'lavfi', '-i', 'color=c=blue:s=320x180:r=24',
        '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000', '-t', '20',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-g', '48', '-c:a', 'aac', str(video),
    ], check=True)
    subprocess.run([
        'ffmpeg', '-v', 'error', '-nostdin', '-f', 'lavfi', '-i', 'sine=frequency=880:sample_rate=48000',
        '-t', '20', '-c:a', 'aac', str(video.with_suffix('.ru.m4a')),
    ], check=True)
    video.with_suffix('.CREDITS.md').write_text('Synthetic test tones; not Russian narration.', encoding='utf-8')
    destination = Path(root) / 'packaged'
    package(source, destination)
    return source, destination
