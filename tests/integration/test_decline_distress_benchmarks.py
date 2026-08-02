import json
from pathlib import Path

import pytest

from tools.decline_distress import (
    bridge_to_common_equity,
    build_closure_value,
    build_decline_forecast,
    build_financing_path,
    contingent_survival_value,
    estimate_distress_sale_value,
    run_going_concern_valuation,
    select_orderly_liquidation,
    turnaround_expected_value,
    value_orderly_liquidation,
)

ROOT = Path(__file__).resolve().parents[2]


def _common(document: dict):
    base = document["base_period"]
    stored_forecast = document["status_quo_forecast"]
    stored_financing = document["financing_path"]
    stored_closure = document["closure"]
    forecast = build_decline_forecast(
        base_revenue=base["continuing_revenues"],
        revenue_growth_rates=stored_forecast["revenue_growth_rates"],
        operating_margins=stored_forecast["operating_margins"],
        tax_rates=stored_forecast["tax_rates"],
        reinvestments=stored_forecast["reinvestments"],
        initial_invested_capital=base["invested_capital"],
    )
    financing = build_financing_path(
        initial_face_debt=base["face_debt"],
        debt_issuances=stored_financing["debt_issuances"],
        debt_repayments=stored_financing["debt_repayments"],
        cash_interest=stored_financing["cash_interest"],
        operating_incomes=forecast.operating_incomes,
        tax_rates=stored_forecast["tax_rates"],
        market_value_debt=stored_financing["market_value_debt"],
        market_value_equity=stored_financing["market_value_equity"],
        pretax_costs_of_debt=stored_financing["pretax_costs_of_debt"],
        costs_of_equity=stored_financing["costs_of_equity"],
    )
    closure = build_closure_value(
        stored_closure["mode"],
        final_revenue=forecast.revenues[-1],
        terminal_growth_rate=stored_closure["terminal_growth_rate"],
        terminal_operating_margin=stored_closure["terminal_operating_margin"],
        terminal_tax_rate=stored_closure["terminal_tax_rate"],
        terminal_return_on_capital=stored_closure["terminal_return_on_capital"],
        terminal_cost_of_capital=stored_closure["terminal_cost_of_capital"],
        finite_life_proceeds=stored_closure["finite_life_proceeds"],
    )
    return forecast, financing, run_going_concern_valuation(forecast, financing, closure)


def test_orderly_wind_down_benchmark_is_deterministic() -> None:
    document = json.loads(
        (ROOT / "benchmarks/fixtures/decline_distress/synthetic-orderly-legacy-distributor.json").read_text(encoding="utf-8")
    )
    expected = json.loads(
        (ROOT / "benchmarks/expected/decline-orderly-legacy-distributor-output.json").read_text(encoding="utf-8")
    )
    forecast, financing, going = _common(document)
    orderly = document["orderly_liquidation"]
    liquidation = value_orderly_liquidation(
        [item["net_proceeds"] for item in orderly["sale_schedule"]],
        [item["discount_rate"] for item in orderly["sale_schedule"]],
    )
    _, selected = select_orderly_liquidation(going.operating_asset_value, liquidation)
    bridge = document["claim_bridge"]
    equity = bridge_to_common_equity(
        selected,
        cash=bridge["cash"],
        market_value_debt=bridge["market_value_debt"],
        senior_claims=bridge["senior_claims"],
        hybrid_claims=bridge["hybrid_claims"],
        option_claims=bridge["option_claims"],
        share_count=bridge["share_count"],
        limited_liability_floor=bridge["limited_liability_floor"],
    )
    assert forecast.fcff == pytest.approx(expected["fcff"])
    assert financing.costs_of_capital == pytest.approx(expected["costs_of_capital"])
    assert going.operating_asset_value == pytest.approx(expected["going_concern_value"])
    assert liquidation == pytest.approx(expected["orderly_liquidation_value"])
    assert selected == pytest.approx(expected["selected_no_distress_value"])
    assert equity.common_equity_value == pytest.approx(expected["common_equity_value"])
    assert equity.per_share_value == pytest.approx(expected["per_share_value"])


def test_levered_service_operator_benchmark_is_deterministic() -> None:
    document = json.loads(
        (ROOT / "benchmarks/fixtures/decline_distress/synthetic-levered-service-operator.json").read_text(encoding="utf-8")
    )
    expected = json.loads(
        (ROOT / "benchmarks/expected/decline-levered-service-operator-output.json").read_text(encoding="utf-8")
    )
    forecast, financing, going = _common(document)
    turnaround = document["turnaround_case"]
    _, _, no_distress = turnaround_expected_value(
        going.operating_asset_value,
        turnaround["turnaround_value"],
        turnaround["probability_of_change"],
    )
    distress = document["distress_case"]
    sale = estimate_distress_sale_value(
        distress["recovery_method"],
        existing_asset_after_tax_income=distress["existing_asset_after_tax_income"],
        existing_asset_cost_of_capital=distress["existing_asset_cost_of_capital"],
        direct_sale_costs=distress["direct_sale_costs"],
        indirect_operating_costs=distress["indirect_operating_costs"],
    )
    contingent = contingent_survival_value(
        no_distress,
        sale.distress_sale_value,
        survival_probability=distress["survival_probability"],
        distress_probability=distress["distress_probability"],
    )
    bridge = document["claim_bridge"]
    equity = bridge_to_common_equity(
        contingent.contingent_value,
        cash=bridge["cash"],
        market_value_debt=bridge["market_value_debt"],
        senior_claims=bridge["senior_claims"],
        hybrid_claims=bridge["hybrid_claims"],
        option_claims=bridge["option_claims"],
        share_count=bridge["share_count"],
        limited_liability_floor=bridge["limited_liability_floor"],
    )
    assert forecast.fcff == pytest.approx(expected["fcff"])
    assert financing.costs_of_capital == pytest.approx(expected["costs_of_capital"])
    assert going.operating_asset_value == pytest.approx(expected["going_concern_value"])
    assert no_distress == pytest.approx(expected["no_distress_expected_value"])
    assert sale.distress_sale_value == pytest.approx(expected["distress_sale_value"])
    assert contingent.contingent_value == pytest.approx(expected["contingent_value"])
    assert equity.common_equity_value == pytest.approx(expected["common_equity_value"])
    assert equity.per_share_value == pytest.approx(expected["per_share_value"])


def test_m1_to_m4_composition_regression() -> None:
    from tools.dcf import run_fcff_dcf
    from tools.growth_company import build_revenue_path
    from tools.young_company import survival_adjustment

    assert run_fcff_dcf([10, 11, 12], 0.1, 0.02).operating_asset_value == pytest.approx(
        142.14876033057845
    )
    assert build_revenue_path(100, [0.1, 0.05])[0] == pytest.approx([110, 115.5])
    assert survival_adjustment(100, 0.2, 0.8, 10).adjusted_operating_asset_value == pytest.approx(82)
