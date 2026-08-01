from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_all_repository_yaml_files_parse_as_mappings() -> None:
    paths = sorted(ROOT.rglob("*.yaml"))
    excluded = {".git", ".venv", ".pre-commit-cache"}
    paths = [path for path in paths if excluded.isdisjoint(path.parts)]
    assert paths, "Expected at least one YAML file"
    for path in paths:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(value, dict), f"{path.relative_to(ROOT)} must contain a top-level mapping"
