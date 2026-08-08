from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M7-governed-agentization-contract.md"
CLAIMS = ROOT / "extraction/reviewed/M7-governed-agentization-claims.yaml"
MANIFEST = ROOT / "extraction/manifests/M7-governed-agentization.yaml"
CHECKLIST = ROOT / "templates/m7-agentization-review-checklist.md"


def test_m7_claims_are_reviewed_and_within_two_sources() -> None:
    document = yaml.safe_load(CLAIMS.read_text(encoding="utf-8"))
    assert document["source_ids"] == [
        "SRC-DAMODARAN-INVESTMENT-FABLES",
        "SRC-BAID-JOYS-COMPOUNDING-ZH-2024",
    ]
    assert [item["id"] for item in document["claims"]] == [
        f"CLM-AGT-{index:03d}" for index in range(1, 21)
    ]
    assert {item["status"] for item in document["claims"]} == {"reviewed"}
    assert {item["reviewer"] for item in document["claims"]} == {"fvi-maintainers"}


def test_m7_manifest_locks_pages_and_excludes_trade_discussion() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["review_status"] == "approved"
    assert manifest["copyright_controls"] == {
        "raw_text_committed": False,
        "tables_or_figures_reproduced": False,
        "sequential_extract_committed": False,
    }
    assert manifest["scope"]["decision_process_source"]["excluded_ranges"] == [
        {
            "pdf_pages": "319-322",
            "reason": "The discussion turns to position holding and sale decisions, which cannot authorize M7 trading or portfolio actions.",
        }
    ]


def test_m7_contract_requires_exact_hash_human_gates_and_offline_execution() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "`case_lock` and `output_approval`" in text
    assert "An agent cannot create an approval." in text
    assert "all active approvals for the old hash become invalid" in text
    assert "Executor-reviewer role separation" in text
    assert "No CI test requires an OpenAI, Gemini, Anthropic, or other model API." in text
    assert "It cannot accept an arbitrary path." in text


def test_m7_contract_preserves_m1_m6_numerical_ownership_and_no_trade_boundary() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    assert "existing M1-M6 artifacts and deterministic engines" in text
    assert "Prompt arithmetic that replaces M1-M6 engines" in text
    assert "backtesting, screening, portfolio construction, trade timing" in text
    assert "It cannot change deterministic valuation output." in text


def test_m7_checklist_records_approved_baseline() -> None:
    checklist = CHECKLIST.read_text(encoding="utf-8")
    assert "Decision: `[x] approve implementation baseline" in checklist
    assert "Baid PDF pages 319-322 are excluded" in checklist
    assert "Independent validation does not import runtime hash or state helpers" in checklist
