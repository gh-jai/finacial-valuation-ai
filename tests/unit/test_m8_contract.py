import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M8-retail-product-safety-contract.md"
SUPPORT_MATRIX = ROOT / "docs/product/retail-v1-issuer-support-matrix.md"
ERROR_POLICY = ROOT / "docs/product/retail-v1-error-data-output-policy.md"
THREAT_MODEL = ROOT / "docs/product/retail-v1-threat-model.md"
PILOT_MATRIX = ROOT / "docs/product/retail-v1-pilot-matrix.md"
CHECKLIST = ROOT / "templates/m8-retail-contract-review-checklist.md"
SCHEMA_NAMES = [
    "company-request",
    "source-snapshot",
    "normalized-financials",
    "valuation-case",
    "retail-report",
]


def load_schema(name: str) -> dict:
    return json.loads((ROOT / f"schemas/{name}.schema.json").read_text(encoding="utf-8"))


def test_m8_is_contract_only_and_not_implementation_authority() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "Status: Draft for human review; implementation not authorized" in text
    assert "It does not ingest live data" in text
    assert "Approval of this contract would authorize M9 implementation planning only" in text
    assert "Stage, commit, push, PR creation, implementation, release" in text


def test_m8_five_schemas_are_strict_unstable_drafts() -> None:
    assert len(SCHEMA_NAMES) == 5
    for name in SCHEMA_NAMES:
        schema = load_schema(name)
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["properties"]["schema_version"] == {"const": "0.1.0"}


def test_company_request_does_not_collect_investor_profile() -> None:
    schema = load_schema("company-request")
    serialized = json.dumps(schema)
    assert schema["properties"]["market_scope"]["const"] == (
        "us-listed-non-financial-operating-company"
    )
    assert "portfolio" not in serialized
    assert "risk_tolerance" not in serialized
    assert schema["properties"]["acknowledgements"]["properties"][
        "no_trade_instruction"
    ] == {"const": True}


def test_source_and_normalized_contracts_require_hashes_and_provenance() -> None:
    snapshot = load_schema("source-snapshot")
    normalized = load_schema("normalized-financials")
    assert "snapshot_hash" in snapshot["required"]
    assert "license_review" in snapshot["required"]
    assert "content_hash" in snapshot["$defs"]["sourceRecord"]["required"]
    assert "source_fact_refs" in normalized["$defs"]["fact"]["required"]
    assert normalized["$defs"]["fact"]["properties"]["provenance_kind"]["enum"] == [
        "filing_fact",
        "derived_calculation",
        "user_override",
    ]
    assert normalized["properties"]["quality"]["properties"]["status"]["enum"] == [
        "complete",
        "needs_review",
        "unsupported",
    ]


def test_valuation_case_requires_human_hash_lock_and_unweighted_scenarios() -> None:
    schema = load_schema("valuation-case")
    case_lock = schema["properties"]["case_lock"]
    assert schema["properties"]["support_decision"]["properties"]["status"] == {
        "const": "supported"
    }
    assert "approved_hash" in case_lock["required"]
    assert case_lock["properties"]["actor_type"] == {"enum": ["human", None]}
    assert schema["$defs"]["scenario"]["properties"]["probability"] == {"type": "null"}
    assert schema["properties"]["scenarios"]["minItems"] == 3
    assert schema["properties"]["scenarios"]["maxItems"] == 3
    assert len(schema["properties"]["scenarios"]["allOf"]) == 3


def test_retail_report_requires_range_evidence_and_null_action_fields() -> None:
    schema = load_schema("retail-report")
    assert schema["properties"]["status"] == {"enum": ["approved", "expired"]}
    for field in [
        "scenario_values",
        "valuation_range",
        "sensitivity",
        "counterevidence",
        "data_gaps",
        "limitations",
        "source_index",
        "output_approval",
    ]:
        assert field in schema["required"]
    controls = schema["properties"]["wording_controls"]["properties"]
    for field in [
        "buy_signal",
        "sell_signal",
        "hold_signal",
        "position_size",
        "trade_timing",
        "personal_suitability",
    ]:
        assert controls[field] == {"type": "null"}
    assert schema["properties"]["output_approval"]["properties"]["actor_type"] == {
        "const": "human"
    }


def test_support_matrix_routes_unsupported_sectors_to_stop() -> None:
    text = SUPPORT_MATRIX.read_text(encoding="utf-8")
    for issuer_class in ["Bank", "Insurance company", "REIT", "Fund", "SPAC"]:
        assert issuer_class in text
    assert text.count("Unsupported") >= 8
    assert "no alternate issuer or invented input" in text


def test_error_policy_and_threat_model_forbid_silent_fallback_and_authority_in_data() -> None:
    policy = ERROR_POLICY.read_text(encoding="utf-8")
    threats = THREAT_MODEL.read_text(encoding="utf-8")
    assert "never reuse stale data silently" in policy
    assert "cannot produce an upside/downside recommendation label" in policy
    assert "cannot authorize actions" in threats
    assert "network-denied M1-M6 runtime" in threats
    assert "Approval tampering" in threats


def test_pilot_matrix_has_eight_development_cases_and_two_holdouts() -> None:
    text = PILOT_MATRIX.read_text(encoding="utf-8")
    assert text.count("`PILOT-") == 8
    assert text.count("`HOLDOUT-") == 2
    assert "no greater than 0.1%" in text
    assert "Subsequent share-price performance is not an acceptance metric" in text


def test_m8_review_remains_pending_across_required_reviewers() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "Review status: Pending" in text
    assert "[ ] approve M9 implementation planning" in text
    for heading in [
        "## Product owner",
        "## Financial reviewer",
        "## Security reviewer",
        "## Legal/compliance and data licensing reviewer",
    ]:
        assert heading in text
