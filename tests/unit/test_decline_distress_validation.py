import copy
import json
from pathlib import Path

import yaml

from tools.validate_decline_distress_valuations import validate_document

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads(
    (ROOT / "schemas/decline-distress-valuation.schema.json").read_text(encoding="utf-8")
)
CATALOG = yaml.safe_load((ROOT / "sources/catalog.yaml").read_text(encoding="utf-8"))
SOURCE_IDS = {item["id"] for item in CATALOG["sources"]}
CLAIM_IDS = {
    item["id"]
    for path in (ROOT / "extraction/reviewed").glob("*.yaml")
    for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"]
}
NARRATIVE_ASSERTIONS = {
    item["id"]
    for path in (ROOT / "benchmarks/fixtures/narratives").glob("*.json")
    for item in json.loads(path.read_text(encoding="utf-8"))["assertions"]
}


def load(name: str) -> dict:
    return json.loads(
        (ROOT / "benchmarks/fixtures/decline_distress" / name).read_text(encoding="utf-8")
    )


def errors_for(document: dict) -> list[str]:
    return validate_document(document, SCHEMA, SOURCE_IDS, CLAIM_IDS, NARRATIVE_ASSERTIONS)


def orderly() -> dict:
    return load("synthetic-orderly-legacy-distributor.json")


def distressed() -> dict:
    return load("synthetic-levered-service-operator.json")


def test_both_benchmarks_pass_all_controls() -> None:
    assert errors_for(orderly()) == []
    assert errors_for(distressed()) == []


def test_one_weak_period_cannot_clear_decline_boundary() -> None:
    document = orderly()
    document["decline_profile"]["decline_evidence"] = ["One weak period"]
    assert any("life-cycle boundary" in error or "too short" in error for error in errors_for(document))


def test_quadrant_is_recomputed_from_independent_classifications() -> None:
    document = orderly()
    document["routing"]["quadrant"] = "reversible_low"
    errors = errors_for(document)
    assert any("quadrant conflicts" in error for error in errors)
    assert any("turnaround_case" in error for error in errors)


def test_base_normalization_is_recomputed_from_reported_values() -> None:
    document = orderly()
    document["base_period"]["continuing_revenues"] += 1
    assert any("normalized base continuing_revenues" in error for error in errors_for(document))


def test_negative_reinvestment_requires_equal_governed_support() -> None:
    document = orderly()
    document["status_quo_forecast"]["negative_reinvestment_support"][0][
        "capital_reduction"
    ] = 60
    assert any("equal documented capital release" in error for error in errors_for(document))


def test_divestiture_capital_and_proceeds_reconcile_to_negative_reinvestment() -> None:
    document = orderly()
    document["divestitures"][0]["capital_removed"] -= 1
    document["divestitures"][1]["net_sale_proceeds"] -= 1
    errors = errors_for(document)
    assert any("capital reduction conflicts" in error for error in errors)
    assert any("recognize divestiture proceeds once" in error for error in errors)


def test_unsupported_negative_reinvestment_is_rejected() -> None:
    document = distressed()
    document["status_quo_forecast"]["negative_reinvestment_support"] = []
    assert any("every negative reinvestment" in error for error in errors_for(document))


def test_divestiture_proceeds_and_disposed_operations_are_recomputed() -> None:
    document = orderly()
    document["divestitures"][0]["net_sale_proceeds"] += 1
    document["divestitures"][1]["remaining_operating_income"] += 1
    errors = errors_for(document)
    assert any("net proceeds" in error for error in errors)
    assert any("retains disposed operating income" in error for error in errors)


def test_divestiture_proceeds_cannot_be_added_twice() -> None:
    document = orderly()
    document["divestitures"][0]["proceeds_in_separate_cash_flow"] = True
    assert any("duplicates proceeds" in error for error in errors_for(document))


def test_every_divestiture_requires_one_same_year_negative_reinvestment_link() -> None:
    document = orderly()
    orphan = copy.deepcopy(document["divestitures"][0])
    orphan["id"] = "DIV-ORPHAN"
    document["divestitures"].append(orphan)
    assert any("exactly one same-year negative-reinvestment support" in error for error in errors_for(document))


def test_loss_period_tax_benefit_is_recomputed_at_zero() -> None:
    document = distressed()
    document["financing_path"]["cash_interest_tax_benefits"][0] = -1
    errors = errors_for(document)
    assert any("cash interest tax benefits" in error for error in errors)


def test_face_debt_market_weights_and_wacc_are_recomputed() -> None:
    document = distressed()
    document["financing_path"]["closing_face_debt"][0] += 1
    document["financing_path"]["debt_to_capital_ratios"][0] = 0.5
    document["financing_path"]["costs_of_capital"][0] += 0.01
    errors = errors_for(document)
    assert any("closing face debt" in error for error in errors)
    assert any("debt-to-capital" in error for error in errors)
    assert any("costs of capital" in error for error in errors)


def test_forecast_discount_rates_must_equal_financing_wacc() -> None:
    document = orderly()
    document["status_quo_forecast"]["discount_rates"][0] += 0.01
    assert any("forecast discount rates" in error for error in errors_for(document))


def test_full_orderly_liquidation_cannot_be_a_closure_mode() -> None:
    document = orderly()
    document["closure"]["mode"] = "orderly_liquidation"
    errors = errors_for(document)
    assert any("closure" in error and "not one of" in error for error in errors)


def test_terminal_or_closure_value_is_recomputed() -> None:
    document = orderly()
    document["going_concern"]["terminal_or_closure_value"] += 1
    assert any("terminal or closure value" in error for error in errors_for(document))


def test_terminal_cost_must_converge_from_financing_path() -> None:
    document = orderly()
    document["closure"]["terminal_cost_of_capital"] += 0.01
    assert any("does not converge" in error for error in errors_for(document))


def test_turnaround_values_are_weighted_without_input_averaging() -> None:
    document = distressed()
    document["turnaround_case"]["turnaround_component"] += 1
    document["turnaround_case"]["no_input_averaging"] = False
    errors = errors_for(document)
    assert any("turnaround component" in error for error in errors)
    assert any("no_input_averaging" in error for error in errors)


def test_turnaround_probability_date_cannot_be_later_than_valuation_date() -> None:
    document = distressed()
    document["turnaround_case"]["probability_as_of_date"] = "2026-01-02"
    assert any("turnaround probability date is later than valuation date" in error for error in errors_for(document))


def test_probability_event_horizon_date_and_mapping_are_governed() -> None:
    document = distressed()
    document["distress_case"]["probability_horizon_years"] = 2
    document["distress_case"]["probability_as_of_date"] = "2026-01-02"
    document["distress_case"]["default_to_cessation_mapping"] = None
    errors = errors_for(document)
    assert any("horizon" in error for error in errors)
    assert any("later than valuation date" in error for error in errors)
    assert any("event-to-cessation mapping" in error for error in errors)


def test_orderly_liquidation_schedule_years_are_recomputed() -> None:
    document = orderly()
    document["orderly_liquidation"]["sale_schedule"][1]["year"] = 3
    assert any("schedule years" in error for error in errors_for(document))


def test_partial_liquidation_must_use_governed_divestitures_in_retained_operations() -> None:
    document = orderly()
    document["orderly_liquidation"]["full_liquidation"] = False
    errors = errors_for(document)
    assert any("partial liquidation must be modeled" in error for error in errors)


def test_distress_probability_and_rate_premium_cannot_be_stacked() -> None:
    document = distressed()
    document["distress_case"]["distress_premium_in_discount_rates"] = True
    errors = errors_for(document)
    assert any("double counted" in error or "False was expected" in error for error in errors)


def test_book_assets_require_impairment_and_forced_sale_adjustments() -> None:
    document = distressed()
    case = document["distress_case"]
    case["recovery_method"] = "adjusted_book_assets"
    case["existing_asset_after_tax_income"] = None
    case["existing_asset_cost_of_capital"] = None
    case["eligible_book_assets"] = 500
    case["economic_impairment"] = None
    case["forced_sale_discount"] = None
    assert any("adjusted-book-assets" in error for error in errors_for(document))


def test_distress_sale_methods_cannot_overlap() -> None:
    document = distressed()
    document["distress_case"]["haircut"] = 0.2
    assert any("overlapping recovery-method" in error for error in errors_for(document))


def test_alternative_values_must_share_one_basis() -> None:
    document = distressed()
    document["turnaround_case"]["basis"] = "firm"
    assert any("basis conflicts" in error for error in errors_for(document))


def test_claim_bridge_uses_current_market_debt_once() -> None:
    document = distressed()
    document["claim_bridge"]["market_value_debt"] = document["base_period"]["book_debt"]
    document["claim_bridge"]["input_value"] -= 10
    errors = errors_for(document)
    assert any("current cash and market debt" in error for error in errors)
    assert any("applicable common-basis value" in error for error in errors)


def test_common_equity_basis_forbids_a_second_claim_bridge() -> None:
    document = distressed()
    document["going_concern"]["basis"] = "common-equity"
    document["turnaround_case"]["basis"] = "common-equity"
    document["distress_case"]["aggregation_basis"] = "common-equity"
    document["claim_bridge"]["input_basis"] = "common-equity"
    assert any("common-equity aggregation basis forbids a claim bridge" in error for error in errors_for(document))


def test_calculation_trails_are_independently_recomputed() -> None:
    document = distressed()
    document["going_concern"]["calculation_trail"][0]["value"] += 1
    document["distress_case"]["calculation_trail"][0]["value"] += 1
    document["claim_bridge"]["calculation_trail"][0]["value"] += 1
    errors = errors_for(document)
    assert any("going-concern calculation trail" in error for error in errors)
    assert any("contingent-survival trail" in error for error in errors)
    assert any("claim-bridge trail" in error for error in errors)


def test_unknown_and_one_way_traceability_are_rejected() -> None:
    document = distressed()
    document["traceability"]["source_refs"] = ["SRC-UNKNOWN"]
    document["traceability"]["claim_refs"] = ["CLM-DST-999"]
    document["traceability"]["narrative_assertion_refs"] = ["NAR-A-999"]
    errors = errors_for(document)
    assert any("unknown source" in error for error in errors)
    assert any("unknown claim" in error for error in errors)
    assert any("unknown narrative assertion" in error for error in errors)
    assert any("must match" in error for error in errors)


def test_excluded_method_output_is_an_undeclared_property() -> None:
    document = copy.deepcopy(distressed())
    document["simulation_value"] = 123
    assert any("Additional properties" in error for error in errors_for(document))
