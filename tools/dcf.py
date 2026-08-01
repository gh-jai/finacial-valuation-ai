"""Dependency-free FCFF discounted cash-flow calculations for FVI benchmarks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Any, Mapping, Sequence


RateInput = float | Sequence[float]


@dataclass(frozen=True)
class DiscountedCashFlows:
    discount_rates: tuple[float, ...]
    cumulative_discount_factors: tuple[float, ...]
    discounted_cash_flows: tuple[float, ...]
    present_value: float


@dataclass(frozen=True)
class DCFResult:
    cash_flows: tuple[float, ...]
    discount_rates: tuple[float, ...]
    cumulative_discount_factors: tuple[float, ...]
    discounted_cash_flows: tuple[float, ...]
    forecast_present_value: float
    terminal_discount_rate: float
    terminal_growth_rate: float
    terminal_cash_flow: float
    terminal_value: float
    terminal_present_value: float
    operating_asset_value: float
    cash_and_non_operating_assets: float
    debt_and_debt_like_claims: float
    equity_value: float | None
    share_count: float | None
    per_share_value: float | None
    calculation_trail: tuple[dict[str, float | int | str], ...]

    @property
    def enterprise_value(self) -> float:
        """Compatibility alias for operating-asset value."""
        return self.operating_asset_value


def _finite_float(name: str, value: float) -> float:
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric and finite") from exc
    if not isfinite(normalized):
        raise ValueError(f"{name} must be finite")
    return normalized


def _finite_sequence(name: str, values: Sequence[float]) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)) or not values:
        raise ValueError(f"{name} must contain at least one value")
    return tuple(_finite_float(f"{name}[{index}]", value) for index, value in enumerate(values, 1))


def _normalize_discount_rates(discount_rate: RateInput, periods: int) -> tuple[float, ...]:
    if isinstance(discount_rate, Sequence) and not isinstance(discount_rate, (str, bytes)):
        rates = _finite_sequence("discount_rate", discount_rate)
        if len(rates) != periods:
            raise ValueError("period-specific discount_rate must match the cash-flow count")
    else:
        rate = _finite_float("discount_rate", discount_rate)  # type: ignore[arg-type]
        rates = (rate,) * periods
    for index, rate in enumerate(rates, 1):
        if rate <= -1.0:
            raise ValueError(f"discount_rate[{index}] must be greater than -100%")
    return rates


def validate_dcf_inputs(
    cash_flows: Sequence[float],
    discount_rate: RateInput,
    terminal_growth_rate: float,
    terminal_discount_rate: float | None = None,
) -> tuple[tuple[float, ...], tuple[float, ...], float, float]:
    """Normalize and validate the core FCFF DCF inputs."""
    normalized_cash_flows = _finite_sequence("cash_flows", cash_flows)
    discount_rates = _normalize_discount_rates(discount_rate, len(normalized_cash_flows))
    growth = _finite_float("terminal_growth_rate", terminal_growth_rate)
    terminal_rate = (
        discount_rates[-1]
        if terminal_discount_rate is None
        else _finite_float("terminal_discount_rate", terminal_discount_rate)
    )
    if terminal_rate <= -1.0:
        raise ValueError("terminal_discount_rate must be greater than -100%")
    if growth >= terminal_rate:
        raise ValueError("terminal_growth_rate must be below terminal_discount_rate")
    return normalized_cash_flows, discount_rates, terminal_rate, growth


def forecast_fcff(
    revenues: Sequence[float],
    operating_margins: Sequence[float],
    tax_rates: Sequence[float],
    reinvestments: Sequence[float],
) -> tuple[float, ...]:
    """Forecast FCFF from explicit operating drivers."""
    revenue_values = _finite_sequence("revenues", revenues)
    margins = _finite_sequence("operating_margins", operating_margins)
    taxes = _finite_sequence("tax_rates", tax_rates)
    reinvestment_values = _finite_sequence("reinvestments", reinvestments)
    lengths = {len(revenue_values), len(margins), len(taxes), len(reinvestment_values)}
    if len(lengths) != 1:
        raise ValueError("FCFF driver sequences must have the same number of periods")
    if any(revenue < 0.0 for revenue in revenue_values):
        raise ValueError("revenues must be non-negative")
    if any(tax < 0.0 or tax > 1.0 for tax in taxes):
        raise ValueError("tax_rates must be between 0 and 1")
    result = tuple(
        revenue * margin * (1.0 - tax) - reinvestment
        for revenue, margin, tax, reinvestment in zip(
            revenue_values, margins, taxes, reinvestment_values
        )
    )
    for index, value in enumerate(result, 1):
        _finite_float(f"forecast_fcff[{index}]", value)
    return result


def estimate_sustainable_growth(reinvestment_rate: float, return_on_capital: float) -> float:
    """Estimate sustainable operating growth as reinvestment rate times return on capital."""
    reinvestment = _finite_float("reinvestment_rate", reinvestment_rate)
    return_value = _finite_float("return_on_capital", return_on_capital)
    growth = reinvestment * return_value
    return _finite_float("sustainable_growth", growth)


def calculate_terminal_value(
    final_fcff: float,
    terminal_growth_rate: float,
    terminal_discount_rate: float,
) -> tuple[float, float]:
    """Return next-period FCFF and Gordon-growth terminal value."""
    final_cash_flow = _finite_float("final_fcff", final_fcff)
    growth = _finite_float("terminal_growth_rate", terminal_growth_rate)
    rate = _finite_float("terminal_discount_rate", terminal_discount_rate)
    if rate <= -1.0:
        raise ValueError("terminal_discount_rate must be greater than -100%")
    if growth >= rate:
        raise ValueError("terminal_growth_rate must be below terminal_discount_rate")
    terminal_cash_flow = final_cash_flow * (1.0 + growth)
    terminal_value = terminal_cash_flow / (rate - growth)
    return (
        _finite_float("terminal_cash_flow", terminal_cash_flow),
        _finite_float("terminal_value", terminal_value),
    )


def discount_fcff(cash_flows: Sequence[float], discount_rate: RateInput) -> DiscountedCashFlows:
    """Discount explicit FCFF using cumulative period-specific discount factors."""
    normalized = _finite_sequence("cash_flows", cash_flows)
    rates = _normalize_discount_rates(discount_rate, len(normalized))
    cumulative_denominator = 1.0
    factors: list[float] = []
    discounted: list[float] = []
    for index, (cash_flow, rate) in enumerate(zip(normalized, rates), 1):
        cumulative_denominator *= 1.0 + rate
        _finite_float(f"cumulative_discount_denominator[{index}]", cumulative_denominator)
        factor = _finite_float(
            f"cumulative_discount_factor[{index}]", 1.0 / cumulative_denominator
        )
        factors.append(factor)
        discounted.append(_finite_float(f"discounted_cash_flow[{index}]", cash_flow * factor))
    present_value = _finite_float("forecast_present_value", sum(discounted))
    return DiscountedCashFlows(rates, tuple(factors), tuple(discounted), present_value)


def bridge_enterprise_to_equity(
    operating_asset_value: float,
    cash_and_non_operating_assets: float,
    debt_and_debt_like_claims: float,
) -> float:
    """Bridge operating-asset value to common-equity value."""
    operating_value = _finite_float("operating_asset_value", operating_asset_value)
    cash = _finite_float("cash_and_non_operating_assets", cash_and_non_operating_assets)
    debt = _finite_float("debt_and_debt_like_claims", debt_and_debt_like_claims)
    return _finite_float("equity_value", operating_value + cash - debt)


def calculate_per_share_value(equity_value: float, share_count: float) -> float:
    """Convert common-equity value to value per share."""
    equity = _finite_float("equity_value", equity_value)
    shares = _finite_float("share_count", share_count)
    if shares <= 0.0:
        raise ValueError("share_count must be positive")
    return _finite_float("per_share_value", equity / shares)


def run_fcff_dcf(
    cash_flows: Sequence[float],
    discount_rate: RateInput,
    terminal_growth_rate: float,
    *,
    terminal_discount_rate: float | None = None,
    cash_and_non_operating_assets: float = 0.0,
    debt_and_debt_like_claims: float = 0.0,
    share_count: float | None = None,
) -> DCFResult:
    """Run an end-of-period FCFF DCF with an optional equity and per-share bridge."""
    normalized, rates, terminal_rate, growth = validate_dcf_inputs(
        cash_flows, discount_rate, terminal_growth_rate, terminal_discount_rate
    )
    discounted = discount_fcff(normalized, rates)
    terminal_cash_flow, terminal_value = calculate_terminal_value(
        normalized[-1], growth, terminal_rate
    )
    terminal_present_value = _finite_float(
        "terminal_present_value", terminal_value * discounted.cumulative_discount_factors[-1]
    )
    operating_asset_value = _finite_float(
        "operating_asset_value", discounted.present_value + terminal_present_value
    )
    cash = _finite_float("cash_and_non_operating_assets", cash_and_non_operating_assets)
    debt = _finite_float("debt_and_debt_like_claims", debt_and_debt_like_claims)

    bridge_requested = cash != 0.0 or debt != 0.0 or share_count is not None
    equity_value = None
    normalized_share_count = None
    per_share_value = None
    if bridge_requested:
        equity_value = bridge_enterprise_to_equity(operating_asset_value, cash, debt)
        if share_count is not None:
            normalized_share_count = _finite_float("share_count", share_count)
            per_share_value = calculate_per_share_value(equity_value, normalized_share_count)

    trail: list[dict[str, float | int | str]] = []
    for period, (fcff, rate, factor, present_value) in enumerate(
        zip(
            normalized,
            discounted.discount_rates,
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
        [
            {"step": "terminal_value", "value": terminal_value},
            {
                "step": "terminal_present_value",
                "cumulative_discount_factor": discounted.cumulative_discount_factors[-1],
                "value": terminal_present_value,
            },
            {"step": "operating_asset_value", "value": operating_asset_value},
        ]
    )
    if equity_value is not None:
        trail.append(
            {
                "step": "enterprise_to_equity_bridge",
                "cash_and_non_operating_assets": cash,
                "debt_and_debt_like_claims": debt,
                "value": equity_value,
            }
        )
    if per_share_value is not None:
        trail.append(
            {
                "step": "per_share_value",
                "share_count": normalized_share_count or 0.0,
                "value": per_share_value,
            }
        )

    return DCFResult(
        cash_flows=normalized,
        discount_rates=discounted.discount_rates,
        cumulative_discount_factors=discounted.cumulative_discount_factors,
        discounted_cash_flows=discounted.discounted_cash_flows,
        forecast_present_value=discounted.present_value,
        terminal_discount_rate=terminal_rate,
        terminal_growth_rate=growth,
        terminal_cash_flow=terminal_cash_flow,
        terminal_value=terminal_value,
        terminal_present_value=terminal_present_value,
        operating_asset_value=operating_asset_value,
        cash_and_non_operating_assets=cash,
        debt_and_debt_like_claims=debt,
        equity_value=equity_value,
        share_count=normalized_share_count,
        per_share_value=per_share_value,
        calculation_trail=tuple(trail),
    )


def run_dcf_sensitivity(
    cash_flows: Sequence[float],
    discount_rate: RateInput,
    terminal_discount_rates: Sequence[float],
    terminal_growth_rates: Sequence[float],
) -> tuple[dict[str, float | str], ...]:
    """Run a deterministic terminal-rate/growth sensitivity grid."""
    terminal_rates = _finite_sequence("terminal_discount_rates", terminal_discount_rates)
    growth_rates = _finite_sequence("terminal_growth_rates", terminal_growth_rates)
    points: list[dict[str, float | str]] = []
    for terminal_rate in terminal_rates:
        for growth in growth_rates:
            result = run_fcff_dcf(
                cash_flows,
                discount_rate,
                growth,
                terminal_discount_rate=terminal_rate,
            )
            points.append(
                {
                    "scenario": f"terminal-rate={terminal_rate:.6f},growth={growth:.6f}",
                    "terminal_discount_rate": terminal_rate,
                    "terminal_growth_rate": growth,
                    "point_estimate": result.operating_asset_value,
                }
            )
    return tuple(points)


def _require_json_finite(value: Any, path: str = "output") -> None:
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{path} must not contain non-finite numbers")
    if isinstance(value, Mapping):
        for key, item in value.items():
            _require_json_finite(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _require_json_finite(item, f"{path}[{index}]")


def to_valuation_output(
    result: DCFResult,
    *,
    as_of_date: str,
    subject: str,
    currency: str,
    evidence_refs: Sequence[str],
    limitations: Sequence[str],
    sensitivity: Sequence[Mapping[str, Any]] = (),
    review_status: str = "unreviewed",
    reviewer: str | None = None,
    reviewed_at: str | None = None,
) -> dict[str, Any]:
    """Convert a completed DCF result to the FVI valuation-output contract."""
    try:
        date.fromisoformat(as_of_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("as_of_date must be an ISO YYYY-MM-DD date") from exc
    if not subject.strip():
        raise ValueError("subject must not be empty")
    if len(currency) != 3 or not currency.isalpha() or currency != currency.upper():
        raise ValueError("currency must be a three-letter uppercase code")
    normalized_evidence = list(dict.fromkeys(evidence_refs))
    if not normalized_evidence or any(not item.strip() for item in normalized_evidence):
        raise ValueError("evidence_refs must contain at least one non-empty reference")
    normalized_limitations = list(limitations)
    if not normalized_limitations or any(not item.strip() for item in normalized_limitations):
        raise ValueError("limitations must contain at least one non-empty statement")
    if review_status not in {"unreviewed", "reviewed", "approved", "rejected"}:
        raise ValueError("review_status is not supported")

    if result.per_share_value is not None:
        basis = "per-share"
        point_estimate = result.per_share_value
    elif result.equity_value is not None:
        basis = "equity"
        point_estimate = result.equity_value
    else:
        basis = "enterprise"
        point_estimate = result.operating_asset_value

    assumptions: list[dict[str, Any]] = [
            {
                "name": "explicit_fcff",
                "value": list(result.cash_flows),
                "unit": currency,
                "rationale": "Synthetic or authorized explicit FCFF sequence supplied to the model.",
                "source_refs": normalized_evidence,
            },
            {
                "name": "discount_rates",
                "value": list(result.discount_rates),
                "unit": "decimal",
                "rationale": "Period-specific cost-of-capital assumptions matched to FCFF.",
                "source_refs": normalized_evidence,
            },
            {
                "name": "terminal_discount_rate",
                "value": result.terminal_discount_rate,
                "unit": "decimal",
                "rationale": "Stable-state cost of capital used in the Gordon-growth denominator.",
                "source_refs": normalized_evidence,
            },
            {
                "name": "terminal_growth_rate",
                "value": result.terminal_growth_rate,
                "unit": "decimal",
                "rationale": "Stable growth assumption constrained below the terminal discount rate.",
                "source_refs": normalized_evidence,
            },
        ]
    if result.equity_value is not None:
        assumptions.extend(
            [
                {
                    "name": "cash_and_non_operating_assets",
                    "value": result.cash_and_non_operating_assets,
                    "unit": currency,
                    "rationale": "Eligible assets excluded from operating FCFF and added in the equity bridge.",
                    "source_refs": normalized_evidence,
                },
                {
                    "name": "debt_and_debt_like_claims",
                    "value": result.debt_and_debt_like_claims,
                    "unit": currency,
                    "rationale": "Non-equity claims subtracted after valuing operating assets.",
                    "source_refs": normalized_evidence,
                },
            ]
        )
    if result.share_count is not None:
        assumptions.append(
            {
                "name": "share_count",
                "value": result.share_count,
                "unit": "shares",
                "rationale": "Positive common-share denominator used after the equity bridge.",
                "source_refs": normalized_evidence,
            }
        )

    output: dict[str, Any] = {
        "schema_version": "1.1.0",
        "as_of_date": as_of_date,
        "subject": subject,
        "currency": currency,
        "method": "dcf",
        "value": {"basis": basis, "point_estimate": point_estimate},
        "assumptions": assumptions,
        "evidence_refs": normalized_evidence,
        "limitations": normalized_limitations,
        "sensitivity": [dict(point) for point in sensitivity],
        "review": {
            "status": review_status,
            "reviewer": reviewer,
            "reviewed_at": reviewed_at,
        },
        "calculation_trail": [dict(step) for step in result.calculation_trail],
    }
    _require_json_finite(output)
    return output
