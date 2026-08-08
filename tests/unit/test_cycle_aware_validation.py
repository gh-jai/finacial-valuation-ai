import copy
import json
from pathlib import Path

import pytest

from tools.validate_cycle_aware_judgments import load_registry, validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "benchmarks" / "fixtures" / "cycle_aware"


def inputs(name: str = "synthetic-established-cycle-industrial.json") -> tuple[dict, tuple]:
    document = json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))
    return document, load_registry(ROOT)


def errors_for(document: dict, registry: tuple) -> list[str]:
    return validate_document(document, *registry)


def test_valid_cycle_documents() -> None:
    for name in (
        "synthetic-established-cycle-industrial.json",
        "synthetic-structural-break-commodity.json",
    ):
        document, registry = inputs(name)
        assert errors_for(document, registry) == []


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda d: d["subject_classification"].update(exposure_type="not_supported"), "must stop"),
        (lambda d: d["subject_classification"]["observation_window"].update(strong_and_weak_conditions=False), "representative"),
        (lambda d: d["subject_classification"]["lifecycle_boundaries"].update(m3_cleared=False), "life-cycle"),
        (lambda d: d["current_base"].update(currency="EUR"), "currency"),
        (lambda d: d["cycle_evidence"]["items"][2]["supports"].remove("subject_classification_counterevidence"), "bidirectionally"),
        (lambda d: d["cycle_assessment"].update(regime="structural_break"), "current expectations"),
        (lambda d: d["cycle_assessment"].update(regime="structural_break", break_assessment=None), "structural break"),
        (lambda d: d["valuation_treatment"].update(mode="normalized_inputs"), "payload"),
        (lambda d: d["valuation_treatment"]["transition_to_normal"].update(recovery_growth_applied=True), "recovery"),
        (lambda d: d["valuation_treatment"]["transition_to_normal"]["period_inputs"][0].update(revenue=101), "current base"),
        (lambda d: d["valuation_treatment"]["transition_to_normal"]["period_inputs"][-1].update(revenue=121), "normalized anchor"),
        (lambda d: d["cycle_evidence"]["items"][0].update(as_of_date="2027-01-01"), "future-dated evidence"),
        (lambda d: d["cycle_evidence"]["items"][0].update(stale=True), "staleness"),
        (lambda d: d["judgment_overlay"]["dimension_assessments"].pop(), "five evidence dimensions"),
        (lambda d: d["judgment_overlay"].update(alignment_count=5), "alignment count"),
        (lambda d: d["judgment_overlay"].update(review_posture="opportunity_review"), "review posture"),
        (lambda d: d["judgment_overlay"]["price_value_observation"].update(observed_after_intrinsic_value=False), "price-to-value ordering"),
        (lambda d: d["judgment_overlay"]["price_value_observation"].update(intrinsic_value=94), "immutable precomputed"),
        (lambda d: d["risk_controls"].update(overlay_changes_intrinsic_value=True), "overlay"),
        (lambda d: d["risk_controls"].update(hidden_numeric_score=True), "hidden numeric score"),
        (lambda d: d["risk_controls"].update(trade_instruction="buy 5%"), "trade instruction"),
        (lambda d: d["risk_controls"].update(excluded_methods=["relative_valuation"]), "excluded method"),
        (lambda d: d["risk_controls"].update(m6_distress_adjustment=True), "distress"),
        (lambda d: d["intrinsic_value_reference"].update(overlay_adjusted_value=101), "schema"),
        (lambda d: d["cycle_assessment"]["supporting_evidence_refs"].append("EVID-UNKNOWN"), "unknown evidence"),
        (lambda d: d["traceability"].update(source_refs=["SRC-UNKNOWN"]), "unknown source"),
        (lambda d: d["traceability"].update(claim_refs=["CLM-CYC-999"]), "unknown claim"),
        (lambda d: d["traceability"].update(narrative_assertion_refs=["NAR-A-999"]), "unknown narrative"),
    ],
)
def test_established_cycle_adversarial_mutations(mutation, message: str) -> None:
    document, registry = inputs()
    mutation(document)
    assert any(message in error for error in errors_for(document, registry))


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda d: d["valuation_treatment"]["current_expectations"]["driver_curve"][0].update(as_of_date="2026-09-01"), "curve as-of"),
        (lambda d: d["valuation_treatment"]["current_expectations"]["driver_curve"][0].update(unit="EUR/unit"), "driver-curve units"),
        (lambda d: d["valuation_treatment"]["current_expectations"].update(carry_limitation_disclosed=False), "carry"),
        (lambda d: d["valuation_treatment"]["current_expectations"]["scenarios"][0]["period_inputs"][0].update(revenue=999), "driver mapping"),
        (lambda d: d["valuation_treatment"]["current_expectations"]["scenarios"][1].update(calculation_trail_id="TRAIL-LOW"), "isolated"),
        (lambda d: d["intrinsic_value_reference"].update(expected_value=100), "expected value"),
        (lambda d: d["judgment_overlay"].update(confidence="low"), "confidence"),
        (lambda d: d["judgment_overlay"]["dimension_assessments"][4].update(stale_evidence_refs=["EVID-CREDIT"]), "extreme"),
        (lambda d: d["risk_controls"].update(distress_handoff=None), "WFL-DST-001"),
    ],
)
def test_structural_break_adversarial_mutations(mutation, message: str) -> None:
    document, registry = inputs("synthetic-structural-break-commodity.json")
    mutation(document)
    assert any(message in error for error in errors_for(document, registry))


def test_overlapping_treatment_payload_is_rejected() -> None:
    document, registry = inputs()
    document["valuation_treatment"]["normalized_inputs"] = copy.deepcopy(
        document["valuation_treatment"]["transition_to_normal"]
    )
    assert any("payload" in error for error in errors_for(document, registry))


def test_normalized_inputs_recompute_and_handoff_the_complete_vector() -> None:
    document, registry = inputs()
    anchor = copy.deepcopy(document["valuation_treatment"]["transition_to_normal"]["normalized_anchor"])
    methods = []
    for name, value in anchor.items():
        methods.append(
            {
                "input_name": name,
                "method": "absolute_historical_average",
                "observations": [value, value],
                "current_scale": None,
                "company_adjustment": None,
                "driver_sensitivity": None,
                "intercept": None,
                "scale_change_material": False,
                "comparability_documented": True,
                "calculated_value": value,
            }
        )
    document["valuation_treatment"] = {
        "mode": "normalized_inputs",
        "normalized_inputs": {
            "normalization_window": {
                "start": "2016-01-01",
                "end": "2025-12-31",
                "representative": True,
                "strong_and_weak_conditions": True,
                "basis": "Synthetic full cycle.",
            },
            "input_methods": methods,
            "normalized_input_set": anchor,
            "limitations": ["Synthetic normalization."],
            "recovery_growth_applied": False,
        },
    }
    document["valuation_input_handoff"].update(
        treatment_mode="normalized_inputs", period_inputs=[], normalized_input_set=anchor
    )
    assert errors_for(document, registry) == []
    document["valuation_treatment"]["normalized_inputs"]["input_methods"].pop()
    assert any("complete governed vector" in error for error in errors_for(document, registry))
