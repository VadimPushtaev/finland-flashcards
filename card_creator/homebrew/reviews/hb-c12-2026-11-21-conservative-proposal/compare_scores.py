"""Compare the completed proposal using the existing formula and fixed cutoffs.

This is a separate reporting step: it does not assess sentences or edit cards.
The card population stays fixed at the same 103 canonical Chapter 12 cards.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from card_creator.homebrew.score_sentences import make_report, TIERS, WEIGHTS

SCORE_KEYS = (*WEIGHTS, "change_risk")


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def histogram(values):
    return dict(sorted(Counter(values).items()))


def main():
    """Produce auditable sentence and card comparisons from validated records."""
    reports = {}
    records = {}
    for label, folder in (("before", "before"), ("proposed", "assessments")):
        reports[label] = make_report(ROOT, ["hb-c12"], tiers=TIERS, cutoffs=(41, 40),
                                     data_dir=HERE / folder)
        records[label] = {r["sentence_id"]: r for r in reports[label]["sentences"]}
        write_json(HERE / f"{label}-selection.json", reports[label])
    before, proposed = records["before"], records["proposed"]
    assert list(before) == list(proposed) and len(before) == 603

    inputs = {}
    provenance = {}
    for section in reports["before"]["assessment_inputs"]:
        path = ROOT / "card_creator/homebrew/card_sources" / f"{section}.yaml"
        raw = path.read_bytes()
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
        for item in yaml.safe_load(raw)["cards"]:
            key = (section, item["row_sha256"])
            assert key not in provenance
            provenance[key] = item

    card_path = ROOT / "data/homebrew/cards/hb-c12.yaml"
    raw = card_path.read_bytes()
    inputs[str(card_path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    cards = []
    seen = set()
    by_sentence = defaultdict(list)
    for card in yaml.safe_load(raw)["cards"]:
        flags = " ".join("1" if option["id"] == card["correct_option_id"] else "0"
                         for option in card["options"])
        row = "|".join([card["question"], card["category"], "2",
                        *(option["text"] for option in card["options"]), "", flags, "2"])
        row_hash = hashlib.sha256(row.encode("utf-8")).hexdigest()
        key = (card["section_id"], row_hash)
        source = provenance[key]
        assert key not in seen
        seen.add(key)
        sid = source["primary_sentence_id"]
        assert source["score"] == before[sid]["score"]
        assert source["priority"] == before[sid]["priority"]
        assert all(s in before for s in source["source_sentence_ids"])
        answer = next(o["text"] for o in card["options"] if o["id"] == card["correct_option_id"])
        item = {
            "card_id": card["id"], "section_id": card["section_id"],
            "question": card["question"], "correct_answer": answer,
            "primary_sentence_id": sid, "primary_sentence": before[sid]["text"],
            "before_total": before[sid]["score"], "proposed_total": proposed[sid]["score"],
            "before_tier": before[sid]["priority"], "proposed_tier": proposed[sid]["priority"],
            "originally_in_62_at_56": before[sid]["score"] == 56,
            "proposed_rationale": proposed[sid]["rationale"],
            "source_sentence_ids": source["source_sentence_ids"], "row_sha256": row_hash,
        }
        cards.append(item)
        by_sentence[sid].append(card["id"])
    assert len(cards) == len(seen) == len(provenance) == 103
    assert len({c["card_id"] for c in cards}) == 103
    assert sum(c["originally_in_62_at_56"] for c in cards) == 62

    rows = []
    for sid, old in before.items():
        new = proposed[sid]
        changed = [k for k in SCORE_KEYS if old["scores"][k] != new["scores"][k]]
        changed += [k for k in ("fact_types", "context_sentence_ids", "duplicate_of",
                                "assessment_confidence", "rationale") if old[k] != new[k]]
        row = {
            "sentence_id": sid, "section_id": old["section_id"], "text": old["text"],
            "changed_fields": ";".join(changed), "existing_primary_cards": ";".join(by_sentence[sid]),
            "before_total": old["score"], "proposed_total": new["score"],
            "before_tier": old["priority"], "proposed_tier": new["priority"],
        }
        for label, record in (("before", old), ("proposed", new)):
            row.update({f"{label}_{k}": record["scores"][k] for k in SCORE_KEYS})
            for key in ("assessment_confidence", "rationale", "duplicate_of"):
                row[f"{label}_{key}"] = record[key]
            for key in ("fact_types", "context_sentence_ids", "review_flags"):
                row[f"{label}_{key}"] = ";".join(record[key])
        rows.append(row)
    write_csv(HERE / "sentence-comparison.csv", rows)
    write_csv(HERE / "existing-card-comparison.csv", [
        {**card, "source_sentence_ids": ";".join(card["source_sentence_ids"])} for card in cards])

    audit = json.loads((HERE / "assessment-audit.json").read_text())
    direction = Counter("lower" if proposed[s]["score"] < before[s]["score"] else
                        "higher" if proposed[s]["score"] > before[s]["score"] else "same"
                        for s in before)
    summary = {
        "chapter_id": "hb-c12", "status": "proposal_not_applied",
        "formula": reports["before"]["formula"], "core_min": 41, "supporting_min": 40,
        "sentence_count": 603, "existing_card_count": 103,
        "review_counts": audit["counts"], "total_score_direction": dict(direction),
        "sentence_tiers": {label: report["requested_counts"] for label, report in reports.items()},
        "sentence_histograms": {
            label: histogram(r["score"] for r in record.values()) for label, record in records.items()},
        "card_histograms": {
            label: histogram(c[f"{label}_total"] for c in cards) for label in ("before", "proposed")},
        "original_62_proposed_histogram": histogram(c["proposed_total"] for c in cards
                                                    if c["originally_in_62_at_56"]),
        "threshold_comparison": [{
            "threshold": threshold,
            **{f"{label}_sentences": sum(r["score"] >= threshold for r in records[label].values())
               for label in ("before", "proposed")},
            **{f"{label}_existing_cards": sum(c[f"{label}_total"] >= threshold for c in cards)
               for label in ("before", "proposed")},
        } for threshold in (41, 45, 50, 60)],
        "relevance_and_value_both_3": {
            label: sum(r["scores"]["exam_relevance"] == r["scores"]["knowledge_value"] == 3
                       for r in record.values()) for label, record in records.items()},
        "provenance_inputs_sha256": inputs,
        "card_comparison": cards,
        "interpretation": "After rescoring the same existing card primaries; no cards generated, removed or selected anew. All sentence histogram includes duplicates and fragments.",
    }
    for sid, digest in audit["baseline_sha256"].items():
        path = HERE / "before" / f"{sid}.yaml"
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    for relative, digest in inputs.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    write_json(HERE / "comparison.json", summary)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("provenance_inputs_sha256", "card_comparison")}, indent=2))


if __name__ == "__main__":
    main()
