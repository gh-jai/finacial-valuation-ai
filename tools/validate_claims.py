"""Validate all reviewed claim collections and Knowledge claim references."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CLAIMS_ROOT = Path("extraction/reviewed")


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_frontmatter(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
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


def validate_claim_collection(
    claims_document: Any,
    source_catalog: Any,
    knowledge_documents: Sequence[tuple[str, dict[str, Any]]],
    claim_schema: dict[str, Any],
    claims_path: Path = Path("extraction/reviewed/M1-basic-dcf-claims.yaml"),
) -> tuple[list[str], int, int]:
    """Return errors, claim count, and Knowledge claim-reference count."""
    errors: list[str] = []
    source_records = source_catalog.get("sources", []) if isinstance(source_catalog, dict) else []
    if not isinstance(source_records, list):
        errors.append("sources/catalog.yaml: 'sources' must be a list")
        source_records = []
    source_ids = {
        record.get("id")
        for record in source_records
        if isinstance(record, dict) and isinstance(record.get("id"), str)
    }

    claims = claims_document.get("claims", []) if isinstance(claims_document, dict) else []
    if not isinstance(claims, list):
        errors.append(f"{claims_path.as_posix()}: 'claims' must be a list")
        claims = []

    validator = Draft202012Validator(claim_schema, format_checker=FormatChecker())
    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        label = f"{claims_path.as_posix()} claims[{index}]"
        for error in sorted(validator.iter_errors(claim), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{label}.{location}: {error.message}")
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("id")
        if isinstance(claim_id, str):
            if claim_id in claim_ids:
                errors.append(f"{label}: duplicate claim ID {claim_id}")
            claim_ids.add(claim_id)

        claim_type = claim.get("claim_type")
        source_refs = claim.get("source_refs")
        if claim_type == "source_statement" and (
            not isinstance(source_refs, list) or not source_refs
        ):
            errors.append(f"{label}: source_statement requires at least one source reference")
        if claim_type in {"derived_rule", "model_inference"} and not claim.get("derivation"):
            errors.append(f"{label}: {claim_type} requires a non-empty derivation")
        if isinstance(source_refs, list):
            for ref_index, source_ref in enumerate(source_refs):
                if not isinstance(source_ref, dict):
                    continue
                source_id = source_ref.get("source_id")
                if isinstance(source_id, str) and source_id not in source_ids:
                    errors.append(
                        f"{label}.source_refs[{ref_index}]: unknown source ID {source_id}"
                    )

    reference_count = 0
    for path, metadata in knowledge_documents:
        claim_refs = metadata.get("claim_refs", [])
        if not isinstance(claim_refs, list):
            errors.append(f"{path}: claim_refs must be a list")
            continue
        for claim_ref in claim_refs:
            reference_count += 1
            if not isinstance(claim_ref, str):
                errors.append(f"{path}: claim reference must be a string")
            elif claim_ref not in claim_ids:
                errors.append(f"{path}: unknown claim reference {claim_ref}")
    return errors, len(claims), reference_count


def iter_knowledge_frontmatter(root: Path) -> Iterable[tuple[str, dict[str, Any]]]:
    for path in sorted((root / "knowledge").rglob("*.md")):
        yield path.relative_to(root).as_posix(), load_frontmatter(path)


def validate_repository(root: Path = ROOT) -> tuple[list[str], int, int]:
    claim_schema = json.loads(
        (root / "schemas" / "claim.schema.json").read_text(encoding="utf-8")
    )
    source_catalog = load_yaml(root / "sources" / "catalog.yaml")
    knowledge_documents = list(iter_knowledge_frontmatter(root))
    claim_paths = sorted((root / CLAIMS_ROOT).glob("*.yaml"))
    combined_claims: dict[str, Any] = {"claims": []}
    errors: list[str] = []
    total_claims = 0
    for path in claim_paths:
        document = load_yaml(path)
        relative = path.relative_to(root)
        collection_errors, count, _ = validate_claim_collection(
            document, source_catalog, [], claim_schema, relative
        )
        errors.extend(collection_errors)
        total_claims += count
        if isinstance(document, dict) and isinstance(document.get("claims"), list):
            combined_claims["claims"].extend(document["claims"])
    cross_errors, _, reference_count = validate_claim_collection(
        combined_claims,
        source_catalog,
        knowledge_documents,
        claim_schema,
        Path("extraction/reviewed/*.yaml"),
    )
    errors.extend(cross_errors)
    return errors, total_claims, reference_count


def main() -> int:
    try:
        errors, claim_count, reference_count = validate_repository()
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"Claim validation failed: {exc}")
        return 1
    if errors:
        print("Claim validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"Validated {claim_count} atomic claims and "
        f"{reference_count} Knowledge claim reference(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
