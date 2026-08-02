"""Decline, distress, contingent-survival, and claim-bridge calculations for M5."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite

from tools.dcf import calculate_terminal_value, discount_fcff


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
class DeclineForecast:
    revenues: tuple[float, ...]
    operating_incomes: tuple[float, ...]
    cash_taxes: tuple[float, ...]
    after_tax_operating_incomes: tuple[float, ...]
    invested_capital: tuple[float, ...]
    implied_returns_on_capital: tuple[float, ...]
    fcff: tuple[float, ...]


@dataclass(frozen=True)
class FinancingPath:
    opening_face_debt: tuple[float, ...]
    closing_face_debt: tuple[float, ...]
    taxable_operating_income_available: tuple[float, ...]
    cash_interest_tax_benefits: tuple[float, ...]
    debt_to_capital_ratios: tuple[float, ...]
    equity_to_capital_ratios: tuple[float, ...]
    effective_interest_tax_rates: tuple[float, ...]
    after_tax_costs_of_debt: tuple[float, ...]
    costs_of_capital: tuple[float, ...]


@dataclass(frozen=True)
class ClosureValue:
    mode: str
    terminal_revenue: float
    terminal_after_tax_operating_income: float
    terminal_reinvestment_rate: float
    terminal_fcff: float
    terminal_or_closure_value: float


@dataclass(frozen=True)
class GoingConcernValue:
    cumulative_discount_factors: tuple[float, ...]
    discounted_fcff: tuple[float, ...]
    forecast_present_value: float
    terminal_or_closure_present_value: float
    operating_asset_value: float
    calculation_trail: tuple[dict[str, float | int | str], ...]


@dataclass(frozen=True)
class DistressSaleValue:
    method: str
    gross_recovery_value: float
    direct_sale_costs: float
    indirect_operating_costs: float
    distress_sale_value: float


@dataclass(frozen=True)
class ContingentValue:
    survival_probability: float
    distress_probability: float
    survival_component: float
    distress_component: float
    contingent_value: float
    calculation_trail: tuple[dict[str, float | str], ...]


@dataclass(frozen=True)
class ClaimBridge:
    input_value: float
    common_equity_value: float
    per_share_value: float | None
    calculation_trail: tuple[dict[str, float | str], ...]


def classify_declining_company(
    *,
    m3_boundary_cleared: bool,
    m4_boundary_cleared: bool,
    mature_boundary_cleared: bool,
    cycle_boundary_cleared: bool,
    multi_period_decline_evidence: bool,
    sector_evidence: bool,
) -> bool:
    """Apply the M5 life-cycle gate without using any single weak-period signal."""
    return all(
        (
            m3_boundary_cleared,
            m4_boundary_cleared,
            mature_boundary_cleared,
            cycle_boundary_cleared,
            multi_period_decline_evidence,
            sector_evidence,
        )
    )


def select_quadrant(reversibility: str, distress_level: str) -> str:
    """Return the one governed M5 quadrant selected by independent classifications."""
    mapping = {
        ("irreversible", "low"): "irreversible_low",
        ("reversible", "low"): "reversible_low",
        ("irreversible", "high"): "irreversible_high",
        ("reversible", "high"): "reversible_high",
    }
    try:
        return mapping[(reversibility, distress_level)]
    except KeyError as exc:
        raise ValueError("reversibility and distress_level must select one M5 quadrant") from exc


def build_decline_forecast(
    *,
    base_revenue: float,
    revenue_growth_rates: Sequence[float],
    operating_margins: Sequence[float],
    tax_rates: Sequence[float],
    reinvestments: Sequence[float],
    initial_invested_capital: float,
) -> DeclineForecast:
    """Build a declining FCFF path while permitting governed capital release."""
    revenue = _finite("base_revenue", base_revenue)
    growth = _series("revenue_growth_rates", revenue_growth_rates)
    margins = _series("operating_margins", operating_margins)
    taxes = _series("tax_rates", tax_rates)
    reinvestment = _series("reinvestments", reinvestments)
    _same_length(growth=growth, margins=margins, taxes=taxes, reinvestments=reinvestment)
    if revenue < 0 or any(rate <= -1 for rate in growth):
        raise ValueError("revenue must be non-negative and growth rates greater than -100%")
    if any(not 0 <= rate <= 1 for rate in taxes):
        raise ValueError("tax rates must be between zero and one")

    revenues: list[float] = []
    operating_incomes: list[float] = []
    cash_taxes: list[float] = []
    after_tax_incomes: list[float] = []
    capital_path: list[float] = []
    returns: list[float] = []
    fcff: list[float] = []
    opening_capital = _finite("initial_invested_capital", initial_invested_capital)
    if opening_capital <= 0:
        raise ValueError("initial invested capital must be positive")

    for index, (rate, margin, tax_rate, reinvested) in enumerate(
        zip(growth, margins, taxes, reinvestment), 1
    ):
        if opening_capital <= 0:
            raise ValueError(f"opening invested capital must remain positive in period {index}")
        revenue *= 1 + rate
        operating_income = revenue * margin
        cash_tax = max(0.0, operating_income) * tax_rate
        after_tax_income = operating_income - cash_tax
        closing_capital = opening_capital + reinvested
        if closing_capital < 0:
            raise ValueError(f"invested capital cannot be negative in period {index}")
        revenues.append(revenue)
        operating_incomes.append(operating_income)
        cash_taxes.append(cash_tax)
        after_tax_incomes.append(after_tax_income)
        returns.append(after_tax_income / opening_capital)
        capital_path.append(closing_capital)
        fcff.append(after_tax_income - reinvested)
        opening_capital = closing_capital

    return DeclineForecast(
        tuple(revenues),
        tuple(operating_incomes),
        tuple(cash_taxes),
        tuple(after_tax_incomes),
        tuple(capital_path),
        tuple(returns),
        tuple(fcff),
    )


def build_financing_path(
    *,
    initial_face_debt: float,
    debt_issuances: Sequence[float],
    debt_repayments: Sequence[float],
    cash_interest: Sequence[float],
    operating_incomes: Sequence[float],
    tax_rates: Sequence[float],
    market_value_debt: Sequence[float],
    market_value_equity: Sequence[float],
    pretax_costs_of_debt: Sequence[float],
    costs_of_equity: Sequence[float],
) -> FinancingPath:
    """Recompute face debt, loss-limited tax shields, market weights, and WACC."""
    issuances = _series("debt_issuances", debt_issuances)
    repayments = _series("debt_repayments", debt_repayments)
    interest = _series("cash_interest", cash_interest)
    operating = _series("operating_incomes", operating_incomes)
    taxes = _series("tax_rates", tax_rates)
    market_debt = _series("market_value_debt", market_value_debt)
    market_equity = _series("market_value_equity", market_value_equity)
    debt_costs = _series("pretax_costs_of_debt", pretax_costs_of_debt)
    equity_costs = _series("costs_of_equity", costs_of_equity)
    _same_length(
        debt_issuances=issuances,
        debt_repayments=repayments,
        cash_interest=interest,
        operating_incomes=operating,
        tax_rates=taxes,
        market_value_debt=market_debt,
        market_value_equity=market_equity,
        pretax_costs_of_debt=debt_costs,
        costs_of_equity=equity_costs,
    )
    if any(value < 0 for values in (issuances, repayments, interest, market_debt, market_equity) for value in values):
        raise ValueError("debt, interest, and market-value capital inputs must be non-negative")
    if any(not 0 <= rate <= 1 for rate in taxes):
        raise ValueError("tax rates must be between zero and one")
    if any(rate <= -1 for values in (debt_costs, equity_costs) for rate in values):
        raise ValueError("financing rates must be greater than -100%")

    opening = _finite("initial_face_debt", initial_face_debt)
    if opening < 0:
        raise ValueError("initial face debt must be non-negative")
    openings: list[float] = []
    closings: list[float] = []
    taxable: list[float] = []
    benefits: list[float] = []
    debt_weights: list[float] = []
    equity_weights: list[float] = []
    effective_rates: list[float] = []
    after_tax_debt_costs: list[float] = []
    capital_costs: list[float] = []
    for index, values in enumerate(
        zip(
            issuances,
            repayments,
            interest,
            operating,
            taxes,
            market_debt,
            market_equity,
            debt_costs,
            equity_costs,
        ),
        1,
    ):
        issuance, repayment, cash_interest_value, income, tax, debt, equity, debt_cost, equity_cost = values
        openings.append(opening)
        closing = opening + issuance - repayment
        if closing < 0:
            raise ValueError(f"closing face debt cannot be negative in period {index}")
        closings.append(closing)
        available_income = max(0.0, income)
        benefit = min(cash_interest_value, available_income) * tax
        effective_tax_rate = 0.0 if cash_interest_value == 0 else benefit / cash_interest_value
        after_tax_debt_cost = debt_cost * (1 - effective_tax_rate)
        capital_value = debt + equity
        if capital_value <= 0:
            raise ValueError(f"market-value capital must be positive in period {index}")
        debt_weight = debt / capital_value
        equity_weight = equity / capital_value
        cost_of_capital = equity_weight * equity_cost + debt_weight * after_tax_debt_cost
        taxable.append(available_income)
        benefits.append(benefit)
        debt_weights.append(debt_weight)
        equity_weights.append(equity_weight)
        effective_rates.append(effective_tax_rate)
        after_tax_debt_costs.append(after_tax_debt_cost)
        capital_costs.append(cost_of_capital)
        opening = closing

    return FinancingPath(
        tuple(openings),
        tuple(closings),
        tuple(taxable),
        tuple(benefits),
        tuple(debt_weights),
        tuple(equity_weights),
        tuple(effective_rates),
        tuple(after_tax_debt_costs),
        tuple(capital_costs),
    )


def build_closure_value(
    mode: str,
    *,
    final_revenue: float,
    terminal_growth_rate: float | None,
    terminal_operating_margin: float | None,
    terminal_tax_rate: float | None,
    terminal_return_on_capital: float | None,
    terminal_cost_of_capital: float | None,
    finite_life_proceeds: float | None,
) -> ClosureValue:
    """Build exactly one status-quo closure value without importing liquidation."""
    revenue = _finite("final_revenue", final_revenue)
    if mode == "finite_life":
        if finite_life_proceeds is None:
            raise ValueError("finite-life closure requires explicit closure proceeds")
        proceeds = _finite("finite_life_proceeds", finite_life_proceeds)
        if proceeds < 0:
            raise ValueError("finite-life closure proceeds must be non-negative")
        return ClosureValue(mode, 0.0, 0.0, 0.0, 0.0, proceeds)
    if mode not in {"stabilized_smaller_company", "negative_perpetuity"}:
        raise ValueError("closure mode is unsupported")
    if None in (
        terminal_growth_rate,
        terminal_operating_margin,
        terminal_tax_rate,
        terminal_return_on_capital,
        terminal_cost_of_capital,
    ):
        raise ValueError("perpetual closure requires all terminal operating inputs")
    growth = _finite("terminal_growth_rate", terminal_growth_rate)  # type: ignore[arg-type]
    margin = _finite("terminal_operating_margin", terminal_operating_margin)  # type: ignore[arg-type]
    tax = _finite("terminal_tax_rate", terminal_tax_rate)  # type: ignore[arg-type]
    return_on_capital = _finite(  # type: ignore[arg-type]
        "terminal_return_on_capital", terminal_return_on_capital
    )
    cost = _finite("terminal_cost_of_capital", terminal_cost_of_capital)  # type: ignore[arg-type]
    if not 0 <= tax <= 1 or return_on_capital <= 0 or growth <= -1 or growth >= cost:
        raise ValueError("terminal growth, tax, return, and cost inputs are inconsistent")
    if mode == "stabilized_smaller_company" and growth < 0:
        raise ValueError("stabilized-smaller-company growth cannot be negative")
    if mode == "negative_perpetuity" and growth >= 0:
        raise ValueError("negative-perpetuity growth must be negative")
    terminal_revenue = revenue * (1 + growth)
    terminal_after_tax_income = terminal_revenue * margin * (1 - tax)
    reinvestment_rate = growth / return_on_capital
    terminal_fcff = terminal_after_tax_income * (1 - reinvestment_rate)
    _, terminal_value = calculate_terminal_value(terminal_fcff / (1 + growth), growth, cost)
    return ClosureValue(
        mode,
        terminal_revenue,
        terminal_after_tax_income,
        reinvestment_rate,
        terminal_fcff,
        terminal_value,
    )


def run_going_concern_valuation(
    forecast: DeclineForecast,
    financing: FinancingPath,
    closure: ClosureValue,
) -> GoingConcernValue:
    """Discount conditional FCFF and one closure amount using M1 cumulative arithmetic."""
    _same_length(fcff=forecast.fcff, costs_of_capital=financing.costs_of_capital)
    discounted = discount_fcff(forecast.fcff, financing.costs_of_capital)
    closure_present_value = (
        closure.terminal_or_closure_value * discounted.cumulative_discount_factors[-1]
    )
    operating_value = discounted.present_value + closure_present_value
    trail: list[dict[str, float | int | str]] = []
    for period, (fcff, rate, factor, value) in enumerate(
        zip(
            forecast.fcff,
            financing.costs_of_capital,
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
                "value": value,
            }
        )
    trail.extend(
        (
            {
                "step": "terminal_or_closure_value",
                "mode": closure.mode,
                "value": closure.terminal_or_closure_value,
            },
            {
                "step": "terminal_or_closure_present_value",
                "cumulative_discount_factor": discounted.cumulative_discount_factors[-1],
                "value": closure_present_value,
            },
            {"step": "operating_asset_value", "value": operating_value},
        )
    )
    return GoingConcernValue(
        discounted.cumulative_discount_factors,
        discounted.discounted_cash_flows,
        discounted.present_value,
        closure_present_value,
        operating_value,
        tuple(trail),
    )


def net_divestiture_proceeds(
    gross_sale_proceeds: float, transaction_costs: float, taxes_on_sale: float
) -> float:
    gross = _finite("gross_sale_proceeds", gross_sale_proceeds)
    costs = _finite("transaction_costs", transaction_costs)
    taxes = _finite("taxes_on_sale", taxes_on_sale)
    if min(gross, costs, taxes) < 0 or costs + taxes > gross:
        raise ValueError("divestiture proceeds, costs, and taxes are inconsistent")
    return gross - costs - taxes


def value_orderly_liquidation(
    net_sale_proceeds: Sequence[float], discount_rates: Sequence[float]
) -> float:
    """Discount a non-urgent multi-period sale program without a terminal value."""
    proceeds = _series("net_sale_proceeds", net_sale_proceeds)
    if any(value < 0 for value in proceeds):
        raise ValueError("orderly-liquidation proceeds must be non-negative")
    return discount_fcff(proceeds, discount_rates).present_value


def turnaround_expected_value(
    status_quo_value: float, turnaround_value: float, probability_of_change: float
) -> tuple[float, float, float]:
    status = _finite("status_quo_value", status_quo_value)
    turnaround = _finite("turnaround_value", turnaround_value)
    probability = _finite("probability_of_change", probability_of_change)
    if not 0 <= probability <= 1:
        raise ValueError("probability_of_change must be between zero and one")
    status_component = status * (1 - probability)
    turnaround_component = turnaround * probability
    return status_component, turnaround_component, status_component + turnaround_component


def select_orderly_liquidation(
    status_quo_value: float, orderly_liquidation_value: float
) -> tuple[str, float]:
    status = _finite("status_quo_value", status_quo_value)
    liquidation = _finite("orderly_liquidation_value", orderly_liquidation_value)
    if liquidation > status:
        return "orderly_liquidation", liquidation
    return "status-quo", status


def estimate_distress_sale_value(
    method: str,
    *,
    reference_going_concern_asset_value: float | None = None,
    haircut: float | None = None,
    existing_asset_after_tax_income: float | None = None,
    existing_asset_cost_of_capital: float | None = None,
    eligible_book_assets: float | None = None,
    economic_impairment: float | None = None,
    forced_sale_discount: float | None = None,
    direct_sale_costs: float = 0.0,
    indirect_operating_costs: float = 0.0,
) -> DistressSaleValue:
    """Apply exactly one governed distress-sale method and expose all costs."""
    if method == "going_concern_haircut":
        if reference_going_concern_asset_value is None or haircut is None:
            raise ValueError("going-concern-haircut requires a reference value and haircut")
        reference = _finite(
            "reference_going_concern_asset_value", reference_going_concern_asset_value
        )
        haircut_value = _finite("haircut", haircut)
        if reference < 0 or not 0 <= haircut_value <= 1:
            raise ValueError("going-concern reference and haircut are invalid")
        gross = reference * (1 - haircut_value)
    elif method == "existing_asset_value":
        if existing_asset_after_tax_income is None or existing_asset_cost_of_capital is None:
            raise ValueError("existing-asset-value requires income and cost of capital")
        income = _finite("existing_asset_after_tax_income", existing_asset_after_tax_income)
        cost = _finite("existing_asset_cost_of_capital", existing_asset_cost_of_capital)
        if income < 0 or cost <= 0:
            raise ValueError("existing-asset income must be non-negative and cost positive")
        gross = income / cost
    elif method == "adjusted_book_assets":
        if None in (eligible_book_assets, economic_impairment, forced_sale_discount):
            raise ValueError("adjusted-book-assets requires book assets and both adjustments")
        book = _finite("eligible_book_assets", eligible_book_assets)  # type: ignore[arg-type]
        impairment = _finite("economic_impairment", economic_impairment)  # type: ignore[arg-type]
        sale_discount = _finite("forced_sale_discount", forced_sale_discount)  # type: ignore[arg-type]
        if book < 0 or not 0 <= impairment <= 1 or not 0 <= sale_discount <= 1:
            raise ValueError("adjusted-book asset inputs are invalid")
        gross = book * (1 - impairment) * (1 - sale_discount)
    else:
        raise ValueError("distress-sale method is unsupported")
    direct = _finite("direct_sale_costs", direct_sale_costs)
    indirect = _finite("indirect_operating_costs", indirect_operating_costs)
    if min(direct, indirect) < 0 or direct + indirect > gross:
        raise ValueError("distress-sale costs are inconsistent with gross recovery")
    return DistressSaleValue(method, gross, direct, indirect, gross - direct - indirect)


def contingent_survival_value(
    no_distress_value: float,
    distress_sale_value: float,
    *,
    survival_probability: float,
    distress_probability: float,
    distress_premium_in_discount_rates: bool = False,
    distress_loss_in_fcff: bool = False,
) -> ContingentValue:
    """Apply one M3-compatible separate distress adjustment on a common basis."""
    no_distress = _finite("no_distress_value", no_distress_value)
    distress_sale = _finite("distress_sale_value", distress_sale_value)
    survival = _finite("survival_probability", survival_probability)
    distress = _finite("distress_probability", distress_probability)
    if not 0 <= survival <= 1 or not 0 <= distress <= 1 or abs(survival + distress - 1) > 1e-10:
        raise ValueError("survival and distress probabilities must be bounded and sum to one")
    if distress_premium_in_discount_rates or distress_loss_in_fcff:
        raise ValueError("discrete distress is double counted outside the separate adjustment")
    survival_component = survival * no_distress
    distress_component = distress * distress_sale
    total = survival_component + distress_component
    trail = (
        {
            "step": "survival_component",
            "probability": survival,
            "scenario_value": no_distress,
            "value": survival_component,
        },
        {
            "step": "distress_component",
            "probability": distress,
            "scenario_value": distress_sale,
            "value": distress_component,
        },
        {"step": "contingent_value", "value": total},
    )
    return ContingentValue(
        survival, distress, survival_component, distress_component, total, trail
    )


def bridge_to_common_equity(
    input_value: float,
    *,
    cash: float,
    market_value_debt: float,
    senior_claims: float,
    hybrid_claims: float,
    option_claims: float,
    share_count: float | None,
    limited_liability_floor: bool,
) -> ClaimBridge:
    """Apply one dated, current-claim bridge after alternative aggregation."""
    value = _finite("input_value", input_value)
    cash_value = _finite("cash", cash)
    debt = _finite("market_value_debt", market_value_debt)
    senior = _finite("senior_claims", senior_claims)
    hybrid = _finite("hybrid_claims", hybrid_claims)
    options = _finite("option_claims", option_claims)
    if min(cash_value, debt, senior, hybrid, options) < 0:
        raise ValueError("claim-bridge inputs must be non-negative")
    raw_equity = value + cash_value - debt - senior - hybrid - options
    equity = max(0.0, raw_equity) if limited_liability_floor else raw_equity
    per_share = None
    normalized_shares = None
    if share_count is not None:
        normalized_shares = _finite("share_count", share_count)
        if normalized_shares <= 0:
            raise ValueError("share_count must be positive")
        per_share = equity / normalized_shares
    trail: list[dict[str, float | str]] = [
        {
            "step": "claim_bridge",
            "input_value": value,
            "cash": cash_value,
            "market_value_debt": debt,
            "senior_claims": senior,
            "hybrid_claims": hybrid,
            "option_claims": options,
            "value": equity,
        }
    ]
    if per_share is not None:
        trail.append(
            {
                "step": "per_share_value",
                "share_count": normalized_shares or 0.0,
                "value": per_share,
            }
        )
    return ClaimBridge(value, equity, per_share, tuple(trail))
