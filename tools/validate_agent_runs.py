"""Independently validate M7 registry and governed agent-run documents."""

from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "benchmarks/fixtures/agentization"
TERMINAL = {
    "completed",
    "blocked_missing_evidence",
    "validation_failed",
    "review_failed",
    "rejected",
    "cancelled",
}
EVENT_STATE = {
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
TRANSITIONS = {
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
PROHIBITED_OUTPUT_PHRASES = (
    "buy",
    "sell",
    "position size",
    "leverage target",
    "hedge order",
    "trade timing",
)


def load_frontmatter(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing opening YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: missing closing YAML frontmatter delimiter") from exc
    value = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: frontmatter must be a mapping")
    return value


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _derive(events: Sequence[Mapping[str, Any]]) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    state: str | None = None
    parent: str | None = None
    seen: set[str] = set()
    for index, event in enumerate(events):
        event_id = event.get("event_id")
        event_type = event.get("event_type")
        if not isinstance(event_id, str) or event_id in seen:
            errors.append(f"event {index} has a missing or duplicate ID")
        if event.get("parent_event_id") != parent:
            errors.append(f"event {event_id} has a broken parent link")
        if state in TERMINAL:
            errors.append(f"event {event_id} follows terminal state {state}")
        if event_type in {"artifact_revised", "approval_invalidated"}:
            target = event.get("details", {}).get("return_to_state")
            if state is None or target not in {"awaiting_case_lock", "awaiting_output_approval"}:
                errors.append(f"event {event_id} has an invalid revision return state")
            else:
                state = str(target)
        elif event_type in {
            "missing_evidence_blocked",
            "validation_failed",
            "review_failed",
            "rejected",
            "cancelled",
        }:
            if state is None:
                errors.append(f"event {event_id} terminates an uninitialized run")
            state = EVENT_STATE.get(str(event_type))
        elif (state, event_type) not in TRANSITIONS:
            errors.append(f"illegal transition from {state} via {event_type}")
        else:
            state = EVENT_STATE[str(event_type)]
        if event.get("actor_type") == "human" and str(event.get("actor_id", "")).startswith("AGT-"):
            errors.append(f"event {event_id} spoofs a human actor")
        if isinstance(event_id, str):
            seen.add(event_id)
            parent = event_id
    return state, errors


def load_registry(root: Path = ROOT) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    registry = yaml.safe_load((root / "agentization/registry.yaml").read_text(encoding="utf-8"))
    run_schema = json.loads((root / "schemas/agent-run.schema.json").read_text(encoding="utf-8"))
    evaluation_schema = json.loads(
        (root / "schemas/evaluation-result.schema.json").read_text(encoding="utf-8")
    )
    return registry, run_schema, evaluation_schema


def validate_registry(
    registry: Mapping[str, Any], root: Path = ROOT
) -> list[str]:
    schema = json.loads(
        (root / "schemas/agentization-registry.schema.json").read_text(encoding="utf-8")
    )
    errors = [
        f"registry schema {'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
        for error in Draft202012Validator(schema).iter_errors(registry)
    ]
    agent_docs = {
        metadata["id"]: metadata
        for metadata in (load_frontmatter(path) for path in sorted((root / "agents").glob("*.md")))
    }
    prompt_docs = {
        metadata["id"]: metadata
        for metadata in (load_frontmatter(path) for path in sorted((root / "prompts").glob("*.md")))
    }
    tool_ids = {item.get("tool_id") for item in registry.get("tools", [])}
    seen_agents: set[str] = set()
    seen_prompts: set[str] = set()
    for record in registry.get("agents", []):
        agent_id = record.get("agent_id")
        prompt_id = record.get("prompt_id")
        if agent_id in seen_agents:
            errors.append(f"duplicate registry agent {agent_id}")
        if prompt_id in seen_prompts:
            errors.append(f"prompt {prompt_id} is assigned to multiple agents")
        seen_agents.add(str(agent_id))
        seen_prompts.add(str(prompt_id))
        agent_doc = agent_docs.get(agent_id)
        prompt_doc = prompt_docs.get(prompt_id)
        if agent_doc is None:
            errors.append(f"registry references unknown agent document {agent_id}")
        elif set(record.get("allowed_tools", [])) != set(agent_doc.get("permitted_tools", [])):
            errors.append(f"registry and agent document tool sets differ for {agent_id}")
        if prompt_doc is None or prompt_doc.get("agent_ref") != agent_id:
            errors.append(f"registry prompt {prompt_id} does not bind agent {agent_id}")
        if not set(record.get("allowed_tools", [])) <= tool_ids:
            errors.append(f"agent {agent_id} references an unknown tool")
        if record.get("can_approve") is not False:
            errors.append(f"agent {agent_id} must not approve")
    if set(agent_docs) != seen_agents:
        errors.append("registry must contain every governed agent document exactly once")
    if set(prompt_docs) != seen_prompts:
        errors.append("registry must contain every governed prompt document exactly once")
    duties = registry.get("separation_of_duties", {})
    if duties.get("executor_agent") == duties.get("reviewer_agent"):
        errors.append("executor and reviewer must be different agents")
    return errors


def validate_document(
    document: Mapping[str, Any],
    registry: Mapping[str, Any],
    run_schema: Mapping[str, Any],
    evaluation_schema: Mapping[str, Any],
) -> list[str]:
    errors = [
        f"schema {'.'.join(map(str, error.path)) or '<root>'}: {error.message}"
        for error in sorted(
            Draft202012Validator(run_schema, format_checker=FormatChecker()).iter_errors(document),
            key=lambda item: list(item.path),
        )
    ]
    derived, event_errors = _derive(document.get("events", []))
    errors.extend(event_errors)
    if derived != document.get("status"):
        errors.append("reported state does not match independent event derivation")

    artifacts = document.get("artifacts", [])
    artifact_versions: dict[str, list[Mapping[str, Any]]] = {}
    for artifact in artifacts:
        artifact_versions.setdefault(str(artifact.get("artifact_id")), []).append(artifact)
        if artifact.get("payload_hash") != _hash(artifact.get("payload")):
            errors.append(f"artifact {artifact.get('artifact_id')} has a forged payload hash")
        if artifact.get("kind") == "evaluation_result":
            for error in Draft202012Validator(
                evaluation_schema, format_checker=FormatChecker()
            ).iter_errors(artifact.get("payload")):
                errors.append(f"evaluation result schema: {error.message}")
        if artifact.get("kind") in {"valuation_output", "memo"}:
            text = _canonical(artifact.get("payload")).lower()
            if any(term in text for term in PROHIBITED_OUTPUT_PHRASES):
                errors.append(f"artifact {artifact.get('artifact_id')} contains a trade instruction")
    for artifact_id, versions in artifact_versions.items():
        revisions = sorted(int(item.get("revision", 0)) for item in versions)
        if revisions != list(range(1, len(revisions) + 1)):
            errors.append(f"artifact {artifact_id} revisions are not contiguous")

    latest = {
        artifact_id: max(versions, key=lambda item: int(item.get("revision", 0)))
        for artifact_id, versions in artifact_versions.items()
    }
    active_by_gate: dict[str, list[Mapping[str, Any]]] = {}
    approval_ids: set[str] = set()
    for approval in document.get("approvals", []):
        approval_id = approval.get("approval_id")
        if approval_id in approval_ids:
            errors.append(f"duplicate approval ID {approval_id}")
        approval_ids.add(str(approval_id))
        if approval.get("actor_type") != "human" or str(approval.get("actor_id", "")).startswith("AGT-"):
            errors.append(f"approval {approval_id} is not human")
        artifact = latest.get(str(approval.get("artifact_id")))
        if artifact is None:
            errors.append(f"approval {approval_id} references an unknown artifact")
            continue
        if approval.get("status") == "active":
            active_by_gate.setdefault(str(approval.get("gate_id")), []).append(approval)
            if approval.get("payload_hash") != artifact.get("payload_hash"):
                errors.append(f"approval {approval_id} is stale")
            if approval.get("invalidated_at") is not None:
                errors.append(f"active approval {approval_id} has an invalidation time")
        elif approval.get("invalidated_at") is None:
            errors.append(f"invalidated approval {approval_id} lacks an invalidation time")
    if any(len(items) > 1 for items in active_by_gate.values()):
        errors.append("a gate has more than one active approval")

    for handoff in document.get("handoffs", []):
        versions = artifact_versions.get(str(handoff.get("artifact_id")), [])
        if not any(item.get("payload_hash") == handoff.get("payload_hash") for item in versions):
            errors.append(f"handoff {handoff.get('handoff_id')} does not bind an artifact revision")

    agent_records = {item["agent_id"]: item for item in registry.get("agents", [])}
    tool_records = {item["tool_id"]: item for item in registry.get("tools", [])}
    used_actions = int(document.get("budgets", {}).get("used_actions", 0))
    if used_actions != len(document.get("tool_calls", [])):
        errors.append("used action budget does not equal audited tool calls")
    if used_actions > int(document.get("budgets", {}).get("max_actions", 0)):
        errors.append("action budget is exceeded")
    calls_by_agent: dict[str, int] = {}
    for index, call in enumerate(document.get("tool_calls", [])):
        agent = agent_records.get(call.get("agent_id"))
        tool = tool_records.get(call.get("tool_id"))
        if agent is None or tool is None:
            errors.append(f"tool call {call.get('call_id')} uses an unknown agent or tool")
            continue
        if call.get("prompt_id") != agent.get("prompt_id"):
            errors.append(f"tool call {call.get('call_id')} uses the wrong prompt")
        if call.get("tool_id") not in agent.get("allowed_tools", []):
            errors.append(f"tool call {call.get('call_id')} is not allowed for its agent")
        if document.get("workflow_id") not in tool.get("allowed_workflows", []):
            errors.append(f"tool call {call.get('call_id')} is outside workflow scope")
        if call.get("tool_id") in {"TL-CYCLE-FIXTURE", "TL-MEMO-RENDER"} and call.get(
            "approval_ref"
        ) not in approval_ids:
            errors.append(f"tool call {call.get('call_id')} lacks a known approval")
        if call.get("tool_id") == "TL-INDEPENDENT-VALIDATE" and call.get("approval_ref") is not None:
            errors.append(f"tool call {call.get('call_id')} must not manufacture an approval")
        if int(call.get("remaining_action_budget", -1)) != int(
            document.get("budgets", {}).get("max_actions", 0)
        ) - index - 1:
            errors.append(f"tool call {call.get('call_id')} reports the wrong remaining budget")
        calls_by_agent[str(call.get("agent_id"))] = calls_by_agent.get(
            str(call.get("agent_id")), 0
        ) + 1
    for agent_id, count in calls_by_agent.items():
        if count > int(agent_records.get(agent_id, {}).get("max_actions", 0)):
            errors.append(f"agent {agent_id} exceeds its action budget")

    executor_events = {
        event.get("actor_id")
        for event in document.get("events", [])
        if event.get("event_type") == "valuation_executed"
    }
    reviewer_events = {
        event.get("actor_id")
        for event in document.get("events", [])
        if event.get("event_type") == "independent_review_passed"
    }
    if executor_events & reviewer_events:
        errors.append("executor and reviewer actors are not separated")
    if executor_events and executor_events != {"AGT-VAL-001"}:
        errors.append("valuation execution actor is not the registered executor")
    if reviewer_events and reviewer_events != {"AGT-REV-001"}:
        errors.append("independent review actor is not the registered reviewer")

    status = document.get("status")
    kinds = {item.get("kind") for item in artifacts}
    if status == "completed":
        if not {"case", "valuation_output", "evaluation_result", "memo"} <= kinds:
            errors.append("completed run lacks required artifacts")
        if set(active_by_gate) != {"case_lock", "output_approval"}:
            errors.append("completed run lacks both active human approvals")
        if not document.get("tool_calls"):
            errors.append("completed run lacks deterministic execution audit")
        required_tools = {"TL-CYCLE-FIXTURE", "TL-INDEPENDENT-VALIDATE", "TL-MEMO-RENDER"}
        if {item.get("tool_id") for item in document.get("tool_calls", [])} != required_tools:
            errors.append("completed run lacks execution, independent-review, or memo tool audit")
    if status == "blocked_missing_evidence":
        if "valuation_output" in kinds or document.get("tool_calls"):
            errors.append("evidence-blocked run must stop before valuation")
        if not any(item.get("severity") == "blocking" for item in document.get("findings", [])):
            errors.append("evidence-blocked run requires a blocking finding")
    if status == "awaiting_case_lock":
        case_ids = [key for key, item in latest.items() if item.get("kind") == "case"]
        if any(active_by_gate.get("case_lock", [])):
            errors.append("awaiting-case-lock run cannot retain an active case approval")
        if len(case_ids) != 1:
            errors.append("approval-tampering run requires one versioned case artifact ID")
    return errors


def main() -> int:
    try:
        registry, run_schema, evaluation_schema = load_registry(ROOT)
        failures = validate_registry(registry, ROOT)
        paths = sorted(FIXTURE_ROOT.glob("*.json"))
        for path in paths:
            document = json.loads(path.read_text(encoding="utf-8"))
            for error in validate_document(document, registry, run_schema, evaluation_schema):
                failures.append(f"{path.relative_to(ROOT)}: {error}")
    except (OSError, TypeError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Agent-run validation failed: {exc}")
        return 1
    if failures:
        print("Agent-run validation failed:")
        for error in failures:
            print(f"- {error}")
        return 1
    print(f"Validated registry and {len(paths)} governed agent run(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
