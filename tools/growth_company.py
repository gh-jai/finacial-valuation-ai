"""Growth-company scaling, fade, stable-state, and DCF composition for M4."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite

from tools.dcf import calculate_terminal_value, discount_fcff
from tools.young_company import apply_nol_carryforward, survival_adjustment


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


def _same_length(**series: Sequence[object]) -> int:
    lengths = {len(values) for values in series.values()}
    if len(lengths) != 1 or not lengths or next(iter(lengths)) == 0:
        raise ValueError(f"{', '.join(series)} must have equal non-zero length")
    return next(iter(lengths))


@dataclass(frozen=True)
class GrowthForecast:
    revenues: tuple[float, ...]
    absolute_revenue_changes: tuple[float, ...]
    operating_incomes: tuple[float, ...]
    tax_rates: tuple[float, ...]
    cash_taxes: tuple[float, ...]
    nol_balances: tuple[float, ...]
    after_tax_operating_incomes: tuple[float, ...]
    reinvestments: tuple[float, ...]
    invested_capital: tuple[float, ...]
    implied_returns_on_capital: tuple[float, ...]
    fcff: tuple[float, ...]


@dataclass(frozen=True)
class StableTerminal:
    terminal_revenue: float
    terminal_after_tax_operating_income: float
    stable_reinvestment_rate: float
    terminal_reinvestment: float
    terminal_fcff: float
    terminal_value: float


@dataclass(frozen=True)
class GrowthValuation:
    forecast: GrowthForecast
    terminal: StableTerminal
    cumulative_discount_factors: tuple[float, ...]
    discounted_fcff: tuple[float, ...]
    forecast_present_value: float
    terminal_present_value: float
    operating_asset_value: float
    terminal_value_share: float
    calculation_trail: tuple[dict[str, float | int | str], ...]


def classify_growth_company(
    *,
    m3_boundary_cleared: bool,
    demonstrated_commercial_product: bool,
    meaningful_operating_evidence: bool,
    material_growth_asset_value: bool,
) -> bool:
    """Apply the reviewed life-cycle routing gate before M4 forecasting."""
    return all(
        (
            m3_boundary_cleared,
            demonstrated_commercial_product,
            meaningful_operating_evidence,
            material_growth_asset_value,
        )
    )


def build_revenue_path(
    base_revenue: float, revenue_growth_rates: Sequence[float]
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Scale revenue from a current normalized base and expose absolute changes."""
    previous = _finite("base_revenue", base_revenue)
    rates = _series("revenue_growth_rates", revenue_growth_rates)
    if previous < 0 or any(rate <= -1 for rate in rates):
        raise ValueError("base revenue must be non-negative and growth rates greater than -100%")
    revenues: list[float] = []
    changes: list[float] = []
    for rate in rates:
        revenue = previous * (1 + rate)
        revenues.append(revenue)
        changes.append(revenue - previous)
        previous = revenue
    return tuple(revenues), tuple(changes)


def margin_convergence_path(
    current_margin: float,
    target_margin: float,
    periods: int,
    *,
    start_year: int = 1,
    end_year: int | None = None,
) -> tuple[float, ...]:
    """Create an explicit linear current-to-target operating-margin path."""
    current = _finite("current_margin", current_margin)
    target = _finite("target_margin", target_margin)
    end = periods if end_year is None else end_year
    if periods < 1 or start_year < 1 or end < start_year or end > periods:
        raise ValueError("margin convergence years must fall inside the forecast")
    path: list[float] = []
    span = end - start_year + 1
    for year in range(1, periods + 1):
        if year < start_year:
            path.append(current)
        elif year >= end:
            path.append(target)
        else:
            path.append(current + (target - current) * (year - start_year + 1) / span)
    return tuple(path)


def reinvestment_path(
    absolute_revenue_changes: Sequence[float],
    after_tax_operating_incomes: Sequence[float],
    methods: Sequence[str],
    sales_to_capital_ratios: Sequence[float | None],
    fundamental_reinvestment_rates: Sequence[float | None],
    capacity_reinvestments: Sequence[float | None],
) -> tuple[float, ...]:
    """Apply exactly one reviewed reinvestment method in each forecast period."""
    changes = _series("absolute_revenue_changes", absolute_revenue_changes)
    incomes = _series("after_tax_operating_incomes", after_tax_operating_incomes)
    _same_length(
        absolute_revenue_changes=changes,
        after_tax_operating_incomes=incomes,
        methods=methods,
        sales_to_capital_ratios=sales_to_capital_ratios,
        fundamental_reinvestment_rates=fundamental_reinvestment_rates,
        capacity_reinvestments=capacity_reinvestments,
    )
    allowed = {"revenue-change", "fundamental", "capacity-holiday"}
    result: list[float] = []
    for index, (change, income, method, ratio_value, rate_value, capacity_value) in enumerate(
        zip(
            changes,
            incomes,
            methods,
            sales_to_capital_ratios,
            fundamental_reinvestment_rates,
            capacity_reinvestments,
        ),
        1,
    ):
        if method not in allowed:
            raise ValueError(f"reinvestment_method[{index}] is unsupported")
        supplied = sum(value is not None for value in (ratio_value, rate_value, capacity_value))
        if supplied != 1:
            raise ValueError(f"reinvestment_method[{index}] must have exactly one method input")
        if method == "revenue-change":
            if ratio_value is None or rate_value is not None or capacity_value is not None:
                raise ValueError(f"reinvestment_method[{index}] conflicts with method inputs")
            ratio = _finite(f"sales_to_capital_ratios[{index}]", ratio_value)
            if ratio <= 0:
                raise ValueError("sales-to-capital ratios must be positive")
            amount = max(0.0, change) / ratio
        elif method == "fundamental":
            if rate_value is None or ratio_value is not None or capacity_value is not None:
                raise ValueError(f"reinvestment_method[{index}] conflicts with method inputs")
            rate = _finite(f"fundamental_reinvestment_rates[{index}]", rate_value)
            if not 0 <= rate <= 1 or income < 0:
                raise ValueError(
                    "fundamental reinvestment requires non-negative income and a bounded rate"
                )
            amount = income * rate
        else:
            if capacity_value is None or ratio_value is not None or rate_value is not None:
                raise ValueError(f"reinvestment_method[{index}] conflicts with method inputs")
            amount = _finite(f"capacity_reinvestments[{index}]", capacity_value)
            if amount < 0:
                raise ValueError("capacity-holiday reinvestment must be non-negative")
        result.append(amount)
    return tuple(result)


def build_growth_forecast(
    *,
    base_revenue: float,
    revenue_growth_rates: Sequence[float],
    operating_margins: Sequence[float],
    marginal_tax_rate: float,
    initial_nol: float,
    initial_invested_capital: float,
    reinvestment_methods: Sequence[str],
    sales_to_capital_ratios: Sequence[float | None],
    fundamental_reinvestment_rates: Sequence[float | None],
    capacity_reinvestments: Sequence[float | None],
) -> GrowthForecast:
    """Build the M4 operating series before delegating discounting to M1."""
    revenues, changes = build_revenue_path(base_revenue, revenue_growth_rates)
    margins = _series("operating_margins", operating_margins)
    _same_length(revenues=revenues, operating_margins=margins)
    operating_incomes = tuple(revenue * margin for revenue, margin in zip(revenues, margins))
    taxes = apply_nol_carryforward(operating_incomes, marginal_tax_rate, initial_nol=initial_nol)
    after_tax = tuple(income - tax for income, tax in zip(operating_incomes, taxes.taxes))
    reinvestments = reinvestment_path(
        changes,
        after_tax,
        reinvestment_methods,
        sales_to_capital_ratios,
        fundamental_reinvestment_rates,
        capacity_reinvestments,
    )
    opening_capital = _finite("initial_invested_capital", initial_invested_capital)
    if opening_capital <= 0:
        raise ValueError("initial invested capital must be positive")
    invested_capital: list[float] = []
    implied_returns: list[float] = []
    previous_capital = opening_capital
    for income, reinvestment in zip(after_tax, reinvestments):
        implied_returns.append(income / previous_capital)
        previous_capital += reinvestment
        invested_capital.append(previous_capital)
    fcff = tuple(income - reinvestment for income, reinvestment in zip(after_tax, reinvestments))
    return GrowthForecast(
        revenues,
        changes,
        operating_incomes,
        taxes.tax_rates,
        taxes.taxes,
        taxes.nol_balances,
        after_tax,
        reinvestments,
        tuple(invested_capital),
        tuple(implied_returns),
        fcff,
    )


def build_stable_terminal(
    final_revenue: float,
    *,
    growth_rate: float,
    operating_margin: float,
    tax_rate: float,
    return_on_capital: float,
    cost_of_capital: float,
) -> StableTerminal:
    """Rebuild terminal FCFF from one internally consistent mature state."""
    revenue = _finite("final_revenue", final_revenue)
    growth = _finite("stable_growth_rate", growth_rate)
    margin = _finite("stable_operating_margin", operating_margin)
    tax = _finite("stable_tax_rate", tax_rate)
    roc = _finite("stable_return_on_capital", return_on_capital)
    rate = _finite("stable_cost_of_capital", cost_of_capital)
    if revenue < 0 or growth < 0 or not 0 <= tax <= 1 or roc <= 0:
        raise ValueError("stable revenue, growth, tax, and return inputs are invalid")
    if growth >= rate:
        raise ValueError("stable growth must be below terminal cost of capital")
    reinvestment_rate = growth / roc
    if not 0 <= reinvestment_rate <= 1:
        raise ValueError("stable reinvestment rate must be finite and bounded")
    terminal_revenue = revenue * (1 + growth)
    terminal_after_tax_income = terminal_revenue * margin * (1 - tax)
    terminal_reinvestment = terminal_after_tax_income * reinvestment_rate
    terminal_fcff = terminal_after_tax_income - terminal_reinvestment
    # M1's helper accepts the final explicit FCFF and grows it once. Supplying the
    # rebuilt next-period FCFF on an equivalent prior-period basis preserves its
    # Gordon-growth arithmetic without carrying forward the high-growth FCFF.
    _, terminal_value = calculate_terminal_value(terminal_fcff / (1 + growth), growth, rate)
    return StableTerminal(
        terminal_revenue,
        terminal_after_tax_income,
        reinvestment_rate,
        terminal_reinvestment,
        terminal_fcff,
        terminal_value,
    )


def run_growth_company_valuation(
    forecast: GrowthForecast,
    discount_rates: Sequence[float],
    *,
    stable_growth_rate: float,
    stable_operating_margin: float,
    stable_tax_rate: float,
    stable_return_on_capital: float,
    stable_cost_of_capital: float,
) -> GrowthValuation:
    """Discount explicit M4 FCFF and a separately rebuilt stable terminal FCFF."""
    rates = _series("discount_rates", discount_rates)
    _same_length(fcff=forecast.fcff, discount_rates=rates)
    if abs(rates[-1] - stable_cost_of_capital) > 1e-10:
        raise ValueError("final discount rate must converge to stable cost of capital")
    terminal = build_stable_terminal(
        forecast.revenues[-1],
        growth_rate=stable_growth_rate,
        operating_margin=stable_operating_margin,
        tax_rate=stable_tax_rate,
        return_on_capital=stable_return_on_capital,
        cost_of_capital=stable_cost_of_capital,
    )
    discounted = discount_fcff(forecast.fcff, rates)
    terminal_present_value = terminal.terminal_value * discounted.cumulative_discount_factors[-1]
    operating_value = discounted.present_value + terminal_present_value
    if not isfinite(operating_value):
        raise ValueError("operating asset value must be finite")
    terminal_share = 0.0 if operating_value == 0 else terminal_present_value / operating_value
    trail: list[dict[str, float | int | str]] = []
    for period, (fcff, rate, factor, present_value) in enumerate(
        zip(
            forecast.fcff,
            rates,
            discounted.cumulative_discount_factors,
            discounted.discounted_cash_flows,
        ),
        1,
    ):
        trail.append(
            {
                "step": "discount_fcff",
                "period": period,
                "fcff": fcff,
                "discount_rate": rate,
                "cumulative_discount_factor": factor,
                "value": present_value,
            }
        )
    trail.extend(
        (
            {"step": "rebuilt_terminal_fcff", "value": terminal.terminal_fcff},
            {"step": "terminal_value", "value": terminal.terminal_value},
            {"step": "terminal_present_value", "value": terminal_present_value},
            {"step": "operating_asset_value", "value": operating_value},
        )
    )
    return GrowthValuation(
        forecast,
        terminal,
        discounted.cumulative_discount_factors,
        discounted.discounted_cash_flows,
        discounted.present_value,
        terminal_present_value,
        operating_value,
        terminal_share,
        tuple(trail),
    )


def apply_failure_handoff(
    going_concern_value: float,
    *,
    material: bool,
    failure_probability: float = 0.0,
    survival_probability: float = 1.0,
    failure_value: float = 0.0,
    failure_premium_in_discount_rate: bool = False,
    failure_loss_in_cash_flows: bool = False,
) -> float:
    """Apply M3 expected-value semantics once when discrete failure is material."""
    if not material:
        if failure_probability != 0 or survival_probability != 1 or failure_value != 0:
            raise ValueError("immaterial failure handoff must not alter going-concern value")
        return _finite("going_concern_value", going_concern_value)
    return survival_adjustment(
        going_concern_value,
        failure_probability,
        survival_probability,
        failure_value,
        failure_premium_in_discount_rate=failure_premium_in_discount_rate,
        failure_loss_in_cash_flows=failure_loss_in_cash_flows,
    ).adjusted_operating_asset_value
