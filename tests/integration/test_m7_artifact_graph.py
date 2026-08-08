import json
from pathlib import Path

import yaml

from tools.validate_agent_runs import validate_registry
from tools.validate_claims import load_frontmatter

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {"SRC-DAMODARAN-INVESTMENT-FABLES", "SRC-BAID-JOYS-COMPOUNDING-ZH-2024"}
SKILLS = [f"SKL-AGT-{index:03d}" for index in range(1, 6)]
AGENTS = ["AGT-ORC-001", "AGT-EVD-001", "AGT-VAL-001", "AGT-REV-001", "AGT-MEM-001"]
PROMPTS = ["PRM-ORC-001", "PRM-EVD-001", "PRM-VAL-001", "PRM-REV-001", "PRM-MEM-001"]


def test_m7_claim_knowledge_skill_agent_prompt_graph() -> None:
    claims = yaml.safe_load(
        (ROOT / "extraction/reviewed/M7-governed-agentization-claims.yaml").read_text(
            encoding="utf-8"
        )
    )["claims"]
    knowledge = [
        load_frontmatter(path)
        for path in sorted((ROOT / "knowledge/cross-domain").glob("AGT-*.md"))
    ]
    skills = [load_frontmatter(path) for path in sorted((ROOT / "skills").glob("SKL-AGT-*.md"))]
    agents = [load_frontmatter(path) for path in sorted((ROOT / "agents").glob("*.md"))]
    prompts = [load_frontmatter(path) for path in sorted((ROOT / "prompts").glob("*.md"))]
    assert len(claims) == 20
    assert len(knowledge) == 4
    assert {ref for item in knowledge for ref in item.get("claim_refs", [])} == {
        item["id"] for item in claims
    }
    assert [item["id"] for item in skills] == SKILLS
    assert {item["id"] for item in agents} == set(AGENTS)
    assert {item["id"] for item in prompts} == set(PROMPTS)
    assert {item["agent_ref"] for item in prompts} == set(AGENTS)


def test_registry_resolves_all_agents_prompts_tools_and_denies_approval() -> None:
    registry = yaml.safe_load((ROOT / "agentization/registry.yaml").read_text(encoding="utf-8"))
    assert validate_registry(registry, ROOT) == []
    assert {item["agent_id"] for item in registry["agents"]} == set(AGENTS)
    assert {item["prompt_id"] for item in registry["agents"]} == set(PROMPTS)
    assert all(item["can_approve"] is False for item in registry["agents"])
    assert all(item["network_access"] is False for item in registry["tools"])
    assert all(item["shell_access"] is False for item in registry["tools"])


def test_workflow_composes_m1_m6_and_has_two_human_gates() -> None:
    metadata = load_frontmatter(ROOT / "workflows/WFL-AGT-001-governed-valuation-case.md")
    assert metadata["skill_refs"] == SKILLS
    assert {f"WFL-{code}-001" for code in ("NAR", "VAL", "YNG", "GRW", "DST", "CYC")} <= set(
        metadata["dependencies"]
    )
    body = (ROOT / "docs/milestones/M7-governed-agentization-contract.md").read_text(
        encoding="utf-8"
    )
    assert "`case_lock` and `output_approval`" in body


def test_m7_source_maps_register_core_artifacts_for_both_sources() -> None:
    source_map = yaml.safe_load((ROOT / "sources/source-map.yaml").read_text(encoding="utf-8"))
    mappings = {
        item["source_id"]: set(item["artifacts"])
        for item in source_map["mappings"]
        if item["source_id"] in SOURCES
    }
    shared = {
        "extraction/reviewed/M7-governed-agentization-claims.yaml",
        "docs/milestones/M7-governed-agentization-contract.md",
        "workflows/WFL-AGT-001-governed-valuation-case.md",
        "agentization/registry.yaml",
        "tools/agent_runtime.py",
        "tools/validate_agent_runs.py",
    }
    assert set(mappings) == SOURCES
    assert all(shared <= artifacts for artifacts in mappings.values())


def test_three_benchmarks_cover_completion_stop_and_approval_invalidation() -> None:
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "benchmarks/fixtures/agentization").glob("*.json"))
    ]
    assert len(documents) == 3
    assert {item["status"] for item in documents} == {
        "completed",
        "blocked_missing_evidence",
        "awaiting_case_lock",
    }
    tamper = next(item for item in documents if item["status"] == "awaiting_case_lock")
    assert [item["revision"] for item in tamper["artifacts"]] == [1, 2]
    assert tamper["approvals"][0]["status"] == "invalidated"
