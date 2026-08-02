"""Young-company forecasts and survival adjustment composed with the M1 DCF engine."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Sequence

from tools.dcf import DCFResult, forecast_fcff, run_fcff_dcf


def _finite(name: str, value: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric and finite") from exc
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _series(name: str, values: Sequence[float]) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)) or not values:
        raise ValueError(f"{name} must contain at least one value")
    return tuple(_finite(f"{name}[{index}]", value) for index, value in enumerate(values, 1))


@dataclass(frozen=True)
class TopDownForecast:
    total_market: tuple[float, ...]
    market_share: tuple[float, ...]
    revenues: tuple[float, ...]


@dataclass(frozen=True)
class BottomUpForecast:
    revenues: tuple[float, ...]
    operating_incomes: tuple[float, ...]
    required_capacity_investment: tuple[float, ...]


@dataclass(frozen=True)
class TaxForecast:
    tax_rates: tuple[float, ...]
    taxes: tuple[float, ...]
    nol_balances: tuple[float, ...]


@dataclass(frozen=True)
class SurvivalAdjustment:
    survival_probability: float
    failure_probability: float
    going_concern_value: float
    failure_value: float
    survival_component: float
    failure_component: float
    adjusted_operating_asset_value: float
    failure_adjustment_delta: float
    calculation_trail: tuple[dict[str, float | str], ...]


@dataclass(frozen=True)
class YoungEquityBridge:
    pre_money_common_equity_value: float
    post_money_common_equity_value: float
    per_share_value: float
    calculation_trail: tuple[dict[str, float | str], ...]


def classify_young_company(
    *, history_years: float, revenue: float, operating_loss: bool, private_capital_dependence: bool
) -> tuple[bool, tuple[str, ...]]:
    """Classify a subject using explicit young-company indicators."""
    history = _finite("history_years", history_years)
    current_revenue = _finite("revenue", revenue)
    if history < 0 or current_revenue < 0:
        raise ValueError("history_years and revenue must be non-negative")
    reasons = []
    if history <= 5:
        reasons.append("limited operating history")
    if current_revenue == 0:
        reasons.append("pre-revenue")
    if operating_loss:
        reasons.append("operating loss")
    if private_capital_dependence:
        reasons.append("private-capital dependence")
    return len(reasons) >= 2, tuple(reasons)


def top_down_forecast(
    total_market: Sequence[float], market_share: Sequence[float]
) -> TopDownForecast:
    markets = _series("total_market", total_market)
    shares = _series("market_share", market_share)
    if len(markets) != len(shares):
        raise ValueError("total_market and market_share must have equal length")
    if any(value < 0 for value in markets) or any(not 0 <= value <= 1 for value in shares):
        raise ValueError("market values must be non-negative and shares must be bounded")
    revenues = tuple(market * share for market, share in zip(markets, shares))
    return TopDownForecast(markets, shares, revenues)


def bottom_up_forecast(
    capacity: Sequence[float],
    utilization: Sequence[float],
    unit_price: Sequence[float],
    unit_cost: Sequence[float],
    fixed_costs: Sequence[float],
    *,
    capacity_investment_per_unit: float,
) -> BottomUpForecast:
    inputs = tuple(_series(name, values) for name, values in (
        ("capacity", capacity), ("utilization", utilization), ("unit_price", unit_price),
        ("unit_cost", unit_cost), ("fixed_costs", fixed_costs),
    ))
    if len({len(values) for values in inputs}) != 1:
        raise ValueError("bottom-up forecast series must have equal length")
    capacities, utilization_values, prices, costs, fixed = inputs
    if any(value < 0 for values in (capacities, prices, costs, fixed) for value in values):
        raise ValueError("bottom-up operating inputs must be non-negative")
    if any(not 0 <= value <= 1 for value in utilization_values):
        raise ValueError("utilization must be between 0 and 1")
    investment_rate = _finite("capacity_investment_per_unit", capacity_investment_per_unit)
    if investment_rate < 0:
        raise ValueError("capacity_investment_per_unit must be non-negative")
    units = tuple(cap * use for cap, use in zip(capacities, utilization_values))
    revenues = tuple(count * price for count, price in zip(units, prices))
    operating = tuple(count * (price - cost) - fixed_cost for count, price, cost, fixed_cost in zip(units, prices, costs, fixed))
    investments = tuple(max(0.0, capacities[index] - (capacities[index - 1] if index else capacities[index])) * investment_rate for index in range(len(capacities)))
    return BottomUpForecast(revenues, operating, investments)


def margin_convergence(current_margin: float, target_margin: float, periods: int) -> tuple[float, ...]:
    current = _finite("current_margin", current_margin)
    target = _finite("target_margin", target_margin)
    if periods < 1:
        raise ValueError("periods must be positive")
    step = (target - current) / periods
    return tuple(current + step * period for period in range(1, periods + 1))


def apply_nol_carryforward(
    operating_incomes: Sequence[float], marginal_tax_rate: float, *, initial_nol: float = 0.0
) -> TaxForecast:
    incomes = _series("operating_incomes", operating_incomes)
    rate = _finite("marginal_tax_rate", marginal_tax_rate)
    nol = _finite("initial_nol", initial_nol)
    if not 0 <= rate <= 1 or nol < 0:
        raise ValueError("tax rate must be bounded and initial NOL non-negative")
    effective_rates: list[float] = []
    taxes: list[float] = []
    balances: list[float] = []
    for income in incomes:
        if income <= 0:
            nol += -income
            tax = 0.0
        else:
            sheltered = min(nol, income)
            nol -= sheltered
            tax = (income - sheltered) * rate
        taxes.append(tax)
        effective_rates.append(0.0 if income <= 0 else tax / income)
        balances.append(nol)
    return TaxForecast(tuple(effective_rates), tuple(taxes), tuple(balances))


def reinvestment_from_revenue_changes(
    revenues: Sequence[float], sales_to_capital_ratio: float, *, initial_revenue: float, lag_periods: int = 0
) -> tuple[float, ...]:
    values = _series("revenues", revenues)
    ratio = _finite("sales_to_capital_ratio", sales_to_capital_ratio)
    previous = _finite("initial_revenue", initial_revenue)
    if ratio <= 0 or previous < 0 or lag_periods < 0:
        raise ValueError("sales-to-capital must be positive; revenue and lag must be non-negative")
    growth_investment = []
    for revenue in values:
        growth_investment.append(max(0.0, revenue - previous) / ratio)
        previous = revenue
    result = [0.0] * len(values)
    for growth_period, amount in enumerate(growth_investment):
        investment_period = growth_period - lag_periods
        if investment_period >= 0:
            result[investment_period] += amount
    return tuple(result)


def discount_rate_path(initial_rate: float, mature_rate: float, periods: int) -> tuple[float, ...]:
    initial = _finite("initial_rate", initial_rate)
    mature = _finite("mature_rate", mature_rate)
    if periods < 1 or initial <= -1 or mature <= -1:
        raise ValueError("periods must be positive and rates greater than -100%")
    if periods == 1:
        return (mature,)
    return tuple(initial + (mature - initial) * index / (periods - 1) for index in range(periods))


def reconcile_probabilities(failure_probability: float, survival_probability: float, *, tolerance: float = 1e-9) -> tuple[float, float]:
    failure = _finite("failure_probability", failure_probability)
    survival = _finite("survival_probability", survival_probability)
    if not 0 <= failure <= 1 or not 0 <= survival <= 1:
        raise ValueError("probabilities must be between 0 and 1")
    if abs(failure + survival - 1.0) > tolerance:
        raise ValueError("failure and survival probabilities must sum to 1")
    return failure, survival


def survival_adjustment(
    going_concern_value: float,
    failure_probability: float,
    survival_probability: float,
    failure_value: float,
    *,
    failure_value_basis: str = "operating-assets",
    failure_premium_in_discount_rate: bool = False,
    failure_loss_in_cash_flows: bool = False,
) -> SurvivalAdjustment:
    going = _finite("going_concern_value", going_concern_value)
    failure_value_number = _finite("failure_value", failure_value)
    failure, survival = reconcile_probabilities(failure_probability, survival_probability)
    if failure_value_basis != "operating-assets":
        raise ValueError("failure value must be reconciled to the operating-assets basis")
    if failure_premium_in_discount_rate or failure_loss_in_cash_flows:
        raise ValueError("failure risk would be double counted")
    survival_component = survival * going
    failure_component = failure * failure_value_number
    adjusted = survival_component + failure_component
    return SurvivalAdjustment(
        survival, failure, going, failure_value_number, survival_component, failure_component,
        adjusted, adjusted - going,
        (
            {"step": "going_concern_component", "probability": survival, "value": survival_component},
            {"step": "failure_component", "probability": failure, "value": failure_component},
            {"step": "survival_adjusted_operating_value", "value": adjusted},
            {"step": "failure_adjustment_delta", "value": adjusted - going},
        ),
    )


def bridge_young_company_equity(
    adjusted_operating_asset_value: float,
    *,
    existing_cash: float = 0.0,
    authorized_financing_proceeds: float = 0.0,
    financing_authorized: bool = False,
    debt_and_senior_claims: float = 0.0,
    option_and_other_equity_claim_value: float = 0.0,
    option_value_explicit: bool = False,
    current_share_count: float,
    negative_fcff_present_value_included: bool = True,
    future_shares_added_to_current_denominator: bool = False,
) -> YoungEquityBridge:
    operating = _finite("adjusted_operating_asset_value", adjusted_operating_asset_value)
    cash = _finite("existing_cash", existing_cash)
    financing = _finite("authorized_financing_proceeds", authorized_financing_proceeds)
    debt = _finite("debt_and_senior_claims", debt_and_senior_claims)
    options = _finite("option_and_other_equity_claim_value", option_and_other_equity_claim_value)
    shares = _finite("current_share_count", current_share_count)
    if financing and not financing_authorized:
        raise ValueError("financing proceeds must be authorized and retained")
    if options and not option_value_explicit:
        raise ValueError("option deduction requires an explicit option value")
    if negative_fcff_present_value_included and future_shares_added_to_current_denominator:
        raise ValueError("future financing dilution would be double counted")
    if shares <= 0:
        raise ValueError("current_share_count must be positive")
    pre_money = operating + cash - debt - options
    post_money = pre_money + financing
    per_share = post_money / shares
    return YoungEquityBridge(
        pre_money, post_money, per_share,
        (
            {"step": "pre_money_common_equity", "value": pre_money},
            {"step": "authorized_financing_proceeds", "value": financing},
            {"step": "post_money_common_equity", "value": post_money},
            {"step": "per_share_value", "value": per_share},
        ),
    )


def run_going_concern_fcff(
    revenues: Sequence[float], operating_margins: Sequence[float], tax_rates: Sequence[float],
    reinvestments: Sequence[float], discount_rates: Sequence[float], terminal_growth_rate: float,
    terminal_discount_rate: float,
) -> tuple[tuple[float, ...], DCFResult]:
    """Create FCFF and delegate all DCF mechanics to the M1 engine."""
    cash_flows = forecast_fcff(revenues, operating_margins, tax_rates, reinvestments)
    result = run_fcff_dcf(cash_flows, discount_rates, terminal_growth_rate, terminal_discount_rate=terminal_discount_rate)
    return cash_flows, result
