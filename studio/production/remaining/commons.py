"""Retrieve Commons image metadata with a shared, conservative request throttle.

Use --search QUERY or --titles 'File:...|File:...' and --output PATH.
This retrieves metadata only; episode owners retain source selection and downloads.
"""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import time
import urllib.parse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--search')
    group.add_argument('--titles')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.limit <= 30:
        parser.error('Use a metadata page size between 1 and 30')
    params = dict(action='query', format='json', prop='imageinfo',
                  iiprop='url|extmetadata', iiurlwidth='1920')
    if args.search:
        params.update(generator='search', gsrnamespace='6',
                      gsrsearch=args.search, gsrlimit=str(args.limit))
    else:
        params['titles'] = args.titles
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(
        params, quote_via=urllib.parse.quote)
    lock = Path('/tmp/homebrew-commons-api.lock')
    stamp = Path('/tmp/homebrew-commons-api-time.json')
    with lock.open('a') as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        previous = json.loads(stamp.read_text()) if stamp.exists() else {}
        wait = max(previous.get('next_request', 0) - time.time(), 0)
        if wait > 55:
            raise SystemExit(f'Commons cooldown active for {wait:.0f}s; use existing metadata and retry later.')
        if wait:
            time.sleep(wait)
        stamp.write_text(json.dumps(dict(next_request=time.time()+6)))
        result = subprocess.run(['curl', '-4', '--silent', '--show-error',
                                 '--max-time', '45', '-A',
                                 'HomebrewVideoStudio/1.0 (educational media research)',
                                 '-w', '\n%{http_code}', url], capture_output=True)
        if result.returncode:
            raise SystemExit(result.stderr.decode(errors='replace'))
        body, status = result.stdout.rsplit(b'\n', 1)
        limited = status == b'429' or b'rate limit' in body[:500].lower()
        if limited:
            stamp.write_text(json.dumps(dict(next_request=time.time()+300)))
            raise SystemExit('Commons requested a cooldown; pausing new API requests for five minutes.')
        if status != b'200':
            raise SystemExit(f'Commons returned HTTP {status.decode()}: {body[:240]!r}')
        document = json.loads(body)
        if document.get('error'):
            raise SystemExit(f'Commons API error: {document["error"]}')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(document, ensure_ascii=False, indent=2)+'\n')
        print(f'Saved {len(document.get("query", {}).get("pages", {}))} source records to {args.output}')


if __name__ == '__main__':
    main()
