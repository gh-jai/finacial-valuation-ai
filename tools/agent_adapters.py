"""Allowlisted offline adapters for M7 governed agent runs."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from tools.validate_cycle_aware_judgments import load_registry, validate_document

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_CYCLE_FIXTURES = {
    "synthetic-established-cycle-industrial": (
        ROOT / "benchmarks/fixtures/cycle_aware/synthetic-established-cycle-industrial.json"
    )
}


class AdapterRegistry:
    """In-memory adapter map whose policy registry remains explicit and inspectable."""

    def __init__(self, policy_registry: Mapping[str, Any]) -> None:
        self.policy_registry = copy.deepcopy(dict(policy_registry))
        self._adapters: dict[str, Callable[[Mapping[str, Any]], Mapping[str, Any]]] = {}

    def register(
        self, tool_id: str, adapter: Callable[[Mapping[str, Any]], Mapping[str, Any]]
    ) -> None:
        registered_tools = {item["tool_id"] for item in self.policy_registry.get("tools", [])}
        if tool_id not in registered_tools:
            raise ValueError(f"cannot register unknown tool {tool_id}")
        self._adapters[tool_id] = adapter

    def invoke(self, tool_id: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if tool_id not in self._adapters:
            raise PermissionError(f"tool {tool_id} has no registered adapter")
        return copy.deepcopy(dict(self._adapters[tool_id](copy.deepcopy(dict(payload)))))


def read_approved_artifact(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    artifact = payload.get("artifact")
    approval = payload.get("approval")
    if not isinstance(artifact, Mapping) or not isinstance(approval, Mapping):
        raise TypeError("approved-artifact envelope is incomplete")
    calculated = hashlib.sha256(
        json.dumps(
            artifact.get("payload"), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()
    if (
        artifact.get("payload_hash") != calculated
        or approval.get("payload_hash") != calculated
        or approval.get("artifact_id") != artifact.get("artifact_id")
        or approval.get("actor_type") != "human"
        or approval.get("status") != "active"
    ):
        raise PermissionError("artifact is not covered by an active exact-hash human approval")
    return copy.deepcopy(dict(artifact["payload"]))


def execute_cycle_fixture(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    fixture_id = payload.get("fixture_id")
    if fixture_id not in ALLOWED_CYCLE_FIXTURES:
        raise ValueError("fixture_id is not in the M7 allowlist")
    path = ALLOWED_CYCLE_FIXTURES[str(fixture_id)]
    document = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_document(document, *load_registry(ROOT))
    if errors:
        raise ValueError("cycle fixture failed independent validation: " + "; ".join(errors))
    if payload.get("valuation_id") != document.get("valuation_id"):
        raise ValueError("approved case valuation_id does not match the fixture")
    return {
        "workflow_id": "WFL-CYC-001",
        "fixture_id": fixture_id,
        "valuation_id": document["valuation_id"],
        "valuation_date": document["valuation_date"],
        "company": document["company"],
        "intrinsic_value_reference": document["intrinsic_value_reference"],
        "judgment_overlay": {
            "market_cycle_position": document["judgment_overlay"]["market_cycle_position"],
            "confidence": document["judgment_overlay"]["confidence"],
            "review_posture": document["judgment_overlay"]["review_posture"],
        },
        "deterministic_validation": {"validator": "validate_cycle_aware_judgments", "passed": True},
        "limitations": list(document["limitations"]),
        "trade_instruction": None,
    }


def render_approved_memo(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    required = {"valuation_id", "intrinsic_value_reference", "limitations"}
    if not required <= payload.keys():
        raise ValueError("validated output is incomplete for memo rendering")
    if payload.get("trade_instruction") is not None:
        raise ValueError("memo rendering refuses trading instructions")
    return {
        "title": f"Governed valuation memo - {payload['valuation_id']}",
        "valuation_id": payload["valuation_id"],
        "intrinsic_value_reference": copy.deepcopy(payload["intrinsic_value_reference"]),
        "judgment_overlay": copy.deepcopy(payload.get("judgment_overlay")),
        "limitations": list(payload["limitations"]),
        "non_advice_notice": "Research workflow output; not investment advice or a trade instruction.",
    }
