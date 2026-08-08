import copy
import json
from pathlib import Path

import pytest

from tools.validate_agent_runs import load_registry, validate_document

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "benchmarks/fixtures/agentization"


def load(name: str = "synthetic-happy-path.json") -> tuple[dict, tuple]:
    document = json.loads((FIXTURES / name).read_text(encoding="utf-8"))
    return document, load_registry(ROOT)


def errors_for(document: dict, registry: tuple) -> list[str]:
    return validate_document(document, *registry)


def test_all_agent_run_fixtures_validate() -> None:
    for path in sorted(FIXTURES.glob("*.json")):
        document, registry = load(path.name)
        assert errors_for(document, registry) == []


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda d: d["artifacts"][0].update(payload_hash="0" * 64), "forged payload hash"),
        (lambda d: d.update(status="memo_rendered"), "reported state"),
        (lambda d: d["events"][4].update(event_type="memo_rendered"), "illegal transition"),
        (lambda d: d["events"][2].update(parent_event_id="EVT-X"), "broken parent"),
        (lambda d: d["approvals"][0].update(actor_type="human", actor_id="AGT-ORC-001"), "not human"),
        (lambda d: d["approvals"][0].update(payload_hash="1" * 64), "stale"),
        (lambda d: d["tool_calls"][0].update(tool_id="TL-UNKNOWN"), "unknown agent or tool"),
        (lambda d: d["tool_calls"][0].update(prompt_id="PRM-ORC-001"), "wrong prompt"),
        (lambda d: d["budgets"].update(used_actions=2), "used action budget"),
        (lambda d: d["events"][6].update(actor_id="AGT-VAL-001"), "not separated"),
        (lambda d: d["artifacts"][1]["payload"].update(trade_instruction="buy"), "trade instruction"),
    ],
)
def test_happy_path_adversarial_mutations(mutation, message: str) -> None:
    document, registry = load()
    mutation(document)
    assert any(message in error for error in errors_for(document, registry))


def test_blocked_case_cannot_smuggle_a_valuation_output() -> None:
    document, registry = load("synthetic-adversarial-stop.json")
    happy, _ = load()
    document["artifacts"].append(copy.deepcopy(happy["artifacts"][1]))
    assert any("stop before valuation" in error for error in errors_for(document, registry))


def test_tampered_case_cannot_retain_active_old_approval() -> None:
    document, registry = load("synthetic-approval-tampering.json")
    document["approvals"][0].update(status="active", invalidated_at=None)
    assert any("stale" in error for error in errors_for(document, registry))
