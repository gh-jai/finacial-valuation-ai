"""Validate FVI JSON Schemas and governed Markdown sample frontmatter."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
DOCUMENT_SCHEMAS = {
    "knowledge": SCHEMA_DIR / "knowledge.schema.json",
    "skill": SCHEMA_DIR / "skill.schema.json",
    "workflow": SCHEMA_DIR / "workflow.schema.json",
    "agent": SCHEMA_DIR / "agent.schema.json",
    "prompt": SCHEMA_DIR / "prompt.schema.json",
}
DOCUMENT_ROOTS = {
    "knowledge": ROOT / "knowledge",
    "skill": ROOT / "skills",
    "workflow": ROOT / "workflows",
    "agent": ROOT / "agents",
    "prompt": ROOT / "prompts",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: missing opening YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError(f"{path}: missing closing YAML frontmatter delimiter") from exc
    value = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return value


def main() -> int:
    errors: list[str] = []
    schema_paths = sorted(SCHEMA_DIR.glob("*.schema.json"))
    if not schema_paths:
        errors.append("No schemas found")

    schemas: dict[Path, dict[str, Any]] = {}
    for path in schema_paths:
        try:
            schema = load_json(path)
            Draft202012Validator.check_schema(schema)
            schemas[path] = schema
        except (OSError, ValueError, json.JSONDecodeError, SchemaError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    for artifact_type, schema_path in DOCUMENT_SCHEMAS.items():
        schema = schemas.get(schema_path)
        if schema is None:
            continue
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for path in sorted(DOCUMENT_ROOTS[artifact_type].rglob("*.md")):
            try:
                metadata = load_frontmatter(path)
            except (OSError, ValueError, yaml.YAMLError) as exc:
                errors.append(str(exc))
                continue
            for error in sorted(validator.iter_errors(metadata), key=lambda item: list(item.path)):
                location = ".".join(str(part) for part in error.path) or "<root>"
                errors.append(f"{path.relative_to(ROOT)} [{location}]: {error.message}")

    if errors:
        print("Schema validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    document_count = sum(len(list(root.rglob("*.md"))) for root in DOCUMENT_ROOTS.values())
    print(f"Validated {len(schema_paths)} schemas and {document_count} governed documents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
