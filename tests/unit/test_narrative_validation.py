import copy
import json
from pathlib import Path

import yaml

from tools.validate_narratives import validate_narrative_document


ROOT = Path(__file__).resolve().parents[2]


def inputs() -> tuple[dict, dict, set[str], set[str]]:
    document = json.loads((ROOT / "benchmarks/fixtures/narratives/synthetic-base.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas/narrative.schema.json").read_text(encoding="utf-8"))
    catalog = yaml.safe_load((ROOT / "sources/catalog.yaml").read_text(encoding="utf-8"))
    source_ids = {item["id"] for item in catalog["sources"]}
    claim_ids: set[str] = set()
    for path in (ROOT / "extraction/reviewed").glob("*.yaml"):
        claim_ids.update(item["id"] for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"])
    return document, schema, source_ids, claim_ids


def errors_for(document: dict) -> list[str]:
    _, schema, sources, claims = inputs()
    return validate_narrative_document(document, schema, sources, claims)


def test_schema_valid_narrative() -> None:
    document, _, _, _ = inputs()
    assert errors_for(document) == []


def test_unsupported_three_p_label_is_rejected() -> None:
    document, _, _, _ = inputs()
    document["three_p"]["overall"] = "certain"
    assert any("schema" in error and "certain" in error for error in errors_for(document))


def test_missing_three_p_evidence_is_rejected() -> None:
    document, _, _, _ = inputs()
    document["three_p"]["plausible"]["supporting_evidence"] = []
    assert any("3P plausible" in error for error in errors_for(document))


def test_duplicate_assertion_ids_are_rejected() -> None:
    document, _, _, _ = inputs()
    document["assertions"].append(copy.deepcopy(document["assertions"][0]))
    assert any("unique" in error for error in errors_for(document))


def test_missing_assertion_mapping_is_rejected() -> None:
    document, _, _, _ = inputs()
    document["value_driver_mappings"] = [item for item in document["value_driver_mappings"] if item["assertion_id"] != "NAR-A-001"]
    assert any("has no value-driver mapping" in error for error in errors_for(document))


def test_unquantified_limitation_must_be_explicit() -> None:
    document, _, _, _ = inputs()
    document["assertions"][-1]["statement"] = "Management execution quality is uncertain."
    assert any("explicitly state its limitation" in error for error in errors_for(document))


def test_current_id_cannot_be_an_alternative() -> None:
    document, _, _, _ = inputs()
    document["alternatives"][0]["narrative_id"] = document["id"]
    assert any("must differ" in error for error in errors_for(document))


def test_feedback_history_cannot_erase_prior_version() -> None:
    revised = json.loads((ROOT / "benchmarks/fixtures/narratives/synthetic-revised.json").read_text(encoding="utf-8"))
    revised["revision_history"][1]["previous_version_ref"] = "9.9.9"
    assert any("does not preserve" in error for error in errors_for(revised))


def test_break_change_shift_classifications_are_supported() -> None:
    revised = json.loads((ROOT / "benchmarks/fixtures/narratives/synthetic-revised.json").read_text(encoding="utf-8"))
    for classification in ("tweak", "shift", "change", "break"):
        candidate = copy.deepcopy(revised)
        candidate["revision_history"][1]["classification"] = classification
        assert errors_for(candidate) == []
