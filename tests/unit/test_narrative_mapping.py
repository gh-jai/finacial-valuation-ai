import copy
import json
from pathlib import Path

import pytest

from tools.narrative import extract_fcff_input_contract, load_narrative, value_narrative_set


ROOT = Path(__file__).resolve().parents[2]
NARRATIVES = ROOT / "benchmarks/fixtures/narratives"


def test_narrative_maps_to_traceable_fcff_contract() -> None:
    base = load_narrative(NARRATIVES / "synthetic-base.json")
    contract = extract_fcff_input_contract(base)
    assert contract["cash_flows"] == pytest.approx([3.0, 4.76, 6.88])
    assert set(contract["traceability"]) >= {"revenues", "operating_margins", "reinvestments", "discount_rate", "failure_probability", "terminal_growth_rate"}
    assert all(item["assertion_id"] and item["evidence_refs"] for item in contract["traceability"].values())


def test_missing_material_mapping_is_rejected() -> None:
    base = load_narrative(NARRATIVES / "synthetic-base.json")
    base["value_driver_mappings"] = [item for item in base["value_driver_mappings"] if item["input_name"] != "failure_probability"]
    with pytest.raises(ValueError, match="missing material narrative mappings"):
        extract_fcff_input_contract(base)


def test_alternative_narratives_are_isolated() -> None:
    base = load_narrative(NARRATIVES / "synthetic-base.json")
    alternative = load_narrative(NARRATIVES / "synthetic-alternative.json")
    values = value_narrative_set(base, [alternative])
    assert set(values) == {base["id"], alternative["id"]}
    assert values[base["id"]][0]["cash_flows"] != values[alternative["id"]][0]["cash_flows"]
    assert values[base["id"]][1].per_share_value != values[alternative["id"]][1].per_share_value


def test_silently_merged_alternative_is_rejected() -> None:
    base = load_narrative(NARRATIVES / "synthetic-base.json")
    merged = copy.deepcopy(base)
    with pytest.raises(ValueError, match="must differ"):
        value_narrative_set(base, [merged])
