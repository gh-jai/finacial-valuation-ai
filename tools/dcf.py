"""Small, dependency-free FCFF discounted cash flow engine for synthetic benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class DCFResult:
    forecast_present_value: float
    terminal_value: float
    terminal_present_value: float
    enterprise_value: float
    equity_value: float | None = None
    per_share_value: float | None = None


def _require_finite(name: str, value: float) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")


def run_fcff_dcf(
    cash_flows: Sequence[float],
    discount_rate: float,
    terminal_growth_rate: float,
    *,
    cash_and_non_operating_assets: float = 0.0,
    debt_and_debt_like_claims: float = 0.0,
    share_count: float | None = None,
) -> DCFResult:
    """Value forecast FCFF with a Gordon-growth terminal value.

    Cash flows are assumed to occur at each period end. FCFF is discounted at
    the cost of capital. Optional bridge inputs convert enterprise value to
    equity and per-share value.
    """
    if not cash_flows:
        raise ValueError("cash_flows must contain at least one forecast period")
    _require_finite("discount_rate", discount_rate)
    _require_finite("terminal_growth_rate", terminal_growth_rate)
    if discount_rate <= -1:
        raise ValueError("discount_rate must be greater than -100%")
    if terminal_growth_rate >= discount_rate:
        raise ValueError("terminal_growth_rate must be below discount_rate")

    normalized = [float(value) for value in cash_flows]
    for index, value in enumerate(normalized, start=1):
        _require_finite(f"cash_flows[{index}]", value)

    forecast_pv = sum(
        cash_flow / ((1.0 + discount_rate) ** period)
        for period, cash_flow in enumerate(normalized, start=1)
    )
    terminal_value = normalized[-1] * (1.0 + terminal_growth_rate) / (
        discount_rate - terminal_growth_rate
    )
    terminal_pv = terminal_value / ((1.0 + discount_rate) ** len(normalized))
    enterprise_value = forecast_pv + terminal_pv

    for name, value in {
        "cash_and_non_operating_assets": cash_and_non_operating_assets,
        "debt_and_debt_like_claims": debt_and_debt_like_claims,
    }.items():
        _require_finite(name, value)

    bridge_requested = (
        cash_and_non_operating_assets != 0.0
        or debt_and_debt_like_claims != 0.0
        or share_count is not None
    )
    equity_value = None
    per_share_value = None
    if bridge_requested:
        equity_value = (
            enterprise_value
            + cash_and_non_operating_assets
            - debt_and_debt_like_claims
        )
        if share_count is not None:
            _require_finite("share_count", share_count)
            if share_count <= 0:
                raise ValueError("share_count must be positive")
            per_share_value = equity_value / share_count

    return DCFResult(
        forecast_present_value=forecast_pv,
        terminal_value=terminal_value,
        terminal_present_value=terminal_pv,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        per_share_value=per_share_value,
    )
