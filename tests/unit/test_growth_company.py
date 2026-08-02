import pytest

from tools.growth_company import (
    apply_failure_handoff,
    build_growth_forecast,
    build_revenue_path,
    build_stable_terminal,
    classify_growth_company,
    margin_convergence_path,
    reinvestment_path,
    run_growth_company_valuation,
)


def test_growth_company_classification_requires_every_lifecycle_gate() -> None:
    assert classify_growth_company(
        m3_boundary_cleared=True,
        demonstrated_commercial_product=True,
        meaningful_operating_evidence=True,
        material_growth_asset_value=True,
    )
    assert not classify_growth_company(
        m3_boundary_cleared=False,
        demonstrated_commercial_product=True,
        meaningful_operating_evidence=True,
        material_growth_asset_value=True,
    )


def test_revenue_path_exposes_absolute_scale() -> None:
    revenues, changes = build_revenue_path(100, [0.2, 0.1, 0.05])
    assert revenues == pytest.approx([120, 132, 138.6])
    assert changes == pytest.approx([20, 12, 6.6])


def test_margin_path_reaches_target_without_a_silent_jump() -> None:
    path = margin_convergence_path(0.10, 0.20, 4, start_year=1, end_year=4)
    assert path == pytest.approx([0.125, 0.15, 0.175, 0.20])


def test_each_reinvestment_method_has_one_input() -> None:
    result = reinvestment_path(
        [20, 10, 5],
        [15, 18, 20],
        ["revenue-change", "fundamental", "capacity-holiday"],
        [2, None, None],
        [None, 0.5, None],
        [None, None, 1],
    )
    assert result == pytest.approx([10, 9, 1])
    with pytest.raises(ValueError, match="exactly one method input"):
        reinvestment_path([20], [15], ["revenue-change"], [2], [0.5], [None])


def test_growth_forecast_rolls_forward_tax_capital_roc_and_fcff() -> None:
    forecast = build_growth_forecast(
        base_revenue=100,
        revenue_growth_rates=[0.2, 0.1],
        operating_margins=[0.1, 0.12],
        marginal_tax_rate=0.25,
        initial_nol=5,
        initial_invested_capital=50,
        reinvestment_methods=["revenue-change", "revenue-change"],
        sales_to_capital_ratios=[2, 2],
        fundamental_reinvestment_rates=[None, None],
        capacity_reinvestments=[None, None],
    )
    assert forecast.revenues == pytest.approx([120, 132])
    assert forecast.cash_taxes == pytest.approx([1.75, 3.96])
    assert forecast.reinvestments == pytest.approx([10, 6])
    assert forecast.invested_capital == pytest.approx([60, 66])
    assert forecast.fcff == pytest.approx([0.25, 5.88])


def test_terminal_fcff_is_rebuilt_from_stable_state() -> None:
    terminal = build_stable_terminal(
        1000,
        growth_rate=0.03,
        operating_margin=0.20,
        tax_rate=0.25,
        return_on_capital=0.12,
        cost_of_capital=0.08,
    )
    assert terminal.stable_reinvestment_rate == pytest.approx(0.25)
    assert terminal.terminal_fcff == pytest.approx(115.875)
    assert terminal.terminal_value == pytest.approx(2317.5)


def test_period_rates_converge_and_discount_cumulatively() -> None:
    forecast = build_growth_forecast(
        base_revenue=100,
        revenue_growth_rates=[0.10, 0.05],
        operating_margins=[0.10, 0.12],
        marginal_tax_rate=0.25,
        initial_nol=0,
        initial_invested_capital=50,
        reinvestment_methods=["revenue-change", "revenue-change"],
        sales_to_capital_ratios=[2, 2],
        fundamental_reinvestment_rates=[None, None],
        capacity_reinvestments=[None, None],
    )
    valuation = run_growth_company_valuation(
        forecast,
        [0.10, 0.08],
        stable_growth_rate=0.03,
        stable_operating_margin=0.12,
        stable_tax_rate=0.25,
        stable_return_on_capital=0.10,
        stable_cost_of_capital=0.08,
    )
    assert valuation.cumulative_discount_factors == pytest.approx([1 / 1.10, 1 / (1.10 * 1.08)])
    assert valuation.terminal.terminal_fcff != pytest.approx(forecast.fcff[-1] * 1.03)


def test_failure_handoff_uses_m3_semantics_once() -> None:
    assert apply_failure_handoff(
        100, material=True, failure_probability=0.1, survival_probability=0.9, failure_value=20
    ) == pytest.approx(92)
    with pytest.raises(ValueError, match="double counted"):
        apply_failure_handoff(
            100,
            material=True,
            failure_probability=0.1,
            survival_probability=0.9,
            failure_value=20,
            failure_premium_in_discount_rate=True,
        )
