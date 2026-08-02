from pathlib import Path

import yaml

from tools.validate_claims import load_frontmatter


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "SRC-DAMODARAN-DARK-SIDE-2018"
SKILLS = [f"SKL-YNG-{number:03d}" for number in range(1, 10)]


def test_m3_claim_knowledge_and_skill_counts() -> None:
    claims = yaml.safe_load((ROOT / "extraction/reviewed/M3-young-company-survival-adjusted-claims.yaml").read_text(encoding="utf-8"))["claims"]
    knowledge_paths = sorted(path for root in (ROOT / "knowledge/lifecycle", ROOT / "knowledge/risk", ROOT / "knowledge/valuation") for path in root.glob("YNG-*.md"))
    knowledge = [load_frontmatter(path) for path in knowledge_paths]
    skills = [load_frontmatter(path) for path in sorted((ROOT / "skills").glob("SKL-YNG-*.md"))]
    assert len(claims) == 30
    assert len(knowledge) == 7
    assert {ref for item in knowledge for ref in item["claim_refs"]} == {item["id"] for item in claims}
    assert [item["id"] for item in skills] == SKILLS
    assert all(SOURCE in item["source_refs"] for item in knowledge + skills)


def test_m3_workflow_composes_with_m1_and_m2() -> None:
    metadata = load_frontmatter(ROOT / "workflows/WFL-YNG-001-young-company-survival-adjusted.md")
    assert metadata["skill_refs"] == SKILLS
    assert {"WFL-NAR-001", "WFL-VAL-001"} <= set(metadata["dependencies"])
    assert len(metadata["review_gates"]) == 9


def test_m3_source_map_contains_artifact_graph() -> None:
    source_map = yaml.safe_load((ROOT / "sources/source-map.yaml").read_text(encoding="utf-8"))
    mapping = next(item for item in source_map["mappings"] if item["source_id"] == SOURCE)
    mapped = set(mapping["artifacts"])
    expected = {path.relative_to(ROOT).as_posix() for path in (ROOT / "skills").glob("SKL-YNG-*.md")}
    expected |= {path.relative_to(ROOT).as_posix() for root in (ROOT / "knowledge/lifecycle", ROOT / "knowledge/risk", ROOT / "knowledge/valuation") for path in root.glob("YNG-*.md")}
    assert expected <= mapped
    assert "workflows/WFL-YNG-001-young-company-survival-adjusted.md" in mapped


def test_benchmarks_keep_narratives_and_claim_structures_separate() -> None:
    import json

    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "benchmarks/fixtures/young_company").glob("*.json"))
    ]
    assert len({item["narrative_id"] for item in documents}) == len(documents)
    structures = {
        (
            item["equity_bridge"]["debt_and_senior_claims"],
            item["equity_bridge"]["option_and_other_equity_claim_value"],
            item["equity_bridge"]["current_share_count"],
        )
        for item in documents
    }
    assert len(structures) == len(documents)
