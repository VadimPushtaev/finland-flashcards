#!/usr/bin/env python3
"""Upload Homebrew media and deploy this checkout's HEAD over SSH."""
import argparse
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DEFAULT_REMOTE_DIR = '/root/finland-flashcards'


def ssh(host, script):
    """Send a script on stdin without interpolating it into the remote shell."""
    subprocess.run(['ssh', '-o', 'BatchMode=yes', '--', host, 'sh -se'],
                   input=script, text=True, check=True)


def deploy(root, host, directory):
    """Sync assets, fetch the captured commit, then rebuild the remote service."""
    commit = subprocess.check_output(
        ['git', '-C', str(root), 'rev-parse', '--verify', 'HEAD^{commit}'], text=True,
    ).strip()
    dirty = subprocess.check_output(
        ['git', '-C', str(root), 'status', '--porcelain', '--untracked-files=no'], text=True,
    )
    if dirty:
        raise ValueError('Commit or stash local tracked changes before deploying HEAD.')

    # Check before uploading binaries; code and metadata are supplied by Git.
    cd = 'cd -- ' + shlex.quote(directory) + '\n'
    ssh(host, cd + '''
test "$(git rev-parse --show-toplevel)" = "$(pwd -P)" || {
    echo 'The remote directory must be the root of an existing Git checkout.' >&2
    exit 1
}
test -z "$(git status --porcelain --untracked-files=no)" || {
    echo 'Commit or stash remote tracked changes before deploying.' >&2
    exit 1
}
command -v docker >/dev/null
docker compose version >/dev/null
''')
    print(f'Uploading assets to {host}:{directory} for commit {commit}', flush=True)
    subprocess.run([
        sys.executable, str(root / 'studio/tools/sync_media.py'),
        '--host', host, '--remote-dir', directory,
    ], check=True)
    print(f'Deploying {commit}', flush=True)
    ssh(host, cd + f'''
export GIT_TERMINAL_PROMPT=0
git fetch --no-tags origin {shlex.quote(commit)}
git checkout --detach {shlex.quote(commit)}
test "$(git rev-parse HEAD)" = {shlex.quote(commit)}
test -z "$(git status --porcelain --untracked-files=no)" || {{
    echo 'Remote tracked files differ from the requested commit; build cancelled.' >&2
    exit 1
}}
docker compose up --build -d
''')
    print(f'Deployed {commit} to {host}:{directory}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, help='SSH alias or user@host')
    parser.add_argument('--remote-dir', default=DEFAULT_REMOTE_DIR,
                        help='absolute remote Git checkout directory (default: %(default)s)')
    args = parser.parse_args()
    if not re.fullmatch(r'(?:[a-zA-Z0-9_.-]+@)?[a-zA-Z0-9_][a-zA-Z0-9_.-]*', args.host):
        parser.error('--host must be an SSH alias or user@host; configure ports/IPv6 in SSH config')
    if (not args.remote_dir.startswith('/') or args.remote_dir == '/'
            or '..' in PurePosixPath(args.remote_dir).parts
            or any(ord(c) < 32 for c in args.remote_dir)):
        parser.error('--remote-dir must be an absolute repository directory, without ..')
    for executable in ('git', 'ssh', 'rsync'):
        if not shutil.which(executable):
            parser.error(f'{executable} is required locally')
    deploy(ROOT, args.host, args.remote_dir)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f'Deployment failed: {exc}', file=sys.stderr)
        sys.exit(1)
