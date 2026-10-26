"""Exercise deployment with real Git/rsync and local SSH/Docker stand-ins."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import deploy_over_ssh as deployment

VIDEO = 'videos/homebrew/hb-c01-01-lage.mp4'
CREDITS = 'videos/homebrew/hb-c01-01-lage.CREDITS.md'


@unittest.skipUnless(shutil.which('rsync'), 'rsync is required for deployment tests')
class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.local = base / 'local'
        self.remote = base / "remote ' $(touch INJECTED)"
        self.origin = base / 'origin.git'
        self.log = base / 'docker.json'
        self.local.mkdir()
        self.git(base, 'init', '--bare', str(self.origin))
        self.git(self.local, 'init', '-b', 'main')
        self.git(self.local, 'config', 'user.name', 'Deployment test')
        self.git(self.local, 'config', 'user.email', 'test@example.invalid')
        self.git(self.local, 'remote', 'add', 'origin', str(self.origin))
        self.put('.gitignore', '*.mp4\n.media-sync.json\n.env\n')
        self.put('app.txt', 'old code')
        self.put(CREDITS, 'old credits')
        self.put('studio/tools/sync_media.py',
                 (deployment.ROOT / 'studio/tools/sync_media.py').read_text())
        self.commit('Initial version')
        self.old = self.git(self.local, 'rev-parse', 'HEAD')
        self.git(self.local, 'push', 'origin', 'main')
        self.git(base, 'clone', '-b', 'main', str(self.origin), str(self.remote))
        self.put('app.txt', 'requested code')
        self.put(CREDITS, 'requested credits')
        self.commit('Requested version')
        self.requested = self.git(self.local, 'rev-parse', 'HEAD')
        self.git(self.local, 'push', 'origin', 'main')
        self.put(VIDEO, 'video bytes')

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
    args = args[2:]
args.pop(0)
sys.exit(subprocess.call(' '.join(args), shell=True))
''')
        ssh.chmod(0o755)
        docker = bin_dir / 'docker'
        docker.write_text('''#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
if sys.argv[1:] == ['compose', 'version']:
    sys.exit(0)
root = pathlib.Path.cwd()
pathlib.Path(os.environ['DEPLOY_TEST_LOG']).write_text(json.dumps({
    'args': sys.argv[1:],
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'code': (root / 'app.txt').read_text(),
    'credits': (root / 'videos/homebrew/hb-c01-01-lage.CREDITS.md').read_text(),
    'video': (root / 'videos/homebrew/hb-c01-01-lage.mp4').read_text(),
}))
sys.exit(int(os.environ.get('DEPLOY_TEST_DOCKER_EXIT', '0')))
''')
        docker.chmod(0o755)
        env = patch.dict(os.environ, {
            'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'],
            'DEPLOY_TEST_LOG': str(self.log),
        })
        env.start()
        self.addCleanup(env.stop)

    def git(self, directory, *args):
        return subprocess.check_output(['git', '-C', str(directory), *args],
                                       text=True, stderr=subprocess.PIPE).strip()

    def put(self, name, text):
        path = self.local / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message):
        self.git(self.local, 'add', '.')
        self.git(self.local, 'commit', '-m', message)

    def deploy(self):
        deployment.deploy(self.local, 'testhost', str(self.remote))

    def test_exact_commit_assets_first_and_quoted_path(self):
        # The branch advances after the selected revision was created.
        self.put('app.txt', 'newer code that must not deploy')
        self.commit('Later version')
        self.git(self.local, 'push', 'origin', 'main')
        self.git(self.local, 'checkout', '--detach', self.requested)
        (self.remote / '.env').write_text('STUDY_PORT=12345\n')
        self.deploy()
        result = json.loads(self.log.read_text())
        self.assertEqual(result, {
            'args': ['compose', 'up', '--build', '-d'],
            'head': self.requested, 'code': 'requested code',
            'credits': 'requested credits', 'video': 'video bytes',
        })
        self.assertEqual((self.remote / '.env').read_text(), 'STUDY_PORT=12345\n')
        self.assertFalse((self.remote / 'INJECTED').exists())
        self.assertFalse(self.git(self.remote, 'status', '--porcelain', '--untracked-files=no'))
        self.assertTrue((self.remote / '.media-sync.json').is_file())

    def test_dirty_local_stops_before_contacting_remote(self):
        self.put('app.txt', 'uncommitted')
        with patch.object(deployment, 'ssh') as ssh:
            with self.assertRaisesRegex(ValueError, 'local tracked changes'):
                self.deploy()
        ssh.assert_not_called()

    def test_dirty_remote_stops_before_upload(self):
        (self.remote / 'app.txt').write_text('remote work')
        with self.assertRaises(subprocess.CalledProcessError):
            self.deploy()
        self.assertFalse((self.remote / VIDEO).exists())
        self.assertEqual((self.remote / 'app.txt').read_text(), 'remote work')
        self.assertFalse(self.log.exists())

    def test_sync_failure_never_checks_out_or_builds(self):
        (self.local / VIDEO).unlink()
        with self.assertRaises(subprocess.CalledProcessError):
            self.deploy()
        self.assertEqual(self.git(self.remote, 'rev-parse', 'HEAD'), self.old)
        self.assertFalse(self.log.exists())

    def test_unpushed_commit_never_builds(self):
        self.put('app.txt', 'unpublished code')
        self.commit('Not pushed')
        with self.assertRaises(subprocess.CalledProcessError):
            self.deploy()
        self.assertEqual(self.git(self.remote, 'rev-parse', 'HEAD'), self.old)
        self.assertFalse(self.log.exists())

    def test_build_failure_is_reported(self):
        with patch.dict(os.environ, {'DEPLOY_TEST_DOCKER_EXIT': '7'}):
            with self.assertRaises(subprocess.CalledProcessError) as error:
                self.deploy()
        self.assertEqual(error.exception.returncode, 7)


if __name__ == '__main__':
    unittest.main()
