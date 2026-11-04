"""Make read-only review galleries for four explicitly assigned C9 exports."""
from pathlib import Path
import hashlib
import json
import math
import sys
import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
PRODUCTION = Path(__file__).resolve().parent
ALLOWED = {"skilsmassa", "flersprakighet", "dodsfall", "begravning"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for slug in sys.argv[1:]:
    assert slug in ALLOWED
    sid = "hb-c09-" + slug
    episode = ROOT / "studio/episodes" / sid
    render = json.loads((episode / "render.json").read_text())
    check = json.loads((episode / "render-check.json").read_text())
    assert render["sha256"] == check["sha256"] == digest(ROOT / render["output"])
    assert check["full_decode"] == "passed"
    frames = [ROOT / "studio/media" / sid / "render" / f"export-frame-{i:02}.png"
              for i in range(len(render["timeline"]))]
    assert all(path.exists() for path in frames)
    directory = PRODUCTION / "independent-final-c09" / slug
    directory.mkdir(parents=True, exist_ok=True)
    contacts = []
    for start in range(0, len(frames), 16):
        chunk = frames[start:start + 16]
        canvas = Image.new("RGB", (1920, math.ceil(len(chunk) / 4) * 294), "#ddd")
        draw = ImageDraw.Draw(canvas)
        for n, path in enumerate(chunk):
            im = Image.open(path).convert("RGB").resize((480, 270))
            x, y = n % 4 * 480, n // 4 * 294
            canvas.paste(im, (x, y))
            draw.text((x + 6, y + 272), path.name, fill="black")
        target = directory / f"actual-{start:03}.jpg"
        canvas.save(target)
        contacts.append(str(target.relative_to(ROOT)))
    script = yaml.safe_load((episode / "script.yaml").read_text())
    body = [(i, row) for i, row in enumerate(render["timeline"]) if row["kind"] == "sentence"]
    # Longest bilingual text cards plus all closing cards; selection is explicit in proof.
    dense = sorted(range(len(script["sentences"])), key=lambda i:
                   len(script["sentences"][i]["sv"]) + len(script["sentences"][i]["ru"]), reverse=True)[:10]
    indices = sorted({body[i][0] for i in dense} |
                     {i for i, row in enumerate(render["timeline"]) if row["kind"] == "credits"})
    phone = Image.new("RGB", (1280, math.ceil(len(indices) / 2) * 384), "#ddd")
    draw = ImageDraw.Draw(phone)
    for n, i in enumerate(indices):
        x, y = n % 2 * 640, n // 2 * 384
        phone.paste(Image.open(frames[i]).convert("RGB").resize((640, 360)), (x, y))
        draw.text((x + 6, y + 362), frames[i].name, fill="black")
    target = directory / "actual-phones.jpg"
    phone.save(target)
    proof = dict(section_id=sid, export=render["output"], export_sha256=render["sha256"],
                 source_pairs=len(script["sentences"]), full_decode=check["full_decode"],
                 actual_cards=len(frames), contacts=contacts, simulated_640px_frames=indices,
                 phone_contact=str(target.relative_to(ROOT)),
                 current_metadata_hashes={name:digest(episode / name) for name in
                                         ["script.yaml", "sources.yaml", "assets.yaml", "CREDITS.md", "render.json", "render-check.json"]},
                 frame_hashes={str(path.relative_to(ROOT)):digest(path) for path in frames},
                 reviewed=False, whole_video_listening=False, physical_device_playback=False,
                 user_acceptance=False)
    (directory / "candidate.json").write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n")
    print(sid, len(frames), len(indices), flush=True)
