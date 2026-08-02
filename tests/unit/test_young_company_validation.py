import copy
import json
from pathlib import Path

import yaml

from tools.validate_young_company_valuations import validate_document


ROOT = Path(__file__).resolve().parents[2]


def inputs() -> tuple[dict, dict, set[str], set[str], set[str]]:
    document = json.loads((ROOT / "benchmarks/fixtures/young_company/synthetic-capital-intensive.json").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas/young-company-valuation.schema.json").read_text(encoding="utf-8"))
    catalog = yaml.safe_load((ROOT / "sources/catalog.yaml").read_text(encoding="utf-8"))
    sources = {item["id"] for item in catalog["sources"]}
    claims: set[str] = set()
    for path in (ROOT / "extraction/reviewed").glob("*.yaml"):
        claims.update(item["id"] for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"])
    assertions: set[str] = set()
    for path in (ROOT / "benchmarks/fixtures/narratives").glob("*.json"):
        assertions.update(item["id"] for item in json.loads(path.read_text(encoding="utf-8"))["assertions"])
    return document, schema, sources, claims, assertions


def errors_for(document: dict) -> list[str]:
    _, schema, sources, claims, assertions = inputs()
    return validate_document(document, schema, sources, claims, assertions)


def test_valid_young_company_document() -> None:
    document, _, _, _, _ = inputs()
    assert errors_for(document) == []


def test_failure_value_basis_mismatch_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["failure_scenario"]["failure_value_basis"] = "equity"
    assert any("basis must match" in error for error in errors_for(document))


def test_survival_risk_double_counting_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["survival_adjustment"]["double_counting_check"]["passed"] = False
    assert any("double-counting" in error for error in errors_for(document))


def test_option_deduction_requires_explicit_trace() -> None:
    document, _, _, _, _ = inputs()
    document["forecast"]["assumption_trace"] = [item for item in document["forecast"]["assumption_trace"] if item["input_name"] != "option_and_other_equity_claim_value"]
    assert any("option deduction" in error for error in errors_for(document))


def test_authorized_financing_requires_trace() -> None:
    document, _, _, _, _ = inputs()
    document["forecast"]["assumption_trace"] = [item for item in document["forecast"]["assumption_trace"] if item["input_name"] != "authorized_financing_proceeds"]
    assert any("authorization trace" in error for error in errors_for(document))


def test_key_person_scenario_must_reconcile_separate_values() -> None:
    document, _, _, _, _ = inputs()
    document["key_person_scenario"] = {"scenario_id": "KEY-SYN-001", "operating_changes": "Synthetic founder absence lowers revenue.", "scenario_value": 80.0, "status_quo_value": 100.0, "discount_amount": 15.0, "evidence_refs": ["EVD-SYN-KEY-001"]}
    assert any("separately valued" in error for error in errors_for(document))


def test_reviewed_document_requires_control_approvals() -> None:
    document, _, _, _, _ = inputs()
    document["review"]["risk_separation_approved"] = False
    assert any("requires risk-separation" in error for error in errors_for(document))


def test_unknown_source_claim_and_assertion_refs_are_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["traceability"]["source_refs"] = ["SRC-UNKNOWN"]
    document["traceability"]["claim_refs"] = ["CLM-YNG-999"]
    document["traceability"]["narrative_assertion_refs"] = ["NAR-A-999"]
    errors = errors_for(document)
    assert any("unknown source" in error for error in errors)
    assert any("unknown claim" in error for error in errors)
    assert any("unknown narrative assertion" in error for error in errors)
