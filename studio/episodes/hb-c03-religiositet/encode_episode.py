"""Render and technically verify one owned festival episode with tracked status."""
from pathlib import Path
import argparse, json, os, subprocess, time
ROOT = Path(__file__).resolve().parents[3]
ALLOWED = {'hb-c03-' + x for x in ['religiositet', 'kalender', 'vinterfester', 'pask', 'valborg', 'midsommar', 'hostfester', 'december', 'kulturdagar', 'ovriga-fester', 'livets-fester']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section', choices=sorted(ALLOWED))
    args = parser.parse_args()
    os.chdir(ROOT)
    folder = ROOT / 'studio/media' / args.section / 'render'
    folder.mkdir(parents=True, exist_ok=True)
    status = folder / 'encode-worker-status.json'

    def phase(name, **extra):
        status.write_text(json.dumps({'pid': os.getpid(), 'phase': name, 'time': time.time(), **extra}))
    try:
        phase('preflight')
        subprocess.run([str(ROOT / 'studio/runtime/.venv/bin/python'), 'studio/episodes/hb-c03-religiositet/check_narration.py', args.section], check=True)
        subprocess.run([str(ROOT / 'studio/runtime/.venv/bin/python'), 'studio/tools/validate_assets.py', args.section], check=True)
        phase('encoding')
        subprocess.run([str(ROOT / 'studio/runtime/.venv/bin/python'), '-u', 'studio/tools/render.py', args.section], check=True)
        phase('verifying')
        subprocess.run([str(ROOT / 'studio/runtime/.venv/bin/python'), '-u', 'studio/tools/verify_render.py', args.section, '--save-frames'], check=True)
        phase('source_validating')
        code = "from pathlib import Path\nfrom functools import lru_cache\nfrom studio.tools import script\nfrom translation.homebrew.tools import workflow\nworkflow.library=lru_cache(maxsize=1)(workflow.library)\nsid=__import__('sys').argv[1];ep=Path('studio/episodes')/sid;c=script.load_context(sid);d=script.read(ep/'script.yaml');script.validate(d,c,ready=True);(ep/'SCRIPT.md').write_text(script.review_markdown(d,c));print(sid,'final source-ready validation passed',flush=True)\n"
        subprocess.run(['poetry', 'run', 'python', '-c', code, args.section], check=True)
        phase('technical_complete', exit_code=0)
    except Exception as e:
        phase('failed', error=str(e))
        raise
if __name__ == '__main__':
    main()
