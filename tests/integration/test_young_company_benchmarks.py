import json
from pathlib import Path

import pytest

from tools.young_company import bridge_young_company_equity, run_going_concern_fcff, survival_adjustment


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("fixture_name,expected_name", [
    ("synthetic-software-platform.json", "young-software-platform-output.json"),
    ("synthetic-capital-intensive.json", "young-capital-intensive-output.json"),
])
def test_young_company_benchmark_is_deterministic(fixture_name: str, expected_name: str) -> None:
    fixture = json.loads((ROOT / "benchmarks/fixtures/young_company" / fixture_name).read_text(encoding="utf-8"))
    expected = json.loads((ROOT / "benchmarks/expected" / expected_name).read_text(encoding="utf-8"))
    forecast = fixture["forecast"]
    fcff, going = run_going_concern_fcff(forecast["revenues"], forecast["operating_margins"], forecast["tax_rates"], forecast["reinvestments"], forecast["discount_rates"], forecast["terminal_growth_rate"], forecast["terminal_discount_rate"])
    failure = fixture["failure_scenario"]
    adjusted = survival_adjustment(going.operating_asset_value, failure["failure_probability"], failure["survival_probability"], failure["failure_value"], failure_value_basis=failure["failure_value_basis"])
    bridge_data = fixture["equity_bridge"]
    bridge = bridge_young_company_equity(adjusted.adjusted_operating_asset_value, existing_cash=bridge_data["existing_cash"], authorized_financing_proceeds=bridge_data["authorized_financing_proceeds"], financing_authorized=bridge_data["authorized_financing_proceeds"] > 0, debt_and_senior_claims=bridge_data["debt_and_senior_claims"], option_and_other_equity_claim_value=bridge_data["option_and_other_equity_claim_value"], option_value_explicit=bridge_data["option_and_other_equity_claim_value"] > 0, current_share_count=bridge_data["current_share_count"])
    assert fcff == pytest.approx(expected["fcff"])
    assert going.operating_asset_value == pytest.approx(expected["going_concern_operating_value"])
    assert adjusted.adjusted_operating_asset_value == pytest.approx(expected["adjusted_operating_value"])
    assert bridge.per_share_value == pytest.approx(expected["per_share_value"])


def test_m1_and_m2_composition_regression() -> None:
    from tools.dcf import run_fcff_dcf
    from tools.narrative import load_narrative, value_narrative
    m1 = run_fcff_dcf([10, 11, 12], 0.1, 0.02)
    assert m1.operating_asset_value == pytest.approx(142.14876033057845)
    narrative = load_narrative(ROOT / "benchmarks/fixtures/narratives/synthetic-base.json")
    _, m2 = value_narrative(narrative)
    assert m2.per_share_value == pytest.approx(14.670223152576089)
