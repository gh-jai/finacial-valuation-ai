"""Validate M5 documents and independently recompute decline and distress values."""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "benchmarks" / "fixtures" / "decline_distress"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.decline_distress import (
    bridge_to_common_equity,
    build_closure_value,
    build_decline_forecast,
    build_financing_path,
    classify_declining_company,
    contingent_survival_value,
    estimate_distress_sale_value,
    net_divestiture_proceeds,
    run_going_concern_valuation,
    select_orderly_liquidation,
    select_quadrant,
    turnaround_expected_value,
    value_orderly_liquidation,
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


def _value_basis(document: Mapping[str, Any]) -> str | None:
    distress = document.get("distress_case")
    if isinstance(distress, Mapping):
        return distress.get("aggregation_basis")  # type: ignore[return-value]
    turnaround = document.get("turnaround_case")
    if isinstance(turnaround, Mapping):
        return turnaround.get("basis")  # type: ignore[return-value]
    orderly = document.get("orderly_liquidation")
    if isinstance(orderly, Mapping):
        return orderly.get("basis")  # type: ignore[return-value]
    going = document.get("going_concern", {})
    return going.get("basis")  # type: ignore[return-value]


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
    profile = document.get("decline_profile", {})
    routing = document.get("routing", {})
    base = document.get("base_period", {})
    forecast_data = document.get("status_quo_forecast", {})
    financing_data = document.get("financing_path", {})
    closure_data = document.get("closure", {})
    going = document.get("going_concern", {})
    trace = document.get("traceability", {})

    if not classify_declining_company(
        m3_boundary_cleared=bool(profile.get("m3_boundary_cleared")),
        m4_boundary_cleared=bool(profile.get("m4_boundary_cleared")),
        mature_boundary_cleared=bool(profile.get("mature_boundary_cleared")),
        cycle_boundary_cleared=bool(profile.get("cycle_boundary_cleared")),
        multi_period_decline_evidence=len(profile.get("decline_evidence", [])) >= 2,
        sector_evidence=bool(profile.get("sector_condition")),
    ):
        errors.append("subject does not clear every M5 life-cycle boundary")
    try:
        expected_quadrant = select_quadrant(
            profile.get("reversibility"), routing.get("distress_level")
        )
    except ValueError as exc:
        errors.append(f"M5 quadrant cannot be selected: {exc}")
    else:
        if routing.get("quadrant") != expected_quadrant:
            errors.append("stored quadrant conflicts with reversibility and distress classifications")

    try:
        period_end = date.fromisoformat(str(base.get("period_end")))
        as_of_date = date.fromisoformat(str(document.get("as_of_date")))
    except ValueError:
        errors.append("base-period and valuation dates cannot be reconciled")
        as_of_date = None
    else:
        staleness = (as_of_date - period_end).days
        if base.get("staleness_days") != staleness or staleness < 0:
            errors.append("base-period staleness is inconsistent with the valuation date")
        if staleness > 90 and not base.get("normalization_adjustments"):
            errors.append("stale base period requires documented normalization adjustments")

    reported = base.get("reported_values", {})
    adjustment_totals: dict[str, float] = {}
    for adjustment in base.get("normalization_adjustments", []):
        field = adjustment.get("field")
        amount = adjustment.get("amount")
        if isinstance(field, str) and _finite_number(amount):
            adjustment_totals[field] = adjustment_totals.get(field, 0.0) + float(amount)
    for field in (
        "continuing_revenues",
        "continuing_operating_income",
        "cash",
        "book_debt",
        "market_debt",
        "face_debt",
        "invested_capital",
        "fixed_obligations",
    ):
        if _finite_number(reported.get(field)):
            normalized = float(reported[field]) + adjustment_totals.get(field, 0.0)
            if not _close(base.get(field), normalized):
                errors.append(f"normalized base {field} is inconsistent with reported value and adjustments")

    years = forecast_data.get("years", [])
    if not years or years != list(range(1, len(years) + 1)):
        errors.append("forecast years must be consecutive and start at one")
    if len(years) > 10:
        errors.append("forecast longer than ten years requires a contract amendment")
    forecast_series = (
        "revenue_growth_rates",
        "revenues",
        "operating_margins",
        "operating_incomes",
        "tax_rates",
        "cash_taxes",
        "after_tax_operating_incomes",
        "reinvestments",
        "invested_capital",
        "implied_returns_on_capital",
        "discount_rates",
    )
    financing_series = (
        "opening_face_debt",
        "debt_issuances",
        "debt_repayments",
        "closing_face_debt",
        "cash_interest",
        "taxable_operating_income_available",
        "cash_interest_tax_benefits",
        "market_value_debt",
        "market_value_equity",
        "debt_to_capital_ratios",
        "equity_to_capital_ratios",
        "pretax_costs_of_debt",
        "effective_interest_tax_rates",
        "after_tax_costs_of_debt",
        "costs_of_equity",
        "costs_of_capital",
    )
    for name in forecast_series:
        if len(forecast_data.get(name, [])) != len(years):
            errors.append(f"forecast {name} length must match years")
    for name in financing_series:
        if len(financing_data.get(name, [])) != len(years):
            errors.append(f"financing {name} length must match forecast years")

    forecast = None
    try:
        forecast = build_decline_forecast(
            base_revenue=base.get("continuing_revenues"),
            revenue_growth_rates=forecast_data.get("revenue_growth_rates", []),
            operating_margins=forecast_data.get("operating_margins", []),
            tax_rates=forecast_data.get("tax_rates", []),
            reinvestments=forecast_data.get("reinvestments", []),
            initial_invested_capital=base.get("invested_capital"),
        )
    except (TypeError, ValueError) as exc:
        errors.append(f"decline forecast cannot be recomputed: {exc}")
    else:
        for label, key, expected in (
            ("revenues", "revenues", forecast.revenues),
            ("operating incomes", "operating_incomes", forecast.operating_incomes),
            ("cash taxes", "cash_taxes", forecast.cash_taxes),
            (
                "after-tax operating incomes",
                "after_tax_operating_incomes",
                forecast.after_tax_operating_incomes,
            ),
            ("invested capital", "invested_capital", forecast.invested_capital),
            (
                "implied returns on capital",
                "implied_returns_on_capital",
                forecast.implied_returns_on_capital,
            ),
        ):
            _append_series_error(errors, label, forecast_data.get(key), expected)

    financing = None
    if forecast is not None:
        try:
            financing = build_financing_path(
                initial_face_debt=base.get("face_debt"),
                debt_issuances=financing_data.get("debt_issuances", []),
                debt_repayments=financing_data.get("debt_repayments", []),
                cash_interest=financing_data.get("cash_interest", []),
                operating_incomes=forecast.operating_incomes,
                tax_rates=forecast_data.get("tax_rates", []),
                market_value_debt=financing_data.get("market_value_debt", []),
                market_value_equity=financing_data.get("market_value_equity", []),
                pretax_costs_of_debt=financing_data.get("pretax_costs_of_debt", []),
                costs_of_equity=financing_data.get("costs_of_equity", []),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"financing path cannot be recomputed: {exc}")
        else:
            for label, key, expected in (
                ("opening face debt", "opening_face_debt", financing.opening_face_debt),
                ("closing face debt", "closing_face_debt", financing.closing_face_debt),
                (
                    "taxable operating income available",
                    "taxable_operating_income_available",
                    financing.taxable_operating_income_available,
                ),
                (
                    "cash interest tax benefits",
                    "cash_interest_tax_benefits",
                    financing.cash_interest_tax_benefits,
                ),
                (
                    "debt-to-capital ratios",
                    "debt_to_capital_ratios",
                    financing.debt_to_capital_ratios,
                ),
                (
                    "equity-to-capital ratios",
                    "equity_to_capital_ratios",
                    financing.equity_to_capital_ratios,
                ),
                (
                    "effective interest tax rates",
                    "effective_interest_tax_rates",
                    financing.effective_interest_tax_rates,
                ),
                (
                    "after-tax costs of debt",
                    "after_tax_costs_of_debt",
                    financing.after_tax_costs_of_debt,
                ),
                ("costs of capital", "costs_of_capital", financing.costs_of_capital),
            ):
                _append_series_error(errors, label, financing_data.get(key), expected)
            _append_series_error(
                errors,
                "forecast discount rates",
                forecast_data.get("discount_rates"),
                financing.costs_of_capital,
            )

    closure = None
    try:
        closure = build_closure_value(
            closure_data.get("mode"),
            final_revenue=forecast.revenues[-1] if forecast is not None else None,
            terminal_growth_rate=closure_data.get("terminal_growth_rate"),
            terminal_operating_margin=closure_data.get("terminal_operating_margin"),
            terminal_tax_rate=closure_data.get("terminal_tax_rate"),
            terminal_return_on_capital=closure_data.get("terminal_return_on_capital"),
            terminal_cost_of_capital=closure_data.get("terminal_cost_of_capital"),
            finite_life_proceeds=closure_data.get("finite_life_proceeds"),
        )
    except (TypeError, ValueError, IndexError) as exc:
        errors.append(f"closure value cannot be recomputed: {exc}")
    else:
        if closure_data.get("closure_year") != len(years):
            errors.append("closure year must equal the explicit forecast horizon")
        if not _close(
            closure_data.get("terminal_reinvestment_rate"), closure.terminal_reinvestment_rate
        ):
            errors.append("stored terminal reinvestment rate is inconsistent")
        if not _close(
            going.get("terminal_or_closure_value"), closure.terminal_or_closure_value
        ):
            errors.append("stored terminal or closure value is inconsistent")
        if (
            financing is not None
            and closure.mode != "finite_life"
            and not _close(
                closure_data.get("terminal_cost_of_capital"), financing.costs_of_capital[-1]
            )
        ):
            errors.append("terminal cost of capital does not converge from the financing path")

    valuation = None
    if forecast is not None and financing is not None and closure is not None:
        try:
            valuation = run_going_concern_valuation(forecast, financing, closure)
        except (TypeError, ValueError) as exc:
            errors.append(f"going-concern value cannot be recomputed: {exc}")
        else:
            _append_series_error(errors, "FCFF", going.get("fcff"), forecast.fcff)
            _append_series_error(
                errors,
                "cumulative discount factors",
                going.get("cumulative_discount_factors"),
                valuation.cumulative_discount_factors,
                1e-10,
            )
            for label, actual, expected in (
                ("forecast present value", going.get("forecast_present_value"), valuation.forecast_present_value),
                (
                    "closure present value",
                    going.get("terminal_or_closure_present_value"),
                    valuation.terminal_or_closure_present_value,
                ),
                ("operating asset value", going.get("operating_asset_value"), valuation.operating_asset_value),
            ):
                if not _close(actual, expected):
                    errors.append(f"stored {label} is inconsistent with recomputed value")
            if not _trail_close(going.get("calculation_trail"), valuation.calculation_trail):
                errors.append("stored going-concern calculation trail is inconsistent")

    divestitures = document.get("divestitures", [])
    divestiture_ids = {item.get("id") for item in divestitures}
    negative_years = {
        index for index, value in enumerate(forecast_data.get("reinvestments", []), 1) if value < 0
    }
    support = forecast_data.get("negative_reinvestment_support", [])
    support_years = {item.get("year") for item in support}
    if negative_years != support_years:
        errors.append("every negative reinvestment period requires one governed support record")
    for item in support:
        year = item.get("year")
        if isinstance(year, int) and 1 <= year <= len(years):
            if not _close(item.get("amount"), forecast_data.get("reinvestments", [])[year - 1]):
                errors.append("negative reinvestment support amount conflicts with forecast")
            documented_release = item.get("capital_reduction", 0) + item.get(
                "working_capital_release", 0
            )
            if not _close(-item.get("amount", 0), documented_release):
                errors.append("negative reinvestment lacks an equal documented capital release")
        if not set(item.get("divestiture_ids", [])) <= divestiture_ids:
            errors.append("negative reinvestment references an unknown divestiture")
        referenced_divestitures = [
            divestiture
            for divestiture in divestitures
            if divestiture.get("id") in set(item.get("divestiture_ids", []))
        ]
        if item.get("source") in {"divestiture", "mixed"}:
            capital_removed = sum(
                divestiture.get("capital_removed", 0) for divestiture in referenced_divestitures
            )
            net_proceeds = sum(
                divestiture.get("net_sale_proceeds", 0) for divestiture in referenced_divestitures
            )
            if not _close(item.get("capital_reduction"), capital_removed):
                errors.append("negative reinvestment capital reduction conflicts with divestitures")
            if not _close(
                -item.get("amount", 0),
                net_proceeds + item.get("working_capital_release", 0),
            ):
                errors.append("negative reinvestment does not recognize divestiture proceeds once")

    for item in divestitures:
        try:
            expected_net = net_divestiture_proceeds(
                item.get("gross_sale_proceeds"),
                item.get("transaction_costs"),
                item.get("taxes_on_sale"),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"divestiture {item.get('id')} cannot be recomputed: {exc}")
            continue
        if not _close(item.get("net_sale_proceeds"), expected_net):
            errors.append(f"divestiture {item.get('id')} net proceeds are inconsistent")
        if not _close(
            item.get("remaining_revenue"),
            item.get("pre_sale_revenue", 0) - item.get("disposed_revenue_contribution", 0),
        ):
            errors.append(f"divestiture {item.get('id')} retains disposed revenue")
        if not _close(
            item.get("remaining_operating_income"),
            item.get("pre_sale_operating_income", 0)
            - item.get("disposed_operating_income_contribution", 0),
        ):
            errors.append(f"divestiture {item.get('id')} retains disposed operating income")
        year = item.get("year")
        if isinstance(year, int) and 1 <= year <= len(years):
            if not _close(forecast_data.get("revenues", [])[year - 1], item.get("remaining_revenue")):
                errors.append(f"divestiture {item.get('id')} remaining revenue conflicts with forecast")
            if not _close(
                forecast_data.get("operating_incomes", [])[year - 1],
                item.get("remaining_operating_income"),
            ):
                errors.append(
                    f"divestiture {item.get('id')} remaining operating income conflicts with forecast"
                )
        if item.get("proceeds_in_separate_cash_flow"):
            errors.append(f"divestiture {item.get('id')} duplicates proceeds outside reinvestment")

    quadrant = routing.get("quadrant")
    no_distress_value = going.get("operating_asset_value")
    turnaround = document.get("turnaround_case")
    if quadrant in {"reversible_low", "reversible_high"} and isinstance(turnaround, Mapping):
        if turnaround.get("basis") != going.get("basis"):
            errors.append("turnaround alternative basis conflicts with going-concern basis")
        try:
            components = turnaround_expected_value(
                turnaround.get("status_quo_value"),
                turnaround.get("turnaround_value"),
                turnaround.get("probability_of_change"),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"turnaround alternative cannot be recomputed: {exc}")
        else:
            if not _close(turnaround.get("probability_of_no_change"), 1 - turnaround.get("probability_of_change", 0)):
                errors.append("turnaround probabilities do not reconcile")
            for label, actual, expected in (
                ("status-quo component", turnaround.get("status_quo_component"), components[0]),
                ("turnaround component", turnaround.get("turnaround_component"), components[1]),
                ("no-distress value", turnaround.get("no_distress_value"), components[2]),
            ):
                if not _close(actual, expected):
                    errors.append(f"stored turnaround {label} is inconsistent")
            if not _close(turnaround.get("status_quo_value"), going.get("operating_asset_value")):
                errors.append("turnaround alternative does not start from status-quo value")
            no_distress_value = components[2]

    orderly = document.get("orderly_liquidation")
    if quadrant == "irreversible_low" and isinstance(orderly, Mapping):
        if orderly.get("basis") != going.get("basis"):
            errors.append("orderly-liquidation basis conflicts with going-concern basis")
        schedule = orderly.get("sale_schedule", [])
        schedule_years = [item.get("year") for item in schedule]
        if schedule_years != list(range(1, len(schedule) + 1)):
            errors.append("orderly-liquidation schedule years must be consecutive and start at one")
        for item in schedule:
            try:
                net = net_divestiture_proceeds(
                    item.get("gross_proceeds"), item.get("transaction_costs"), item.get("taxes_on_sale")
                )
            except (TypeError, ValueError) as exc:
                errors.append(f"orderly-liquidation sale cannot be recomputed: {exc}")
            else:
                if not _close(item.get("net_proceeds"), net):
                    errors.append("orderly-liquidation net proceeds are inconsistent")
        try:
            orderly_value = value_orderly_liquidation(
                [item.get("net_proceeds") for item in schedule],
                [item.get("discount_rate") for item in schedule],
            )
            selected, selected_value = select_orderly_liquidation(
                orderly.get("status_quo_value"), orderly_value
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"orderly-liquidation value cannot be recomputed: {exc}")
        else:
            if not _close(orderly.get("value"), orderly_value):
                errors.append("stored orderly-liquidation value is inconsistent")
            if orderly.get("selected_alternative") != selected or not _close(
                orderly.get("selected_value"), selected_value
            ):
                errors.append("orderly-liquidation selection is inconsistent")
            if not _close(orderly.get("status_quo_value"), going.get("operating_asset_value")):
                errors.append("orderly-liquidation comparison uses a stale status-quo value")
            no_distress_value = selected_value

    basis = _value_basis(document)
    if basis != going.get("basis"):
        errors.append("alternative aggregation basis conflicts with going-concern basis")
    distress = document.get("distress_case")
    applicable_value = no_distress_value
    if routing.get("distress_level") == "high" and isinstance(distress, Mapping):
        if not _close(distress.get("no_distress_value"), no_distress_value):
            errors.append("distress case uses a stale no-distress value")
        try:
            probability_date = date.fromisoformat(str(distress.get("probability_as_of_date")))
        except ValueError:
            errors.append("distress probability date is invalid")
        else:
            if as_of_date is not None and probability_date > as_of_date:
                errors.append("distress probability date is later than valuation date")
        if distress.get("probability_horizon_years") != len(years):
            errors.append("distress probability horizon must match the valuation horizon")
        if (
            distress.get("source_event") != distress.get("probability_event")
            and not distress.get("default_to_cessation_mapping")
        ):
            errors.append("default or bankruptcy evidence requires an event-to-cessation mapping")
        if distress.get("probability_source_ref") not in distress.get("evidence_refs", []):
            errors.append("distress probability source must appear in the case evidence references")
        method_fields = {
            "going_concern_haircut": {
                "reference_going_concern_asset_value",
                "haircut",
            },
            "existing_asset_value": {
                "existing_asset_after_tax_income",
                "existing_asset_cost_of_capital",
            },
            "adjusted_book_assets": {
                "eligible_book_assets",
                "economic_impairment",
                "forced_sale_discount",
            },
        }
        selected_method = distress.get("recovery_method")
        selected_fields = method_fields.get(selected_method, set())
        all_method_fields = set().union(*method_fields.values())
        if any(
            distress.get(field) is not None
            for field in all_method_fields - selected_fields
        ):
            errors.append("distress-sale case supplies overlapping recovery-method inputs")
        try:
            sale = estimate_distress_sale_value(
                distress.get("recovery_method"),
                reference_going_concern_asset_value=distress.get(
                    "reference_going_concern_asset_value"
                ),
                haircut=distress.get("haircut"),
                existing_asset_after_tax_income=distress.get("existing_asset_after_tax_income"),
                existing_asset_cost_of_capital=distress.get("existing_asset_cost_of_capital"),
                eligible_book_assets=distress.get("eligible_book_assets"),
                economic_impairment=distress.get("economic_impairment"),
                forced_sale_discount=distress.get("forced_sale_discount"),
                direct_sale_costs=distress.get("direct_sale_costs"),
                indirect_operating_costs=distress.get("indirect_operating_costs"),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"distress-sale value cannot be recomputed: {exc}")
        else:
            if not _close(distress.get("gross_recovery_value"), sale.gross_recovery_value):
                errors.append("stored gross recovery value is inconsistent")
            if not _close(distress.get("distress_sale_value"), sale.distress_sale_value):
                errors.append("stored distress-sale value is inconsistent")
            try:
                contingent = contingent_survival_value(
                    no_distress_value,
                    sale.distress_sale_value,
                    survival_probability=distress.get("survival_probability"),
                    distress_probability=distress.get("distress_probability"),
                    distress_premium_in_discount_rates=distress.get(
                        "distress_premium_in_discount_rates"
                    ),
                    distress_loss_in_fcff=distress.get("distress_loss_in_fcff"),
                )
            except (TypeError, ValueError) as exc:
                errors.append(f"contingent-survival value cannot be recomputed: {exc}")
            else:
                for label, actual, expected in (
                    ("survival component", distress.get("survival_component"), contingent.survival_component),
                    ("distress component", distress.get("distress_component"), contingent.distress_component),
                    ("contingent value", distress.get("contingent_value"), contingent.contingent_value),
                ):
                    if not _close(actual, expected):
                        errors.append(f"stored {label} is inconsistent")
                if not _trail_close(distress.get("calculation_trail"), contingent.calculation_trail):
                    errors.append("stored contingent-survival trail is inconsistent")
                applicable_value = contingent.contingent_value

    bridge = document.get("claim_bridge")
    if basis != "common-equity" and not isinstance(bridge, Mapping):
        errors.append("non-equity aggregation basis requires one claim bridge")
    elif isinstance(bridge, Mapping):
        if bridge.get("input_basis") != basis or not _close(bridge.get("input_value"), applicable_value):
            errors.append("claim bridge does not start from the applicable common-basis value")
        if bridge.get("basis_date") != document.get("as_of_date"):
            errors.append("claim bridge is not dated to the valuation date")
        if not _close(bridge.get("cash"), base.get("cash")) or not _close(
            bridge.get("market_value_debt"), base.get("market_debt")
        ):
            errors.append("claim bridge must use current cash and market debt from the normalized base")
        try:
            recomputed_bridge = bridge_to_common_equity(
                bridge.get("input_value"),
                cash=bridge.get("cash"),
                market_value_debt=bridge.get("market_value_debt"),
                senior_claims=bridge.get("senior_claims"),
                hybrid_claims=bridge.get("hybrid_claims"),
                option_claims=bridge.get("option_claims"),
                share_count=bridge.get("share_count"),
                limited_liability_floor=bridge.get("limited_liability_floor"),
            )
        except (TypeError, ValueError) as exc:
            errors.append(f"claim bridge cannot be recomputed: {exc}")
        else:
            if not _close(bridge.get("common_equity_value"), recomputed_bridge.common_equity_value):
                errors.append("stored common-equity value is inconsistent")
            if recomputed_bridge.per_share_value is None:
                if bridge.get("per_share_value") is not None:
                    errors.append("per-share value exists without a share count")
            elif not _close(bridge.get("per_share_value"), recomputed_bridge.per_share_value):
                errors.append("stored per-share value is inconsistent")
            if not _trail_close(bridge.get("calculation_trail"), recomputed_bridge.calculation_trail):
                errors.append("stored claim-bridge trail is inconsistent")

    assumption_traces = list(forecast_data.get("assumption_trace", [])) + list(
        financing_data.get("assumption_trace", [])
    )
    trace_names = {item.get("input_name") for item in assumption_traces}
    required_trace_names = {
        "revenue_growth_rates",
        "operating_margins",
        "reinvestments",
        "tax_rates",
        "debt_schedule",
        "cash_interest",
        "market_value_capital",
        "costs_of_debt",
        "costs_of_equity",
        "closure",
    }
    if not required_trace_names <= trace_names:
        errors.append("forecast and financing paths are missing required assumption traces")
    assumption_assertions = {item.get("assertion_id") for item in assumption_traces}
    for ref in trace.get("source_refs", []):
        if ref not in source_ids:
            errors.append(f"unknown source reference {ref}")
    for ref in trace.get("claim_refs", []):
        if ref not in claim_ids:
            errors.append(f"unknown claim reference {ref}")
    for ref in trace.get("narrative_assertion_refs", []):
        if ref not in narrative_assertions:
            errors.append(f"unknown narrative assertion reference {ref}")
    for ref in assumption_assertions:
        if ref not in narrative_assertions:
            errors.append(f"unknown assumption assertion reference {ref}")
    if assumption_assertions != set(trace.get("narrative_assertion_refs", [])):
        errors.append("assumption traces and narrative assertion references must match")

    review = document.get("review", {})
    approvals = (
        "classification_approved",
        "quadrant_approved",
        "divestiture_approved",
        "probability_approved",
        "basis_approved",
        "risk_separation_approved",
        "closure_approved",
    )
    if review.get("status") == "unreviewed":
        errors.append("M5 valuation requires human review status")
    if review.get("status") in {"reviewed", "approved"} and not all(
        review.get(key) for key in approvals
    ):
        errors.append("reviewed M5 valuation requires every control approval")
    return errors


def validate_repository(root: Path = ROOT) -> tuple[list[str], int]:
    schema = json.loads(
        (root / "schemas/decline-distress-valuation.schema.json").read_text(encoding="utf-8")
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
    paths = sorted((root / "benchmarks/fixtures/decline_distress").glob("*.json"))
    ids: set[str] = set()
    narratives: set[str] = set()
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(root)
        if document.get("id") in ids:
            errors.append(f"{relative}: duplicate valuation ID")
        ids.add(document.get("id"))
        if document.get("narrative_id") in narratives:
            errors.append(f"{relative}: silently merged M5 alternatives")
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
        print(f"Decline-distress validation failed: {exc}")
        return 1
    if errors:
        print("Decline-distress validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {count} decline-distress valuation document(s) and control invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
