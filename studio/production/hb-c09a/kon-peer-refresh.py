"""Clarify warning, wellbeing condition and attention symbols, retaining source text and selected audio."""
import subprocess
for command in [
    ['studio/runtime/.venv/bin/python','studio/episodes/hb-c09-kon/prepare_foregrounds.py'],
    ['studio/runtime/.venv/bin/python','studio/production/hb-c09a/refresh_timed_stills.py','hb-c09-kon'],
]:
    subprocess.run(command,check=True)
