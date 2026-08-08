import json
from pathlib import Path

import yaml

from tools.validate_claims import load_frontmatter

ROOT = Path(__file__).resolve().parents[2]
METHOD_SOURCE = "SRC-DAMODARAN-DARK-SIDE-2018"
JUDGMENT_SOURCE = "SRC-MARKS-MASTERING-MARKET-CYCLE-2018"
SKILLS = [f"SKL-CYC-{number:03d}" for number in range(1, 11)]


def test_m6_claim_knowledge_and_skill_graph() -> None:
    claims = yaml.safe_load(
        (ROOT / "extraction/reviewed/M6-cycle-aware-judgment-layer-claims.yaml").read_text(
            encoding="utf-8"
        )
    )["claims"]
    knowledge_paths = sorted(
        path
        for root in (ROOT / "knowledge/lifecycle", ROOT / "knowledge/risk", ROOT / "knowledge/valuation", ROOT / "knowledge/market-pricing")
        for path in root.glob("CYC-*.md")
    )
    knowledge = [load_frontmatter(path) for path in knowledge_paths]
    skills = [load_frontmatter(path) for path in sorted((ROOT / "skills").glob("SKL-CYC-*.md"))]
    assert len(claims) == 36
    assert len(knowledge) == 8
    assert {ref for item in knowledge for ref in item["claim_refs"]} == {
        item["id"] for item in claims
    }
    assert [item["id"] for item in skills] == SKILLS
    assert all(item["source_refs"] for item in knowledge + skills)


def test_m6_workflow_composes_prior_milestones_without_an_opaque_score() -> None:
    path = ROOT / "workflows/WFL-CYC-001-cycle-aware-judgment-layer.md"
    metadata = load_frontmatter(path)
    body = path.read_text(encoding="utf-8")
    assert metadata["skill_refs"] == SKILLS
    assert {"WFL-NAR-001", "WFL-VAL-001", "WFL-GRW-001", "WFL-DST-001"} <= set(
        metadata["dependencies"]
    )
    assert len(metadata["review_gates"]) == 10
    assert "hidden composite score" in body


def test_m6_source_maps_contain_complete_artifact_graph() -> None:
    source_map = yaml.safe_load((ROOT / "sources/source-map.yaml").read_text(encoding="utf-8"))
    mappings = {
        item["source_id"]: set(item["artifacts"])
        for item in source_map["mappings"]
        if item["source_id"] in {METHOD_SOURCE, JUDGMENT_SOURCE}
    }
    shared = {
        "workflows/WFL-CYC-001-cycle-aware-judgment-layer.md",
        "schemas/cycle-aware-judgment.schema.json",
        "tools/cycle_aware.py",
        "tools/validate_cycle_aware_judgments.py",
    }
    assert shared <= mappings[METHOD_SOURCE]
    assert shared <= mappings[JUDGMENT_SOURCE]
    expected_knowledge = {
        path.relative_to(ROOT).as_posix()
        for root in (ROOT / "knowledge/lifecycle", ROOT / "knowledge/risk", ROOT / "knowledge/valuation", ROOT / "knowledge/market-pricing")
        for path in root.glob("CYC-*.md")
    }
    assert expected_knowledge <= mappings[METHOD_SOURCE] | mappings[JUDGMENT_SOURCE]


def test_benchmarks_cover_distinct_regimes_treatments_and_postures() -> None:
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "benchmarks/fixtures/cycle_aware").glob("*.json"))
    ]
    assert len(documents) == 2
    assert {item["cycle_assessment"]["regime"] for item in documents} == {
        "established_recurring",
        "structural_break",
    }
    assert {item["valuation_treatment"]["mode"] for item in documents} == {
        "transition_to_normal",
        "current_expectations",
    }
    assert {item["judgment_overlay"]["review_posture"] for item in documents} == {
        "balanced_review",
        "defensive_review",
    }
