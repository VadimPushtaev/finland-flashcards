"""Record a completed independent visual review without writing owner directories."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
PRODUCTION = Path(__file__).resolve().parent
NOTES = {
    "skilsmassa": [
        "Joint or single application; spouse opposition does not prevent divorce.",
        "Two stages; judgment only after the second application. Six-month reflection exception requires separate addresses during the previous two years.",
        "Joint reflection begins on court receipt, single reflection on service to the other spouse. Second application deadline is one year from reflection START.",
        "Asset division can start after first application; no need to wait six months. Joint mortgage, interim residence and division-fee conditions retained.",
        "Foreign law may apply to some matters; family mediation may help. Low OR medium income MAY qualify for free OR partial legal aid; covering insurance excludes public aid."
    ],
    "flersprakighet": [
        "Family adaptation and roles MAY change; relatives, culture and partner-language support shown without attributing stereotypes to photographed people.",
        "Children may adapt faster; both partners learning language avoids dependence. Preschool attendance and school language alternatives remain Finnish OR Swedish.",
        "Parents MAY THINK only the new home language helps; this is visibly a thought, followed by the source explanation of strong mother-tongue skills helping new-language learning.",
        "Parents should use their strongest language; multiple simultaneous languages and more than one mother tongue are possible. No promise of a specific school-language service."
    ],
    "dodsfall": [
        "Doctor always certifies death; home/sudden/night/weekend notification qualifications preserved. Population-register transmission differs from family notifications.",
        "Death certificate identifies cause and may be delayed; it is not required for routine authority matters, mainly relevant for life-insurance affairs.",
        "Medical autopsy requires family consent. Police-ordered forensic autopsy does not require that consent and cannot be refused on that basis.",
        "Burial waits until cause is investigated. Archived presumed organ donation preserves known opposition, attempt to discover wishes and living directive; family cannot veto known donor wish.",
        "Body donation for teaching requires signed agreement; no clinical eligibility, graphic procedure or invented transport instructions."
    ],
    "begravning": [
        "Usual delay of weeks is qualified; faster burial requires investigated cause AND physician burial permit. Wishes respected IF possible.",
        "Coffin burial in approved cemeteries; cremation/urn/scattering choices, other land or water OWNER permission and all ashes in ONE location are explicit.",
        "MOST Lutheran cemeteries accept others; separate areas and other-faith/private cemeteries remain qualified possibilities.",
        "For foreign transport, destination embassy is contacted and family pays. Foreign-national notification to origin mission and relatives differs from destination transport arrangements.",
        "Bereavement support languages and funeral/survivor benefits preserve some/most/MAY conditions; no current fees, guarantees or new contact hours."
    ],
}

for slug in sys.argv[1:]:
    assert slug in NOTES
    directory = PRODUCTION / "independent-final-c09" / slug
    candidate = json.loads((directory / "candidate.json").read_text())
    sid = candidate["section_id"]
    episode = ROOT / "studio/episodes" / sid
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(ROOT / candidate["export"]) == candidate["export_sha256"]
    for name, value in candidate["current_metadata_hashes"].items():
        assert digest(episode / name) == value
    for name, value in candidate["frame_hashes"].items():
        assert digest(ROOT / name) == value
    validators = json.loads((PRODUCTION / "c09-independent-source-validations.json").read_text())
    assert validators[slug]["returncode"] == 0
    report = dict(candidate)
    report.update(
        reviewer="/root/chapter10", reviewed=True,
        reviewed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_pairs_read=candidate["source_pairs"],
        actual_exported_frames_inspected=candidate["actual_cards"],
        script_sha256=candidate["current_metadata_hashes"]["script.yaml"],
        assets_sha256=candidate["current_metadata_hashes"]["assets.yaml"],
        frame_sha256={Path(name).name:value for name, value in candidate["frame_hashes"].items()},
        findings=[], source_condition_checks=NOTES[slug],
        source_validator=validators[slug],
        scope="Every exact Swedish/Russian pair read; all verifier-decoded current exported title/body/credit cards visually inspected, with listed dense bilingual/credit simulated640px samples. Source/picture conditions and credit notices checked. Static cards do not constitute continuous whole-video watching/listening, physical-device playback or user acceptance.",
        owner_directories_mutated=False,
    )
    target = PRODUCTION / f"peer-final-hb-c09-{slug}.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(target.relative_to(ROOT), report["actual_cards"], report["export_sha256"], flush=True)
