"""Exercise real rsync transfers through a local SSH stand-in, without a server."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from studio.tools import sync_media as media

VIDEO = 'videos/homebrew/hb-c01-01-lage.mp4'
CREDITS = 'videos/homebrew/hb-c01-01-lage.CREDITS.md'
WAV = 'studio/media/hb-c01-lage/narration/hb-c01-u0001-s001.wav'
METRICS = 'studio/media/hb-c01-lage/narration/metrics.json'


def put(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


@unittest.skipUnless(shutil.which('rsync'), 'rsync is required for transfer tests')
class MediaSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.source = base / 'source checkout'
        self.target = base / "target ' $(touch INJECTED)"
        self.source.mkdir()
        put(self.source, VIDEO, b'video contents' * 2000)
        put(self.source, CREDITS, b'Credits\n')
        put(self.source, WAV, b'narration bytes' * 2000)
        put(self.source, METRICS, json.dumps([{'path': WAV}]).encode())
        bin_dir = base / 'bin'
        bin_dir.mkdir()
        ssh = bin_dir / 'ssh'
        ssh.write_text('''#!/usr/bin/env python3
import subprocess, sys
args = sys.argv[1:]
while args and args[0].startswith('-'):
    if args[0] == '--':
        args.pop(0)
        break
    args.pop(0)
    args.pop(0)
args.pop(0)  # host
sys.exit(subprocess.call(' '.join(args), shell=True))
''')
        ssh.chmod(0o755)
        self.env = patch.dict(os.environ, {'PATH': str(bin_dir) + os.pathsep + os.environ['PATH']})
        self.env.start()
        self.addCleanup(self.env.stop)

    def sync(self, **kwargs):
        media.sync(self.source, 'testhost', str(self.target), **kwargs)

    def test_upload_idempotence_restore_extras_and_quoted_paths(self):
        extra = 'videos/homebrew/hb-c99-01-extra.mp4'
        put(self.target, extra, b'remote only')
        put(self.source, 'studio/media/hb-c01-lage/render/scratch.wav', b'excluded')
        put(self.source, 'studio/media/hb-c01-lage/narration-party-retakes-01/metrics.json',
            b'[{"path": "discarded.wav"}]')
        put(self.source, 'studio/media/hb-c01-lage/narration-resumed/metrics.json',
            b'[{"path": "discarded.wav"}]')
        self.sync()
        media.verify(self.target, media.select_files(self.source))
        original_stat = (self.target / VIDEO).stat()
        self.sync()
        self.assertEqual(original_stat.st_mtime_ns, (self.target / VIDEO).stat().st_mtime_ns)
        self.assertTrue((self.target / extra).exists())
        self.assertFalse((self.target / 'studio/media/hb-c01-lage/render').exists())
        restore = self.source.parent / 'restore'
        restore.mkdir()
        put(restore, 'keep-local.txt', b'local only')
        media.sync(restore, 'testhost', str(self.target), pull=True)
        media.verify(restore, media.read_receipt(self.target))
        self.assertFalse((restore / extra).exists())
        self.assertEqual((restore / 'keep-local.txt').read_bytes(), b'local only')
        self.assertFalse(Path('INJECTED').exists())

    def test_read_only_modes_and_corruption_detection(self):
        self.sync(dry_run=True)
        self.assertFalse(self.target.exists())
        self.assertFalse((self.source / media.RECEIPT).exists())
        self.sync()
        receipt = (self.target / media.RECEIPT).read_bytes()
        self.sync(verify_only=True)
        put(self.target, VIDEO, b'corrupt')
        with self.assertRaisesRegex(ValueError, 'verification failed'):
            self.sync(verify_only=True)
        with self.assertRaises(subprocess.CalledProcessError):
            self.sync(pull=True)
        self.assertEqual(receipt, (self.target / media.RECEIPT).read_bytes())
        self.sync()
        self.assertEqual((self.source / VIDEO).read_bytes(), (self.target / VIDEO).read_bytes())

    def test_missing_source_rejected_before_transfer(self):
        (self.source / WAV).unlink()
        with self.assertRaises(FileNotFoundError):
            self.sync()
        self.assertFalse(self.target.exists())

    def test_missing_episode_and_export_detected(self):
        self.sync()
        shutil.rmtree(self.source / 'studio/media')
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            media.select_files(self.source)
        (self.source / media.RECEIPT).unlink()
        (self.source / VIDEO).unlink()
        with self.assertRaises(FileNotFoundError):
            media.select_files(self.source)

    def test_interrupted_transfer_keeps_receipt_and_resumes_partial(self):
        self.sync()
        receipt = (self.target / media.RECEIPT).read_bytes()
        put(self.source, VIDEO, b'new video' * 10000)
        partial = 'videos/homebrew/.rsync-partial/hb-c01-01-lage.mp4'
        put(self.target, partial, b'new video' * 500)
        with patch.object(media, 'transfer', side_effect=subprocess.CalledProcessError(23, 'rsync')):
            with self.assertRaises(subprocess.CalledProcessError):
                self.sync()
        self.assertEqual(receipt, (self.target / media.RECEIPT).read_bytes())
        self.sync()
        media.verify(self.target, media.select_files(self.source))
        self.assertFalse((self.target / partial).exists())

    def test_paths_symlinks_and_manifests_cannot_escape(self):
        manifest = media.select_files(self.source)
        for name in ('../escape.wav', '/tmp/escape.wav', 'videos/homebrew/../../escape.mp4'):
            with self.assertRaises(ValueError):
                media.safe_path(self.source, name)
        self.target.mkdir()
        (self.target / 'videos').symlink_to(self.source / 'videos', target_is_directory=True)
        with self.assertRaises(ValueError):
            media.worker({'root': str(self.target), 'action': 'prepare', 'manifest': manifest})
        with self.assertRaises(ValueError):
            media.validate_manifest({'version': 1, 'files': {}})
        (self.source / WAV).unlink()
        (self.source / WAV).symlink_to(self.source / VIDEO)
        with self.assertRaisesRegex(ValueError, 'Symlinks'):
            media.select_files(self.source)

    def test_failed_verification_never_publishes_receipt(self):
        manifest = media.select_files(self.source)
        put(self.source, WAV, b'changed after manifest')
        with self.assertRaisesRegex(ValueError, 'verification failed'):
            media.publish_receipt(self.source, manifest)
        self.assertFalse((self.source / media.RECEIPT).exists())


if __name__ == '__main__':
    unittest.main()
