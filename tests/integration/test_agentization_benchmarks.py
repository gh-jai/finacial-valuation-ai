import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = ROOT / "benchmarks/fixtures/agentization"
EXPECTED_ROOT = ROOT / "benchmarks/expected"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def project(document: dict) -> dict:
    result = {
        "run_id": document["run_id"],
        "status": document["status"],
        "artifact_kinds": sorted({item["kind"] for item in document["artifacts"]}),
        "active_gates": sorted(
            item["gate_id"] for item in document["approvals"] if item["status"] == "active"
        ),
        "tool_call_count": len(document["tool_calls"]),
    }
    if document["status"] == "completed":
        output = next(item for item in document["artifacts"] if item["kind"] == "valuation_output")
        result.update(
            intrinsic_value=output["payload"]["intrinsic_value_reference"]["expected_value"],
            review_posture=output["payload"]["judgment_overlay"]["review_posture"],
        )
    elif document["status"] == "blocked_missing_evidence":
        result["blocking_codes"] = sorted(
            item["code"] for item in document["findings"] if item["severity"] == "blocking"
        )
    elif document["status"] == "awaiting_case_lock":
        cases = [item for item in document["artifacts"] if item["kind"] == "case"]
        latest = max(cases, key=lambda item: item["revision"])
        result.update(
            approval_statuses=sorted(item["status"] for item in document["approvals"]),
            case_revisions=sorted(item["revision"] for item in cases),
            latest_normalized_margin=latest["payload"]["assumptions"]["normalized_margin"],
        )
    return result


def test_agentization_benchmarks_match_expected_projections() -> None:
    cases = {
        "synthetic-happy-path.json": "agentization-happy-path-output.json",
        "synthetic-adversarial-stop.json": "agentization-adversarial-stop-output.json",
        "synthetic-approval-tampering.json": "agentization-approval-tampering-output.json",
    }
    for fixture_name, expected_name in cases.items():
        assert project(load(FIXTURE_ROOT / fixture_name)) == load(EXPECTED_ROOT / expected_name)
