"""Materialize explicit Chapter 12 review judgments without changing canonical data.

This copies existing records and applies the individually authored overrides;
it does not infer scores, calculate totals, or choose a selection threshold.
"""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCORE_ORDER = (
    "exam_relevance", "knowledge_value", "question_suitability",
    "factual_specificity", "change_risk",
)


def main():
    """Validate the snapshot, apply explicit edits, and validate full coverage."""
    path = ROOT / ".agents/skills/assess-homebrew-sentences/scripts/assessments.py"
    spec = importlib.util.spec_from_file_location("assessment_helper", path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    sections, sentences, targets = helper.source_index(ROOT)
    selected = helper.resolve(["hb-c12"], sentences, targets)
    section_ids = list(dict.fromkeys(sentences[s]["section_id"] for s in selected))
    assert len(selected) == 603 and len(section_ids) == 20

    edits = {}
    for line in (HERE / "changes.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        identity, digits, confidence, rationale = line.split("|", 3)
        assert identity in selected and identity not in edits, identity
        assert len(digits) == 5 and set(digits) <= set("0123"), identity
        edits[identity] = {
            "scores": dict(zip(SCORE_ORDER, map(int, digits))),
            "assessment_confidence": confidence,
            "rationale": rationale,
        }
    metadata = yaml.safe_load((HERE / "metadata-overrides.yaml").read_text())
    assert set(metadata) <= set(selected)
    assert all(set(v) <= {"fact_types", "context_sentence_ids", "duplicate_of"}
               for v in metadata.values())

    for name in ("before", "assessments"):
        (HERE / name).mkdir(exist_ok=True)
    audit_path = HERE / "assessment-audit.json"
    existing_audit = json.loads(audit_path.read_text()) if audit_path.exists() else None
    audit = {
        "chapter_id": "hb-c12", "review_date": "2026-11-21",
        "status": "proposal_not_applied", "reviewed_sentences": len(selected),
        "score_order_in_changes_tsv": list(SCORE_ORDER),
        "method": "Individual contextual review using the existing 0-3 rubric; no quotas or inferred scores.",
        "reviewed_sections": section_ids, "baseline_sha256": {},
        "proposed_sha256": {}, "counts": {
            "records_changed": 0, "scores_changed": 0,
            "rationale_or_metadata_only": 0, "records_reused_unchanged": 0,
        },
    }
    for section_id in section_ids:
        canonical = ROOT / "card_creator/homebrew/assessments" / f"{section_id}.yaml"
        canonical_before = canonical.read_bytes()
        snapshot = HERE / "before" / canonical.name
        if snapshot.exists():
            raw = snapshot.read_bytes()
            if existing_audit:
                assert hashlib.sha256(raw).hexdigest() == existing_audit["baseline_sha256"][section_id], \
                    "Saved baseline changed; do not silently resnapshot"
        else:
            assert existing_audit is None, "Saved baseline is missing"
            raw = canonical_before
            snapshot.write_bytes(raw)
        document = yaml.safe_load(raw)
        helper.validate_document(document, section_id, sections[section_id], sentences)
        proposal = deepcopy(document)
        for old, new in zip(document["assessments"], proposal["assessments"]):
            identity = old["sentence_id"]
            new.update(edits.get(identity, {}))
            new.update(metadata.get(identity, {}))
            audit["counts"]["records_changed"] += old != new
            audit["counts"]["scores_changed"] += old["scores"] != new["scores"]
            audit["counts"]["rationale_or_metadata_only"] += (
                old != new and old["scores"] == new["scores"])
            audit["counts"]["records_reused_unchanged"] += old == new
        helper.validate_document(proposal, section_id, sections[section_id], sentences)
        output = HERE / "assessments" / canonical.name
        output.write_text(yaml.safe_dump(proposal, allow_unicode=True, sort_keys=False,
                                         width=100), encoding="utf-8")
        audit["baseline_sha256"][section_id] = hashlib.sha256(raw).hexdigest()
        audit["proposed_sha256"][section_id] = hashlib.sha256(output.read_bytes()).hexdigest()
        assert canonical.read_bytes() == canonical_before

    helper.validate(selected, sections, sentences, HERE / "assessments")
    (HERE / "assessment-audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit["counts"], indent=2))


if __name__ == "__main__":
    main()
