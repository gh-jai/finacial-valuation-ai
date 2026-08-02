import pytest

from tools.decline_distress import (
    bridge_to_common_equity,
    build_closure_value,
    build_decline_forecast,
    build_financing_path,
    classify_declining_company,
    contingent_survival_value,
    estimate_distress_sale_value,
    net_divestiture_proceeds,
    run_going_concern_valuation,
    select_orderly_liquidation,
    select_quadrant,
    turnaround_expected_value,
    value_orderly_liquidation,
)


def _forecast():
    return build_decline_forecast(
        base_revenue=100,
        revenue_growth_rates=[-0.10, -0.05],
        operating_margins=[0.10, 0.08],
        tax_rates=[0.25, 0.25],
        reinvestments=[-5, -4],
        initial_invested_capital=50,
    )


def _financing(operating_incomes):
    return build_financing_path(
        initial_face_debt=40,
        debt_issuances=[0, 0],
        debt_repayments=[5, 5],
        cash_interest=[4, 3.5],
        operating_incomes=operating_incomes,
        tax_rates=[0.25, 0.25],
        market_value_debt=[35, 30],
        market_value_equity=[45, 50],
        pretax_costs_of_debt=[0.10, 0.09],
        costs_of_equity=[0.16, 0.14],
    )


def test_decline_classification_and_quadrant_are_independent() -> None:
    assert classify_declining_company(
        m3_boundary_cleared=True,
        m4_boundary_cleared=True,
        mature_boundary_cleared=True,
        cycle_boundary_cleared=True,
        multi_period_decline_evidence=True,
        sector_evidence=True,
    )
    assert select_quadrant("reversible", "high") == "reversible_high"


def test_decline_forecast_permits_governed_negative_reinvestment() -> None:
    forecast = _forecast()
    assert forecast.revenues == pytest.approx([90, 85.5])
    assert forecast.cash_taxes == pytest.approx([2.25, 1.71])
    assert forecast.invested_capital == pytest.approx([45, 41])
    assert forecast.fcff == pytest.approx([11.75, 9.13])


def test_invested_capital_cannot_reach_zero_before_a_later_period() -> None:
    with pytest.raises(ValueError, match="opening invested capital must remain positive"):
        build_decline_forecast(
            base_revenue=100,
            revenue_growth_rates=[-0.1, -0.1],
            operating_margins=[0.1, 0.1],
            tax_rates=[0.25, 0.25],
            reinvestments=[-50, 0],
            initial_invested_capital=50,
        )


def test_loss_produces_no_cash_tax_or_negative_interest_tax_benefit() -> None:
    forecast = build_decline_forecast(
        base_revenue=100,
        revenue_growth_rates=[-0.1],
        operating_margins=[-0.1],
        tax_rates=[0.25],
        reinvestments=[0],
        initial_invested_capital=50,
    )
    financing = build_financing_path(
        initial_face_debt=20,
        debt_issuances=[0],
        debt_repayments=[0],
        cash_interest=[3],
        operating_incomes=forecast.operating_incomes,
        tax_rates=[0.25],
        market_value_debt=[15],
        market_value_equity=[5],
        pretax_costs_of_debt=[0.15],
        costs_of_equity=[0.25],
    )
    assert forecast.cash_taxes == (0.0,)
    assert financing.taxable_operating_income_available == (0.0,)
    assert financing.cash_interest_tax_benefits == (0.0,)
    assert financing.after_tax_costs_of_debt == pytest.approx([0.15])


def test_financing_path_rolls_face_debt_and_recomputes_market_wacc() -> None:
    financing = _financing(_forecast().operating_incomes)
    assert financing.opening_face_debt == pytest.approx([40, 35])
    assert financing.closing_face_debt == pytest.approx([35, 30])
    assert financing.debt_to_capital_ratios == pytest.approx([0.4375, 0.375])
    assert financing.costs_of_capital == pytest.approx([0.1228125, 0.1128125])


def test_closure_modes_are_mutually_exclusive_and_recomputed() -> None:
    finite = build_closure_value(
        "finite_life",
        final_revenue=100,
        terminal_growth_rate=None,
        terminal_operating_margin=None,
        terminal_tax_rate=None,
        terminal_return_on_capital=None,
        terminal_cost_of_capital=None,
        finite_life_proceeds=10,
    )
    negative = build_closure_value(
        "negative_perpetuity",
        final_revenue=100,
        terminal_growth_rate=-0.02,
        terminal_operating_margin=0.08,
        terminal_tax_rate=0.25,
        terminal_return_on_capital=0.06,
        terminal_cost_of_capital=0.10,
        finite_life_proceeds=None,
    )
    assert finite.terminal_or_closure_value == pytest.approx(10)
    assert negative.terminal_reinvestment_rate == pytest.approx(-1 / 3)
    with pytest.raises(ValueError, match="must be negative"):
        build_closure_value(
            "negative_perpetuity",
            final_revenue=100,
            terminal_growth_rate=0.01,
            terminal_operating_margin=0.08,
            terminal_tax_rate=0.25,
            terminal_return_on_capital=0.06,
            terminal_cost_of_capital=0.10,
            finite_life_proceeds=None,
        )


def test_going_concern_uses_financing_costs_and_one_closure_value() -> None:
    forecast = _forecast()
    financing = _financing(forecast.operating_incomes)
    closure = build_closure_value(
        "finite_life",
        final_revenue=forecast.revenues[-1],
        terminal_growth_rate=None,
        terminal_operating_margin=None,
        terminal_tax_rate=None,
        terminal_return_on_capital=None,
        terminal_cost_of_capital=None,
        finite_life_proceeds=10,
    )
    value = run_going_concern_valuation(forecast, financing, closure)
    assert value.operating_asset_value == pytest.approx(25.775164398496155)
    assert len(value.calculation_trail) == 5


def test_divestiture_and_orderly_liquidation_are_separate() -> None:
    assert net_divestiture_proceeds(100, 5, 10) == pytest.approx(85)
    liquidation = value_orderly_liquidation([50, 40], [0.10, 0.10])
    assert liquidation == pytest.approx(78.51239669421486)
    selected, selected_value = select_orderly_liquidation(70, liquidation)
    assert selected == "orderly_liquidation"
    assert selected_value == pytest.approx(liquidation)


def test_turnaround_uses_value_weighting_not_input_averaging() -> None:
    status, turnaround, total = turnaround_expected_value(80, 140, 0.25)
    assert (status, turnaround, total) == pytest.approx((60, 35, 95))


@pytest.mark.parametrize(
    "method,kwargs,expected",
    [
        ("going_concern_haircut", {"reference_going_concern_asset_value": 100, "haircut": 0.4}, 55),
        ("existing_asset_value", {"existing_asset_after_tax_income": 8, "existing_asset_cost_of_capital": 0.1}, 75),
        ("adjusted_book_assets", {"eligible_book_assets": 100, "economic_impairment": 0.2, "forced_sale_discount": 0.1}, 67),
    ],
)
def test_distress_sale_methods_expose_costs(method, kwargs, expected) -> None:
    result = estimate_distress_sale_value(
        method, **kwargs, direct_sale_costs=3, indirect_operating_costs=2
    )
    assert result.distress_sale_value == pytest.approx(expected)


def test_contingent_survival_applies_distress_once() -> None:
    result = contingent_survival_value(
        100, 40, survival_probability=0.8, distress_probability=0.2
    )
    assert result.contingent_value == pytest.approx(88)
    with pytest.raises(ValueError, match="double counted"):
        contingent_survival_value(
            100,
            40,
            survival_probability=0.8,
            distress_probability=0.2,
            distress_premium_in_discount_rates=True,
        )


def test_claim_bridge_is_applied_once_after_contingent_value() -> None:
    bridge = bridge_to_common_equity(
        88,
        cash=10,
        market_value_debt=70,
        senior_claims=5,
        hybrid_claims=2,
        option_claims=1,
        share_count=10,
        limited_liability_floor=True,
    )
    assert bridge.common_equity_value == pytest.approx(20)
    assert bridge.per_share_value == pytest.approx(2)
