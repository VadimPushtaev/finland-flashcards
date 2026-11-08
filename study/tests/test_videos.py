"""Verify real packaging, shared media, and serving without source MP4 copies."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app
from app.package_videos import package, prepare_mounted
from video_fixture import create_videos


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'Requires FFmpeg')
class VideoTests(unittest.TestCase):
    def test_mounted_packaging_reuse_failure_and_audio_removal(self):
        with tempfile.TemporaryDirectory() as directory:
            source, _ = create_videos(directory)
            video = source / 'hb-c01-01-lage.mp4'
            original = video.read_bytes()
            ordinary = source / 'hb-c01-02-befolkning.mp4'
            ordinary.write_bytes(original)
            source.chmod(0o700)
            video.chmod(0o600)
            prepare_mounted(source)
            self.assertEqual(source.stat().st_mode & 0o555, 0o555)
            self.assertEqual(video.stat().st_mode & 0o444, 0o444)
            link = video.with_suffix('')
            self.assertTrue(link.is_symlink())
            target = link.resolve()
            self.assertEqual(video.read_bytes(), original)
            self.assertFalse(ordinary.with_suffix('').exists())
            with patch('app.package_videos.package') as build:
                prepare_mounted(source)
                build.assert_not_called()
            with patch('app.main.VIDEO_DIR', source), patch.dict(os.environ, {
                'STUDY_DATABASE_PATH': str(Path(directory) / 'study.sqlite3'),
            }), TestClient(app) as client:
                base = '/api/chapters/hb-c01/sections/hb-c01-lage/video'
                self.assertEqual(client.get(base + '/hls/master-ru.m3u8').status_code, 200)
                self.assertEqual(client.get(base + '/hls/video.m4s',
                                           headers={'Range': 'bytes=0-15'}).status_code, 206)
            russian = video.with_suffix('.ru.m4a')
            audio = russian.read_bytes()
            russian.write_bytes(b'invalid changed audio')
            with self.assertRaises(subprocess.CalledProcessError):
                prepare_mounted(source)
            self.assertEqual(link.resolve(), target)
            self.assertTrue((link / 'master.m3u8').is_file())
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi',
                            '-i', 'sine=frequency=660:sample_rate=48000',
                            '-t', '20', '-c:a', 'aac', str(russian)], check=True)
            prepare_mounted(source)
            self.assertNotEqual(link.resolve(), target)
            self.assertTrue(target.is_dir())
            russian.write_bytes(audio)
            prepare_mounted(source)
            self.assertEqual(link.resolve(), target)
            russian.unlink()
            prepare_mounted(source)
            self.assertFalse(link.is_symlink())
            self.assertTrue(video.is_file())
            self.assertTrue(target.is_dir())

    def test_packaging_and_public_hls_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = create_videos(directory)
            self.assertTrue((source / 'hb-c01-01-lage.mp4').is_file())
            self.assertFalse((output / 'hb-c01-01-lage.mp4').exists())
            folder = output / 'hb-c01-01-lage'
            self.assertEqual({p.name for p in folder.glob('*.m4s')}, {'video.m4s', 'sv.m4s', 'ru.m4s'})
            for language in ['sv', 'ru']:
                master = (folder / f'master-{language}.m3u8').read_text()
                self.assertIn('video.m3u8', master)
                self.assertIn(f'URI="{language}.m3u8"', master)
            with patch('app.main.VIDEO_DIR', output), patch.dict(os.environ, {'STUDY_DATABASE_PATH': str(Path(directory) / 'test.sqlite3')}), TestClient(app) as client:
                base = '/api/chapters/hb-c01/sections/hb-c01-lage/video'
                video = client.get('/api/chapters/hb-c01').json()['videos']['hb-c01-lage']
                self.assertEqual(video['format'], 'hls')
                self.assertEqual([t['language'] for t in video['audio_tracks']], ['sv', 'ru'])
                self.assertEqual(client.get(video['url']).status_code, 200)
                self.assertEqual(client.get(video['credits_url']).status_code, 200)
                response = client.get(base + '/hls/video.m4s', headers={'Range': 'bytes=0-15'})
                self.assertEqual(response.status_code, 206)
                self.assertEqual(len(response.content), 16)
                self.assertEqual(client.get(base + '/hls/master.m3u8').headers['content-type'], 'application/vnd.apple.mpegurl')
                for name in ['missing.m4s', 'private.txt', '%2e%2e%2fmaster.m3u8']:
                    self.assertEqual(client.get(base + '/hls/' + name).status_code, 404)
            with self.assertRaises(ValueError):
                package(source, output)
            # A short narration must fail rather than silently desynchronize scenes.
            import subprocess
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=880',
                            '-t', '2', '-c:a', 'aac', str(source / 'hb-c01-01-lage.ru.m4a')], check=True)
            with self.assertRaisesRegex(ValueError, 'duration'):
                package(source, Path(directory) / 'invalid')
            self.assertFalse((Path(directory) / 'invalid').exists())
