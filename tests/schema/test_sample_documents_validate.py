import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SAMPLES = [
    (ROOT / "knowledge" / "valuation" / "VAL-001-intrinsic-value.md", "knowledge"),
    (ROOT / "skills" / "SKL-VAL-001-validate-dcf-inputs.md", "skill"),
    (ROOT / "workflows" / "WFL-VAL-001-standard-company-valuation.md", "workflow"),
]


def frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---"
    end = lines.index("---", 1)
    metadata = yaml.safe_load("\n".join(lines[1:end]))
    assert isinstance(metadata, dict)
    return metadata


def test_sample_frontmatter_validates() -> None:
    for path, artifact_type in SAMPLES:
        schema_path = ROOT / "schemas" / f"{artifact_type}.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        errors = list(validator.iter_errors(frontmatter(path)))
        assert not errors, f"{path.name}: {[error.message for error in errors]}"


def test_samples_have_required_frontmatter_fields() -> None:
    required = {
        "id", "title", "type", "status", "version", "domain",
        "source_refs", "dependencies", "owner", "last_updated",
    }
    for path, _ in SAMPLES:
        assert required <= frontmatter(path).keys()
