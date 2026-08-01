from pathlib import Path

import yaml

from tools.validate_claims import load_frontmatter


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ID = "SRC-DAMODARAN-LBV-2024"
EXPECTED_SKILLS = [f"SKL-VAL-{number:03d}" for number in range(1, 9)]


def test_m1_has_four_sourced_knowledge_artifacts() -> None:
    paths = sorted((ROOT / "knowledge" / "valuation").glob("VAL-00[2-5]-*.md"))
    metadata = [load_frontmatter(path) for path in paths]
    assert len(metadata) == 4
    assert all(SOURCE_ID in document["source_refs"] for document in metadata)
    assert sum(len(document["claim_refs"]) for document in metadata) == 12


def test_eight_bounded_skills_are_unique_and_sourced() -> None:
    metadata = [
        load_frontmatter(path)
        for path in sorted((ROOT / "skills").glob("SKL-VAL-*.md"))
    ]
    assert [document["id"] for document in metadata] == EXPECTED_SKILLS
    assert all(SOURCE_ID in document["source_refs"] for document in metadata)
    assert all(document["inputs"] and document["outputs"] for document in metadata)


def test_workflow_references_skills_in_execution_order() -> None:
    path = ROOT / "workflows" / "WFL-VAL-001-standard-company-valuation.md"
    metadata = load_frontmatter(path)
    assert metadata["skill_refs"] == EXPECTED_SKILLS
    assert len(metadata["review_gates"]) == 7


def test_source_map_contains_every_m1_skill_and_workflow() -> None:
    source_map = yaml.safe_load((ROOT / "sources" / "source-map.yaml").read_text(encoding="utf-8"))
    mapping = next(item for item in source_map["mappings"] if item["source_id"] == SOURCE_ID)
    mapped = set(mapping["artifacts"])
    skill_paths = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "skills").glob("SKL-VAL-*.md")
    }
    assert skill_paths <= mapped
    assert "workflows/WFL-VAL-001-standard-company-valuation.md" in mapped
