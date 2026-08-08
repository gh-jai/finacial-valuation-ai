"""Governed M7 event, artifact, approval, and authorization primitives."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

TERMINAL_STATES = {
    "blocked_missing_evidence",
    "validation_failed",
    "review_failed",
    "rejected",
    "cancelled",
    "completed",
}

EVENT_STATES = {
    "run_initialized": "initialized",
    "case_assembled": "case_assembled",
    "case_lock_requested": "awaiting_case_lock",
    "case_lock_approved": "case_locked",
    "valuation_executed": "draft_computed",
    "deterministic_validation_passed": "deterministic_validated",
    "independent_review_passed": "independent_reviewed",
    "output_approval_requested": "awaiting_output_approval",
    "output_approved": "output_approved",
    "memo_rendered": "memo_rendered",
    "run_completed": "completed",
    "missing_evidence_blocked": "blocked_missing_evidence",
    "validation_failed": "validation_failed",
    "review_failed": "review_failed",
    "rejected": "rejected",
    "cancelled": "cancelled",
}

ALLOWED_TRANSITIONS = {
    (None, "run_initialized"),
    ("initialized", "case_assembled"),
    ("case_assembled", "case_lock_requested"),
    ("awaiting_case_lock", "case_lock_approved"),
    ("case_locked", "valuation_executed"),
    ("draft_computed", "deterministic_validation_passed"),
    ("deterministic_validated", "independent_review_passed"),
    ("independent_reviewed", "output_approval_requested"),
    ("awaiting_output_approval", "output_approved"),
    ("output_approved", "memo_rendered"),
    ("memo_rendered", "run_completed"),
}


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    code: str
    reason: str
    approval_ref: str | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    """Return the sole canonical JSON representation used by the runtime."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payload_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _revision_state(event: Mapping[str, Any]) -> str:
    state = event.get("details", {}).get("return_to_state")
    if state not in {"awaiting_case_lock", "awaiting_output_approval"}:
        raise ValueError("revision event requires a governed return_to_state")
    return str(state)


def derive_state(events: Sequence[Mapping[str, Any]]) -> str:
    """Derive state from an ordered event stream and reject illegal transitions."""
    state: str | None = None
    previous_event_id: str | None = None
    seen: set[str] = set()
    for index, event in enumerate(events):
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        if not isinstance(event_id, str) or event_id in seen:
            raise ValueError(f"event {index} has a missing or duplicate event_id")
        if event.get("parent_event_id") != previous_event_id:
            raise ValueError(f"event {event_id} has a broken parent link")
        if state in TERMINAL_STATES:
            raise ValueError(f"event {event_id} follows terminal state {state}")
        if event_type in {"artifact_revised", "approval_invalidated"}:
            if state is None:
                raise ValueError(f"event {event_id} cannot revise an uninitialized run")
            state = _revision_state(event)
        elif event_type in {
            "missing_evidence_blocked",
            "validation_failed",
            "review_failed",
            "rejected",
            "cancelled",
        }:
            if state is None:
                raise ValueError(f"event {event_id} cannot terminate an uninitialized run")
            state = EVENT_STATES[str(event_type)]
        else:
            if (state, event_type) not in ALLOWED_TRANSITIONS:
                raise ValueError(f"illegal transition from {state} via {event_type}")
            state = EVENT_STATES[str(event_type)]
        seen.add(event_id)
        previous_event_id = event_id
    if state is None:
        raise ValueError("event stream is empty")
    return state


def append_event(run: Mapping[str, Any], event: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(run))
    events = list(result.get("events", []))
    events.append(copy.deepcopy(dict(event)))
    result["events"] = events
    result["status"] = derive_state(events)
    return result


def latest_artifact(run: Mapping[str, Any], artifact_id: str) -> Mapping[str, Any]:
    matches = [item for item in run.get("artifacts", []) if item.get("artifact_id") == artifact_id]
    if not matches:
        raise ValueError(f"unknown artifact {artifact_id}")
    return max(matches, key=lambda item: int(item.get("revision", 0)))


def active_approval(
    run: Mapping[str, Any], gate_id: str, artifact_id: str
) -> Mapping[str, Any] | None:
    artifact = latest_artifact(run, artifact_id)
    current_hash = payload_hash(artifact["payload"])
    for approval in reversed(run.get("approvals", [])):
        if (
            approval.get("gate_id") == gate_id
            and approval.get("artifact_id") == artifact_id
            and approval.get("status") == "active"
            and approval.get("actor_type") == "human"
            and approval.get("payload_hash") == current_hash
            and artifact.get("payload_hash") == current_hash
        ):
            return approval
    return None


def add_artifact(
    run: Mapping[str, Any],
    artifact_id: str,
    kind: str,
    payload: Mapping[str, Any],
    creator: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    result = copy.deepcopy(dict(run))
    prior = [item for item in result.get("artifacts", []) if item.get("artifact_id") == artifact_id]
    revision = max((int(item["revision"]) for item in prior), default=0) + 1
    artifact = {
        "artifact_id": artifact_id,
        "kind": kind,
        "revision": revision,
        "payload": copy.deepcopy(dict(payload)),
        "payload_hash": payload_hash(payload),
        "created_by": creator,
    }
    result.setdefault("artifacts", []).append(artifact)
    if prior:
        return_state = "awaiting_case_lock" if kind == "case" else "awaiting_output_approval"
        event = {
            "event_id": f"EVT-{len(result.get('events', [])) + 1:04d}",
            "event_type": "artifact_revised",
            "actor_id": creator,
            "actor_type": "agent" if creator.startswith("AGT-") else "runtime",
            "timestamp": timestamp or _now(),
            "parent_event_id": result["events"][-1]["event_id"],
            "artifact_id": artifact_id,
            "details": {"revision": revision, "return_to_state": return_state},
        }
        result = append_event(result, event)
    return result


def create_handoff(
    run: Mapping[str, Any], artifact_id: str, sender: str, recipient: str, timestamp: str | None = None
) -> dict[str, Any]:
    result = copy.deepcopy(dict(run))
    artifact = latest_artifact(result, artifact_id)
    current_hash = payload_hash(artifact["payload"])
    if artifact.get("payload_hash") != current_hash:
        raise ValueError("artifact hash mismatch prevents handoff")
    handoff = {
        "handoff_id": f"HND-{len(result.get('handoffs', [])) + 1:04d}",
        "sender": sender,
        "recipient": recipient,
        "artifact_id": artifact_id,
        "payload_hash": current_hash,
        "created_at": timestamp or _now(),
    }
    result.setdefault("handoffs", []).append(handoff)
    return result


def bind_human_approval(
    run: Mapping[str, Any], gate_id: str, artifact_id: str, actor: str, timestamp: str | None = None
) -> dict[str, Any]:
    if gate_id not in {"case_lock", "output_approval"}:
        raise ValueError("unknown human gate")
    if not actor or actor.startswith("AGT-"):
        raise ValueError("approval actor must be an identified human")
    required_state = "awaiting_case_lock" if gate_id == "case_lock" else "awaiting_output_approval"
    if run.get("status") != required_state:
        raise ValueError(f"{gate_id} approval requires state {required_state}")
    artifact = latest_artifact(run, artifact_id)
    expected_kind = "case" if gate_id == "case_lock" else "valuation_output"
    if artifact.get("kind") != expected_kind:
        raise ValueError(f"{gate_id} must bind a {expected_kind} artifact")
    current_hash = payload_hash(artifact["payload"])
    if artifact.get("payload_hash") != current_hash:
        raise ValueError("artifact hash mismatch prevents approval")
    approved_at = timestamp or _now()
    result = copy.deepcopy(dict(run))
    approval_id = f"APR-{len(result.get('approvals', [])) + 1:04d}"
    result.setdefault("approvals", []).append(
        {
            "approval_id": approval_id,
            "gate_id": gate_id,
            "artifact_id": artifact_id,
            "payload_hash": current_hash,
            "actor_id": actor,
            "actor_type": "human",
            "status": "active",
            "approved_at": approved_at,
            "invalidated_at": None,
        }
    )
    event_type = "case_lock_approved" if gate_id == "case_lock" else "output_approved"
    event = {
        "event_id": f"EVT-{len(result.get('events', [])) + 1:04d}",
        "event_type": event_type,
        "actor_id": actor,
        "actor_type": "human",
        "timestamp": approved_at,
        "parent_event_id": result["events"][-1]["event_id"],
        "artifact_id": artifact_id,
        "details": {"approval_id": approval_id, "payload_hash": current_hash},
    }
    return append_event(result, event)


def invalidate_stale_approvals(
    run: Mapping[str, Any], timestamp: str | None = None
) -> dict[str, Any]:
    result = copy.deepcopy(dict(run))
    invalidated: list[tuple[str, str]] = []
    for approval in result.get("approvals", []):
        if approval.get("status") != "active":
            continue
        artifact = latest_artifact(result, str(approval["artifact_id"]))
        current_hash = payload_hash(artifact["payload"])
        if approval.get("payload_hash") != current_hash or artifact.get("payload_hash") != current_hash:
            approval["status"] = "invalidated"
            approval["invalidated_at"] = timestamp or _now()
            invalidated.append((str(approval["approval_id"]), str(approval["gate_id"])))
    for approval_id, gate_id in invalidated:
        return_state = "awaiting_case_lock" if gate_id == "case_lock" else "awaiting_output_approval"
        event = {
            "event_id": f"EVT-{len(result.get('events', [])) + 1:04d}",
            "event_type": "approval_invalidated",
            "actor_id": "M7-RUNTIME",
            "actor_type": "runtime",
            "timestamp": timestamp or _now(),
            "parent_event_id": result["events"][-1]["event_id"],
            "artifact_id": None,
            "details": {"approval_id": approval_id, "return_to_state": return_state},
        }
        result = append_event(result, event)
    return result


def _registry_agent(registry: Mapping[str, Any], agent_id: str) -> Mapping[str, Any] | None:
    return next((item for item in registry.get("agents", []) if item.get("agent_id") == agent_id), None)


def authorize_action(
    registry: Mapping[str, Any],
    run: Mapping[str, Any],
    agent_id: str,
    action: str,
    tool_id: str | None = None,
    artifact_id: str | None = None,
) -> PolicyDecision:
    agent = _registry_agent(registry, agent_id)
    if agent is None:
        return PolicyDecision(False, "unknown_agent", "agent is not registered")
    if run.get("status") in TERMINAL_STATES:
        return PolicyDecision(False, "terminal_run", "terminal runs cannot accept actions")
    if action not in agent.get("allowed_actions", []):
        return PolicyDecision(False, "action_denied", "action is not allowed for this agent")
    used_actions = int(run.get("budgets", {}).get("used_actions", 0))
    agent_actions = sum(
        call.get("agent_id") == agent_id for call in run.get("tool_calls", [])
    )
    if used_actions >= int(run.get("budgets", {}).get("max_actions", 0)) or agent_actions >= int(
        agent.get("max_actions", 0)
    ):
        return PolicyDecision(False, "budget_exhausted", "remaining action budget is zero")
    if tool_id is not None:
        if tool_id not in agent.get("allowed_tools", []):
            return PolicyDecision(False, "tool_denied", "tool is not allowed for this agent")
        tool = next((item for item in registry.get("tools", []) if item.get("tool_id") == tool_id), None)
        if tool is None or run.get("workflow_id") not in tool.get("allowed_workflows", []):
            return PolicyDecision(False, "tool_scope_denied", "tool is unknown or out of workflow scope")
    if action == "execute_workflow":
        if run.get("status") != "case_locked":
            return PolicyDecision(False, "state_denied", "execution requires case_locked state")
        if not artifact_id:
            return PolicyDecision(False, "approval_missing", "execution requires a case artifact")
        approval = active_approval(run, "case_lock", artifact_id)
        if approval is None:
            return PolicyDecision(False, "approval_stale", "active exact-hash case approval is absent")
        return PolicyDecision(True, "allowed", "approved deterministic execution", str(approval["approval_id"]))
    if action == "render_memo":
        if run.get("status") != "output_approved":
            return PolicyDecision(False, "state_denied", "memo rendering requires output_approved state")
        if not artifact_id:
            return PolicyDecision(False, "approval_missing", "memo rendering requires an output artifact")
        approval = active_approval(run, "output_approval", artifact_id)
        if approval is None:
            return PolicyDecision(False, "approval_stale", "active exact-hash output approval is absent")
        return PolicyDecision(True, "allowed", "approved memo rendering", str(approval["approval_id"]))
    return PolicyDecision(True, "allowed", "registered action is allowed")


def execute_approved_workflow(
    run: Mapping[str, Any],
    adapter_registry: Any,
    case_artifact_id: str,
    output_artifact_id: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    registry = adapter_registry.policy_registry
    decision = authorize_action(
        registry,
        run,
        "AGT-VAL-001",
        "execute_workflow",
        "TL-CYCLE-FIXTURE",
        case_artifact_id,
    )
    if not decision.allowed:
        raise PermissionError(f"{decision.code}: {decision.reason}")
    case = latest_artifact(run, case_artifact_id)
    result_payload = adapter_registry.invoke("TL-CYCLE-FIXTURE", case["payload"])
    result = add_artifact(
        run, output_artifact_id, "valuation_output", result_payload, "AGT-VAL-001"
    )
    used = int(result["budgets"]["used_actions"]) + 1
    result["budgets"]["used_actions"] = used
    tool_call = {
        "call_id": f"CALL-{len(result.get('tool_calls', [])) + 1:04d}",
        "agent_id": "AGT-VAL-001",
        "prompt_id": "PRM-VAL-001",
        "tool_id": "TL-CYCLE-FIXTURE",
        "input_hash": str(case["payload_hash"]),
        "output_hash": payload_hash(result_payload),
        "parent_event_id": result["events"][-1]["event_id"],
        "timestamp": timestamp or _now(),
        "status": "success",
        "error_code": None,
        "approval_ref": decision.approval_ref,
        "remaining_action_budget": int(result["budgets"]["max_actions"]) - used,
    }
    result.setdefault("tool_calls", []).append(tool_call)
    event = {
        "event_id": f"EVT-{len(result.get('events', [])) + 1:04d}",
        "event_type": "valuation_executed",
        "actor_id": "AGT-VAL-001",
        "actor_type": "agent",
        "timestamp": timestamp or _now(),
        "parent_event_id": result["events"][-1]["event_id"],
        "artifact_id": output_artifact_id,
        "details": {"tool_call_id": tool_call["call_id"]},
    }
    return append_event(result, event)


def render_approved_memo(
    run: Mapping[str, Any],
    adapter_registry: Any,
    output_artifact_id: str,
    memo_artifact_id: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    registry = adapter_registry.policy_registry
    decision = authorize_action(
        registry,
        run,
        "AGT-MEM-001",
        "render_memo",
        "TL-MEMO-RENDER",
        output_artifact_id,
    )
    if not decision.allowed:
        raise PermissionError(f"{decision.code}: {decision.reason}")
    output = latest_artifact(run, output_artifact_id)
    memo_payload = adapter_registry.invoke("TL-MEMO-RENDER", output["payload"])
    result = add_artifact(run, memo_artifact_id, "memo", memo_payload, "AGT-MEM-001")
    used = int(result["budgets"]["used_actions"]) + 1
    result["budgets"]["used_actions"] = used
    tool_call = {
        "call_id": f"CALL-{len(result.get('tool_calls', [])) + 1:04d}",
        "agent_id": "AGT-MEM-001",
        "prompt_id": "PRM-MEM-001",
        "tool_id": "TL-MEMO-RENDER",
        "input_hash": str(output["payload_hash"]),
        "output_hash": payload_hash(memo_payload),
        "parent_event_id": result["events"][-1]["event_id"],
        "timestamp": timestamp or _now(),
        "status": "success",
        "error_code": None,
        "approval_ref": decision.approval_ref,
        "remaining_action_budget": int(result["budgets"]["max_actions"]) - used,
    }
    result.setdefault("tool_calls", []).append(tool_call)
    event = {
        "event_id": f"EVT-{len(result.get('events', [])) + 1:04d}",
        "event_type": "memo_rendered",
        "actor_id": "AGT-MEM-001",
        "actor_type": "agent",
        "timestamp": timestamp or _now(),
        "parent_event_id": result["events"][-1]["event_id"],
        "artifact_id": memo_artifact_id,
        "details": {"tool_call_id": tool_call["call_id"]},
    }
    return append_event(result, event)
