"""Record fresh read-only source validators for the assigned independent reviews."""
from pathlib import Path
import json
import subprocess

directory = Path(__file__).resolve().parent
result = {}
for slug in ["skilsmassa", "flersprakighet", "dodsfall", "begravning"]:
    process = subprocess.run([".venv/bin/python", "studio/tools/script.py", "validate",
                              "hb-c09-" + slug, "--ready"], capture_output=True, text=True)
    result[slug] = dict(returncode=process.returncode, stdout=process.stdout, stderr=process.stderr)
    (directory / "c09-independent-source-validations.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(slug, process.returncode, process.stdout[-300:], process.stderr[-300:], flush=True)
    assert process.returncode == 0
