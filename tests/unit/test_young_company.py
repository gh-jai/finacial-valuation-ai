import pytest

from tools.young_company import (
    apply_nol_carryforward,
    bottom_up_forecast,
    bridge_young_company_equity,
    classify_young_company,
    discount_rate_path,
    margin_convergence,
    reconcile_probabilities,
    reinvestment_from_revenue_changes,
    run_going_concern_fcff,
    survival_adjustment,
    top_down_forecast,
)


def test_young_company_classification() -> None:
    applies, reasons = classify_young_company(history_years=2, revenue=5, operating_loss=True, private_capital_dependence=True)
    assert applies and len(reasons) == 3
    assert not classify_young_company(history_years=12, revenue=500, operating_loss=False, private_capital_dependence=False)[0]


def test_top_down_forecast() -> None:
    result = top_down_forecast([100, 120], [0.1, 0.15])
    assert result.revenues == pytest.approx([10, 18])


def test_bottom_up_forecast() -> None:
    result = bottom_up_forecast([100, 130], [0.5, 0.6], [2, 2], [1, 1], [10, 10], capacity_investment_per_unit=0.2)
    assert result.revenues == pytest.approx([100, 156])
    assert result.operating_incomes == pytest.approx([40, 68])
    assert result.required_capacity_investment == pytest.approx([0, 6])


def test_margin_convergence_reaches_target() -> None:
    margins = margin_convergence(-0.2, 0.2, 4)
    assert margins == pytest.approx([-0.1, 0.0, 0.1, 0.2])


def test_nol_carryforward_shelters_income_before_tax() -> None:
    result = apply_nol_carryforward([-10, 4, 10], 0.25)
    assert result.nol_balances == pytest.approx([10, 6, 0])
    assert result.taxes == pytest.approx([0, 0, 1])
    assert result.tax_rates == pytest.approx([0, 0, 0.1])


def test_reinvestment_lag_moves_growth_investment_earlier() -> None:
    immediate = reinvestment_from_revenue_changes([10, 20, 30], 2, initial_revenue=0)
    lagged = reinvestment_from_revenue_changes([10, 20, 30], 2, initial_revenue=0, lag_periods=1)
    assert immediate == pytest.approx([5, 5, 5])
    assert lagged == pytest.approx([5, 5, 0])


def test_time_varying_rate_path_and_cumulative_discounting() -> None:
    rates = discount_rate_path(0.2, 0.1, 3)
    assert rates == pytest.approx([0.2, 0.15, 0.1])
    _, result = run_going_concern_fcff([100, 110, 120], [0.1] * 3, [0] * 3, [5] * 3, rates, 0.02, 0.09)
    assert result.cumulative_discount_factors == pytest.approx([1 / 1.2, 1 / (1.2 * 1.15), 1 / (1.2 * 1.15 * 1.1)])


def test_terminal_constraint_is_delegated_to_m1() -> None:
    with pytest.raises(ValueError, match="terminal_growth_rate"):
        run_going_concern_fcff([100], [0.1], [0.2], [1], [0.1], 0.1, 0.1)


def test_probability_reconciliation_and_survival_arithmetic() -> None:
    assert reconcile_probabilities(0.2, 0.8) == (0.2, 0.8)
    result = survival_adjustment(100, 0.2, 0.8, 10)
    assert result.survival_component == 80
    assert result.failure_component == 2
    assert result.adjusted_operating_asset_value == 82
    assert result.failure_adjustment_delta == -18
    with pytest.raises(ValueError, match="sum to 1"):
        reconcile_probabilities(0.2, 0.7)
    with pytest.raises(ValueError, match="between 0 and 1"):
        reconcile_probabilities(1.2, -0.2)


def test_basis_and_risk_double_counting_are_rejected() -> None:
    with pytest.raises(ValueError, match="operating-assets basis"):
        survival_adjustment(100, 0.2, 0.8, 10, failure_value_basis="equity")
    with pytest.raises(ValueError, match="double counted"):
        survival_adjustment(100, 0.2, 0.8, 10, failure_premium_in_discount_rate=True)
    with pytest.raises(ValueError, match="double counted"):
        survival_adjustment(100, 0.2, 0.8, 10, failure_loss_in_cash_flows=True)


def test_equity_bridge_pre_money_post_money_and_per_share() -> None:
    result = bridge_young_company_equity(100, existing_cash=10, authorized_financing_proceeds=20, financing_authorized=True, debt_and_senior_claims=30, option_and_other_equity_claim_value=5, option_value_explicit=True, current_share_count=5)
    assert result.pre_money_common_equity_value == 75
    assert result.post_money_common_equity_value == 95
    assert result.per_share_value == 19


def test_equity_bridge_double_counting_controls() -> None:
    with pytest.raises(ValueError, match="authorized"):
        bridge_young_company_equity(100, authorized_financing_proceeds=10, current_share_count=5)
    with pytest.raises(ValueError, match="explicit option value"):
        bridge_young_company_equity(100, option_and_other_equity_claim_value=5, current_share_count=5)
    with pytest.raises(ValueError, match="dilution"):
        bridge_young_company_equity(100, current_share_count=5, future_shares_added_to_current_denominator=True)
