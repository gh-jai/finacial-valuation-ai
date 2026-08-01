from pathlib import Path

import yaml

from tools.validate_claims import load_frontmatter


ROOT = Path(__file__).resolve().parents[2]
SOURCE_ID = "SRC-DAMODARAN-NARRATIVE-NUMBERS-2017"
SKILLS = [f"SKL-NAR-{number:03d}" for number in range(1, 9)]


def test_m2_artifact_counts_and_sources() -> None:
    knowledge = [load_frontmatter(path) for path in sorted((ROOT / "knowledge/narrative").glob("*.md"))]
    skills = [load_frontmatter(path) for path in sorted((ROOT / "skills").glob("SKL-NAR-*.md"))]
    assert len(knowledge) == 6
    assert sum(len(item["claim_refs"]) for item in knowledge) >= 24
    assert [item["id"] for item in skills] == SKILLS
    assert all(SOURCE_ID in item["source_refs"] for item in knowledge + skills)


def test_narrative_workflow_composes_with_m1() -> None:
    workflow = load_frontmatter(ROOT / "workflows/WFL-NAR-001-narrative-to-numbers.md")
    body = (ROOT / "workflows/WFL-NAR-001-narrative-to-numbers.md").read_text(encoding="utf-8")
    assert workflow["skill_refs"] == SKILLS
    assert "WFL-VAL-001" in workflow["dependencies"]
    assert "WFL-VAL-001" in body
    assert len(workflow["review_gates"]) == 8


def test_source_map_contains_m2_graph() -> None:
    source_map = yaml.safe_load((ROOT / "sources/source-map.yaml").read_text(encoding="utf-8"))
    mapping = next(item for item in source_map["mappings"] if item["source_id"] == SOURCE_ID)
    mapped = set(mapping["artifacts"])
    expected = {path.relative_to(ROOT).as_posix() for root in (ROOT / "knowledge/narrative", ROOT / "skills") for path in root.glob("*NAR-*.md")}
    assert expected <= mapped
    assert "workflows/WFL-NAR-001-narrative-to-numbers.md" in mapped
