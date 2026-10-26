#!/usr/bin/env python3
"""Copy retained Homebrew media over SSH, independently of Git (stdlib only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2] if '__file__' in globals() else None
RECEIPT = '.media-sync.json'
MANAGED = re.compile(
    r'(?:videos/homebrew/hb-c\d+-\d+-[a-z0-9-]+(?:\.mp4|\.[a-z]+\.m4a|\.CREDITS\.md)'
    r'|studio/media/hb-c\d+-[a-z0-9-]+/narration(?:-[a-z]{2,3})?/'
    r'(?:metrics\.json|(?:raw/)?hb-[a-z0-9-]+\.wav))\Z'
)


def safe_path(root, name):
    """Reject traversal and symlinks, including destination parent symlinks."""
    if not isinstance(name, str) or not MANAGED.fullmatch(name):
        raise ValueError(f'Not a managed media path: {name!r}')
    path = root
    for part in PurePosixPath(name).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f'Symlinks are not supported: {path}')
    return path


def file_record(path):
    before = path.stat()
    if not path.is_file() or before.st_size == 0:
        raise ValueError(f'Missing or empty file: {path}')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f'File changed during hashing: {path}')
    return {'size': after.st_size, 'sha256': digest.hexdigest()}


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get('version') != 1:
        raise ValueError('Unsupported media manifest')
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('Empty media manifest')
    for name, record in files.items():
        if not MANAGED.fullmatch(name):
            raise ValueError(f'Not a managed media path: {name!r}')
        if (not isinstance(record, dict) or type(record.get('size')) is not int
                or record['size'] <= 0
                or not re.fullmatch('[0-9a-f]{64}', str(record.get('sha256', '')))):
            raise ValueError(f'Invalid file record: {name}')
    return manifest


def read_receipt(root):
    path = root / RECEIPT
    if path.is_symlink():
        raise ValueError(f'Symlink receipt: {path}')
    return validate_manifest(json.loads(path.read_text()))


def select_files(root):
    """Select exports and only narration takes named in generation metrics."""
    names = set()
    exports = root / 'videos/homebrew'
    for pattern in ('*.mp4', '*.m4a', '*.CREDITS.md'):
        names.update(p.relative_to(root).as_posix() for p in exports.glob(pattern))
    # Production records catch exports missing even when their sidecar is missing.
    for pattern in ('*/render.json', '*/russian-narration.json'):
        for record in (root / 'studio/episodes').glob(pattern):
            output = json.loads(record.read_text()).get('output')
            if output:
                names.add(output)
    for name in list(names):
        if name.endswith('.CREDITS.md'):
            names.add(name.removesuffix('.CREDITS.md') + '.mp4')
        elif name.endswith('.mp4'):
            names.add(name.removesuffix('.mp4') + '.CREDITS.md')
        elif name.endswith('.m4a'):
            stem = name.rsplit('.', 2)[0]
            names.update((stem + '.mp4', stem + '.CREDITS.md'))
    for pattern in ('hb-c*/narration/metrics.json', 'hb-c*/narration-*/metrics.json'):
        for metrics in (root / 'studio/media').glob(pattern):
            relative = metrics.relative_to(root).as_posix()
            if not MANAGED.fullmatch(relative):
                continue
            names.add(relative)
            records = json.loads(metrics.read_text())
            if not isinstance(records, list) or not records:
                raise ValueError(f'Empty or invalid narration metrics: {metrics}')
            for record in records:
                names.add(record['path'])
                if record.get('raw_path'):
                    names.add(record['raw_path'])
    if not any(name.endswith('.mp4') for name in names):
        raise ValueError('No exports found; restore media with --pull first')
    previous = root / RECEIPT
    if previous.exists() or previous.is_symlink():
        missing = set(read_receipt(root)['files']) - names
        if missing:
            raise ValueError(f'Source is incomplete relative to last sync: {sorted(missing)[:5]}')
    return validate_manifest({'version': 1, 'files': {
        name: file_record(safe_path(root, name)) for name in sorted(names)
    }})


def differences(root, manifest):
    """Read-only verification; missing files are reported as mismatches."""
    validate_manifest(manifest)
    changed = []
    for name, expected in manifest['files'].items():
        path = safe_path(root, name)
        if (not path.exists() or path.stat().st_size != expected['size']
                or file_record(path) != expected):
            changed.append(name)
    return changed


def verify(root, manifest):
    changed = differences(root, manifest)
    if changed:
        raise ValueError(f'Checksum verification failed ({len(changed)} files): {changed[:5]}')


def publish_receipt(root, manifest):
    """Verify bytes before atomically replacing the successful-sync manifest."""
    verify(root, manifest)
    if (root / RECEIPT).is_symlink():
        raise ValueError('Symlink receipt is not supported')
    with tempfile.NamedTemporaryFile(mode='w', dir=root, prefix='.media-sync-',
                                     suffix='.tmp', delete=False) as stream:
        tmp = Path(stream.name)
        try:
            json.dump(manifest, stream, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            tmp.unlink()
            raise
    try:
        tmp.replace(root / RECEIPT)
    finally:
        tmp.unlink(missing_ok=True)


def worker(request):
    """Run the same path/verification rules remotely without installing this file."""
    root = Path(request['root'])
    if not root.is_absolute() or '..' in root.parts:
        raise ValueError('Remote directory must be absolute, without ..')
    for path in (root, *root.parents):
        if path.is_symlink():
            raise ValueError(f'Symlink root is not supported: {path}')
    if not shutil.which('rsync'):
        raise ValueError('rsync is required on the remote host')
    action = request['action']
    if action == 'read':
        return read_receipt(root)
    manifest = validate_manifest(request['manifest'])
    for name in manifest['files']:
        safe_path(root, name)
    if action == 'prepare':
        root.mkdir(parents=True, exist_ok=True)
    elif action == 'compare':
        return differences(root, manifest)
    elif action == 'verify':
        verify(root, manifest)
    elif action == 'publish':
        publish_receipt(root, manifest)
    else:
        raise ValueError(f'Unknown remote operation: {action}')
    return True


def remote(host, directory, action, manifest=None):
    # Arguments are shell-quoted once for the remote shell, never interpolated code.
    command = shlex.join(['python3', '-c', Path(__file__).read_text(), '--worker'])
    result = subprocess.run(
        ['ssh', '-o', 'BatchMode=yes', '--', host, command],
        input=json.dumps({'root': directory, 'action': action, 'manifest': manifest}),
        text=True, stdout=subprocess.PIPE, check=True,
    )
    return json.loads(result.stdout)


def transfer(root, host, directory, manifest, pull=False):
    names = b''.join(name.encode() + b'\0' for name in sorted(manifest['files']))
    local_path = str(root) + '/'
    remote_path = f'{host}:{directory.rstrip("/")}/'
    source, destination = (remote_path, local_path) if pull else (local_path, remote_path)
    # -s protects the remote path, even spaces, quotes and shell metacharacters.
    # No --delete, --inplace, or --append: interrupted transfers keep old files intact.
    subprocess.run([
        'rsync', '-rt', '--checksum', '--protect-args', '--relative',
        '--partial-dir=.rsync-partial', '--from0', '--files-from=-', '--stats',
        '-e', 'ssh -o BatchMode=yes', '--', source, destination,
    ], input=names, check=True)


def sync(root, host, directory, pull=False, dry_run=False, verify_only=False):
    manifest = remote(host, directory, 'read') if pull else select_files(root)
    validate_manifest(manifest)
    for name in manifest['files']:
        safe_path(root, name)
    size = sum(record['size'] for record in manifest['files'].values())
    print(f'{len(manifest["files"])} files, {size / 1024**3:.2f} GiB; '
          f'{"restore from" if pull else "upload to"} {host}:{directory}', flush=True)
    if pull:
        remote(host, directory, 'verify', manifest)
    if dry_run or verify_only:
        changed = differences(root, manifest) if pull else remote(host, directory, 'compare', manifest)
        if verify_only and changed:
            raise ValueError(f'Checksum verification failed ({len(changed)} files): {changed[:5]}')
        print(f'{len(changed)} files need copying; destination unchanged.', flush=True)
        for name in changed[:20]:
            print(f'  {name}')
        return
    if not pull:
        remote(host, directory, 'prepare', manifest)
    transfer(root, host, directory, manifest, pull=pull)
    # Detect source changes during transfer as well as destination corruption.
    verify(root, manifest)
    remote(host, directory, 'verify' if pull else 'publish', manifest)
    publish_receipt(root, manifest)
    print('Verified every selected file with SHA-256. Sync manifest saved.', flush=True)


def main():
    if sys.argv[1:] == ['--worker']:
        print(json.dumps(worker(json.load(sys.stdin))))
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, help='SSH alias or user@host')
    parser.add_argument('--remote-dir', default='/root/finland-flashcards',
                        help='absolute remote repository path (default: %(default)s)')
    parser.add_argument('--pull', action='store_true', help='restore the last successful upload')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true', help='list changes without writing')
    mode.add_argument('--verify-only', action='store_true', help='check hashes without writing')
    args = parser.parse_args()
    if not re.fullmatch(r'(?:[a-zA-Z0-9_.-]+@)?[a-zA-Z0-9_][a-zA-Z0-9_.-]*', args.host):
        parser.error('--host must be an SSH alias or user@host; configure ports/IPv6 in SSH config')
    if (not args.remote_dir.startswith('/') or args.remote_dir == '/'
            or '..' in PurePosixPath(args.remote_dir).parts
            or any(ord(c) < 32 for c in args.remote_dir)):
        parser.error('--remote-dir must be an absolute repository directory, without ..')
    for executable in ('ssh', 'rsync'):
        if not shutil.which(executable):
            parser.error(f'{executable} is required locally')
    sync(ROOT, args.host, args.remote_dir, args.pull, args.dry_run, args.verify_only)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        print(f'Media sync failed: {exc}', file=sys.stderr)
        sys.exit(1)
