"""Validate the source catalog and cross-references without opening private inputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> int:
    errors: list[str] = []
    schema = json.loads((ROOT / "schemas" / "source.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    catalog = load_yaml(ROOT / "sources" / "catalog.yaml")
    source_map = load_yaml(ROOT / "sources" / "source-map.yaml")
    if not isinstance(catalog, dict) or not isinstance(catalog.get("sources"), list):
        errors.append("sources/catalog.yaml: 'sources' must be a list")
        sources: list[Any] = []
    else:
        sources = catalog["sources"]

    seen: set[str] = set()
    for index, source in enumerate(sources):
        for error in validator.iter_errors(source):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"sources/catalog.yaml sources[{index}].{location}: {error.message}")
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        if isinstance(source_id, str):
            if source_id in seen:
                errors.append(f"sources/catalog.yaml: duplicate source ID {source_id}")
            seen.add(source_id)
        locator = source.get("private_locator")
        if isinstance(locator, str):
            normalized = locator.replace("\\", "/")
            parts = PurePosixPath(normalized).parts
            if ".." in parts or PurePosixPath(normalized).is_absolute():
                errors.append(f"sources/catalog.yaml: unsafe private_locator for {source_id}")

    mappings = source_map.get("mappings", []) if isinstance(source_map, dict) else []
    if not isinstance(mappings, list):
        errors.append("sources/source-map.yaml: 'mappings' must be a list")
        mappings = []
    mapped: set[str] = set()
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict) or not isinstance(mapping.get("source_id"), str):
            errors.append(f"sources/source-map.yaml mappings[{index}]: source_id is required")
            continue
        source_id = mapping["source_id"]
        if source_id not in seen:
            errors.append(f"sources/source-map.yaml: unknown source ID {source_id}")
        if source_id in mapped:
            errors.append(f"sources/source-map.yaml: duplicate mapping for {source_id}")
        mapped.add(source_id)
        artifacts = mapping.get("artifacts", [])
        if not isinstance(artifacts, list) or not all(isinstance(item, str) for item in artifacts):
            errors.append(f"sources/source-map.yaml: artifacts for {source_id} must be strings")

    if errors:
        print("Source metadata validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {len(sources)} source record(s) and {len(mappings)} source mapping(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
