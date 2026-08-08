from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M6-cycle-aware-judgment-layer-contract.md"
CLAIMS = ROOT / "extraction/reviewed/M6-cycle-aware-judgment-layer-claims.yaml"
MANIFEST = ROOT / "extraction/manifests/M6-cycle-aware-judgment-layer.yaml"
CHECKLIST = ROOT / "templates/m6-cycle-aware-judgment-review-checklist.md"


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def test_m6_claim_set_is_reviewed_and_dual_source() -> None:
    document = yaml.safe_load(CLAIMS.read_text(encoding="utf-8"))
    claims = document["claims"]

    assert document["source_ids"] == [
        "SRC-DAMODARAN-DARK-SIDE-2018",
        "SRC-MARKS-MASTERING-MARKET-CYCLE-2018",
    ]
    assert len(claims) == 36
    assert [claim["id"] for claim in claims] == [
        f"CLM-CYC-{index:03d}" for index in range(1, 37)
    ]
    assert {claim["status"] for claim in claims} == {"reviewed"}
    assert {claim["reviewer"] for claim in claims} == {"fvi-maintainers"}


def test_m6_manifest_preserves_source_roles_and_exclusions() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["review_status"] == "approved"
    assert manifest["scope"]["methodology_source"]["source_id"] == (
        "SRC-DAMODARAN-DARK-SIDE-2018"
    )
    assert manifest["scope"]["judgment_source"]["source_id"] == (
        "SRC-MARKS-MASTERING-MARKET-CYCLE-2018"
    )
    assert manifest["copyright_controls"] == {
        "raw_text_committed": False,
        "tables_or_figures_reproduced": False,
        "sequential_extract_committed": False,
    }


def test_m6_valuation_and_judgment_outputs_are_isolated() -> None:
    text = _contract_text()

    assert "a `valuation_input_handoff`" in text
    assert "a `judgment_overlay`" in text
    assert "The overlay never changes the intrinsic-value result." in text
    assert "`intrinsic_value_reference` is unchanged by the judgment overlay" in text
    assert "Market psychology and risk attitude" in text
    assert "Direct DCF input with no financial bridge" in text


def test_m6_treatment_routing_is_exclusive_and_regime_bound() -> None:
    text = _contract_text()

    for mode in (
        "`normalized_inputs`",
        "`transition_to_normal`",
        "`current_expectations`",
        "`stop`",
    ):
        assert mode in text
    assert "Exactly one `valuation_treatment.mode` is selected" in text
    assert "Exactly one valuation-treatment payload is present" in text
    assert "`current_expectations` is required for `unstable` or `structural_break`" in text
    assert "cannot include a hidden historical-normal terminal anchor" in text


def test_m6_dates_extremes_and_scenarios_are_governed() -> None:
    text = _contract_text()

    assert "Every evidence date must be on or before `valuation_date`." in text
    assert "Stale evidence remains visible" in text
    assert "An extreme requires non-stale price-to-value evidence" in text
    assert "sum to one within tolerance" in text
    assert "reports a range and does not manufacture an expected value" in text


def test_m6_dimension_alignment_is_independently_recomputable() -> None:
    text = _contract_text()

    assert "`band_implication`" in text
    assert "An unavailable dimension must use `signal: neutral`" in text
    assert "two available dimensions are aligned" in text
    assert "The validator must recompute the alignment count" in text


def test_m6_market_credit_and_issuer_distress_evidence_are_separate() -> None:
    text = _contract_text()

    assert "Broad market credit is abundant" in text
    assert "issuer-specific leverage, liquidity, and refinancing weakness" in text
    assert "M6 applies no distress haircut" in text


def test_m6_adversarial_cases_name_rejection_reasons() -> None:
    section = _contract_text().split("### Adversarial cases", 1)[1].split(
        "## Acceptance criteria", 1
    )[0]
    cases = [line for line in section.splitlines() if line.startswith("- ")]

    assert len(cases) == 27
    assert all("**Expected rejection:**" in case for case in cases)


def test_m6_review_records_approval_without_implementation() -> None:
    contract = _contract_text()
    checklist = CHECKLIST.read_text(encoding="utf-8")

    assert "Status: Approved for implementation" in contract
    assert "locked baseline for M6 implementation" in contract
    assert "in a later separately authorized checkpoint" in contract
    assert "Decision: `[x] approve  [ ] request changes  [ ] reject`" in checklist
    assert "No M6 schema, engine, validator, fixture, workflow, Skill" in checklist
