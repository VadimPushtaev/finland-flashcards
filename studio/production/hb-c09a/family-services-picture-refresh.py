"""Clarify police recipients and a non-graphic violence warning, retaining source text and selected audio."""
import subprocess
for command in [
    ['studio/runtime/.venv/bin/python','studio/episodes/hb-c09-familjetjanster/prepare_foregrounds.py'],
    ['studio/runtime/.venv/bin/python','studio/production/hb-c09a/refresh_timed_stills.py','hb-c09-familjetjanster'],
]:
    subprocess.run(command,check=True)
