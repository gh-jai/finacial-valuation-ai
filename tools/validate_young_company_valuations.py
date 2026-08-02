"""Validate M3 young-company artifacts and cross-field valuation controls."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "benchmarks" / "fixtures" / "young_company"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.young_company import reconcile_probabilities


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_document(document: Mapping[str, Any], schema: Mapping[str, Any], source_ids: set[str], claim_ids: set[str], narrative_assertions: set[str]) -> list[str]:
    errors = [f"schema {'.'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document), key=lambda item: list(item.path))]
    failure = document.get("failure_scenario", {})
    adjustment = document.get("survival_adjustment", {})
    going = document.get("going_concern", {})
    forecast = document.get("forecast", {})
    bridge = document.get("equity_bridge", {})
    trace = document.get("traceability", {})
    try:
        probability_failure, probability_survival = reconcile_probabilities(failure.get("failure_probability"), failure.get("survival_probability"), tolerance=adjustment.get("probability_tolerance", 1e-9))
    except (TypeError, ValueError) as exc:
        errors.append(str(exc))
        probability_failure = probability_survival = math.nan
    for name, value in (("failure_value", failure.get("failure_value")), ("going_concern_value", going.get("operating_asset_value"))):
        if not _finite_number(value):
            errors.append(f"{name} must be finite")
    if failure.get("failure_value_basis") != "operating-assets":
        errors.append("failure value basis must match going-concern operating-assets basis")
    if not failure.get("recovery_basis"):
        errors.append("failure value requires a recovery rationale")
    controls = adjustment.get("double_counting_check", {})
    if controls.get("failure_premium_in_discount_rate") or controls.get("failure_loss_in_cash_flows") or not controls.get("passed"):
        errors.append("survival-risk double-counting control failed")
    if all(_finite_number(value) for value in (probability_failure, probability_survival, failure.get("failure_value"), going.get("operating_asset_value"))):
        survival_component = probability_survival * going["operating_asset_value"]
        failure_component = probability_failure * failure["failure_value"]
        adjusted = survival_component + failure_component
        if abs(adjustment.get("survival_component", math.nan) - survival_component) > 1e-8 or abs(adjustment.get("failure_component", math.nan) - failure_component) > 1e-8 or abs(adjustment.get("adjusted_operating_asset_value", math.nan) - adjusted) > 1e-8:
            errors.append("survival-adjustment arithmetic is inconsistent")
    rates = forecast.get("discount_rates", [])
    factors = going.get("cumulative_discount_factors", [])
    expected_factors: list[float] = []
    if isinstance(rates, list) and all(_finite_number(rate) and rate > -1 for rate in rates):
        cumulative = 1.0
        for rate in rates:
            cumulative *= 1 + rate
            expected_factors.append(1 / cumulative)
    if not isinstance(factors, list) or not all(_finite_number(value) for value in factors) or len(factors) != len(expected_factors) or any(abs(a-b) > 1e-10 for a, b in zip(factors, expected_factors)):
        errors.append("cumulative discount factors are inconsistent with period rates")
    if forecast.get("terminal_growth_rate", 0) >= forecast.get("terminal_discount_rate", 0):
        errors.append("terminal growth must be below terminal discount rate")
    margins = forecast.get("operating_margins", [])
    mature_year = forecast.get("mature_year", 0)
    if not margins or mature_year != len(margins):
        errors.append("margin convergence must explicitly end in the mature year")
    revenues, reinvestments = forecast.get("revenues", []), forecast.get("reinvestments", [])
    lag = forecast.get("reinvestment_lag_periods", 0)
    for index in range(1, len(revenues)):
        support_index = index - lag
        if revenues[index] > revenues[index-1] and support_index >= 0 and (support_index >= len(reinvestments) or reinvestments[support_index] <= 0):
            errors.append("forecast growth lacks reinvestment support")
            break
    dilution = bridge.get("future_financing_dilution_handling", {})
    if dilution.get("negative_fcff_present_value_included") and dilution.get("future_shares_added_to_current_denominator"):
        errors.append("future-share dilution double counts negative FCFF")
    option_value = bridge.get("option_and_other_equity_claim_value", 0)
    trace_names = {item.get("input_name") for item in forecast.get("assumption_trace", [])}
    if option_value and "option_and_other_equity_claim_value" not in trace_names:
        errors.append("option deduction requires explicit option valuation trace")
    if bridge.get("authorized_financing_proceeds", 0) and "authorized_financing_proceeds" not in trace_names:
        errors.append("financing proceeds require authorization trace")
    review = document.get("review", {})
    if review.get("status") == "unreviewed":
        errors.append("young-company valuation requires human review status")
    if review.get("status") in {"reviewed", "approved"} and (
        not review.get("risk_separation_approved") or not review.get("claim_structure_reviewed")
    ):
        errors.append("reviewed valuation requires risk-separation and claim-structure approval")
    for ref in trace.get("source_refs", []):
        if ref.startswith("SRC-") and ref not in source_ids:
            errors.append(f"unknown source reference {ref}")
    for ref in trace.get("claim_refs", []):
        if ref not in claim_ids:
            errors.append(f"unknown claim reference {ref}")
    for ref in trace.get("narrative_assertion_refs", []):
        if ref not in narrative_assertions:
            errors.append(f"unknown narrative assertion reference {ref}")
    key_person = document.get("key_person_scenario")
    if key_person is not None:
        key_values = (
            key_person.get("status_quo_value"), key_person.get("scenario_value"),
            key_person.get("discount_amount"),
        )
        if not all(_finite_number(value) for value in key_values) or abs(key_values[0] - key_values[1] - key_values[2]) > 1e-8:
            errors.append("key-person risk must use a separately valued operating scenario")
    return errors


def validate_repository(root: Path = ROOT) -> tuple[list[str], int]:
    schema = json.loads((root / "schemas/young-company-valuation.schema.json").read_text(encoding="utf-8"))
    catalog = yaml.safe_load((root / "sources/catalog.yaml").read_text(encoding="utf-8"))
    source_ids = {item["id"] for item in catalog["sources"]}
    claim_ids: set[str] = set()
    for path in (root / "extraction/reviewed").glob("*.yaml"):
        claim_ids.update(item["id"] for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"])
    narrative_assertions: set[str] = set()
    for path in (root / "benchmarks/fixtures/narratives").glob("*.json"):
        narrative_assertions.update(item["id"] for item in json.loads(path.read_text(encoding="utf-8"))["assertions"])
    errors: list[str] = []
    paths = sorted((root / "benchmarks/fixtures/young_company").glob("*.json"))
    ids: set[str] = set()
    narrative_claim_structures: set[tuple[str, float, float, float]] = set()
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("id") in ids:
            errors.append(f"{path.relative_to(root)}: duplicate valuation ID")
        ids.add(document.get("id"))
        bridge = document.get("equity_bridge", {})
        structure = (document.get("narrative_id"), bridge.get("debt_and_senior_claims", 0), bridge.get("option_and_other_equity_claim_value", 0), bridge.get("current_share_count", 0))
        if structure in narrative_claim_structures:
            errors.append(f"{path.relative_to(root)}: silently merged alternative or claim structure")
        narrative_claim_structures.add(structure)
        errors.extend(f"{path.relative_to(root)}: {error}" for error in validate_document(document, schema, source_ids, claim_ids, narrative_assertions))
    return errors, len(paths)


def main() -> int:
    try:
        errors, count = validate_repository()
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Young-company validation failed: {exc}")
        return 1
    if errors:
        print("Young-company validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {count} young-company valuation document(s) and control invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
