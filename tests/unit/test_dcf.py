import math

import pytest

from tools.dcf import run_fcff_dcf


def test_basic_fcff_dcf_matches_synthetic_benchmark() -> None:
    result = run_fcff_dcf([10.0, 11.0, 12.0], 0.10, 0.02)

    assert result.forecast_present_value == pytest.approx(27.1975957926)
    assert result.terminal_value == pytest.approx(153.0)
    assert result.terminal_present_value == pytest.approx(114.9511645379)
    assert result.enterprise_value == pytest.approx(142.1487603306)
    assert result.equity_value is None
    assert result.per_share_value is None


def test_enterprise_to_equity_bridge() -> None:
    result = run_fcff_dcf(
        [10.0, 11.0, 12.0],
        0.10,
        0.02,
        cash_and_non_operating_assets=20.0,
        debt_and_debt_like_claims=50.0,
        share_count=10.0,
    )

    assert result.equity_value == pytest.approx(result.enterprise_value - 30.0)
    assert result.per_share_value == pytest.approx(result.equity_value / 10.0)


@pytest.mark.parametrize("growth", [0.10, 0.11])
def test_rejects_terminal_growth_at_or_above_discount_rate(growth: float) -> None:
    with pytest.raises(ValueError, match="terminal_growth_rate"):
        run_fcff_dcf([10.0], 0.10, growth)


def test_rejects_non_finite_inputs() -> None:
    with pytest.raises(ValueError, match="finite"):
        run_fcff_dcf([10.0, math.inf], 0.10, 0.02)


def test_rejects_non_positive_share_count() -> None:
    with pytest.raises(ValueError, match="share_count"):
        run_fcff_dcf([10.0], 0.10, 0.02, share_count=0.0)
