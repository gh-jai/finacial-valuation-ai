import json
from pathlib import Path

import yaml

from tools.validate_claims import load_frontmatter

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "SRC-DAMODARAN-DARK-SIDE-2018"
SKILLS = [f"SKL-DST-{number:03d}" for number in range(1, 11)]


def test_m5_claim_knowledge_and_skill_graph() -> None:
    claims = yaml.safe_load(
        (ROOT / "extraction/reviewed/M5-decline-distress-contingent-survival-claims.yaml").read_text(
            encoding="utf-8"
        )
    )["claims"]
    knowledge_paths = sorted(
        path
        for root in (ROOT / "knowledge/lifecycle", ROOT / "knowledge/risk", ROOT / "knowledge/valuation")
        for path in root.glob("DST-*.md")
    )
    knowledge = [load_frontmatter(path) for path in knowledge_paths]
    skills = [load_frontmatter(path) for path in sorted((ROOT / "skills").glob("SKL-DST-*.md"))]
    assert len(claims) == 32
    assert len(knowledge) == 8
    assert {ref for item in knowledge for ref in item["claim_refs"]} == {
        item["id"] for item in claims
    }
    assert [item["id"] for item in skills] == SKILLS
    assert all(SOURCE in item["source_refs"] for item in knowledge + skills)


def test_m5_workflow_composes_prior_milestones() -> None:
    metadata = load_frontmatter(
        ROOT / "workflows/WFL-DST-001-decline-distress-contingent-survival.md"
    )
    assert metadata["skill_refs"] == SKILLS
    assert {"WFL-NAR-001", "WFL-VAL-001", "WFL-YNG-001", "WFL-GRW-001"} <= set(
        metadata["dependencies"]
    )
    assert len(metadata["review_gates"]) == 10


def test_m5_source_map_contains_complete_artifact_graph() -> None:
    source_map = yaml.safe_load((ROOT / "sources/source-map.yaml").read_text(encoding="utf-8"))
    mapping = next(item for item in source_map["mappings"] if item["source_id"] == SOURCE)
    mapped = set(mapping["artifacts"])
    expected = {
        path.relative_to(ROOT).as_posix()
        for pattern in (
            "knowledge/lifecycle/DST-*.md",
            "knowledge/risk/DST-*.md",
            "knowledge/valuation/DST-*.md",
            "skills/SKL-DST-*.md",
        )
        for path in ROOT.glob(pattern)
    }
    expected |= {
        "workflows/WFL-DST-001-decline-distress-contingent-survival.md",
        "schemas/decline-distress-valuation.schema.json",
        "tools/decline_distress.py",
        "tools/validate_decline_distress_valuations.py",
    }
    assert expected <= mapped


def test_benchmarks_cover_two_distinct_quadrants_and_narratives() -> None:
    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "benchmarks/fixtures/decline_distress").glob("*.json"))
    ]
    assert len(documents) == 2
    assert {item["routing"]["quadrant"] for item in documents} == {
        "irreversible_low",
        "reversible_high",
    }
    assert len({item["narrative_id"] for item in documents}) == 2
    assert sum("orderly_liquidation" in item for item in documents) == 1
    assert sum("distress_case" in item for item in documents) == 1
