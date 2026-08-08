import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M8-retail-product-safety-contract.md"
SUPPORT_MATRIX = ROOT / "docs/product/retail-v1-issuer-support-matrix.md"
ERROR_POLICY = ROOT / "docs/product/retail-v1-error-data-output-policy.md"
THREAT_MODEL = ROOT / "docs/product/retail-v1-threat-model.md"
PILOT_MATRIX = ROOT / "docs/product/retail-v1-pilot-matrix.md"
CHECKLIST = ROOT / "templates/m8-retail-contract-review-checklist.md"
REVIEW = ROOT / "docs/milestones/M8-cross-functional-review.md"
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
    assert "Status: Cross-functional design review complete" in text
    assert "It does not ingest live data" in text
    assert "recommends approval of M9 implementation planning" in text
    assert "stage, commit, push, PR creation, implementation, release" in text


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
    assert "distribution_approved" not in serialized
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


def test_complete_source_snapshot_rejects_stale_or_unapproved_storage() -> None:
    schema = load_schema("source-snapshot")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    document = {
        "schema_version": "0.1.0",
        "snapshot_id": "SNP-TEST",
        "request_id": "REQ-TEST",
        "created_at": "2026-08-08T00:00:00Z",
        "company_identity": {
            "cik": "0000000001",
            "legal_name": "Synthetic Operating Company",
            "ticker": "TEST",
            "exchange": "TEST-EXCHANGE",
            "identity_status": "verified",
        },
        "records": [
            {
                "record_id": "REC-TEST",
                "provider": "sec-edgar",
                "record_type": "10-K",
                "accession": "0000000001-26-000001",
                "retrieved_at": "2026-08-08T00:00:00Z",
                "as_of": "2026-08-08T00:00:00Z",
                "period_start": "2025-01-01",
                "period_end": "2025-12-31",
                "currency": "USD",
                "unit_basis": "units",
                "source_url": "https://www.sec.gov/example",
                "content_hash": "a" * 64,
                "license_ref": "LIC-SEC",
            }
        ],
        "freshness": {
            "evaluated_at": "2026-08-08T00:00:00Z",
            "financials_as_of": "2025-12-31",
            "market_data_as_of": None,
            "policy_id": "FRESH-1",
            "stale": False,
        },
        "license_review": {
            "status": "approved",
            "reviewer": "reviewer-1",
            "reviewed_at": "2026-08-08T00:00:00Z",
            "storage_allowed": True,
            "display_allowed": True,
            "export_allowed": True,
            "redistribution_allowed": False,
        },
        "snapshot_hash": "b" * 64,
        "status": "complete",
        "warnings": [],
    }
    assert list(validator.iter_errors(document)) == []
    document["freshness"]["stale"] = True
    assert list(validator.iter_errors(document))
    document["freshness"]["stale"] = False
    document["license_review"]["storage_allowed"] = False
    assert list(validator.iter_errors(document))


def test_complete_normalized_financials_reject_unapproved_facts_or_findings() -> None:
    schema = load_schema("normalized-financials")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    document = {
        "schema_version": "0.1.0",
        "normalized_id": "NRM-TEST",
        "snapshot_id": "SNP-TEST",
        "snapshot_hash": "a" * 64,
        "company_cik": "0000000001",
        "currency": "USD",
        "periods": [
            {
                "period_id": "PER-FY-2025",
                "basis": "annual",
                "start": "2025-01-01",
                "end": "2025-12-31",
                "fiscal_year": 2025,
                "fiscal_period": "FY",
                "filing_record_refs": ["REC-TEST"],
            }
        ],
        "facts": [
            {
                "fact_id": "FACT-REVENUE",
                "concept": "revenue",
                "value": 100.0,
                "unit": "USD",
                "period_id": "PER-FY-2025",
                "provenance_kind": "filing_fact",
                "source_fact_refs": ["REC-TEST"],
                "calculation": None,
                "review_status": "approved",
            }
        ],
        "reconciliations": [
            {
                "check_id": "RECCHK-TEST",
                "check_type": "unit",
                "status": "passed",
                "difference": 0.0,
                "tolerance": 0.0,
                "fact_refs": ["FACT-REVENUE"],
                "message": "Synthetic unit check passed.",
            }
        ],
        "quality": {
            "status": "complete",
            "material_missing_fields": [],
            "blocking_error_codes": [],
            "review_error_codes": [],
        },
        "normalized_hash": "b" * 64,
    }
    assert list(validator.iter_errors(document)) == []
    document["facts"][0]["review_status"] = "unreviewed"
    assert list(validator.iter_errors(document))
    document["facts"][0]["review_status"] = "approved"
    document["quality"]["blocking_error_codes"] = ["DATA-BLOCKING"]
    assert list(validator.iter_errors(document))


def test_valuation_case_requires_human_hash_lock_and_unweighted_scenarios() -> None:
    schema = load_schema("valuation-case")
    case_lock = schema["properties"]["case_lock"]
    assert schema["properties"]["support_decision"]["properties"]["status"] == {
        "const": "supported"
    }
    assert "approved_hash" in case_lock["required"]
    assert case_lock["properties"]["approval_subject"] == {"const": "valuation-case"}
    assert case_lock["properties"]["actor_type"] == {"enum": ["human", None]}
    assert schema["$defs"]["scenario"]["properties"]["probability"] == {"type": "null"}
    assert schema["properties"]["scenarios"]["minItems"] == 3
    assert schema["properties"]["scenarios"]["maxItems"] == 3
    assert len(schema["properties"]["scenarios"]["allOf"]) == 3
    assert len(schema["properties"]["route"]["oneOf"]) == 5
    assert schema["allOf"], "Active case-lock invariants must be schema-enforced"


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
        "distribution",
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
    assert schema["properties"]["output_approval"]["properties"]["approval_subject"] == {
        "const": "valuation-output"
    }
    assert "license_decision_ref" in schema["$defs"]["sourceIndexItem"]["required"]


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


def test_m8_review_is_complete_with_later_external_conditions() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    review = REVIEW.read_text(encoding="utf-8")
    assert "Review status: Complete" in text
    assert "[x] approve M9 implementation planning with conditions" in text
    assert "[ ] authorize M9 implementation planning" in text
    assert "qualified legal/compliance reviewer" in text
    assert "this is not external counsel or provider sign-off" in text
    for finding in ["M8-R01", "M8-R02", "M8-R03", "M8-R04", "M8-R05"]:
        assert finding in review
    for condition in ["M8-C01", "M8-C02", "M8-C03", "M8-C04", "M8-C05", "M8-C06", "M8-C07"]:
        assert condition in review
    for heading in [
        "## Product owner",
        "## Financial reviewer",
        "## Security reviewer",
        "## Internal legal/compliance and data-licensing perimeter",
    ]:
        assert heading in text
