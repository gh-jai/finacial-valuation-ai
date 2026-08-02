import json
from pathlib import Path

import yaml

from tools.validate_growth_company_valuations import validate_document

ROOT = Path(__file__).resolve().parents[2]


def inputs() -> tuple[dict, dict, set[str], set[str], set[str]]:
    document = json.loads(
        (ROOT / "benchmarks/fixtures/growth_company/synthetic-capacity-expansion.json").read_text(
            encoding="utf-8"
        )
    )
    schema = json.loads(
        (ROOT / "schemas/growth-company-valuation.schema.json").read_text(encoding="utf-8")
    )
    catalog = yaml.safe_load((ROOT / "sources/catalog.yaml").read_text(encoding="utf-8"))
    sources = {item["id"] for item in catalog["sources"]}
    claims: set[str] = set()
    for path in (ROOT / "extraction/reviewed").glob("*.yaml"):
        claims.update(
            item["id"] for item in yaml.safe_load(path.read_text(encoding="utf-8"))["claims"]
        )
    assertions: set[str] = set()
    for path in (ROOT / "benchmarks/fixtures/narratives").glob("*.json"):
        assertions.update(
            item["id"] for item in json.loads(path.read_text(encoding="utf-8"))["assertions"]
        )
    return document, schema, sources, claims, assertions


def errors_for(document: dict) -> list[str]:
    _, schema, sources, claims, assertions = inputs()
    return validate_document(document, schema, sources, claims, assertions)


def test_valid_growth_company_document() -> None:
    document, _, _, _, _ = inputs()
    assert errors_for(document) == []


def test_m3_boundary_must_be_cleared() -> None:
    document, _, _, _, _ = inputs()
    document["growth_company_profile"]["m3_boundary_cleared"] = False
    assert any("M3-to-M4" in error for error in errors_for(document))


def test_stale_base_requires_normalization() -> None:
    document, _, _, _, _ = inputs()
    document["base_period"]["period_end"] = "2025-01-01"
    document["base_period"]["staleness_days"] = 365
    document["base_period"]["normalization_adjustments"] = []
    assert any("stale base period" in error for error in errors_for(document))


def test_unbounded_scale_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    del document["market_context"]
    assert any("unbounded" in error for error in errors_for(document))


def test_growth_without_reinvestment_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["forecast"]["reinvestments"][2] = 0
    assert any("reinvestments" in error for error in errors_for(document))


def test_overlapping_reinvestment_inputs_are_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["forecast"]["fundamental_reinvestment_rates"][2] = 0.5
    assert any("exactly one method input" in error for error in errors_for(document))


def test_capacity_holiday_cannot_exceed_supported_output() -> None:
    document, _, _, _, _ = inputs()
    document["capacity_holiday"]["maximum_supported_output"] = 600
    assert any("exceeds supported output" in error for error in errors_for(document))


def test_margin_jump_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["forecast"]["operating_margins"][0] = 0.16
    assert any("operating margins" in error for error in errors_for(document))


def test_constant_high_growth_risk_rate_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["forecast"]["discount_rates"] = [0.13] * 10
    document["stable_state"]["cost_of_capital"] = 0.13
    document["stable_state"]["excess_return"] = document["stable_state"]["return_on_capital"] - 0.13
    assert any("constant growth-company discount rate" in error for error in errors_for(document))


def test_terminal_fcff_must_be_rebuilt() -> None:
    document, _, _, _, _ = inputs()
    document["going_concern"]["terminal_fcff"] = document["going_concern"]["fcff"][-1] * 1.025
    assert any("terminal FCFF" in error for error in errors_for(document))


def test_stable_growth_below_cost_and_reinvestment_reconciliation() -> None:
    document, _, _, _, _ = inputs()
    document["stable_state"]["growth_rate"] = 0.09
    document["stable_state"]["reinvestment_rate"] = 0.8
    errors = errors_for(document)
    assert any("stable growth" in error for error in errors)
    assert any("stable reinvestment rate" in error for error in errors)


def test_failure_risk_double_counting_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["failure_handoff"]["failure_premium_in_discount_rate"] = True
    assert any("double counted" in error for error in errors_for(document))


def test_future_share_dilution_double_counting_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["equity_bridge_handoff"]["future_shares_added_to_current_denominator"] = True
    assert any("future-share dilution" in error for error in errors_for(document))


def test_market_price_cannot_change_the_base_case() -> None:
    document, _, _, _, _ = inputs()
    document["sensitivity"]["base_case_unchanged"] = False
    assert any("base_case_unchanged" in error for error in errors_for(document))


def test_unknown_traceability_references_are_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["traceability"]["source_refs"] = ["SRC-UNKNOWN"]
    document["traceability"]["claim_refs"] = ["CLM-GRW-999"]
    document["traceability"]["narrative_assertion_refs"] = ["NAR-A-999"]
    errors = errors_for(document)
    assert any("unknown source" in error for error in errors)
    assert any("unknown claim" in error for error in errors)
    assert any("unknown narrative assertion" in error for error in errors)


def test_non_prefixed_unknown_source_reference_is_rejected() -> None:
    document, _, _, _, _ = inputs()
    document["traceability"]["source_refs"] = ["NOT-A-REGISTERED-SOURCE"]
    assert any("unknown source" in error for error in errors_for(document))


def test_unknown_assumption_assertion_is_rejected_bidirectionally() -> None:
    document, _, _, _, _ = inputs()
    document["forecast"]["assumption_trace"][0]["assertion_id"] = "NAR-A-999"
    errors = errors_for(document)
    assert any("unknown assumption assertion" in error for error in errors)
    assert any("must match" in error for error in errors)


def test_market_growth_series_is_recomputed() -> None:
    document, _, _, _, _ = inputs()
    document["market_context"]["market_growth_rates"][3] = 0.04
    assert any("addressable market" in error for error in errors_for(document))


def test_capacity_utilization_series_is_recomputed() -> None:
    document, _, _, _, _ = inputs()
    document["capacity_holiday"]["utilization_rates"][0] = 0.5
    assert any("capacity utilization" in error for error in errors_for(document))


def test_calculation_trail_is_recomputed() -> None:
    document, _, _, _, _ = inputs()
    document["going_concern"]["calculation_trail"][0]["value"] += 1
    assert any("calculation trail" in error for error in errors_for(document))


def test_sensitivity_grid_is_recomputed() -> None:
    document, _, _, _, _ = inputs()
    document["sensitivity"]["driver_grid"][0]["operating_asset_value"] += 1
    assert any("sensitivity scenario" in error for error in errors_for(document))


def test_break_even_value_is_recomputed() -> None:
    document, _, _, _, _ = inputs()
    document["sensitivity"]["break_even_values"][0]["value"] += 0.1
    assert any("break-even driver" in error for error in errors_for(document))
