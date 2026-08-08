import json
from pathlib import Path

import pytest

from tools.cycle_aware import build_current_expectations_scenario, build_transition_path
from tools.validate_cycle_aware_judgments import load_registry, validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "benchmarks" / "fixtures" / "cycle_aware"
EXPECTED_ROOT = ROOT / "benchmarks" / "expected"


@pytest.mark.parametrize(
    ("fixture_name", "expected_name"),
    [
        ("synthetic-established-cycle-industrial.json", "cycle-established-industrial-output.json"),
        ("synthetic-structural-break-commodity.json", "cycle-structural-break-commodity-output.json"),
    ],
)
def test_cycle_aware_benchmarks_validate_and_recompute(
    fixture_name: str, expected_name: str
) -> None:
    document = json.loads((FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8"))
    schema, sources, claims, narratives = load_registry(ROOT)
    assert validate_document(document, schema, sources, claims, narratives) == []
    expected = json.loads((EXPECTED_ROOT / expected_name).read_text(encoding="utf-8"))
    actual = {
        "judgment_id": document["judgment_id"],
        "regime": document["cycle_assessment"]["regime"],
        "treatment_mode": document["valuation_treatment"]["mode"],
        "handoff_status": document["valuation_input_handoff"]["status"],
        "value_range": document["intrinsic_value_reference"]["value_range"],
        "expected_value": document["intrinsic_value_reference"]["expected_value"],
        "market_cycle_position": document["judgment_overlay"]["market_cycle_position"],
        "confidence": document["judgment_overlay"]["confidence"],
        "alignment_count": document["judgment_overlay"]["alignment_count"],
        "review_posture": document["judgment_overlay"]["review_posture"],
        "overlay_changes_intrinsic_value": document["risk_controls"]["overlay_changes_intrinsic_value"],
        "distress_handoff": document["risk_controls"]["distress_handoff"] is not None,
    }
    assert actual == expected


def test_established_cycle_transition_matches_engine() -> None:
    document = json.loads(
        (FIXTURE_ROOT / "synthetic-established-cycle-industrial.json").read_text(encoding="utf-8")
    )
    payload = document["valuation_treatment"]["transition_to_normal"]
    assert payload["period_inputs"] == build_transition_path(
        payload["current_input_set"],
        payload["normalized_anchor"],
        payload["transition_periods"],
        payload["tax_rate"],
    )


def test_structural_break_scenarios_are_isolated_and_recomputed() -> None:
    document = json.loads(
        (FIXTURE_ROOT / "synthetic-structural-break-commodity.json").read_text(encoding="utf-8")
    )
    scenarios = document["valuation_treatment"]["current_expectations"]["scenarios"]
    assert len({item["calculation_trail_id"] for item in scenarios}) == len(scenarios)
    for scenario in scenarios:
        inputs = scenario["input_set"]
        assert scenario["period_inputs"] == build_current_expectations_scenario(
            driver_values=[item["value"] for item in inputs["driver_curve"]],
            volumes=inputs["volumes"],
            fixed_costs=inputs["fixed_costs"],
            unit_costs=inputs["unit_costs"],
            base_reinvestments=inputs["base_reinvestments"],
            reinvestment_sensitivity=inputs["reinvestment_sensitivity"],
            base_driver=inputs["base_driver"],
            initial_invested_capital=inputs["initial_invested_capital"],
            tax_rate=inputs["tax_rate"],
            base_financing_cost=inputs["base_financing_cost"],
            funding_sensitivity=inputs["funding_sensitivity"],
        )
