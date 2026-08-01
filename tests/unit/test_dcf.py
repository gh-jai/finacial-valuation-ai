import math

import pytest

from tools.dcf import (
    bridge_enterprise_to_equity,
    calculate_per_share_value,
    calculate_terminal_value,
    discount_fcff,
    estimate_sustainable_growth,
    forecast_fcff,
    run_dcf_sensitivity,
    run_fcff_dcf,
)


def test_basic_fcff_dcf_matches_synthetic_benchmark() -> None:
    result = run_fcff_dcf([10.0, 11.0, 12.0], 0.10, 0.02)

    assert result.forecast_present_value == pytest.approx(27.1975957926)
    assert result.terminal_cash_flow == pytest.approx(12.24)
    assert result.terminal_value == pytest.approx(153.0)
    assert result.terminal_present_value == pytest.approx(114.9511645379)
    assert result.operating_asset_value == pytest.approx(142.1487603306)
    assert result.enterprise_value == result.operating_asset_value
    assert result.equity_value is None
    assert result.per_share_value is None
    assert len(result.calculation_trail) == 6


def test_forecast_fcff_from_operating_drivers() -> None:
    result = forecast_fcff(
        revenues=[100.0, 110.0],
        operating_margins=[0.20, 0.21],
        tax_rates=[0.25, 0.25],
        reinvestments=[5.0, 6.0],
    )
    assert result == pytest.approx((10.0, 11.325))


def test_sustainable_growth_identity() -> None:
    assert estimate_sustainable_growth(0.40, 0.15) == pytest.approx(0.06)


def test_varying_discount_rates_use_cumulative_factors() -> None:
    discounted = discount_fcff([8.0, 10.0, 13.0], [0.08, 0.09, 0.10])
    expected_factors = (1 / 1.08, 1 / (1.08 * 1.09), 1 / (1.08 * 1.09 * 1.10))
    assert discounted.cumulative_discount_factors == pytest.approx(expected_factors)
    assert discounted.discounted_cash_flows == pytest.approx(
        tuple(value * factor for value, factor in zip((8.0, 10.0, 13.0), expected_factors))
    )


def test_separate_terminal_discount_rate() -> None:
    result = run_fcff_dcf(
        [8.0, 10.0, 13.0],
        [0.08, 0.09, 0.10],
        0.025,
        terminal_discount_rate=0.095,
    )
    assert result.terminal_discount_rate == pytest.approx(0.095)
    assert result.terminal_value == pytest.approx(190.35714285714283)


def test_terminal_value_uses_next_period_fcff() -> None:
    terminal_cash_flow, terminal_value = calculate_terminal_value(12.0, 0.02, 0.10)
    assert terminal_cash_flow == pytest.approx(12.24)
    assert terminal_value == pytest.approx(153.0)


@pytest.mark.parametrize("growth", [0.10, 0.11])
def test_rejects_terminal_growth_at_or_above_discount_rate(growth: float) -> None:
    with pytest.raises(ValueError, match="terminal_growth_rate"):
        run_fcff_dcf([10.0], 0.10, growth)


@pytest.mark.parametrize(
    ("cash_flows", "discount_rate"),
    [([10.0, math.inf], 0.10), ([10.0], math.nan), ([10.0], [math.inf])],
)
def test_rejects_non_finite_inputs(cash_flows: list[float], discount_rate: object) -> None:
    with pytest.raises(ValueError, match="finite"):
        run_fcff_dcf(cash_flows, discount_rate, 0.02)  # type: ignore[arg-type]


def test_rejects_empty_cash_flow_sequence() -> None:
    with pytest.raises(ValueError, match="at least one"):
        run_fcff_dcf([], 0.10, 0.02)


def test_rejects_mismatched_period_specific_rates() -> None:
    with pytest.raises(ValueError, match="match the cash-flow count"):
        run_fcff_dcf([10.0, 11.0], [0.10], 0.02)


@pytest.mark.parametrize("share_count", [0.0, -1.0, math.inf])
def test_rejects_invalid_share_count(share_count: float) -> None:
    with pytest.raises(ValueError, match="share_count"):
        run_fcff_dcf([10.0], 0.10, 0.02, share_count=share_count)


def test_enterprise_to_equity_bridge() -> None:
    assert bridge_enterprise_to_equity(150.0, 20.0, 50.0) == pytest.approx(120.0)
    result = run_fcff_dcf(
        [10.0, 11.0, 12.0],
        0.10,
        0.02,
        cash_and_non_operating_assets=20.0,
        debt_and_debt_like_claims=50.0,
    )
    assert result.equity_value == pytest.approx(result.operating_asset_value - 30.0)


def test_per_share_calculation() -> None:
    assert calculate_per_share_value(120.0, 10.0) == pytest.approx(12.0)
    result = run_fcff_dcf(
        [10.0, 11.0, 12.0],
        0.10,
        0.02,
        cash_and_non_operating_assets=20.0,
        debt_and_debt_like_claims=50.0,
        share_count=10.0,
    )
    assert result.per_share_value == pytest.approx(result.equity_value / 10.0)


def test_sensitivity_grid_is_deterministic() -> None:
    first = run_dcf_sensitivity([10.0, 11.0, 12.0], 0.10, [0.09, 0.10], [0.01, 0.02])
    second = run_dcf_sensitivity([10.0, 11.0, 12.0], 0.10, [0.09, 0.10], [0.01, 0.02])
    assert first == second
    assert len(first) == 4
