import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from tools.dcf import run_dcf_sensitivity, run_fcff_dcf, to_valuation_output


ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_fixture(fixture: dict):
    return run_fcff_dcf(
        fixture["cash_flows"],
        fixture["discount_rate"],
        fixture["terminal_growth_rate"],
        terminal_discount_rate=fixture.get("terminal_discount_rate"),
        cash_and_non_operating_assets=fixture.get("cash_and_non_operating_assets", 0.0),
        debt_and_debt_like_claims=fixture.get("debt_and_debt_like_claims", 0.0),
        share_count=fixture.get("share_count"),
    )


@pytest.mark.parametrize("stem", ["basic-dcf", "varying-rate-dcf"])
def test_synthetic_benchmark_outputs_and_structured_schema(stem: str) -> None:
    fixture = load_json(ROOT / "benchmarks" / "fixtures" / f"{stem}-input.json")
    expected = load_json(ROOT / "benchmarks" / "expected" / f"{stem}-output.json")
    result = run_fixture(fixture)
    tolerance = expected["tolerance"]

    for field in (
        "forecast_present_value",
        "terminal_value",
        "terminal_present_value",
    ):
        assert getattr(result, field) == pytest.approx(expected[field], abs=tolerance)
    expected_operating_value = expected.get("operating_asset_value")
    if expected_operating_value is None:
        expected_operating_value = expected["enterprise_value"]
    assert result.operating_asset_value == pytest.approx(expected_operating_value, abs=tolerance)
    for optional_field in ("equity_value", "per_share_value"):
        if optional_field in expected:
            assert getattr(result, optional_field) == pytest.approx(
                expected[optional_field], abs=tolerance
            )
    if "cumulative_discount_factors" in expected:
        assert result.cumulative_discount_factors == pytest.approx(
            expected["cumulative_discount_factors"], abs=tolerance
        )

    sensitivity = run_dcf_sensitivity(
        fixture["cash_flows"], fixture["discount_rate"], [0.09, 0.10], [0.01, 0.02]
    )
    output = to_valuation_output(
        result,
        as_of_date=fixture["as_of_date"],
        subject=fixture["subject"],
        currency=fixture["currency"],
        evidence_refs=fixture["evidence_refs"],
        limitations=fixture["limitations"],
        sensitivity=sensitivity,
    )
    schema = load_json(ROOT / "schemas" / "valuation-output.schema.json")
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(output))
    assert errors == []
    assert output["review"]["status"] == "unreviewed"
    assert output["calculation_trail"]


def test_benchmark_enforces_terminal_growth_boundary() -> None:
    fixture = load_json(ROOT / "benchmarks" / "fixtures" / "basic-dcf-input.json")
    fixture["terminal_growth_rate"] = fixture["terminal_discount_rate"]
    with pytest.raises(ValueError, match="terminal_growth_rate"):
        run_fixture(fixture)
