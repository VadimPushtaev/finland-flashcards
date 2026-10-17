"""Restore downloaded assets from the checked-in SHA-256 manifest."""
import argparse
import hashlib
from pathlib import Path
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    checksum = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            checksum.update(block)
    return checksum.hexdigest()


def fetch(entry):
    destination = ROOT / entry['path']
    if not destination.resolve().is_relative_to((ROOT / 'studio/media').resolve()):
        raise ValueError('Asset destinations must stay inside studio/media')
    if destination.exists() and digest(destination) == entry['sha256']:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + '.download')
    for attempt in range(6):
        offset = partial.stat().st_size if partial.exists() else 0
        request = urllib.request.Request(entry['url'], headers={'User-Agent': 'HomebrewVideoStudio/1.0', 'Range': f'bytes={offset}-'})
        with urllib.request.urlopen(request, timeout=120) as response:
            with partial.open('ab' if response.status == 206 else 'wb') as output:
                while block := response.read(1024 * 1024):
                    output.write(block)
        if digest(partial) == entry['sha256']:
            partial.replace(destination)
            return
        if partial.stat().st_size >= entry['bytes']:
            partial.unlink()
    raise ValueError(f'Incomplete or changed download: {destination}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    for entry in yaml.safe_load(args.manifest.read_text())['downloads']:
        if args.verify:
            path = ROOT / entry['path']
            if not path.exists() or digest(path) != entry['sha256']:
                raise ValueError(f'Missing or changed: {path}')
        else:
            fetch(entry)
        print(entry['path'])


if __name__ == '__main__':
    main()
