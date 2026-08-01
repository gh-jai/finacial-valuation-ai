import json
from pathlib import Path

import pytest

from tools.narrative import load_narrative, value_narrative, value_narrative_set


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "benchmarks/fixtures"
EXPECTED = ROOT / "benchmarks/expected"


def test_base_and_alternative_benchmark_is_deterministic() -> None:
    case = json.loads((FIXTURES / "narrative-base-with-alternative.json").read_text(encoding="utf-8"))
    expected = json.loads((EXPECTED / "narrative-base-with-alternative-output.json").read_text(encoding="utf-8"))
    base = load_narrative(FIXTURES / case["current"])
    alternatives = [load_narrative(FIXTURES / path) for path in case["alternatives"]]
    values = value_narrative_set(base, alternatives)
    base_contract, base_value = values[base["id"]]
    alt_value = values[alternatives[0]["id"]][1]
    assert base["three_p"]["overall"] == expected["three_p_result"]
    assert base_contract["cash_flows"] == pytest.approx(expected["mapped_fcff_assumptions"]["cash_flows"])
    assert base_value.per_share_value == pytest.approx(expected["valuation_output"]["per_share_value"])
    assert alt_value.per_share_value == pytest.approx(expected["alternative"]["per_share_value"])


def test_feedback_revision_benchmark_preserves_history_and_value_delta() -> None:
    case = json.loads((FIXTURES / "narrative-feedback-revision.json").read_text(encoding="utf-8"))
    expected = json.loads((EXPECTED / "narrative-feedback-revision-output.json").read_text(encoding="utf-8"))
    prior = load_narrative(FIXTURES / case["prior"])
    revised = load_narrative(FIXTURES / case["revised"])
    _, prior_value = value_narrative(prior)
    revised_contract, revised_value = value_narrative(revised)
    assert len(revised["revision_history"]) == 2
    assert revised["revision_history"][-1]["classification"] == expected["revision_classification"]
    assert revised_contract["cash_flows"] == pytest.approx(expected["mapped_fcff_assumptions"]["cash_flows"])
    assert revised_value.per_share_value - prior_value.per_share_value == pytest.approx(expected["revision_delta"])
