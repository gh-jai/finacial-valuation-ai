"""Validate M4 growth-company artifacts and independently recompute every numeric series."""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from itertools import pairwise
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "benchmarks" / "fixtures" / "growth_company"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.growth_company import (
    apply_failure_handoff,
    build_growth_forecast,
    classify_growth_company,
    margin_convergence_path,
    run_growth_company_valuation,
)


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _close(actual: Any, expected: float, tolerance: float = 1e-8) -> bool:
    return _finite_number(actual) and abs(float(actual) - expected) <= tolerance


def _series_close(actual: Any, expected: Sequence[float], tolerance: float = 1e-8) -> bool:
    return (
        isinstance(actual, list)
        and len(actual) == len(expected)
        and all(_close(value, target, tolerance) for value, target in zip(actual, expected))
    )


def _append_series_error(
    errors: list[str], name: str, actual: Any, expected: Sequence[float], tolerance: float = 1e-8
) -> None:
    if not _series_close(actual, expected, tolerance):
        errors.append(f"stored {name} is inconsistent with recomputed values")


def _trail_close(actual: Any, expected: Sequence[Mapping[str, Any]]) -> bool:
    if not isinstance(actual, list) or len(actual) != len(expected):
        return False
    for actual_step, expected_step in zip(actual, expected):
        if not isinstance(actual_step, Mapping) or set(actual_step) != set(expected_step):
            return False
        for key, expected_value in expected_step.items():
            actual_value = actual_step[key]
            if _finite_number(expected_value):
                if not _close(actual_value, float(expected_value), 1e-10):
                    return False
            elif actual_value != expected_value:
                return False
    return True


def _bisect_break_even(
    function: Callable[[float], float], target: float, low: float, high: float
) -> float:
    low_delta = function(low) - target
    high_delta = function(high) - target
    if low_delta == 0:
        return low
    if high_delta == 0:
        return high
    if low_delta * high_delta > 0:
        raise ValueError("break-even target is not bracketed by the supported driver range")
    for _ in range(100):
        midpoint = (low + high) / 2
        midpoint_delta = function(midpoint) - target
        if abs(midpoint_delta) <= 1e-10:
            return midpoint
        if low_delta * midpoint_delta <= 0:
            high = midpoint
        else:
            low = midpoint
            low_delta = midpoint_delta
    return (low + high) / 2


def validate_document(
    document: Mapping[str, Any],
    schema: Mapping[str, Any],
    source_ids: set[str],
    claim_ids: set[str],
    narrative_assertions: set[str],
) -> list[str]:
    errors = [
        f"schema {'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
        for error in sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: list(item.path),
        )
    ]
    profile = document.get("growth_company_profile", {})
    base = document.get("base_period", {})
    forecast = document.get("forecast", {})
    stable = document.get("stable_state", {})
    going = document.get("going_concern", {})
    trace = document.get("traceability", {})

    if not classify_growth_company(
        m3_boundary_cleared=bool(profile.get("m3_boundary_cleared")),
        demonstrated_commercial_product=bool(profile.get("commercial_evidence_refs")),
        meaningful_operating_evidence=bool(base.get("evidence_refs")),
        material_growth_asset_value=bool(profile.get("growth_asset_reasoning")),
    ):
        errors.append("subject does not clear the M3-to-M4 growth-company boundary")

    try:
        period_end = date.fromisoformat(str(base.get("period_end")))
        base_as_of = date.fromisoformat(str(base.get("as_of_date")))
        document_as_of = date.fromisoformat(str(document.get("as_of_date")))
    except ValueError:
        errors.append("base-period dates cannot be reconciled")
    else:
        expected_staleness = (base_as_of - period_end).days
        if base_as_of != document_as_of or base.get("staleness_days") != expected_staleness:
            errors.append("base-period staleness is inconsistent with the valuation date")
        if expected_staleness > 90 and not base.get("normalization_adjustments"):
            errors.append("stale base period requires documented normalization adjustments")

    years = forecast.get("years", [])
    series_names = (
        "revenue_growth_rates",
        "revenues",
        "absolute_revenue_changes",
        "operating_margins",
        "operating_incomes",
        "tax_rates",
        "cash_taxes",
        "nol_balances",
        "after_tax_operating_incomes",
        "reinvestment_method",
        "sales_to_capital_ratios",
        "fundamental_reinvestment_rates",
        "capacity_reinvestments",
        "reinvestments",
        "invested_capital",
        "implied_returns_on_capital",
        "discount_rates",
    )
    if not years or years != list(range(1, len(years) + 1)):
        errors.append("forecast years must be consecutive and start at one")
    for name in series_names:
        if len(forecast.get(name, [])) != len(years):
            errors.append(f"forecast {name} length must match years")

    convergence = forecast.get("margin_convergence", {})
    try:
        expected_margins = margin_convergence_path(
            convergence.get("current_margin"),
            convergence.get("target_margin"),
            len(years),
            start_year=convergence.get("start_year"),
            end_year=convergence.get("end_year"),
        )
    except (TypeError, ValueError) as exc:
        errors.append(f"margin convergence cannot be recomputed: {exc}")
    else:
        _append_series_error(
            errors, "operating margins", forecast.get("operating_margins"), expected_margins
        )
        if not _close(stable.get("operating_margin"), expected_margins[-1]):
            errors.append("margin convergence does not end at the stable-state margin")

    try:
        recalculated = build_growth_forecast(
            base_revenue=base.get("revenues"),
            revenue_growth_rates=forecast.get("revenue_growth_rates", []),
            operating_margins=forecast.get("operating_margins", []),
            marginal_tax_rate=forecast.get("marginal_tax_rate"),
            initial_nol=base.get("net_operating_loss"),
            initial_invested_capital=base.get("invested_capital"),
            reinvestment_methods=forecast.get("reinvestment_method", []),
            sales_to_capital_ratios=forecast.get("sales_to_capital_ratios", []),
            fundamental_reinvestment_rates=forecast.get("fundamental_reinvestment_rates", []),
            capacity_reinvestments=forecast.get("capacity_reinvestments", []),
        )
    except (TypeError, ValueError) as exc:
        errors.append(f"growth-company forecast cannot be recomputed: {exc}")
        recalculated = None
    valuation = None
    if recalculated is not None:
        pairs = (
            ("revenues", recalculated.revenues),
            ("absolute revenue changes", recalculated.absolute_revenue_changes),
            ("operating incomes", recalculated.operating_incomes),
            ("tax rates", recalculated.tax_rates),
            ("cash taxes", recalculated.cash_taxes),
            ("NOL balances", recalculated.nol_balances),
            ("after-tax operating incomes", recalculated.after_tax_operating_incomes),
            ("reinvestments", recalculated.reinvestments),
            ("invested capital", recalculated.invested_capital),
            ("implied returns on capital", recalculated.implied_returns_on_capital),
        )
        keys = (
            "revenues",
            "absolute_revenue_changes",
            "operating_incomes",
            "tax_rates",
            "cash_taxes",
            "nol_balances",
            "after_tax_operating_incomes",
            "reinvestments",
            "invested_capital",
            "implied_returns_on_capital",
        )
        for (label, expected), key in zip(pairs, keys):
            _append_series_error(errors, label, forecast.get(key), expected)

        try:
            valuation = run_growth_company_valuation(
                recalculated,
                forecast.get("discount_rates", []),
                stable_growth_rate=stable.get("growth_rate"),
                stable_operating_margin=stable.get("operating_margin"),
                stable_tax_rate=stable.get("tax_rate"),
                stable_return_on_capital=stable.get("return_on_capital"),
                stable_cost_of_capital=stable.get("cost_of_capital"),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"going-concern valuation cannot be recomputed: {exc}")
            valuation = None
        if valuation is not None:
            _append_series_error(errors, "FCFF", going.get("fcff"), recalculated.fcff)
            _append_series_error(
                errors,
                "cumulative discount factors",
                going.get("cumulative_discount_factors"),
                valuation.cumulative_discount_factors,
                1e-10,
            )
            scalar_checks = (
                (
                    "forecast present value",
                    going.get("forecast_present_value"),
                    valuation.forecast_present_value,
                ),
                ("terminal FCFF", going.get("terminal_fcff"), valuation.terminal.terminal_fcff),
                ("terminal value", going.get("terminal_value"), valuation.terminal.terminal_value),
                (
                    "terminal present value",
                    going.get("terminal_present_value"),
                    valuation.terminal_present_value,
                ),
                (
                    "operating asset value",
                    going.get("operating_asset_value"),
                    valuation.operating_asset_value,
                ),
                (
                    "terminal-value share",
                    going.get("terminal_value_share"),
                    valuation.terminal_value_share,
                ),
            )
            for label, actual, expected in scalar_checks:
                if not _close(actual, expected):
                    errors.append(f"stored {label} is inconsistent with recomputed value")
            if not _trail_close(going.get("calculation_trail"), valuation.calculation_trail):
                errors.append("stored calculation trail is inconsistent with recomputed steps")

    if len(years) > 10:
        errors.append("forecast longer than ten years requires an unsupported contract amendment")
    if stable.get("mature_year") != len(years):
        errors.append("stable mature year must equal the explicit forecast horizon")
    if (
        _finite_number(stable.get("growth_rate"))
        and _finite_number(stable.get("cost_of_capital"))
        and stable["growth_rate"] >= stable["cost_of_capital"]
    ):
        errors.append("stable growth must be below terminal cost of capital")
    if (
        _finite_number(stable.get("growth_rate"))
        and _finite_number(stable.get("return_on_capital"))
        and stable["return_on_capital"] > 0
    ):
        expected_rate = stable["growth_rate"] / stable["return_on_capital"]
        if not _close(stable.get("reinvestment_rate"), expected_rate):
            errors.append("stable reinvestment rate must equal growth divided by return on capital")
    if (
        _finite_number(stable.get("return_on_capital"))
        and _finite_number(stable.get("cost_of_capital"))
        and not _close(
            stable.get("excess_return"),
            stable["return_on_capital"] - stable["cost_of_capital"],
        )
    ):
        errors.append("stable excess return is inconsistent")

    trace_names = {item.get("input_name") for item in forecast.get("assumption_trace", [])}
    required_traces = {
        "revenue_growth_rates",
        "operating_margins",
        "reinvestments",
        "discount_rates",
        "stable_state",
    }
    if not required_traces <= trace_names:
        errors.append("forecast is missing required narrative assumption traces")
    growth_rates = forecast.get("revenue_growth_rates", [])
    if (
        any(next_rate >= rate for rate, next_rate in pairwise(growth_rates))
        and "revenue_growth_rates" not in trace_names
    ):
        errors.append("growth plateau or increase lacks reviewed narrative support")
    discount_rates = forecast.get("discount_rates", [])
    if len(discount_rates) > 1 and len(set(discount_rates)) == 1:
        errors.append("constant growth-company discount rate is unsupported by maturation")

    market = document.get("market_context")
    if market is None:
        errors.append("revenue scale is unbounded without market context")
    else:
        for key in ("addressable_market", "market_growth_rates", "market_shares"):
            if len(market.get(key, [])) != len(years):
                errors.append(f"market-context {key} length must match forecast years")
        market_sizes = market.get("addressable_market", [])
        market_growth_rates = market.get("market_growth_rates", [])
        if len(market_sizes) == len(market_growth_rates) == len(years):
            previous_market = market.get("base_addressable_market")
            expected_market_sizes: list[float] = []
            if _finite_number(previous_market):
                for rate in market_growth_rates:
                    previous_market = float(previous_market) * (1 + rate)
                    expected_market_sizes.append(previous_market)
                _append_series_error(
                    errors, "addressable market", market_sizes, expected_market_sizes
                )
        if len(market.get("addressable_market", [])) == len(forecast.get("revenues", [])):
            expected_shares = [
                revenue / market_size
                for revenue, market_size in zip(forecast["revenues"], market["addressable_market"])
            ]
            _append_series_error(
                errors, "market shares", market.get("market_shares"), expected_shares
            )
            if any(share > 1 for share in expected_shares):
                errors.append("forecast revenue exceeds the addressable market")

    holiday = document.get("capacity_holiday")
    methods = forecast.get("reinvestment_method", [])
    holiday_years = [
        index for index, method in enumerate(methods, 1) if method == "capacity-holiday"
    ]
    if holiday_years:
        if holiday is None:
            errors.append("capacity-holiday method requires capacity support")
        else:
            start, end = holiday.get("start_year"), holiday.get("end_year")
            if holiday_years != list(range(start, end + 1)):
                errors.append("capacity-holiday methods do not match the declared holiday interval")
            if holiday.get("reinvestment_resumption_year") != end + 1:
                errors.append(
                    "capacity holiday must state the immediate reinvestment resumption year"
                )
            if len(holiday.get("utilization_rates", [])) != len(years):
                errors.append("capacity utilization length must match forecast years")
            available_capacity = holiday.get("available_capacity")
            if _finite_number(available_capacity) and len(forecast.get("revenues", [])) == len(
                holiday.get("utilization_rates", [])
            ):
                expected_utilization = [
                    min(revenue / float(available_capacity), 1.0)
                    for revenue in forecast["revenues"]
                ]
                _append_series_error(
                    errors,
                    "capacity utilization",
                    holiday.get("utilization_rates"),
                    expected_utilization,
                )
            maximum = holiday.get("maximum_supported_output")
            if _finite_number(maximum):
                for year in holiday_years:
                    if forecast.get("revenues", [])[year - 1] > maximum:
                        errors.append("capacity holiday exceeds supported output")
                        break
    elif holiday is not None:
        errors.append("capacity-holiday object exists without a holiday forecast segment")

    failure = document.get("failure_handoff")
    operating_value = going.get("operating_asset_value")
    bridge_start = operating_value
    if failure is not None and _finite_number(operating_value):
        try:
            adjusted = apply_failure_handoff(
                operating_value,
                material=failure.get("material"),
                failure_probability=failure.get("failure_probability"),
                survival_probability=failure.get("survival_probability"),
                failure_value=failure.get("failure_value"),
                failure_premium_in_discount_rate=failure.get("failure_premium_in_discount_rate"),
                failure_loss_in_cash_flows=failure.get("failure_loss_in_cash_flows"),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"failure handoff is inconsistent: {exc}")
        else:
            bridge_start = adjusted
            if not _close(failure.get("adjusted_operating_asset_value"), adjusted):
                errors.append("failure handoff adjusted value is inconsistent")
            if failure.get("material") and not failure.get("adjustment_input_ref"):
                errors.append(
                    "material failure risk requires an M3-compatible adjustment reference"
                )

    bridge = document.get("equity_bridge_handoff")
    if bridge is not None:
        if _finite_number(bridge_start) and not _close(
            bridge.get("operating_asset_value"), bridge_start
        ):
            errors.append("equity bridge does not start from the applicable operating value")
        if bridge.get("future_shares_added_to_current_denominator"):
            errors.append("future-share dilution double counts forecast financing")
        if not bridge.get("input_refs"):
            errors.append("equity bridge requires current-input references")

    review = document.get("review", {})
    approvals = (
        "classification_approved",
        "scale_approved",
        "reinvestment_approved",
        "risk_fade_approved",
        "stable_state_approved",
        "failure_risk_reviewed",
    )
    if review.get("status") == "unreviewed":
        errors.append("growth-company valuation requires human review status")
    if review.get("status") in {"reviewed", "approved"} and not all(
        review.get(key) for key in approvals
    ):
        errors.append("reviewed growth-company valuation requires all control approvals")

    sensitivity = document.get("sensitivity", {})
    scenario_ids = sensitivity.get("scenario_ids", [])
    grid = sensitivity.get("driver_grid", [])
    if scenario_ids != [item.get("scenario_id") for item in grid]:
        errors.append("sensitivity scenario IDs must match the deterministic driver grid")
    if valuation is not None:
        if (
            sensitivity.get("driver_one") != "stable_growth_rate"
            or sensitivity.get("driver_two") != "stable_cost_of_capital"
        ):
            errors.append("sensitivity grid must identify its two supported terminal drivers")
        else:
            for item in grid:
                try:
                    scenario_rates = list(forecast.get("discount_rates", []))
                    scenario_rates[-1] = item.get("driver_two")
                    scenario = run_growth_company_valuation(
                        recalculated,
                        scenario_rates,
                        stable_growth_rate=item.get("driver_one"),
                        stable_operating_margin=stable.get("operating_margin"),
                        stable_tax_rate=stable.get("tax_rate"),
                        stable_return_on_capital=stable.get("return_on_capital"),
                        stable_cost_of_capital=item.get("driver_two"),
                    )
                except (IndexError, TypeError, ValueError) as exc:
                    errors.append(f"sensitivity scenario cannot be recomputed: {exc}")
                    continue
                if not _close(item.get("operating_asset_value"), scenario.operating_asset_value):
                    errors.append(
                        f"sensitivity scenario {item.get('scenario_id')} is inconsistent with recomputed value"
                    )

        market_observation = sensitivity.get("market_price_observation")
        break_even_values = sensitivity.get("break_even_values", [])
        if market_observation is None and break_even_values:
            errors.append("break-even values require an observed comparison value")
        elif _finite_number(market_observation):
            for item in break_even_values:
                driver = item.get("driver")
                try:
                    if driver == "stable_growth_rate":
                        terminal_rate = stable.get("cost_of_capital")

                        def value_at(candidate: float, terminal_rate: float = terminal_rate) -> float:
                            return run_growth_company_valuation(
                                recalculated,
                                forecast.get("discount_rates", []),
                                stable_growth_rate=candidate,
                                stable_operating_margin=stable.get("operating_margin"),
                                stable_tax_rate=stable.get("tax_rate"),
                                stable_return_on_capital=stable.get("return_on_capital"),
                                stable_cost_of_capital=terminal_rate,
                            ).operating_asset_value

                        expected_break_even = _bisect_break_even(
                            value_at, float(market_observation), 0.0, terminal_rate - 1e-8
                        )
                    elif driver == "sales_to_capital_ratio":

                        def value_at(candidate: float) -> float:
                            scenario_forecast = build_growth_forecast(
                                base_revenue=base.get("revenues"),
                                revenue_growth_rates=forecast.get("revenue_growth_rates", []),
                                operating_margins=forecast.get("operating_margins", []),
                                marginal_tax_rate=forecast.get("marginal_tax_rate"),
                                initial_nol=base.get("net_operating_loss"),
                                initial_invested_capital=base.get("invested_capital"),
                                reinvestment_methods=forecast.get("reinvestment_method", []),
                                sales_to_capital_ratios=[
                                    candidate if method == "revenue-change" else None
                                    for method in forecast.get("reinvestment_method", [])
                                ],
                                fundamental_reinvestment_rates=forecast.get(
                                    "fundamental_reinvestment_rates", []
                                ),
                                capacity_reinvestments=forecast.get(
                                    "capacity_reinvestments", []
                                ),
                            )
                            return run_growth_company_valuation(
                                scenario_forecast,
                                forecast.get("discount_rates", []),
                                stable_growth_rate=stable.get("growth_rate"),
                                stable_operating_margin=stable.get("operating_margin"),
                                stable_tax_rate=stable.get("tax_rate"),
                                stable_return_on_capital=stable.get("return_on_capital"),
                                stable_cost_of_capital=stable.get("cost_of_capital"),
                            ).operating_asset_value

                        expected_break_even = _bisect_break_even(
                            value_at, float(market_observation), 0.01, 1000.0
                        )
                    else:
                        errors.append(f"unsupported break-even driver {driver}")
                        continue
                except (TypeError, ValueError) as exc:
                    errors.append(f"break-even value cannot be recomputed: {exc}")
                    continue
                if not _close(item.get("value"), expected_break_even, 1e-8):
                    errors.append(f"break-even driver {driver} is inconsistent with recomputed value")

    for ref in trace.get("source_refs", []):
        if ref not in source_ids:
            errors.append(f"unknown source reference {ref}")
    for ref in trace.get("claim_refs", []):
        if ref not in claim_ids:
            errors.append(f"unknown claim reference {ref}")
    for ref in trace.get("narrative_assertion_refs", []):
        if ref not in narrative_assertions:
            errors.append(f"unknown narrative assertion reference {ref}")
    assumption_assertions = {
        item.get("assertion_id") for item in forecast.get("assumption_trace", [])
    }
    for ref in assumption_assertions:
        if ref not in narrative_assertions:
            errors.append(f"unknown assumption assertion reference {ref}")
    if assumption_assertions != set(trace.get("narrative_assertion_refs", [])):
        errors.append("assumption traces and narrative assertion references must match")
    return errors


def validate_repository(root: Path = ROOT) -> tuple[list[str], int]:
    schema = json.loads(
        (root / "schemas/growth-company-valuation.schema.json").read_text(encoding="utf-8")
    )
    catalog = yaml.safe_load((root / "sources/catalog.yaml").read_text(encoding="utf-8"))
    source_ids = {item["id"] for item in catalog["sources"]}
    claim_ids: set[str] = set()
    for path in (root / "extraction/reviewed").glob("*.yaml"):
        claim_ids.update(
            item["id"] for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"]
        )
    narrative_assertions: set[str] = set()
    for path in (root / "benchmarks/fixtures/narratives").glob("*.json"):
        narrative_assertions.update(
            item["id"] for item in json.loads(path.read_text(encoding="utf-8"))["assertions"]
        )
    errors: list[str] = []
    paths = sorted((root / "benchmarks/fixtures/growth_company").glob("*.json"))
    ids: set[str] = set()
    narratives: set[str] = set()
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(root)
        if document.get("id") in ids:
            errors.append(f"{relative}: duplicate valuation ID")
        ids.add(document.get("id"))
        if document.get("narrative_id") in narratives:
            errors.append(f"{relative}: silently merged growth-company alternatives")
        narratives.add(document.get("narrative_id"))
        errors.extend(
            f"{relative}: {error}"
            for error in validate_document(
                document, schema, source_ids, claim_ids, narrative_assertions
            )
        )
    return errors, len(paths)


def main() -> int:
    try:
        errors, count = validate_repository()
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Growth-company validation failed: {exc}")
        return 1
    if errors:
        print("Growth-company validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {count} growth-company valuation document(s) and control invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
