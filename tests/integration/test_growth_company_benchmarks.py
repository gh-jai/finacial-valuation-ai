import json
from pathlib import Path

import pytest

from tools.growth_company import (
    apply_failure_handoff,
    build_growth_forecast,
    run_growth_company_valuation,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "fixture_name,expected_name",
    [
        ("synthetic-asset-light-platform.json", "growth-asset-light-platform-output.json"),
        ("synthetic-capacity-expansion.json", "growth-capacity-expansion-output.json"),
    ],
)
def test_growth_company_benchmark_is_deterministic(fixture_name: str, expected_name: str) -> None:
    fixture = json.loads(
        (ROOT / "benchmarks/fixtures/growth_company" / fixture_name).read_text(encoding="utf-8")
    )
    expected = json.loads(
        (ROOT / "benchmarks/expected" / expected_name).read_text(encoding="utf-8")
    )
    base, forecast_data, stable = (
        fixture["base_period"],
        fixture["forecast"],
        fixture["stable_state"],
    )
    forecast = build_growth_forecast(
        base_revenue=base["revenues"],
        revenue_growth_rates=forecast_data["revenue_growth_rates"],
        operating_margins=forecast_data["operating_margins"],
        marginal_tax_rate=forecast_data["marginal_tax_rate"],
        initial_nol=base["net_operating_loss"],
        initial_invested_capital=base["invested_capital"],
        reinvestment_methods=forecast_data["reinvestment_method"],
        sales_to_capital_ratios=forecast_data["sales_to_capital_ratios"],
        fundamental_reinvestment_rates=forecast_data["fundamental_reinvestment_rates"],
        capacity_reinvestments=forecast_data["capacity_reinvestments"],
    )
    valuation = run_growth_company_valuation(
        forecast,
        forecast_data["discount_rates"],
        stable_growth_rate=stable["growth_rate"],
        stable_operating_margin=stable["operating_margin"],
        stable_tax_rate=stable["tax_rate"],
        stable_return_on_capital=stable["return_on_capital"],
        stable_cost_of_capital=stable["cost_of_capital"],
    )
    assert forecast.fcff == pytest.approx(expected["fcff"])
    assert valuation.terminal.terminal_fcff == pytest.approx(expected["terminal_fcff"])
    assert valuation.forecast_present_value == pytest.approx(expected["forecast_present_value"])
    assert valuation.terminal_present_value == pytest.approx(expected["terminal_present_value"])
    assert valuation.operating_asset_value == pytest.approx(expected["operating_asset_value"])
    assert valuation.terminal_value_share == pytest.approx(expected["terminal_value_share"])
    if "adjusted_operating_asset_value" in expected:
        failure = fixture["failure_handoff"]
        adjusted = apply_failure_handoff(
            valuation.operating_asset_value,
            material=failure["material"],
            failure_probability=failure["failure_probability"],
            survival_probability=failure["survival_probability"],
            failure_value=failure["failure_value"],
        )
        assert adjusted == pytest.approx(expected["adjusted_operating_asset_value"])


def test_m1_m2_and_m3_composition_regression() -> None:
    from tools.dcf import run_fcff_dcf
    from tools.narrative import load_narrative, value_narrative
    from tools.young_company import survival_adjustment

    assert run_fcff_dcf([10, 11, 12], 0.1, 0.02).operating_asset_value == pytest.approx(
        142.14876033057845
    )
    narrative = load_narrative(ROOT / "benchmarks/fixtures/narratives/synthetic-base.json")
    assert value_narrative(narrative)[1].per_share_value == pytest.approx(14.670223152576089)
    assert survival_adjustment(100, 0.2, 0.8, 10).adjusted_operating_asset_value == pytest.approx(
        82
    )
