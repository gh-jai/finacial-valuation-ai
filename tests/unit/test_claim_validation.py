import copy
import json
from pathlib import Path

import yaml

from tools.validate_claims import iter_knowledge_frontmatter, validate_claim_collection


ROOT = Path(__file__).resolve().parents[2]


def repository_inputs() -> tuple[dict, dict, list[tuple[str, dict]], dict]:
    claims = yaml.safe_load(
        (ROOT / "extraction" / "reviewed" / "M1-basic-dcf-claims.yaml").read_text(
            encoding="utf-8"
        )
    )
    sources = yaml.safe_load((ROOT / "sources" / "catalog.yaml").read_text(encoding="utf-8"))
    knowledge = list(iter_knowledge_frontmatter(ROOT))
    schema = json.loads((ROOT / "schemas" / "claim.schema.json").read_text(encoding="utf-8"))
    return claims, sources, knowledge, schema


def test_m1_claim_collection_and_knowledge_references_validate() -> None:
    claims, sources, knowledge, schema = repository_inputs()
    errors, claim_count, reference_count = validate_claim_collection(
        claims, sources, knowledge, schema
    )
    assert errors == []
    assert claim_count == 12
    assert reference_count == 12


def test_missing_knowledge_claim_reference_is_rejected() -> None:
    claims, sources, _, schema = repository_inputs()
    errors, _, _ = validate_claim_collection(
        claims,
        sources,
        [("knowledge/valuation/broken.md", {"claim_refs": ["CLM-VAL-DCF-999"]})],
        schema,
    )
    assert any("unknown claim reference CLM-VAL-DCF-999" in error for error in errors)


def test_source_statement_without_source_reference_is_rejected() -> None:
    claims, sources, knowledge, schema = repository_inputs()
    broken = copy.deepcopy(claims)
    broken["claims"][0]["source_refs"] = []
    errors, _, _ = validate_claim_collection(broken, sources, knowledge, schema)
    assert any("source_statement requires" in error for error in errors)


def test_derived_rule_without_derivation_is_rejected() -> None:
    claims, sources, knowledge, schema = repository_inputs()
    broken = copy.deepcopy(claims)
    broken["claims"][-1].pop("derivation")
    errors, _, _ = validate_claim_collection(broken, sources, knowledge, schema)
    assert any("derived_rule requires" in error for error in errors)


def test_unknown_source_id_is_rejected() -> None:
    claims, sources, knowledge, schema = repository_inputs()
    broken = copy.deepcopy(claims)
    broken["claims"][0]["source_refs"][0]["source_id"] = "SRC-UNKNOWN-999"
    errors, _, _ = validate_claim_collection(broken, sources, knowledge, schema)
    assert any("unknown source ID SRC-UNKNOWN-999" in error for error in errors)
