from datetime import date

import pytest

from tools.cycle_aware import (
    alignment_count,
    build_current_expectations_scenario,
    build_transition_path,
    classify_cycle_subject,
    derive_confidence,
    derive_review_posture,
    normalize_input,
    probability_weighted_value,
)


def test_cycle_classification_requires_company_specific_driver_mapping() -> None:
    assert classify_cycle_subject(
        exposure_type="economic_cycle",
        external_driver="industrial-production index",
        linked_financial_series=["revenue", "operating_margin"],
        observation_years=10,
        has_strong_and_weak_conditions=True,
        lifecycle_boundaries_cleared=True,
    )
    assert not classify_cycle_subject(
        exposure_type="economic_cycle",
        external_driver="industry label only",
        linked_financial_series=[],
        observation_years=1,
        has_strong_and_weak_conditions=False,
        lifecycle_boundaries_cleared=True,
    )


def test_normalization_methods_recompute_governed_values() -> None:
    assert normalize_input("absolute_historical_average", [8, 10, 12]) == pytest.approx(10)
    assert normalize_input(
        "relative_historical_average", [0.08, 0.10, 0.12], current_scale=200
    ) == pytest.approx(20)
    assert normalize_input(
        "sector_average_with_adjustment", [0.09, 0.11], company_adjustment=-0.01
    ) == pytest.approx(0.09)
    assert normalize_input(
        "normalized_external_driver",
        [70],
        driver_sensitivity=2.5,
        intercept=5,
    ) == pytest.approx(180)


def test_transition_starts_at_current_base_and_converges_once() -> None:
    path = build_transition_path(
        current={
            "driver": 80,
            "revenue": 100,
            "operating_margin": 0.04,
            "reinvestment": 2,
            "invested_capital": 60,
            "leverage": 0.4,
            "financing_cost": 0.09,
        },
        normalized_anchor={
            "driver": 100,
            "revenue": 120,
            "operating_margin": 0.10,
            "reinvestment": 8,
            "invested_capital": 75,
            "leverage": 0.3,
            "financing_cost": 0.07,
        },
        periods=3,
        tax_rate=0.25,
    )
    assert path[0]["revenue"] == pytest.approx(100)
    assert path[-1]["revenue"] == pytest.approx(120)
    assert path[-1]["operating_income"] == pytest.approx(12)
    assert [row["revenue"] for row in path] == pytest.approx([100, 106.6666667, 113.3333333, 120])


def test_driver_scenario_recomputes_complete_financial_mapping() -> None:
    result = build_current_expectations_scenario(
        driver_values=[60, 70],
        volumes=[2, 2.1],
        fixed_costs=[20, 20],
        unit_costs=[15, 15],
        base_reinvestments=[5, 5],
        reinvestment_sensitivity=0.10,
        base_driver=60,
        initial_invested_capital=50,
        tax_rate=0.25,
        base_financing_cost=0.08,
        funding_sensitivity=-0.001,
    )
    assert result[0]["revenue"] == pytest.approx(120)
    assert result[0]["operating_income"] == pytest.approx(70)
    assert result[1]["reinvestment"] == pytest.approx(6)
    assert result[1]["financing_cost"] == pytest.approx(0.07)
    assert result[1]["invested_capital"] == pytest.approx(61)


def test_alignment_confidence_and_posture_are_deterministic() -> None:
    dimensions = [
        {"availability": "available", "band_implication": band, "stale_evidence_refs": [], "unresolved_strong_contradiction": False}
        for band in ["extreme_high", "above_midpoint", "extreme_high", "extreme_high", "above_midpoint"]
    ]
    assert alignment_count("extreme_high", dimensions) == 5
    assert derive_confidence("extreme_high", dimensions) == "high"
    assert derive_review_posture("extreme_high") == "defensive_review"
    assert derive_review_posture("extreme_low") == "opportunity_review"
    assert derive_review_posture("indeterminate") == "insufficient_evidence"


def test_probability_weighting_requires_one_reviewed_basis() -> None:
    assert probability_weighted_value(
        [80, 100, 130],
        [0.2, 0.5, 0.3],
        event_definitions=["average-price"] * 3,
        horizons=["2027-2029"] * 3,
        as_of_dates=[date(2026, 8, 1)] * 3,
    ) == pytest.approx(105)
    with pytest.raises(ValueError, match="sum to one"):
        probability_weighted_value(
            [80, 100],
            [0.2, 0.7],
            event_definitions=["price"] * 2,
            horizons=["2027"] * 2,
            as_of_dates=[date(2026, 8, 1)] * 2,
        )
