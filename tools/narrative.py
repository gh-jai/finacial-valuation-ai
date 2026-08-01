"""Narrative-to-FCFF mapping that composes with the M1 DCF engine."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker

from tools.dcf import DCFResult, forecast_fcff, run_fcff_dcf


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_INPUTS = {
    "revenues",
    "operating_margins",
    "tax_rates",
    "reinvestments",
    "discount_rate",
    "failure_probability",
    "terminal_growth_rate",
}


def load_narrative(path: Path, schema_path: Path | None = None) -> dict[str, Any]:
    """Load and schema-validate one narrative JSON document."""
    document = json.loads(path.read_text(encoding="utf-8"))
    schema_file = schema_path or ROOT / "schemas" / "narrative.schema.json"
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document),
        key=lambda item: list(item.path),
    )
    if errors:
        raise ValueError(f"invalid narrative {path}: {errors[0].message}")
    return document


def extract_fcff_input_contract(narrative: Mapping[str, Any]) -> dict[str, Any]:
    """Translate mapped assertions into one explicit, traceable M1 DCF input contract."""
    mappings = narrative.get("value_driver_mappings", [])
    by_name: dict[str, dict[str, Any]] = {}
    for mapping in mappings:
        name = mapping["input_name"]
        if name in by_name:
            raise ValueError(f"duplicate mapped input: {name}")
        by_name[name] = mapping
    missing = sorted(REQUIRED_INPUTS - by_name.keys())
    if missing:
        raise ValueError(f"missing material narrative mappings: {', '.join(missing)}")

    cash_flows = forecast_fcff(
        by_name["revenues"]["value"],
        by_name["operating_margins"]["value"],
        by_name["tax_rates"]["value"],
        by_name["reinvestments"]["value"],
    )
    contract: dict[str, Any] = {
        "narrative_id": narrative["id"],
        "cash_flows": list(cash_flows),
        "discount_rate": deepcopy(by_name["discount_rate"]["value"]),
        "terminal_growth_rate": by_name["terminal_growth_rate"]["value"],
        "failure_probability": by_name["failure_probability"]["value"],
        "traceability": {},
    }
    for optional in (
        "terminal_discount_rate",
        "cash_and_non_operating_assets",
        "debt_and_debt_like_claims",
        "share_count",
    ):
        if optional in by_name:
            contract[optional] = deepcopy(by_name[optional]["value"])
    for name, mapping in by_name.items():
        contract["traceability"][name] = {
            "assertion_id": mapping["assertion_id"],
            "evidence_refs": list(mapping["evidence_refs"]),
            "rationale": mapping["rationale"],
        }
    return contract


def value_narrative(narrative: Mapping[str, Any]) -> tuple[dict[str, Any], DCFResult]:
    """Map one narrative and run the existing M1 FCFF DCF implementation."""
    contract = extract_fcff_input_contract(narrative)
    kwargs = {
        key: contract[key]
        for key in (
            "terminal_discount_rate",
            "cash_and_non_operating_assets",
            "debt_and_debt_like_claims",
            "share_count",
        )
        if key in contract
    }
    result = run_fcff_dcf(
        contract["cash_flows"],
        contract["discount_rate"],
        contract["terminal_growth_rate"],
        **kwargs,
    )
    return contract, result


def value_narrative_set(
    current: Mapping[str, Any], alternatives: Sequence[Mapping[str, Any]]
) -> dict[str, tuple[dict[str, Any], DCFResult]]:
    """Value current and active alternatives as isolated input sets."""
    expected = {
        item["narrative_id"] for item in current.get("alternatives", []) if item["status"] == "active"
    }
    supplied = {item["id"] for item in alternatives}
    if current["id"] in supplied:
        raise ValueError("alternative narrative ID must differ from the current narrative ID")
    if expected != supplied:
        raise ValueError("active alternatives must be supplied separately and exactly once")
    documents = [current, *alternatives]
    if len({item["id"] for item in documents}) != len(documents):
        raise ValueError("silently merged or duplicate alternative narrative")
    return {item["id"]: value_narrative(item) for item in documents}
