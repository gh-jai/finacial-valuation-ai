import copy
import json
from pathlib import Path

import pytest
import yaml

from tools.agent_adapters import (
    AdapterRegistry,
    execute_cycle_fixture,
    read_approved_artifact,
)
from tools.agent_adapters import (
    render_approved_memo as memo_adapter,
)
from tools.agent_runtime import (
    add_artifact,
    authorize_action,
    bind_human_approval,
    canonical_json,
    derive_state,
    execute_approved_workflow,
    invalidate_stale_approvals,
    payload_hash,
    render_approved_memo,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "benchmarks/fixtures/agentization"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def registry() -> dict:
    return yaml.safe_load((ROOT / "agentization/registry.yaml").read_text(encoding="utf-8"))


def test_canonical_hash_is_order_independent_and_unicode_preserving() -> None:
    left = {"b": 2, "a": {"中文": True, "items": [3, 1]}}
    right = {"a": {"items": [3, 1], "中文": True}, "b": 2}
    assert canonical_json(left) == canonical_json(right)
    assert payload_hash(left) == payload_hash(right)
    assert len(payload_hash(left)) == 64


def test_state_is_derived_from_parent_linked_legal_events() -> None:
    happy = load("synthetic-happy-path.json")
    assert derive_state(happy["events"]) == "completed"
    broken = copy.deepcopy(happy["events"])
    broken[4]["event_type"] = "memo_rendered"
    with pytest.raises(ValueError, match="illegal transition"):
        derive_state(broken)
    broken = copy.deepcopy(happy["events"])
    broken[2]["parent_event_id"] = "EVT-UNKNOWN"
    with pytest.raises(ValueError, match="broken parent"):
        derive_state(broken)


def test_only_identified_human_can_bind_exact_case_hash() -> None:
    happy = load("synthetic-happy-path.json")
    run = copy.deepcopy(happy)
    run["events"] = run["events"][:3]
    run["status"] = "awaiting_case_lock"
    run["artifacts"] = run["artifacts"][:1]
    run["approvals"] = []
    approved = bind_human_approval(
        run, "case_lock", "ART-CASE-HAPPY", "human-reviewer", "2026-08-08T01:00:00Z"
    )
    assert approved["status"] == "case_locked"
    assert approved["approvals"][0]["payload_hash"] == run["artifacts"][0]["payload_hash"]
    with pytest.raises(ValueError, match="identified human"):
        bind_human_approval(run, "case_lock", "ART-CASE-HAPPY", "AGT-ORC-001")


def test_case_revision_invalidates_old_approval_and_returns_to_gate() -> None:
    happy = load("synthetic-happy-path.json")
    run = copy.deepcopy(happy)
    run["events"] = run["events"][:4]
    run["status"] = "case_locked"
    run["artifacts"] = run["artifacts"][:1]
    run["approvals"] = run["approvals"][:1]
    revised = copy.deepcopy(run["artifacts"][0]["payload"])
    revised["assumptions"]["synthetic_only"] = False
    run = add_artifact(
        run,
        "ART-CASE-HAPPY",
        "case",
        revised,
        "AGT-EVD-001",
        "2026-08-08T01:01:00Z",
    )
    run = invalidate_stale_approvals(run, "2026-08-08T01:02:00Z")
    assert run["status"] == "awaiting_case_lock"
    assert run["approvals"][0]["status"] == "invalidated"
    decision = authorize_action(
        registry(), run, "AGT-VAL-001", "execute_workflow", "TL-CYCLE-FIXTURE", "ART-CASE-HAPPY"
    )
    assert not decision.allowed
    assert decision.code == "state_denied"


def test_authorization_denies_unknown_action_tool_and_exhausted_budget() -> None:
    tamper = load("synthetic-approval-tampering.json")
    assert authorize_action(registry(), tamper, "AGT-UNKNOWN", "derive_state").code == "unknown_agent"
    assert authorize_action(registry(), tamper, "AGT-EVD-001", "execute_workflow").code == "action_denied"
    assert authorize_action(
        registry(), tamper, "AGT-ORC-001", "derive_state", "TL-CYCLE-FIXTURE"
    ).code == "tool_denied"
    exhausted = copy.deepcopy(tamper)
    exhausted["budgets"] = {"max_actions": 2, "used_actions": 2}
    assert authorize_action(registry(), exhausted, "AGT-ORC-001", "derive_state").code == "budget_exhausted"


def test_approved_workflow_uses_only_registered_allowlisted_adapter() -> None:
    happy = load("synthetic-happy-path.json")
    run = copy.deepcopy(happy)
    run["events"] = run["events"][:4]
    run["status"] = "case_locked"
    run["artifacts"] = run["artifacts"][:1]
    run["approvals"] = run["approvals"][:1]
    run["tool_calls"] = []
    run["budgets"] = {"max_actions": 10, "used_actions": 0}
    adapters = AdapterRegistry(registry())
    adapters.register("TL-CYCLE-FIXTURE", execute_cycle_fixture)
    result = execute_approved_workflow(
        run,
        adapters,
        "ART-CASE-HAPPY",
        "ART-OUTPUT-NEW",
        "2026-08-08T01:03:00Z",
    )
    assert result["status"] == "draft_computed"
    assert result["artifacts"][-1]["payload"]["intrinsic_value_reference"]["expected_value"] == 95
    assert result["tool_calls"][0]["approval_ref"] == "APR-0001"
    unsafe = copy.deepcopy(run["artifacts"][0]["payload"])
    unsafe["fixture_id"] = "../../private-source"
    with pytest.raises(ValueError, match="allowlist"):
        execute_cycle_fixture(unsafe)


def test_approved_artifact_read_requires_active_exact_hash_envelope() -> None:
    happy = load("synthetic-happy-path.json")
    envelope = {"artifact": happy["artifacts"][0], "approval": happy["approvals"][0]}
    assert read_approved_artifact(envelope)["valuation_id"] == "VAL-ESTABLISHED-INDUSTRIAL"
    envelope = copy.deepcopy(envelope)
    envelope["approval"]["status"] = "invalidated"
    with pytest.raises(PermissionError, match="active exact-hash"):
        read_approved_artifact(envelope)


def test_memo_runtime_requires_output_approval_and_audits_rendering() -> None:
    happy = load("synthetic-happy-path.json")
    run = copy.deepcopy(happy)
    run["events"] = run["events"][:9]
    run["status"] = "output_approved"
    run["artifacts"] = run["artifacts"][:3]
    run["tool_calls"] = run["tool_calls"][:2]
    run["budgets"] = {"max_actions": 10, "used_actions": 2}
    adapters = AdapterRegistry(registry())
    adapters.register("TL-MEMO-RENDER", memo_adapter)
    result = render_approved_memo(
        run,
        adapters,
        "ART-OUTPUT-HAPPY",
        "ART-MEMO-NEW",
        "2026-08-08T01:04:00Z",
    )
    assert result["status"] == "memo_rendered"
    assert result["tool_calls"][-1]["approval_ref"] == "APR-0002"
    assert result["artifacts"][-1]["kind"] == "memo"

    stale = copy.deepcopy(run)
    stale["approvals"][1]["status"] = "invalidated"
    stale["approvals"][1]["invalidated_at"] = "2026-08-08T01:03:00Z"
    with pytest.raises(PermissionError, match="approval_stale"):
        render_approved_memo(stale, adapters, "ART-OUTPUT-HAPPY", "ART-MEMO-NEW")
