import json
from pathlib import Path

import yaml

from tools.validate_claims import load_frontmatter

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "SRC-DAMODARAN-DARK-SIDE-2018"
SKILLS = [f"SKL-GRW-{number:03d}" for number in range(1, 10)]


def test_m4_claim_knowledge_and_skill_graph() -> None:
    claims = yaml.safe_load(
        (ROOT / "extraction/reviewed/M4-growth-company-scaling-and-fade-claims.yaml").read_text(
            encoding="utf-8"
        )
    )["claims"]
    knowledge_paths = sorted(
        path
        for root in (
            ROOT / "knowledge/lifecycle",
            ROOT / "knowledge/risk",
            ROOT / "knowledge/valuation",
        )
        for path in root.glob("GRW-*.md")
    )
    knowledge = [load_frontmatter(path) for path in knowledge_paths]
    skills = [load_frontmatter(path) for path in sorted((ROOT / "skills").glob("SKL-GRW-*.md"))]
    assert len(claims) == 30
    assert len(knowledge) == 7
    assert {ref for item in knowledge for ref in item["claim_refs"]} == {
        item["id"] for item in claims
    }
    assert [item["id"] for item in skills] == SKILLS
    assert all(SOURCE in item["source_refs"] for item in knowledge + skills)


def test_m4_workflow_composes_m1_m2_and_m3_handoff() -> None:
    metadata = load_frontmatter(ROOT / "workflows/WFL-GRW-001-growth-company-scaling-and-fade.md")
    assert metadata["skill_refs"] == SKILLS
    assert {"WFL-NAR-001", "WFL-VAL-001", "WFL-YNG-001"} <= set(metadata["dependencies"])
    assert len(metadata["review_gates"]) == 10


def test_m4_source_map_contains_complete_artifact_graph() -> None:
    source_map = yaml.safe_load((ROOT / "sources/source-map.yaml").read_text(encoding="utf-8"))
    mapping = next(item for item in source_map["mappings"] if item["source_id"] == SOURCE)
    mapped = set(mapping["artifacts"])
    expected = {
        path.relative_to(ROOT).as_posix()
        for pattern in (
            "knowledge/lifecycle/GRW-*.md",
            "knowledge/risk/GRW-*.md",
            "knowledge/valuation/GRW-*.md",
            "skills/SKL-GRW-*.md",
        )
        for path in ROOT.glob(pattern)
    }
    expected |= {
        "workflows/WFL-GRW-001-growth-company-scaling-and-fade.md",
        "schemas/growth-company-valuation.schema.json",
        "tools/growth_company.py",
        "tools/validate_growth_company_valuations.py",
    }
    assert expected <= mapped


def test_benchmarks_keep_narratives_and_failure_handoffs_separate() -> None:
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "benchmarks/fixtures/growth_company").glob("*.json"))
    ]
    assert len(documents) == 2
    assert len({item["narrative_id"] for item in documents}) == 2
    assert sum("failure_handoff" in item for item in documents) == 1
    for item in documents:
        assert item["growth_company_profile"]["m3_boundary_cleared"]
        assert item["stable_state"]["mature_year"] == len(item["forecast"]["years"])
