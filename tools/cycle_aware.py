"""Deterministic calculations for the M6 cycle-aware judgment layer."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from math import isfinite
from typing import Any


MARKET_BANDS = (
    "extreme_low",
    "below_midpoint",
    "midpoint",
    "above_midpoint",
    "extreme_high",
)


def _finite(name: str, value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric and finite") from exc
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _clean(value: float) -> float:
    return round(value, 12)


def classify_cycle_subject(
    *,
    exposure_type: str,
    external_driver: str,
    linked_financial_series: Sequence[str],
    observation_years: int,
    has_strong_and_weak_conditions: bool,
    lifecycle_boundaries_cleared: bool,
) -> bool:
    """Require company-specific exposure, history, and cleared life-cycle boundaries."""
    return all(
        (
            exposure_type in {"economic_cycle", "commodity_price", "mixed_cycle"},
            bool(str(external_driver).strip()),
            bool(linked_financial_series),
            observation_years >= 2,
            has_strong_and_weak_conditions,
            lifecycle_boundaries_cleared,
        )
    )


def normalize_input(
    method: str,
    observations: Sequence[float],
    *,
    current_scale: float | None = None,
    company_adjustment: float | None = None,
    driver_sensitivity: float | None = None,
    intercept: float | None = None,
) -> float:
    """Calculate one governed normalized input from its declared method."""
    if not observations:
        raise ValueError("normalization observations must not be empty")
    values = [_finite("normalization observation", value) for value in observations]
    average = sum(values) / len(values)
    if method == "absolute_historical_average":
        result = average
    elif method == "relative_historical_average":
        if current_scale is None:
            raise ValueError("relative normalization requires current_scale")
        result = average * _finite("current_scale", current_scale)
    elif method == "sector_average_with_adjustment":
        if company_adjustment is None:
            raise ValueError("sector normalization requires company_adjustment")
        result = average + _finite("company_adjustment", company_adjustment)
    elif method == "normalized_external_driver":
        if driver_sensitivity is None or intercept is None:
            raise ValueError("external-driver normalization requires sensitivity and intercept")
        result = average * _finite("driver_sensitivity", driver_sensitivity) + _finite(
            "intercept", intercept
        )
    else:
        raise ValueError("unsupported normalization method")
    return _clean(result)


def build_transition_path(
    current: Mapping[str, float],
    normalized_anchor: Mapping[str, float],
    periods: int,
    tax_rate: float,
) -> list[dict[str, float | int]]:
    """Linearly converge once from the reconciled current state to one normal anchor."""
    if not isinstance(periods, int) or periods < 1:
        raise ValueError("transition periods must be a positive integer")
    tax = _finite("tax_rate", tax_rate)
    if not 0 <= tax <= 1:
        raise ValueError("tax_rate must be between zero and one")
    fields = (
        "driver",
        "revenue",
        "operating_margin",
        "reinvestment",
        "invested_capital",
        "leverage",
        "financing_cost",
    )
    if set(current) != set(fields) or set(normalized_anchor) != set(fields):
        raise ValueError("transition input sets must contain the complete governed vector")
    start = {name: _finite(f"current {name}", current[name]) for name in fields}
    end = {name: _finite(f"normalized {name}", normalized_anchor[name]) for name in fields}
    result: list[dict[str, float | int]] = []
    for period in range(periods + 1):
        weight = period / periods
        row = {name: _clean(start[name] + (end[name] - start[name]) * weight) for name in fields}
        operating_income = row["revenue"] * row["operating_margin"]
        after_tax = operating_income * (1 - tax)
        if row["invested_capital"] <= 0:
            raise ValueError("transition invested capital must remain positive")
        result.append(
            {
                "period": period,
                **row,
                "operating_income": _clean(operating_income),
                "after_tax_operating_income": _clean(after_tax),
                "return_on_capital": _clean(after_tax / row["invested_capital"]),
            }
        )
    return result


def build_current_expectations_scenario(
    *,
    driver_values: Sequence[float],
    volumes: Sequence[float],
    fixed_costs: Sequence[float],
    unit_costs: Sequence[float],
    base_reinvestments: Sequence[float],
    reinvestment_sensitivity: float,
    base_driver: float,
    initial_invested_capital: float,
    tax_rate: float,
    base_financing_cost: float,
    funding_sensitivity: float,
) -> list[dict[str, float | int]]:
    """Map a dated driver path into a complete, isolated operating and financing path."""
    lengths = {
        len(driver_values),
        len(volumes),
        len(fixed_costs),
        len(unit_costs),
        len(base_reinvestments),
    }
    if len(lengths) != 1 or not driver_values:
        raise ValueError("scenario series must have equal non-zero length")
    tax = _finite("tax_rate", tax_rate)
    if not 0 <= tax <= 1:
        raise ValueError("tax_rate must be between zero and one")
    sensitivity = _finite("reinvestment_sensitivity", reinvestment_sensitivity)
    driver_base = _finite("base_driver", base_driver)
    capital = _finite("initial_invested_capital", initial_invested_capital)
    financing_base = _finite("base_financing_cost", base_financing_cost)
    funding = _finite("funding_sensitivity", funding_sensitivity)
    if capital <= 0:
        raise ValueError("initial invested capital must be positive")
    result: list[dict[str, float | int]] = []
    for period, values in enumerate(
        zip(driver_values, volumes, fixed_costs, unit_costs, base_reinvestments), 1
    ):
        driver, volume, fixed_cost, unit_cost, base_reinvestment = (
            _finite("scenario input", item) for item in values
        )
        revenue = driver * volume
        operating_cost = fixed_cost + unit_cost * volume
        operating_income = revenue - operating_cost
        margin = operating_income / revenue if revenue else 0.0
        after_tax = operating_income - max(0.0, operating_income) * tax
        reinvestment = base_reinvestment + sensitivity * (driver - driver_base)
        opening_capital = capital
        capital += reinvestment
        if capital <= 0:
            raise ValueError("scenario invested capital must remain positive")
        financing_cost = financing_base + funding * (driver - driver_base)
        result.append(
            {
                "period": period,
                "driver": _clean(driver),
                "volume": _clean(volume),
                "revenue": _clean(revenue),
                "operating_cost": _clean(operating_cost),
                "operating_margin": _clean(margin),
                "operating_income": _clean(operating_income),
                "after_tax_operating_income": _clean(after_tax),
                "reinvestment": _clean(reinvestment),
                "invested_capital": _clean(capital),
                "return_on_capital": _clean(after_tax / opening_capital),
                "financing_cost": _clean(financing_cost),
            }
        )
    return result


def evidence_is_stale(valuation_date: date, as_of_date: date, max_age_days: int) -> bool:
    """Apply the disclosed point-evidence staleness policy."""
    if as_of_date > valuation_date:
        raise ValueError("evidence date cannot be after valuation date")
    if max_age_days < 0:
        raise ValueError("max_age_days must be non-negative")
    return (valuation_date - as_of_date).days > max_age_days


def _aligned(selected_band: str, implication: str) -> bool:
    if selected_band not in MARKET_BANDS or implication not in MARKET_BANDS:
        return False
    return abs(MARKET_BANDS.index(selected_band) - MARKET_BANDS.index(implication)) <= 1


def alignment_count(selected_band: str, dimensions: Sequence[Mapping[str, Any]]) -> int:
    """Recompute usable alignment without converting categories to a composite score."""
    count = 0
    for item in dimensions:
        if item.get("availability") != "available":
            continue
        if item.get("stale_evidence_refs"):
            continue
        if item.get("unresolved_strong_contradiction"):
            continue
        if _aligned(selected_band, str(item.get("band_implication"))):
            count += 1
    return count


def derive_confidence(selected_band: str, dimensions: Sequence[Mapping[str, Any]]) -> str:
    """Apply the contract's categorical confidence thresholds."""
    available = [item for item in dimensions if item.get("availability") == "available"]
    non_stale = [item for item in available if not item.get("stale_evidence_refs")]
    aligned = alignment_count(selected_band, dimensions)
    unresolved = any(item.get("unresolved_strong_contradiction") for item in dimensions)
    if len(available) == 5 and aligned >= 4 and not unresolved:
        return "high"
    if len(non_stale) >= 3 and aligned >= 3 and not unresolved:
        return "medium"
    return "low"


def derive_review_posture(market_cycle_position: str) -> str:
    """Map the market band to its bounded human-review posture."""
    if market_cycle_position == "extreme_high":
        return "defensive_review"
    if market_cycle_position == "extreme_low":
        return "opportunity_review"
    if market_cycle_position in {"below_midpoint", "midpoint", "above_midpoint"}:
        return "balanced_review"
    if market_cycle_position == "indeterminate":
        return "insufficient_evidence"
    raise ValueError("unsupported market cycle position")


def probability_weighted_value(
    values: Sequence[float],
    probabilities: Sequence[float],
    *,
    event_definitions: Sequence[str],
    horizons: Sequence[str],
    as_of_dates: Sequence[date],
) -> float:
    """Weight complete scenarios only when one reviewed probability basis reconciles."""
    lengths = {
        len(values),
        len(probabilities),
        len(event_definitions),
        len(horizons),
        len(as_of_dates),
    }
    if len(lengths) != 1 or not values:
        raise ValueError("probability inputs must have equal non-zero length")
    weights = [_finite("probability", value) for value in probabilities]
    if any(value < 0 or value > 1 for value in weights) or abs(sum(weights) - 1) > 1e-9:
        raise ValueError("scenario probabilities must sum to one")
    if len(set(event_definitions)) != 1 or len(set(horizons)) != 1 or len(set(as_of_dates)) != 1:
        raise ValueError("scenario probabilities require one event, horizon, and as-of date")
    return _clean(sum(_finite("scenario value", value) * weight for value, weight in zip(values, weights)))
