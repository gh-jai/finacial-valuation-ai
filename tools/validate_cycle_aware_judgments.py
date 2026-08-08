"""Independently validate and recompute M6 cycle-aware judgment documents."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "benchmarks" / "fixtures" / "cycle_aware"
DIMENSIONS = {"economic", "company_profit", "psychology_valuation", "risk_attitude", "credit"}
BANDS = ("extreme_low", "below_midpoint", "midpoint", "above_midpoint", "extreme_high")
PAYLOADS = {"normalized_inputs", "transition_to_normal", "current_expectations", "stop"}


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _close(actual: Any, expected: float, tolerance: float = 1e-9) -> bool:
    return _finite(actual) and abs(float(actual) - expected) <= tolerance


def _clean(value: float) -> float:
    return round(value, 12)


def _transition(
    current: Mapping[str, Any], anchor: Mapping[str, Any], periods: int, tax_rate: float
) -> list[dict[str, float | int]]:
    fields = ("driver", "revenue", "operating_margin", "reinvestment", "invested_capital", "leverage", "financing_cost")
    result: list[dict[str, float | int]] = []
    for period in range(periods + 1):
        weight = period / periods
        row = {name: _clean(float(current[name]) + (float(anchor[name]) - float(current[name])) * weight) for name in fields}
        operating_income = row["revenue"] * row["operating_margin"]
        after_tax = operating_income * (1 - tax_rate)
        result.append({
            "period": period, **row,
            "operating_income": _clean(operating_income),
            "after_tax_operating_income": _clean(after_tax),
            "return_on_capital": _clean(after_tax / row["invested_capital"]),
        })
    return result


def _scenario(inputs: Mapping[str, Any]) -> list[dict[str, float | int]]:
    drivers = [item["value"] for item in inputs["driver_curve"]]
    capital = float(inputs["initial_invested_capital"])
    result: list[dict[str, float | int]] = []
    for period, values in enumerate(zip(drivers, inputs["volumes"], inputs["fixed_costs"], inputs["unit_costs"], inputs["base_reinvestments"]), 1):
        driver, volume, fixed_cost, unit_cost, base_reinvestment = map(float, values)
        revenue = driver * volume
        operating_cost = fixed_cost + unit_cost * volume
        operating_income = revenue - operating_cost
        margin = operating_income / revenue if revenue else 0.0
        after_tax = operating_income - max(0.0, operating_income) * float(inputs["tax_rate"])
        reinvestment = base_reinvestment + float(inputs["reinvestment_sensitivity"]) * (driver - float(inputs["base_driver"]))
        opening_capital = capital
        capital += reinvestment
        financing_cost = float(inputs["base_financing_cost"]) + float(inputs["funding_sensitivity"]) * (driver - float(inputs["base_driver"]))
        result.append({
            "period": period, "driver": _clean(driver), "volume": _clean(volume),
            "revenue": _clean(revenue), "operating_cost": _clean(operating_cost),
            "operating_margin": _clean(margin), "operating_income": _clean(operating_income),
            "after_tax_operating_income": _clean(after_tax), "reinvestment": _clean(reinvestment),
            "invested_capital": _clean(capital), "return_on_capital": _clean(after_tax / opening_capital),
            "financing_cost": _clean(financing_cost),
        })
    return result


def _rows_close(actual: Any, expected: Sequence[Mapping[str, Any]]) -> bool:
    if not isinstance(actual, list) or len(actual) != len(expected):
        return False
    for actual_row, expected_row in zip(actual, expected):
        if not isinstance(actual_row, Mapping) or set(actual_row) != set(expected_row):
            return False
        for key, expected_value in expected_row.items():
            actual_value = actual_row[key]
            if _finite(expected_value):
                if not _close(actual_value, float(expected_value)):
                    return False
            elif actual_value != expected_value:
                return False
    return True


def _normalized_value(item: Mapping[str, Any]) -> float:
    values = [float(value) for value in item["observations"]]
    average = sum(values) / len(values)
    method = item["method"]
    if method == "absolute_historical_average":
        return _clean(average)
    if method == "relative_historical_average":
        return _clean(average * float(item["current_scale"]))
    if method == "sector_average_with_adjustment":
        return _clean(average + float(item["company_adjustment"]))
    return _clean(average * float(item["driver_sensitivity"]) + float(item["intercept"]))


def _aligned(selected: str, implication: str) -> bool:
    return selected in BANDS and implication in BANDS and abs(BANDS.index(selected) - BANDS.index(implication)) <= 1


def _alignment(selected: str, dimensions: Sequence[Mapping[str, Any]]) -> int:
    return sum(
        item.get("availability") == "available"
        and not item.get("stale_evidence_refs")
        and not item.get("unresolved_strong_contradiction")
        and _aligned(selected, str(item.get("band_implication")))
        for item in dimensions
    )


def _confidence(selected: str, dimensions: Sequence[Mapping[str, Any]]) -> str:
    available = [item for item in dimensions if item.get("availability") == "available"]
    non_stale = [item for item in available if not item.get("stale_evidence_refs")]
    aligned = _alignment(selected, dimensions)
    unresolved = any(item.get("unresolved_strong_contradiction") for item in dimensions)
    if len(available) == 5 and aligned >= 4 and not unresolved:
        return "high"
    if len(non_stale) >= 3 and aligned >= 3 and not unresolved:
        return "medium"
    return "low"


def _posture(position: str) -> str:
    return {
        "extreme_high": "defensive_review", "extreme_low": "opportunity_review",
        "below_midpoint": "balanced_review", "midpoint": "balanced_review",
        "above_midpoint": "balanced_review", "indeterminate": "insufficient_evidence",
    }.get(position, "insufficient_evidence")


def load_registry(root: Path = ROOT) -> tuple[dict, set[str], set[str], set[str]]:
    schema = json.loads((root / "schemas/cycle-aware-judgment.schema.json").read_text(encoding="utf-8"))
    catalog = yaml.safe_load((root / "sources/catalog.yaml").read_text(encoding="utf-8"))
    sources = {item["id"] for item in catalog["sources"]}
    claims: set[str] = set()
    for path in (root / "extraction/reviewed").glob("*.yaml"):
        claims.update(item["id"] for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"])
    narratives: set[str] = set()
    for path in (root / "benchmarks/fixtures/narratives").glob("*.json"):
        narratives.update(item["id"] for item in json.loads(path.read_text(encoding="utf-8"))["assertions"])
    return schema, sources, claims, narratives


def validate_document(
    document: Mapping[str, Any],
    schema: Mapping[str, Any],
    source_ids: set[str],
    claim_ids: set[str],
    narrative_assertions: set[str],
) -> list[str]:
    errors = [
        f"schema {'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
        for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document), key=lambda item: list(item.path))
    ]
    try:
        valuation_date = date.fromisoformat(str(document.get("valuation_date")))
    except ValueError:
        return errors + ["valuation date cannot be parsed"]

    subject = document.get("subject_classification", {})
    boundaries = subject.get("lifecycle_boundaries", {})
    observation = subject.get("observation_window", {})
    exposure = subject.get("exposure_type")
    if not all(boundaries.get(key) for key in ("m3_cleared", "m4_cleared", "m5_cleared", "mature_company")) or boundaries.get("route") != "M6":
        errors.append("subject has an uncleared life-cycle boundary and cannot enter M6")
    if exposure in {"economic_cycle", "commodity_price", "mixed_cycle"} and (not observation.get("strong_and_weak_conditions") or int(observation.get("observation_years", 0)) < 2):
        errors.append("cycle treatment requires a representative observation window with strong and weak conditions")
    if exposure in {"economic_cycle", "commodity_price", "mixed_cycle"} and not subject.get("linked_financial_series"):
        errors.append("supported cycle exposure requires a company-specific driver-to-financial mapping")
    company_currency = document.get("company", {}).get("currency")
    base_currency = document.get("current_base", {}).get("currency")
    intrinsic_currency = document.get("intrinsic_value_reference", {}).get("currency")
    if len({company_currency, base_currency, intrinsic_currency}) != 1:
        errors.append("company, current-base, and intrinsic-value currency must be identical")

    assessment = document.get("cycle_assessment", {})
    regime = assessment.get("regime")
    treatment = document.get("valuation_treatment", {})
    mode = treatment.get("mode")
    present_payloads = PAYLOADS & set(treatment)
    if len(present_payloads) != 1 or present_payloads != {mode}:
        errors.append("valuation treatment must contain exactly one matching payload")
    if exposure == "not_supported" or regime == "insufficient_evidence":
        if mode != "stop":
            errors.append("unsupported exposure or insufficient evidence must stop")
    if regime in {"unstable", "structural_break"} and mode not in {"current_expectations", "stop"}:
        errors.append("unstable or structural-break regimes require current expectations or stop")
    if regime == "structural_break":
        break_assessment = assessment.get("break_assessment")
        if not isinstance(break_assessment, Mapping) or not all(break_assessment.get(key) for key in ("hypothesis", "date_or_interval", "mechanism", "affected_inputs", "counterevidence_refs")):
            errors.append("structural break requires a dated mechanism, affected inputs, and counterevidence")
    if mode in {"normalized_inputs", "transition_to_normal"} and regime != "established_recurring":
        errors.append("historical normalization requires an established recurring regime")

    evidence_items = document.get("cycle_evidence", {}).get("items", [])
    evidence_by_id = {item.get("evidence_id"): item for item in evidence_items if isinstance(item, Mapping)}
    counts = Counter(item.get("dimension") for item in evidence_items if isinstance(item, Mapping))
    if set(counts) != DIMENSIONS:
        errors.append("all five evidence dimensions must appear as available or explicitly unavailable")
    max_age = document.get("evidence_staleness_policy", {}).get("max_age_days")
    if not isinstance(max_age, int):
        max_age = 0
    for item in evidence_items:
        try:
            as_of = date.fromisoformat(str(item.get("as_of_date")))
        except ValueError:
            continue
        if as_of > valuation_date:
            errors.append(f"future-dated evidence {item.get('evidence_id')} is not permitted")
        expected_stale = (valuation_date - as_of).days > max_age
        if item.get("stale") != expected_stale:
            errors.append(f"evidence staleness for {item.get('evidence_id')} is inconsistent with policy")

    conclusion_refs = (
        (subject.get("supporting_evidence_refs", []), "subject_classification"),
        (subject.get("contradicting_evidence_refs", []), "subject_classification_counterevidence"),
        (assessment.get("supporting_evidence_refs", []), "cycle_assessment"),
        (assessment.get("counterevidence_refs", []), "cycle_assessment_counterevidence"),
        (document.get("judgment_overlay", {}).get("supporting_evidence_refs", []), "judgment_overlay"),
        (document.get("judgment_overlay", {}).get("counterevidence_refs", []), "judgment_overlay_counterevidence"),
    )
    for refs, conclusion in conclusion_refs:
        for ref in refs:
            item = evidence_by_id.get(ref)
            if item is None:
                errors.append(f"unknown evidence reference {ref}")
            elif conclusion not in item.get("supports", []):
                errors.append(f"evidence reference {ref} is not bidirectionally linked to {conclusion}")

    if mode == "normalized_inputs" and isinstance(treatment.get("normalized_inputs"), Mapping):
        payload = treatment["normalized_inputs"]
        window = payload.get("normalization_window", {})
        if not window.get("representative") or not window.get("strong_and_weak_conditions"):
            errors.append("normalized inputs require a representative full-cycle window")
        methods = payload.get("input_methods", [])
        method_names = {item.get("input_name") for item in methods}
        normalized_set = payload.get("normalized_input_set", {})
        if method_names != set(normalized_set):
            errors.append("normalized input methods must recompute the complete governed vector")
        for item in methods:
            method = item.get("method")
            if method == "absolute_historical_average" and item.get("scale_change_material"):
                errors.append("absolute average cannot ignore a material scale change")
            if method == "sector_average_with_adjustment" and not item.get("comparability_documented"):
                errors.append("sector normalization requires comparability and a company adjustment")
            try:
                expected = _normalized_value(item)
            except (KeyError, TypeError, ValueError):
                errors.append(f"normalized input {item.get('input_name')} cannot be recomputed")
            else:
                if not _close(item.get("calculated_value"), expected):
                    errors.append(f"normalized input {item.get('input_name')} is inconsistent with governed observations")
                if item.get("input_name") in normalized_set and not _close(normalized_set[item["input_name"]], expected):
                    errors.append(f"normalized input set does not preserve recomputed {item.get('input_name')}")
        if document.get("valuation_input_handoff", {}).get("normalized_input_set") != normalized_set:
            errors.append("valuation-input handoff does not preserve the complete normalized input set")

    if mode == "transition_to_normal" and isinstance(treatment.get("transition_to_normal"), Mapping):
        payload = treatment["transition_to_normal"]
        window = payload.get("normalization_window", {})
        if not window.get("representative") or not window.get("strong_and_weak_conditions"):
            errors.append("transition requires a representative normalization window")
        try:
            expected_path = _transition(payload["current_input_set"], payload["normalized_anchor"], int(payload["transition_periods"]), float(payload["tax_rate"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            errors.append("transition path cannot be independently recomputed")
        else:
            actual_path = payload.get("period_inputs")
            if not actual_path or not _rows_close([actual_path[0]], [expected_path[0]]):
                errors.append("transition does not begin at the reconciled current base")
            if not actual_path or not _rows_close([actual_path[-1]], [expected_path[-1]]):
                errors.append("transition does not end at the one normalized anchor")
            if not _rows_close(actual_path, expected_path):
                errors.append("stored transition path is inconsistent with independent recomputation")
            if document.get("valuation_input_handoff", {}).get("period_inputs") != actual_path:
                errors.append("valuation-input handoff does not preserve the governed transition path")
        if payload.get("recovery_growth_applied"):
            errors.append("recovery growth double counts the normalized transition")

    if mode == "current_expectations" and isinstance(treatment.get("current_expectations"), Mapping):
        payload = treatment["current_expectations"]
        all_curves = [payload.get("driver_curve", [])] + [item.get("input_set", {}).get("driver_curve", []) for item in payload.get("scenarios", [])]
        current_driver_unit = document.get("current_base", {}).get("current_driver", {}).get("unit")
        for curve in all_curves:
            for point in curve:
                try:
                    as_of = date.fromisoformat(str(point.get("as_of_date")))
                except ValueError:
                    continue
                if as_of > valuation_date:
                    errors.append("curve as-of date cannot be after the valuation date")
                if point.get("unit") != current_driver_unit:
                    errors.append("driver-curve units must match the reconciled current driver unit")
        if payload.get("storable_commodity") and any(point.get("source_type") == "forward_or_futures" for curve in all_curves for point in curve) and not payload.get("carry_limitation_disclosed"):
            errors.append("storable-commodity futures require a carry limitation disclosure")
        if payload.get("historical_normal_reused"):
            errors.append("current expectations cannot silently reuse the invalid historical normal")
        scenarios = payload.get("scenarios", [])
        trail_ids = [item.get("calculation_trail_id") for item in scenarios]
        if len(trail_ids) != len(set(trail_ids)):
            errors.append("scenario calculation trails must be isolated")
        scenario_ids: list[str] = []
        for scenario in scenarios:
            scenario_ids.append(str(scenario.get("scenario_id")))
            inputs = scenario.get("input_set", {})
            lengths = {len(inputs.get(name, [])) for name in ("driver_curve", "volumes", "fixed_costs", "unit_costs", "base_reinvestments")}
            if len(lengths) != 1:
                errors.append(f"scenario {scenario.get('scenario_id')} has incomplete driver mapping lengths")
                continue
            try:
                expected = _scenario(inputs)
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                errors.append(f"scenario {scenario.get('scenario_id')} driver mapping cannot be recomputed")
            else:
                if not _rows_close(scenario.get("period_inputs"), expected):
                    errors.append(f"scenario {scenario.get('scenario_id')} driver mapping is incomplete or inconsistent")
        if document.get("valuation_input_handoff", {}).get("scenario_ids") != scenario_ids:
            errors.append("valuation-input handoff scenario IDs do not match isolated scenarios")
        probabilities = [item.get("probability") for item in scenarios]
        intrinsic = document.get("intrinsic_value_reference", {})
        if all(item is None for item in probabilities):
            if intrinsic.get("expected_value") is not None:
                errors.append("expected value cannot be reported without approved probabilities")
        elif any(item is None for item in probabilities):
            errors.append("scenario probabilities must be supplied for every scenario or none")
        else:
            total = sum(float(item["value"]) for item in probabilities)
            bases = {(item["event_definition"], item["horizon"], item["as_of_date"]) for item in probabilities}
            if abs(total - 1) > 1e-9 or len(bases) != 1:
                errors.append("scenario probabilities must reconcile to one event, horizon, and as-of date")

    intrinsic = document.get("intrinsic_value_reference", {})
    scenario_values = intrinsic.get("scenario_values", [])
    values = [item.get("value") for item in scenario_values if _finite(item.get("value"))]
    if values:
        value_range = intrinsic.get("value_range", {})
        if not _close(value_range.get("low"), min(values)) or not _close(value_range.get("high"), max(values)):
            errors.append("intrinsic value range is inconsistent with complete scenario values")

    overlay = document.get("judgment_overlay", {})
    dimensions = overlay.get("dimension_assessments", [])
    if {item.get("dimension") for item in dimensions} != DIMENSIONS:
        errors.append("judgment overlay must contain all five evidence dimensions exactly once")
    for item in dimensions:
        if item.get("availability") == "not_available" and (item.get("signal") != "neutral" or item.get("band_implication") != "indeterminate" or item.get("evidence_refs")):
            errors.append("unavailable dimension must use the neutral serialization placeholder and cannot count as evidence")
        for ref in item.get("evidence_refs", []) + item.get("stale_evidence_refs", []) + item.get("counterevidence_refs", []):
            if ref not in evidence_by_id:
                errors.append(f"unknown evidence reference {ref} in dimension assessment")
    position = str(overlay.get("market_cycle_position"))
    expected_alignment = _alignment(position, dimensions)
    if overlay.get("alignment_count") != expected_alignment:
        errors.append("reported alignment count is inconsistent with recomputed dimension alignment")
    expected_confidence = _confidence(position, dimensions)
    if overlay.get("confidence") != expected_confidence:
        errors.append("reported confidence is inconsistent with governed evidence thresholds")
    if overlay.get("review_posture") != _posture(position):
        errors.append("review posture is inconsistent with the deterministic position mapping")
    implications = {item.get("band_implication") for item in dimensions if item.get("availability") == "available" and not item.get("stale_evidence_refs")}
    if {"extreme_low", "extreme_high"} <= implications and position != "indeterminate":
        errors.append("opposing extremes require an indeterminate market position")

    price = overlay.get("price_value_observation", {})
    if price.get("observed_after_intrinsic_value") is not True:
        errors.append("price-to-value ordering requires intrinsic value to be computed first")
    if _finite(price.get("market_price")) and _finite(price.get("intrinsic_value")) and float(price["intrinsic_value"]) != 0:
        if not _close(price.get("ratio"), float(price["market_price"]) / float(price["intrinsic_value"])):
            errors.append("price-to-intrinsic-value ratio cannot be recomputed")
    if price.get("evidence_ref") not in evidence_by_id:
        errors.append("price-to-value evidence reference is unknown")
    reference_values = {item.get("scenario_id"): item.get("value") for item in scenario_values}
    expected_overlay_value = intrinsic.get("expected_value")
    if expected_overlay_value is None:
        expected_overlay_value = reference_values.get("SCN-BASE", next(iter(reference_values.values()), None))
    if _finite(expected_overlay_value) and not _close(price.get("intrinsic_value"), float(expected_overlay_value)):
        errors.append("judgment overlay intrinsic value does not match the immutable precomputed reference")
    try:
        price_as_of = date.fromisoformat(str(price.get("as_of_date")))
    except ValueError:
        price_as_of = valuation_date
    expected_price_stale = (valuation_date - price_as_of).days > max_age
    if price.get("stale") != expected_price_stale:
        errors.append("price-to-value staleness is inconsistent with policy")
    if position in {"extreme_low", "extreme_high"}:
        by_dimension = {item.get("dimension"): item for item in dimensions}
        psych_or_risk = any(_aligned(position, by_dimension.get(name, {}).get("band_implication", "indeterminate")) and not by_dimension.get(name, {}).get("stale_evidence_refs") for name in ("psychology_valuation", "risk_attitude"))
        credit = by_dimension.get("credit", {})
        if price.get("stale") or credit.get("availability") != "available" or credit.get("stale_evidence_refs") or not psych_or_risk:
            errors.append("extreme position lacks non-stale price, credit, and psychology or risk evidence")

    risk = document.get("risk_controls", {})
    if risk.get("overlay_changes_intrinsic_value"):
        errors.append("judgment overlay cannot modify intrinsic value")
    if risk.get("hidden_numeric_score"):
        errors.append("hidden numeric score is prohibited")
    if risk.get("trade_instruction") is not None:
        errors.append("trade instruction or position size is prohibited")
    if risk.get("excluded_methods"):
        errors.append("excluded method cannot be imported into M6")
    if risk.get("m6_distress_adjustment"):
        errors.append("distress risk cannot be adjusted in both M6 and M5")
    if risk.get("distress_material"):
        handoff = risk.get("distress_handoff")
        if not isinstance(handoff, Mapping) or handoff.get("workflow_ref") != "WFL-DST-001":
            errors.append("material issuer distress requires exactly one WFL-DST-001 handoff")
    elif risk.get("distress_handoff") is not None:
        errors.append("immaterial distress cannot create an M5 handoff")

    handoff = document.get("valuation_input_handoff", {})
    if handoff.get("treatment_mode") != mode:
        errors.append("valuation-input handoff treatment mode does not match the selected treatment")
    if mode == "stop" and handoff.get("status") != "stopped":
        errors.append("stopped treatment cannot produce a valuation-input handoff")
    if mode != "stop" and handoff.get("status") != "produced":
        errors.append("selected treatment must produce its governed valuation-input handoff")

    trace = document.get("traceability", {})
    for ref in trace.get("source_refs", []):
        if ref not in source_ids:
            errors.append(f"unknown source reference {ref}")
    for ref in trace.get("claim_refs", []):
        if ref not in claim_ids:
            errors.append(f"unknown claim reference {ref}")
    for ref in trace.get("narrative_assertion_refs", []):
        if ref not in narrative_assertions:
            errors.append(f"unknown narrative assertion reference {ref}")
    return errors


def main() -> int:
    schema, sources, claims, narratives = load_registry(ROOT)
    paths = sorted(FIXTURE_ROOT.glob("*.json"))
    failures = 0
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_document(document, schema, sources, claims, narratives)
        if errors:
            failures += 1
            print(f"{path.relative_to(ROOT)}:")
            for error in errors:
                print(f"- {error}")
    if failures:
        return 1
    print(f"Validated {len(paths)} cycle-aware judgment document(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
