"""Download one selected public media source with shared Wikimedia throttling.

Selection, identity, relevance and license checks belong to the episode owner.
Completed files are retained and fingerprinted; incomplete downloads never replace
them. Wikimedia image requests use one shared five-second spacing and respect a
five-minute cooldown after HTTP 429. No automatic retry hides rate limiting.
"""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import time
import urllib.parse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--sha256')
    parser.add_argument('--timeout', type=int, default=50,
                        help='Maximum transfer seconds; allow longer for large music masters')
    args = parser.parse_args()
    if not 1 <= args.timeout <= 1200:
        parser.error('Transfer timeout must be between1and1200seconds')
    url = urllib.parse.urlsplit(args.url)
    if url.scheme != 'https':
        parser.error('Use an HTTPS public source URL')
    output = args.output.resolve()
    root = Path(__file__).resolve().parents[3]
    if not output.is_relative_to(root/'studio/media'):
        parser.error('Write selected media within studio/media only')
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        lock = Path('/tmp/homebrew-image-download.lock')
        stamp = Path('/tmp/homebrew-image-download-time.json')
        with lock.open('a') as handle:
            if url.hostname.endswith(('wikimedia.org', 'wikipedia.org')):
                fcntl.flock(handle, fcntl.LOCK_EX)
                previous = json.loads(stamp.read_text()) if stamp.exists() else {}
                wait = max(previous.get('next_request', 0)-time.time(), 0)
                if wait > 55:
                    raise SystemExit(f'Image cooldown active for {wait:.0f}s; retain other work and retry later.')
                if wait:
                    time.sleep(wait)
                stamp.write_text(json.dumps(dict(next_request=time.time()+5)))
            temporary = output.with_name(output.name+'.download-part')
            result = subprocess.run(['curl','-4','--silent','--show-error','--max-time',str(args.timeout),
                                     '-A','HomebrewVideoStudio/1.0 (educational media)',
                                     '-w','%{http_code}','-o',str(temporary),args.url],capture_output=True)
            if result.stdout == b'429':
                stamp.write_text(json.dumps(dict(next_request=time.time()+300)))
                temporary.unlink(missing_ok=True)
                raise SystemExit('Image source returned429; no retry, five-minute shared cooldown.')
            if result.returncode or result.stdout != b'200':
                temporary.unlink(missing_ok=True)
                raise SystemExit(f'Download failed: HTTP{result.stdout.decode(errors="replace")}; '+result.stderr.decode(errors='replace'))
            digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
            if args.sha256 and digest != args.sha256:
                temporary.unlink()
                raise SystemExit('Downloaded bytes differ from the pinned source checksum')
            temporary.replace(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    if args.sha256 and digest != args.sha256:
        raise SystemExit('Retained source differs from the pinned checksum; do not overwrite silently')
    print(json.dumps(dict(path=str(output.relative_to(root)),bytes=output.stat().st_size,
                          sha256=digest,url=args.url),ensure_ascii=False))


if __name__=='__main__':
    main()
